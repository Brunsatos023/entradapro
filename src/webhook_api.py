import hashlib
import hmac
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Garante que os outros arquivos de src/ (subscription_service.py,
# payment_plans.py, etc.) sejam encontrados independente de como
# este arquivo é iniciado (ex: "uvicorn src.webhook_api:app" a
# partir da raiz do projeto).
sys.path.insert(0, str(Path(__file__).resolve().parent))

import requests
from dotenv import load_dotenv
from fastapi import (
    FastAPI,
    HTTPException,
    Request
)

from subscription_service import processar_evento_mercado_pago


load_dotenv()


# ---------------------------------------------------------
# Logging: grava em arquivo, além do console, para que seja
# possível diagnosticar problemas depois (ex: um pagamento que
# não ativou o usuário) mesmo sem estar olhando o terminal no
# momento em que aconteceu.
# ---------------------------------------------------------
import logging  # noqa: E402

PASTA_LOGS = Path(__file__).resolve().parents[1] / "data" / "logs"
PASTA_LOGS.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(
            PASTA_LOGS / "webhook.log", encoding="utf-8"
        ),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("entradapro.webhook")


app = FastAPI(
    title="EntradaPro Webhook API",
    version="1.1.0"
)


RAIZ_PROJETO = (
    Path(__file__).resolve().parents[1]
)


CAMINHO_LOGS = (
    RAIZ_PROJETO
    / "data"
    / "webhook_events.jsonl"
)


CAMINHO_SECRETS_STREAMLIT = (
    RAIZ_PROJETO
    / ".streamlit"
    / "secrets.toml"
)


def garantir_pasta_logs():
    CAMINHO_LOGS.parent.mkdir(
        parents=True,
        exist_ok=True
    )


def salvar_evento(
    evento
):
    garantir_pasta_logs()

    with CAMINHO_LOGS.open(
        "a",
        encoding="utf-8"
    ) as arquivo:
        arquivo.write(
            json.dumps(
                evento,
                ensure_ascii=False
            )
        )

        arquivo.write(
            "\n"
        )


def obter_webhook_secret():
    return os.getenv(
        "MERCADO_PAGO_WEBHOOK_SECRET"
    )


def obter_access_token():
    token_env = os.getenv(
        "MERCADO_PAGO_ACCESS_TOKEN"
    )

    if token_env:
        return token_env

    if not CAMINHO_SECRETS_STREAMLIT.exists():
        return None

    try:
        import tomllib

        with CAMINHO_SECRETS_STREAMLIT.open(
            "rb"
        ) as arquivo:
            secrets = tomllib.load(
                arquivo
            )

        return secrets.get(
            "MERCADO_PAGO_ACCESS_TOKEN"
        )

    except Exception:
        return None


def extrair_assinatura(
    x_signature
):
    if not x_signature:
        return {
            "ts": None,
            "v1": None
        }

    ts = None
    v1 = None

    partes = x_signature.split(
        ","
    )

    for parte in partes:
        chave_valor = parte.split(
            "=",
            1
        )

        if len(
            chave_valor
        ) != 2:
            continue

        chave = (
            chave_valor[0]
            .strip()
            .lower()
        )

        valor = (
            chave_valor[1]
            .strip()
        )

        if chave == "ts":
            ts = valor

        elif chave == "v1":
            v1 = valor

    return {
        "ts": ts,
        "v1": v1
    }


def montar_manifesto(
    data_id,
    x_request_id,
    ts
):
    partes = []

    if data_id:
        partes.append(
            f"id:{data_id};"
        )

    if x_request_id:
        partes.append(
            f"request-id:{x_request_id};"
        )

    if ts:
        partes.append(
            f"ts:{ts};"
        )

    return "".join(
        partes
    )


def validar_assinatura_mercado_pago(
    x_signature,
    x_request_id,
    data_id
):
    secret = obter_webhook_secret()

    if not secret:
        return {
            "valida": False,
            "motivo": (
                "Webhook Secret não configurada."
            )
        }

    assinatura = extrair_assinatura(
        x_signature
    )

    ts = assinatura[
        "ts"
    ]

    v1_recebido = assinatura[
        "v1"
    ]

    if not ts:
        return {
            "valida": False,
            "motivo": (
                "Timestamp ausente "
                "em x-signature."
            )
        }

    if not v1_recebido:
        return {
            "valida": False,
            "motivo": (
                "Hash v1 ausente "
                "em x-signature."
            )
        }

    manifesto = montar_manifesto(
        data_id=data_id,
        x_request_id=x_request_id,
        ts=ts
    )

    if not manifesto:
        return {
            "valida": False,
            "motivo": (
                "Manifesto vazio."
            )
        }

    assinatura_calculada = (
        hmac.new(
            secret.encode(
                "utf-8"
            ),
            manifesto.encode(
                "utf-8"
            ),
            hashlib.sha256
        ).hexdigest()
    )

    valida = hmac.compare_digest(
        assinatura_calculada,
        v1_recebido
    )

    return {
        "valida": valida,
        "motivo": (
            None
            if valida
            else "Assinatura inválida."
        ),
        "ts": ts
    }


def consultar_recurso_mercado_pago(
    tipo,
    data_id
):
    access_token = obter_access_token()

    if not access_token:
        return {
            "sucesso": False,
            "mensagem": (
                "Access Token não encontrado."
            )
        }

    if not data_id:
        return {
            "sucesso": False,
            "mensagem": (
                "Data ID não informado."
            )
        }

    if tipo == "subscription_preapproval":
        url = (
            "https://api.mercadopago.com/"
            f"preapproval/{data_id}"
        )

    elif tipo == (
        "subscription_authorized_payment"
    ):
        url = (
            "https://api.mercadopago.com/"
            f"authorized_payments/{data_id}"
        )

    elif tipo == "payment":
        url = (
            "https://api.mercadopago.com/"
            f"v1/payments/{data_id}"
        )

    elif tipo == (
        "subscription_preapproval_plan"
    ):
        url = (
            "https://api.mercadopago.com/"
            f"preapproval_plan/{data_id}"
        )

    else:
        return {
            "sucesso": False,
            "ignorado": True,
            "mensagem": (
                f"Tipo '{tipo}' ainda não tratado."
            )
        }

    headers = {
        "Authorization": (
            f"Bearer {access_token}"
        ),
        "Content-Type": (
            "application/json"
        )
    }

    try:
        resposta = requests.get(
            url,
            headers=headers,
            timeout=20
        )

    except requests.RequestException as erro:
        return {
            "sucesso": False,
            "mensagem": (
                "Erro de comunicação com "
                f"o Mercado Pago: {erro}"
            )
        }

    if resposta.status_code != 200:
        return {
            "sucesso": False,
            "status_http": (
                resposta.status_code
            ),
            "mensagem": (
                "Mercado Pago respondeu "
                f"HTTP {resposta.status_code}."
            )
        }

    try:
        dados = resposta.json()

    except Exception:
        return {
            "sucesso": False,
            "mensagem": (
                "Resposta inválida "
                "do Mercado Pago."
            )
        }

    return {
        "sucesso": True,
        "dados": dados
    }


def resumir_recurso(
    tipo,
    dados
):
    if not isinstance(
        dados,
        dict
    ):
        return {}

    if tipo == "subscription_preapproval":
        auto_recurring = (
            dados.get(
                "auto_recurring"
            )
            or {}
        )

        return {
            "id": dados.get(
                "id"
            ),
            "status": dados.get(
                "status"
            ),
            "external_reference": (
                dados.get(
                    "external_reference"
                )
            ),
            "preapproval_plan_id": (
                dados.get(
                    "preapproval_plan_id"
                )
            ),
            "transaction_amount": (
                auto_recurring.get(
                    "transaction_amount"
                )
            ),
            "currency_id": (
                auto_recurring.get(
                    "currency_id"
                )
            ),
            "next_payment_date": (
                auto_recurring.get(
                    "next_payment_date"
                )
            )
        }

    if tipo == (
        "subscription_authorized_payment"
    ):
        pagamento = (
            dados.get(
                "payment"
            )
            or {}
        )

        return {
            "id": dados.get(
                "id"
            ),
            "status": dados.get(
                "status"
            ),
            "summarized": dados.get(
                "summarized"
            ),
            "preapproval_id": (
                dados.get(
                    "preapproval_id"
                )
            ),
            "external_reference": (
                dados.get(
                    "external_reference"
                )
            ),
            "transaction_amount": (
                dados.get(
                    "transaction_amount"
                )
            ),
            "currency_id": (
                dados.get(
                    "currency_id"
                )
            ),
            "payment_id": pagamento.get(
                "id"
            ),
            "payment_status": (
                pagamento.get(
                    "status"
                )
            )
        }

    if tipo == "payment":
        return {
            "id": dados.get(
                "id"
            ),
            "status": dados.get(
                "status"
            ),
            "status_detail": (
                dados.get(
                    "status_detail"
                )
            ),
            "external_reference": (
                dados.get(
                    "external_reference"
                )
            ),
            "transaction_amount": (
                dados.get(
                    "transaction_amount"
                )
            ),
            "currency_id": (
                dados.get(
                    "currency_id"
                )
            )
        }

    if tipo == (
        "subscription_preapproval_plan"
    ):
        auto_recurring = (
            dados.get(
                "auto_recurring"
            )
            or {}
        )

        return {
            "id": dados.get(
                "id"
            ),
            "status": dados.get(
                "status"
            ),
            "reason": dados.get(
                "reason"
            ),
            "transaction_amount": (
                auto_recurring.get(
                    "transaction_amount"
                )
            ),
            "currency_id": (
                auto_recurring.get(
                    "currency_id"
                )
            )
        }

    return {}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": (
            "EntradaPro Webhook API"
        )
    }


@app.get(
    "/webhook/mercado-pago"
)
def webhook_mercado_pago_status():
    return {
        "status": "online",
        "webhook": "mercado-pago",
        "method": "POST"
    }


@app.post(
    "/webhook/mercado-pago"
)
async def webhook_mercado_pago(
    request: Request
):
    try:
        corpo = await request.json()

    except Exception:
        corpo = {}

    query_params = dict(
        request.query_params
    )

    tipo = (
        corpo.get(
            "type"
        )
        or query_params.get(
            "type"
        )
    )

    acao = corpo.get(
        "action"
    )

    dados_corpo = corpo.get(
        "data"
    )

    if not isinstance(
        dados_corpo,
        dict
    ):
        dados_corpo = {}

    data_id = (
        query_params.get(
            "data.id"
        )
        or dados_corpo.get(
            "id"
        )
        or query_params.get(
            "id"
        )
    )

    if data_id is not None:
        data_id = str(
            data_id
        ).lower()

    x_request_id = (
        request.headers.get(
            "x-request-id"
        )
    )

    x_signature = (
        request.headers.get(
            "x-signature"
        )
    )

    resultado_validacao = (
        validar_assinatura_mercado_pago(
            x_signature=x_signature,
            x_request_id=x_request_id,
            data_id=data_id
        )
    )

    assinatura_valida = (
        resultado_validacao[
            "valida"
        ]
    )

    if not assinatura_valida:
        evento_invalido = {
            "recebido_em": (
                datetime.now().isoformat(
                    timespec="seconds"
                )
            ),
            "tipo": tipo,
            "acao": acao,
            "data_id": data_id,
            "assinatura_valida": False
        }

        salvar_evento(
            evento_invalido
        )

        logger.warning(
            "Webhook com assinatura INVALIDA rejeitado | "
            "tipo=%s data_id=%s motivo=%s",
            tipo, data_id,
            resultado_validacao.get("motivo", "desconhecido"),
        )

        raise HTTPException(
            status_code=401,
            detail=(
                resultado_validacao.get(
                    "motivo",
                    "Assinatura inválida."
                )
            )
        )

    resultado_consulta = (
        consultar_recurso_mercado_pago(
            tipo=tipo,
            data_id=data_id
        )
    )

    resumo_recurso = {}
    resultado_processamento = {"acao": "nao_processado"}

    if resultado_consulta.get(
        "sucesso"
    ):
        resumo_recurso = resumir_recurso(
            tipo=tipo,
            dados=(
                resultado_consulta[
                    "dados"
                ]
            )
        )

        try:
            resultado_processamento = processar_evento_mercado_pago(
                tipo=tipo,
                resumo=resumo_recurso,
            )
        except Exception as erro:
            # Nunca deixamos uma falha aqui derrubar a resposta ao
            # Mercado Pago (isso faria ele reenviar o webhook
            # repetidamente) - registramos o erro para investigar,
            # e respondemos normalmente.
            logger.exception(
                "Erro ao processar evento do webhook: %s", erro
            )
            resultado_processamento = {
                "acao": "erro",
                "motivo": str(erro),
            }

    evento = {
        "recebido_em": (
            datetime.now().isoformat(
                timespec="seconds"
            )
        ),
        "tipo": tipo,
        "acao": acao,
        "data_id": data_id,
        "live_mode": corpo.get(
            "live_mode"
        ),
        "user_id_mp": corpo.get(
            "user_id"
        ),
        "api_version": corpo.get(
            "api_version"
        ),
        "x_request_id": (
            x_request_id
        ),
        "x_signature_presente": bool(
            x_signature
        ),
        "assinatura_valida": True,
        "consulta_mp_sucesso": (
            resultado_consulta.get(
                "sucesso",
                False
            )
        ),
        "consulta_mp_status_http": (
            resultado_consulta.get(
                "status_http"
            )
        ),
        "consulta_mp_mensagem": (
            resultado_consulta.get(
                "mensagem"
            )
        ),
        "recurso": resumo_recurso,
        "processamento": resultado_processamento,
        "query_params": (
            query_params
        )
    }

    salvar_evento(
        evento
    )

    logger.info(
        "Webhook recebido | tipo=%s acao=%s data_id=%s "
        "status_recurso=%s external_reference=%s | "
        "processamento=%s",
        tipo,
        acao,
        data_id,
        resumo_recurso.get("status") if resumo_recurso else None,
        resumo_recurso.get("external_reference") if resumo_recurso else None,
        resultado_processamento.get("acao"),
    )

    return {
        "received": True,
        "status": "ok",
        "signature_valid": True,
        "resource_checked": (
            resultado_consulta.get(
                "sucesso",
                False
            )
        ),
        "processing_action": resultado_processamento.get("acao"),
    }