import html

import streamlit.components.v1 as components


ALTURA_COMPONENTE = 690


def _limitar_percentual(valor) -> float:
    """
    Garante que o valor permaneça entre 0 e 100.
    """
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return 0.0

    return max(0.0, min(numero, 100.0))


def _formatar_texto(valor, padrao: str = "—") -> str:
    """
    Converte o valor para texto seguro para HTML.
    """
    if valor is None:
        return padrao

    texto = str(valor).strip()

    if not texto:
        return padrao

    return html.escape(texto)


def _formatar_odd(valor) -> str:
    """
    Formata uma odd decimal.
    """
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return "—"

    if numero <= 0:
        return "—"

    return f"{numero:.2f}"


def _formatar_percentual(
    valor,
    casas: int = 1,
    mostrar_sinal: bool = False
) -> str:
    """
    Formata valores percentuais.
    """
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        numero = 0.0

    sinal = ""

    if mostrar_sinal and numero > 0:
        sinal = "+"

    return f"{sinal}{numero:.{casas}f}%"


def _calcular_score_partida(
    resultado_match: dict
) -> float:
    """
    Calcula o score visual da partida pela média das notas
    de inteligência do mandante e do visitante.

    Não altera nenhum cálculo dos motores.
    Apenas resume os dois intelligence scores já existentes.
    """
    intelligence_casa = _limitar_percentual(
        resultado_match.get(
            "intelligence_casa",
            0
        )
    )

    intelligence_fora = _limitar_percentual(
        resultado_match.get(
            "intelligence_fora",
            0
        )
    )

    if intelligence_casa == 0 and intelligence_fora == 0:
        return 0.0

    return (
        intelligence_casa
        + intelligence_fora
    ) / 2


def _obter_confianca(
    resultado_match: dict
) -> tuple[str, str]:
    """
    Usa diretamente a confiança produzida pelo MatchEngine.
    """
    confianca = str(
        resultado_match.get(
            "confianca",
            "Baixa"
        )
    ).strip()

    confianca_normalizada = (
        confianca
        .lower()
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )

    if confianca_normalizada in {
        "muito alta",
        "alta"
    }:
        return confianca.upper(), "positive"

    if confianca_normalizada in {
        "media",
        "moderada"
    }:
        return confianca.upper(), "warning"

    return confianca.upper(), "negative"


def _obter_classificacao(
    resultado_value: dict
) -> tuple[str, str]:
    """
    Usa diretamente a classificação produzida pelo ValueEngine.
    """
    classificacao = str(
        resultado_value.get(
            "classificacao",
            "Sem valor"
        )
    ).strip()

    classificacao_normalizada = (
        classificacao
        .lower()
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )

    if classificacao_normalizada in {
        "excelente",
        "muito boa",
        "boa"
    }:
        return classificacao.upper(), "positive"

    if classificacao_normalizada == "marginal":
        return classificacao.upper(), "warning"

    return classificacao.upper(), "negative"


def renderizar_hero_card(
    nome_mandante: str,
    nome_visitante: str,
    favorito: str,
    resultado_match: dict,
    resultado_prediction: dict,
    melhor_mercado: str,
    resultado_value: dict
) -> None:
    """
    Renderiza o resumo executivo principal da partida.

    Chaves utilizadas:

    MatchEngine:
        intelligence_casa
        intelligence_fora
        confianca

    MatchPredictor:
        mais_15
        ambas_marcam

    ValueEngine:
        odd_casa
        odd_justa
        edge
        valor_esperado
        value_bet
        classificacao
    """
    score = _calcular_score_partida(
        resultado_match
    )

    intelligence_casa = _limitar_percentual(
        resultado_match.get(
            "intelligence_casa",
            0
        )
    )

    intelligence_fora = _limitar_percentual(
        resultado_match.get(
            "intelligence_fora",
            0
        )
    )

    probabilidade_over15 = _limitar_percentual(
        resultado_prediction.get(
            "mais_15",
            0
        )
    )

    probabilidade_btts = _limitar_percentual(
        resultado_prediction.get(
            "ambas_marcam",
            0
        )
    )

    odd_mercado = resultado_value.get(
        "odd_casa",
        0
    )

    odd_justa = resultado_value.get(
        "odd_justa",
        0
    )

    edge = resultado_value.get(
        "edge",
        0
    )

    valor_esperado = resultado_value.get(
        "valor_esperado",
        0
    )

    value_bet = bool(
        resultado_value.get(
            "value_bet",
            False
        )
    )

    confianca, classe_confianca = (
        _obter_confianca(
            resultado_match
        )
    )

    classificacao, classe_classificacao = (
        _obter_classificacao(
            resultado_value
        )
    )

    classe_value = (
        "value-positive"
        if value_bet
        else "value-negative"
    )

    titulo_partida = (
        f"{_formatar_texto(nome_mandante)}"
        " <span class='versus'>×</span> "
        f"{_formatar_texto(nome_visitante)}"
    )

    documento_html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <style>
        :root {{
            color-scheme: dark;
            --background: #0f172a;
            --surface: rgba(30, 41, 59, 0.72);
            --surface-strong: rgba(15, 23, 42, 0.88);
            --border: rgba(148, 163, 184, 0.18);
            --text: #f8fafc;
            --muted: #94a3b8;
            --green: #22c55e;
            --green-soft: rgba(34, 197, 94, 0.14);
            --yellow: #f59e0b;
            --yellow-soft: rgba(245, 158, 11, 0.14);
            --red: #ef4444;
            --red-soft: rgba(239, 68, 68, 0.14);
        }}

        * {{
            box-sizing: border-box;
        }}

        html,
        body {{
            margin: 0;
            padding: 0;
            background: transparent;
            color: var(--text);
            font-family:
                Inter,
                ui-sans-serif,
                system-ui,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
        }}

        .hero {{
            width: 100%;
            padding: 26px;
            border: 1px solid var(--border);
            border-radius: 22px;
            background:
                radial-gradient(
                    circle at top right,
                    rgba(34, 197, 94, 0.10),
                    transparent 34%
                ),
                linear-gradient(
                    135deg,
                    rgba(15, 23, 42, 0.98),
                    rgba(17, 24, 39, 0.97)
                );
            box-shadow:
                0 18px 46px rgba(0, 0, 0, 0.25);
        }}

        .match {{
            margin-bottom: 20px;
            text-align: center;
        }}

        .eyebrow {{
            margin-bottom: 7px;
            color: var(--muted);
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }}

        .match-title {{
            margin: 0;
            color: var(--text);
            font-size: clamp(25px, 4vw, 36px);
            font-weight: 900;
            line-height: 1.15;
        }}

        .versus {{
            color: #64748b;
            padding: 0 6px;
        }}

        .top-grid {{
            display: grid;
            grid-template-columns:
                minmax(0, 1.15fr)
                minmax(0, 1fr)
                minmax(0, 1fr);
            gap: 13px;
        }}

        .box {{
            min-height: 116px;
            padding: 17px;
            border: 1px solid var(--border);
            border-radius: 16px;
            background: var(--surface);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
        }}

        .label {{
            margin-bottom: 8px;
            color: var(--muted);
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }}

        .score {{
            font-size: 42px;
            font-weight: 950;
            line-height: 1;
        }}

        .score span {{
            margin-left: 2px;
            color: var(--muted);
            font-size: 15px;
            font-weight: 800;
        }}

        .main-value {{
            font-size: 20px;
            font-weight: 900;
            overflow-wrap: anywhere;
        }}

        .badge {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 34px;
            padding: 7px 13px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 950;
            letter-spacing: 0.05em;
        }}

        .positive {{
            color: #bbf7d0;
            border: 1px solid rgba(34, 197, 94, 0.38);
            background: var(--green-soft);
        }}

        .warning {{
            color: #fde68a;
            border: 1px solid rgba(245, 158, 11, 0.40);
            background: var(--yellow-soft);
        }}

        .negative {{
            color: #fecaca;
            border: 1px solid rgba(239, 68, 68, 0.38);
            background: var(--red-soft);
        }}

        .divider {{
            height: 1px;
            margin: 20px 0;
            background: var(--border);
        }}

        .section-title {{
            margin-bottom: 12px;
            color: #cbd5e1;
            font-size: 12px;
            font-weight: 900;
            letter-spacing: 0.11em;
            text-transform: uppercase;
        }}

        .market-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 13px;
        }}

        .market {{
            padding: 15px 17px;
            border: 1px solid var(--border);
            border-radius: 15px;
            background: rgba(255, 255, 255, 0.035);
        }}

        .market-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 10px;
        }}

        .market-name {{
            color: #e2e8f0;
            font-size: 14px;
            font-weight: 800;
        }}

        .market-value {{
            font-size: 18px;
            font-weight: 950;
        }}

        .track {{
            width: 100%;
            height: 8px;
            overflow: hidden;
            border-radius: 999px;
            background: rgba(148, 163, 184, 0.17);
        }}

        .fill {{
            height: 100%;
            border-radius: 999px;
            background:
                linear-gradient(
                    90deg,
                    #16a34a,
                    #4ade80
                );
        }}

        .intelligence {{
            display: flex;
            justify-content: space-between;
            gap: 12px;
            margin-top: 9px;
            color: var(--muted);
            font-size: 11px;
            font-weight: 750;
        }}

        .opportunity {{
            padding: 18px;
            border: 1px solid rgba(34, 197, 94, 0.24);
            border-radius: 17px;
            background: rgba(34, 197, 94, 0.06);
        }}

        .opportunity-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 13px;
            margin-bottom: 15px;
        }}

        .opportunity-title {{
            font-size: 18px;
            font-weight: 950;
        }}

        .opportunity-grid {{
            display: grid;
            grid-template-columns:
                minmax(0, 1.25fr)
                repeat(4, minmax(0, 0.8fr));
            gap: 10px;
        }}

        .opportunity-item {{
            min-height: 76px;
            padding: 12px;
            border: 1px solid rgba(148, 163, 184, 0.13);
            border-radius: 13px;
            background: var(--surface-strong);
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        .item-label {{
            margin-bottom: 5px;
            color: var(--muted);
            font-size: 10px;
            font-weight: 850;
            letter-spacing: 0.07em;
            text-transform: uppercase;
        }}

        .item-value {{
            font-size: 16px;
            font-weight: 900;
            line-height: 1.22;
            overflow-wrap: anywhere;
        }}

        .value-positive {{
            color: #86efac;
        }}

        .value-negative {{
            color: #fca5a5;
        }}

        @media (max-width: 850px) {{
            .top-grid {{
                grid-template-columns: 1fr;
            }}

            .opportunity-grid {{
                grid-template-columns: 1fr 1fr;
            }}
        }}

        @media (max-width: 560px) {{
            .hero {{
                padding: 19px 15px;
                border-radius: 17px;
            }}

            .market-grid,
            .opportunity-grid {{
                grid-template-columns: 1fr;
            }}

            .opportunity-header {{
                align-items: flex-start;
                flex-direction: column;
            }}
        }}
    </style>
</head>

<body>
    <section class="hero">
        <header class="match">
            <div class="eyebrow">
                Análise FootballAI
            </div>

            <h1 class="match-title">
                ⚽ {titulo_partida}
            </h1>
        </header>

        <div class="top-grid">
            <article class="box">
                <div class="label">
                    FootballAI Score
                </div>

                <div class="score">
                    {score:.0f}<span>/100</span>
                </div>
            </article>

            <article class="box">
                <div class="label">
                    Favorito
                </div>

                <div class="main-value">
                    {_formatar_texto(favorito)}
                </div>
            </article>

            <article class="box">
                <div class="label">
                    Confiança
                </div>

                <div class="badge {classe_confianca}">
                    {_formatar_texto(confianca)}
                </div>
            </article>
        </div>

        <div class="divider"></div>

        <div class="section-title">
            Probabilidades dos mercados
        </div>

        <div class="market-grid">
            <article class="market">
                <div class="market-header">
                    <div class="market-name">
                        Mais de 1,5 gols
                    </div>

                    <div class="market-value">
                        {probabilidade_over15:.1f}%
                    </div>
                </div>

                <div class="track">
                    <div
                        class="fill"
                        style="width:{probabilidade_over15:.1f}%"
                    ></div>
                </div>
            </article>

            <article class="market">
                <div class="market-header">
                    <div class="market-name">
                        Ambas marcam
                    </div>

                    <div class="market-value">
                        {probabilidade_btts:.1f}%
                    </div>
                </div>

                <div class="track">
                    <div
                        class="fill"
                        style="width:{probabilidade_btts:.1f}%"
                    ></div>
                </div>
            </article>
        </div>

        <div class="intelligence">
            <span>
                Inteligência mandante:
                {intelligence_casa:.1f}
            </span>

            <span>
                Inteligência visitante:
                {intelligence_fora:.1f}
            </span>
        </div>

        <div class="divider"></div>

        <section class="opportunity">
            <div class="opportunity-header">
                <div class="opportunity-title">
                    🎯 Melhor oportunidade
                </div>

                <div class="badge {classe_classificacao}">
                    {_formatar_texto(classificacao)}
                </div>
            </div>

            <div class="opportunity-grid">
                <article class="opportunity-item">
                    <div class="item-label">
                        Mercado
                    </div>

                    <div class="item-value">
                        {_formatar_texto(melhor_mercado)}
                    </div>
                </article>

                <article class="opportunity-item">
                    <div class="item-label">
                        Odd de mercado
                    </div>

                    <div class="item-value">
                        {_formatar_odd(odd_mercado)}
                    </div>
                </article>

                <article class="opportunity-item">
                    <div class="item-label">
                        Odd justa
                    </div>

                    <div class="item-value">
                        {_formatar_odd(odd_justa)}
                    </div>
                </article>

                <article class="opportunity-item">
                    <div class="item-label">
                        Edge
                    </div>

                    <div class="item-value">
                        {_formatar_percentual(
                            edge,
                            casas=1,
                            mostrar_sinal=True
                        )}
                    </div>
                </article>

                <article class="opportunity-item">
                    <div class="item-label">
                        Valor esperado
                    </div>

                    <div class="item-value {classe_value}">
                        {_formatar_percentual(
                            valor_esperado,
                            casas=1,
                            mostrar_sinal=True
                        )}
                    </div>
                </article>
            </div>
        </section>
    </section>
</body>
</html>
"""

    components.html(
        documento_html,
        height=ALTURA_COMPONENTE,
        scrolling=False
    )