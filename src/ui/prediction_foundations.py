import html

import streamlit as st


# =========================================================
# UTILITÁRIOS
# =========================================================

def normalizar_texto(valor):
    """
    Normaliza valores para comparação.
    """
    return (
        str(valor)
        .strip()
        .upper()
    )


def lista_segura(valor):
    """
    Garante que os motivos sejam tratados como lista.
    """
    if valor is None:
        return []

    if isinstance(valor, list):
        return valor

    if isinstance(valor, tuple):
        return list(valor)

    return [valor]


# =========================================================
# ESTILOS
# =========================================================

def aplicar_estilos_fundamentos():
    """
    Aplica os estilos dos fundamentos da previsão.
    """
    st.html(
        """
        <style>

            .foundation-intro {
                color: #8fa2b7;
                font-size: 11px;
                line-height: 1.55;
                margin-bottom: 14px;
            }


            .foundation-card {
                background:
                    linear-gradient(
                        145deg,
                        rgba(16, 34, 55, 0.98),
                        rgba(9, 24, 41, 0.98)
                    );

                border:
                    1px solid rgba(93, 129, 166, 0.24);

                border-radius: 15px;

                padding: 18px;

                min-height: 210px;
            }


            .foundation-card-valid {
                border-color:
                    rgba(83, 217, 159, 0.34);

                background:
                    linear-gradient(
                        145deg,
                        rgba(13, 48, 42, 0.96),
                        rgba(8, 30, 28, 0.96)
                    );
            }


            .foundation-card-experimental {
                border-color:
                    rgba(231, 185, 75, 0.26);

                background:
                    linear-gradient(
                        145deg,
                        rgba(42, 42, 31, 0.96),
                        rgba(26, 29, 24, 0.96)
                    );
            }


            .foundation-top {
                display: flex;
                align-items: flex-start;
                justify-content: space-between;
                gap: 12px;
            }


            .foundation-label {
                color: #8297ad;
                font-size: 9px;
                font-weight: 800;
                letter-spacing: 0.8px;
                text-transform: uppercase;
            }


            .foundation-title {
                color: #ffffff;
                font-size: 18px;
                font-weight: 850;
                margin-top: 4px;
            }


            .foundation-badge {
                border-radius: 999px;
                padding: 5px 9px;

                font-size: 9px;
                font-weight: 850;

                white-space: nowrap;
            }


            .foundation-badge-valid {
                color: #72e5b5;

                background:
                    rgba(83, 217, 159, 0.11);

                border:
                    1px solid rgba(83, 217, 159, 0.27);
            }


            .foundation-badge-warning {
                color: #efd16f;

                background:
                    rgba(231, 185, 75, 0.10);

                border:
                    1px solid rgba(231, 185, 75, 0.24);
            }


            .foundation-divider {
                height: 1px;

                background:
                    rgba(255, 255, 255, 0.07);

                margin: 14px 0;
            }


            .foundation-reason {
                display: flex;
                align-items: flex-start;
                gap: 8px;

                color: #c7d5e4;

                font-size: 11px;
                line-height: 1.45;

                margin-bottom: 9px;
            }


            .foundation-reason-icon {
                color: #58dda9;
                font-weight: 900;
                flex-shrink: 0;
            }


            .foundation-reason-icon-warning {
                color: #e4c55e;
            }


            .foundation-empty {
                color: #8294a7;
                font-size: 11px;
                font-style: italic;
            }


            .foundation-note {
                margin-top: 14px;

                padding: 11px 13px;

                border-radius: 10px;

                background:
                    rgba(14, 37, 61, 0.72);

                border:
                    1px solid rgba(93, 129, 166, 0.16);

                color: #9fb1c3;

                font-size: 10px;

                line-height: 1.5;
            }


            @media screen and (max-width: 768px) {

                .foundation-card {
                    min-height: auto;
                }

                .foundation-top {
                    flex-direction: column;
                }
            }

        </style>
        """
    )


# =========================================================
# CARD
# =========================================================

def criar_html_motivos(
    motivos,
    experimental=False
):
    """
    Cria a lista visual dos motivos.
    """
    motivos = lista_segura(
        motivos
    )

    if not motivos:
        return (
            '<div class="foundation-empty">'
            "Nenhum fundamento adicional foi informado."
            "</div>"
        )

    partes = []

    classe_icone = (
        "foundation-reason-icon-warning"
        if experimental
        else "foundation-reason-icon"
    )

    for motivo in motivos:
        motivo_seguro = html.escape(
            str(motivo)
        )

        partes.append(
            (
                '<div class="foundation-reason">'

                f'<span class="{classe_icone}">'
                "•"
                "</span>"

                "<span>"
                f"{motivo_seguro}"
                "</span>"

                "</div>"
            )
        )

    return "".join(
        partes
    )


def renderizar_card_fundamento(
    titulo,
    etiqueta,
    status,
    motivos,
    experimental=False
):
    """
    Renderiza um card individual de fundamentos.
    """
    titulo_seguro = html.escape(
        str(titulo)
    )

    etiqueta_segura = html.escape(
        str(etiqueta)
    )

    status_seguro = html.escape(
        str(status)
    )

    if experimental:
        classe_card = (
            "foundation-card "
            "foundation-card-experimental"
        )

        classe_badge = (
            "foundation-badge "
            "foundation-badge-warning"
        )

    else:
        classe_card = (
            "foundation-card "
            "foundation-card-valid"
        )

        classe_badge = (
            "foundation-badge "
            "foundation-badge-valid"
        )

    motivos_html = criar_html_motivos(
        motivos=motivos,
        experimental=experimental
    )

    conteudo_html = (
        f'<div class="{classe_card}">'

        '<div class="foundation-top">'

        "<div>"

        '<div class="foundation-label">'
        f"{etiqueta_segura}"
        "</div>"

        '<div class="foundation-title">'
        f"{titulo_seguro}"
        "</div>"

        "</div>"

        f'<div class="{classe_badge}">'
        f"{status_seguro}"
        "</div>"

        "</div>"

        '<div class="foundation-divider"></div>'

        f"{motivos_html}"

        "</div>"
    )

    st.html(
        conteudo_html
    )


# =========================================================
# FUNÇÃO PRINCIPAL
# =========================================================

def renderizar_fundamentos_previsao(
    resultado_prediction
):
    """
    Renderiza os fundamentos dos mercados analisados.
    """
    aplicar_estilos_fundamentos()

    motivos_over15 = resultado_prediction.get(
        "motivos_mais_15",
        []
    )

    motivos_btts = resultado_prediction.get(
        "motivos_btts",
        []
    )

    status_over15 = resultado_prediction.get(
        "status_estrategico_over15",
        "NÃO AVALIADO"
    )

    status_btts = resultado_prediction.get(
        "status_estrategico_btts",
        "NÃO VALIDADO"
    )

    with st.expander(
        "📊 Entenda os fundamentos da previsão"
    ):
        st.html(
            """
            <div class="foundation-intro">
                Estes fundamentos mostram os principais
                fatores estatísticos utilizados na leitura
                dos mercados analisados.
            </div>
            """
        )

        col1, col2 = st.columns(2)

        with col1:
            renderizar_card_fundamento(
                titulo="Mais de 1,5 gols",
                etiqueta="MERCADO VALIDADO NA V1",
                status=status_over15,
                motivos=motivos_over15,
                experimental=False
            )

        with col2:
            renderizar_card_fundamento(
                titulo="Ambas marcam",
                etiqueta="MERCADO EXPERIMENTAL",
                status=status_btts,
                motivos=motivos_btts,
                experimental=True
            )

        st.html(
            """
            <div class="foundation-note">
                O percentual calculado para um mercado
                não significa, isoladamente, que exista
                uma oportunidade de aposta. A recomendação
                depende também dos critérios estratégicos
                validados pelo sistema.
            </div>
            """
        )