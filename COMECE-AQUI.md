# Comece aqui

Pegue um caso por vez. Rode, faça uma mudança pequena e confira o resultado. A mudança é a parte que mais ajuda na entrevista.

## 1. Entenda um KPI em SQL

Abra [Agenda Analytics](agenda-analytics/). A [base](agenda-analytics/resultados/agendamentos.csv) tem uma linha por agendamento. Conte faltas, realizados e cancelamentos. Faça a conta de cabeça com 10 agendamentos: 2 faltas, 6 realizados, 2 cancelados. A taxa de falta é **2 ÷ 8 = 25%**.

Pratique esta consulta em SQLite depois de criar a base pelo script:

```sql
SELECT turno, COUNT(*) AS faltas
FROM agendamento
WHERE desfecho = 'falta'
GROUP BY turno
ORDER BY faltas DESC;
```

O banco do script padrão fica em memória. Para praticar num arquivo, rode o comando abaixo na pasta `agenda-analytics`. Depois abra `pratica.sqlite` em um cliente SQLite ou use `python -m sqlite3 pratica.sqlite` no Python 3.12+.

```bash
python -c "import sqlite3; from analysis import build, generate; db = sqlite3.connect('pratica.sqlite'); build(db, generate(2400)); db.close()"
```

**Sua mudança:** adicione `unidade_id` ao `SELECT` e ao `GROUP BY`. Compare o grupo com mais faltas com o de maior taxa no CSV de segmentos. Por que eles são diferentes?

Se quiser começar com uma base menor, rode [pratica-vendas.sql](pratica-vendas.sql) em um banco SQLite vazio. O exemplo adapta o `JOIN` de um exercício da FIAP sobre vendas. Compare as três linhas detalhadas com as duas linhas agrupadas. Ana deve aparecer com duas vendas e R$ 200 no total.

## 2. Refaça a visualização no Power BI

Abra o [guia do painel](agenda-analytics/power-bi/). Reproduza primeiro um cartão de total e um de taxa de falta. Depois crie um filtro de turno e confirme que os cartões mudam.

**Sua mudança:** adicione uma matriz com unidade nas linhas e turno nas colunas. Compare as taxas com [segmentos.csv](agenda-analytics/resultados/segmentos.csv). Na entrevista, explique por que dividir totais é diferente de tirar a média das taxas de cada grupo.

## 3. Leia um JSON e junte duas séries

Abra [Indicadores do Banco Central](indicadores-bcb/). Compare [duas respostas JSON](indicadores-bcb/dados/) e encontre o mesmo mês nos dois arquivos. Siga o código em `pipeline.py` até o [JOIN](indicadores-bcb/metricas.sql) e confira a linha final no CSV.

**Sua mudança:** acrescente ao CSV uma coluna com a variação do IPCA do mês atual menos a do mês anterior. Confira um mês com uma calculadora e decida como preencher a primeira linha, que não tem mês anterior no recorte.

## Conte a história em 60 segundos

1. Qual era a pergunta?
2. De onde vieram os dados e o que representa uma linha?
3. Como foi calculado o indicador?
4. O que o resultado permite investigar? Qual é a limitação?
5. O que você modificou e como conferiu?

Exemplo para praticar: “Na agenda simulada, eu quis descobrir onde investigar faltas primeiro. Comparei o número de faltas com a taxa entre consultas elegíveis. Centro à noite teve o maior volume, e Norte à noite, a maior taxa. Eu ajustei [sua mudança] e conferi com [sua verificação].”

O material inicial foi preparado com apoio de IA. Na entrevista, descreva o que você executou, conferiu e modificou de fato.
