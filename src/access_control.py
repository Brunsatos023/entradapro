import streamlit as st


PLANO_FREE = "FREE"
PLANO_PRO = "PRO"


def obter_plano_usuario():
    usuario = st.session_state.get(
        "usuario"
    )

    if not usuario:
        return PLANO_FREE

    plano = usuario.get(
        "plano",
        PLANO_FREE
    )

    return str(
        plano
    ).strip().upper()


def usuario_eh_free():
    return (
        obter_plano_usuario()
        == PLANO_FREE
    )


def usuario_eh_pro():
    return (
        obter_plano_usuario()
        == PLANO_PRO
    )


def recurso_disponivel_para_pro():
    return usuario_eh_pro()


def renderizar_bloqueio_pro(
    titulo="Recurso exclusivo PRO",
    mensagem=(
        "Este recurso está disponível "
        "no plano EntradaPro PRO."
    )
):
    st.warning(
        f"🔒 {titulo}"
    )

    st.caption(
        mensagem
    )

    st.page_link(
        "pages/2_Assinatura_PRO.py",
        label="⭐ Conhecer o EntradaPro PRO",
        use_container_width=True
    )


def renderizar_selo_plano():
    plano = obter_plano_usuario()

    if plano == PLANO_PRO:
        st.success(
            "⭐ Plano PRO"
        )

    else:
        st.info(
            "Plano FREE"
        )