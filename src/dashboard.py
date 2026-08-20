import streamlit as st
import pandas as pd

from data_storage import carregar_json
from engines.match_analysis_engine import MatchAnalysisEngine

from auth import (
    inicializar_banco,
    inicializar_estado_autenticacao,
    usuario_esta_autenticado,
    renderizar_usuario_sidebar,
    renderizar_acoes_visitante_topo,
    renderizar_dialogo_autenticacao,
    abrir_autenticacao
)

from access_control import (
    usuario_eh_pro,
    renderizar_bloqueio_pro
)

from subscription_service import expirar_assinaturas_vencidas

from ui import (
    aplicar_estilos,
    renderizar_cabecalho,
    renderizar_estado_inicial,
    renderizar_titulo_secao,
    renderizar_hero_card,
    renderizar_comparacao_times,
    renderizar_comparacao_forma,
    renderizar_comparacao_motores,
    renderizar_radar_chart,
    renderizar_mercados_gols,
    renderizar_value_card,
    identificar_favorito,
    mostrar_motivos
)

from ui.match_selector import renderizar_seletor_partida
from ui.overview import renderizar_overview
from ui.prediction_foundations import renderizar_fundamentos_previsao
from ui.performance_view import renderizar_performance_view
from ui.methodology_view import renderizar_metodologia_view
from ui.jogos_futuros import renderizar_jogos_futuros
from ui.melhores_entradas import renderizar_melhores_entradas
from ui.alertas_risco import renderizar_alertas_risco
from ui.corners_view import renderizar_secao_corners
from ui.vitrine_campeonatos import renderizar_vitrine_campeonatos


ARQUIVO_JSON = "brasileirao_serie_a_2024.json"
COMPETICAO_PADRAO = "Brasileirão Série A"
JANELA = 5


st.set_page_config(
    page_title="EntradaPro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_data
def carregar_dados():
    dados = carregar_json(
        ARQUIVO_JSON
    )

    if not isinstance(dados, dict):
        raise ValueError(
            "O arquivo JSON não retornou "
            "um dicionário válido."
        )

    partidas = dados.get(
        "response"
    )

    if not isinstance(partidas, list):
        raise TypeError(
            "A chave 'response' precisa "
            "conter uma lista."
        )

    if not partidas:
        raise ValueError(
            "Nenhuma partida foi encontrada"
            "no arquivo JSON."
        )

    return partidas


def listar_times(partidas):
    times = {}

    for partida in partidas:
        times_partida = partida.get(
            "teams",
            {}
        )

        time_casa = times_partida.get(
            "home",
            {}
        )

        time_fora = times_partida.get(
            "away",
            {}
        )

        nome_casa = time_casa.get(
            "name"
        )

        id_casa = time_casa.get(
            "id"
        )

        nome_fora = time_fora.get(
            "name"
        )

        id_fora = time_fora.get(
            "id"
        )

        if nome_casa and id_casa is not None:
            times[nome_casa] = id_casa

        if nome_fora and id_fora is not None:
            times[nome_fora] = id_fora

    return dict(
        sorted(
            times.items(),
            key=lambda item: item[0]
        )
    )


def calcular_analise_completa(
    partidas,
    id_mandante,
    id_visitante,
    odd_over15,
    odd_btts,
    odd_over25=None
):
    resultado = MatchAnalysisEngine(
        partidas=partidas,
        id_mandante=id_mandante,
        id_visitante=id_visitante,
        odd_over15=odd_over15,
        odd_btts=odd_btts,
        odd_over25=odd_over25,
        janela=JANELA
    ).analisar()

    if not isinstance(resultado, dict):
        raise TypeError(
            "O MatchAnalysisEngine precisa retornar "
            "um dicionário válido."
        )

    if resultado.get("erro"):
        raise ValueError(
            resultado["erro"]
        )

    return resultado


def inicializar_estado():
    if "partida_analisada" not in st.session_state:
        st.session_state.partida_analisada = False

    if "mandante_ativo" not in st.session_state:
        st.session_state.mandante_ativo = None

    if "visitante_ativo" not in st.session_state:
        st.session_state.visitante_ativo = None

    if "competicao_ativa" not in st.session_state:
        st.session_state.competicao_ativa =(
            COMPETICAO_PADRAO
        )


def obter_time_padrao(
    nomes_times,
    nome_desejado,
    indice_alternativo
):
    if nome_desejado in nomes_times:
        return nome_desejado

    if not nomes_times:
        return None

    indice_seguro = min(
        indice_alternativo,
        len(nomes_times) - 1
    )

    return nomes_times[
        indice_seguro
    ]


def renderizar_configuracoes_laterais():
    autenticado = usuario_esta_autenticado()

    with st.sidebar:
        st.markdown(
            """
            <div class="marca-lateral">
                <div class="marca-lateral-selo">⚽</div>
                <div>
                    <div class="marca-lateral-nome">
                        ENTRADA<span>PRO</span>
                    </div>
                    <div class="marca-lateral-tagline">
                        FOOTBALL INTELLIGENCE
                    </div>
                </div>
            </div>
            <div class="marca-lateral-linha"></div>
            """,
            unsafe_allow_html=True
        )

        st.caption(
            "Análise inteligente de partidas "
            "e identificação de apostas de valor."
        )

        if autenticado:
            renderizar_usuario_sidebar()

            st.page_link(
                "pages/2_Assinatura_PRO.py",
                label="⭐ EntradaPro PRO",
                use_container_width=True
            )

        st.divider()

        st.markdown(
            "### Odds de mercado"
        )

        st.caption(
            "Confira a odd atual no seu site de apostas "
            "preferido e informe abaixo para calcular o Value."
        )

        if autenticado:
            odd_over15 = st.number_input(
                "Odd — Mais de 1,5 gols",
                min_value=1.01,
                max_value=20.00,
                value=1.40,
                step=0.01,
                format="%.2f",
                key="odd_over15"
            )

            odd_over25 = st.number_input(
                "Odd — Mais de 2,5 gols",
                min_value=1.01,
                max_value=20.00,
                value=2.10,
                step=0.01,
                format="%.2f",
                key="odd_over25"
            )

            odd_btts = st.number_input(
                "Odd — Ambas marcam",
                min_value=1.01,
                max_value=20.00,
                value=1.70,
                step=0.01,
                format="%.2f",
                key="odd_btts"
            )

        else:
            st.number_input(
                "Odd — Mais de 1,5 gols",
                min_value=1.01,
                max_value=20.00,
                value=1.40,
                step=0.01,
                format="%.2f",
                disabled=True,
                key="odd_over15_visitante"
            )

            st.number_input(
                "Odd — Mais de 2,5 gols",
                min_value=1.01,
                max_value=20.00,
                value=2.10,
                step=0.01,
                format="%.2f",
                disabled=True,
                key="odd_over25_visitante"
            )

            st.number_input(
                "Odd — Ambas marcam",
                min_value=1.01,
                max_value=20.00,
                value=1.70,
                step=0.01,
                format="%.2f",
                disabled=True,
                key="odd_btts_visitante"
            )

            if st.button(
                "🔒 Entrar para ajustar odds",
                use_container_width=True,
                key="login_odds_visitante"
            ):
                abrir_autenticacao("login")
                st.rerun()

            odd_over15 = 1.40
            odd_over25 = 2.10
            odd_btts = 1.70

        st.divider()

        st.caption(
            "As odds são usadas pelo ValueEngine "
            "para comparar o preço de mercado com "
            "a probabilidade calculada."
        )

    return {
        "odd_over15": odd_over15,
        "odd_over25": odd_over25,
        "odd_btts": odd_btts
    }


def atualizar_partida_ativa(
    resultado_seletor
):
    if not resultado_seletor["analisar"]:
        return

    if not usuario_esta_autenticado():
        abrir_autenticacao(
            "login"
        )

        st.rerun()

    st.session_state.competicao_ativa = (
        resultado_seletor[
            "competicao"
        ]
    )

    st.session_state.mandante_ativo = (
        resultado_seletor[
            "mandante"
        ]
    )

    st.session_state.visitante_ativo = (
        resultado_seletor[
            "visitante"
        ]
    )

    st.session_state.partida_analisada = True


def renderizar_fundamentos(
    resultado_prediction
):
    with st.expander(
        "📊 Ver fundamentos da previsão"
    ):
        st.markdown(
            "### Mais de 1,5 gols"
        )

        mostrar_motivos(
            resultado_prediction[
                "motivos_mais_15"
            ]
        )

        st.markdown(
            "### Ambas marcam"
        )

        mostrar_motivos(
            resultado_prediction[
                "motivos_btts"
            ]
        )


def renderizar_rodape():
    st.markdown(
        """
        <div class="footer-warning">
            As análises são estatísticas
            e não garantem lucro.
            Aposte com responsabilidade.
        </div>
        """,
        unsafe_allow_html=True
    )


def renderizar_resumo_visual(
    nome_mandante,
    nome_visitante,
    resultado_match,
    resultado_prediction
):
    st.markdown(
        "### 📊 Resumo visual"
    )

    dados = pd.DataFrame(
        {
            "Indicador": [
                f"Vitória — {nome_mandante}",
                "Empate",
                f"Vitória — {nome_visitante}",
                "Mais de 1,5 gols",
                "Ambas marcam"
            ],
            "Probabilidade": [
                float(
                    resultado_match[
                        "probabilidade_casa"
                    ]
                ),
                float(
                    resultado_match[
                        "probabilidade_empate"
                    ]
                ),
                float(
                    resultado_match[
                        "probabilidade_fora"
                    ]
                ),
                float(
                    resultado_prediction[
                        "mais_15"
                    ]
                ),
                float(
                    resultado_prediction[
                        "ambas_marcam"
                    ]
                )
            ]
        }
    )

    st.bar_chart(
        dados,
        x="Indicador",
        y="Probabilidade",
        horizontal=True,
        height=330
    )

    st.caption(
        "BTTS é exibido para análise, maspermanece "
        "não validado estrategicamente na V1."
    )


def renderizar_resumo_decisao(
    melhor_mercado,
    resultado_prediction,
    resultado_value,
    resultado_oportunidade
):
    recomendacao_validada = resultado_oportunidade.get(
        "recomendacao_validada",
        True
    )

    with st.container(border=True):

        if not recomendacao_validada:
            st.markdown(
                "## 🚫 NÃO APOSTAR"
            )

            st.caption(
                "Nenhum mercado atingiu os critérios "
                "estratégicos validados."
            )

            return

        if melhor_mercado == "Mais de 1,5 gols":
            probabilidade = resultado_prediction[
                "mais_15"
            ]

            status = resultado_prediction.get(
                "status_estrategico_over15",
                ""
            )

        else:
            probabilidade = resultado_prediction[
                "ambas_marcam"
            ]

            status = resultado_prediction.get(
                "status_estrategico_btts",
                ""
            )

        col1, col2 = st.columns(
            [1.5, 1]
        )

        with col1:
            st.caption(
                "MELHOR OPORTUNIDADE"
            )

            st.markdown(
                f"## 🎯 {melhor_mercado}"
            )

            st.markdown(
                f"### {probabilidade:.2f}%"
            )

            if status:
                st.success(
                    status
                )

        with col2:
            st.metric(
                "Odd",
                f"{resultado_value['odd_casa']:.2f}"
            )

            st.metric(
                "Edge",
                f"{resultado_value['edge']:+.2f}%"
            )

            st.metric(
                "Valor esperado",
                f"{resultado_value['valor_esperado']:+.2f}%"
            )


def renderizar_performance():
    st.markdown(
        "## 📈 Validação histórica"
    )

    st.caption(
        "Resultados consolidados do backtest "
        "do Brasileirão Série A entre 2022 e 2024."
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Apostas",
            "201"
        )

    with col2:
        st.metric(
            "Taxa de acerto",
            "76,62%"
        )

    with col3:
        st.metric(
            "ROI",
            "+7,26%"
        )

    with col4:
        st.metric(
            "Temporadas positivas",
            "3/3"
        )

    st.divider()

    dados_roi = pd.DataFrame(
        {
            "Temporada": [
                "2022",
                "2023",
                "2024"
            ],
            "ROI": [
                17.60,
                0.27,
                7.27
            ]
        }
    )

    st.markdown(
        "### ROI por temporada — Over 1.5≥ 70%"
    )

    st.bar_chart(
        dados_roi,
        x="Temporada",
        y="ROI",
        height=300
    )

    st.success(
        "Over 1.5 — Estratégia ROBUSTA"
    )

    st.write(
        "Corte validado em probabilidade ≥ 70%, "
        "com resultado positivo nas três temporadas."
    )

    st.divider()

    st.markdown(
        "### ⚠️ Ambas marcam — BTTS"
    )

    st.warning(
        "Mercado não validado na V1"
    )

    st.write(
        "Os testes multitemporada ainda não apresentaram "
        "robustez suficiente para utilizar BTTS como "
        "estratégia oficial."
    )


def renderizar_metodologia():
    st.markdown(
        "## 🧠 Metodologia EntradaPro"
    )

    st.caption(
        "Entenda as principais camadas utilizadas "
        "na análise de uma partida."
    )

    col1, col2 = st.columns(2)

    with col1:

        with st.container(border=True):
            st.markdown(
                "### 🏟️ Home / Away Engine"
            )
            st.write(
                "Separa o comportamento como "
                "mandante e visitante."
            )

        with st.container(border=True):
            st.markdown(
                "### 🛡️ Opponent Strength"
            )
            st.write(
                "Considera a força dos adversários."
            )

        with st.container(border=True):
            st.markdown(
                "### 💰 Value Engine"
            )
            st.write(
                "Compara a probabilidade calculada "
                "com a odd de mercado."
            )

    st.divider()

    st.info(
        "Over 1.5 possui validação multitemporada "
        "no corte ≥ 70%. BTTS permanece experimental."
    )

    st.error(
        "Se nenhum mercado atingir os critérios "
        "estratégicos, o EntradaPro recomenda NÃO APOSTAR."
    )


def main():
    aplicar_estilos()
    inicializar_estado()
    inicializar_banco()
    expirar_assinaturas_vencidas()
    inicializar_estado_autenticacao()

    if not usuario_esta_autenticado():
        renderizar_acoes_visitante_topo()

    try:
        total_partidas_base = len(carregar_dados())
    except Exception:
        total_partidas_base = None

    renderizar_cabecalho(total_partidas_base)
    renderizar_dialogo_autenticacao()

    st.warning(
        "MINISTÉRIO DA FAZENDA ADVERTE: "
        "APOSTA NÃO É INVESTIMENTO | "
        "🔞 +18 | Jogue com responsabilidade"
    )

    try:
        partidas = carregar_dados()

        times = listar_times(
            partidas
        )

    except Exception as erro:
        st.error(
            f"Erro ao carregar os dados: "
            f"{erro}"
        )

        st.stop()

    nomes_times = list(
        times.keys()
    )

    if len(nomes_times) < 2:
        st.error(
            "Não existem equipes suficientes "
            "para análise."
        )

        st.stop()

    mandante_padrao = obter_time_padrao(
        nomes_times=nomes_times,
        nome_desejado="Flamengo",
        indice_alternativo=0
    )

    visitante_padrao = obter_time_padrao(
        nomes_times=nomes_times,
        nome_desejado="Palmeiras",
        indice_alternativo=1
    )

    # Primeira visita: em vez de esperar o usuário escolher e
    # clicar em "Analisar partida", já mostramos de cara uma
    # análise pronta com um confronto de destaque - reduz o
    # primeiro passo necessário para ver o produto funcionando.
    eh_primeira_visita = (
        not st.session_state.partida_analisada
        and st.session_state.mandante_ativo is None
        and st.session_state.visitante_ativo is None
        and usuario_esta_autenticado()
    )

    if eh_primeira_visita:
        st.session_state.competicao_ativa = COMPETICAO_PADRAO
        st.session_state.mandante_ativo = mandante_padrao
        st.session_state.visitante_ativo = visitante_padrao
        st.session_state.partida_analisada = True

    configuracao_lateral = (
        renderizar_configuracoes_laterais()
    )

    if usuario_esta_autenticado():
        try:
            renderizar_alertas_risco()
        except Exception:
            pass

        try:
            renderizar_melhores_entradas()
        except Exception:
            pass

        try:
            renderizar_vitrine_campeonatos()
        except Exception:
            pass

        try:
            selecao_jogo_futuro = renderizar_jogos_futuros(
                nomes_times
            )
        except Exception:
            # Falha silenciosa e segura: se a busca de jogos
            # futuros der qualquer problema (sem chave de API,
            # API fora do ar, etc.), o site continua funcionando
            # normalmente com a seleção manual abaixo.
            selecao_jogo_futuro = None

        if selecao_jogo_futuro:
            st.session_state.competicao_ativa = COMPETICAO_PADRAO
            st.session_state.mandante_ativo = selecao_jogo_futuro[0]
            st.session_state.visitante_ativo = selecao_jogo_futuro[1]
            st.session_state.partida_analisada = True
            st.rerun()

        resultado_seletor = renderizar_seletor_partida(
            competicoes=[
                COMPETICAO_PADRAO
            ],
            times=nomes_times,
            competicao_padrao=(
                st.session_state.competicao_ativa
                or COMPETICAO_PADRAO
            ),
            mandante_padrao=(
                st.session_state.mandante_ativo
                or mandante_padrao
            ),
            visitante_padrao=(
                st.session_state.visitante_ativo
                or visitante_padrao
            )
        )

        atualizar_partida_ativa(
            resultado_seletor
        )

    else:
        st.markdown(
            "### 🔎 Análise de partida"
        )

        with st.container(
            border=True
        ):
            col1, col2, col3 = st.columns(
                [1, 1, 0.8]
            )

            with col1:
                st.selectbox(
                    "Mandante",
                    options=[
                        mandante_padrao
                    ],
                    disabled=True,
                    key="mandante_visitante_preview"
                )

            with col2:
                st.selectbox(
                    "Visitante",
                    options=[
                        visitante_padrao
                    ],
                    disabled=True,
                    key="visitante_visitante_preview"
                )

            with col3:
                st.markdown(
                    "<div style='height:28px'></div>",
                    unsafe_allow_html=True
                )

                if st.button(
                    "🔒 Analisar partida",
                    use_container_width=True,
                    key="analisar_visitante"
                ):
                    abrir_autenticacao(
                        "login"
                    )

                    st.rerun()

        st.caption(
            "Entre ou crie sua conta para utilizar "
            "as ferramentas do EntradaPro."
        )

        renderizar_estado_inicial()
        renderizar_rodape()
        return

    if not st.session_state.partida_analisada:
        renderizar_estado_inicial()
        renderizar_rodape()
        return

    if eh_primeira_visita:
        st.caption(
            "⭐ Mostrando um confronto em destaque para você "
            "começar. Escolha outros times acima quando quiser."
        )

    nome_mandante = (
        st.session_state.mandante_ativo
    )

    nome_visitante = (
        st.session_state.visitante_ativo
    )

    if (
        nome_mandante not in times
        or nome_visitante not in times
    ):
        st.error(
            "Uma das equipes selecionadas "
            "não foi localizada no dataset."
        )

        st.session_state.partida_analisada = False
        st.stop()

    if nome_mandante == nome_visitante:
        st.warning(
            "Escolha equipes diferentes."
        )

        st.stop()

    odd_over15 = configuracao_lateral[
        "odd_over15"
    ]

    odd_over25 = configuracao_lateral.get(
        "odd_over25"
    )

    odd_btts = configuracao_lateral[
        "odd_btts"
    ]

    id_mandante = times[
        nome_mandante
    ]

    id_visitante = times[
        nome_visitante
    ]

    try:
        with st.spinner(
            "Executando os motores do EntradaPro..."
        ):
            analise_completa = calcular_analise_completa(
                partidas=partidas,
                id_mandante=id_mandante,
                id_visitante=id_visitante,
                odd_over15=odd_over15,
                odd_btts=odd_btts,
                odd_over25=odd_over25
            )

    except Exception as erro:
        st.error(
            "Não foi possível realizar "
            f"a análise: {erro}"
        )

        st.stop()

    analise_mandante = analise_completa[
        "analise_mandante"
    ]

    analise_visitante = analise_completa[
        "analise_visitante"
    ]

    resultado_match = analise_completa[
        "resultado_match"
    ]

    resultado_prediction = analise_completa[
        "resultado_prediction"
    ]

    melhor_mercado = analise_completa[
        "melhor_mercado"
    ]

    resultado_value = analise_completa[
        "resultado_value"
    ]

    resultado_oportunidade = analise_completa[
        "resultado_oportunidade"
    ]

    favorito = identificar_favorito(
        resultado_match=resultado_match,
        nome_mandante=nome_mandante,
        nome_visitante=nome_visitante
    )

    (
        aba_visao_geral,
        aba_analise,
        aba_mercados,
        aba_performance,
        aba_metodologia
    ) = st.tabs(
        [
            "🏠 Visão Geral",
            "⚽ Análise da Partida",
            "🎯 Mercados",
            "📈 Performance",
            "🧠 Metodologia"
        ]
    )

    with aba_visao_geral:

        renderizar_overview(
            nome_mandante=nome_mandante,
            nome_visitante=nome_visitante,
            favorito=favorito,
            resultado_match=resultado_match,
            resultado_prediction=resultado_prediction,
            melhor_mercado=melhor_mercado,
            resultado_value=resultado_value,
            resultado_oportunidade=resultado_oportunidade
        )

        st.divider()

        try:
            renderizar_secao_corners(
                id_mandante=id_mandante,
                id_visitante=id_visitante,
            )
        except Exception:
            pass

    with aba_analise:

        renderizar_titulo_secao(
            "Comparação das equipes"
        )

        renderizar_comparacao_times(
            nome_mandante=nome_mandante,
            nome_visitante=nome_visitante,
            analise_mandante=analise_mandante,
            analise_visitante=analise_visitante,
            resultado_match=resultado_match,
            favorito=favorito
        )

        renderizar_titulo_secao(
            "Forma recente"
        )

        renderizar_comparacao_forma(
            nome_mandante=nome_mandante,
            nome_visitante=nome_visitante,
            analise_mandante=analise_mandante,
            analise_visitante=analise_visitante
        )

        if usuario_eh_pro():
            renderizar_titulo_secao(
                "Comparação dos motores"
            )

            renderizar_comparacao_motores(
                nome_mandante=nome_mandante,
                nome_visitante=nome_visitante,
                analise_mandante=analise_mandante,
                analise_visitante=analise_visitante
            )

            renderizar_titulo_secao(
                "Mapa de forças"
            )

            renderizar_radar_chart(
                nome_mandante=nome_mandante,
                nome_visitante=nome_visitante,
                analise_mandante=analise_mandante,
                analise_visitante=analise_visitante
            )

        else:
            renderizar_titulo_secao(
                "Comparação dos motores"
            )

            renderizar_bloqueio_pro(
                titulo="Comparação dos motores exclusiva do plano PRO",
                mensagem=(
                    "Rating, Forma, Pulse, Casa/Fora e força dos adversários "
                    "estão disponíveis para usuários PRO."
                )
            )

            renderizar_titulo_secao(
                "Mapa de forças"
            )

            renderizar_bloqueio_pro(
                titulo="Mapa de forças exclusivo do plano PRO",
                mensagem=(
                    "A visualização avançada das forças das equipes "
                    "está disponível para usuários PRO."
                )
            )

    with aba_mercados:

        renderizar_titulo_secao(
            "Mercados analisados"
        )

        renderizar_mercados_gols(
            resultado_prediction=resultado_prediction
        )

        renderizar_titulo_secao(
            "Value e recomendação"
        )

        if usuario_eh_pro():
            renderizar_value_card(
                melhor_mercado=melhor_mercado,
                resultado_value=resultado_value,
                resultado_oportunidade=resultado_oportunidade
            )
        else:
            renderizar_bloqueio_pro(
                titulo="Value e recomendação exclusivos do plano PRO",
                mensagem=(
                    "Odd justa, edge, valor esperado e recomendação "
                    "estratégica estão disponíveis para usuários PRO."
                )
            )

        renderizar_fundamentos_previsao(
            resultado_prediction=resultado_prediction
        )

    with aba_performance:
        if usuario_eh_pro():
            renderizar_performance_view()
        else:
            renderizar_bloqueio_pro(
                titulo="Performance exclusiva do plano PRO",
                mensagem=(
                    "Os dados de validação histórica, ROI, "
                    "taxa de acerto e backtests completos "
                    "estão disponíveis para usuários PRO."
                )
            )

    with aba_metodologia:
        renderizar_metodologia_view()

    renderizar_rodape()


if __name__ == "__main__":
    main()