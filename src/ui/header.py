import base64
from io import BytesIO
from pathlib import Path

import streamlit as st
from PIL import Image


def _obter_banner_base64():
    caminho_logo = (
        Path(__file__).resolve().parents[2]
        / "assets"
        / "logo_entradapro.png"
    )

    if not caminho_logo.exists():
        return None

    try:
        imagem = Image.open(caminho_logo)

        largura, altura = imagem.size

        if largura == 1536 and altura == 1024:
            imagem = imagem.crop(
                (
                    0,
                    130,
                    1536,
                    650
                )
            )
        else:
            proporcao_banner = 1536 / 520

            altura_banner = int(
                largura / proporcao_banner
            )

            altura_banner = min(
                altura_banner,
                altura
            )

            topo = max(
                0,
                int(
                    (altura - altura_banner)
                    * 0.34
                )
            )

            fundo = min(
                altura,
                topo + altura_banner
            )

            imagem = imagem.crop(
                (
                    0,
                    topo,
                    largura,
                    fundo
                )
            )

        buffer = BytesIO()

        imagem.save(
            buffer,
            format="PNG",
            optimize=True
        )

        return base64.b64encode(
            buffer.getvalue()
        ).decode(
            "utf-8"
        )

    except (
        OSError,
        ValueError
    ):
        return None


def renderizar_cabecalho():
    banner_base64 = _obter_banner_base64()

    if banner_base64:
        html = (
            '<div class="hero" '
            'style="'
            'padding:14px 16px 18px 16px;'
            'overflow:hidden;'
            '">'

            '<img '
            f'src="data:image/png;base64,{banner_base64}" '
            'alt="EntradaPro Football Intelligence" '
            'style="'
            'display:block;'
            'width:100%;'
            'height:auto;'
            'margin:0 auto;'
            'border-radius:14px;'
            '">'

            '<div '
            'style="'
            'text-align:center;'
            'margin-top:14px;'
            'color:#d7e2ed;'
            'font-size:15px;'
            'font-weight:600;'
            'line-height:1.5;'
            '">'
            'Análise inteligente de partidas, probabilidades '
            'e identificação de apostas de valor.'
            '</div>'

            '</div>'
        )

    else:
        html = (
            '<div class="hero">'
            '<p class="hero-title">'
            'Entrada<span class="hero-highlight">Pro</span>'
            '</p>'
            '<p class="hero-subtitle">'
            'Football Intelligence • '
            'Análise inteligente de partidas, probabilidades '
            'e identificação de apostas de valor.'
            '</p>'
            '</div>'
        )

    st.markdown(
        html,
        unsafe_allow_html=True
    )


def renderizar_partida(
    nome_mandante,
    nome_visitante
):
    html = (
        '<div class="match-header">'
        '<div class="match-label">'
        'Análise da partida'
        '</div>'
        '<div class="match-name">'
        f'{nome_mandante} &nbsp;&nbsp; x &nbsp;&nbsp; '
        f'{nome_visitante}'
        '</div>'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True
    )


def renderizar_estado_inicial():
    html = (
        '<div class="match-header">'
        '<div class="match-label">'
        'EntradaPro está pronto'
        '</div>'
        '<div class="match-name">'
        'Selecione os times e clique em '
        '<span style="color:#53d99f;">'
        '“Analisar partida”'
        '</span>'
        '</div>'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True
    )


def renderizar_titulo_secao(titulo):
    html = (
        '<div class="section-title">'
        f'{titulo}'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True
    )