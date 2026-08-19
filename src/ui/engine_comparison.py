import html

import streamlit as st


MOTORES = [
    ("Rating", "rating", "Força geral"),
    ("Forma", "forma", "Momento recente"),
    ("Pulse", "pulse", "Tendência"),
    ("Casa/Fora", "home_away", "Mando de campo"),
    ("Adversários", "opponent", "Nível enfrentado"),
]


def limitar_score(valor):
    """
    Limita uma nota entre 0 e 100.
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


def formatar_score(valor):
    """
    Formata uma nota com duas casas decimais.
    """
    try:
        return f"{float(valor):.2f}"
    except (TypeError, ValueError):
        return "0.00"


def aplicar_estilos_motores():
    """
    Aplica os estilos da comparação dos motores.
    """
    st.html(
        """
        <style>

            .engine-card {
                background:
                    linear-gradient(
                        145deg,
                        rgba(16, 34, 55, 0.98),
                        rgba(9, 24, 41, 0.98)
                    );

                border:
                    1px solid rgba(93, 129, 166, 0.24);

                border-radius:
                    16px;

                padding:
                    18px;

                box-shadow:
                    0 8px 24px rgba(0, 0, 0, 0.17);

                transition:
                    transform 0.18s ease,
                    border-color 0.18s ease;
            }


            .engine-card:hover {
                transform:
                    translateY(-2px);

                border-color:
                    rgba(83, 217, 159, 0.38);
            }


            .engine-header {
                display:
                    flex;

                align-items:
                    flex-start;

                justify-content:
                    space-between;

                gap:
                    12px;

                margin-bottom:
                    15px;
            }


            .engine-title {
                color:
                    #ffffff;

                font-size:
                    18px;

                font-weight:
                    850;

                line-height:
                    1.2;
            }


            .engine-subtitle {
                color:
                    #8fa1b5;

                font-size:
                    10px;

                font-weight:
                    650;

                margin-top:
                    3px;
            }


            .engine-advantage {
                background:
                    rgba(83, 217, 159, 0.10);

                border:
                    1px solid rgba(83, 217, 159, 0.22);

                color:
                    #70e2b2;

                border-radius:
                    999px;

                padding:
                    5px 9px;

                font-size:
                    9px;

                font-weight:
                    800;

                white-space:
                    nowrap;
            }


            .engine-team {
                margin-bottom:
                    14px;
            }


            .engine-team:last-child {
                margin-bottom:
                    0;
            }


            .engine-team-header {
                display:
                    flex;

                align-items:
                    center;

                justify-content:
                    space-between;

                gap:
                    10px;

                margin-bottom:
                    7px;
            }


            .engine-team-name {
                color:
                    #9fb0c3;

                font-size:
                    10px;

                font-weight:
                    700;
            }


            .engine-team-score {
                color:
                    #ffffff;

                font-size:
                    16px;

                font-weight:
                    900;
            }


            .engine-team-score-best {
                color:
                    #66e3b1;
            }


            .engine-track {
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


            .engine-fill {
                height:
                    100%;

                border-radius:
                    999px;

                background:
                    linear-gradient(
                        90deg,
                        #71859b,
                        #9baabd
                    );
            }


            .engine-fill-best {
                background:
                    linear-gradient(
                        90deg,
                        #28b981,
                        #67e7b4
                    );

                box-shadow:
                    0 0 11px rgba(83, 217, 159, 0.20);
            }


            .engine-summary {
                margin-top:
                    12px;

                padding-top:
                    11px;

                border-top:
                    1px solid rgba(255, 255, 255, 0.06);

                color:
                    #8799ad;

                font-size:
                    9px;

                font-weight:
                    700;
            }


            @media screen and (max-width: 768px) {

                .engine-card {
                    padding:
                        16px;
                }

                .engine-header {
                    flex-direction:
                        column;
                }
            }

        </style>
        """
    )


def obter_vantagem(
    score_mandante,
    score_visitante,
    nome_mandante,
    nome_visitante
):
    """
    Retorna o time com maior nota no motor.
    """
    if score_mandante > score_visitante:
        return nome_mandante

    if score_visitante > score_mandante:
        return nome_visitante

    return "Equilíbrio"


def renderizar_motor(
    nome_motor,
    descricao_motor,
    score_mandante,
    score_visitante,
    nome_mandante,
    nome_visitante
):
    """
    Renderiza um card de comparação entre as equipes.
    """
    score_mandante_limitado = limitar_score(
        score_mandante
    )

    score_visitante_limitado = limitar_score(
        score_visitante
    )

    score_mandante_formatado = formatar_score(
        score_mandante
    )

    score_visitante_formatado = formatar_score(
        score_visitante
    )

    vantagem = obter_vantagem(
        score_mandante=score_mandante,
        score_visitante=score_visitante,
        nome_mandante=nome_mandante,
        nome_visitante=nome_visitante
    )

    nome_motor_seguro = html.escape(
        str(nome_motor)
    )

    descricao_segura = html.escape(
        str(descricao_motor)
    )

    nome_mandante_seguro = html.escape(
        str(nome_mandante)
    )

    nome_visitante_seguro = html.escape(
        str(nome_visitante)
    )

    vantagem_segura = html.escape(
        str(vantagem)
    )

    classe_score_mandante = (
        "engine-team-score-best"
        if score_mandante > score_visitante
        else ""
    )

    classe_score_visitante = (
        "engine-team-score-best"
        if score_visitante > score_mandante
        else ""
    )

    classe_fill_mandante = (
        "engine-fill-best"
        if score_mandante > score_visitante
        else ""
    )

    classe_fill_visitante = (
        "engine-fill-best"
        if score_visitante > score_mandante
        else ""
    )

    diferenca = abs(
        float(score_mandante)
        - float(score_visitante)
    )

    conteudo_html = (
        '<div class="engine-card">'

        '<div class="engine-header">'

        '<div>'

        '<div class="engine-title">'
        f"{nome_motor_seguro}"
        "</div>"

        '<div class="engine-subtitle">'
        f"{descricao_segura}"
        "</div>"

        "</div>"

        '<div class="engine-advantage">'
        f"Vantagem: {vantagem_segura}"
        "</div>"

        "</div>"

        '<div class="engine-team">'

        '<div class="engine-team-header">'

        '<span class="engine-team-name">'
        f"{nome_mandante_seguro}"
        "</span>"

        f'<span class="engine-team-score {classe_score_mandante}">'
        f"{score_mandante_formatado}"
        "</span>"

        "</div>"

        '<div class="engine-track">'

        f'<div class="engine-fill {classe_fill_mandante}" '
        f'style="width:{score_mandante_limitado}%;"></div>'

        "</div>"

        "</div>"

        '<div class="engine-team">'

        '<div class="engine-team-header">'

        '<span class="engine-team-name">'
        f"{nome_visitante_seguro}"
        "</span>"

        f'<span class="engine-team-score {classe_score_visitante}">'
        f"{score_visitante_formatado}"
        "</span>"

        "</div>"

        '<div class="engine-track">'

        f'<div class="engine-fill {classe_fill_visitante}" '
        f'style="width:{score_visitante_limitado}%;"></div>'

        "</div>"

        "</div>"

        '<div class="engine-summary">'
        f"Diferença neste motor: {diferenca:.2f} pontos"
        "</div>"

        "</div>"
    )

    st.html(
        conteudo_html
    )


def renderizar_comparacao_motores(
    nome_mandante,
    nome_visitante,
    analise_mandante,
    analise_visitante
):
    """
    Renderiza a comparação dos motores do FootballAI.
    """
    aplicar_estilos_motores()

    notas_mandante = analise_mandante.get(
        "notas_resumidas",
        {}
    )

    notas_visitante = analise_visitante.get(
        "notas_resumidas",
        {}
    )

    for indice in range(
        0,
        len(MOTORES),
        2
    ):
        motores_linha = MOTORES[
            indice:indice + 2
        ]

        colunas = st.columns(
            len(motores_linha)
        )

        for coluna, motor in zip(
            colunas,
            motores_linha
        ):
            (
                nome_motor,
                chave_motor,
                descricao_motor
            ) = motor

            score_mandante = float(
                notas_mandante.get(
                    chave_motor,
                    0
                )
            )

            score_visitante = float(
                notas_visitante.get(
                    chave_motor,
                    0
                )
            )

            with coluna:
                renderizar_motor(
                    nome_motor=nome_motor,
                    descricao_motor=descricao_motor,
                    score_mandante=score_mandante,
                    score_visitante=score_visitante,
                    nome_mandante=nome_mandante,
                    nome_visitante=nome_visitante
                )