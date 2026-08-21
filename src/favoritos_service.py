"""
Serviço de times favoritos: usuário marca times para acompanhar
mais de perto - reaproveitável em qualquer lista de times/jogos
para destacar os favoritos primeiro.
"""

from db import conectar_banco


def eh_favorito(usuario_id, nome_time):
    with conectar_banco() as conexao:
        linha = conexao.execute(
            """
            SELECT id FROM times_favoritos
            WHERE usuario_id = ? AND nome_time = ?
            """,
            (usuario_id, nome_time),
        ).fetchone()

    return linha is not None


def alternar_favorito(usuario_id, nome_time):
    """
    Se o time já é favorito, remove. Se não é, adiciona.
    Retorna o novo estado (True = agora é favorito).
    """
    if eh_favorito(usuario_id, nome_time):
        with conectar_banco() as conexao:
            conexao.execute(
                """
                DELETE FROM times_favoritos
                WHERE usuario_id = ? AND nome_time = ?
                """,
                (usuario_id, nome_time),
            )
            conexao.commit()
        return False

    with conectar_banco() as conexao:
        conexao.execute(
            """
            INSERT INTO times_favoritos (usuario_id, nome_time)
            VALUES (?, ?)
            """,
            (usuario_id, nome_time),
        )
        conexao.commit()
    return True


def listar_favoritos(usuario_id):
    with conectar_banco() as conexao:
        linhas = conexao.execute(
            """
            SELECT nome_time FROM times_favoritos
            WHERE usuario_id = ?
            ORDER BY criado_em DESC
            """,
            (usuario_id,),
        ).fetchall()

    return [linha["nome_time"] for linha in linhas]
