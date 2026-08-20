"""
O login nativo do Streamlit (st.login) lê as credenciais do
Google de um arquivo .streamlit/secrets.toml - mas no Render a
gente configura variáveis de ambiente, não arquivos. Esta função
gera esse arquivo automaticamente, uma vez, a partir das
variáveis de ambiente já configuradas.

Chame configurar_secrets_google() bem no início do dashboard,
antes de qualquer st.login()/st.user ser usado.
"""

import os
from pathlib import Path


CAMINHO_SECRETS = (
    Path(__file__).resolve().parents[1]
    / ".streamlit"
    / "secrets.toml"
)


def google_login_configurado():
    return bool(
        os.getenv("GOOGLE_CLIENT_ID")
        and os.getenv("GOOGLE_CLIENT_SECRET")
        and os.getenv("STREAMLIT_COOKIE_SECRET")
        and os.getenv("STREAMLIT_REDIRECT_URI")
    )


def configurar_secrets_google():
    """
    Gera .streamlit/secrets.toml a partir das variáveis de
    ambiente, se todas estiverem presentes e o arquivo ainda não
    existir. Idempotente e seguro de chamar toda vez que o app
    inicia.
    """
    if not google_login_configurado():
        return False

    if CAMINHO_SECRETS.exists():
        return True

    CAMINHO_SECRETS.parent.mkdir(parents=True, exist_ok=True)

    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    cookie_secret = os.getenv("STREAMLIT_COOKIE_SECRET")
    redirect_uri = os.getenv("STREAMLIT_REDIRECT_URI")

    conteudo = f"""[auth]
redirect_uri = "{redirect_uri}"
cookie_secret = "{cookie_secret}"
client_id = "{client_id}"
client_secret = "{client_secret}"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
"""

    with open(CAMINHO_SECRETS, "w", encoding="utf-8") as arquivo:
        arquivo.write(conteudo)

    return True
