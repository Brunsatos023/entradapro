import sqlite3
from pathlib import Path


CAMINHO_BANCO = (
    Path(__file__).resolve().parent
    / "data"
    / "entradapro_users.db"
)


USUARIO_ADMIN = "brunovini96"


def migrar_admin():
    with sqlite3.connect(
        CAMINHO_BANCO
    ) as conexao:
        conexao.row_factory = sqlite3.Row

        colunas = conexao.execute(
            """
            PRAGMA table_info(usuarios)
            """
        ).fetchall()

        nomes_colunas = {
            coluna["name"]
            for coluna in colunas
        }

        if "admin" not in nomes_colunas:
            conexao.execute(
                """
                ALTER TABLE usuarios
                ADD COLUMN admin INTEGER
                NOT NULL DEFAULT 0
                """
            )

            conexao.commit()

            print(
                "Coluna 'admin' criada com sucesso."
            )

        else:
            print(
                "A coluna 'admin' já existe."
            )

        usuario = conexao.execute(
            """
            SELECT
                id,
                nome,
                usuario,
                email,
                plano,
                ativo,
                admin
            FROM usuarios
            WHERE usuario = ?
            """,
            (
                USUARIO_ADMIN,
            )
        ).fetchone()

        if not usuario:
            print()
            print(
                f"Usuário @{USUARIO_ADMIN} "
                "não encontrado."
            )

            return

        conexao.execute(
            """
            UPDATE usuarios
            SET admin = 1
            WHERE id = ?
            """,
            (
                usuario["id"],
            )
        )

        conexao.commit()

        usuario_atualizado = conexao.execute(
            """
            SELECT
                id,
                nome,
                usuario,
                email,
                plano,
                ativo,
                admin
            FROM usuarios
            WHERE id = ?
            """,
            (
                usuario["id"],
            )
        ).fetchone()

        print()
        print(
            "Administrador configurado:"
        )

        print(
            f"Nome: {usuario_atualizado['nome']}"
        )

        print(
            f"Usuário: @{usuario_atualizado['usuario']}"
        )

        print(
            f"E-mail: {usuario_atualizado['email']}"
        )

        print(
            f"Plano: {usuario_atualizado['plano']}"
        )

        print(
            f"Ativo: {usuario_atualizado['ativo']}"
        )

        print(
            f"Admin: {usuario_atualizado['admin']}"
        )

        print()
        print(
            "Migração ADMIN concluída com sucesso."
        )


if __name__ == "__main__":
    migrar_admin()