# Painel de agendamentos no Power BI

O projeto tem uma página com quatro cartões, faltas por unidade e turno e evolução mensal da taxa. Usa a mesma base sintética e as mesmas regras do estudo SQL.

## Abrir

1. Baixe ou clone o repositório completo. Abra [Agenda.pbip](Agenda.pbip) no Power BI Desktop. Preserve as duas pastas do projeto ao lado do arquivo.
2. Se sua versão pedir, ative os formatos Power BI Project e PBIR em **Arquivo → Opções e configurações → Opções → Recursos de visualização** e reinicie o aplicativo.
3. Clique em **Atualizar** para carregar a base sintética incorporada. Confira **2.400** agendamentos, **229** cancelamentos, **320** faltas e **14,74%** de taxa.

Os arquivos foram conferidos contra os esquemas publicados pela Microsoft. A conferência em tela depende do Power BI Desktop, que não estava instalado no ambiente de preparação. [Documentação do formato PBIP](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview)

## Refazer para aprender

1. No Desktop, crie um relatório e importe [agendamentos.csv](../resultados/agendamentos.csv) em **Obter dados → Texto/CSV**. Use UTF-8 e vírgula. Renomeie a tabela para `Agenda`.
2. Crie estas medidas em **Modelagem → Nova medida**, uma por vez:

   ```dax
   Agendamentos = COUNTROWS(Agenda)
   Cancelamentos = CALCULATE([Agendamentos], Agenda[desfecho] = "cancelado")
   Faltas = CALCULATE([Agendamentos], Agenda[desfecho] = "falta")
   Elegíveis = CALCULATE([Agendamentos], Agenda[desfecho] IN {"realizado", "falta"})
   Taxa de falta = DIVIDE([Faltas], [Elegíveis])
   ```

3. Coloque **Agendamentos**, **Cancelamentos**, **Faltas** e **Taxa de falta** em cartões. Formate a última medida como percentual com duas casas.
4. Adicione um gráfico de barras com `unidade_id` no eixo de categoria, `turno` na legenda e **Faltas** no eixo de valores. Adicione uma segmentação por turno. Use `N` para Norte, `S` para Sul e `C` para Centro.
5. Clique em **Noite**. O cartão de faltas deve mostrar **141** (53 + 48 + 40). Limpe o filtro para voltar a **320**.

**Como explicar:** uma medida recalcula conforme o filtro da página. O denominador da taxa inclui realizados e faltas. O Power BI e o SQL trabalham com a mesma definição de elegibilidade.
