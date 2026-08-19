import re
import sqlite3
from pathlib import Path


CAMINHO_BANCO = (
    Path(__file__).resolve().parent
    / "data"
    / "entradapro_users.db"
)


def usuario_valido(usuario):
    return bool(
        re.fullmatch(
            r"[a-z0-9._]{4,20}",
            usuario
        )
    )


def migrar():
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

        if "usuario" not in nomes_colunas:
            conexao.execute(
                """
                ALTER TABLE usuarios
                ADD COLUMN usuario TEXT
                """
            )

            conexao.commit()

            print(
                "Coluna 'usuario' criada com sucesso."
            )

        else:
            print(
                "A coluna 'usuario' já existe."
            )

        usuarios = conexao.execute(
            """
            SELECT
                id,
                nome,
                email,
                usuario
            FROM usuarios
            ORDER BY id
            """
        ).fetchall()

        for conta in usuarios:
            if conta["usuario"]:
                print(
                    f"\n{conta['nome']} já possui usuário: "
                    f"{conta['usuario']}"
                )

                continue

            print()
            print(
                f"Nome: {conta['nome']}"
            )

            print(
                f"E-mail: {conta['email']}"
            )

            while True:
                novo_usuario = input(
                    "Escolha o nome de usuário: "
                ).strip().lower()

                if not usuario_valido(
                    novo_usuario
                ):
                    print(
                        "Use de 4 a 20 caracteres, "
                        "apenas letras minúsculas, "
                        "números, ponto ou underline."
                    )

                    continue

                existente = conexao.execute(
                    """
                    SELECT id
                    FROM usuarios
                    WHERE usuario = ?
                    """,
                    (
                        novo_usuario,
                    )
                ).fetchone()

                if existente:
                    print(
                        "Esse nome de usuário já está em uso."
                    )

                    continue

                conexao.execute(
                    """
                    UPDATE usuarios
                    SET usuario = ?
                    WHERE id = ?
                    """,
                    (
                        novo_usuario,
                        conta["id"]
                    )
                )

                conexao.commit()

                print(
                    f"Usuário definido como: "
                    f"{novo_usuario}"
                )

                break

        conexao.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_usuarios_usuario
            ON usuarios(usuario)
            """
        )

        conexao.commit()

        print()
        print(
            "Migração concluída com sucesso."
        )


if __name__ == "__main__":
    migrar()