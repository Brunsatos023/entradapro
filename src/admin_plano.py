import sqlite3
from pathlib import Path


CAMINHO_BANCO = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "entradapro_users.db"
)


def alterar_plano(email, novo_plano):
    novo_plano = str(
        novo_plano
    ).strip().upper()

    if novo_plano not in {
        "FREE",
        "PRO"
    }:
        raise ValueError(
            "Plano inválido. Use FREE ou PRO."
        )

    email = str(
        email
    ).strip().lower()

    with sqlite3.connect(
        CAMINHO_BANCO
    ) as conexao:
        cursor = conexao.execute(
            """
            UPDATE usuarios
            SET plano = ?
            WHERE email = ?
            """,
            (
                novo_plano,
                email
            )
        )

        conexao.commit()

        if cursor.rowcount == 0:
            print(
                "Nenhum usuário encontrado "
                "com esse e-mail."
            )

            return

        print(
            f"Plano alterado para {novo_plano} "
            f"com sucesso."
        )


if __name__ == "__main__":
    email = input(
        "E-mail do usuário: "
    )

    plano = input(
        "Novo plano (FREE/PRO): "
    )

    alterar_plano(
        email=email,
        novo_plano=plano
    )