import hashlib
import hmac
import os
import re
import sqlite3
import secrets
from datetime import datetime, timedelta
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

        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS recuperacao_senha (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                token_hash TEXT NOT NULL,
                expira_em DATETIME NOT NULL,
                usado INTEGER NOT NULL DEFAULT 0,
                criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
            """
        )

        colunas_usuarios = conexao.execute(
            "PRAGMA table_info(usuarios)"
        ).fetchall()

        nomes_colunas = {
            coluna["name"]
            for coluna in colunas_usuarios
        }

        if "usuario" not in nomes_colunas:
            conexao.execute(
                """
                ALTER TABLE usuarios
                ADD COLUMN usuario TEXT
                """
            )

        conexao.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_usuarios_usuario
            ON usuarios(usuario)
            """
        )

        conexao.commit()


def _normalizar_email(email):
    return str(
        email
    ).strip().lower()


def _normalizar_usuario(usuario):
    return str(
        usuario
    ).strip().lower()


def _usuario_valido(usuario):
    return bool(
        re.fullmatch(
            r"[a-z0-9._]{4,20}",
            usuario
        )
    )


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
                usuario,
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


def _buscar_usuario_por_nome_usuario(
    usuario
):
    usuario_normalizado = (
        _normalizar_usuario(
            usuario
        )
    )

    with _conectar_banco() as conexao:
        conta = conexao.execute(
            """
            SELECT
                id,
                nome,
                usuario,
                email,
                senha_hash,
                senha_salt,
                plano,
                ativo
            FROM usuarios
            WHERE usuario = ?
            """,
            (
                usuario_normalizado,
            )
        ).fetchone()

    return conta


def cadastrar_usuario(
    nome,
    usuario,
    email,
    senha,
    confirmar_senha
):
    nome = str(
        nome
    ).strip()

    usuario = _normalizar_usuario(
        usuario
    )

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

    if not _usuario_valido(
        usuario
    ):
        return (
            False,
            "O usuário deve ter de 4 a 20 caracteres e usar "
            "apenas letras minúsculas, números, ponto ou underline."
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

    if _buscar_usuario_por_nome_usuario(
        usuario
    ):
        return (
            False,
            "Esse nome de usuário já está em uso."
        )

    if _buscar_usuario_por_email(
        email
    ):
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
                    usuario,
                    email,
                    senha_hash,
                    senha_salt,
                    plano,
                    ativo
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    nome,
                    usuario,
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
            "Usuário ou e-mail já cadastrado."
        )

    return (
        True,
        "Conta criada com sucesso."
    )

def autenticar_usuario(
    usuario,
    senha
):
    usuario = _normalizar_usuario(
        usuario
    )

    conta = (
        _buscar_usuario_por_nome_usuario(
            usuario
        )
    )

    if not conta:
        return None

    if int(
        conta["ativo"]
    ) != 1:
        return None

    senha_valida = (
        _validar_senha(
            senha=senha,
            senha_hash_salva=conta[
                "senha_hash"
            ],
            senha_salt_salva=conta[
                "senha_salt"
            ]
        )
    )

    if not senha_valida:
        return None

    return {
        "id": conta[
            "id"
        ],
        "nome": conta[
            "nome"
        ],
        "usuario": conta[
            "usuario"
        ],
        "email": conta[
            "email"
        ],
        "plano": conta[
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
        st.markdown(f"**Usuário:** @{usuario['usuario']}")
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




def _hash_token_recuperacao(token):
    return hashlib.sha256(str(token).encode("utf-8")).hexdigest()


def solicitar_recuperacao_senha(email):
    email = _normalizar_email(email)
    usuario = _buscar_usuario_por_email(email)
    mensagem_padrao = (
        "Se o e-mail estiver cadastrado, "
        "um código de recuperação será gerado."
    )

    if not usuario or int(usuario["ativo"]) != 1:
        return True, mensagem_padrao, None

    codigo = f"{secrets.randbelow(1_000_000):06d}"
    token_hash = _hash_token_recuperacao(codigo)
    expira_em = datetime.now() + timedelta(minutes=15)

    with _conectar_banco() as conexao:
        conexao.execute(
            """
            UPDATE recuperacao_senha
            SET usado = 1
            WHERE usuario_id = ? AND usado = 0
            """,
            (usuario["id"],)
        )
        conexao.execute(
            """
            INSERT INTO recuperacao_senha (
                usuario_id, token_hash, expira_em, usado
            )
            VALUES (?, ?, ?, 0)
            """,
            (
                usuario["id"],
                token_hash,
                expira_em.isoformat(timespec="seconds")
            )
        )
        conexao.commit()

    return True, mensagem_padrao, codigo


def validar_codigo_recuperacao(email, codigo):
    email = _normalizar_email(email)
    codigo = str(codigo).strip()

    if not codigo:
        return False, "Informe o código de recuperação."

    usuario = _buscar_usuario_por_email(email)
    if not usuario:
        return False, "Código inválido ou expirado."

    token_hash = _hash_token_recuperacao(codigo)

    with _conectar_banco() as conexao:
        registro = conexao.execute(
            """
            SELECT id, token_hash, expira_em, usado
            FROM recuperacao_senha
            WHERE usuario_id = ? AND usado = 0
            ORDER BY id DESC
            LIMIT 1
            """,
            (usuario["id"],)
        ).fetchone()

    if not registro:
        return False, "Código inválido ou expirado."

    if not hmac.compare_digest(registro["token_hash"], token_hash):
        return False, "Código inválido ou expirado."

    try:
        expira_em = datetime.fromisoformat(registro["expira_em"])
    except ValueError:
        return False, "Código inválido ou expirado."

    if datetime.now() > expira_em:
        return False, "Código inválido ou expirado."

    return True, registro["id"]


def redefinir_senha_com_codigo(email, codigo, nova_senha, confirmar_nova_senha):
    nova_senha = str(nova_senha)
    confirmar_nova_senha = str(confirmar_nova_senha)

    if len(nova_senha) < 8:
        return False, "A nova senha deve ter pelo menos 8 caracteres."
    if nova_senha != confirmar_nova_senha:
        return False, "As novas senhas não coincidem."

    valido, resultado = validar_codigo_recuperacao(email, codigo)
    if not valido:
        return False, resultado

    recuperacao_id = resultado
    usuario = _buscar_usuario_por_email(email)
    if not usuario:
        return False, "Não foi possível redefinir a senha."

    novo_hash, novo_salt = _gerar_hash_senha(nova_senha)

    with _conectar_banco() as conexao:
        conexao.execute(
            """
            UPDATE usuarios
            SET senha_hash = ?, senha_salt = ?
            WHERE id = ?
            """,
            (novo_hash, novo_salt, usuario["id"])
        )
        conexao.execute(
            """
            UPDATE recuperacao_senha
            SET usado = 1
            WHERE id = ?
            """,
            (recuperacao_id,)
        )
        conexao.commit()

    return True, "Senha redefinida com sucesso."


def _renderizar_esqueci_senha():
    st.markdown("### Esqueci minha senha")
    st.caption(
        "Informe o e-mail da sua conta para gerar um código temporário."
    )

    with st.form("form_solicitar_recuperacao"):
        email = st.text_input(
            "E-mail",
            placeholder="seuemail@exemplo.com",
            key="email_recuperacao_input"
        )
        solicitar = st.form_submit_button(
            "Gerar código",
            use_container_width=True
        )

    if solicitar:
        sucesso, mensagem, codigo = solicitar_recuperacao_senha(email)
        if sucesso:
            st.info(mensagem)
            if codigo:
                st.session_state.email_recuperacao = _normalizar_email(email)
                st.session_state.codigo_recuperacao_dev = codigo
                st.session_state.tela_auth = "redefinir_senha"
                st.rerun()

    st.divider()
    if st.button(
        "Voltar ao login",
        use_container_width=True,
        key="voltar_login_recuperacao"
    ):
        st.session_state.tela_auth = "login"
        st.rerun()


def _renderizar_redefinir_senha():
    st.markdown("### Redefinir senha")
    st.caption(
        "Use o código temporário e crie uma nova senha."
    )

    codigo_dev = st.session_state.get("codigo_recuperacao_dev")
    if codigo_dev:
        st.warning(
            "MODO DE DESENVOLVIMENTO: "
            f"código de recuperação: {codigo_dev}"
        )
        st.caption(
            "Na versão publicada, este código será enviado ao e-mail "
            "do usuário e não será exibido na tela."
        )

    email = st.session_state.get("email_recuperacao", "")

    with st.form("form_redefinir_senha"):
        st.text_input(
            "E-mail",
            value=email,
            disabled=True
        )
        codigo = st.text_input(
            "Código de recuperação",
            placeholder="000000",
            max_chars=6
        )
        nova_senha = st.text_input(
            "Nova senha",
            type="password",
            placeholder="Mínimo de 8 caracteres"
        )
        confirmar_nova_senha = st.text_input(
            "Confirmar nova senha",
            type="password"
        )
        redefinir = st.form_submit_button(
            "Redefinir senha",
            use_container_width=True
        )

    if redefinir:
        sucesso, mensagem = redefinir_senha_com_codigo(
            email=email,
            codigo=codigo,
            nova_senha=nova_senha,
            confirmar_nova_senha=confirmar_nova_senha
        )
        if sucesso:
            st.success(mensagem)
            st.session_state.pop("codigo_recuperacao_dev", None)
            st.session_state.pop("email_recuperacao", None)
            st.session_state.tela_auth = "login"
        else:
            st.error(mensagem)

    st.divider()
    if st.button(
        "Voltar ao login",
        use_container_width=True,
        key="voltar_login_redefinir"
    ):
        st.session_state.tela_auth = "login"
        st.rerun()


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

    if (
        "modal_auth_aberto"
        not in st.session_state
    ):
        st.session_state.modal_auth_aberto = (
            False
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

    st.session_state.modal_auth_aberto = (
        False
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
        nome_usuario = st.text_input(
            "Usuário",
            placeholder="Seu nome de usuário"
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
            usuario=nome_usuario,
            senha=senha
        )

        if not usuario:
            st.error(
                "Usuário ou senha inválidos."
            )

        else:
            st.session_state.usuario_autenticado = (
                True
            )

            st.session_state.usuario = (
                usuario
            )

            st.rerun()

    if st.button(
        "Esqueci minha senha?",
        use_container_width=True,
        key="abrir_recuperacao_senha"
    ):
        st.session_state.tela_auth = (
            "esqueci_senha"
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

        nome_usuario = st.text_input(
            "Usuário",
            placeholder="Ex.: brunovini96",
            help=(
                "Use de 4 a 20 caracteres: letras minúsculas, "
                "números, ponto ou underline."
            )
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
                usuario=nome_usuario,
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

def abrir_autenticacao(tela="login"):
    inicializar_banco()
    inicializar_estado_autenticacao()

    if tela not in {"login", "cadastro"}:
        tela = "login"

    st.session_state.tela_auth = tela
    st.session_state.modal_auth_aberto = True


def fechar_autenticacao():
    st.session_state.modal_auth_aberto = False


def renderizar_acoes_visitante_topo():
    inicializar_estado_autenticacao()

    if usuario_esta_autenticado():
        return

    _, coluna_registrar, coluna_login = st.columns(
        [8, 1.25, 1]
    )

    with coluna_registrar:
        if st.button(
            "Registrar",
            use_container_width=True,
            key="topo_registrar"
        ):
            abrir_autenticacao("cadastro")
            st.rerun()

    with coluna_login:
        if st.button(
            "Login",
            use_container_width=True,
            key="topo_login"
        ):
            abrir_autenticacao("login")
            st.rerun()


@st.dialog("Acesse o EntradaPro", width="small")
def _dialogo_autenticacao():
    _renderizar_cabecalho_auth()

    if st.session_state.tela_auth == "cadastro":
        _renderizar_cadastro()
    elif st.session_state.tela_auth == "esqueci_senha":
        _renderizar_esqueci_senha()
    elif st.session_state.tela_auth == "redefinir_senha":
        _renderizar_redefinir_senha()
    else:
        _renderizar_login()

    st.divider()

    if st.button(
        "Continuar visualizando",
        use_container_width=True,
        key="fechar_modal_auth"
    ):
        fechar_autenticacao()
        st.rerun()


def renderizar_dialogo_autenticacao():
    inicializar_banco()
    inicializar_estado_autenticacao()

    if usuario_esta_autenticado():
        st.session_state.modal_auth_aberto = False
        return

    if st.session_state.get("modal_auth_aberto", False):
        _dialogo_autenticacao()


def exigir_autenticacao(tela="login"):
    if usuario_esta_autenticado():
        return True

    abrir_autenticacao(tela)
    return False



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

            elif (
                st.session_state.tela_auth
                == "esqueci_senha"
            ):
                _renderizar_esqueci_senha()

            elif (
                st.session_state.tela_auth
                == "redefinir_senha"
            ):
                _renderizar_redefinir_senha()

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
        st.caption(f"@{usuario['usuario']}")
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