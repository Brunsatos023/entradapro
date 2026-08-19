import html

import streamlit as st


def converter_float(
    valor,
    padrao=0.0
):
    """
    Converte um valor para float de forma segura.
    """
    try:
        return float(valor)
    except (TypeError, ValueError):
        return padrao


def formatar_value_bet(
    resultado_value
):
    """
    Retorna o texto e a classe visual do Value Bet.
    """
    possui_value = bool(
        resultado_value.get(
            "value_bet",
            False
        )
    )

    if possui_value:
        return {
            "texto": "SIM",
            "icone": "✓",
            "classe": "executive-positive",
            "classe_painel": "executive-summary-positive"
        }

    return {
        "texto": "NÃO",
        "icone": "!",
        "classe": "executive-negative",
        "classe_painel": "executive-summary-negative"
    }


def calcular_probabilidade_favorito(
    resultado_match
):
    """
    Identifica a maior probabilidade entre
    vitória da casa, empate e vitória visitante.
    """
    probabilidades = [
        converter_float(
            resultado_match.get(
                "probabilidade_casa",
                0
            )
        ),
        converter_float(
            resultado_match.get(
                "probabilidade_empate",
                0
            )
        ),
        converter_float(
            resultado_match.get(
                "probabilidade_fora",
                0
            )
        )
    ]

    return max(
        probabilidades
    )


def aplicar_estilos_resumo_executivo():
    """
    Aplica os estilos do painel executivo.
    """
    st.html(
        """
        <style>
            .executive-summary {
                position: relative;
                overflow: hidden;
                background:
                    radial-gradient(
                        circle at top right,
                        rgba(83, 217, 159, 0.11),
                        transparent 34%
                    ),
                    linear-gradient(
                        145deg,
                        rgba(16, 35, 56, 0.99),
                        rgba(8, 23, 40, 0.99)
                    );
                border: 1px solid rgba(91, 131, 170, 0.34);
                border-radius: 22px;
                padding: 25px;
                margin-bottom: 12px;
                box-shadow:
                    0 16px 38px rgba(0, 0, 0, 0.25);
            }

            .executive-summary-positive {
                border-color: rgba(83, 217, 159, 0.44);
            }

            .executive-summary-negative {
                border-color: rgba(239, 117, 131, 0.38);
            }

            .executive-summary-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 14px;
                padding-bottom: 18px;
                margin-bottom: 20px;
                border-bottom:
                    1px solid rgba(255, 255, 255, 0.08);
            }

            .executive-summary-title-area {
                display: flex;
                align-items: center;
                gap: 12px;
            }

            .executive-summary-icon {
                display: flex;
                align-items: center;
                justify-content: center;
                width: 42px;
                height: 42px;
                border-radius: 12px;
                background-color: rgba(83, 217, 159, 0.13);
                border: 1px solid rgba(83, 217, 159, 0.28);
                color: #69e4b2;
                font-size: 21px;
            }

            .executive-summary-title {
                color: #ffffff;
                font-size: 21px;
                font-weight: 900;
                line-height: 1.1;
            }

            .executive-summary-subtitle {
                color: #8fa4b9;
                font-size: 11px;
                font-weight: 650;
                margin-top: 5px;
            }

            .executive-summary-status {
                display: inline-flex;
                align-items: center;
                gap: 7px;
                border-radius: 999px;
                padding: 7px 12px;
                background-color: rgba(83, 217, 159, 0.11);
                border: 1px solid rgba(83, 217, 159, 0.26);
                color: #70e5b5;
                font-size: 11px;
                font-weight: 850;
                letter-spacing: 0.5px;
            }

            .executive-main-grid {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 15px;
                margin-bottom: 15px;
            }

            .executive-main-card {
                background:
                    linear-gradient(
                        145deg,
                        rgba(255, 255, 255, 0.045),
                        rgba(255, 255, 255, 0.018)
                    );
                border: 1px solid rgba(255, 255, 255, 0.075);
                border-radius: 17px;
                padding: 20px;
                min-height: 145px;
            }

            .executive-main-label {
                color: #8fa4b9;
                font-size: 10px;
                font-weight: 850;
                letter-spacing: 1.1px;
                text-transform: uppercase;
            }

            .executive-main-value {
                color: #ffffff;
                font-size: 25px;
                font-weight: 900;
                line-height: 1.15;
                margin-top: 11px;
            }

            .executive-main-percentage {
                color: #5fe0aa;
                font-size: 29px;
                font-weight: 950;
                line-height: 1;
                margin-top: 14px;
            }

            .executive-main-description {
                color: #a7b7c8;
                font-size: 12px;
                margin-top: 9px;
            }

            .executive-metrics-grid {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 12px;
            }

            .executive-metric-card {
                background-color: rgba(5, 17, 30, 0.48);
                border: 1px solid rgba(255, 255, 255, 0.07);
                border-radius: 14px;
                padding: 16px;
                min-height: 100px;
            }

            .executive-metric-label {
                color: #8fa4b9;
                font-size: 10px;
                font-weight: 800;
                letter-spacing: 0.7px;
                text-transform: uppercase;
            }

            .executive-metric-value {
                color: #ffffff;
                font-size: 23px;
                font-weight: 950;
                margin-top: 10px;
            }

            .executive-positive {
                color: #5fe0aa;
            }

            .executive-negative {
                color: #ef7d8b;
            }

            .executive-message {
                display: flex;
                align-items: center;
                gap: 11px;
                border-radius: 14px;
                padding: 15px 17px;
                margin-top: 15px;
                font-size: 12px;
                font-weight: 700;
                line-height: 1.45;
            }

            .executive-message-positive {
                background-color: rgba(83, 217, 159, 0.09);
                border: 1px solid rgba(83, 217, 159, 0.23);
                color: #a9e8ce;
            }

            .executive-message-negative {
                background-color: rgba(239, 117, 131, 0.08);
                border: 1px solid rgba(239, 117, 131, 0.22);
                color: #efb1b9;
            }

            .executive-message-icon {
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
                width: 29px;
                height: 29px;
                border-radius: 50%;
                background-color: rgba(255, 255, 255, 0.07);
                color: #ffffff;
                font-size: 13px;
                font-weight: 900;
            }

            @media screen and (max-width: 900px) {
                .executive-main-grid {
                    grid-template-columns: 1fr;
                }

                .executive-metrics-grid {
                    grid-template-columns: 1fr;
                }

                .executive-summary-header {
                    align-items: flex-start;
                    flex-direction: column;
                }
            }
        </style>
        """
    )


def renderizar_resumo_executivo(
    favorito,
    resultado_match,
    resultado_prediction,
    melhor_mercado,
    resultado_value
):
    """
    Renderiza o painel executivo principal do FootballAI.
    """
    aplicar_estilos_resumo_executivo()

    configuracao_value = formatar_value_bet(
        resultado_value
    )

    probabilidade_favorito = (
        calcular_probabilidade_favorito(
            resultado_match
        )
    )

    melhor_score = converter_float(
        resultado_prediction.get(
            "melhor_score",
            0
        )
    )

    odd_justa = converter_float(
        resultado_value.get(
            "odd_justa",
            0
        )
    )

    edge = converter_float(
        resultado_value.get(
            "edge",
            0
        )
    )

    confianca = html.escape(
        str(
            resultado_match.get(
                "confianca",
                "Não informada"
            )
        )
    )

    classificacao = html.escape(
        str(
            resultado_value.get(
                "classificacao",
                "Não informada"
            )
        )
    )

    favorito_seguro = html.escape(
        str(favorito)
    )

    mercado_seguro = html.escape(
        str(melhor_mercado)
    )

    if resultado_value.get(
        "value_bet",
        False
    ):
        mensagem = (
            "O FootballAI identificou uma oportunidade "
            "com valor estatístico positivo."
        )

        classe_mensagem = (
            "executive-message-positive"
        )

        icone_mensagem = "✓"

    else:
        mensagem = (
            "A odd informada não apresenta "
            "valor estatístico positivo."
        )

        classe_mensagem = (
            "executive-message-negative"
        )

        icone_mensagem = "!"

    conteudo_html = (
        f'<div class="executive-summary '
        f'{configuracao_value["classe_painel"]}">'

        '<div class="executive-summary-header">'

        '<div class="executive-summary-title-area">'

        '<div class="executive-summary-icon">'
        "⚡"
        "</div>"

        "<div>"

        '<div class="executive-summary-title">'
        "FootballAI Intelligence"
        "</div>"

        '<div class="executive-summary-subtitle">'
        "Resumo executivo da análise estatística"
        "</div>"

        "</div>"

        "</div>"

        '<div class="executive-summary-status">'
        "● ANÁLISE CONCLUÍDA"
        "</div>"

        "</div>"

        '<div class="executive-main-grid">'

        '<div class="executive-main-card">'

        '<div class="executive-main-label">'
        "🏆 Favorito da partida"
        "</div>"

        '<div class="executive-main-value">'
        f"{favorito_seguro}"
        "</div>"

        '<div class="executive-main-percentage">'
        f"{probabilidade_favorito:.2f}%"
        "</div>"

        '<div class="executive-main-description">'
        f"Confiança da análise: {confianca}"
        "</div>"

        "</div>"

        '<div class="executive-main-card">'

        '<div class="executive-main-label">'
        "🎯 Melhor mercado"
        "</div>"

        '<div class="executive-main-value">'
        f"{mercado_seguro}"
        "</div>"

        '<div class="executive-main-percentage">'
        f"{melhor_score:.2f}%"
        "</div>"

        '<div class="executive-main-description">'
        f"Classificação: {classificacao}"
        "</div>"

        "</div>"

        "</div>"

        '<div class="executive-metrics-grid">'

        '<div class="executive-metric-card">'

        '<div class="executive-metric-label">'
        "Value Bet"
        "</div>"

        f'<div class="executive-metric-value '
        f'{configuracao_value["classe"]}">'

        f'{configuracao_value["icone"]} '
        f'{configuracao_value["texto"]}'

        "</div>"

        "</div>"

        '<div class="executive-metric-card">'

        '<div class="executive-metric-label">'
        "Odd justa"
        "</div>"

        '<div class="executive-metric-value">'
        f"{odd_justa:.2f}"
        "</div>"

        "</div>"

        '<div class="executive-metric-card">'

        '<div class="executive-metric-label">'
        "Edge"
        "</div>"

        f'<div class="executive-metric-value '
        f'{configuracao_value["classe"]}">'

        f"{edge:+.2f}%"

        "</div>"

        "</div>"

        "</div>"

        f'<div class="executive-message '
        f'{classe_mensagem}">'

        '<div class="executive-message-icon">'
        f"{icone_mensagem}"
        "</div>"

        "<div>"
        f"{mensagem}"
        "</div>"

        "</div>"

        "</div>"
    )

    st.html(
        conteudo_html
    )