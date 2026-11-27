-- Projeto CEAP 2025 | MySQL 8
-- 1) Crie o banco e a tabela de estágio.
CREATE DATABASE IF NOT EXISTS ceap_2025
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ceap_2025;

DROP TABLE IF EXISTS fato_despesa;
DROP TABLE IF EXISTS dim_fornecedor;
DROP TABLE IF EXISTS dim_categoria;
DROP TABLE IF EXISTS dim_parlamentar;
DROP TABLE IF EXISTS stg_despesas_ceap;

CREATE TABLE stg_despesas_ceap (
    txNomeParlamentar VARCHAR(180),
    cpf VARCHAR(30),
    ideCadastro BIGINT NULL,
    nuCarteiraParlamentar INT NULL,
    nuLegislatura INT,
    sgUF CHAR(2) NULL,
    sgPartido VARCHAR(30) NULL,
    codLegislatura INT,
    numSubCota INT,
    txtDescricao VARCHAR(255),
    numEspecificacaoSubCota INT,
    txtDescricaoEspecificacao VARCHAR(255) NULL,
    txtFornecedor VARCHAR(255),
    txtCNPJCPF VARCHAR(40),
    txtNumero VARCHAR(80),
    indTipoDocumento INT,
    datEmissao DATETIME NULL,
    vlrDocumento DECIMAL(15,2),
    vlrGlosa DECIMAL(15,2),
    vlrLiquido DECIMAL(15,2),
    numMes INT,
    numAno INT,
    numParcela INT,
    txtPassageiro VARCHAR(255) NULL,
    txtTrecho VARCHAR(255) NULL,
    numLote BIGINT,
    numRessarcimento BIGINT NULL,
    datPagamentoRestituicao DATETIME NULL,
    vlrRestituicao DECIMAL(15,2) NULL,
    nuDeputadoId INT,
    ideDocumento BIGINT,
    urlDocumento TEXT,
    indicador_outlier_vlrLiquido TINYINT,
    mes_referencia CHAR(7)
);

-- 2) Importe CEAP_2025_tratada.csv nesta tabela usando:
-- MySQL Workbench > Server > Data Import > Table Data Import Wizard.
-- Delimitador: ponto e vírgula (;). Codificação: UTF-8.
-- Não marque a primeira coluna como índice: a tabela já tem os campos definidos.

-- 3) Dimensões (modelo estrela).
CREATE TABLE dim_parlamentar (
    parlamentar_key INT AUTO_INCREMENT PRIMARY KEY,
    nuDeputadoId INT NOT NULL,
    nome_parlamentar VARCHAR(180) NOT NULL,
    uf CHAR(2) NULL,
    partido VARCHAR(30) NULL,
    UNIQUE KEY uk_parlamentar (nuDeputadoId)
);

CREATE TABLE dim_categoria (
    categoria_key INT AUTO_INCREMENT PRIMARY KEY,
    numSubCota INT NOT NULL,
    numEspecificacaoSubCota INT NOT NULL,
    descricao VARCHAR(255) NOT NULL,
    descricao_especificacao VARCHAR(255) NULL,
    UNIQUE KEY uk_categoria (numSubCota, numEspecificacaoSubCota, descricao)
);

CREATE TABLE dim_fornecedor (
    fornecedor_key INT AUTO_INCREMENT PRIMARY KEY,
    cnpj_cpf VARCHAR(40) NOT NULL,
    nome_fornecedor VARCHAR(255) NOT NULL,
    UNIQUE KEY uk_fornecedor (cnpj_cpf, nome_fornecedor)
);

CREATE TABLE fato_despesa (
    despesa_key BIGINT AUTO_INCREMENT PRIMARY KEY,
    parlamentar_key INT NOT NULL,
    categoria_key INT NOT NULL,
    fornecedor_key INT NOT NULL,
    data_emissao DATETIME NULL,
    valor_documento DECIMAL(15,2) NOT NULL,
    valor_glosa DECIMAL(15,2) NOT NULL,
    valor_liquido DECIMAL(15,2) NOT NULL,
    num_mes INT NOT NULL,
    num_ano INT NOT NULL,
    num_parcela INT NOT NULL,
    num_lote BIGINT NOT NULL,
    ide_documento BIGINT NOT NULL,
    indicador_outlier TINYINT NOT NULL DEFAULT 0,
    mes_referencia CHAR(7),
    CONSTRAINT fk_fato_parlamentar FOREIGN KEY (parlamentar_key)
        REFERENCES dim_parlamentar(parlamentar_key),
    CONSTRAINT fk_fato_categoria FOREIGN KEY (categoria_key)
        REFERENCES dim_categoria(categoria_key),
    CONSTRAINT fk_fato_fornecedor FOREIGN KEY (fornecedor_key)
        REFERENCES dim_fornecedor(fornecedor_key)
);

-- 4) Popular dimensões com os dados da camada de estágio.
INSERT IGNORE INTO dim_parlamentar (nuDeputadoId, nome_parlamentar, uf, partido)
SELECT DISTINCT nuDeputadoId, txNomeParlamentar, sgUF, sgPartido
FROM stg_despesas_ceap
WHERE nuDeputadoId IS NOT NULL;

INSERT IGNORE INTO dim_categoria
    (numSubCota, numEspecificacaoSubCota, descricao, descricao_especificacao)
SELECT DISTINCT numSubCota, numEspecificacaoSubCota, txtDescricao,
       txtDescricaoEspecificacao
FROM stg_despesas_ceap;

INSERT IGNORE INTO dim_fornecedor (cnpj_cpf, nome_fornecedor)
SELECT DISTINCT txtCNPJCPF, txtFornecedor
FROM stg_despesas_ceap;

-- 5) Popular tabela fato. Cada linha original permanece como um lançamento.
INSERT INTO fato_despesa
    (parlamentar_key, categoria_key, fornecedor_key, data_emissao,
     valor_documento, valor_glosa, valor_liquido, num_mes, num_ano,
     num_parcela, num_lote, ide_documento, indicador_outlier, mes_referencia)
SELECT p.parlamentar_key, c.categoria_key, f.fornecedor_key, s.datEmissao,
       s.vlrDocumento, s.vlrGlosa, s.vlrLiquido, s.numMes, s.numAno,
       s.numParcela, s.numLote, s.ideDocumento,
       s.indicador_outlier_vlrLiquido, s.mes_referencia
FROM stg_despesas_ceap s
JOIN dim_parlamentar p ON p.nuDeputadoId = s.nuDeputadoId
JOIN dim_categoria c ON c.numSubCota = s.numSubCota
    AND c.numEspecificacaoSubCota = s.numEspecificacaoSubCota
    AND c.descricao = s.txtDescricao
JOIN dim_fornecedor f ON f.cnpj_cpf = s.txtCNPJCPF
    AND f.nome_fornecedor = s.txtFornecedor;

-- 6) Conferência após a carga.
SELECT COUNT(*) AS total_registros_estagio FROM stg_despesas_ceap;
SELECT COUNT(*) AS total_registros_fato FROM fato_despesa;
SELECT SUM(valor_liquido) AS total_valor_liquido FROM fato_despesa;
