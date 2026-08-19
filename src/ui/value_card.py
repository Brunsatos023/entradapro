import html

import streamlit as st


# =========================================================
# UTILITÁRIOS
# =========================================================

def formatar_numero(
    valor,
    casas=2
):
    """
    Formata um número de forma segura.
    """
    try:
        return f"{float(valor):.{casas}f}"
    except (TypeError, ValueError):
        return f"{0:.{casas}f}"


def aplicar_estilos_value_card():
    """
    Aplica os estilos específicos do bloco
    de Value e Recomendação.
    """
    st.html(
        """
        <style>

            .value-main-card {
                background:
                    linear-gradient(
                        145deg,
                        rgba(13, 55, 45, 0.98),
                        rgba(7, 34, 29, 0.98)
                    );

                border:
                    1px solid rgba(83, 217, 159, 0.42);

                border-radius:
                    18px;

                padding:
                    22px;

                box-shadow:
                    0 10px 28px rgba(0, 0, 0, 0.19);

                margin-bottom:
                    14px;
            }


            .value-main-header {
                display:
                    flex;

                align-items:
                    flex-start;

                justify-content:
                    space-between;

                gap:
                    18px;
            }


            .value-main-label {
                color:
                    #8fb9aa;

                font-size:
                    10px;

                font-weight:
                    800;

                letter-spacing:
                    1.1px;

                text-transform:
                    uppercase;
            }


            .value-main-market {
                color:
                    #ffffff;

                font-size:
                    26px;

                font-weight:
                    900;

                line-height:
                    1.15;

                margin-top:
                    6px;
            }


            .value-main-category {
                border-radius:
                    999px;

                padding:
                    6px 11px;

                background:
                    rgba(83, 217, 159, 0.12);

                border:
                    1px solid rgba(83, 217, 159, 0.28);

                color:
                    #72e5b5;

                font-size:
                    10px;

                font-weight:
                    850;

                white-space:
                    nowrap;
            }


            .value-price-grid {
                display:
                    grid;

                grid-template-columns:
                    repeat(4, 1fr);

                gap:
                    10px;

                margin-top:
                    19px;
            }


            .value-price-item {
                background:
                    rgba(4, 20, 17, 0.34);

                border:
                    1px solid rgba(255, 255, 255, 0.07);

                border-radius:
                    12px;

                padding:
                    12px;
            }


            .value-price-label {
                color:
                    #8ea7a0;

                font-size:
                    9px;

                font-weight:
                    750;

                text-transform:
                    uppercase;

                letter-spacing:
                    0.5px;
            }


            .value-price-number {
                color:
                    #ffffff;

                font-size:
                    20px;

                font-weight:
                    900;

                margin-top:
                    5px;
            }


            .value-price-positive {
                color:
                    #65e4b1;
            }


            .value-score-card {
                background:
                    linear-gradient(
                        145deg,
                        rgba(16, 34, 55, 0.98),
                        rgba(9, 24, 41, 0.98)
                    );

                border:
                    1px solid rgba(93, 129, 166, 0.24);

                border-radius:
                    15px;

                padding:
                    17px;
            }


            .value-score-label {
                color:
                    #8fa2b7;

                font-size:
                    9px;

                font-weight:
                    750;

                text-transform:
                    uppercase;

                letter-spacing:
                    0.5px;
            }


            .value-score-number {
                color:
                    #ffffff;

                font-size:
                    27px;

                font-weight:
                    900;

                line-height:
                    1;

                margin-top:
                    7px;
            }


            .value-score-highlight {
                color:
                    #61e1ad;
            }


            .value-explanation {
                background:
                    rgba(16, 47, 78, 0.58);

                border:
                    1px solid rgba(78, 159, 245, 0.18);

                border-radius:
                    11px;

                padding:
                    12px 14px;

                color:
                    #c7d8e9;

                font-size:
                    11px;

                font-weight:
                    650;

                line-height:
                    1.5;

                margin-top:
                    13px;
            }


            .value-no-bet {
                background:
                    linear-gradient(
                        145deg,
                        rgba(71, 28, 37, 0.98),
                        rgba(40, 18, 24, 0.98)
                    );

                border:
                    1px solid rgba(239, 117, 131, 0.42);

                border-radius:
                    18px;

                padding:
                    22px;

                box-shadow:
                    0 10px 28px rgba(0, 0, 0, 0.19);
            }


            .value-no-bet-label {
                color:
                    #d9939d;

                font-size:
                    10px;

                font-weight:
                    800;

                text-transform:
                    uppercase;

                letter-spacing:
                    1px;
            }


            .value-no-bet-title {
                color:
                    #ffffff;

                font-size:
                    27px;

                font-weight:
                    900;

                margin-top:
                    6px;
            }


            .value-no-bet-text {
                color:
                    #c6b8bc;

                font-size:
                    12px;

                line-height:
                    1.5;

                margin-top:
                    8px;
            }


            @media screen and (max-width: 768px) {

                .value-price-grid {
                    grid-template-columns:
                        repeat(2, 1fr);
                }

                .value-main-header {
                    flex-direction:
                        column;
                }
            }

        </style>
        """
    )


# =========================================================
# CENÁRIO SEM OPORTUNIDADE
# =========================================================

def renderizar_sem_oportunidade(
    motivo_validacao
):
    """
    Renderiza o estado de não apostar.
    """
    if motivo_validacao:
        motivo = str(
            motivo_validacao
        )
    else:
        motivo = (
            "Nenhum mercado atingiu os critérios "
            "estratégicos validados da V1."
        )

    motivo_seguro = html.escape(
        motivo
    )

    conteudo_html = (
        '<div class="value-no-bet">'

        '<div class="value-no-bet-label">'
        "DECISÃO DO SISTEMA"
        "</div>"

        '<div class="value-no-bet-title">'
        "🚫 NÃO APOSTAR"
        "</div>"

        '<div class="value-no-bet-text">'
        f"{motivo_seguro}"
        "</div>"

        '<div class="value-no-bet-text">'
        "O sistema analisou os mercados disponíveis, "
        "mas não encontrou uma oportunidade que atendesse "
        "aos critérios estratégicos validados da V1."
        "</div>"

        "</div>"
    )

    st.html(
        conteudo_html
    )


# =========================================================
# CENÁRIO COM OPORTUNIDADE
# =========================================================

def renderizar_oportunidade(
    melhor_mercado,
    resultado_value,
    resultado_oportunidade
):
    """
    Renderiza uma oportunidade validada.
    """
    mercado_seguro = html.escape(
        str(melhor_mercado)
    )

    classificacao = resultado_value.get(
        "classificacao",
        "Sem classificação"
    )

    classificacao_segura = html.escape(
        str(classificacao)
    )

    odd_casa = formatar_numero(
        resultado_value.get(
            "odd_casa",
            0.0
        )
    )

    odd_justa = formatar_numero(
        resultado_value.get(
            "odd_justa",
            0.0
        )
    )

    edge = formatar_numero(
        resultado_value.get(
            "edge",
            0.0
        )
    )

    valor_esperado = formatar_numero(
        resultado_value.get(
            "valor_esperado",
            0.0
        )
    )

    conteudo_html = (
        '<div class="value-main-card">'

        '<div class="value-main-header">'

        '<div>'

        '<div class="value-main-label">'
        "🎯 MELHOR OPORTUNIDADE"
        "</div>"

        '<div class="value-main-market">'
        f"{mercado_seguro}"
        "</div>"

        "</div>"

        '<div class="value-main-category">'
        f"{classificacao_segura}"
        "</div>"

        "</div>"

        '<div class="value-price-grid">'

        '<div class="value-price-item">'
        '<div class="value-price-label">'
        "Odd mercado"
        "</div>"
        '<div class="value-price-number">'
        f"{odd_casa}"
        "</div>"
        "</div>"

        '<div class="value-price-item">'
        '<div class="value-price-label">'
        "Odd justa"
        "</div>"
        '<div class="value-price-number">'
        f"{odd_justa}"
        "</div>"
        "</div>"

        '<div class="value-price-item">'
        '<div class="value-price-label">'
        "Edge"
        "</div>"
        '<div class="value-price-number '
        'value-price-positive">'
        f"+{edge}%"
        "</div>"
        "</div>"

        '<div class="value-price-item">'
        '<div class="value-price-label">'
        "Valor esperado"
        "</div>"
        '<div class="value-price-number '
        'value-price-positive">'
        f"+{valor_esperado}%"
        "</div>"
        "</div>"

        "</div>"

        "</div>"
    )

    st.html(
        conteudo_html
    )

    footballai_score = resultado_oportunidade.get(
        "footballai_score",
        0.0
    )

    confianca = resultado_oportunidade.get(
        "confianca",
        "N/D"
    )

    col1, col2 = st.columns(2)

    with col1:
        score_seguro = html.escape(
            str(footballai_score)
        )

        st.html(
            (
                '<div class="value-score-card">'
                '<div class="value-score-label">'
                "EntradaPro Score"
                "</div>"
                '<div class="value-score-number '
                'value-score-highlight">'
                f"{score_seguro}/100"
                "</div>"
                "</div>"
            )
        )

    with col2:
        confianca_segura = html.escape(
            str(confianca)
        )

        st.html(
            (
                '<div class="value-score-card">'
                '<div class="value-score-label">'
                "Confiança"
                "</div>"
                '<div class="value-score-number">'
                f"{confianca_segura}"
                "</div>"
                "</div>"
            )
        )

    motivos = resultado_oportunidade.get(
        "motivos",
        []
    )

    if motivos:
        motivos_seguros = [
            html.escape(
                str(motivo)
            )
            for motivo in motivos
        ]

        explicacao = " ".join(
            motivos_seguros
        )

    else:
        explicacao = (
            "O mercado atingiu os critérios "
            "estratégicos definidos pelo sistema."
        )

    st.html(
        (
            '<div class="value-explanation">'
            f"{explicacao}"
            "</div>"
        )
    )


# =========================================================
# FUNÇÃO PRINCIPAL
# =========================================================

def renderizar_value_card(
    melhor_mercado,
    resultado_value,
    resultado_oportunidade
):
    """
    Renderiza a recomendação de valor do FootballAI.
    """
    aplicar_estilos_value_card()

    recomendacao_validada = resultado_oportunidade.get(
        "recomendacao_validada",
        True
    )

    motivo_validacao = resultado_oportunidade.get(
        "motivo_validacao",
        ""
    )

    if not recomendacao_validada:
        renderizar_sem_oportunidade(
            motivo_validacao=motivo_validacao
        )

        return

    renderizar_oportunidade(
        melhor_mercado=melhor_mercado,
        resultado_value=resultado_value,
        resultado_oportunidade=resultado_oportunidade
    )