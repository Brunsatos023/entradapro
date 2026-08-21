import math

import matplotlib.pyplot as plt
import streamlit as st


MOTORES = [
    ("Rating", "rating"),
    ("Forma", "forma"),
    ("Pulse", "pulse"),
    ("Casa/Fora", "home_away"),
    ("Adversários", "opponent"),
]


def limitar_nota(valor):
    """
    Limita uma nota entre 0 e 100.
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


def preparar_notas(
    analise_time
):
    """
    Extrai as notas resumidas dos motores.
    """
    notas_resumidas = analise_time.get(
        "notas_resumidas",
        {}
    )

    notas = []

    for _, chave in MOTORES:
        nota = notas_resumidas.get(
            chave,
            0
        )

        notas.append(
            limitar_nota(
                nota
            )
        )

    return notas


def fechar_poligono(
    valores
):
    """
    Repete o primeiro ponto no final para fechar o radar.
    """
    if not valores:
        return []

    return valores + [
        valores[0]
    ]


def criar_radar_chart(
    nome_mandante,
    nome_visitante,
    analise_mandante,
    analise_visitante
):
    """
    Cria o gráfico radar comparativo dos motores.
    """
    categorias = [
        nome
        for nome, _ in MOTORES
    ]

    notas_mandante = preparar_notas(
        analise_mandante
    )

    notas_visitante = preparar_notas(
        analise_visitante
    )

    quantidade = len(
        categorias
    )

    angulos = [
        indice
        / quantidade
        * 2
        * math.pi
        for indice in range(
            quantidade
        )
    ]

    angulos = fechar_poligono(
        angulos
    )

    notas_mandante_fechadas = fechar_poligono(
        notas_mandante
    )

    notas_visitante_fechadas = fechar_poligono(
        notas_visitante
    )

    figura = plt.figure(
        figsize=(7.5, 6.3),
        facecolor="#0a1727"
    )

    eixo = figura.add_subplot(
        111,
        polar=True
    )

    eixo.set_facecolor(
        "#0f1f33"
    )

    eixo.set_theta_offset(
        math.pi / 2
    )

    eixo.set_theta_direction(
        -1
    )

    eixo.set_xticks(
        angulos[:-1]
    )

    eixo.set_xticklabels(
        categorias,
        fontsize=10,
        color="#dce7f3",
        fontweight="bold"
    )

    eixo.set_ylim(
        0,
        100
    )

    eixo.set_yticks(
        [
            20,
            40,
            60,
            80,
            100
        ]
    )

    eixo.set_yticklabels(
        [
            "20",
            "40",
            "60",
            "80",
            "100"
        ],
        fontsize=8,
        color="#8093a8"
    )

    eixo.grid(
        color="#31445a",
        alpha=0.65,
        linewidth=0.8
    )

    eixo.spines[
        "polar"
    ].set_color(
        "#42566c"
    )

    eixo.plot(
        angulos,
        notas_mandante_fechadas,
        linewidth=2.4,
        color="#14e89e",
        label=nome_mandante
    )

    eixo.fill(
        angulos,
        notas_mandante_fechadas,
        alpha=0.16,
        color="#14e89e"
    )

    eixo.plot(
        angulos,
        notas_visitante_fechadas,
        linewidth=2.4,
        color="#4e9ff5",
        label=nome_visitante
    )

    eixo.fill(
        angulos,
        notas_visitante_fechadas,
        alpha=0.13,
        color="#4e9ff5"
    )

    for angulo, nota in zip(
        angulos[:-1],
        notas_mandante
    ):
        eixo.scatter(
            angulo,
            nota,
            s=30,
            color="#14e89e",
            zorder=5
        )

    for angulo, nota in zip(
        angulos[:-1],
        notas_visitante
    ):
        eixo.scatter(
            angulo,
            nota,
            s=30,
            color="#4e9ff5",
            zorder=5
        )

    eixo.set_title(
        "Mapa de forças",
        pad=26,
        fontsize=15,
        fontweight="bold",
        color="#ffffff"
    )

    legenda = eixo.legend(
        loc="upper center",
        bbox_to_anchor=(
            0.5,
            -0.08
        ),
        ncol=2,
        frameon=False,
        fontsize=9
    )

    for texto in legenda.get_texts():
        texto.set_color(
            "#dce7f3"
        )

    figura.tight_layout()

    return figura


def renderizar_resumo_radar(
    nome_mandante,
    nome_visitante,
    analise_mandante,
    analise_visitante
):
    """
    Mostra um pequeno resumo textual abaixo do radar.
    """
    notas_mandante = preparar_notas(
        analise_mandante
    )

    notas_visitante = preparar_notas(
        analise_visitante
    )

    vitorias_mandante = 0
    vitorias_visitante = 0
    empates = 0

    for nota_mandante, nota_visitante in zip(
        notas_mandante,
        notas_visitante
    ):
        if nota_mandante > nota_visitante:
            vitorias_mandante += 1

        elif nota_visitante > nota_mandante:
            vitorias_visitante += 1

        else:
            empates += 1

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            f"Motores — {nome_mandante}",
            f"{vitorias_mandante}/5"
        )

    with col2:
        st.metric(
            f"Motores — {nome_visitante}",
            f"{vitorias_visitante}/5"
        )

    with col3:
        st.metric(
            "Empates",
            str(empates)
        )


def renderizar_radar_chart(
    nome_mandante,
    nome_visitante,
    analise_mandante,
    analise_visitante
):
    """
    Renderiza o radar comparativo no dashboard.
    """
    figura = criar_radar_chart(
        nome_mandante=nome_mandante,
        nome_visitante=nome_visitante,
        analise_mandante=analise_mandante,
        analise_visitante=analise_visitante
    )

    with st.container(
        border=True
    ):
        st.pyplot(
            figura,
            use_container_width=True
        )

        renderizar_resumo_radar(
            nome_mandante=nome_mandante,
            nome_visitante=nome_visitante,
            analise_mandante=analise_mandante,
            analise_visitante=analise_visitante
        )

        st.caption(
            "Quanto mais próximo da borda, "
            "maior a nota naquele motor. "
            "O resumo abaixo indica em quantos "
            "dos cinco motores cada equipe teve vantagem."
        )

    plt.close(
        figura
    )