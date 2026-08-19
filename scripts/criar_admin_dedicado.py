"""
Cria (ou atualiza) uma conta de administrador DEDICADA, com usuário
e senha fixos definidos abaixo - para acabar com a confusão entre
usar e-mail ou nome de usuário na tela de login do admin.

COMO USAR:

    No Shell do Render (aba Shell do serviço entradapro-webhook):

        python scripts/criar_admin_dedicado.py

Depois de rodar, use estes dados para entrar em
entradapro.com.br -> página "Administracao":

    Usuário: entradapro_admin
    Senha:   VS3S4gRnuN5SG3

(Se quiser, pode trocar a senha abaixo antes de rodar o script, ou
trocar depois pela própria tela "Minha Conta" do site, uma vez
logado.)

Este script é seguro de rodar mais de uma vez - se a conta já
existir, apenas garante que ela tem a senha e a permissão de admin
corretas, não duplica nada.
"""

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


USUARIO_ADMIN = "entradapro_admin"
SENHA_ADMIN = "VS3S4gRnuN5SG3"
EMAIL_ADMIN = "admin@entradapro.com.br"
NOME_ADMIN = "Administrador EntradaPro"


def criar_admin_dedicado():
    import db
    import auth

    db.inicializar_banco()

    with db.conectar_banco() as conexao:
        existente = conexao.execute(
            "SELECT id FROM usuarios WHERE usuario = ?",
            (USUARIO_ADMIN,),
        ).fetchone()

    if existente:
        # já existe: garante a senha certa e a permissão de admin
        with db.conectar_banco() as conexao:
            hash_novo, salt_novo = auth._gerar_hash_senha(SENHA_ADMIN)
            conexao.execute(
                """
                UPDATE usuarios
                SET senha_hash = ?, senha_salt = ?, admin = 1, ativo = 1
                WHERE id = ?
                """,
                (hash_novo, salt_novo, existente["id"]),
            )
            conexao.commit()

        print(f"Conta '{USUARIO_ADMIN}' já existia - senha e permissão atualizadas.")
    else:
        ok, mensagem = auth.cadastrar_usuario(
            nome=NOME_ADMIN,
            usuario=USUARIO_ADMIN,
            email=EMAIL_ADMIN,
            senha=SENHA_ADMIN,
            confirmar_senha=SENHA_ADMIN,
        )

        if not ok:
            print(f"Erro ao criar a conta: {mensagem}")
            return

        with db.conectar_banco() as conexao:
            usuario = conexao.execute(
                "SELECT id FROM usuarios WHERE usuario = ?",
                (USUARIO_ADMIN,),
            ).fetchone()

            conexao.execute(
                "UPDATE usuarios SET admin = 1 WHERE id = ?",
                (usuario["id"],),
            )
            conexao.commit()

        print(f"Conta '{USUARIO_ADMIN}' criada com sucesso e marcada como admin.")

    print()
    print("=" * 50)
    print("USE ESTES DADOS NA PÁGINA DE ADMINISTRAÇÃO:")
    print(f"  Usuário: {USUARIO_ADMIN}")
    print(f"  Senha:   {SENHA_ADMIN}")
    print("=" * 50)


if __name__ == "__main__":
    criar_admin_dedicado()
