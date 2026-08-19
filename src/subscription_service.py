import sqlite3
from datetime import datetime
from pathlib import Path

from payment_plans import (
    obter_plano
)


CAMINHO_BANCO = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "entradapro_users.db"
)


def conectar_banco():
    conexao = sqlite3.connect(
        CAMINHO_BANCO
    )

    conexao.row_factory = sqlite3.Row

    return conexao


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

    return {
        "sucesso": True
    }