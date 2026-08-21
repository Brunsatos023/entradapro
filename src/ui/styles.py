import streamlit as st


def aplicar_estilos():
    st.markdown(
        """
        <style>

        @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600&display=swap');

        /* ==========================================================
           ENTRADAPRO — DESIGN SYSTEM V2
           Paleta: gramado profundo + dourado (identidade de "Value"),
           em vez do azul-marinho + verde-menta genérico da V1.
           Tipografia: Oswald (títulos/placar, estilo transmissão
           esportiva) + Manrope (texto corrido) + JetBrains Mono
           (números/odds, sensação de dado analítico).
           ========================================================== */

        html, body, [class*="css"] {
            font-family: 'Manrope', -apple-system, sans-serif;
        }

        h1, h2, h3,
        .match-name,
        .match-label {
            font-family: 'Oswald', sans-serif !important;
            letter-spacing: 0.01em;
        }

        /* Números/odds/percentuais ganham fonte monoespaçada -
           reforça a leitura "dado analítico", diferencia do texto
           corrido e evita ambiguidade entre 1/l/I em números longos. */
        .metric-value,
        .metric-value-green,
        .premium-card-value,
        .premium-card-value-green,
        .premium-card-value-red,
        .premium-team-score,
        .value-item-number {
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 600 !important;
            letter-spacing: -0.01em;
        }

        /* Marca na barra lateral - selo com borda dourada,
           nome em duas cores, tagline espaçada estilo selo */
        .marca-lateral {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 4px;
        }

        .marca-lateral-selo {
            width: 40px;
            height: 40px;
            border-radius: 10px;
            background: var(--bg-card);
            border: 2px solid var(--green);
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Oswald', sans-serif;
            font-size: 15px;
            font-weight: 700;
            letter-spacing: -0.02em;
            color: var(--green);
            box-shadow: 0 0 0 3px rgba(217, 163, 83, 0.15);
            flex-shrink: 0;
        }

        .marca-lateral-nome {
            font-family: 'Oswald', sans-serif;
            color: #ffffff;
            font-size: 19px;
            font-weight: 700;
            letter-spacing: 0.01em;
            line-height: 1;
        }

        .marca-lateral-nome span {
            color: var(--green);
        }

        .marca-lateral-tagline {
            color: var(--green);
            font-size: 9px;
            letter-spacing: 0.16em;
            font-weight: 600;
            margin-top: 3px;
        }

        .marca-lateral-linha {
            height: 2px;
            background: linear-gradient(
                90deg, var(--green), transparent
            );
            margin: 12px 0 10px 0;
            border-radius: 2px;
        }

        /* Campos de login/cadastro arredondados (estilo "pill"),
           igual referencia visual aprovada */
        div[data-testid="stForm"] input[type="text"],
        div[data-testid="stForm"] input[type="password"] {
            border-radius: 24px !important;
            padding-left: 18px !important;
            height: 44px;
        }

        /* Botao "G" do login com Google - formato circular,
           escopado so a esses dois containers especificos para
           nao afetar nenhum outro botao do site. */
        .st-key-badge_google_login button,
        .st-key-badge_google_cadastro button {
            border-radius: 50% !important;
            width: 44px !important;
            height: 44px !important;
            padding: 0 !important;
            font-weight: 700;
            margin: 0 auto;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <style>

        /* ==========================================================
           FOOTBALLAI — DESIGN SYSTEM V1
           ========================================================== */

        :root {
            --bg-main: #091d14;
            --bg-secondary: #0e251a;
            --bg-card: #122e21;
            --bg-card-soft: #163627;

            --border: rgba(134, 183, 150, 0.20);
            --border-strong: rgba(134, 183, 150, 0.34);

            --text-primary: #fcfbfa;
            --text-secondary: #bcc8b6;
            --text-muted: #909f88;

            --green: #d9a353;
            --green-light: #e8b972;
            --green-dark: #9e6b1f;

            --red: #ef7583;
            --yellow: #e7c84b;
            --blue: #4eedf5;

            --radius-small: 10px;
            --radius-medium: 15px;
            --radius-large: 20px;
            --radius-xl: 24px;
        }


        /* ==========================================================
           APP
           ========================================================== */

        /* Remove o cabeçalho padrão do Streamlit */
        [data-testid="stHeader"] {
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
        }

        /* Remove a barra superior decorativa do Streamlit */
        [data-testid="stDecoration"] {
            display: none !important;
            height: 0 !important;
        }

        /* Garante que o conteúdo não reserve espaço para o header */
        header[data-testid="stHeader"] {
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
        }

        /* Ajusta o topo do conteúdo após esconder o header */
        .block-container {
            padding-top: 1rem !important;
        }

        .stApp {
            background:
                radial-gradient(
                    circle at 85% 0%,
                    rgba(42, 94, 129, 0.15),
                    transparent 27%
                ),
                linear-gradient(
                    145deg,
                    #081b12 0%,
                    #0c2318 52%,
                    #091d14 100%
                );

            color: var(--text-primary);
        }


        .block-container {
            max-width: 1380px;
            padding-top: 1.15rem;
            padding-bottom: 3rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }


        /* ==========================================================
           SIDEBAR
           ========================================================== */

        [data-testid="stSidebar"] {
            background:
                linear-gradient(
                    180deg,
                    #091f15 0%,
                    #0c2419 100%
                );

            border-right:
                1px solid rgba(134, 183, 150, 0.17);
        }


        [data-testid="stSidebar"] * {
            color: #f6f6f4;
        }


        [data-testid="stSidebar"] hr {
            border-color:
                rgba(255, 255, 255, 0.08);
        }


        /* ==========================================================
           HEADER PRINCIPAL
           ========================================================== */

        .hero {
            background:
                radial-gradient(
                    circle at 90% 20%,
                    rgba(217, 163, 83, 0.10),
                    transparent 30%
                ),
                linear-gradient(
                    125deg,
                    rgba(15, 36, 27, 0.98),
                    rgba(6, 16, 11, 0.98)
                );

            border:
                1px solid rgba(99, 180, 139, 0.28);

            border-radius: 18px;

            padding: 18px 24px;

            margin-bottom: 14px;

            box-shadow:
                0 10px 28px rgba(0, 0, 0, 0.22);
        }


        .hero-title {
            font-family: 'Oswald', sans-serif;

            color: #ffffff;

            font-size: 32px;

            font-weight: 700;

            letter-spacing: 0.01em;

            margin: 0;
        }


        .hero-highlight {
            color: var(--green);
        }


        .hero-subtitle {
            color: var(--text-secondary);

            font-size: 14px;

            margin-top: 6px;

            margin-bottom: 0;
        }


        .hero-indicador {
            display: inline-block;

            margin-top: 12px;

            padding: 5px 12px;

            font-size: 12px;

            font-weight: 600;

            color: var(--green);

            background: rgba(217, 163, 83, 0.12);

            border: 1px solid rgba(217, 163, 83, 0.30);

            border-radius: 999px;
        }


        /* ==========================================================
           NAVEGAÇÃO POR ABAS
           ========================================================== */

        .stTabs {
            margin-top: 8px;
        }


        .stTabs [data-baseweb="tab-list"] {
            gap: 6px;

            padding:
                6px;

            background:
                rgba(10, 32, 22, 0.70);

            border:
                1px solid rgba(134, 183, 150, 0.14);

            border-radius:
                14px;

            margin-bottom:
                18px;
        }


        .stTabs [data-baseweb="tab"] {
            min-height:
                43px;

            padding:
                0 17px;

            border-radius:
                9px;

            border:
                1px solid transparent;

            background:
                transparent;

            transition:
                all 0.18s ease;
        }


        .stTabs [data-baseweb="tab"] p {
            color:
                #aebba7 !important;

            font-size:
                13px;

            font-weight:
                750;

            white-space:
                nowrap;
        }


        .stTabs [data-baseweb="tab"]:hover {
            background:
                rgba(255, 255, 255, 0.035);

            border-color:
                rgba(134, 183, 150, 0.15);
        }


        .stTabs [aria-selected="true"] {
            background:
                linear-gradient(
                    135deg,
                    rgba(217, 163, 83, 0.15),
                    rgba(126, 92, 40, 0.09)
                ) !important;

            border:
                1px solid rgba(217, 163, 83, 0.30) !important;

            box-shadow:
                inset 0 0 0 1px
                rgba(217, 163, 83, 0.035);
        }


        .stTabs [aria-selected="true"] p {
            color:
                #e7b974 !important;
        }


        .stTabs [data-baseweb="tab-highlight"] {
            background:
                var(--green) !important;

            height:
                2px;
        }


        .stTabs [data-baseweb="tab-border"] {
            display:
                none;
        }


        /* ==========================================================
           SELEÇÃO DE PARTIDA
           ========================================================== */

        [data-testid="stSelectbox"] label,
        [data-testid="stNumberInput"] label {
            color:
                #bcc8b6 !important;

            font-size:
                11px !important;

            font-weight:
                750 !important;

            text-transform:
                uppercase;

            letter-spacing:
                0.45px;
        }


        [data-baseweb="select"] > div {
            border-radius:
                10px !important;

            border-color:
                rgba(134, 183, 150, 0.18) !important;
        }


        /* ==========================================================
           BOTÕES
           ========================================================== */

        div.stButton > button,
        div.stFormSubmitButton > button {
            width: 100%;

            min-height: 44px;

            color:
                #061b14;

            background:
                linear-gradient(
                    135deg,
                    #d59c46,
                    #ba822f
                );

            border:
                1px solid rgba(232, 179, 100, 0.40);

            border-radius:
                10px;

            font-weight:
                850;

            box-shadow:
                0 8px 20px
                rgba(181, 123, 35, 0.18);

            transition:
                all 0.18s ease;
        }


        div.stButton > button:hover,
        div.stFormSubmitButton > button:hover {
            color:
                #041711;

            background:
                linear-gradient(
                    135deg,
                    #e5b163,
                    #c98f39
                );

            border:
                1px solid rgba(239, 191, 118, 0.60);

            transform:
                translateY(-1px);

            box-shadow:
                0 10px 24px
                rgba(181, 123, 35, 0.25);
        }


        /* ==========================================================
           HEADER DA PARTIDA
           ========================================================== */

        .match-header {
            background:
                rgba(17, 47, 33, 0.90);

            border:
                1px solid var(--border);

            border-radius:
                16px;

            padding:
                16px 22px;

            margin-bottom:
                14px;

            text-align:
                center;
        }


        .match-label {
            color:
                #94a18d;

            font-size:
                11px;

            font-weight:
                750;

            letter-spacing:
                1.7px;

            text-transform:
                uppercase;
        }


        .match-name {
            color:
                #ffffff;

            font-size:
                27px;

            font-weight:
                850;

            margin-top:
                3px;
        }


        /* ==========================================================
           TÍTULOS
           ========================================================== */

        .section-title {
            color:
                #ffffff;

            font-size:
                20px;

            font-weight:
                820;

            margin-top:
                22px;

            margin-bottom:
                10px;

            letter-spacing:
                -0.2px;
        }


        .stApp h1 {
            font-size:
                31px;
        }


        .stApp h2 {
            font-size:
                23px;
        }


        .stApp h3 {
            font-size:
                18px;
        }


        .stApp h1,
        .stApp h2,
        .stApp h3,
        .stApp h4 {
            color:
                #ffffff;

            letter-spacing:
                -0.25px;
        }


        /* ==========================================================
           MÉTRICAS NATIVAS
           ========================================================== */

        .stApp [data-testid="stMetric"] {
            background:
                linear-gradient(
                    145deg,
                    rgba(21, 53, 38, 0.88),
                    rgba(15, 42, 29, 0.88)
                );

            border:
                1px solid rgba(134, 183, 150, 0.17);

            border-radius:
                13px;

            padding:
                13px 14px;

            min-height:
                94px;

            box-shadow:
                inset 0 1px 0
                rgba(255, 255, 255, 0.02);
        }


        .stApp [data-testid="stMetricLabel"] {
            color:
                #abb7a5 !important;
        }


        .stApp [data-testid="stMetricLabel"] p {
            color:
                #abb7a5 !important;

            font-size:
                11px !important;

            font-weight:
                700 !important;
        }


        .stApp [data-testid="stMetricValue"] {
            color:
                #fcfcfb !important;
        }


        .stApp [data-testid="stMetricValue"] div {
            color:
                #fcfcfb !important;

            font-weight:
                850;

            letter-spacing:
                -0.4px;
        }


        .stApp [data-testid="stMetricDelta"] {
            color:
                #dfb370 !important;
        }


        /* ==========================================================
           CARDS GENÉRICOS
           ========================================================== */

        .metric-card {
            background:
                linear-gradient(
                    145deg,
                    rgba(20, 52, 37, 0.95),
                    rgba(14, 41, 28, 0.95)
                );

            border:
                1px solid var(--border);

            border-radius:
                15px;

            padding:
                17px;

            min-height:
                110px;
        }


        .metric-label {
            color:
                #a1ae9a;

            font-size:
                12px;

            font-weight:
                650;
        }


        .metric-value {
            color:
                #ffffff;

            font-size:
                28px;

            font-weight:
                850;

            margin-top:
                8px;
        }


        .metric-value-green {
            color:
                var(--green);

            font-size:
                28px;

            font-weight:
                850;

            margin-top:
                8px;
        }


        /* ==========================================================
           PREMIUM CARD BASE
           ========================================================== */

        .premium-card {
            position:
                relative;

            overflow:
                hidden;

            background:
                linear-gradient(
                    145deg,
                    rgba(22, 58, 41, 0.97),
                    rgba(12, 38, 26, 0.97)
                );

            border:
                1px solid rgba(122, 180, 141, 0.25);

            border-radius:
                18px;

            padding:
                20px;

            min-height:
                140px;

            box-shadow:
                0 10px 28px
                rgba(0, 0, 0, 0.20),
                inset 0 1px 0
                rgba(255, 255, 255, 0.025);

            transition:
                transform 0.20s ease,
                border-color 0.20s ease,
                box-shadow 0.20s ease;
        }


        .premium-card::before {
            content:
                "";

            position:
                absolute;

            top:
                -75px;

            right:
                -75px;

            width:
                180px;

            height:
                180px;

            border-radius:
                50%;

            background:
                radial-gradient(
                    circle,
                    rgba(217, 163, 83, 0.09),
                    transparent 68%
                );

            pointer-events:
                none;
        }


        .premium-card:hover {
            transform:
                translateY(-2px);

            border-color:
                rgba(217, 163, 83, 0.40);

            box-shadow:
                0 14px 34px
                rgba(0, 0, 0, 0.27);
        }


        .premium-card-green {
            background:
                linear-gradient(
                    145deg,
                    rgba(15, 57, 46, 0.97),
                    rgba(7, 34, 29, 0.97)
                );

            border-color:
                rgba(217, 163, 83, 0.42);
        }


        .premium-card-red {
            background:
                linear-gradient(
                    145deg,
                    rgba(69, 28, 37, 0.97),
                    rgba(39, 17, 24, 0.97)
                );

            border-color:
                rgba(239, 117, 131, 0.42);
        }


        .premium-card-neutral {
            background:
                linear-gradient(
                    145deg,
                    rgba(30, 61, 47, 0.97),
                    rgba(16, 41, 29, 0.97)
                );
        }


        .premium-card-header {
            display:
                flex;

            align-items:
                center;

            justify-content:
                space-between;

            gap:
                12px;

            margin-bottom:
                14px;
        }


        .premium-card-label {
            color:
                #a2b19a;

            font-size:
                10px;

            font-weight:
                800;

            letter-spacing:
                1.2px;

            text-transform:
                uppercase;
        }


        .premium-card-title {
            color:
                #ffffff;

            font-size:
                23px;

            font-weight:
                850;

            line-height:
                1.15;

            margin:
                0;
        }


        .premium-card-value {
            color:
                #ffffff;

            font-size:
                35px;

            font-weight:
                900;

            line-height:
                1;

            margin-top:
                11px;

            letter-spacing:
                -0.8px;
        }


        .premium-card-value-green {
            color:
                var(--green);
        }


        .premium-card-value-red {
            color:
                var(--red);
        }


        .premium-card-subtitle {
            color:
                #b9c4b4;

            font-size:
                13px;

            line-height:
                1.45;

            margin-top:
                8px;
        }


        .premium-card-footer {
            display:
                flex;

            align-items:
                center;

            justify-content:
                space-between;

            gap:
                10px;

            margin-top:
                15px;

            padding-top:
                12px;

            border-top:
                1px solid
                rgba(255, 255, 255, 0.065);
        }


        /* ==========================================================
           BADGES
           ========================================================== */

        .premium-badge {
            display:
                inline-flex;

            align-items:
                center;

            justify-content:
                center;

            width:
                fit-content;

            border-radius:
                999px;

            padding:
                6px 11px;

            background:
                rgba(217, 163, 83, 0.12);

            border:
                1px solid
                rgba(217, 163, 83, 0.30);

            color:
                #e4b672;

            font-size:
                10px;

            font-weight:
                820;
        }


        .premium-badge-neutral {
            background:
                rgba(148, 183, 160, 0.10);

            border-color:
                rgba(148, 183, 160, 0.23);

            color:
                #c5d0bf;
        }


        .premium-badge-red {
            background:
                rgba(239, 117, 131, 0.11);

            border-color:
                rgba(239, 117, 131, 0.28);

            color:
                #f195a0;
        }


        /* ==========================================================
           DIVISOR
           ========================================================== */

        .premium-divider {
            width:
                100%;

            height:
                1px;

            background:
                linear-gradient(
                    90deg,
                    transparent,
                    rgba(255, 255, 255, 0.10),
                    transparent
                );

            margin:
                15px 0;
        }


        /* ==========================================================
           BARRAS PREMIUM
           ========================================================== */

        .premium-progress-wrapper {
            margin-top:
                13px;
        }


        .premium-progress-header {
            display:
                flex;

            align-items:
                center;

            justify-content:
                space-between;

            color:
                #c4cfbf;

            font-size:
                11px;

            font-weight:
                700;

            margin-bottom:
                6px;
        }


        .premium-progress-track {
            width:
                100%;

            height:
                7px;

            overflow:
                hidden;

            background:
                rgba(255, 255, 255, 0.07);

            border-radius:
                999px;
        }


        .premium-progress-fill {
            height:
                100%;

            border-radius:
                999px;

            background:
                linear-gradient(
                    90deg,
                    #b97f28,
                    #e7b467
                );

            box-shadow:
                0 0 12px
                rgba(217, 163, 83, 0.22);
        }


        .premium-progress-fill-neutral {
            height:
                100%;

            border-radius:
                999px;

            background:
                linear-gradient(
                    90deg,
                    #82927a,
                    #b6c1b1
                );
        }


        .premium-progress-fill-red {
            height:
                100%;

            border-radius:
                999px;

            background:
                linear-gradient(
                    90deg,
                    #cf4d5e,
                    #ef7583
                );
        }


        /* ==========================================================
           CARDS DAS EQUIPES
           ========================================================== */

        .premium-team-card,
        .premium-favorite-card {
            min-height:
                410px;

            text-align:
                center;
        }


        .premium-team-role,
        .premium-favorite-label {
            color:
                #a2b19a;

            font-size:
                10px;

            font-weight:
                800;

            letter-spacing:
                1.25px;

            text-transform:
                uppercase;

            text-align:
                center;
        }


        .premium-team-logo-wrapper {
            display:
                flex;

            align-items:
                center;

            justify-content:
                center;

            height:
                105px;

            margin-top:
                10px;

            margin-bottom:
                5px;
        }


        .premium-team-logo {
            display:
                block;

            object-fit:
                contain;

            max-height:
                94px;

            filter:
                drop-shadow(
                    0 7px 11px
                    rgba(0, 0, 0, 0.28)
                );

            transition:
                transform 0.20s ease;
        }


        .premium-card:hover
        .premium-team-logo {
            transform:
                scale(1.035);
        }


        .premium-team-logo-fallback {
            display:
                flex;

            align-items:
                center;

            justify-content:
                center;

            width:
                82px;

            height:
                82px;

            border-radius:
                50%;

            background:
                rgba(255, 255, 255, 0.05);

            border:
                1px solid
                rgba(255, 255, 255, 0.09);

            font-size:
                38px;
        }


        .premium-team-name,
        .premium-favorite-name {
            color:
                #ffffff;

            font-size:
                21px;

            font-weight:
                850;

            line-height:
                1.2;

            text-align:
                center;

            min-height:
                45px;

            display:
                flex;

            align-items:
                center;

            justify-content:
                center;
        }


        .premium-team-score {
            margin-top:
                9px;

            text-align:
                center;
        }


        .premium-team-score-label {
            color:
                #acb9a6;

            font-size:
                11px;

            font-weight:
                650;

            margin-top:
                5px;

            text-align:
                center;
        }


        .premium-card-footer-label {
            color:
                #a2b19a;

            font-size:
                10px;

            font-weight:
                700;
        }


        .premium-favorite-card {
            border-color:
                rgba(217, 163, 83, 0.48);
        }


        .premium-favorite-name {
            font-size:
                23px;

            margin-top:
                3px;
        }


        .premium-favorite-card
        .premium-badge {
            margin:
                12px auto 0;
        }


        .premium-favorite-message {
            color:
                #c3cdbe;

            font-size:
                12px;

            line-height:
                1.4;

            min-height:
                34px;

            margin-top:
                10px;

            text-align:
                center;
        }


        .premium-favorite-status {
            color:
                #e5b56d;

            font-size:
                10px;

            font-weight:
                800;
        }


        /* ==========================================================
           VALUE BET LEGADO
           ========================================================== */

        .value-positive {
            background:
                linear-gradient(
                    145deg,
                    rgba(16, 62, 47, 0.97),
                    rgba(8, 37, 31, 0.97)
                );

            border:
                1px solid
                rgba(182, 130, 53, 0.55);

            border-radius:
                18px;

            padding:
                21px;

            box-shadow:
                0 10px 28px
                rgba(0, 0, 0, 0.20);
        }


        .value-negative {
            background:
                linear-gradient(
                    145deg,
                    rgba(70, 28, 37, 0.97),
                    rgba(41, 19, 25, 0.97)
                );

            border:
                1px solid
                rgba(186, 89, 104, 0.55);

            border-radius:
                18px;

            padding:
                21px;
        }


        .value-market {
            color:
                #ffffff;

            font-size:
                24px;

            font-weight:
                850;
        }


        .value-status {
            color:
                #ffffff;

            font-size:
                13px;

            font-weight:
                700;

            margin-bottom:
                14px;
        }


        .value-grid {
            display:
                grid;

            grid-template-columns:
                repeat(
                    auto-fit,
                    minmax(130px, 1fr)
                );

            gap:
                10px;
        }


        .value-item {
            background:
                rgba(7, 23, 16, 0.28);

            border:
                1px solid
                rgba(255, 255, 255, 0.075);

            border-radius:
                11px;

            padding:
                11px;
        }


        .value-item-label {
            color:
                #b9c4b4;

            font-size:
                10px;
        }


        .value-item-number {
            color:
                #ffffff;

            font-size:
                18px;

            font-weight:
                820;

            margin-top:
                3px;
        }


        /* ==========================================================
           CONTAINERS DO STREAMLIT
           ========================================================== */

        .stApp
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-color:
                rgba(134, 183, 150, 0.17) !important;

            background:
                linear-gradient(
                    145deg,
                    rgba(15, 43, 30, 0.62),
                    rgba(11, 35, 24, 0.62)
                );

            border-radius:
                15px !important;

            box-shadow:
                inset 0 1px 0
                rgba(255, 255, 255, 0.015);
        }


        /* ==========================================================
           ALERTAS
           ========================================================== */

        .stApp [data-testid="stAlert"] {
            border-radius:
                11px;
        }


        .stApp [data-testid="stAlert"] p {
            color:
                #f8f7f5 !important;

            font-weight:
                650;

            font-size:
                12px;
        }


        /* ==========================================================
           PROGRESS BAR NATIVA
           ========================================================== */

        .stApp [data-testid="stProgress"] > div > div {
            border-radius:
                999px;
        }


        .stApp [data-testid="stProgress"] p {
            color:
                #c5d2bf !important;
        }


        /* ==========================================================
           TEXTO
           ========================================================== */

        .stApp
        [data-testid="stMarkdownContainer"] p,
        .stApp
        [data-testid="stMarkdownContainer"] li {
            color:
                #e9e8e5;
        }


        .stApp
        [data-testid="stMarkdownContainer"] strong {
            color:
                #fcfcfb;
        }


        .stApp
        [data-testid="stCaptionContainer"] {
            color:
                #a1af9a !important;
        }


        .stApp
        [data-testid="stCaptionContainer"] p {
            color:
                #a1af9a !important;

            font-size:
                11px;
        }


        /* ==========================================================
           EXPANDER
           ========================================================== */

        [data-testid="stExpander"] {
            border:
                1px solid
                rgba(134, 183, 150, 0.15) !important;

            border-radius:
                11px !important;

            background:
                rgba(12, 38, 26, 0.35);
        }


        [data-testid="stExpander"] summary {
            font-weight:
                700;
        }


        /* ==========================================================
           DIVISORES
           ========================================================== */

        .stApp hr {
            border-color:
                rgba(255, 255, 255, 0.075);
        }


        /* ==========================================================
           FOOTER
           ========================================================== */

        .footer-warning {
            color:
                #85947d;

            text-align:
                center;

            font-size:
                10px;

            margin-top:
                30px;

            padding-top:
                12px;

            border-top:
                1px solid
                rgba(255, 255, 255, 0.055);
        }


        /* ==========================================================
           TABELAS / DATAFRAMES
           ========================================================== */

        [data-testid="stDataFrame"] {
            border:
                1px solid
                rgba(134, 183, 150, 0.15);

            border-radius:
                12px;

            overflow:
                hidden;
        }


        /* ==========================================================
           GRÁFICOS
           ========================================================== */

        [data-testid="stImage"] img {
            border-radius:
                12px;
        }


        [data-testid="stVegaLiteChart"],
        [data-testid="stPlotlyChart"] {
            background:
                rgba(11, 35, 24, 0.38);

            border:
                1px solid
                rgba(134, 183, 150, 0.13);

            border-radius:
                14px;

            padding:
                8px;
        }


        /* ==========================================================
           SCROLLBAR
           ========================================================== */

        ::-webkit-scrollbar {
            width:
                8px;

            height:
                8px;
        }


        ::-webkit-scrollbar-track {
            background:
                #091d14;
        }


        ::-webkit-scrollbar-thumb {
            background:
                #2a4d3d;

            border-radius:
                999px;
        }


        ::-webkit-scrollbar-thumb:hover {
            background:
                #38536d;
        }


        /* ==========================================================
           RESPONSIVIDADE
           ========================================================== */

        @media screen and (max-width: 1000px) {

            .block-container {
                padding-left:
                    1.3rem;

                padding-right:
                    1.3rem;
            }


            .premium-team-card,
            .premium-favorite-card {
                min-height:
                    auto;
            }


            .stTabs [data-baseweb="tab"] {
                padding:
                    0 11px;
            }


            .stTabs [data-baseweb="tab"] p {
                font-size:
                    11px;
            }
        }


        @media screen and (max-width: 768px) {

            .block-container {
                padding-left:
                    0.9rem;

                padding-right:
                    0.9rem;

                padding-top:
                    0.8rem;
            }


            .hero {
                padding:
                    18px;
            }


            .hero-title {
                font-size:
                    28px;
            }


            .hero-subtitle {
                font-size:
                    12px;
            }


            .match-name {
                font-size:
                    22px;
            }


            .section-title {
                font-size:
                    18px;
            }


            .premium-card {
                padding:
                    17px;

                min-height:
                    auto;
            }


            .premium-card-title {
                font-size:
                    20px;
            }


            .premium-card-value {
                font-size:
                    30px;
            }


            .premium-team-card,
            .premium-favorite-card {
                min-height:
                    auto;
            }


            .premium-team-logo-wrapper {
                height:
                    90px;
            }


            .premium-team-logo {
                max-height:
                    80px;
            }


            .stTabs [data-baseweb="tab-list"] {
                overflow-x:
                    auto;

                justify-content:
                    flex-start;

                flex-wrap:
                    nowrap;
            }


            .stTabs [data-baseweb="tab"] {
                min-width:
                    max-content;

                padding:
                    0 10px;
            }
        }


        /* Telas bem pequenas (iPhone SE, celulares mais estreitos) */
        @media screen and (max-width: 420px) {

            .block-container {
                padding-left:
                    0.6rem;

                padding-right:
                    0.6rem;
            }


            .hero {
                padding:
                    14px;
            }


            .hero-title {
                font-size:
                    24px;
            }


            .hero-subtitle {
                font-size:
                    11px;
            }


            .hero-indicador {
                font-size:
                    10px;

                padding:
                    4px 9px;
            }


            .match-name {
                font-size:
                    18px;
            }


            .section-title {
                font-size:
                    16px;
            }


            div.stButton > button {
                font-size:
                    13px;
            }


            .metric-value,
            .metric-value-green,
            .premium-card-value,
            .premium-card-value-green,
            .premium-card-value-red {
                font-size:
                    22px !important;
            }
        }


        </style>
        """,
        unsafe_allow_html=True
    )