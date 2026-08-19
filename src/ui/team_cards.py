import base64
import html
import mimetypes
from pathlib import Path

import streamlit as st

from ui.team_logo import obter_caminho_escudo


# =========================================================
# UTILITÁRIOS
# =========================================================

def limitar_score(score):
    """
    Limita um score entre 0 e 100.
    """
    try:
        score_convertido = float(score)
    except (TypeError, ValueError):
        return 0

    return max(
        0,
        min(
            int(round(score_convertido)),
            100
        )
    )


def formatar_score(score):
    """
    Formata um score com duas casas decimais.
    """
    try:
        return f"{float(score):.2f}"
    except (TypeError, ValueError):
        return "0.00"


def converter_imagem_para_base64(
    caminho_imagem
):
    """
    Converte um escudo local em Base64.
    """
    if not caminho_imagem:
        return None

    caminho = Path(
        caminho_imagem
    )

    if (
        not caminho.exists()
        or not caminho.is_file()
    ):
        return None

    try:
        conteudo_imagem = (
            caminho.read_bytes()
        )

        imagem_base64 = (
            base64.b64encode(
                conteudo_imagem
            ).decode(
                "utf-8"
            )
        )

        tipo_mime, _ = (
            mimetypes.guess_type(
                caminho.name
            )
        )

        if not tipo_mime:
            tipo_mime = "image/png"

        return (
            f"data:{tipo_mime};"
            f"base64,{imagem_base64}"
        )

    except OSError:
        return None


def criar_html_escudo(
    nome_time,
    largura=92
):
    """
    Cria o HTML do escudo do time.
    """
    caminho_escudo = (
        obter_caminho_escudo(
            nome_time
        )
    )

    imagem_base64 = (
        converter_imagem_para_base64(
            caminho_escudo
        )
    )

    nome_seguro = html.escape(
        str(nome_time)
    )

    if imagem_base64:
        return (
            '<div class="compare-team-logo-wrapper">'
            '<img '
            'class="compare-team-logo" '
            f'src="{imagem_base64}" '
            f'alt="Escudo do {nome_seguro}" '
            f'style="width:{largura}px;max-width:100%;">'
            "</div>"
        )

    return (
        '<div class="compare-team-logo-wrapper">'
        '<div class="compare-team-logo-fallback">'
        "⚽"
        "</div>"
        "</div>"
    )


def normalizar_confianca(
    confianca
):
    """
    Normaliza o texto de confiança.
    """
    return (
        str(confianca)
        .strip()
        .lower()
    )


def obter_classe_confianca(
    confianca
):
    """
    Retorna a classe visual da confiança.
    """
    confianca_normalizada = (
        normalizar_confianca(
            confianca
        )
    )

    if confianca_normalizada in {
        "muito alta",
        "alta"
    }:
        return "compare-confidence-high"

    if confianca_normalizada == "média":
        return "compare-confidence-medium"

    return "compare-confidence-low"


def obter_texto_diferenca(
    diferenca
):
    """
    Formata a diferença entre as inteligências.
    """
    try:
        valor = abs(
            float(diferenca)
        )

        return f"{valor:.2f}"

    except (TypeError, ValueError):
        return "0.00"


def obter_time_superior(
    nome_mandante,
    nome_visitante,
    intelligence_casa,
    intelligence_fora
):
    """
    Identifica quem possui maior Intelligence Score.
    """
    try:
        casa = float(
            intelligence_casa
        )

        fora = float(
            intelligence_fora
        )

    except (TypeError, ValueError):
        return "Equilíbrio"

    if casa > fora:
        return nome_mandante

    if fora > casa:
        return nome_visitante

    return "Equilíbrio"


# =========================================================
# ESTILOS
# =========================================================

def aplicar_estilos_comparacao():
    """
    Estilos específicos da comparação das equipes.
    """
    st.html(
        """
        <style>

            .compare-team-card {
                background:
                    linear-gradient(
                        145deg,
                        rgba(17, 35, 57, 0.98),
                        rgba(9, 24, 42, 0.98)
                    );

                border:
                    1px solid rgba(103, 139, 176, 0.24);

                border-radius:
                    18px;

                padding:
                    22px;

                min-height:
                    355px;

                text-align:
                    center;

                box-shadow:
                    0 10px 28px rgba(0, 0, 0, 0.20);

                transition:
                    transform 0.20s ease,
                    border-color 0.20s ease;
            }


            .compare-team-card:hover {
                transform:
                    translateY(-2px);

                border-color:
                    rgba(83, 217, 159, 0.40);
            }


            .compare-team-role {
                color:
                    #8fa2b8;

                font-size:
                    10px;

                font-weight:
                    800;

                letter-spacing:
                    1.4px;

                text-transform:
                    uppercase;
            }


            .compare-team-logo-wrapper {
                display:
                    flex;

                align-items:
                    center;

                justify-content:
                    center;

                height:
                    105px;

                margin-top:
                    12px;

                margin-bottom:
                    4px;
            }


            .compare-team-logo {
                display:
                    block;

                object-fit:
                    contain;

                max-height:
                    92px;

                filter:
                    drop-shadow(
                        0 7px 12px
                        rgba(0, 0, 0, 0.30)
                    );
            }


            .compare-team-logo-fallback {
                display:
                    flex;

                align-items:
                    center;

                justify-content:
                    center;

                width:
                    78px;

                height:
                    78px;

                border-radius:
                    50%;

                background:
                    rgba(255, 255, 255, 0.05);

                border:
                    1px solid rgba(255, 255, 255, 0.08);

                font-size:
                    36px;
            }


            .compare-team-name {
                color:
                    #ffffff;

                font-size:
                    22px;

                font-weight:
                    850;

                min-height:
                    50px;

                display:
                    flex;

                align-items:
                    center;

                justify-content:
                    center;

                line-height:
                    1.2;
            }


            .compare-score {
                color:
                    #60e2ad;

                font-size:
                    40px;

                font-weight:
                    900;

                line-height:
                    1;

                margin-top:
                    9px;
            }


            .compare-score-label {
                color:
                    #91a4b8;

                font-size:
                    11px;

                font-weight:
                    650;

                margin-top:
                    6px;
            }


            .compare-progress-header {
                display:
                    flex;

                justify-content:
                    space-between;

                align-items:
                    center;

                margin-top:
                    17px;

                margin-bottom:
                    7px;

                color:
                    #9caec0;

                font-size:
                    10px;

                font-weight:
                    700;
            }


            .compare-progress-track {
                width:
                    100%;

                height:
                    7px;

                background:
                    rgba(255, 255, 255, 0.07);

                border-radius:
                    999px;

                overflow:
                    hidden;
            }


            .compare-progress-fill {
                height:
                    100%;

                border-radius:
                    999px;

                background:
                    linear-gradient(
                        90deg,
                        #28b981,
                        #67e7b4
                    );

                box-shadow:
                    0 0 12px
                    rgba(83, 217, 159, 0.22);
            }


            .compare-category {
                margin-top:
                    17px;

                padding-top:
                    14px;

                border-top:
                    1px solid
                    rgba(255, 255, 255, 0.065);

                display:
                    flex;

                align-items:
                    center;

                justify-content:
                    space-between;

                gap:
                    10px;
            }


            .compare-category-label {
                color:
                    #8295a9;

                font-size:
                    10px;

                font-weight:
                    700;
            }


            .compare-category-badge {
                background:
                    rgba(83, 217, 159, 0.10);

                border:
                    1px solid
                    rgba(83, 217, 159, 0.23);

                color:
                    #73e5b5;

                border-radius:
                    999px;

                padding:
                    5px 10px;

                font-size:
                    10px;

                font-weight:
                    800;
            }


            .compare-center {
                display:
                    flex;

                flex-direction:
                    column;

                align-items:
                    center;

                justify-content:
                    center;

                height:
                    355px;

                padding:
                    20px 10px;
            }


            .compare-vs {
                color:
                    #6f8297;

                font-size:
                    13px;

                font-weight:
                    900;

                letter-spacing:
                    2px;

                margin-bottom:
                    18px;
            }


            .compare-difference-label {
                color:
                    #8497aa;

                font-size:
                    10px;

                font-weight:
                    800;

                letter-spacing:
                    1px;

                text-transform:
                    uppercase;
            }


            .compare-difference-value {
                color:
                    #ffffff;

                font-size:
                    32px;

                font-weight:
                    900;

                line-height:
                    1;

                margin-top:
                    6px;
            }


            .compare-difference-team {
                color:
                    #65e3b0;

                font-size:
                    12px;

                font-weight:
                    800;

                margin-top:
                    8px;

                text-align:
                    center;
            }


            .favorite-strip {
                margin-top:
                    17px;

                background:
                    linear-gradient(
                        145deg,
                        rgba(14, 57, 46, 0.95),
                        rgba(7, 34, 29, 0.95)
                    );

                border:
                    1px solid
                    rgba(83, 217, 159, 0.36);

                border-radius:
                    15px;

                padding:
                    15px 18px;

                display:
                    flex;

                align-items:
                    center;

                justify-content:
                    space-between;

                gap:
                    16px;
            }


            .favorite-strip-main {
                display:
                    flex;

                align-items:
                    center;

                gap:
                    10px;

                flex-wrap:
                    wrap;
            }


            .favorite-strip-label {
                color:
                    #8db8aa;

                font-size:
                    10px;

                font-weight:
                    800;

                letter-spacing:
                    1px;

                text-transform:
                    uppercase;
            }


            .favorite-strip-name {
                color:
                    #ffffff;

                font-size:
                    18px;

                font-weight:
                    900;
            }


            .favorite-strip-subtitle {
                color:
                    #9fb5ad;

                font-size:
                    11px;

                margin-top:
                    3px;
            }


            .compare-confidence {
                border-radius:
                    999px;

                padding:
                    6px 12px;

                font-size:
                    10px;

                font-weight:
                    850;

                white-space:
                    nowrap;
            }


            .compare-confidence-high {
                background:
                    rgba(83, 217, 159, 0.13);

                border:
                    1px solid
                    rgba(83, 217, 159, 0.30);

                color:
                    #73e5b5;
            }


            .compare-confidence-medium {
                background:
                    rgba(229, 186, 77, 0.12);

                border:
                    1px solid
                    rgba(229, 186, 77, 0.27);

                color:
                    #f0cd70;
            }


            .compare-confidence-low {
                background:
                    rgba(239, 117, 131, 0.12);

                border:
                    1px solid
                    rgba(239, 117, 131, 0.28);

                color:
                    #f195a0;
            }


            @media screen and (max-width: 768px) {

                .compare-team-card {
                    min-height:
                        auto;
                }

                .compare-center {
                    height:
                        auto;

                    padding:
                        15px;
                }

                .favorite-strip {
                    flex-direction:
                        column;

                    align-items:
                        flex-start;
                }
            }

        </style>
        """
    )


# =========================================================
# CARDS
# =========================================================

def renderizar_card_time(
    funcao,
    nome_time,
    intelligence_score,
    categoria
):
    """
    Renderiza um card de equipe.
    """
    score_limitado = limitar_score(
        intelligence_score
    )

    score_formatado = formatar_score(
        intelligence_score
    )

    funcao_segura = html.escape(
        str(funcao).upper()
    )

    nome_seguro = html.escape(
        str(nome_time)
    )

    categoria_segura = html.escape(
        str(categoria)
    )

    html_escudo = criar_html_escudo(
        nome_time=nome_time,
        largura=92
    )

    conteudo_html = (
        '<div class="compare-team-card">'

        '<div class="compare-team-role">'
        f"{funcao_segura}"
        "</div>"

        f"{html_escudo}"

        '<div class="compare-team-name">'
        f"{nome_seguro}"
        "</div>"

        '<div class="compare-score">'
        f"{score_formatado}"
        "</div>"

        '<div class="compare-score-label">'
        "Intelligence Score"
        "</div>"

        '<div class="compare-progress-header">'
        "<span>Força geral</span>"
        f"<span>{score_limitado}%</span>"
        "</div>"

        '<div class="compare-progress-track">'
        '<div class="compare-progress-fill" '
        f'style="width:{score_limitado}%;"></div>'
        "</div>"

        '<div class="compare-category">'

        '<span class="compare-category-label">'
        "Categoria"
        "</span>"

        '<span class="compare-category-badge">'
        f"{categoria_segura}"
        "</span>"

        "</div>"

        "</div>"
    )

    st.html(
        conteudo_html
    )


def renderizar_comparador_central(
    nome_mandante,
    nome_visitante,
    intelligence_casa,
    intelligence_fora,
    diferenca
):
    """
    Exibe a diferença entre as equipes.
    """
    time_superior = obter_time_superior(
        nome_mandante=nome_mandante,
        nome_visitante=nome_visitante,
        intelligence_casa=intelligence_casa,
        intelligence_fora=intelligence_fora
    )

    diferenca_formatada = (
        obter_texto_diferenca(
            diferenca
        )
    )

    time_superior_seguro = (
        html.escape(
            str(time_superior)
        )
    )

    conteudo_html = (
        '<div class="compare-center">'

        '<div class="compare-vs">'
        "VS"
        "</div>"

        '<div class="compare-difference-label">'
        "Diferença de Intelligence"
        "</div>"

        '<div class="compare-difference-value">'
        f"+{diferenca_formatada}"
        "</div>"

        '<div class="compare-difference-team">'
        f"Vantagem: {time_superior_seguro}"
        "</div>"

        "</div>"
    )

    st.html(
        conteudo_html
    )


def renderizar_faixa_favorito(
    favorito,
    confianca
):
    """
    Renderiza uma faixa compacta com o favorito.
    """
    favorito_seguro = html.escape(
        str(favorito)
    )

    confianca_segura = html.escape(
        str(confianca)
    )

    classe_confianca = (
        obter_classe_confianca(
            confianca
        )
    )

    conteudo_html = (
        '<div class="favorite-strip">'

        '<div>'

        '<div class="favorite-strip-main">'

        '<span class="favorite-strip-label">'
        "🏆 Favorito da partida"
        "</span>"

        '<span class="favorite-strip-name">'
        f"{favorito_seguro}"
        "</span>"

        "</div>"

        '<div class="favorite-strip-subtitle">'
        "Equipe com maior probabilidade calculada "
        "pelo EntradaPro."
        "</div>"

        "</div>"

        f'<div class="compare-confidence '
        f'{classe_confianca}">'

        f"Confiança {confianca_segura}"

        "</div>"

        "</div>"
    )

    st.html(
        conteudo_html
    )


# =========================================================
# COMPARAÇÃO PRINCIPAL
# =========================================================

def renderizar_comparacao_times(
    nome_mandante,
    nome_visitante,
    analise_mandante,
    analise_visitante,
    resultado_match,
    favorito
):
    """
    Renderiza a comparação direta entre as equipes.
    """
    aplicar_estilos_comparacao()

    intelligence_casa = resultado_match[
        "intelligence_casa"
    ]

    intelligence_fora = resultado_match[
        "intelligence_fora"
    ]

    diferenca = resultado_match.get(
        "diferenca",
        (
            float(intelligence_casa)
            - float(intelligence_fora)
        )
    )

    coluna_mandante, coluna_centro, coluna_visitante = (
        st.columns(
            [1, 0.48, 1]
        )
    )

    with coluna_mandante:
        renderizar_card_time(
            funcao="Mandante",
            nome_time=nome_mandante,
            intelligence_score=intelligence_casa,
            categoria=analise_mandante[
                "categoria_intelligence"
            ]
        )

    with coluna_centro:
        renderizar_comparador_central(
            nome_mandante=nome_mandante,
            nome_visitante=nome_visitante,
            intelligence_casa=intelligence_casa,
            intelligence_fora=intelligence_fora,
            diferenca=diferenca
        )

    with coluna_visitante:
        renderizar_card_time(
            funcao="Visitante",
            nome_time=nome_visitante,
            intelligence_score=intelligence_fora,
            categoria=analise_visitante[
                "categoria_intelligence"
            ]
        )

    renderizar_faixa_favorito(
        favorito=favorito,
        confianca=resultado_match[
            "confianca"
        ]
    )