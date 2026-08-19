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
  recente, desempenho casa/fora, rating, força do adversário, tendências e
  identificação de valor (odds vs. probabilidade).
- **Autenticação e assinaturas** (`src/auth.py`, `src/subscription_service.py`,
  `src/mercado_pago_service.py`) — cadastro, login, planos e pagamentos via
  Mercado Pago.
- **Webhook de pagamento** (`src/webhook_api.py`) — recebe as confirmações de
  pagamento do Mercado Pago (roda como um serviço separado do dashboard).
- **Painel administrativo** (`src/admin_users.py`, `src/admin_plano.py`).

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

## Segurança

- O arquivo `.env` **nunca** deve ser commitado no Git — está protegido no
  `.gitignore`.
- Bancos de dados (`*.db`) e o modelo treinado (`*.pkl`) também não entram
  no controle de versão — são gerados/atualizados localmente.
- Se você suspeitar que alguma credencial vazou, rotacione (gere uma nova)
  imediatamente no painel de origem (API-Football ou Mercado Pago).

---

## Status do projeto

Em desenvolvimento ativo rumo à V1 comercial. Veja `docs/` para
documentação técnica adicional das engines de análise.
