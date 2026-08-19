"""
Migra os dados do banco local (SQLite) para um banco PostgreSQL de
produção (ex: Neon).

QUANDO USAR:
Depois que você já tiver a "connection string" do PostgreSQL (o
texto que começa com postgresql://...) e quiser levar os usuários,
assinaturas e pagamentos que já existem no seu banco local para lá.

COMO USAR:

    python scripts/migrar_para_postgres.py "postgresql://usuario:senha@endereco/banco"

(troque o texto entre aspas pela sua connection string real)

O QUE ELE FAZ:
1. Cria as tabelas no PostgreSQL (se ainda não existirem).
2. Copia todos os usuários, códigos de recuperação de senha,
   assinaturas e pagamentos do seu banco local para lá.
3. NÃO apaga nem modifica nada no seu banco local — é seguro rodar
   mais de uma vez (registros já existentes no destino são
   ignorados, não duplicados).

⚠️ Precisa de conexão com a internet e do pacote psycopg2-binary
instalado (já está no requirements.txt).
"""

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def migrar(url_postgres):
    import os
    import sqlite3

    # Aponta temporariamente o módulo de banco para o Postgres de
    # destino, só para criar as tabelas lá (reaproveita a mesma
    # lógica usada pelo app em produção).
    os.environ["DATABASE_URL"] = url_postgres

    import db  # noqa: E402 - importado aqui de propósito, depois do DATABASE_URL

    print("Conectando ao PostgreSQL de destino...")
    db.inicializar_banco()
    print("Tabelas conferidas/criadas no PostgreSQL.\n")

    caminho_sqlite = (
        Path(__file__).resolve().parents[1] / "data" / "entradapro_users.db"
    )

    if not caminho_sqlite.exists():
        print(f"Banco local não encontrado em: {caminho_sqlite}")
        print("Nada para migrar.")
        return

    origem = sqlite3.connect(caminho_sqlite)
    origem.row_factory = sqlite3.Row

    destino = db.conectar_banco()

    # A ordem importa: usuarios primeiro (assinaturas/pagamentos
    # dependem do id do usuário já existir).
    total_usuarios = _migrar_tabela(
        origem, destino,
        tabela="usuarios",
        colunas=[
            "id", "nome", "usuario", "email", "senha_hash",
            "senha_salt", "plano", "ativo", "criado_em",
        ],
        chave_conflito="email",
    )
    print(f"Usuários migrados: {total_usuarios}")

    total_recuperacao = _migrar_tabela(
        origem, destino,
        tabela="recuperacao_senha",
        colunas=[
            "id", "usuario_id", "token_hash", "expira_em",
            "usado", "criado_em",
        ],
        chave_conflito=None,
    )
    print(f"Códigos de recuperação migrados: {total_recuperacao}")

    total_assinaturas = _migrar_tabela(
        origem, destino,
        tabela="assinaturas",
        colunas=[
            "id", "usuario_id", "provedor", "assinatura_externa_id",
            "plano_codigo", "periodicidade", "valor", "status",
            "inicio_em", "proxima_cobranca_em", "cancelado_em",
            "criado_em", "atualizado_em",
        ],
        chave_conflito="assinatura_externa_id",
    )
    print(f"Assinaturas migradas: {total_assinaturas}")

    total_pagamentos = _migrar_tabela(
        origem, destino,
        tabela="pagamentos",
        colunas=[
            "id", "usuario_id", "assinatura_id", "provedor",
            "pagamento_externo_id", "valor", "status",
            "forma_pagamento", "pago_em", "criado_em",
        ],
        chave_conflito="pagamento_externo_id",
    )
    print(f"Pagamentos migrados: {total_pagamentos}")

    destino.close()
    origem.close()

    print("\nMigração concluída com sucesso.")
    print(
        "O banco local (SQLite) não foi alterado — "
        "continua intacto como backup."
    )


def _migrar_tabela(origem, destino, tabela, colunas, chave_conflito):
    linhas = origem.execute(f"SELECT * FROM {tabela}").fetchall()

    migrados = 0
    for linha in linhas:
        valores = [linha[c] for c in colunas]

        if chave_conflito:
            existente = destino.execute(
                f"SELECT id FROM {tabela} WHERE {chave_conflito} = ?",
                (linha[chave_conflito],),
            ).fetchone()
            if existente:
                continue  # já migrado antes, não duplica

        placeholders = ", ".join(["?"] * len(colunas))
        colunas_sql = ", ".join(colunas)

        destino.execute(
            f"INSERT INTO {tabela} ({colunas_sql}) VALUES ({placeholders})",
            valores,
        )
        migrados += 1

    destino.commit()
    return migrados


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    migrar(sys.argv[1])
