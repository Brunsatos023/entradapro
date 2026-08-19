import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st


CAMINHO_BANCO = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "entradapro_users.db"
)


def conectar_banco():
    conexao = sqlite3.connect(
        CAMINHO_BANCO
    )

    conexao.row_factory = sqlite3.Row

    return conexao


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
                criado_em
            FROM usuarios
            ORDER BY criado_em DESC
            """
        ).fetchall()

    return [
        dict(
            usuario
        )
        for usuario in usuarios
    ]


def buscar_usuario_por_id(
    usuario_id
):
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
                criado_em
            FROM usuarios
            WHERE id = ?
            """,
            (
                usuario_id,
            )
        ).fetchone()

    if not usuario:
        return None

    return dict(
        usuario
    )


def alterar_plano(
    usuario_id,
    novo_plano
):
    novo_plano = str(
        novo_plano
    ).strip().upper()

    if novo_plano not in {
        "FREE",
        "PRO"
    }:
        return (
            False,
            "Plano inválido."
        )

    with conectar_banco() as conexao:
        cursor = conexao.execute(
            """
            UPDATE usuarios
            SET plano = ?
            WHERE id = ?
            """,
            (
                novo_plano,
                usuario_id
            )
        )

        conexao.commit()

    if cursor.rowcount == 0:
        return (
            False,
            "Usuário não encontrado."
        )

    return (
        True,
        f"Plano alterado para {novo_plano}."
    )


def alterar_status_conta(
    usuario_id,
    ativo
):
    valor_ativo = (
        1
        if ativo
        else 0
    )

    with conectar_banco() as conexao:
        cursor = conexao.execute(
            """
            UPDATE usuarios
            SET ativo = ?
            WHERE id = ?
            """,
            (
                valor_ativo,
                usuario_id
            )
        )

        conexao.commit()

    if cursor.rowcount == 0:
        return (
            False,
            "Usuário não encontrado."
        )

    if ativo:
        mensagem = (
            "Conta ativada com sucesso."
        )

    else:
        mensagem = (
            "Conta desativada com sucesso."
        )

    return (
        True,
        mensagem
    )


def montar_dataframe(
    usuarios
):
    linhas = []

    for usuario in usuarios:
        linhas.append(
            {
                "ID": usuario[
                    "id"
                ],
                "Nome": usuario[
                    "nome"
                ],
                "Usuário": (
                    f"@{usuario['usuario']}"
                    if usuario[
                        "usuario"
                    ]
                    else "-"
                ),
                "E-mail": usuario[
                    "email"
                ],
                "Plano": usuario[
                    "plano"
                ],
                "Status": (
                    "Ativo"
                    if int(
                        usuario[
                            "ativo"
                        ]
                    ) == 1
                    else "Inativo"
                ),
                "Criado em": usuario[
                    "criado_em"
                ]
            }
        )

    return pd.DataFrame(
        linhas
    )


def aplicar_filtros(
    usuarios,
    filtro_plano,
    filtro_status,
    busca
):
    resultado = []

    busca = str(
        busca
    ).strip().lower()

    for usuario in usuarios:
        if (
            filtro_plano
            != "Todos"
        ):
            if (
                usuario[
                    "plano"
                ]
                != filtro_plano
            ):
                continue

        if (
            filtro_status
            != "Todos"
        ):
            status_atual = (
                "Ativo"
                if int(
                    usuario[
                        "ativo"
                    ]
                ) == 1
                else "Inativo"
            )

            if (
                status_atual
                != filtro_status
            ):
                continue

        if busca:
            dados_busca = (
                f"{usuario['nome']} "
                f"{usuario['usuario']} "
                f"{usuario['email']}"
            ).lower()

            if (
                busca
                not in dados_busca
            ):
                continue

        resultado.append(
            usuario
        )

    return resultado


def renderizar_resumo(
    usuarios
):
    total = len(
        usuarios
    )

    total_free = sum(
        1
        for usuario in usuarios
        if usuario[
            "plano"
        ] == "FREE"
    )

    total_pro = sum(
        1
        for usuario in usuarios
        if usuario[
            "plano"
        ] == "PRO"
    )

    total_ativos = sum(
        1
        for usuario in usuarios
        if int(
            usuario[
                "ativo"
            ]
        ) == 1
    )

    col1, col2, col3, col4 = (
        st.columns(
            4
        )
    )

    with col1:
        st.metric(
            "Usuários",
            total
        )

    with col2:
        st.metric(
            "FREE",
            total_free
        )

    with col3:
        st.metric(
            "PRO",
            total_pro
        )

    with col4:
        st.metric(
            "Ativos",
            total_ativos
        )


def renderizar_edicao_usuario(
    usuarios
):
    if not usuarios:
        st.info(
            "Nenhum usuário disponível."
        )

        return

    opcoes = {}

    for usuario in usuarios:
        nome_exibicao = (
            f"{usuario['id']} | "
            f"@{usuario['usuario']} | "
            f"{usuario['nome']}"
        )

        opcoes[
            nome_exibicao
        ] = usuario[
            "id"
        ]

    st.markdown(
        "## Gerenciar usuário"
    )

    selecionado = st.selectbox(
        "Selecione um usuário",
        options=list(
            opcoes.keys()
        )
    )

    usuario_id = opcoes[
        selecionado
    ]

    usuario = buscar_usuario_por_id(
        usuario_id
    )

    if not usuario:
        st.error(
            "Usuário não encontrado."
        )

        return

    with st.container(
        border=True
    ):
        st.markdown(
            f"**Nome:** "
            f"{usuario['nome']}"
        )

        st.markdown(
            f"**Usuário:** "
            f"@{usuario['usuario']}"
        )

        st.markdown(
            f"**E-mail:** "
            f"{usuario['email']}"
        )

        st.markdown(
            f"**Plano atual:** "
            f"{usuario['plano']}"
        )

        status_texto = (
            "Ativo"
            if int(
                usuario[
                    "ativo"
                ]
            ) == 1
            else "Inativo"
        )

        st.markdown(
            f"**Status:** "
            f"{status_texto}"
        )

        st.markdown(
            f"**Criado em:** "
            f"{usuario['criado_em']}"
        )

    st.markdown(
        "### Alterar plano"
    )

    novo_plano = st.selectbox(
        "Plano",
        options=[
            "FREE",
            "PRO"
        ],
        index=(
            0
            if usuario[
                "plano"
            ] == "FREE"
            else 1
        ),
        key=(
            f"plano_usuario_"
            f"{usuario_id}"
        )
    )

    if st.button(
        "Salvar plano",
        use_container_width=True,
        key=(
            f"salvar_plano_"
            f"{usuario_id}"
        )
    ):
        sucesso, mensagem = (
            alterar_plano(
                usuario_id=(
                    usuario_id
                ),
                novo_plano=(
                    novo_plano
                )
            )
        )

        if sucesso:
            st.success(
                mensagem
            )

            st.rerun()

        else:
            st.error(
                mensagem
            )

    st.markdown(
        "### Status da conta"
    )

    conta_ativa = (
        int(
            usuario[
                "ativo"
            ]
        )
        == 1
    )

    if conta_ativa:
        if st.button(
            "Desativar conta",
            use_container_width=True,
            key=(
                f"desativar_"
                f"{usuario_id}"
            )
        ):
            sucesso, mensagem = (
                alterar_status_conta(
                    usuario_id=(
                        usuario_id
                    ),
                    ativo=False
                )
            )

            if sucesso:
                st.success(
                    mensagem
                )

                st.rerun()

            else:
                st.error(
                    mensagem
                )

    else:
        if st.button(
            "Ativar conta",
            use_container_width=True,
            key=(
                f"ativar_"
                f"{usuario_id}"
            )
        ):
            sucesso, mensagem = (
                alterar_status_conta(
                    usuario_id=(
                        usuario_id
                    ),
                    ativo=True
                )
            )

            if sucesso:
                st.success(
                    mensagem
                )

                st.rerun()

            else:
                st.error(
                    mensagem
                )


def main():
    st.set_page_config(
        page_title=(
            "EntradaPro Admin"
        ),
        page_icon="⚙️",
        layout="wide"
    )

    st.title(
        "⚙️ EntradaPro Admin"
    )

    st.caption(
        "Painel administrativo de usuários."
    )

    try:
        usuarios = (
            listar_usuarios()
        )

    except Exception as erro:
        st.error(
            "Não foi possível carregar "
            f"os usuários: {erro}"
        )

        st.stop()

    renderizar_resumo(
        usuarios
    )

    st.divider()

    st.markdown(
        "## Usuários cadastrados"
    )

    col1, col2, col3 = (
        st.columns(
            [
                1,
                1,
                2
            ]
        )
    )

    with col1:
        filtro_plano = (
            st.selectbox(
                "Plano",
                options=[
                    "Todos",
                    "FREE",
                    "PRO"
                ]
            )
        )

    with col2:
        filtro_status = (
            st.selectbox(
                "Status",
                options=[
                    "Todos",
                    "Ativo",
                    "Inativo"
                ]
            )
        )

    with col3:
        busca = st.text_input(
            "Buscar",
            placeholder=(
                "Nome, usuário ou e-mail"
            )
        )

    usuarios_filtrados = (
        aplicar_filtros(
            usuarios=usuarios,
            filtro_plano=(
                filtro_plano
            ),
            filtro_status=(
                filtro_status
            ),
            busca=busca
        )
    )

    dataframe = (
        montar_dataframe(
            usuarios_filtrados
        )
    )

    if dataframe.empty:
        st.info(
            "Nenhum usuário encontrado."
        )

    else:
        st.dataframe(
            dataframe,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    renderizar_edicao_usuario(
        usuarios
    )


if __name__ == "__main__":
    main()