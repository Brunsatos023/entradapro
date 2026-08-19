import streamlit as st


def aplicar_estilos():
    st.markdown(
        """
        <style>

        /* ==========================================================
           FOOTBALLAI — DESIGN SYSTEM V1
           ========================================================== */

        :root {
            --bg-main: #07111f;
            --bg-secondary: #0b1728;
            --bg-card: #0f1e31;
            --bg-card-soft: #12233a;

            --border: rgba(126, 158, 191, 0.20);
            --border-strong: rgba(126, 158, 191, 0.34);

            --text-primary: #f7fbff;
            --text-secondary: #aebed0;
            --text-muted: #7f91a8;

            --green: #53d99f;
            --green-light: #72e8b6;
            --green-dark: #1f9e72;

            --red: #ef7583;
            --yellow: #e7b94b;
            --blue: #4e9ff5;

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
                    #06101d 0%,
                    #091626 52%,
                    #07111f 100%
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
                    #071321 0%,
                    #091827 100%
                );

            border-right:
                1px solid rgba(126, 158, 191, 0.17);
        }


        [data-testid="stSidebar"] * {
            color: #eef5fc;
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
                    rgba(83, 217, 159, 0.08),
                    transparent 30%
                ),
                linear-gradient(
                    125deg,
                    rgba(18, 40, 64, 0.98),
                    rgba(9, 27, 46, 0.98)
                );

            border:
                1px solid rgba(99, 139, 180, 0.28);

            border-radius: 20px;

            padding: 22px 28px;

            margin-bottom: 16px;

            box-shadow:
                0 12px 35px rgba(0, 0, 0, 0.22);
        }


        .hero-title {
            color: #ffffff;

            font-size: 36px;

            font-weight: 850;

            letter-spacing: -0.8px;

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
                rgba(7, 20, 35, 0.70);

            border:
                1px solid rgba(126, 158, 191, 0.14);

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
                #9fb0c3 !important;

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
                rgba(126, 158, 191, 0.15);
        }


        .stTabs [aria-selected="true"] {
            background:
                linear-gradient(
                    135deg,
                    rgba(83, 217, 159, 0.15),
                    rgba(40, 126, 97, 0.09)
                ) !important;

            border:
                1px solid rgba(83, 217, 159, 0.30) !important;

            box-shadow:
                inset 0 0 0 1px
                rgba(83, 217, 159, 0.035);
        }


        .stTabs [aria-selected="true"] p {
            color:
                #74e7b7 !important;
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
                #aebdd0 !important;

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
                rgba(126, 158, 191, 0.18) !important;
        }


        /* ==========================================================
           BOTÕES
           ========================================================== */

        div.stButton > button {
            width: 100%;

            min-height: 42px;

            color:
                #061b14;

            background:
                linear-gradient(
                    135deg,
                    #46d596,
                    #2fba81
                );

            border:
                1px solid rgba(100, 232, 180, 0.40);

            border-radius:
                10px;

            font-weight:
                850;

            box-shadow:
                0 8px 20px
                rgba(35, 181, 124, 0.18);

            transition:
                all 0.18s ease;
        }


        div.stButton > button:hover {
            color:
                #041711;

            background:
                linear-gradient(
                    135deg,
                    #63e5ac,
                    #39c98e
                );

            border:
                1px solid rgba(118, 239, 192, 0.60);

            transform:
                translateY(-1px);

            box-shadow:
                0 10px 24px
                rgba(35, 181, 124, 0.25);
        }


        /* ==========================================================
           HEADER DA PARTIDA
           ========================================================== */

        .match-header {
            background:
                rgba(14, 31, 50, 0.90);

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
                #8496aa;

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
                    rgba(18, 35, 56, 0.88),
                    rgba(12, 27, 45, 0.88)
                );

            border:
                1px solid rgba(126, 158, 191, 0.17);

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
                #9dadbf !important;
        }


        .stApp [data-testid="stMetricLabel"] p {
            color:
                #9dadbf !important;

            font-size:
                11px !important;

            font-weight:
                700 !important;
        }


        .stApp [data-testid="stMetricValue"] {
            color:
                #f8fbff !important;
        }


        .stApp [data-testid="stMetricValue"] div {
            color:
                #f8fbff !important;

            font-weight:
                850;

            letter-spacing:
                -0.4px;
        }


        .stApp [data-testid="stMetricDelta"] {
            color:
                #70dfb1 !important;
        }


        /* ==========================================================
           CARDS GENÉRICOS
           ========================================================== */

        .metric-card {
            background:
                linear-gradient(
                    145deg,
                    rgba(17, 34, 55, 0.95),
                    rgba(11, 26, 44, 0.95)
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
                #91a2b7;

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
                    rgba(18, 39, 62, 0.97),
                    rgba(9, 24, 41, 0.97)
                );

            border:
                1px solid rgba(112, 151, 190, 0.25);

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
                    rgba(83, 217, 159, 0.09),
                    transparent 68%
                );

            pointer-events:
                none;
        }


        .premium-card:hover {
            transform:
                translateY(-2px);

            border-color:
                rgba(83, 217, 159, 0.40);

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
                rgba(83, 217, 159, 0.42);
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
                    rgba(27, 44, 64, 0.97),
                    rgba(13, 27, 44, 0.97)
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
                #91a5ba;

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
                #aebdca;

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
                rgba(83, 217, 159, 0.12);

            border:
                1px solid
                rgba(83, 217, 159, 0.30);

            color:
                #72e4b5;

            font-size:
                10px;

            font-weight:
                820;
        }


        .premium-badge-neutral {
            background:
                rgba(142, 164, 189, 0.10);

            border-color:
                rgba(142, 164, 189, 0.23);

            color:
                #b8c7d7;
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
                #b9c7d5;

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
                    #28b981,
                    #67e7b4
                );

            box-shadow:
                0 0 12px
                rgba(83, 217, 159, 0.22);
        }


        .premium-progress-fill-neutral {
            height:
                100%;

            border-radius:
                999px;

            background:
                linear-gradient(
                    90deg,
                    #71859b,
                    #aab8c8
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
                #91a5ba;

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
                #9eafc1;

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
                #91a5ba;

            font-size:
                10px;

            font-weight:
                700;
        }


        .premium-favorite-card {
            border-color:
                rgba(83, 217, 159, 0.48);
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
                #b7c7d4;

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
                #6de5b3;

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
                rgba(53, 182, 133, 0.55);

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
                rgba(5, 15, 25, 0.28);

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
                #aebdca;

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
                rgba(126, 158, 191, 0.17) !important;

            background:
                linear-gradient(
                    145deg,
                    rgba(12, 28, 46, 0.62),
                    rgba(8, 22, 38, 0.62)
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
                #eef6ff !important;

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
                #b8c8d9 !important;
        }


        /* ==========================================================
           TEXTO
           ========================================================== */

        .stApp
        [data-testid="stMarkdownContainer"] p,
        .stApp
        [data-testid="stMarkdownContainer"] li {
            color:
                #dce6f2;
        }


        .stApp
        [data-testid="stMarkdownContainer"] strong {
            color:
                #f8fbff;
        }


        .stApp
        [data-testid="stCaptionContainer"] {
            color:
                #91a4b8 !important;
        }


        .stApp
        [data-testid="stCaptionContainer"] p {
            color:
                #91a4b8 !important;

            font-size:
                11px;
        }


        /* ==========================================================
           EXPANDER
           ========================================================== */

        [data-testid="stExpander"] {
            border:
                1px solid
                rgba(126, 158, 191, 0.15) !important;

            border-radius:
                11px !important;

            background:
                rgba(9, 24, 41, 0.35);
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
                #74879d;

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
                rgba(126, 158, 191, 0.15);

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
                rgba(8, 22, 38, 0.38);

            border:
                1px solid
                rgba(126, 158, 191, 0.13);

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
                #07111f;
        }


        ::-webkit-scrollbar-thumb {
            background:
                #263b51;

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


        </style>
        """,
        unsafe_allow_html=True
    )