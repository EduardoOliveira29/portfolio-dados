# Portfólio de Dados e BI

Dois estudos reproduzíveis com Python e SQL. Cada caso parte de uma pergunta, documenta suas regras de negócio e entrega dados processados, testes e uma visualização.

[Roteiro de estudo e prática](COMECE-AQUI.md) · [Painel e exercício no Power BI](agenda-analytics/power-bi/)

| Projeto | Pergunta | Evidência |
| --- | --- | --- |
| [Indicadores do Banco Central](indicadores-bcb/) | Como IPCA e Selic acumulados em 12 meses evoluíram entre 2020 e 2025? | API pública, validação de cobertura, `JOIN` por mês e conferência com o IBGE |
| [Agenda Analytics](agenda-analytics/) | Onde faz mais sentido começar a investigar faltas em agendamentos? | Base sintética, SQL por segmento, medidas DAX e painel editável no Power BI |

Minha base em Java aparece no [Defesa Ribeirinho](defesa-ribeirinho/), com um exemplo executável sobre confirmação de alertas e ocupação de abrigos. A [consulta de vendas por vendedor](pratica-vendas.sql) retoma um exercício de Java/JDBC da faculdade.

**Execução:** Python 3.10+ e SQLite da biblioteca padrão. Cada pasta contém os comandos e os resultados do caso. Para regenerar as duas figuras, execute os pipelines, instale `matplotlib` e rode `python graficos.py` na raiz.

Os projetos foram preparados com assistência de IA como material de estudo e prática. As premissas e os testes estão no repositório para que os resultados possam ser reproduzidos e revisados.
