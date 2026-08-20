"""
Página "Administração" — conecta o admin_users.py (que já existia
no código, mas nunca estava ligado ao site) ao menu de páginas do
Streamlit.

Protegida por login próprio (usuário precisa ter a permissão
"admin" no banco) - ver admin_users.py / garantir_acesso_admin().
Não é exibida com destaque para usuários comuns na navegação, mas
mesmo que apareça na lista de páginas, ninguém sem a permissão
"admin" no banco consegue passar do login.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from admin_users import main  # noqa: E402

main()
