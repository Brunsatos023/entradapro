# Roadmap V2 — o que ficou decidido para depois do lançamento

Este arquivo existe para não perder decisões de escopo tomadas durante
a preparação da V1. Nada aqui bloqueia o lançamento da V1.

## Jogos ao vivo + busca automática de odds

**Decisão (Etapa 7):** a V1 lança usando apenas o dataset histórico
local (`data/raw/brasileirao_serie_a_2024.json`). O usuário digita a
odd manualmente (como já funciona hoje).

**O que falta para V2:**
1. Buscar jogos futuros reais via API-Football (endpoint `/fixtures`,
   com data de hoje/próximos dias) — hoje o dashboard só sabe navegar
   pelo dataset histórico, não existe uma lista de "jogos de hoje".
2. Ligar essa lista de jogos futuros a um `fixture_id` real.
3. Com o `fixture_id` em mãos, usar a engine já pronta em
   `src/engines/odds_engine.py` (`buscar_melhores_odds(fixture_id)`)
   para buscar e comparar odds reais entre 6 casas de apostas
   (Bet365, Betano, Sportingbet, Betway, Betfair, Superbet) e mostrar
   a melhor automaticamente — sem o usuário digitar nada.

**O que já está pronto, esperando a V2:**
- `src/engines/odds_engine.py` — engine completa de busca e
  comparação de odds, já testada (9 testes em
  `tests/test_odds_engine.py`, todos passando, usando respostas
  simuladas no formato real da API-Football).
- Só falta a parte de buscar jogos futuros (`/fixtures`) e ligar o
  `fixture_id` encontrado a essa engine.

## Reformulação completa de layout (estilo Forebet) — pós-lançamento

Bruno enviou uma especificação completa e detalhada de reformulação de
UX/UI (cabeçalho, navegação por data, filtro de competições, lista de
jogos, EntradaPro Score, Value Bet destacado, Melhores Entradas do Dia,
Ranking de Value, página individual da partida com abas, histórico de
previsões com ROI/yield, competições, busca, favoritos, responsividade
completa). Decisão: publicar a V1 atual primeiro, revisitar esse
documento depois do lançamento.

Boa parte dessa especificação depende da infraestrutura de "jogos
futuros reais" já adiada para V2 (navegação por data, múltiplos
campeonatos, lista de vários jogos simultâneos, Melhores Entradas do
Dia, Ranking de Value, busca, favoritos, histórico de previsões).

A parte que É viável sem essa infraestrutura (reaproveitando os dados/
engines atuais): EntradaPro Score, página da partida com abas, selo de
Value, explicação da previsão, forma dos times, desempenho casa/fora,
cards mobile responsivos, indicação Free/Premium, rodapé com avisos
legais.
