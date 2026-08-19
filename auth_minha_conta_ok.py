import hashlib
import hmac
import os
import sqlite3
from pathlib import Path

import streamlit as st


CAMINHO_BANCO = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "entradapro_users.db"
)


def _conectar_banco():
    CAMINHO_BANCO.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    conexao = sqlite3.connect(
        CAMINHO_BANCO
    )

    conexao.row_factory = sqlite3.Row

    return conexao


def inicializar_banco():
    with _conectar_banco() as conexao:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha_hash TEXT NOT NULL,
                senha_salt TEXT NOT NULL,
                plano TEXT NOT NULL DEFAULT 'FREE',
                ativo INTEGER NOT NULL DEFAULT 1,
                criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conexao.commit()


def _normalizar_email(email):
    return str(
        email
    ).strip().lower()


def _gerar_hash_senha(
    senha,
    salt=None
):
    if salt is None:
        salt_bytes = os.urandom(
            32
        )

    else:
        salt_bytes = bytes.fromhex(
            salt
        )

    senha_hash = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode(
            "utf-8"
        ),
        salt_bytes,
        200_000
    )

    return (
        senha_hash.hex(),
        salt_bytes.hex()
    )


def _validar_senha(
    senha,
    senha_hash_salva,
    senha_salt_salva
):
    senha_hash_atual, _ = (
        _gerar_hash_senha(
            senha=senha,
            salt=senha_salt_salva
        )
    )

    return hmac.compare_digest(
        senha_hash_atual,
        senha_hash_salva
    )


def _buscar_usuario_por_email(
    email
):
    email_normalizado = (
        _normalizar_email(
            email
        )
    )

    with _conectar_banco() as conexao:
        usuario = conexao.execute(
            """
            SELECT
                id,
                nome,
                email,
                senha_hash,
                senha_salt,
                plano,
                ativo
            FROM usuarios
            WHERE email = ?
            """,
            (
                email_normalizado,
            )
        ).fetchone()

    return usuario


def cadastrar_usuario(
    nome,
    email,
    senha,
    confirmar_senha
):
    nome = str(
        nome
    ).strip()

    email = _normalizar_email(
        email
    )

    senha = str(
        senha
    )

    confirmar_senha = str(
        confirmar_senha
    )

    if len(nome) < 2:
        return (
            False,
            "Informe seu nome."
        )

    if (
        not email
        or "@" not in email
        or "." not in email
    ):
        return (
            False,
            "Informe um e-mail válido."
        )

    if len(senha) < 8:
        return (
            False,
            "A senha deve ter pelo menos 8 caracteres."
        )

    if senha != confirmar_senha:
        return (
            False,
            "As senhas não coincidem."
        )

    usuario_existente = (
        _buscar_usuario_por_email(
            email
        )
    )

    if usuario_existente:
        return (
            False,
            "Já existe uma conta com esse e-mail."
        )

    senha_hash, senha_salt = (
        _gerar_hash_senha(
            senha
        )
    )

    try:
        with _conectar_banco() as conexao:
            conexao.execute(
                """
                INSERT INTO usuarios (
                    nome,
                    email,
                    senha_hash,
                    senha_salt,
                    plano,
                    ativo
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    nome,
                    email,
                    senha_hash,
                    senha_salt,
                    "FREE",
                    1
                )
            )

            conexao.commit()

    except sqlite3.IntegrityError:
        return (
            False,
            "Já existe uma conta com esse e-mail."
        )

    return (
        True,
        "Conta criada com sucesso."
    )


def autenticar_usuario(
    email,
    senha
):
    email = _normalizar_email(
        email
    )

    usuario = (
        _buscar_usuario_por_email(
            email
        )
    )

    if not usuario:
        return None

    if int(
        usuario["ativo"]
    ) != 1:
        return None

    senha_valida = (
        _validar_senha(
            senha=senha,
            senha_hash_salva=usuario[
                "senha_hash"
            ],
            senha_salt_salva=usuario[
                "senha_salt"
            ]
        )
    )

    if not senha_valida:
        return None

    return {
        "id": usuario[
            "id"
        ],
        "nome": usuario[
            "nome"
        ],
        "email": usuario[
            "email"
        ],
        "plano": usuario[
            "plano"
        ]
    }



def alterar_senha_usuario(usuario_id, senha_atual, nova_senha, confirmar_nova_senha):
    senha_atual = str(senha_atual)
    nova_senha = str(nova_senha)
    confirmar_nova_senha = str(confirmar_nova_senha)

    if not senha_atual:
        return False, "Informe sua senha atual."
    if len(nova_senha) < 8:
        return False, "A nova senha deve ter pelo menos 8 caracteres."
    if nova_senha != confirmar_nova_senha:
        return False, "As novas senhas não coincidem."
    if nova_senha == senha_atual:
        return False, "A nova senha deve ser diferente da senha atual."

    with _conectar_banco() as conexao:
        usuario = conexao.execute(
            """
            SELECT senha_hash, senha_salt, ativo
            FROM usuarios
            WHERE id = ?
            """,
            (usuario_id,)
        ).fetchone()

        if not usuario:
            return False, "Usuário não encontrado."
        if int(usuario["ativo"]) != 1:
            return False, "Esta conta está desativada."

        if not _validar_senha(
            senha=senha_atual,
            senha_hash_salva=usuario["senha_hash"],
            senha_salt_salva=usuario["senha_salt"]
        ):
            return False, "A senha atual está incorreta."

        novo_hash, novo_salt = _gerar_hash_senha(nova_senha)
        conexao.execute(
            """
            UPDATE usuarios
            SET senha_hash = ?, senha_salt = ?
            WHERE id = ?
            """,
            (novo_hash, novo_salt, usuario_id)
        )
        conexao.commit()

    return True, "Senha alterada com sucesso."


def renderizar_minha_conta():
    usuario = obter_usuario_logado()
    if not usuario:
        return

    st.markdown("### 👤 Minha Conta")
    st.caption("Consulte seus dados e altere sua senha.")

    with st.container(border=True):
        st.markdown(f"**Nome:** {usuario['nome']}")
        st.markdown(f"**E-mail:** {usuario['email']}")
        st.markdown(f"**Plano:** {usuario['plano']}")

    st.markdown("#### 🔐 Alterar senha")

    with st.form("form_alterar_senha"):
        senha_atual = st.text_input("Senha atual", type="password")
        nova_senha = st.text_input(
            "Nova senha",
            type="password",
            placeholder="Mínimo de 8 caracteres"
        )
        confirmar = st.text_input("Confirmar nova senha", type="password")
        alterar = st.form_submit_button(
            "Alterar senha",
            use_container_width=True
        )

    if alterar:
        sucesso, mensagem = alterar_senha_usuario(
            usuario_id=usuario["id"],
            senha_atual=senha_atual,
            nova_senha=nova_senha,
            confirmar_nova_senha=confirmar
        )
        if sucesso:
            st.success(mensagem)
        else:
            st.error(mensagem)



def inicializar_estado_autenticacao():
    if (
        "usuario_autenticado"
        not in st.session_state
    ):
        st.session_state.usuario_autenticado = (
            False
        )

    if (
        "usuario"
        not in st.session_state
    ):
        st.session_state.usuario = (
            None
        )

    if (
        "tela_auth"
        not in st.session_state
    ):
        st.session_state.tela_auth = (
            "login"
        )


def usuario_esta_autenticado():
    return bool(
        st.session_state.get(
            "usuario_autenticado",
            False
        )
    )


def obter_usuario_logado():
    return st.session_state.get(
        "usuario"
    )


def fazer_logout():
    st.session_state.usuario_autenticado = (
        False
    )

    st.session_state.usuario = (
        None
    )

    st.session_state.tela_auth = (
        "login"
    )

    st.rerun()


def _renderizar_cabecalho_auth():
    st.html(
        """
        <div style="
            text-align:center;
            margin-top:25px;
            margin-bottom:28px;
        ">
            <div style="
                font-size:38px;
                font-weight:900;
                color:#ffffff;
                line-height:1;
            ">
                Entrada<span style="color:#53d99f;">Pro</span>
            </div>

            <div style="
                margin-top:10px;
                color:#91a4b8;
                font-size:14px;
            ">
                Football Intelligence
            </div>
        </div>
        """
    )


def _renderizar_login():
    st.markdown(
        "### Entrar"
    )

    st.caption(
        "Acesse sua conta para continuar."
    )

    with st.form(
        "form_login"
    ):
        email = st.text_input(
            "E-mail",
            placeholder=(
                "seuemail@exemplo.com"
            )
        )

        senha = st.text_input(
            "Senha",
            type="password",
            placeholder="Sua senha"
        )

        enviar = st.form_submit_button(
            "Entrar",
            use_container_width=True
        )

    if enviar:
        usuario = autenticar_usuario(
            email=email,
            senha=senha
        )

        if not usuario:
            st.error(
                "E-mail ou senha inválidos."
            )

        else:
            st.session_state.usuario_autenticado = (
                True
            )

            st.session_state.usuario = (
                usuario
            )

            st.rerun()

    st.divider()

    if st.button(
        "Criar conta",
        use_container_width=True,
        key="abrir_cadastro"
    ):
        st.session_state.tela_auth = (
            "cadastro"
        )

        st.rerun()


def _renderizar_cadastro():
    st.markdown(
        "### Criar conta"
    )

    st.caption(
        "Cadastre-se para acessar o EntradaPro."
    )

    with st.form(
        "form_cadastro"
    ):
        nome = st.text_input(
            "Nome",
            placeholder="Seu nome"
        )

        email = st.text_input(
            "E-mail",
            placeholder=(
                "seuemail@exemplo.com"
            )
        )

        senha = st.text_input(
            "Senha",
            type="password",
            placeholder=(
                "Mínimo de 8 caracteres"
            )
        )

        confirmar_senha = st.text_input(
            "Confirmar senha",
            type="password"
        )

        cadastrar = (
            st.form_submit_button(
                "Criar minha conta",
                use_container_width=True
            )
        )

    if cadastrar:
        sucesso, mensagem = (
            cadastrar_usuario(
                nome=nome,
                email=email,
                senha=senha,
                confirmar_senha=(
                    confirmar_senha
                )
            )
        )

        if sucesso:
            st.success(
                mensagem
            )

            st.info(
                "Sua conta foi criada no plano FREE."
            )

            st.session_state.tela_auth = (
                "login"
            )

            st.rerun()

        else:
            st.error(
                mensagem
            )

    st.divider()

    if st.button(
        "Já tenho uma conta",
        use_container_width=True,
        key="voltar_login"
    ):
        st.session_state.tela_auth = (
            "login"
        )

        st.rerun()


def renderizar_autenticacao():
    inicializar_banco()
    inicializar_estado_autenticacao()

    if usuario_esta_autenticado():
        return True

    coluna_esquerda, coluna_centro, coluna_direita = (
        st.columns(
            [1.3, 1, 1.3]
        )
    )

    with coluna_centro:
        _renderizar_cabecalho_auth()

        with st.container(
            border=True
        ):
            if (
                st.session_state.tela_auth
                == "cadastro"
            ):
                _renderizar_cadastro()

            else:
                _renderizar_login()

    return False


def renderizar_usuario_sidebar():
    usuario = obter_usuario_logado()

    if not usuario:
        return

    with st.sidebar:
        st.divider()
        st.caption("CONTA")
        st.markdown(f"**{usuario['nome']}**")
        st.caption(usuario["email"])
        st.caption(f"Plano: {usuario['plano']}")

        if st.button(
            "Minha Conta",
            use_container_width=True,
            key="minha_conta"
        ):
            st.session_state.mostrar_minha_conta = (
                not st.session_state.get("mostrar_minha_conta", False)
            )
            st.rerun()

        if st.session_state.get("mostrar_minha_conta", False):
            renderizar_minha_conta()

        if st.button(
            "Sair",
            use_container_width=True,
            key="logout"
        ):
            fazer_logout()