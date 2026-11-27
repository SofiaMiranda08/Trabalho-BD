# -*- coding: utf-8 -*-
"""
Carga da camada Prata (CEAP_2025_tratada.csv) para a camada Ouro no MySQL.
Antes: rode modelo_mysql_ceap_2025.sql para criar o banco e as tabelas.
Execução:
    pip install pandas mysql-connector-python
    python src/carregar_mysql.py
"""
import pandas as pd
from pathlib import Path
import mysql.connector

# ===== AJUSTE AQUI =====
HOST = "localhost"
USUARIO = "root"
SENHA = "SUA_SENHA_AQUI"
BANCO = "ceap_2025"
ARQUIVO = Path(__file__).resolve().parent.parent / "data" / "silver" / "CEAP_2025_tratada.csv.gz"
# =======================

COLUNAS_INTEIRAS = [
    "ideCadastro", "nuCarteiraParlamentar", "nuLegislatura", "codLegislatura",
    "numSubCota", "numEspecificacaoSubCota", "indTipoDocumento", "numMes",
    "numAno", "numParcela", "numLote", "numRessarcimento", "nuDeputadoId",
    "ideDocumento", "indicador_outlier_vlrLiquido",
]

print("Lendo", ARQUIVO, "...")
df = pd.read_csv(ARQUIVO, sep=";", encoding="utf-8-sig", low_memory=False)
df.columns = [c.strip() for c in df.columns]
for c in COLUNAS_INTEIRAS:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")

# Vazios viram NULL no MySQL (não viram zero).
df = df.astype(object).where(df.notna(), None)
# Converte tipos do numpy para tipos do Python (o conector exige).
linhas = [tuple(v.item() if hasattr(v, "item") else v for v in linha)
          for linha in df.itertuples(index=False, name=None)]
print("Registros lidos:", len(linhas))

con = mysql.connector.connect(host=HOST, user=USUARIO, password=SENHA, database=BANCO)
cur = con.cursor()

print("Limpando tabelas...")
cur.execute("SET FOREIGN_KEY_CHECKS = 0")
for t in ["fato_despesa", "dim_fornecedor", "dim_categoria", "dim_parlamentar", "stg_despesas_ceap"]:
    cur.execute(f"TRUNCATE TABLE {t}")
cur.execute("SET FOREIGN_KEY_CHECKS = 1")

colunas = ", ".join(f"`{c}`" for c in df.columns)
marcadores = ", ".join(["%s"] * len(df.columns))
sql = f"INSERT INTO stg_despesas_ceap ({colunas}) VALUES ({marcadores})"

print("Carregando tabela de estágio...")
LOTE = 5000
for i in range(0, len(linhas), LOTE):
    cur.executemany(sql, linhas[i:i + LOTE])
    con.commit()
    print(f"  {min(i + LOTE, len(linhas))}/{len(linhas)}")

print("Populando dimensões...")
cur.execute("""
INSERT IGNORE INTO dim_parlamentar (nuDeputadoId, nome_parlamentar, uf, partido)
SELECT DISTINCT nuDeputadoId, txNomeParlamentar, sgUF, sgPartido
FROM stg_despesas_ceap WHERE nuDeputadoId IS NOT NULL""")
cur.execute("""
INSERT IGNORE INTO dim_categoria
    (numSubCota, numEspecificacaoSubCota, descricao, descricao_especificacao)
SELECT DISTINCT numSubCota, COALESCE(numEspecificacaoSubCota, 0),
       COALESCE(txtDescricao, ''), txtDescricaoEspecificacao
FROM stg_despesas_ceap""")
cur.execute("""
INSERT IGNORE INTO dim_fornecedor (cnpj_cpf, nome_fornecedor)
SELECT DISTINCT COALESCE(txtCNPJCPF, ''), COALESCE(txtFornecedor, '')
FROM stg_despesas_ceap""")
con.commit()

print("Populando tabela fato...")
cur.execute("""
INSERT INTO fato_despesa
    (parlamentar_key, categoria_key, fornecedor_key, data_emissao,
     valor_documento, valor_glosa, valor_liquido, num_mes, num_ano,
     num_parcela, num_lote, ide_documento, indicador_outlier, mes_referencia)
SELECT p.parlamentar_key, c.categoria_key, f.fornecedor_key, s.datEmissao,
       COALESCE(s.vlrDocumento, 0), COALESCE(s.vlrGlosa, 0), COALESCE(s.vlrLiquido, 0),
       s.numMes, s.numAno, COALESCE(s.numParcela, 0), COALESCE(s.numLote, 0),
       COALESCE(s.ideDocumento, 0), COALESCE(s.indicador_outlier_vlrLiquido, 0),
       s.mes_referencia
FROM stg_despesas_ceap s
JOIN dim_parlamentar p ON p.nuDeputadoId = s.nuDeputadoId
JOIN dim_categoria c ON c.numSubCota = s.numSubCota
    AND c.numEspecificacaoSubCota = COALESCE(s.numEspecificacaoSubCota, 0)
    AND c.descricao = COALESCE(s.txtDescricao, '')
JOIN dim_fornecedor f ON f.cnpj_cpf = COALESCE(s.txtCNPJCPF, '')
    AND f.nome_fornecedor = COALESCE(s.txtFornecedor, '')""")
con.commit()

print("\n=== CONFERÊNCIA ===")
for titulo, q in [
    ("Registros no estágio", "SELECT COUNT(*) FROM stg_despesas_ceap"),
    ("Registros na fato", "SELECT COUNT(*) FROM fato_despesa"),
    ("Total valor líquido (R$)", "SELECT SUM(valor_liquido) FROM fato_despesa"),
]:
    cur.execute(q)
    print(f"{titulo}: {cur.fetchone()[0]}")

cur.close()
con.close()
print("Carga concluída!")
