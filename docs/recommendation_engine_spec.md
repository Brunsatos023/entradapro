# Recommendation Engine

## Objetivo

A Recommendation Engine será responsável por transformar os resultados produzidos pelos motores estatísticos do FootballAI em recomendações objetivas para apostas esportivas.

Ela não realizará novos cálculos estatísticos.

Sua função será interpretar os dados já produzidos pelo sistema e responder, de forma clara, quais mercados apresentam maior sustentação estatística.

---

## Princípios

A Recommendation Engine deverá seguir os seguintes princípios:

- Nunca inventar dados.
- Nunca garantir resultados.
- Explicar toda recomendação.
- Informar o nível de confiança.
- Preservar os motores existentes.
- Utilizar apenas dados validados.

---

## Mercados previstos para o MVP

- Resultado da partida
- Over 1.5 gols
- Over 2.5 gols
- Ambos Marcam (BTTS)
- Melhor mercado disponível

Escanteios, placares exatos e mercados avançados serão adicionados futuramente quando houver dados suficientes.

---

## Fluxo da arquitetura

Data
↓

Motores Estatísticos
↓

FootballAI Engine
↓

Recommendation Engine
↓

Dashboard

---

## Próxima etapa

Mapear todos os dados que o FootballAI já produz para identificar quais informações poderão alimentar a Recommendation Engine.