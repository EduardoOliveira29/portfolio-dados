SELECT
    ipca.mes,
    ipca.taxa AS ipca_mensal_pct,
    selic.taxa AS selic_mensal_pct
FROM ipca
JOIN selic ON selic.mes = ipca.mes
ORDER BY ipca.mes;
