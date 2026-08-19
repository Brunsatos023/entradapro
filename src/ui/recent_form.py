import html

import streamlit as st


CORES_RESULTADOS = {
    "V": {
        "classe": "recent-result-win",
        "descricao": "Vitória"
    },
    "E": {
        "classe": "recent-result-draw",
        "descricao": "Empate"
    },
    "D": {
        "classe": "recent-result-loss",
        "descricao": "Derrota"
    }
}


def limitar_percentual(valor):
    """
    Converte e limita um percentual entre 0 e 100.
    """
    try:
        valor_convertido = float(valor)
    except (TypeError, ValueError):
        return 0.0

    return max(
        0.0,
        min(
            valor_convertido,
            100.0
        )
    )


def converter_inteiro(valor):
    """
    Converte um valor para inteiro de forma segura.
    """
    try:
        return int(valor)
    except (TypeError, ValueError):
        return 0


def aplicar_estilos_forma_recente():
    """
    Aplica os estilos específicos da seção Forma recente.
    """
    st.html(
        """
        <style>

            .recent-compare-card {
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

                box-shadow:
                    0 10px 26px rgba(0, 0, 0, 0.18);

                transition:
                    transform 0.18s ease,
                    border-color 0.18s ease;
            }


            .recent-compare-card:hover {
                transform:
                    translateY(-2px);

                border-color:
                    rgba(83, 217, 159, 0.38);
            }


            .recent-header {
                display:
                    flex;

                align-items:
                    center;

                justify-content:
                    space-between;

                gap:
                    12px;

                margin-bottom:
                    15px;
            }


            .recent-team-name {
                color:
                    #ffffff;

                font-size:
                    20px;

                font-weight:
                    850;

                line-height:
                    1.2;
            }


            .recent-subtitle {
                color:
                    #8fa1b5;

                font-size:
                    10px;

                font-weight:
                    700;

                margin-top:
                    3px;
            }


            .recent-aproveitamento {
                background:
                    rgba(83, 217, 159, 0.10);

                border:
                    1px solid rgba(83, 217, 159, 0.24);

                color:
                    #70e2b2;

                border-radius:
                    999px;

                padding:
                    6px 10px;

                font-size:
                    10px;

                font-weight:
                    800;

                white-space:
                    nowrap;
            }


            .recent-sequence-label {
                color:
                    #91a3b7;

                font-size:
                    10px;

                font-weight:
                    800;

                text-transform:
                    uppercase;

                letter-spacing:
                    0.8px;

                margin-bottom:
                    9px;
            }


            .recent-results {
                display:
                    flex;

                align-items:
                    center;

                gap:
                    9px;

                flex-wrap:
                    wrap;

                margin-bottom:
                    18px;
            }


            .recent-result-item {
                display:
                    flex;

                flex-direction:
                    column;

                align-items:
                    center;

                gap:
                    5px;
            }


            .recent-result-circle {
                display:
                    flex;

                align-items:
                    center;

                justify-content:
                    center;

                width:
                    30px;

                height:
                    30px;

                border-radius:
                    50%;

                color:
                    #ffffff;

                font-size:
                    11px;

                font-weight:
                    900;

                box-shadow:
                    0 5px 12px rgba(0, 0, 0, 0.25);
            }


            .recent-result-win {
                background:
                    linear-gradient(
                        145deg,
                        #65e1af,
                        #23b878
                    );
            }


            .recent-result-draw {
                background:
                    linear-gradient(
                        145deg,
                        #ffd76a,
                        #d79826
                    );
            }


            .recent-result-loss {
                background:
                    linear-gradient(
                        145deg,
                        #ff6d7d,
                        #cf344a
                    );
            }


            .recent-result-neutral {
                background:
                    linear-gradient(
                        145deg,
                        #9caabb,
                        #657488
                    );
            }


            .recent-result-label {
                color:
                    #788ba0;

                font-size:
                    9px;

                font-weight:
                    800;
            }


            .recent-empty {
                display:
                    flex;

                align-items:
                    center;

                justify-content:
                    center;

                min-height:
                    55px;

                color:
                    #91a3b7;

                font-size:
                    11px;

                margin-bottom:
                    16px;
            }


            .recent-metrics-grid {
                display:
                    grid;

                grid-template-columns:
                    repeat(3, 1fr);

                gap:
                    9px;

                margin-bottom:
                    17px;
            }


            .recent-metric {
                background:
                    rgba(255, 255, 255, 0.025);

                border:
                    1px solid rgba(255, 255, 255, 0.055);

                border-radius:
                    11px;

                padding:
                    10px 8px;

                text-align:
                    center;
            }


            .recent-metric-label {
                color:
                    #8799ad;

                font-size:
                    9px;

                font-weight:
                    700;

                margin-bottom:
                    5px;

                text-transform:
                    uppercase;

                letter-spacing:
                    0.4px;
            }


            .recent-metric-value {
                color:
                    #ffffff;

                font-size:
                    21px;

                font-weight:
                    900;

                line-height:
                    1;
            }


            .recent-progress-header {
                display:
                    flex;

                align-items:
                    center;

                justify-content:
                    space-between;

                gap:
                    10px;

                color:
                    #a6b6c7;

                font-size:
                    10px;

                font-weight:
                    700;

                margin-bottom:
                    6px;
            }


            .recent-progress-value {
                color:
                    #64e4b0;

                font-weight:
                    850;
            }


            .recent-progress-track {
                width:
                    100%;

                height:
                    7px;

                overflow:
                    hidden;

                background:
                    rgba(255, 255, 255, 0.07);

                border-radius:
                    999px;
            }


            .recent-progress-fill {
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
                    0 0 12px rgba(83, 217, 159, 0.22);
            }


            @media screen and (max-width: 768px) {

                .recent-compare-card {
                    padding:
                        17px;
                }

                .recent-header {
                    align-items:
                        flex-start;

                    flex-direction:
                        column;
                }

                .recent-results {
                    gap:
                        7px;
                }

                .recent-result-circle {
                    width:
                        27px;

                    height:
                        27px;
                }
            }

        </style>
        """
    )


def criar_html_sequencia(sequencia):
    """
    Cria o HTML da sequência de resultados recentes.
    """
    if not sequencia:
        return (
            '<div class="recent-empty">'
            "Sem histórico recente disponível."
            "</div>"
        )

    itens_html = []

    for resultado in sequencia:
        resultado_normalizado = (
            str(resultado)
            .strip()
            .upper()
        )

        configuracao = CORES_RESULTADOS.get(
            resultado_normalizado,
            {
                "classe": "recent-result-neutral",
                "descricao": "Sem resultado"
            }
        )

        classe = configuracao[
            "classe"
        ]

        descricao = html.escape(
            configuracao[
                "descricao"
            ]
        )

        letra = html.escape(
            resultado_normalizado
            if resultado_normalizado
            else "-"
        )

        itens_html.append(
            '<div class="recent-result-item">'

            f'<div class="recent-result-circle {classe}" '
            f'title="{descricao}">'

            f"{letra}"

            "</div>"

            f'<div class="recent-result-label">'
            f"{letra}"
            "</div>"

            "</div>"
        )

    return (
        '<div class="recent-results">'
        + "".join(
            itens_html
        )
        + "</div>"
    )


def renderizar_forma_time(
    nome_time,
    analise_time
):
    """
    Renderiza a forma recente de uma equipe.
    """
    resultado_forma = analise_time.get(
        "form",
        {}
    )

    sequencia = resultado_forma.get(
        "sequencia",
        []
    )

    vitorias = converter_inteiro(
        resultado_forma.get(
            "vitorias",
            0
        )
    )

    empates = converter_inteiro(
        resultado_forma.get(
            "empates",
            0
        )
    )

    derrotas = converter_inteiro(
        resultado_forma.get(
            "derrotas",
            0
        )
    )

    aproveitamento = limitar_percentual(
        resultado_forma.get(
            "aproveitamento",
            0
        )
    )

    nome_seguro = html.escape(
        str(nome_time)
    )

    sequencia_html = criar_html_sequencia(
        sequencia
    )

    conteudo_html = (
        '<div class="recent-compare-card">'

        '<div class="recent-header">'

        '<div>'

        '<div class="recent-team-name">'
        f"{nome_seguro}"
        "</div>"

        '<div class="recent-subtitle">'
        "Últimos jogos analisados"
        "</div>"

        "</div>"

        '<div class="recent-aproveitamento">'
        f"{aproveitamento:.2f}% aproveitamento"
        "</div>"

        "</div>"

        '<div class="recent-sequence-label">'
        "Sequência recente"
        "</div>"

        f"{sequencia_html}"

        '<div class="recent-metrics-grid">'

        '<div class="recent-metric">'
        '<div class="recent-metric-label">'
        "Vitórias"
        "</div>"
        '<div class="recent-metric-value">'
        f"{vitorias}"
        "</div>"
        "</div>"

        '<div class="recent-metric">'
        '<div class="recent-metric-label">'
        "Empates"
        "</div>"
        '<div class="recent-metric-value">'
        f"{empates}"
        "</div>"
        "</div>"

        '<div class="recent-metric">'
        '<div class="recent-metric-label">'
        "Derrotas"
        "</div>"
        '<div class="recent-metric-value">'
        f"{derrotas}"
        "</div>"
        "</div>"

        "</div>"

        '<div class="recent-progress-header">'

        "<span>Aproveitamento recente</span>"

        '<span class="recent-progress-value">'
        f"{aproveitamento:.2f}%"
        "</span>"

        "</div>"

        '<div class="recent-progress-track">'

        '<div class="recent-progress-fill" '
        f'style="width:{aproveitamento:.2f}%;">'
        "</div>"

        "</div>"

        "</div>"
    )

    st.html(
        conteudo_html
    )


def renderizar_comparacao_forma(
    nome_mandante,
    nome_visitante,
    analise_mandante,
    analise_visitante
):
    """
    Renderiza a comparação de forma recente.
    """
    aplicar_estilos_forma_recente()

    coluna_mandante, coluna_visitante = (
        st.columns(
            2
        )
    )

    with coluna_mandante:
        renderizar_forma_time(
            nome_time=nome_mandante,
            analise_time=analise_mandante
        )

    with coluna_visitante:
        renderizar_forma_time(
            nome_time=nome_visitante,
            analise_time=analise_visitante
        )