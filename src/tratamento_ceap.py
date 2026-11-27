# -*- coding: utf-8 -*-
"""
Tratamento da base CEAP 2025
Bibliotecas: pandas
Execução:
    pip install pandas
    python tratamento_ceap.py
Coloque Ano-2025.csv em data/raw/. Execute a partir da pasta do projeto:
    python src/tratamento_ceap.py
O arquivo original não é alterado.
"""
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
ARQUIVO_ORIGINAL = BASE / "data" / "raw" / "Ano-2025.csv"          # camada Bronze
ARQUIVO_TRATADO = BASE / "data" / "silver" / "CEAP_2025_tratada.csv.gz"  # camada Prata

df = pd.read_csv(ARQUIVO_ORIGINAL, sep=";", encoding="utf-8-sig", low_memory=False)
df.columns = [col.strip().replace("\\ufeff", "") for col in df.columns]

# 1. Padronização simples dos textos: remove espaços extras.
colunas_texto = df.select_dtypes(include=["object"]).columns
for coluna in colunas_texto:
    df[coluna] = df[coluna].astype("string").str.strip()
    df[coluna] = df[coluna].replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})

# 2. Conversão das colunas numéricas.
colunas_numericas = [
    "ideCadastro", "nuCarteiraParlamentar", "nuLegislatura", "codLegislatura",
    "numSubCota", "numEspecificacaoSubCota", "indTipoDocumento",
    "vlrDocumento", "vlrGlosa", "vlrLiquido", "numMes", "numAno",
    "numParcela", "numLote", "numRessarcimento", "vlrRestituicao",
    "nuDeputadoId", "ideDocumento"
]
for coluna in colunas_numericas:
    if coluna in df.columns:
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce")

# 3. Conversão de datas. Datas ausentes continuam vazias (não viram zero).
df["datEmissao"] = pd.to_datetime(df["datEmissao"], errors="coerce")
if "datPagamentoRestituicao" in df.columns:
    df["datPagamentoRestituicao"] = pd.to_datetime(
        df["datPagamentoRestituicao"], errors="coerce"
    )

# 4. Duplicidades: remove somente linhas totalmente iguais.
# Não usar ideDocumento isoladamente como chave: há documentos com mais de
# um registro válido (por exemplo, valores repartidos em parcelas).
df = df.drop_duplicates().copy()

# 5. Outliers: regra do intervalo interquartil (IQR).
# Os valores extremos são sinalizados, não excluídos, pois podem ser despesas reais.
q1 = df["vlrLiquido"].quantile(0.25)
q3 = df["vlrLiquido"].quantile(0.75)
iqr = q3 - q1
limite_inferior = q1 - 1.5 * iqr
limite_superior = q3 + 1.5 * iqr
df["indicador_outlier_vlrLiquido"] = (
    (df["vlrLiquido"] < limite_inferior) |
    (df["vlrLiquido"] > limite_superior)
).astype("int8")

# 6. Campo de referência mensal para facilitar os gráficos.
df["mes_referencia"] = (
    df["numAno"].fillna(0).astype(int).astype(str) + "-" +
    df["numMes"].fillna(0).astype(int).astype(str).str.zfill(2)
)

# 7. Exportação da nova base. O CSV original permanece intacto.
df.to_csv(
    ARQUIVO_TRATADO, sep=";", index=False, encoding="utf-8-sig",
    date_format="%Y-%m-%d %H:%M:%S"
)
print("Tratamento concluído.")
print("Registros:", len(df))
print("Colunas:", len(df.columns))
print("Outliers sinalizados:", int(df["indicador_outlier_vlrLiquido"].sum()))
print("Arquivo gerado:", ARQUIVO_TRATADO)
