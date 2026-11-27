# 👁️ Olho na Cota — Pipeline ETL e Painel da CEAP 2025

Projeto prático de **Engenharia de Dados** (Banco de Dados, 3ª série do Ensino Médio Técnico).

## 🎯 Problema
Os gastos dos deputados federais com a **Cota para o Exercício da Atividade Parlamentar (CEAP)** são públicos, mas estão em um arquivo com mais de **171 mil linhas**, difícil de entender para o cidadão. Este projeto transforma esses dados em um **painel interativo de transparência**, mostrando quanto foi gasto, em quê, por quem e onde há gastos fora do padrão.

## 🤝 Impacto social
- O **eleitor** consulta o deputado em quem votou e vota e cobra com base em fatos.
- **Jornalistas e órgãos de controle** sabem onde investigar primeiro.
- O debate sobre o uso do dinheiro público passa a se basear em dados.

O painel **não diz em quem votar**: ele mostra os dados para que cada pessoa decida com mais informação.

## 📊 Números principais (2025)
| Indicador | Valor |
|---|---|
| Total gasto (valor líquido) | R$ 215,1 milhões |
| Lançamentos | 171.059 |
| Deputados com gastos | 562 |
| Fornecedores | 22.250 |
| Gastos sinalizados como outliers (IQR) | 31.183 |

## 🏗️ Arquitetura Medalhão
| Camada | O que acontece | Arquivo |
|---|---|---|
| 🥉 Bronze | Dado bruto da Câmara, sem alterações | `data/raw/` |
| 🥈 Prata | Limpeza com pandas: textos, tipos, datas ISO-8601, duplicatas, outliers sinalizados | `src/tratamento_ceap.py` → `data/silver/` |
| 🥇 Ouro | Modelo estrela no MySQL (fato + 3 dimensões, PK/FK) e carga automatizada | `sql/modelo_mysql_ceap_2025.sql`, `src/carregar_mysql.py` |
| 📊 Visualização | Painel em Streamlit, versão HTML e planejamento do Power BI com DAX | `app.py`, `dashboard/`, `docs/` |

## 🖥️ Telas do painel
1. **Início**: problema, impacto e indicadores
2. **Visão geral**: evolução mensal, composição por categoria, distribuição dos valores
3. **Categorias**: rosca e ranking
4. **Deputados**: top 10 e busca por nome, partido ou UF
5. **Estados e partidos**: mapa de calor e média por deputado
6. **Fornecedores**: maiores recebedores
7. **Alertas**: gastos fora do padrão (regra IQR)
8. **Sobre o projeto**: pipeline, DER e decisões

## ❓ Perguntas de negócio
1. Como os gastos evoluíram mês a mês em 2025?
2. Em que categorias a cota é mais usada?
3. Quais deputados mais gastaram?
4. Quais estados e partidos têm maior gasto médio por deputado?
5. Quais gastos fogem do padrão e merecem revisão?

## ▶️ Como executar
```bash
pip install -r requirements.txt
streamlit run app.py
```
Mais detalhes em `COMO_RODAR.txt`.

Para refazer o pipeline do zero: baixe `Ano-2025.csv` no portal de Dados Abertos da Câmara, salve em `data/raw/` e rode `python src/tratamento_ceap.py`.

## 📁 Estrutura
```
olho-na-cota-ceap-2025/
├── app.py                      # Painel Streamlit
├── requirements.txt
├── COMO_RODAR.txt
├── data/
│   ├── raw/                    # Bronze (Ano-2025.csv, fora do Git)
│   └── silver/                 # Prata (CEAP_2025_tratada.csv.gz)
├── src/
│   ├── tratamento_ceap.py      # Bronze → Prata
│   └── carregar_mysql.py       # Prata → Ouro (MySQL)
├── sql/modelo_mysql_ceap_2025.sql
├── dashboard/index.html        # Versão HTML do painel
└── docs/                       # Relatório EDA, DAX, planejamento, roteiro
```

## ⚖️ Decisões de tratamento
- **Outliers sinalizados, não apagados**: podem ser despesas reais.
- **Nulos mantidos vazios**: trocar por zero distorceria médias.
- **Duplicatas só por linha idêntica**: `ideDocumento` não é chave única.
- **Lideranças fora dos rankings**: registros como `LID.GOV-CD` não são deputados.
- **Gasto alto ≠ irregularidade**: o painel indica onde olhar, não acusa.

**Fonte:** Câmara dos Deputados — Dados Abertos (CEAP 2025).
