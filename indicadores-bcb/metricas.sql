WITH janela_movel AS (
    SELECT
        mes,
        ipca,
        selic,
        COUNT(*) OVER ultimos_12 AS meses_na_janela,
        SUM(log_factor(ipca)) OVER ultimos_12 AS soma_log_ipca,
        SUM(log_factor(selic)) OVER ultimos_12 AS soma_log_selic
    FROM serie_mensal
    WINDOW ultimos_12 AS (ORDER BY mes ROWS BETWEEN 11 PRECEDING AND CURRENT ROW)
)
SELECT
    mes,
    ipca AS ipca_mensal_pct,
    selic AS selic_mensal_pct,
    CASE WHEN meses_na_janela = 12 THEN ROUND(to_percent(soma_log_ipca), 8) END AS ipca_12m_pct,
    CASE WHEN meses_na_janela = 12 THEN ROUND(to_percent(soma_log_selic), 8) END AS selic_12m_pct
FROM janela_movel
ORDER BY mes;
