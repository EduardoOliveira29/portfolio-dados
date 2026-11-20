# Painel de agendamentos no Power BI

O projeto tem uma página com quatro cartões, faltas por unidade e turno e evolução mensal da taxa. Usa a mesma base sintética e as mesmas regras do estudo SQL.

## Abrir

1. Baixe ou clone o repositório completo. Abra [Agenda.pbip](Agenda.pbip) no Power BI Desktop. Preserve as duas pastas do projeto ao lado do arquivo.
2. Se sua versão pedir, ative os formatos Power BI Project e PBIR em **Arquivo → Opções e configurações → Opções → Recursos de visualização** e reinicie o aplicativo.
3. Clique em **Atualizar** para carregar a base sintética incorporada. Confira **2.400** agendamentos, **229** cancelamentos, **320** faltas e **14,74%** de taxa.

Os arquivos foram conferidos contra os esquemas publicados pela Microsoft. A conferência em tela depende do Power BI Desktop, que não estava instalado no ambiente de preparação. [Documentação do formato PBIP](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview)

## Indicador de faltas

A taxa divide as faltas pelo total de atendimentos realizados e faltas no recorte selecionado. Os cancelamentos ficam fora do denominador. No turno da noite, são 141 faltas nas três unidades. As [medidas DAX do modelo](Agenda.SemanticModel/model.bim) e a [consulta Oracle](../modelo.sql) permitem conferir a mesma regra.
