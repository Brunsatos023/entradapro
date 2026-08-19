import streamlit as st


def aplicar_estilos_seletor():
    """
    Aplica o estilo visual da barra de seleção da partida.
    """
    st.html(
        """
        <style>
            .match-selector-header {
                margin-bottom: 12px;
            }

            .match-selector-title {
                color: #ffffff;
                font-size: 14px;
                font-weight: 800;
                letter-spacing: 0.4px;
            }

            .match-selector-subtitle {
                color: #8fa1b6;
                font-size: 12px;
                margin-top: 3px;
            }

            div[data-testid="stVerticalBlockBorderWrapper"] {
                border-color: rgba(74, 111, 148, 0.32);
                border-radius: 18px;
                background:
                    linear-gradient(
                        145deg,
                        rgba(13, 29, 48, 0.98),
                        rgba(7, 20, 36, 0.98)
                    );
            }

            div[data-baseweb="select"] > div {
                min-height: 48px;
                background-color: rgba(15, 32, 52, 0.96);
                border-color: rgba(87, 125, 163, 0.35);
                border-radius: 11px;
                color: #ffffff;
            }

            div[data-baseweb="select"] > div:hover {
                border-color: rgba(83, 217, 159, 0.65);
            }

            div[data-testid="stSelectbox"] label p {
                color: #9eb0c4;
                font-size: 11px;
                font-weight: 800;
                letter-spacing: 0.8px;
                text-transform: uppercase;
            }

            div[data-testid="stButton"] button {
                width: 100%;
                min-height: 48px;
                margin-top: 28px;
                background:
                    linear-gradient(
                        90deg,
                        #168b55,
                        #24b86e
                    );
                border: 1px solid rgba(83, 217, 159, 0.45);
                border-radius: 11px;
                color: #ffffff;
                font-size: 13px;
                font-weight: 850;
                letter-spacing: 0.5px;
                box-shadow:
                    0 8px 20px rgba(24, 154, 91, 0.22);
            }

            div[data-testid="stButton"] button:hover {
                background:
                    linear-gradient(
                        90deg,
                        #1a9d61,
                        #2ac77b
                    );
                border-color: #64e4b0;
                color: #ffffff;
                transform: translateY(-1px);
            }
        </style>
        """
    )


def organizar_times(lista_times):
    """
    Remove valores vazios, duplicados e organiza os times.
    """
    if not lista_times:
        return []

    times_validos = {
        str(time).strip()
        for time in lista_times
        if str(time).strip()
    }

    return sorted(
        times_validos
    )


def encontrar_indice(
    opcoes,
    valor_padrao
):
    """
    Localiza o índice de uma opção padrão.

    Retorna zero quando o valor não é encontrado.
    """
    if not opcoes:
        return 0

    if valor_padrao in opcoes:
        return opcoes.index(
            valor_padrao
        )

    return 0


def renderizar_seletor_partida(
    competicoes,
    times,
    competicao_padrao=None,
    mandante_padrao=None,
    visitante_padrao=None
):
    """
    Renderiza a barra superior de seleção.

    Retorna um dicionário com:
    - competição;
    - mandante;
    - visitante;
    - botão analisar;
    - seleção válida.
    """
    aplicar_estilos_seletor()

    competicoes_organizadas = organizar_times(
        competicoes
    )

    times_organizados = organizar_times(
        times
    )

    if not competicoes_organizadas:
        st.error(
            "Nenhuma competição disponível."
        )

        return {
            "competicao": None,
            "mandante": None,
            "visitante": None,
            "analisar": False,
            "selecao_valida": False
        }

    if len(times_organizados) < 2:
        st.error(
            "São necessários pelo menos dois times disponíveis."
        )

        return {
            "competicao": None,
            "mandante": None,
            "visitante": None,
            "analisar": False,
            "selecao_valida": False
        }

    indice_competicao = encontrar_indice(
        competicoes_organizadas,
        competicao_padrao
    )

    indice_mandante = encontrar_indice(
        times_organizados,
        mandante_padrao
    )

    indice_visitante = encontrar_indice(
        times_organizados,
        visitante_padrao
    )

    with st.container(
        border=True
    ):
        st.html(
            """
            <div class="match-selector-header">
                <div class="match-selector-title">
                    Selecionar partida
                </div>

                <div class="match-selector-subtitle">
                    Escolha a competição e as equipes para executar a análise.
                </div>
            </div>
            """
        )

        coluna_competicao, coluna_mandante, coluna_separador, \
            coluna_visitante, coluna_botao = st.columns(
                [1.15, 1.25, 0.16, 1.25, 0.92],
                vertical_alignment="bottom"
            )

        with coluna_competicao:
            competicao = st.selectbox(
                "Competição",
                options=competicoes_organizadas,
                index=indice_competicao,
                key="selector_competicao"
            )

        with coluna_mandante:
            mandante = st.selectbox(
                "Mandante",
                options=times_organizados,
                index=indice_mandante,
                key="selector_mandante"
            )

        with coluna_separador:
            st.markdown(
                "<div style='"
                "text-align:center;"
                "color:#ffffff;"
                "font-size:18px;"
                "font-weight:900;"
                "padding-bottom:13px;"
                "'>×</div>",
                unsafe_allow_html=True
            )

        with coluna_visitante:
            visitante = st.selectbox(
                "Visitante",
                options=times_organizados,
                index=indice_visitante,
                key="selector_visitante"
            )

        with coluna_botao:
            analisar = st.button(
                "📈 ANALISAR PARTIDA",
                use_container_width=True,
                key="botao_analisar_partida"
            )

    selecao_valida = (
        mandante != visitante
    )

    if analisar and not selecao_valida:
        st.warning(
            "Mandante e visitante precisam ser times diferentes."
        )

    return {
        "competicao": competicao,
        "mandante": mandante,
        "visitante": visitante,
        "analisar": (
            analisar
            and selecao_valida
        ),
        "selecao_valida": selecao_valida
    }