import html

import matplotlib.pyplot as plt
import streamlit as st


# =========================================================
# DADOS CONSOLIDADOS DA V1
# =========================================================

TOTAL_APOSTAS = 201
TAXA_ACERTO = 76.62
ROI_CONSOLIDADO = 7.26
TEMPORADAS_POSITIVAS = "3/3"

ROI_POR_TEMPORADA = {
    "2022": 17.60,
    "2023": 0.27,
    "2024": 7.27,
}


# =========================================================
# ESTILOS
# =========================================================

def aplicar_estilos_performance():
    """
    Aplica os estilos da aba de performance.
    """
    st.html(
        """
        <style>

            .performance-intro {
                color: #8fa2b7;
                font-size: 11px;
                line-height: 1.55;
                margin-bottom: 16px;
            }


            .performance-kpi {
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

                min-height: 112px;
            }


            .performance-kpi-label {
                color: #8ea1b6;

                font-size: 9px;

                font-weight: 800;

                letter-spacing: 0.6px;

                text-transform: uppercase;
            }


            .performance-kpi-value {
                color: #ffffff;

                font-size: 29px;

                font-weight: 900;

                line-height: 1;

                margin-top: 9px;
            }


            .performance-kpi-positive {
                color: #62e3af;
            }


            .performance-block {
                background:
                    linear-gradient(
                        145deg,
                        rgba(16, 34, 55, 0.98),
                        rgba(9, 24, 41, 0.98)
                    );

                border:
                    1px solid rgba(93, 129, 166, 0.24);

                border-radius: 16px;

                padding: 18px;

                margin-top: 16px;
            }


            .performance-block-valid {
                background:
                    linear-gradient(
                        145deg,
                        rgba(13, 48, 42, 0.96),
                        rgba(8, 30, 28, 0.96)
                    );

                border-color:
                    rgba(83, 217, 159, 0.34);
            }


            .performance-block-warning {
                background:
                    linear-gradient(
                        145deg,
                        rgba(42, 42, 31, 0.96),
                        rgba(26, 29, 24, 0.96)
                    );

                border-color:
                    rgba(231, 185, 75, 0.26);
            }


            .performance-block-top {
                display: flex;
                align-items: flex-start;
                justify-content: space-between;
                gap: 12px;
            }


            .performance-block-label {
                color: #8497ab;

                font-size: 9px;

                font-weight: 800;

                letter-spacing: 0.8px;

                text-transform: uppercase;
            }


            .performance-block-title {
                color: #ffffff;

                font-size: 20px;

                font-weight: 900;

                margin-top: 4px;
            }


            .performance-badge {
                border-radius: 999px;

                padding: 5px 9px;

                font-size: 9px;

                font-weight: 850;

                white-space: nowrap;
            }


            .performance-badge-valid {
                color: #72e5b5;

                background:
                    rgba(83, 217, 159, 0.11);

                border:
                    1px solid rgba(83, 217, 159, 0.27);
            }


            .performance-badge-warning {
                color: #efd16f;

                background:
                    rgba(231, 185, 75, 0.10);

                border:
                    1px solid rgba(231, 185, 75, 0.24);
            }


            .performance-block-text {
                color: #b8c7d6;

                font-size: 11px;

                line-height: 1.55;

                margin-top: 11px;
            }


            .performance-summary-grid {
                display: grid;

                grid-template-columns:
                    repeat(3, 1fr);

                gap: 10px;

                margin-top: 14px;
            }


            .performance-summary-item {
                background:
                    rgba(255, 255, 255, 0.025);

                border:
                    1px solid rgba(255, 255, 255, 0.055);

                border-radius: 11px;

                padding: 10px;
            }


            .performance-summary-label {
                color: #8497ab;

                font-size: 9px;

                font-weight: 700;

                text-transform: uppercase;
            }


            .performance-summary-value {
                color: #ffffff;

                font-size: 18px;

                font-weight: 900;

                margin-top: 5px;
            }


            @media screen and (max-width: 768px) {

                .performance-summary-grid {
                    grid-template-columns: 1fr;
                }

                .performance-block-top {
                    flex-direction: column;
                }
            }

        </style>
        """
    )


# =========================================================
# KPIS
# =========================================================

def renderizar_kpi(
    titulo,
    valor,
    positivo=False
):
    """
    Renderiza um KPI da performance.
    """
    titulo_seguro = html.escape(
        str(titulo)
    )

    valor_seguro = html.escape(
        str(valor)
    )

    classe_valor = (
        "performance-kpi-value performance-kpi-positive"
        if positivo
        else "performance-kpi-value"
    )

    st.html(
        (
            '<div class="performance-kpi">'

            '<div class="performance-kpi-label">'
            f"{titulo_seguro}"
            "</div>"

            f'<div class="{classe_valor}">'
            f"{valor_seguro}"
            "</div>"

            "</div>"
        )
    )


# =========================================================
# GRÁFICO
# =========================================================

def criar_grafico_roi():
    """
    Cria o gráfico de ROI por temporada
    integrado ao tema escuro.
    """
    temporadas = list(
        ROI_POR_TEMPORADA.keys()
    )

    valores = list(
        ROI_POR_TEMPORADA.values()
    )

    figura, eixo = plt.subplots(
        figsize=(8.5, 4.2),
        facecolor="#0a1727"
    )

    eixo.set_facecolor(
        "#0f1f33"
    )

    barras = eixo.bar(
        temporadas,
        valores,
        color="#53d99f",
        width=0.55
    )

    eixo.axhline(
        0,
        color="#62758a",
        linewidth=0.8
    )

    eixo.set_title(
        "ROI por temporada — Over 1.5 ≥ 70%",
        color="#ffffff",
        fontsize=13,
        fontweight="bold",
        pad=14
    )

    eixo.set_ylabel(
        "ROI (%)",
        color="#9fb1c3",
        fontsize=9
    )

    eixo.tick_params(
        axis="x",
        colors="#dce7f3"
    )

    eixo.tick_params(
        axis="y",
        colors="#90a2b6"
    )

    eixo.grid(
        axis="y",
        color="#31445a",
        alpha=0.45,
        linewidth=0.7
    )

    eixo.set_axisbelow(
        True
    )

    for spine in eixo.spines.values():
        spine.set_color(
            "#304258"
        )

    for barra, valor in zip(
        barras,
        valores
    ):
        eixo.text(
            barra.get_x()
            + barra.get_width() / 2,
            barra.get_height() + 0.35,
            f"{valor:.2f}%",
            ha="center",
            va="bottom",
            color="#dff8ed",
            fontsize=9,
            fontweight="bold"
        )

    figura.tight_layout()

    return figura


# =========================================================
# BLOCOS DE ESTRATÉGIA
# =========================================================

def renderizar_bloco_over15():
    """
    Renderiza a validação do Over 1.5.
    """
    st.html(
        """
        <div class="
            performance-block
            performance-block-valid
        ">

            <div class="performance-block-top">

                <div>

                    <div class="performance-block-label">
                        ESTRATÉGIA VALIDADA
                    </div>

                    <div class="performance-block-title">
                        Mais de 1,5 gols
                    </div>

                </div>

                <div class="
                    performance-badge
                    performance-badge-valid
                ">
                    ROBUSTA
                </div>

            </div>

            <div class="performance-block-text">
                O corte de probabilidade ≥ 70% apresentou
                resultado positivo nas três temporadas
                analisadas e foi classificado como robusto
                na validação multitemporada.
            </div>

            <div class="performance-summary-grid">

                <div class="performance-summary-item">
                    <div class="performance-summary-label">
                        Amostra
                    </div>
                    <div class="performance-summary-value">
                        201 apostas
                    </div>
                </div>

                <div class="performance-summary-item">
                    <div class="performance-summary-label">
                        Taxa de acerto
                    </div>
                    <div class="performance-summary-value">
                        76,62%
                    </div>
                </div>

                <div class="performance-summary-item">
                    <div class="performance-summary-label">
                        ROI consolidado
                    </div>
                    <div class="performance-summary-value">
                        +7,26%
                    </div>
                </div>

            </div>

        </div>
        """
    )


def renderizar_bloco_btts():
    """
    Renderiza o status do BTTS.
    """
    st.html(
        """
        <div class="
            performance-block
            performance-block-warning
        ">

            <div class="performance-block-top">

                <div>

                    <div class="performance-block-label">
                        MERCADO EXPERIMENTAL
                    </div>

                    <div class="performance-block-title">
                        Ambas marcam — BTTS
                    </div>

                </div>

                <div class="
                    performance-badge
                    performance-badge-warning
                ">
                    NÃO VALIDADO
                </div>

            </div>

            <div class="performance-block-text">
                Os testes multitemporada ainda não
                apresentaram robustez suficiente para
                utilizar BTTS como estratégia oficial
                da V1.
            </div>

        </div>
        """
    )


# =========================================================
# FUNÇÃO PRINCIPAL
# =========================================================

def renderizar_performance_view():
    """
    Renderiza a aba de validação histórica.
    """
    aplicar_estilos_performance()

    st.markdown(
        "## 📈 Validação histórica"
    )

    st.html(
        """
        <div class="performance-intro">
            Resultados consolidados do backtest
            do Brasileirão Série A entre 2022 e 2024.
        </div>
        """
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        renderizar_kpi(
            titulo="Apostas",
            valor=str(
                TOTAL_APOSTAS
            )
        )

    with col2:
        renderizar_kpi(
            titulo="Taxa de acerto",
            valor=f"{TAXA_ACERTO:.2f}%"
        )

    with col3:
        renderizar_kpi(
            titulo="ROI consolidado",
            valor=f"+{ROI_CONSOLIDADO:.2f}%",
            positivo=True
        )

    with col4:
        renderizar_kpi(
            titulo="Temporadas positivas",
            valor=TEMPORADAS_POSITIVAS,
            positivo=True
        )

    st.markdown(
        "### Evolução por temporada"
    )

    figura = criar_grafico_roi()

    with st.container(
        border=True
    ):
        st.pyplot(
            figura,
            use_container_width=True
        )

    plt.close(
        figura
    )

    renderizar_bloco_over15()

    renderizar_bloco_btts()