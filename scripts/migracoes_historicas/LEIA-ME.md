# Scripts de migração histórica

Estes scripts já foram executados no passado para evoluir o banco de dados
de usuários (adicionar campo de admin, adicionar pagamentos, corrigir login).
Estão aqui como referência/documentação de como o banco chegou ao formato
atual.

✅ **Atualização (Etapa 4):** a criação das tabelas de assinatura e
pagamento (que antes só existia em `migrar_pagamentos.py`) agora também
está dentro de `inicializar_banco()`, em `src/auth.py` — que roda
automaticamente toda vez que o EntradaPro inicia. Ou seja, **não é mais
necessário rodar `migrar_pagamentos.py` manualmente**, nem num banco novo
(produção) nem no banco atual. Os scripts continuam aqui só como histórico.

⚠️ Se algum dia precisar rodar um destes scripts de novo mesmo assim,
revise o caminho do banco de dados dentro do arquivo antes: eles foram
escritos para procurar `entradapro_users.db` na mesma pasta do script, mas
o banco real do projeto hoje fica em `data/entradapro_users.db`.

- `migrar_admin.py` — adicionou o campo de administrador aos usuários.
- `migrar_pagamentos.py` — adicionou as tabelas de pagamento/assinatura.
- `migrar_usuario_login.py` — corrigiu/ajustou o sistema de login.
