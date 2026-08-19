from datetime import datetime

from payment_plans import (
    obter_plano
)

from db import conectar_banco


def normalizar_status(
    status
):
    return str(
        status
        or ""
    ).strip().upper()


def registrar_assinatura_pendente(
    usuario_id,
    codigo_plano
):
    plano = obter_plano(
        codigo_plano
    )

    if not plano:
        return {
            "sucesso": False,
            "mensagem": (
                "Plano não encontrado."
            )
        }

    periodicidade = plano[
        "periodicidade"
    ]

    valor = float(
        plano[
            "valor"
        ]
    )

    with conectar_banco() as conexao:
        assinatura_existente = (
            conexao.execute(
                """
                SELECT
                    id,
                    usuario_id,
                    plano_codigo,
                    periodicidade,
                    valor,
                    status
                FROM assinaturas
                WHERE usuario_id = ?
                  AND status IN (
                      'PENDENTE',
                      'ATIVA'
                  )
                ORDER BY id DESC
                LIMIT 1
                """,
                (
                    usuario_id,
                )
            ).fetchone()
        )

        if assinatura_existente:
            return {
                "sucesso": True,
                "assinatura_id": (
                    assinatura_existente[
                        "id"
                    ]
                ),
                "ja_existia": True
            }

        cursor = conexao.execute(
            """
            INSERT INTO assinaturas (
                usuario_id,
                provedor,
                plano_codigo,
                periodicidade,
                valor,
                status,
                criado_em,
                atualizado_em
            )
            VALUES (
                ?,
                'MERCADO_PAGO',
                ?,
                ?,
                ?,
                'PENDENTE',
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
            """,
            (
                usuario_id,
                codigo_plano,
                periodicidade,
                valor
            )
        )

        conexao.commit()

        assinatura_id = (
            cursor.lastrowid
        )

    return {
        "sucesso": True,
        "assinatura_id": (
            assinatura_id
        ),
        "ja_existia": False
    }


def buscar_assinatura_por_id(
    assinatura_id
):
    with conectar_banco() as conexao:
        assinatura = conexao.execute(
            """
            SELECT
                id,
                usuario_id,
                provedor,
                assinatura_externa_id,
                plano_codigo,
                periodicidade,
                valor,
                status,
                inicio_em,
                proxima_cobranca_em,
                cancelado_em,
                criado_em,
                atualizado_em
            FROM assinaturas
            WHERE id = ?
            """,
            (
                assinatura_id,
            )
        ).fetchone()

    if not assinatura:
        return None

    return dict(
        assinatura
    )


def buscar_assinatura_mais_recente_usuario(
    usuario_id
):
    with conectar_banco() as conexao:
        assinatura = conexao.execute(
            """
            SELECT
                id,
                usuario_id,
                provedor,
                assinatura_externa_id,
                plano_codigo,
                periodicidade,
                valor,
                status,
                inicio_em,
                proxima_cobranca_em,
                cancelado_em,
                criado_em,
                atualizado_em
            FROM assinaturas
            WHERE usuario_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                usuario_id,
            )
        ).fetchone()

    if not assinatura:
        return None

    return dict(
        assinatura
    )


def vincular_assinatura_externa(
    assinatura_id,
    assinatura_externa_id
):
    assinatura_externa_id = str(
        assinatura_externa_id
        or ""
    ).strip()

    if not assinatura_externa_id:
        return {
            "sucesso": False,
            "mensagem": (
                "ID externo da assinatura "
                "não informado."
            )
        }

    with conectar_banco() as conexao:
        cursor = conexao.execute(
            """
            UPDATE assinaturas
            SET
                assinatura_externa_id = ?,
                atualizado_em = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                assinatura_externa_id,
                assinatura_id
            )
        )

        conexao.commit()

    if cursor.rowcount == 0:
        return {
            "sucesso": False,
            "mensagem": (
                "Assinatura não encontrada."
            )
        }

    return {
        "sucesso": True
    }


def atualizar_status_assinatura(
    assinatura_id,
    status,
    inicio_em=None,
    proxima_cobranca_em=None,
    cancelado_em=None
):
    status_normalizado = (
        normalizar_status(
            status
        )
    )

    if not status_normalizado:
        return {
            "sucesso": False,
            "mensagem": (
                "Status inválido."
            )
        }

    with conectar_banco() as conexao:
        cursor = conexao.execute(
            """
            UPDATE assinaturas
            SET
                status = ?,
                inicio_em = COALESCE(
                    ?,
                    inicio_em
                ),
                proxima_cobranca_em = COALESCE(
                    ?,
                    proxima_cobranca_em
                ),
                cancelado_em = COALESCE(
                    ?,
                    cancelado_em
                ),
                atualizado_em = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                status_normalizado,
                inicio_em,
                proxima_cobranca_em,
                cancelado_em,
                assinatura_id
            )
        )

        conexao.commit()

    if cursor.rowcount == 0:
        return {
            "sucesso": False,
            "mensagem": (
                "Assinatura não encontrada."
            )
        }

    return {
        "sucesso": True
    }


def ativar_usuario_pro(
    usuario_id
):
    with conectar_banco() as conexao:
        cursor = conexao.execute(
            """
            UPDATE usuarios
            SET plano = 'PRO'
            WHERE id = ?
            """,
            (
                usuario_id,
            )
        )

        conexao.commit()

    if cursor.rowcount == 0:
        return {
            "sucesso": False,
            "mensagem": (
                "Usuário não encontrado."
            )
        }

    return {
        "sucesso": True
    }


def rebaixar_usuario_free(
    usuario_id
):
    with conectar_banco() as conexao:
        cursor = conexao.execute(
            """
            UPDATE usuarios
            SET plano = 'FREE'
            WHERE id = ?
            """,
            (
                usuario_id,
            )
        )

        conexao.commit()

    if cursor.rowcount == 0:
        return {
            "sucesso": False,
            "mensagem": (
                "Usuário não encontrado."
            )
        }

    return {
        "sucesso": True
    }


def registrar_pagamento(
    usuario_id,
    assinatura_id,
    pagamento_externo_id,
    valor,
    status,
    forma_pagamento=None,
    pago_em=None
):
    pagamento_externo_id = str(
        pagamento_externo_id
        or ""
    ).strip()

    if not pagamento_externo_id:
        return {
            "sucesso": False,
            "mensagem": (
                "ID externo do pagamento "
                "não informado."
            )
        }

    status_normalizado = (
        normalizar_status(
            status
        )
    )

    try:
        valor_float = float(
            valor
        )

    except (
        TypeError,
        ValueError
    ):
        return {
            "sucesso": False,
            "mensagem": (
                "Valor do pagamento inválido."
            )
        }

    with conectar_banco() as conexao:
        existente = conexao.execute(
            """
            SELECT id
            FROM pagamentos
            WHERE pagamento_externo_id = ?
            """,
            (
                pagamento_externo_id,
            )
        ).fetchone()

        if existente:
            conexao.execute(
                """
                UPDATE pagamentos
                SET
                    status = ?,
                    forma_pagamento = COALESCE(
                        ?,
                        forma_pagamento
                    ),
                    pago_em = COALESCE(
                        ?,
                        pago_em
                    )
                WHERE pagamento_externo_id = ?
                """,
                (
                    status_normalizado,
                    forma_pagamento,
                    pago_em,
                    pagamento_externo_id
                )
            )

            conexao.commit()

            return {
                "sucesso": True,
                "pagamento_id": (
                    existente[
                        "id"
                    ]
                ),
                "ja_existia": True
            }

        cursor = conexao.execute(
            """
            INSERT INTO pagamentos (
                usuario_id,
                assinatura_id,
                provedor,
                pagamento_externo_id,
                valor,
                status,
                forma_pagamento,
                pago_em,
                criado_em
            )
            VALUES (
                ?,
                ?,
                'MERCADO_PAGO',
                ?,
                ?,
                ?,
                ?,
                ?,
                CURRENT_TIMESTAMP
            )
            """,
            (
                usuario_id,
                assinatura_id,
                pagamento_externo_id,
                valor_float,
                status_normalizado,
                forma_pagamento,
                pago_em
            )
        )

        conexao.commit()

        pagamento_id = (
            cursor.lastrowid
        )

    return {
        "sucesso": True,
        "pagamento_id": (
            pagamento_id
        ),
        "ja_existia": False
    }


def buscar_assinatura_por_externa_id(
    assinatura_externa_id
):
    assinatura_externa_id = str(assinatura_externa_id or "").strip()

    if not assinatura_externa_id:
        return None

    with conectar_banco() as conexao:
        assinatura = conexao.execute(
            """
            SELECT
                id,
                usuario_id,
                provedor,
                assinatura_externa_id,
                plano_codigo,
                periodicidade,
                valor,
                status,
                inicio_em,
                proxima_cobranca_em,
                cancelado_em,
                criado_em,
                atualizado_em
            FROM assinaturas
            WHERE assinatura_externa_id = ?
            """,
            (assinatura_externa_id,)
        ).fetchone()

    if not assinatura:
        return None

    return dict(assinatura)


def _localizar_assinatura_do_evento(external_reference, mp_id):
    """
    Encontra a assinatura interna correspondente a um evento do
    Mercado Pago. Tenta primeiro pelo external_reference (que
    guardamos como o nosso próprio id da assinatura no momento do
    checkout); se não achar, tenta pelo id externo já vinculado
    (útil para eventos seguintes, como renovação e cancelamento,
    onde o external_reference pode não vir preenchido de novo).
    """
    if external_reference:
        try:
            assinatura_id = int(external_reference)
        except (TypeError, ValueError):
            assinatura_id = None

        if assinatura_id is not None:
            assinatura = buscar_assinatura_por_id(assinatura_id)
            if assinatura:
                return assinatura

    if mp_id:
        return buscar_assinatura_por_externa_id(mp_id)

    return None


def processar_evento_mercado_pago(tipo, resumo):
    """
    Ponto único que decide o que fazer com um evento do webhook já
    validado (assinatura HMAC conferida) e já consultado na API do
    Mercado Pago (resumo = o dicionário devolvido por
    resumir_recurso() em webhook_api.py).

    Retorna um dicionário descrevendo a ação tomada, para fins de
    log/diagnóstico. Nunca levanta exceção por conta própria - erros
    de dados inesperados resultam em "ignorado".
    """
    if not isinstance(resumo, dict) or not resumo:
        return {"acao": "ignorado", "motivo": "recurso vazio"}

    if tipo == "subscription_preapproval":
        return _processar_evento_preapproval(resumo)

    if tipo == "subscription_authorized_payment":
        return _processar_evento_pagamento_recorrente(resumo)

    if tipo == "payment":
        return _processar_evento_pagamento_avulso(resumo)

    return {"acao": "ignorado", "motivo": f"tipo '{tipo}' não requer ação"}


def _processar_evento_preapproval(resumo):
    mp_id = resumo.get("id")
    status_mp = normalizar_status(resumo.get("status"))
    external_reference = resumo.get("external_reference")

    assinatura = _localizar_assinatura_do_evento(external_reference, mp_id)

    if not assinatura:
        return {
            "acao": "ignorado",
            "motivo": (
                "assinatura interna não encontrada "
                f"(external_reference={external_reference}, mp_id={mp_id})"
            ),
        }

    if mp_id and not assinatura.get("assinatura_externa_id"):
        vincular_assinatura_externa(
            assinatura_id=assinatura["id"],
            assinatura_externa_id=mp_id,
        )

    if status_mp == "AUTHORIZED":
        resultado = processar_assinatura_ativa(
            assinatura_id=assinatura["id"],
            proxima_cobranca_em=resumo.get("next_payment_date"),
        )
        return {"acao": "assinatura_ativada", "resultado": resultado}

    if status_mp in ("CANCELLED", "PAUSED"):
        resultado = processar_assinatura_cancelada(
            assinatura_id=assinatura["id"]
        )
        return {"acao": "assinatura_cancelada", "resultado": resultado}

    return {
        "acao": "sem_efeito",
        "motivo": f"status '{status_mp}' não exige mudança",
    }


def _processar_evento_pagamento_recorrente(resumo):
    preapproval_id = resumo.get("preapproval_id")
    payment_id = resumo.get("payment_id")
    payment_status = normalizar_status(resumo.get("payment_status"))
    valor = resumo.get("transaction_amount")

    assinatura = buscar_assinatura_por_externa_id(preapproval_id)

    if not assinatura:
        return {
            "acao": "ignorado",
            "motivo": (
                "assinatura não encontrada para "
                f"preapproval_id={preapproval_id}"
            ),
        }

    if payment_id:
        registrar_pagamento(
            usuario_id=assinatura["usuario_id"],
            assinatura_id=assinatura["id"],
            pagamento_externo_id=payment_id,
            valor=valor or assinatura["valor"],
            status=payment_status,
        )

    if payment_status == "APPROVED":
        resultado = processar_assinatura_ativa(assinatura_id=assinatura["id"])
        return {"acao": "renovacao_aprovada", "resultado": resultado}

    if payment_status in ("REJECTED", "CANCELLED"):
        return {"acao": "renovacao_recusada", "assinatura_id": assinatura["id"]}

    return {"acao": "pagamento_registrado", "status": payment_status}


def _processar_evento_pagamento_avulso(resumo):
    payment_id = resumo.get("id")
    status_pagamento = normalizar_status(resumo.get("status"))
    external_reference = resumo.get("external_reference")
    valor = resumo.get("transaction_amount")

    assinatura = _localizar_assinatura_do_evento(external_reference, None)

    if not assinatura:
        return {
            "acao": "ignorado",
            "motivo": (
                "assinatura não encontrada para "
                f"external_reference={external_reference}"
            ),
        }

    if payment_id:
        registrar_pagamento(
            usuario_id=assinatura["usuario_id"],
            assinatura_id=assinatura["id"],
            pagamento_externo_id=payment_id,
            valor=valor or assinatura["valor"],
            status=status_pagamento,
        )

    if status_pagamento == "APPROVED":
        resultado = processar_assinatura_ativa(assinatura_id=assinatura["id"])
        return {"acao": "assinatura_ativada", "resultado": resultado}

    if status_pagamento in ("REJECTED", "CANCELLED"):
        return {"acao": "pagamento_recusado", "assinatura_id": assinatura["id"]}

    return {"acao": "pagamento_registrado", "status": status_pagamento}


def processar_assinatura_ativa(
    assinatura_id,
    inicio_em=None,
    proxima_cobranca_em=None
):
    assinatura = buscar_assinatura_por_id(
        assinatura_id
    )

    if not assinatura:
        return {
            "sucesso": False,
            "mensagem": (
                "Assinatura não encontrada."
            )
        }

    resultado_status = (
        atualizar_status_assinatura(
            assinatura_id=(
                assinatura_id
            ),
            status="ATIVA",
            inicio_em=inicio_em,
            proxima_cobranca_em=(
                proxima_cobranca_em
            )
        )
    )

    if not resultado_status[
        "sucesso"
    ]:
        return resultado_status

    resultado_usuario = (
        ativar_usuario_pro(
            assinatura[
                "usuario_id"
            ]
        )
    )

    if not resultado_usuario[
        "sucesso"
    ]:
        return resultado_usuario

    return {
        "sucesso": True
    }


def processar_assinatura_cancelada(
    assinatura_id
):
    assinatura = buscar_assinatura_por_id(
        assinatura_id
    )

    if not assinatura:
        return {
            "sucesso": False,
            "mensagem": (
                "Assinatura não encontrada."
            )
        }

    agora = datetime.now().isoformat(
        timespec="seconds"
    )

    resultado_status = (
        atualizar_status_assinatura(
            assinatura_id=(
                assinatura_id
            ),
            status="CANCELADA",
            cancelado_em=agora
        )
    )

    if not resultado_status[
        "sucesso"
    ]:
        return resultado_status

    # Sem isto, o usuário continuaria PRO para sempre mesmo depois
    # de cancelar - o cancelamento precisa necessariamente rebaixar
    # o acesso, não só marcar a assinatura como cancelada.
    resultado_usuario = (
        rebaixar_usuario_free(
            assinatura[
                "usuario_id"
            ]
        )
    )

    if not resultado_usuario[
        "sucesso"
    ]:
        return resultado_usuario

    return {
        "sucesso": True
    }


def expirar_assinaturas_vencidas():
    """
    Rede de segurança: procura assinaturas marcadas como ATIVA cuja
    data de próxima cobrança já passou, e rebaixa esses usuários
    para FREE automaticamente.

    Isto cobre o caso de um webhook de cancelamento/falha de
    pagamento do Mercado Pago não ter chegado (rede instável,
    servidor fora do ar no momento, etc.) - sem isto, um usuário
    que parou de pagar continuaria PRO para sempre.

    Segura de chamar com frequência (ex: toda vez que o dashboard
    carrega) - só age sobre assinaturas realmente vencidas.
    """
    agora = datetime.now().isoformat(timespec="seconds")

    with conectar_banco() as conexao:
        vencidas = conexao.execute(
            """
            SELECT id, usuario_id
            FROM assinaturas
            WHERE status = 'ATIVA'
              AND proxima_cobranca_em IS NOT NULL
              AND proxima_cobranca_em < ?
            """,
            (agora,)
        ).fetchall()

    quantidade_expirada = 0

    for assinatura in vencidas:
        resultado = atualizar_status_assinatura(
            assinatura_id=assinatura["id"],
            status="EXPIRADA",
        )
        if resultado["sucesso"]:
            rebaixar_usuario_free(assinatura["usuario_id"])
            quantidade_expirada += 1

    return {
        "sucesso": True,
        "expiradas": quantidade_expirada,
    }