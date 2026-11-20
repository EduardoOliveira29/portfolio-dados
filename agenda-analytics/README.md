# Agenda Analytics

Estudo de BI operacional em uma rede fictícia de atendimento. A pergunta é **em quais combinações de unidade e turno investigar primeiro as faltas a agendamentos?**

![Gráfico de faltas por unidade e turno. Centro à noite soma 53 faltas, seguido de Norte à noite com 48.](resultados/faltas.png)

[Projeto editável e passo a passo no Power BI](power-bi/)

## O que aparece no cenário

No conjunto de **2.400 agendamentos**, houve **320 faltas** e **229 cancelamentos**. A taxa de falta foi de **14,74% entre os 2.171 agendamentos elegíveis**.

| Segmento | Faltas | Elegíveis | Taxa |
| --- | ---: | ---: | ---: |
| Centro à noite | 53 | 265 | 20,00% |
| Norte à noite | 48 | 227 | 21,15% |
| Sul à noite | 40 | 236 | 16,95% |

Centro à noite seria o primeiro recorte a investigar se a meta fosse recuperar o maior número de horários. Norte à noite entraria primeiro se a meta fosse reduzir a maior taxa. Numa operação real, a investigação começaria pela qualidade do registro de desfechos e pela diferença de composição entre unidades e turnos.

## Regras e modelo

- **Grão**: uma linha por agendamento. Cada agendamento tem um desfecho, um turno e uma unidade.
- **Elegíveis**: realizados e faltas. Cancelamentos são acompanhados à parte.
- **Taxa de falta**: faltas divididas por elegíveis. Um grupo sem elegíveis retorna valor nulo.
- **Qualidade**: chave primária, referência obrigatória à unidade, valores aceitos para desfecho e testes para o denominador.

Toda a base é **sintética**, gerada com uma semente fixa. O gerador embute diferenças entre turnos e unidades para permitir a prática de segmentação. Os números descrevem um exercício e o estudo não mede efeito de lembretes ou de outra intervenção.

## Reproduzir

Na pasta deste projeto, com Python 3.10 ou superior:

```bash
python analysis.py
python -m unittest -v
```

O script gera a [base de agendamentos](resultados/agendamentos.csv) e exporta [resumo](resultados/resumo.json), [segmentos](resultados/segmentos.csv) e [série mensal](resultados/mensal.csv). A definição dos KPIs está em [modelo.sql](modelo.sql). Os CSVs podem ser importados no Power BI ou no Excel.
