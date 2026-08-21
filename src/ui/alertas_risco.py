"""
Componente visual: exibe os alertas de sequência ruim recente
(Etapa E do roteiro "EntradaPro Autônomo"), quando existirem.

Sempre informativo, nunca bloqueia nada - é o usuário quem decide
o que fazer com essa informação.
"""

import streamlit as st

from risk_management_service import obter_status_risco_geral

import logging
logger = logging.getLogger("entradapro.dashboard")


def renderizar_alertas_risco():
    try:
        status = obter_status_risco_geral()
    except Exception as erro:
        logger.exception(
            "Erro ao obter status de risco: %s", erro
        )
        return

    if not status.get("tem_alerta"):
        return

    for alerta in status["alertas_ativos"]:
        st.warning(alerta["mensagem"])
