"""
Promove um usuário existente a administrador (acesso ao painel
/pages/3_Administracao.py).

COMO USAR (local, testando no seu banco SQLite):

    python scripts/tornar_admin.py nome.do.usuario

COMO USAR (no banco de produção/Neon):

    Defina a variável de ambiente DATABASE_URL antes de rodar
    (mesma connection string usada no Render), por exemplo:

    Windows (PowerShell):
        $env:DATABASE_URL="postgresql://..."
        python scripts/tornar_admin.py nome.do.usuario

    Ou rode diretamente pelo "Shell" do próprio serviço no Render
    (aba Shell do entradapro-webhook, que já tem DATABASE_URL
    configurada automaticamente):

        python scripts/tornar_admin.py nome.do.usuario

Este script é seguro de rodar mais de uma vez - se o usuário já for
admin, apenas confirma isso, não duplica nem quebra nada.
"""

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def tornar_admin(nome_usuario):
    import db

    db.inicializar_banco()

    with db.conectar_banco() as conexao:
        usuario = conexao.execute(
            "SELECT id, nome, usuario, admin FROM usuarios WHERE usuario = ?",
            (nome_usuario,),
        ).fetchone()

        if not usuario:
            print(f"Usuário '{nome_usuario}' não encontrado.")
            print(
                "Confira se digitou o nome de usuário exatamente "
                "como foi cadastrado (não é o e-mail)."
            )
            return

        if int(usuario["admin"]) == 1:
            print(
                f"'{usuario['nome']}' (@{usuario['usuario']}) "
                "já é administrador. Nada a fazer."
            )
            return

        conexao.execute(
            "UPDATE usuarios SET admin = 1 WHERE id = ?",
            (usuario["id"],),
        )
        conexao.commit()

        print(
            f"Pronto: '{usuario['nome']}' (@{usuario['usuario']}) "
            "agora é administrador."
        )
        print("Acesse /pages/3_Administracao.py no site para conferir.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python scripts/tornar_admin.py nome_do_usuario")
        sys.exit(1)

    tornar_admin(sys.argv[1])
