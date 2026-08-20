# Backups automáticos

Esta pasta recebe, todo dia às 6h (horário de Brasília), um backup
automático das tabelas principais do banco de produção (usuários,
assinaturas, pagamentos, previsões) — sem senhas nem dados sensíveis.

Gerado automaticamente pelo GitHub Actions
(`.github/workflows/backup_diario.yml`). Não precisa mexer aqui
manualmente.

Se precisar restaurar algo, o arquivo mais recente é o que tem a
data mais nova no nome (`backup_AAAA-MM-DD_HHMM.json`).
