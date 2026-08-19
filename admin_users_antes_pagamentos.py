import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

from auth import autenticar_usuario


CAMINHO_BANCO = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "entradapro_users.db"
)


def conectar_banco():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao


def inicializar_estado_admin():
    if "admin_autenticado" not in st.session_state:
        st.session_state.admin_autenticado = False

    if "admin_usuario" not in st.session_state:
        st.session_state.admin_usuario = None


def buscar_permissao_admin(usuario_id):
    with conectar_banco() as conexao:
        resultado = conexao.execute(
            """
            SELECT
                id,
                nome,
                usuario,
                email,
                plano,
                ativo,
                admin
            FROM usuarios
            WHERE id = ?
            """,
            (usuario_id,)
        ).fetchone()

    if not resultado:
        return None

    return dict(resultado)


def usuario_tem_permissao_admin(usuario_id):
    usuario = buscar_permissao_admin(usuario_id)

    if not usuario:
        return False

    if int(usuario["ativo"]) != 1:
        return False

    return int(usuario["admin"]) == 1


def fazer_logout_admin():
    st.session_state.admin_autenticado = False
    st.session_state.admin_usuario = None
    st.rerun()


def renderizar_login_admin():
    st.markdown("## 🔐 Acesso administrativo")
    st.caption(
        "Entre com uma conta autorizada como administrador."
    )

    coluna_esquerda, coluna_centro, coluna_direita = st.columns(
        [1.2, 1, 1.2]
    )

    with coluna_centro:
        with st.container(border=True):
            with st.form("form_login_admin"):
                nome_usuario = st.text_input(
                    "Usuário",
                    placeholder="Seu nome de usuário"
                )

                senha = st.text_input(
                    "Senha",
                    type="password",
                    placeholder="Sua senha"
                )

                entrar = st.form_submit_button(
                    "Entrar no painel",
                    use_container_width=True
                )

            if entrar:
                usuario = autenticar_usuario(
                    usuario=nome_usuario,
                    senha=senha
                )

                if not usuario:
                    st.error(
                        "Usuário ou senha inválidos."
                    )
                    return False

                if not usuario_tem_permissao_admin(
                    usuario["id"]
                ):
                    st.error(
                        "Acesso não autorizado."
                    )
                    return False

                usuario_admin = buscar_permissao_admin(
                    usuario["id"]
                )

                st.session_state.admin_autenticado = True
                st.session_state.admin_usuario = usuario_admin
                st.rerun()

    return False


def garantir_acesso_admin():
    inicializar_estado_admin()

    if not st.session_state.get(
        "admin_autenticado",
        False
    ):
        renderizar_login_admin()
        return False

    usuario = st.session_state.get("admin_usuario")

    if not usuario:
        fazer_logout_admin()
        return False

    permissao_atual = buscar_permissao_admin(
        usuario["id"]
    )

    if not permissao_atual:
        fazer_logout_admin()
        return False

    if (
        int(permissao_atual["ativo"]) != 1
        or int(permissao_atual["admin"]) != 1
    ):
        st.session_state.admin_autenticado = False
        st.session_state.admin_usuario = None
        st.error(
            "Sua permissão administrativa não está mais ativa."
        )
        return False

    st.session_state.admin_usuario = permissao_atual
    return True


def listar_usuarios():
    with conectar_banco() as conexao:
        usuarios = conexao.execute(
            """
            SELECT
                id,
                nome,
                usuario,
                email,
                plano,
                ativo,
                admin,
                criado_em
            FROM usuarios
            ORDER BY criado_em DESC
            """
        ).fetchall()

    return [dict(usuario) for usuario in usuarios]


def buscar_usuario_por_id(usuario_id):
    with conectar_banco() as conexao:
        usuario = conexao.execute(
            """
            SELECT
                id,
                nome,
                usuario,
                email,
                plano,
                ativo,
                admin,
                criado_em
            FROM usuarios
            WHERE id = ?
            """,
            (usuario_id,)
        ).fetchone()

    if not usuario:
        return None

    return dict(usuario)


def alterar_plano(usuario_id, novo_plano):
    novo_plano = str(novo_plano).strip().upper()

    if novo_plano not in {"FREE", "PRO"}:
        return False, "Plano inválido."

    with conectar_banco() as conexao:
        cursor = conexao.execute(
            """
            UPDATE usuarios
            SET plano = ?
            WHERE id = ?
            """,
            (novo_plano, usuario_id)
        )
        conexao.commit()

    if cursor.rowcount == 0:
        return False, "Usuário não encontrado."

    return True, f"Plano alterado para {novo_plano}."


def alterar_status_conta(usuario_id, ativo):
    valor_ativo = 1 if ativo else 0

    usuario_alvo = buscar_usuario_por_id(usuario_id)

    if not usuario_alvo:
        return False, "Usuário não encontrado."

    admin_logado = st.session_state.get("admin_usuario")

    if (
        admin_logado
        and usuario_id == admin_logado["id"]
        and not ativo
    ):
        return (
            False,
            "Você não pode desativar a própria conta administrativa."
        )

    with conectar_banco() as conexao:
        cursor = conexao.execute(
            """
            UPDATE usuarios
            SET ativo = ?
            WHERE id = ?
            """,
            (valor_ativo, usuario_id)
        )
        conexao.commit()

    if cursor.rowcount == 0:
        return False, "Usuário não encontrado."

    return (
        True,
        "Conta ativada com sucesso."
        if ativo
        else "Conta desativada com sucesso."
    )


def montar_dataframe(usuarios):
    linhas = []

    for usuario in usuarios:
        linhas.append(
            {
                "ID": usuario["id"],
                "Nome": usuario["nome"],
                "Usuário": (
                    f"@{usuario['usuario']}"
                    if usuario["usuario"]
                    else "-"
                ),
                "E-mail": usuario["email"],
                "Plano": usuario["plano"],
                "Status": (
                    "Ativo"
                    if int(usuario["ativo"]) == 1
                    else "Inativo"
                ),
                "Admin": (
                    "Sim"
                    if int(usuario["admin"]) == 1
                    else "Não"
                ),
                "Criado em": usuario["criado_em"]
            }
        )

    return pd.DataFrame(linhas)


def aplicar_filtros(
    usuarios,
    filtro_plano,
    filtro_status,
    busca
):
    resultado = []
    busca = str(busca).strip().lower()

    for usuario in usuarios:
        if (
            filtro_plano != "Todos"
            and usuario["plano"] != filtro_plano
        ):
            continue

        if filtro_status != "Todos":
            status_atual = (
                "Ativo"
                if int(usuario["ativo"]) == 1
                else "Inativo"
            )

            if status_atual != filtro_status:
                continue

        if busca:
            dados_busca = (
                f"{usuario['nome']} "
                f"{usuario['usuario']} "
                f"{usuario['email']}"
            ).lower()

            if busca not in dados_busca:
                continue

        resultado.append(usuario)

    return resultado


def renderizar_resumo(usuarios):
    total = len(usuarios)

    total_free = sum(
        1
        for usuario in usuarios
        if usuario["plano"] == "FREE"
    )

    total_pro = sum(
        1
        for usuario in usuarios
        if usuario["plano"] == "PRO"
    )

    total_ativos = sum(
        1
        for usuario in usuarios
        if int(usuario["ativo"]) == 1
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Usuários", total)

    with col2:
        st.metric("FREE", total_free)

    with col3:
        st.metric("PRO", total_pro)

    with col4:
        st.metric("Ativos", total_ativos)


def renderizar_edicao_usuario(usuarios):
    if not usuarios:
        st.info("Nenhum usuário disponível.")
        return

    opcoes = {}

    for usuario in usuarios:
        nome_exibicao = (
            f"{usuario['id']} | "
            f"@{usuario['usuario']} | "
            f"{usuario['nome']}"
        )
        opcoes[nome_exibicao] = usuario["id"]

    st.markdown("## Gerenciar usuário")

    selecionado = st.selectbox(
        "Selecione um usuário",
        options=list(opcoes.keys())
    )

    usuario_id = opcoes[selecionado]
    usuario = buscar_usuario_por_id(usuario_id)

    if not usuario:
        st.error("Usuário não encontrado.")
        return

    with st.container(border=True):
        st.markdown(f"**Nome:** {usuario['nome']}")
        st.markdown(f"**Usuário:** @{usuario['usuario']}")
        st.markdown(f"**E-mail:** {usuario['email']}")
        st.markdown(f"**Plano atual:** {usuario['plano']}")

        status_texto = (
            "Ativo"
            if int(usuario["ativo"]) == 1
            else "Inativo"
        )

        st.markdown(f"**Status:** {status_texto}")

        admin_texto = (
            "Sim"
            if int(usuario["admin"]) == 1
            else "Não"
        )

        st.markdown(
            f"**Administrador:** {admin_texto}"
        )

        st.markdown(
            f"**Criado em:** {usuario['criado_em']}"
        )

    st.markdown("### Alterar plano")

    novo_plano = st.selectbox(
        "Plano",
        options=["FREE", "PRO"],
        index=0 if usuario["plano"] == "FREE" else 1,
        key=f"plano_usuario_{usuario_id}"
    )

    if st.button(
        "Salvar plano",
        use_container_width=True,
        key=f"salvar_plano_{usuario_id}"
    ):
        sucesso, mensagem = alterar_plano(
            usuario_id=usuario_id,
            novo_plano=novo_plano
        )

        if sucesso:
            st.success(mensagem)
            st.rerun()
        else:
            st.error(mensagem)

    st.markdown("### Status da conta")

    conta_ativa = int(usuario["ativo"]) == 1
    admin_logado = st.session_state.get("admin_usuario")

    propria_conta = bool(
        admin_logado
        and usuario_id == admin_logado["id"]
    )

    if conta_ativa:
        if propria_conta:
            st.info(
                "Sua própria conta administrativa "
                "não pode ser desativada por este painel."
            )
        else:
            if st.button(
                "Desativar conta",
                use_container_width=True,
                key=f"desativar_{usuario_id}"
            ):
                sucesso, mensagem = alterar_status_conta(
                    usuario_id=usuario_id,
                    ativo=False
                )

                if sucesso:
                    st.success(mensagem)
                    st.rerun()
                else:
                    st.error(mensagem)

    else:
        if st.button(
            "Ativar conta",
            use_container_width=True,
            key=f"ativar_{usuario_id}"
        ):
            sucesso, mensagem = alterar_status_conta(
                usuario_id=usuario_id,
                ativo=True
            )

            if sucesso:
                st.success(mensagem)
                st.rerun()
            else:
                st.error(mensagem)


def renderizar_topo_admin():
    admin = st.session_state.get("admin_usuario")

    col1, col2 = st.columns([6, 1])

    with col1:
        st.title("⚙️ EntradaPro Admin")
        st.caption(
            "Painel administrativo de usuários."
        )

    with col2:
        if admin:
            st.caption("ADMIN")
            st.markdown(
                f"**@{admin['usuario']}**"
            )

        if st.button(
            "Sair",
            use_container_width=True,
            key="logout_admin"
        ):
            fazer_logout_admin()


def main():
    st.set_page_config(
        page_title="EntradaPro Admin",
        page_icon="⚙️",
        layout="wide"
    )

    inicializar_estado_admin()

    if not garantir_acesso_admin():
        return

    renderizar_topo_admin()

    try:
        usuarios = listar_usuarios()
    except Exception as erro:
        st.error(
            "Não foi possível carregar "
            f"os usuários: {erro}"
        )
        st.stop()

    renderizar_resumo(usuarios)

    st.divider()
    st.markdown("## Usuários cadastrados")

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        filtro_plano = st.selectbox(
            "Plano",
            options=["Todos", "FREE", "PRO"]
        )

    with col2:
        filtro_status = st.selectbox(
            "Status",
            options=["Todos", "Ativo", "Inativo"]
        )

    with col3:
        busca = st.text_input(
            "Buscar",
            placeholder="Nome, usuário ou e-mail"
        )

    usuarios_filtrados = aplicar_filtros(
        usuarios=usuarios,
        filtro_plano=filtro_plano,
        filtro_status=filtro_status,
        busca=busca
    )

    dataframe = montar_dataframe(
        usuarios_filtrados
    )

    if dataframe.empty:
        st.info("Nenhum usuário encontrado.")
    else:
        st.dataframe(
            dataframe,
            use_container_width=True,
            hide_index=True
        )

    st.divider()
    renderizar_edicao_usuario(usuarios)


if __name__ == "__main__":
    main()