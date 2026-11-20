-- Os parâmetros contêm as séries mensais normalizadas pelo Python.
WITH ipca AS (
    SELECT mes, taxa FROM JSON_TABLE(:ipca, '$[*]' ERROR ON ERROR COLUMNS (
        mes VARCHAR2(7) PATH '$.mes', taxa NUMBER PATH '$.taxa'
    ))
), selic AS (
    SELECT mes, taxa FROM JSON_TABLE(:selic, '$[*]' ERROR ON ERROR COLUMNS (
        mes VARCHAR2(7) PATH '$.mes', taxa NUMBER PATH '$.taxa'
    ))
)
SELECT ipca.mes, ipca.taxa AS ipca_mensal_pct, selic.taxa AS selic_mensal_pct
FROM ipca JOIN selic ON selic.mes = ipca.mes
ORDER BY ipca.mes
