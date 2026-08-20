# EntradaPro ⚽

Plataforma de inteligência e análise de partidas de futebol — estatísticas,
probabilidades e identificação de oportunidades de valor (Value Betting).

> ⚠️ **MINISTÉRIO DA FAZENDA ADVERTE: APOSTA NÃO É INVESTIMENTO.**
> O EntradaPro é uma ferramenta de análise e estatística. Não garante
> resultados e não deve ser tratado como recomendação financeira.

---

## O que este projeto contém

- **Dashboard principal** (`src/dashboard.py`) — a aplicação Streamlit que o
  usuário final acessa: análise de partidas, comparação de times,
  probabilidades, indicadores de valor, planos FREE/PRO.
- **Engines de análise** (`src/engines/`) — os motores que calculam forma
  recente, desempenho casa/fora, rating, força do adversário, tendências,
  identificação de valor (odds vs. probabilidade), jogos futuros reais,
  odds automáticas, varredura de oportunidades e escanteios.
- **Autenticação e assinaturas** (`src/auth.py`, `src/subscription_service.py`,
  `src/mercado_pago_service.py`) — cadastro, login (com proteção contra
  força bruta), planos e pagamentos via Mercado Pago.
- **Webhook de pagamento** (`src/webhook_api.py`) — recebe as confirmações de
  pagamento do Mercado Pago (roda como um serviço separado do dashboard).
- **Painel administrativo** (`src/admin_users.py`, `src/admin_plano.py`).
- **"EntradaPro Autônomo"** — o sistema busca jogos futuros sozinho, escolhe
  as melhores oportunidades do dia, guarda o histórico de cada previsão,
  confere com o resultado real (Green/Red), ajusta seus próprios critérios
  com base no desempenho, e alerta sobre sequências ruins recentes. Ver
  `src/engines/fixtures_engine.py`, `opportunity_scanner.py`,
  `src/prediction_history_service.py`, `src/auto_tuning_service.py` e
  `src/risk_management_service.py`.
- **Vitrine multi-campeonatos** (`src/ui/vitrine_campeonatos.py`) — Champions
  League, Premier League, La Liga e outras, com placar ao vivo (exclusivo
  PRO; sem análise completa do EntradaPro, que hoje só cobre o Brasileirão).
- **Backup automático** (`scripts/backup_banco.py` +
  `.github/workflows/backup_diario.yml`) — roda todo dia sozinho via GitHub
  Actions, exportando os dados principais (sem senhas).

---

## Páginas do site (multipage do Streamlit)

| Página | Arquivo | O que é |
|---|---|---|
| Dashboard | `src/dashboard.py` | Análise principal, jogos futuros, melhores entradas, vitrine |
| Performance Analytics | `src/pages/1_Performance_Analytics.py` | Estatísticas de performance das engines |
| Assinatura PRO | `src/pages/2_Assinatura_PRO.py` | Escolha de plano e checkout Mercado Pago |
| Administração | `src/pages/3_Administracao.py` | Painel de admin (login próprio, exige permissão) |
| Resultados | `src/pages/4_Resultados.py` | Histórico transparente de previsões e ROI real |

---

## Pré-requisitos

- **Python 3.11 ou mais recente** (o projeto foi desenvolvido com Python 3.13)
- Uma chave de API da [API-Football](https://dashboard.api-football.com)
- Uma conta [Mercado Pago Developers](https://www.mercadopago.com.br/developers)
  com credenciais de teste (para pagamentos)

---

## Instalação (ambiente local)

**1. Crie um ambiente virtual** (recomendado, evita conflito com outros projetos Python):

```bash
python -m venv .venv
```

Ative o ambiente:
- Windows: `.venv\Scripts\activate`
- Mac/Linux: `source .venv/bin/activate`

**2. Instale as dependências:**

```bash
pip install -r requirements.txt
```

**3. Configure as variáveis de ambiente:**

Copie o arquivo modelo e preencha com suas credenciais reais:

```bash
cp .env.example .env
```

Abra o `.env` e preencha cada valor (chave da API-Football, credenciais do
Mercado Pago). **Nunca compartilhe ou envie este arquivo para o Git** — ele
já está protegido no `.gitignore`.

---

## Como executar

### Dashboard principal (aplicação que o usuário acessa)

```bash
streamlit run src/dashboard.py
```

Isso abre automaticamente no navegador em `http://localhost:8501`.

### Servidor de webhook do Mercado Pago (processo separado)

O webhook precisa rodar como um serviço à parte (não é uma página do
Streamlit — é quem recebe a confirmação de pagamento do Mercado Pago):

```bash
uvicorn src.webhook_api:app --host 0.0.0.0 --port 8000
```

> Em produção, essa URL precisa ser pública e configurada no painel do
> Mercado Pago (Suas integrações → Webhooks). Trataremos disso na etapa de
> deploy.

---

## Estrutura de pastas

```
FootballAI/
├── src/                    # Código-fonte da aplicação
│   ├── dashboard.py        # Dashboard principal (oficial)
│   ├── auth.py              # Cadastro, login, sessão
│   ├── access_control.py    # Controle de acesso FREE/PRO
│   ├── admin_users.py       # Painel administrativo de usuários
│   ├── webhook_api.py       # Recebe confirmações do Mercado Pago
│   ├── mercado_pago_service.py
│   ├── subscription_service.py
│   ├── engines/              # Motores de análise (forma, rating, value, etc.)
│   ├── ui/                   # Componentes visuais do dashboard
│   └── pages/                 # Páginas extras do Streamlit (multipage)
├── data/
│   ├── raw/                  # Dados brutos (JSON de partidas)
│   ├── processed/             # Dados tratados (CSV, relatórios)
│   └── entradapro_users.db    # Banco de dados de usuários (SQLite)
├── models/                    # Modelo treinado (.pkl)
├── assets/                    # Logo e imagens da marca
├── scripts/                   # Utilitários (criação de planos, migrações, testes manuais)
├── tests/                      # Testes automatizados
├── docs/                        # Documentação técnica
├── _arquivo_backups/            # Versões antigas guardadas (fora do Git)
├── requirements.txt
├── .env.example                  # Modelo de variáveis de ambiente (sem segredos)
└── .gitignore
```

---

## Testes automatizados

```bash
pip install pytest
pytest tests/
```

---

## Banco de dados: local (SQLite) vs. produção (PostgreSQL)

Por padrão, o projeto usa SQLite (`data/entradapro_users.db`) — funciona
sozinho, sem configuração extra, ideal para rodar na sua máquina.

Para usar PostgreSQL (recomendado em produção), defina a variável de
ambiente `DATABASE_URL` no `.env` com a connection string do seu banco
(ex: do [Neon](https://neon.tech)):

```
DATABASE_URL=postgresql://usuario:senha@endereco/banco
```

Com essa variável definida, o projeto passa a usar PostgreSQL
automaticamente — nenhum outro arquivo precisa mudar.

**Para levar os dados que já existem no SQLite local para o PostgreSQL:**

```bash
python scripts/migrar_para_postgres.py "postgresql://usuario:senha@endereco/banco"
```

Esse script não apaga nem altera o banco local — é seguro rodar mais de
uma vez (não duplica registros já migrados).

---

## Segurança

- O arquivo `.env` **nunca** deve ser commitado no Git — está protegido no
  `.gitignore`.
- Bancos de dados (`*.db`) e o modelo treinado (`*.pkl`) também não entram
  no controle de versão — são gerados/atualizados localmente.
- Se você suspeitar que alguma credencial vazou, rotacione (gere uma nova)
  imediatamente no painel de origem (API-Football ou Mercado Pago).
- Login protegido contra força bruta: 5 tentativas erradas seguidas
  bloqueiam a conta por 15 minutos.
- Backup diário automático (ver `.github/workflows/backup_diario.yml`) —
  rede de segurança independente do provedor de banco de dados.

---

## Transparência das análises

O EntradaPro guarda toda previsão que faz e confere com o resultado real
(página "Resultados"). O histórico é sempre honesto, incluindo períodos
negativos — análise estatística não é garantia de resultado, e isso fica
visível em todos os pontos onde uma recomendação aparece na tela.

---

## Status do projeto

Publicado em produção em `entradapro.com.br`, hospedado no Render
(dashboard + webhook) com banco PostgreSQL (Neon). Veja `docs/` para
documentação técnica adicional e `docs/ROADMAP_V2.md` para os próximos
passos planejados (mais campeonatos com análise completa, reformulação
de layout, etc.).
