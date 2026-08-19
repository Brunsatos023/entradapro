# Scripts de migração histórica

Estes scripts já foram executados no passado para evoluir o banco de dados
de usuários (adicionar campo de admin, adicionar pagamentos, corrigir login).
Estão aqui como referência/documentação de como o banco chegou ao formato
atual — não fazem parte do funcionamento normal do EntradaPro.

⚠️ Se algum dia precisar rodar um deles de novo, revise o caminho do banco
de dados dentro do arquivo antes: eles foram escritos para procurar
`entradapro_users.db` na mesma pasta do script, mas o banco real do
projeto hoje fica em `data/entradapro_users.db`.

- `migrar_admin.py` — adicionou o campo de administrador aos usuários.
- `migrar_pagamentos.py` — adicionou as tabelas de pagamento/assinatura.
- `migrar_usuario_login.py` — corrigiu/ajustou o sistema de login.
