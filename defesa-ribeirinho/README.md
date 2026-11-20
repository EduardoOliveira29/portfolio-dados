# Defesa Ribeirinho · do alerta à ocupação do abrigo

O Defesa Ribeirinho é um MVP acadêmico da FIAP. Nele, um operador registra manualmente o nível de água de uma área. Famílias daquela área podem receber um aviso interno, confirmar a leitura e solicitar acolhimento. O check-in ocupa vagas pelo número de pessoas da família. A saída libera essas vagas.

O projeto acadêmico usa Java 21, Spring Boot, JPA e uma API JSON, com H2 local e um perfil para Oracle. A coleção Postman documenta 16 requisições com dados fictícios. O repositório original é privado. O arquivo [ResumoAbrigo.java](ResumoAbrigo.java) é um exercício independente, preparado com assistência de IA para estudar dois indicadores desse fluxo.

## Três famílias recebem o mesmo aviso

| Família fictícia | Pessoas | Confirmou o aviso? | Está no abrigo? |
| --- | ---: | --- | --- |
| A | 4 | Sim | Sim |
| B | 2 | Sim | Não |
| C | 3 | Não | Não |

A confirmação é contada **por família avisada**. Duas das três confirmaram, o que dá 66,7%. A ocupação é contada **por pessoa presente**. A família A ocupa quatro das dez vagas, ou 40%. A família B entra no primeiro cálculo e só entraria no segundo após o check-in.

## Rode e mude o cenário

Com um JDK 21 ou superior, abra um terminal nesta pasta e execute:

```console
java ResumoAbrigo.java
```

O exemplo imprime os dois percentuais e seis vagas disponíveis. Para simular a chegada da família B, troque `new Familia(2, true, false)` por `new Familia(2, true, true)`. Antes de rodar de novo, tente prever qual percentual muda. A nova ocupação deve ser 60%, com quatro vagas disponíveis e as mesmas duas confirmações.

O exemplo usa um único aviso, um abrigo e uma fotografia do momento. Para analisar várias datas, seria preciso saber quem estava acolhido no instante de cada medição. Somar todos os check-ins da semana contaria também quem já saiu.
