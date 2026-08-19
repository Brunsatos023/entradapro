import sqlite3
from pathlib import Path


CAMINHO_BANCO = (
    Path(__file__).resolve().parent
    / "data"
    / "entradapro_users.db"
)


def migrar_pagamentos():
    with sqlite3.connect(
        CAMINHO_BANCO
    ) as conexao:
        conexao.row_factory = sqlite3.Row

        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS assinaturas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                provedor TEXT NOT NULL DEFAULT 'MERCADO_PAGO',
                assinatura_externa_id TEXT,
                plano_codigo TEXT NOT NULL,
                periodicidade TEXT NOT NULL,
                valor REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDENTE',
                inicio_em DATETIME,
                proxima_cobranca_em DATETIME,
                cancelado_em DATETIME,
                criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
                atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (usuario_id)
                    REFERENCES usuarios(id)
            )
            """
        )

        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS pagamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                assinatura_id INTEGER,
                provedor TEXT NOT NULL DEFAULT 'MERCADO_PAGO',
                pagamento_externo_id TEXT,
                valor REAL NOT NULL,
                status TEXT NOT NULL,
                forma_pagamento TEXT,
                pago_em DATETIME,
                criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (usuario_id)
                    REFERENCES usuarios(id),

                FOREIGN KEY (assinatura_id)
                    REFERENCES assinaturas(id)
            )
            """
        )

        conexao.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_assinaturas_externa
            ON assinaturas(
                assinatura_externa_id
            )
            """
        )

        conexao.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_pagamentos_externo
            ON pagamentos(
                pagamento_externo_id
            )
            """
        )

        conexao.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_assinaturas_usuario
            ON assinaturas(
                usuario_id
            )
            """
        )

        conexao.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_pagamentos_usuario
            ON pagamentos(
                usuario_id
            )
            """
        )

        conexao.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_assinaturas_status
            ON assinaturas(
                status
            )
            """
        )

        conexao.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_pagamentos_status
            ON pagamentos(
                status
            )
            """
        )

        conexao.commit()

        print()
        print(
            "Estrutura de pagamentos criada com sucesso."
        )

        print()
        print(
            "Tabelas disponíveis:"
        )

        tabelas = conexao.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
            """
        ).fetchall()

        for tabela in tabelas:
            print(
                f"- {tabela['name']}"
            )

        print()
        print(
            "Migração de pagamentos concluída."
        )


if __name__ == "__main__":
    migrar_pagamentos()