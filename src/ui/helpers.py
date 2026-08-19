import streamlit as st

from engines.value_engine import ValueEngine


def identificar_favorito(
    resultado_match,
    nome_mandante,
    nome_visitante
):
    favorito = resultado_match["favorito"]

    if favorito == "Mandante":
        return nome_mandante

    if favorito == "Visitante":
        return nome_visitante

    return "Partida equilibrada"


def criar_value_engine(
    resultado_prediction,
    odd_over15,
    odd_btts
):
    melhor_mercado = resultado_prediction[
        "melhor_mercado"
    ]

    if melhor_mercado == "Mais de 1,5 gols":
        probabilidade = resultado_prediction["mais_15"]
        odd = odd_over15

    else:
        probabilidade = resultado_prediction[
            "ambas_marcam"
        ]
        odd = odd_btts

    resultado_value = ValueEngine(
        probabilidade_footballai=probabilidade,
        odd_casa=odd
    ).analisar()

    return melhor_mercado, resultado_value


def mostrar_motivos(motivos):
    for motivo in motivos:
        st.write(f"• {motivo}")


def limitar_percentual(valor):
    return max(
        0.0,
        min(float(valor), 100.0)
    )