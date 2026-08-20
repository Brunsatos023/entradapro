"""
Componente visual: "Melhores Entradas do Dia" - a Etapa B do
roteiro "EntradaPro Autônomo" em tela. Mostra automaticamente as
melhores oportunidades encontradas pela varredura, sem o usuário
precisar checar jogo por jogo.

Assim como os jogos futuros, é ADITIVO e com falha silenciosa: se
a varredura não funcionar por qualquer motivo, esta seção
simplesmente não aparece - o resto do site continua normal.
"""

import streamlit as st

from engines.opportunity_scanner import escanear_melhores_oportunidades
from access_control import usuario_eh_pro, renderizar_bloqueio_pro


@st.cache_data(ttl=600, show_spinner=False)
def _escanear_com_cache(dias_a_frente, limite):
    return escanear_melhores_oportunidades(
        dias_a_frente=dias_a_frente, limite=limite
    )


def renderizar_melhores_entradas():
    try:
        resultado = _escanear_com_cache(
            dias_a_frente=3, limite=5
        )
    except Exception:
        return

    if not resultado.get("sucesso"):
        return

    oportunidades = resultado.get("oportunidades", [])

    if not oportunidades:
        return

    eh_pro = usuario_eh_pro()

    # Free ve so a primeira oportunidade (teaser); PRO ve todas.
    oportunidades_visiveis = (
        oportunidades if eh_pro else oportunidades[:1]
    )

    with st.container(border=True):
        st.markdown("### 🔥 Melhores Entradas do Dia")

        st.caption(
            "Selecionadas automaticamente entre os próximos jogos "
            "do Brasileirão, comparando a probabilidade calculada "
            "com as odds reais do mercado."
        )

        for oportunidade in oportunidades_visiveis:
            with st.container(border=True):
                col_info, col_metrica = st.columns([3, 1])

                with col_info:
                    st.markdown(
                        f"**{oportunidade['mandante']}** x "
                        f"**{oportunidade['visitante']}**"
                    )

                    st.caption(
                        f"{oportunidade['melhor_mercado']} · "
                        f"Odd {oportunidade['odd']:.2f}"
                        + (
                            f" ({oportunidade['casa_da_odd']})"
                            if oportunidade.get("casa_da_odd")
                            else ""
                        )
                    )

                    st.caption(
                        f"Confiança: {oportunidade['probabilidade']:.0f}% · "
                        f"{oportunidade['classificacao']}"
                    )

                with col_metrica:
                    st.metric(
                        "Value",
                        f"+{oportunidade['edge']:.1f}%"
                    )

        oportunidades_ocultas = len(oportunidades) - len(
            oportunidades_visiveis
        )

        if not eh_pro and oportunidades_ocultas > 0:
            renderizar_bloqueio_pro(
                titulo=(
                    f"+{oportunidades_ocultas} oportunidade(s) "
                    "adicional(is) disponível(is) no PRO"
                ),
                mensagem=(
                    "Assinantes PRO veem todas as melhores "
                    "entradas do dia, não só a primeira."
                )
            )

        st.caption(
            "⚠️ Estas são análises estatísticas, não garantias de "
            "resultado. Aposta não é investimento — jogue com "
            "responsabilidade."
        )

        st.page_link(
            "pages/4_Resultados.py",
            label="📊 Ver histórico real de acertos (Green/Red/ROI)",
            use_container_width=True
        )
