"""
Login com Google — usa a autenticação nativa do Streamlit
(st.login(), disponível a partir da versão 1.42), que implementa
OpenID Connect de verdade (padrão da indústria, mesmo mecanismo
usado por grandes sites).

Quando alguém entra com o Google pela primeira vez, criamos uma
conta local do EntradaPro automaticamente (plano FREE, sem senha
utilizável — essa conta só entra pelo Google mesmo). Da segunda
vez em diante, só reconhecemos a conta já existente pelo e-mail.
"""

import os
import secrets

from db import conectar_banco
from auth import (
    _gerar_hash_senha,
    _normalizar_email,
    _normalizar_usuario,
    _buscar_usuario_por_email,
)


def _gerar_usuario_unico_a_partir_do_email(email):
    """
    Deriva um nome de usuário a partir do e-mail (parte antes do
    @), garantindo que seja único mesmo se já existir alguém com
    o mesmo prefixo.
    """
    base = _normalizar_usuario(email.split("@")[0])
    candidato = base
    sufixo = 1

    with conectar_banco() as conexao:
        while True:
            existente = conexao.execute(
                "SELECT id FROM usuarios WHERE usuario = ?",
                (candidato,),
            ).fetchone()

            if not existente:
                return candidato

            sufixo += 1
            candidato = f"{base}{sufixo}"


def obter_ou_criar_usuario_google(email, nome):
    """
    Encontra a conta local correspondente a esse e-mail do Google,
    ou cria uma nova automaticamente (plano FREE) se for a
    primeira vez.

    Retorna o dicionário da conta, no mesmo formato que
    auth.autenticar_usuario() retorna - para que o resto do
    sistema (FREE/PRO, admin, etc.) funcione sem precisar saber
    que o login veio do Google.
    """
    email_normalizado = _normalizar_email(email)

    conta_existente = _buscar_usuario_por_email(email_normalizado)

    if conta_existente:
        return {
            "id": conta_existente["id"],
            "nome": conta_existente["nome"],
            "usuario": conta_existente["usuario"],
            "email": conta_existente["email"],
            "plano": conta_existente["plano"],
        }

    usuario_gerado = _gerar_usuario_unico_a_partir_do_email(
        email_normalizado
    )

    # Senha aleatoria e descartada - esta conta so entra pelo
    # Google, nunca vai ser usada para login com senha.
    senha_hash, senha_salt = _gerar_hash_senha(
        secrets.token_urlsafe(32)
    )

    with conectar_banco() as conexao:
        cursor = conexao.execute(
            """
            INSERT INTO usuarios (
                nome, usuario, email, senha_hash, senha_salt,
                plano, ativo, login_google
            ) VALUES (?, ?, ?, ?, ?, 'FREE', 1, 1)
            """,
            (
                nome or usuario_gerado,
                usuario_gerado,
                email_normalizado,
                senha_hash,
                senha_salt,
            ),
        )
        conexao.commit()
        novo_id = cursor.lastrowid

    return {
        "id": novo_id,
        "nome": nome or usuario_gerado,
        "usuario": usuario_gerado,
        "email": email_normalizado,
        "plano": "FREE",
    }
