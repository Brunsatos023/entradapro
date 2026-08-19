import hashlib
import hmac
import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import (
    FastAPI,
    HTTPException,
    Request
)


load_dotenv()


app = FastAPI(
    title="EntradaPro Webhook API",
    version="1.0.0"
)


CAMINHO_LOGS = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "webhook_events.jsonl"
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
        data_id=(
            data_id
        ),
        x_request_id=(
            x_request_id
        ),
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

    valida = (
        hmac.compare_digest(
            assinatura_calculada,
            v1_recebido
        )
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

    dados = corpo.get(
        "data"
    )

    if not isinstance(
        dados,
        dict
    ):
        dados = {}

    data_id = (
        query_params.get(
            "data.id"
        )
        or dados.get(
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
            x_signature=(
                x_signature
            ),
            x_request_id=(
                x_request_id
            ),
            data_id=(
                data_id
            )
        )
    )

    assinatura_valida = (
        resultado_validacao[
            "valida"
        ]
    )

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
        "assinatura_valida": (
            assinatura_valida
        ),
        "query_params": (
            query_params
        )
    }

    salvar_evento(
        evento
    )

    print()
    print(
        "===== WEBHOOK MERCADO PAGO ====="
    )

    print(
        f"Tipo: {tipo}"
    )

    print(
        f"Ação: {acao}"
    )

    print(
        f"Data ID: {data_id}"
    )

    print(
        "Assinatura presente: "
        f"{bool(x_signature)}"
    )

    print(
        "Assinatura válida: "
        f"{assinatura_valida}"
    )

    print(
        "================================"
    )

    print()

    if not assinatura_valida:
        raise HTTPException(
            status_code=401,
            detail=(
                resultado_validacao.get(
                    "motivo",
                    (
                        "Assinatura do webhook "
                        "inválida."
                    )
                )
            )
        )

    return {
        "received": True,
        "status": "ok"
    }