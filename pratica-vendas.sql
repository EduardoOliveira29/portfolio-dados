-- Prática com SQLite em um banco novo. Os valores são fictícios.
-- O JOIN segue a ideia do relatório de vendas do exercício Java da FIAP.
PRAGMA foreign_keys = ON;

CREATE TABLE vendedor (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL
);

CREATE TABLE venda (
    id INTEGER PRIMARY KEY,
    vendedor_id INTEGER NOT NULL REFERENCES vendedor (id),
    valor_centavos INTEGER NOT NULL
);

INSERT INTO vendedor VALUES (1, 'Ana'), (2, 'Rui');
INSERT INTO venda VALUES (1, 1, 12000), (2, 1, 8000), (3, 2, 15000);

-- Uma linha por venda, com o nome do vendedor.
SELECT
    vendedor.nome,
    venda.valor_centavos / 100.0 AS valor_reais
FROM venda
JOIN vendedor ON vendedor.id = venda.vendedor_id
ORDER BY venda.id;

-- Uma linha por vendedor, com a quantidade e o total das vendas.
SELECT
    vendedor.nome,
    COUNT(venda.id) AS quantidade,
    SUM(venda.valor_centavos) / 100.0 AS total_reais
FROM venda
JOIN vendedor ON vendedor.id = venda.vendedor_id
GROUP BY vendedor.id, vendedor.nome
ORDER BY total_reais DESC;
