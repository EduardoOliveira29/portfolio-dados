-- Cada objeto no JSON representa um agendamento. O Python envia o arquivo
-- como parâmetro CLOB. A consulta usa os dados apenas durante a execução.
WITH base AS (
    SELECT SUBSTR(a.data_prevista, 1, 7) AS mes,
           CASE a.unidade_id WHEN 'N' THEN 'Norte' WHEN 'C' THEN 'Centro'
                             WHEN 'S' THEN 'Sul' END AS unidade,
           a.turno,
           CASE WHEN a.desfecho IN ('falta', 'realizado') THEN 1 ELSE 0 END AS elegivel,
           CASE WHEN a.desfecho = 'falta' THEN 1 ELSE 0 END AS falta,
           CASE WHEN a.desfecho = 'cancelado' THEN 1 ELSE 0 END AS cancelado
    FROM JSON_TABLE(:dados, '$[*]' ERROR ON ERROR COLUMNS (
        data_prevista VARCHAR2(10) PATH '$.data_prevista',
        unidade_id VARCHAR2(1) PATH '$.unidade_id',
        turno VARCHAR2(10) PATH '$.turno',
        desfecho VARCHAR2(12) PATH '$.desfecho'
    )) a
)
-- Cada agrupamento produz uma parte do relatório.
SELECT CASE WHEN GROUPING(mes) = 0 THEN 'mensal'
            WHEN GROUPING(unidade) = 0 THEN 'segmento'
            ELSE 'resumo' END AS recorte,
       mes, unidade, turno, COUNT(*) AS marcados,
       NVL(SUM(elegivel), 0) AS elegiveis, NVL(SUM(falta), 0) AS faltas,
       NVL(SUM(cancelado), 0) AS cancelados,
       ROUND(100 * SUM(falta) / NULLIF(SUM(elegivel), 0), 2) AS taxa_falta_pct
FROM base
GROUP BY GROUPING SETS ((), (mes), (unidade, turno))
ORDER BY mes, faltas DESC, unidade, turno
