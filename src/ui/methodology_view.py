import html

import streamlit as st


# =========================================================
# ESTILOS
# =========================================================

def aplicar_estilos_metodologia():
    """
    Aplica os estilos da aba de metodologia.
    """
    st.html(
        """
        <style>

            .method-intro {
                color: #8fa2b7;
                font-size: 11px;
                line-height: 1.55;
                margin-bottom: 16px;
            }


            .method-flow {
                display: grid;
                grid-template-columns: repeat(6, 1fr);
                gap: 8px;
                margin-bottom: 20px;
            }


            .method-flow-step {
                background:
                    linear-gradient(
                        145deg,
                        rgba(16, 34, 55, 0.98),
                        rgba(9, 24, 41, 0.98)
                    );

                border:
                    1px solid rgba(93, 129, 166, 0.24);

                border-radius: 12px;

                padding: 13px 9px;

                text-align: center;
            }


            .method-flow-number {
                color: #65e3b0;

                font-size: 10px;

                font-weight: 900;

                margin-bottom: 5px;
            }


            .method-flow-title {
                color: #ffffff;

                font-size: 11px;

                font-weight: 800;

                line-height: 1.25;
            }


            .method-section-title {
                color: #ffffff;

                font-size: 18px;

                font-weight: 850;

                margin-top: 20px;

                margin-bottom: 10px;
            }


            .method-card {
                background:
                    linear-gradient(
                        145deg,
                        rgba(16, 34, 55, 0.98),
                        rgba(9, 24, 41, 0.98)
                    );

                border:
                    1px solid rgba(93, 129, 166, 0.24);

                border-radius: 15px;

                padding: 17px;

                min-height: 150px;

                transition:
                    transform 0.18s ease,
                    border-color 0.18s ease;
            }


            .method-card:hover {
                transform: translateY(-2px);

                border-color:
                    rgba(83, 217, 159, 0.36);
            }


            .method-card-icon {
                font-size: 20px;
                margin-bottom: 8px;
            }


            .method-card-title {
                color: #ffffff;

                font-size: 16px;

                font-weight: 850;

                line-height: 1.2;
            }


            .method-card-text {
                color: #aebdca;

                font-size: 10px;

                line-height: 1.5;

                margin-top: 7px;
            }


            .method-card-note {
                color: #7f92a6;

                font-size: 9px;

                font-weight: 650;

                margin-top: 9px;
            }


            .method-strategy {
                background:
                    linear-gradient(
                        145deg,
                        rgba(13, 48, 42, 0.96),
                        rgba(8, 30, 28, 0.96)
                    );

                border:
                    1px solid rgba(83, 217, 159, 0.34);

                border-radius: 15px;

                padding: 17px;

                margin-top: 14px;
            }


            .method-strategy-label {
                color: #83b8a6;

                font-size: 9px;

                font-weight: 800;

                letter-spacing: 0.8px;

                text-transform: uppercase;
            }


            .method-strategy-title {
                color: #ffffff;

                font-size: 18px;

                font-weight: 900;

                margin-top: 4px;
            }


            .method-strategy-text {
                color: #b7c8c1;

                font-size: 10px;

                line-height: 1.55;

                margin-top: 8px;
            }


            .method-warning {
                background:
                    linear-gradient(
                        145deg,
                        rgba(71, 28, 37, 0.96),
                        rgba(40, 18, 24, 0.96)
                    );

                border:
                    1px solid rgba(239, 117, 131, 0.34);

                border-radius: 15px;

                padding: 17px;

                margin-top: 12px;
            }


            .method-warning-label {
                color: #d997a1;

                font-size: 9px;

                font-weight: 800;

                letter-spacing: 0.8px;

                text-transform: uppercase;
            }


            .method-warning-title {
                color: #ffffff;

                font-size: 18px;

                font-weight: 900;

                margin-top: 4px;
            }


            .method-warning-text {
                color: #c8b9bd;

                font-size: 10px;

                line-height: 1.55;

                margin-top: 8px;
            }


            .method-disclaimer {
                color: #7f91a5;

                font-size: 9px;

                line-height: 1.45;

                margin-top: 14px;
            }


            @media screen and (max-width: 1000px) {

                .method-flow {
                    grid-template-columns: repeat(3, 1fr);
                }
            }


            @media screen and (max-width: 768px) {

                .method-flow {
                    grid-template-columns: repeat(2, 1fr);
                }

                .method-card {
                    min-height: auto;
                }
            }

        </style>
        """
    )


# =========================================================
# COMPONENTES
# =========================================================

def renderizar_fluxo():
    """
    Renderiza o fluxo macro da análise.
    """
    etapas = [
        ("1", "Dados"),
        ("2", "Motores"),
        ("3", "Probabilidades"),
        ("4", "Validação"),
        ("5", "Value"),
        ("6", "Decisão"),
    ]

    partes = []

    for numero, titulo in etapas:
        numero_seguro = html.escape(
            str(numero)
        )

        titulo_seguro = html.escape(
            str(titulo)
        )

        partes.append(
            (
                '<div class="method-flow-step">'

                '<div class="method-flow-number">'
                f"{numero_seguro}"
                "</div>"

                '<div class="method-flow-title">'
                f"{titulo_seguro}"
                "</div>"

                "</div>"
            )
        )

    st.html(
        (
            '<div class="method-flow">'
            + "".join(partes)
            + "</div>"
        )
    )


def renderizar_card(
    icone,
    titulo,
    texto,
    nota=""
):
    """
    Renderiza um card de metodologia.
    """
    icone_seguro = html.escape(
        str(icone)
    )

    titulo_seguro = html.escape(
        str(titulo)
    )

    texto_seguro = html.escape(
        str(texto)
    )

    nota_segura = html.escape(
        str(nota)
    )

    conteudo = (
        '<div class="method-card">'

        '<div class="method-card-icon">'
        f"{icone_seguro}"
        "</div>"

        '<div class="method-card-title">'
        f"{titulo_seguro}"
        "</div>"

        '<div class="method-card-text">'
        f"{texto_seguro}"
        "</div>"
    )

    if nota_segura:
        conteudo += (
            '<div class="method-card-note">'
            f"{nota_segura}"
            "</div>"
        )

    conteudo += "</div>"

    st.html(
        conteudo
    )


# =========================================================
# FUNÇÃO PRINCIPAL
# =========================================================

def renderizar_metodologia_view():
    """
    Renderiza a aba de metodologia.
    """
    aplicar_estilos_metodologia()

    st.markdown(
        "## 🧠 Como a análise é construída"
    )

    st.html(
        """
        <div class="method-intro">
            O sistema combina diferentes camadas estatísticas
            para transformar o histórico das equipes em uma
            leitura de partida, probabilidades de mercado e
            uma decisão estratégica final.
        </div>
        """
    )

    renderizar_fluxo()

    st.html(
        """
        <div class="method-section-title">
            Motores de análise
        </div>
        """
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        renderizar_card(
            icone="⭐",
            titulo="Rating",
            texto=(
                "Resume a força geral recente da equipe "
                "a partir do desempenho observado."
            )
        )

    with col2:
        renderizar_card(
            icone="📊",
            titulo="Forma",
            texto=(
                "Avalia vitórias, empates, derrotas, "
                "produção ofensiva e comportamento recente."
            )
        )

    with col3:
        renderizar_card(
            icone="⚡",
            titulo="Pulse",
            texto=(
                "Procura identificar aceleração, estabilidade "
                "ou queda no momento recente da equipe."
            )
        )

    col1, col2 = st.columns(2)

    with col1:
        renderizar_card(
            icone="🏟️",
            titulo="Casa / Fora",
            texto=(
                "Separa o desempenho da equipe conforme "
                "o mando de campo."
            )
        )

    with col2:
        renderizar_card(
            icone="🛡️",
            titulo="Força dos adversários",
            texto=(
                "Considera o nível recente dos adversários "
                "enfrentados para dar contexto ao desempenho."
            )
        )

    st.html(
        """
        <div class="method-section-title">
            Da análise para os mercados
        </div>
        """
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        renderizar_card(
            icone="🎯",
            titulo="Prediction",
            texto=(
                "Transforma os dados das equipes em "
                "probabilidades estimadas para os mercados."
            ),
            nota="Na V1: Over 1.5 e BTTS."
        )

    with col2:
        renderizar_card(
            icone="✅",
            titulo="Validação estratégica",
            texto=(
                "Compara o sinal atual com os critérios "
                "obtidos na validação histórica."
            ),
            nota=(
                "Over 1.5 possui corte validado em ≥ 70%."
            )
        )

    with col3:
        renderizar_card(
            icone="💰",
            titulo="Value Engine",
            texto=(
                "Compara a probabilidade calculada com a "
                "probabilidade implícita da odd de mercado."
            ),
            nota="Gera odd justa, edge e valor esperado."
        )

    st.html(
        """
        <div class="method-strategy">

            <div class="method-strategy-label">
                REGRA ESTRATÉGICA DA V1
            </div>

            <div class="method-strategy-title">
                Over 1.5 validado
            </div>

            <div class="method-strategy-text">
                O mercado Mais de 1,5 gols possui validação
                multitemporada no corte de probabilidade
                igual ou superior a 70%. BTTS permanece
                experimental e não é tratado como estratégia
                oficial da V1.
            </div>

        </div>
        """
    )

    st.html(
        """
        <div class="method-warning">

            <div class="method-warning-label">
                REGRA DE SEGURANÇA
            </div>

            <div class="method-warning-title">
                🚫 NÃO APOSTAR
            </div>

            <div class="method-warning-text">
                Se nenhum mercado atingir os critérios
                estratégicos validados, a decisão final do
                sistema é não recomendar uma aposta.
            </div>

        </div>
        """
    )

    st.html(
        """
        <div class="method-disclaimer">
            A metodologia apresentada nesta página descreve
            a lógica geral da análise. Os detalhes internos
            de cálculo e ponderação dos motores não são
            expostos nesta interface.
        </div>
        """
    )