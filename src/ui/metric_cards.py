import html

import streamlit as st


# =========================================================
# UTILITÁRIOS
# =========================================================

def limitar_percentual(valor):
    """
    Limita um percentual entre 0 e 100.
    """
    try:
        valor_convertido = float(valor)
    except (TypeError, ValueError):
        return 0

    return max(
        0,
        min(
            int(round(valor_convertido)),
            100
        )
    )


def formatar_numero(valor):
    """
    Formata um número com duas casas decimais.
    """
    try:
        return f"{float(valor):.2f}"
    except (TypeError, ValueError):
        return "0.00"


# =========================================================
# ESTILOS
# =========================================================

def aplicar_estilos_metricas():
    """
    Estilos específicos dos cards de mercados.
    """
    st.html(
        """
        <style>

            .market-card {
                position:
                    relative;

                overflow:
                    hidden;

                background:
                    linear-gradient(
                        145deg,
                        rgba(16, 34, 55, 0.98),
                        rgba(9, 24, 41, 0.98)
                    );

                border:
                    1px solid rgba(93, 129, 166, 0.24);

                border-radius:
                    17px;

                padding:
                    20px;

                min-height:
                    235px;

                box-shadow:
                    0 9px 26px rgba(0, 0, 0, 0.18);

                transition:
                    transform 0.18s ease,
                    border-color 0.18s ease;
            }


            .market-card:hover {
                transform:
                    translateY(-2px);

                border-color:
                    rgba(83, 217, 159, 0.38);
            }


            .market-card-valid {
                background:
                    linear-gradient(
                        145deg,
                        rgba(13, 55, 45, 0.98),
                        rgba(7, 34, 29, 0.98)
                    );

                border-color:
                    rgba(83, 217, 159, 0.42);
            }


            .market-card-experimental {
                background:
                    linear-gradient(
                        145deg,
                        rgba(42, 42, 31, 0.98),
                        rgba(26, 29, 24, 0.98)
                    );

                border-color:
                    rgba(222, 184, 74, 0.28);
            }


            .market-card-label {
                color:
                    #8fa2b7;

                font-size:
                    10px;

                font-weight:
                    800;

                letter-spacing:
                    1px;

                text-transform:
                    uppercase;

                margin-bottom:
                    7px;
            }


            .market-card-title {
                color:
                    #ffffff;

                font-size:
                    19px;

                font-weight:
                    850;

                line-height:
                    1.2;

                min-height:
                    47px;
            }


            .market-card-value {
                color:
                    #ffffff;

                font-size:
                    36px;

                font-weight:
                    900;

                line-height:
                    1;

                margin-top:
                    11px;
            }


            .market-card-value-green {
                color:
                    #62e3af;
            }


            .market-card-value-yellow {
                color:
                    #efd16f;
            }


            .market-card-unit {
                color:
                    #8295aa;

                font-size:
                    11px;

                font-weight:
                    650;

                margin-top:
                    5px;
            }


            .market-progress {
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

                margin-top:
                    17px;
            }


            .market-progress-fill {
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
                    0 0 12px rgba(83, 217, 159, 0.20);
            }


            .market-progress-fill-neutral {
                height:
                    100%;

                border-radius:
                    999px;

                background:
                    linear-gradient(
                        90deg,
                        #68809a,
                        #9dafc1
                    );
            }


            .market-progress-fill-yellow {
                height:
                    100%;

                border-radius:
                    999px;

                background:
                    linear-gradient(
                        90deg,
                        #c59a32,
                        #e8c65f
                    );
            }


            .market-footer {
                display:
                    flex;

                align-items:
                    center;

                justify-content:
                    space-between;

                gap:
                    10px;

                margin-top:
                    16px;

                padding-top:
                    13px;

                border-top:
                    1px solid rgba(255, 255, 255, 0.06);
            }


            .market-classification {
                color:
                    #91a4b8;

                font-size:
                    10px;

                font-weight:
                    700;
            }


            .market-status {
                border-radius:
                    999px;

                padding:
                    5px 9px;

                font-size:
                    9px;

                font-weight:
                    850;

                white-space:
                    nowrap;
            }


            .market-status-valid {
                color:
                    #71e4b4;

                background:
                    rgba(83, 217, 159, 0.11);

                border:
                    1px solid rgba(83, 217, 159, 0.27);
            }


            .market-status-warning {
                color:
                    #efd16f;

                background:
                    rgba(231, 185, 75, 0.10);

                border:
                    1px solid rgba(231, 185, 75, 0.24);
            }


            .market-status-neutral {
                color:
                    #aebdca;

                background:
                    rgba(142, 164, 189, 0.10);

                border:
                    1px solid rgba(142, 164, 189, 0.21);
            }


            .prob-card {
                background:
                    linear-gradient(
                        145deg,
                        rgba(16, 34, 55, 0.98),
                        rgba(9, 24, 41, 0.98)
                    );

                border:
                    1px solid rgba(93, 129, 166, 0.22);

                border-radius:
                    15px;

                padding:
                    16px;

                min-height:
                    130px;
            }


            .prob-card-best {
                border-color:
                    rgba(83, 217, 159, 0.36);

                background:
                    linear-gradient(
                        145deg,
                        rgba(13, 48, 42, 0.96),
                        rgba(8, 30, 28, 0.96)
                    );
            }


            .prob-label {
                color:
                    #8fa2b7;

                font-size:
                    10px;

                font-weight:
                    700;
            }


            .prob-value {
                color:
                    #ffffff;

                font-size:
                    27px;

                font-weight:
                    900;

                margin-top:
                    7px;
            }


            .prob-value-best {
                color:
                    #62e3af;
            }


            @media screen and (max-width: 768px) {

                .market-card {
                    min-height:
                        auto;

                    padding:
                        17px;
                }

                .market-card-title {
                    min-height:
                        auto;
                }

                .market-footer {
                    align-items:
                        flex-start;

                    flex-direction:
                        column;
                }
            }

        </style>
        """
    )


# =========================================================
# PROBABILIDADES 1X2
# =========================================================

def renderizar_card_probabilidade(
    titulo,
    valor,
    destaque=False
):
    """
    Renderiza um card de probabilidade da partida.
    """
    percentual = limitar_percentual(
        valor
    )

    titulo_seguro = html.escape(
        str(titulo)
    )

    valor_formatado = formatar_numero(
        valor
    )

    classe_card = (
        "prob-card prob-card-best"
        if destaque
        else "prob-card"
    )

    classe_valor = (
        "prob-value prob-value-best"
        if destaque
        else "prob-value"
    )

    classe_barra = (
        "market-progress-fill"
        if destaque
        else "market-progress-fill-neutral"
    )

    conteudo_html = (
        f'<div class="{classe_card}">'

        '<div class="prob-label">'
        f"{titulo_seguro}"
        "</div>"

        f'<div class="{classe_valor}">'
        f"{valor_formatado}%"
        "</div>"

        '<div class="market-progress">'

        f'<div class="{classe_barra}" '
        f'style="width:{percentual}%;"></div>'

        "</div>"

        "</div>"
    )

    st.html(
        conteudo_html
    )


def renderizar_probabilidades(
    nome_mandante,
    nome_visitante,
    resultado_match
):
    """
    Renderiza as probabilidades de vitória/empate.
    """
    aplicar_estilos_metricas()

    prob_casa = float(
        resultado_match[
            "probabilidade_casa"
        ]
    )

    prob_empate = float(
        resultado_match[
            "probabilidade_empate"
        ]
    )

    prob_fora = float(
        resultado_match[
            "probabilidade_fora"
        ]
    )

    maior = max(
        prob_casa,
        prob_empate,
        prob_fora
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        renderizar_card_probabilidade(
            titulo=f"Vitória — {nome_mandante}",
            valor=prob_casa,
            destaque=(
                prob_casa == maior
            )
        )

    with col2:
        renderizar_card_probabilidade(
            titulo="Empate",
            valor=prob_empate,
            destaque=(
                prob_empate == maior
            )
        )

    with col3:
        renderizar_card_probabilidade(
            titulo=f"Vitória — {nome_visitante}",
            valor=prob_fora,
            destaque=(
                prob_fora == maior
            )
        )


# =========================================================
# MERCADOS DE GOLS
# =========================================================

def renderizar_card_gols_esperados(
    gols
):
    """
    Renderiza o card informativo de gols esperados.
    """
    valor_formatado = formatar_numero(
        gols
    )

    conteudo_html = (
        '<div class="market-card">'

        '<div class="market-card-label">'
        "PROJEÇÃO DA PARTIDA"
        "</div>"

        '<div class="market-card-title">'
        "Gols esperados"
        "</div>"

        '<div class="market-card-value">'
        f"{valor_formatado}"
        "</div>"

        '<div class="market-card-unit">'
        "gols projetados"
        "</div>"

        '<div class="market-footer">'

        '<span class="market-classification">'
        "Indicador estatístico"
        "</span>"

        '<span class="market-status '
        'market-status-neutral">'
        "INFORMATIVO"
        "</span>"

        "</div>"

        "</div>"
    )

    st.html(
        conteudo_html
    )


def renderizar_card_over15(
    probabilidade,
    classificacao,
    status
):
    """
    Renderiza o mercado Over 1.5.
    """
    percentual = limitar_percentual(
        probabilidade
    )

    probabilidade_formatada = formatar_numero(
        probabilidade
    )

    classificacao_segura = html.escape(
        str(classificacao)
    )

    status_seguro = html.escape(
        str(status)
    )

    status_validado = status in {
        "APTO",
        "APTO FORTE",
        "APTO EXPERIMENTAL"
    }

    if status_validado:
        classe_card = (
            "market-card "
            "market-card-valid"
        )

        classe_status = (
            "market-status "
            "market-status-valid"
        )

    else:
        classe_card = (
            "market-card"
        )

        classe_status = (
            "market-status "
            "market-status-neutral"
        )

    conteudo_html = (
        f'<div class="{classe_card}">'

        '<div class="market-card-label">'
        "MERCADO VALIDADO NA V1"
        "</div>"

        '<div class="market-card-title">'
        "Mais de 1,5 gols"
        "</div>"

        '<div class="market-card-value '
        'market-card-value-green">'
        f"{probabilidade_formatada}%"
        "</div>"

        '<div class="market-progress">'

        '<div class="market-progress-fill" '
        f'style="width:{percentual}%;"></div>'

        "</div>"

        '<div class="market-footer">'

        '<span class="market-classification">'
        f"{classificacao_segura}"
        "</span>"

        f'<span class="{classe_status}">'
        f"{status_seguro}"
        "</span>"

        "</div>"

        "</div>"
    )

    st.html(
        conteudo_html
    )


def renderizar_card_btts(
    probabilidade,
    classificacao,
    status
):
    """
    Renderiza o mercado BTTS.
    """
    percentual = limitar_percentual(
        probabilidade
    )

    probabilidade_formatada = formatar_numero(
        probabilidade
    )

    classificacao_segura = html.escape(
        str(classificacao)
    )

    status_seguro = html.escape(
        str(status)
    )

    conteudo_html = (
        '<div class="market-card '
        'market-card-experimental">'

        '<div class="market-card-label">'
        "MERCADO EXPERIMENTAL"
        "</div>"

        '<div class="market-card-title">'
        "Ambas marcam"
        "</div>"

        '<div class="market-card-value '
        'market-card-value-yellow">'
        f"{probabilidade_formatada}%"
        "</div>"

        '<div class="market-progress">'

        '<div class="market-progress-fill-yellow" '
        f'style="width:{percentual}%;"></div>'

        "</div>"

        '<div class="market-footer">'

        '<span class="market-classification">'
        f"{classificacao_segura}"
        "</span>"

        '<span class="market-status '
        'market-status-warning">'
        f"{status_seguro}"
        "</span>"

        "</div>"

        "</div>"
    )

    st.html(
        conteudo_html
    )


def renderizar_mercados_gols(
    resultado_prediction
):
    """
    Renderiza os principais mercados de gols.
    """
    aplicar_estilos_metricas()

    gols = float(
        resultado_prediction.get(
            "gols_esperados_total",
            0.0
        )
    )

    over15 = float(
        resultado_prediction.get(
            "mais_15",
            0.0
        )
    )

    classificacao_over15 = resultado_prediction.get(
        "classificacao_over15",
        "NÃO CLASSIFICADO"
    )

    status_over15 = resultado_prediction.get(
        "status_estrategico_over15",
        "NÃO AVALIADO"
    )

    btts = float(
        resultado_prediction.get(
            "ambas_marcam",
            0.0
        )
    )

    classificacao_btts = resultado_prediction.get(
        "classificacao_btts",
        "NÃO CLASSIFICADO"
    )

    status_btts = resultado_prediction.get(
        "status_estrategico_btts",
        "NÃO VALIDADO"
    )

    col1, col2, col3 = st.columns(
        [0.85, 1.1, 1.1]
    )

    with col1:
        renderizar_card_gols_esperados(
            gols=gols
        )

    with col2:
        renderizar_card_over15(
            probabilidade=over15,
            classificacao=classificacao_over15,
            status=status_over15
        )

    with col3:
        renderizar_card_btts(
            probabilidade=btts,
            classificacao=classificacao_btts,
            status=status_btts
        )