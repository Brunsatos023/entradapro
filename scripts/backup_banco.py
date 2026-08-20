"""
Backup do banco de dados de produção: exporta as tabelas mais
importantes (usuários, assinaturas, pagamentos, previsões) para
um arquivo JSON com data - uma rede de segurança independente do
Neon, já que o plano gratuito só guarda 6 horas de histórico de
recuperação.

Dados sensíveis (hash e salt de senha) são EXCLUÍDOS do backup de
propósito - não são necessários para restaurar o negócio, e não
há motivo para guardar essa informação em mais um lugar.

COMO USAR:

    Precisa da variável de ambiente DATABASE_URL configurada
    (mesma connection string do Neon usada em produção):

    python scripts/backup_banco.py

Isso é executado automaticamente todo dia pelo GitHub Actions
(.github/workflows/backup_diario.yml) - não precisa rodar manual
no dia a dia, mas pode rodar quando quiser uma cópia extra.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


TABELAS_PARA_BACKUP = {
    "usuarios": [
        "id", "nome", "usuario", "email", "plano",
        "ativo", "admin", "criado_em",
        # senha_hash e senha_salt propositalmente EXCLUIDOS
    ],
    "assinaturas": "*",
    "pagamentos": "*",
    "previsoes": "*",
}


def fazer_backup():
    import db

    pasta_backups = Path(__file__).resolve().parents[1] / "backups"
    pasta_backups.mkdir(parents=True, exist_ok=True)

    agora = datetime.now().strftime("%Y-%m-%d_%H%M")
    caminho_arquivo = pasta_backups / f"backup_{agora}.json"

    backup = {
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "tabelas": {},
    }

    with db.conectar_banco() as conexao:
        for tabela, colunas in TABELAS_PARA_BACKUP.items():
            lista_colunas = (
                "*" if colunas == "*" else ", ".join(colunas)
            )

            linhas = conexao.execute(
                f"SELECT {lista_colunas} FROM {tabela}"
            ).fetchall()

            backup["tabelas"][tabela] = [
                dict(linha) for linha in linhas
            ]

    with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
        json.dump(
            backup, arquivo, indent=2, default=str, ensure_ascii=False
        )

    print(f"Backup salvo em: {caminho_arquivo}")

    for tabela, linhas in backup["tabelas"].items():
        print(f"  {tabela}: {len(linhas)} registro(s)")

    return caminho_arquivo


if __name__ == "__main__":
    fazer_backup()
