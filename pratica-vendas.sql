-- Execute no Oracle SQL Developer. Os dados fictícios existem só nesta consulta.
WITH vendedor (id, nome) AS (
    SELECT 1, 'Ana' FROM dual UNION ALL
    SELECT 2, 'Rui' FROM dual
), venda (id, vendedor_id, valor_centavos) AS (
    SELECT 1, 1, 12000 FROM dual UNION ALL
    SELECT 2, 1,  8000 FROM dual UNION ALL
    SELECT 3, 2, 15000 FROM dual
)
SELECT vendedor.nome, COUNT(venda.id) AS quantidade,
       SUM(venda.valor_centavos) / 100 AS total_reais
FROM venda JOIN vendedor ON vendedor.id = venda.vendedor_id
GROUP BY vendedor.id, vendedor.nome
ORDER BY total_reais DESC;
