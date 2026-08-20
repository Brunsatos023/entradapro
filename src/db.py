"""
Módulo central de conexão com o banco de dados do EntradaPro.

Todos os outros arquivos (auth.py, subscription_service.py,
admin_users.py, admin_plano.py) devem importar `conectar_banco`,
`inicializar_banco` e `ErroIntegridade` DAQUI, em vez de conectar
direto no sqlite3/psycopg2. Isso mantém um único lugar responsável
por "onde e como" os dados são guardados.

Comportamento:

- Por padrão (nenhuma configuração extra), usa SQLite, salvando em
  data/entradapro_users.db — exatamente como o projeto sempre
  funcionou. Ideal para rodar na sua máquina.

- Se a variável de ambiente DATABASE_URL estiver definida (aponta
  para um banco PostgreSQL, como o Neon), passa a usar PostgreSQL
  automaticamente. Nenhum outro arquivo do projeto precisa mudar.

⚠️ O caminho do PostgreSQL depende do pacote "psycopg2-binary"
(já incluso no requirements.txt) e de uma conexão de rede de verdade
com o banco — por isso só pode ser validado de um ambiente com
acesso à internet (sua máquina, ou o servidor de produção).
"""

import os
import sqlite3
from pathlib import Path


CAMINHO_BANCO_SQLITE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "entradapro_users.db"
)

DATABASE_URL = os.getenv("DATABASE_URL")


def usando_postgres():
    return bool(DATABASE_URL)


# Erro de "violação de restrição" (ex: e-mail duplicado). O nome da
# classe muda entre SQLite e PostgreSQL, então expomos uma tupla
# única que funciona nos dois casos: `except ErroIntegridade:`
if usando_postgres():
    import psycopg2

    ErroIntegridade = (psycopg2.IntegrityError,)
else:
    ErroIntegridade = (sqlite3.IntegrityError,)


class _CursorCompativel:
    """
    Faz um cursor do psycopg2 aceitar o mesmo estilo de SQL que o
    projeto já usa com SQLite: placeholders com "?" (em vez de "%s")
    e `cursor.lastrowid` disponível logo após um INSERT.
    """

    def __init__(self, cursor_real):
        self._cursor = cursor_real
        self.lastrowid = None

    def execute(self, sql, parametros=()):
        sql_postgres = sql.replace("?", "%s")

        eh_insert = sql.strip().upper().startswith("INSERT")
        if eh_insert and "RETURNING" not in sql_postgres.upper():
            sql_postgres = sql_postgres.rstrip().rstrip(";") + " RETURNING id"

        self._cursor.execute(sql_postgres, parametros)

        if eh_insert:
            try:
                linha = self._cursor.fetchone()
                self.lastrowid = linha["id"] if linha else None
            except Exception:
                self.lastrowid = None

        return self

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    @property
    def rowcount(self):
        return self._cursor.rowcount


class _ConexaoCompativel:
    """
    Faz uma conexão do psycopg2 se comportar como a conexão do
    sqlite3 que o projeto já usa: `conexao.execute(...)` direto
    (sem precisar pegar um cursor à parte) e `with conexao as c:`
    fazendo commit automático ao final do bloco.
    """

    def __init__(self, conexao_real):
        self._conexao = conexao_real

    def execute(self, sql, parametros=()):
        cursor = _CursorCompativel(self._conexao.cursor())
        cursor.execute(sql, parametros)
        return cursor

    def commit(self):
        self._conexao.commit()

    def close(self):
        self._conexao.close()

    def __enter__(self):
        return self

    def __exit__(self, tipo, valor, rastreamento):
        if tipo is None:
            self._conexao.commit()
        self._conexao.close()


def conectar_banco():
    """
    Ponto único de conexão com o banco. Use esta função em vez de
    chamar sqlite3.connect(...) ou psycopg2.connect(...) diretamente
    em qualquer outro arquivo do projeto.
    """
    if usando_postgres():
        import psycopg2
        import psycopg2.extras

        conexao_real = psycopg2.connect(
            DATABASE_URL,
            cursor_factory=psycopg2.extras.RealDictCursor,
        )
        return _ConexaoCompativel(conexao_real)

    CAMINHO_BANCO_SQLITE.parent.mkdir(parents=True, exist_ok=True)
    conexao = sqlite3.connect(CAMINHO_BANCO_SQLITE)
    conexao.row_factory = sqlite3.Row
    return conexao


def inicializar_banco():
    """
    Cria (se ainda não existirem) todas as tabelas que o EntradaPro
    precisa: usuários, recuperação de senha, assinaturas e
    pagamentos. Segura de rodar toda vez que o app inicia, e mesmo
    várias vezes seguidas — nunca apaga ou altera dado existente.
    """
    if usando_postgres():
        _inicializar_banco_postgres()
    else:
        _inicializar_banco_sqlite()


def _inicializar_banco_sqlite():
    with conectar_banco() as conexao:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha_hash TEXT NOT NULL,
                senha_salt TEXT NOT NULL,
                plano TEXT NOT NULL DEFAULT 'FREE',
                ativo INTEGER NOT NULL DEFAULT 1,
                criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS recuperacao_senha (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                token_hash TEXT NOT NULL,
                expira_em DATETIME NOT NULL,
                usado INTEGER NOT NULL DEFAULT 0,
                criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
            """
        )

        colunas_usuarios = conexao.execute(
            "PRAGMA table_info(usuarios)"
        ).fetchall()

        nomes_colunas = {coluna["name"] for coluna in colunas_usuarios}

        if "usuario" not in nomes_colunas:
            conexao.execute(
                "ALTER TABLE usuarios ADD COLUMN usuario TEXT"
            )

        if "admin" not in nomes_colunas:
            conexao.execute(
                """
                ALTER TABLE usuarios
                ADD COLUMN admin INTEGER NOT NULL DEFAULT 0
                """
            )

        conexao.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_usuarios_usuario ON usuarios(usuario)
            """
        )

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
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
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
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                FOREIGN KEY (assinatura_id) REFERENCES assinaturas(id)
            )
            """
        )

        conexao.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_assinaturas_externa ON assinaturas(assinatura_externa_id)
            """
        )
        conexao.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_pagamentos_externo ON pagamentos(pagamento_externo_id)
            """
        )
        conexao.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_assinaturas_usuario ON assinaturas(usuario_id)
            """
        )
        conexao.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_pagamentos_usuario ON pagamentos(usuario_id)
            """
        )
        conexao.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_assinaturas_status ON assinaturas(status)
            """
        )
        conexao.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_pagamentos_status ON pagamentos(status)
            """
        )

        # Etapa C do roteiro "EntradaPro Autonomo": a "memoria" do
        # sistema - toda previsao feita (manual ou pela varredura
        # automatica) fica registrada aqui, para depois comparar
        # com o resultado real (Green/Red/Void) e alimentar as
        # estatisticas de acerto/ROI.
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS previsoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fixture_id TEXT NOT NULL,
                mandante TEXT NOT NULL,
                visitante TEXT NOT NULL,
                mercado TEXT NOT NULL,
                odd REAL NOT NULL,
                probabilidade REAL NOT NULL,
                edge REAL NOT NULL,
                data_jogo DATETIME,
                status TEXT NOT NULL DEFAULT 'PENDENTE',
                gols_casa_real INTEGER,
                gols_visitante_real INTEGER,
                criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
                verificado_em DATETIME
            )
            """
        )

        conexao.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_previsoes_fixture_mercado
            ON previsoes(fixture_id, mercado)
            """
        )
        conexao.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_previsoes_status ON previsoes(status)
            """
        )

        conexao.commit()


def _inicializar_banco_postgres():
    with conectar_banco() as conexao:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                usuario TEXT UNIQUE,
                email TEXT NOT NULL UNIQUE,
                senha_hash TEXT NOT NULL,
                senha_salt TEXT NOT NULL,
                plano TEXT NOT NULL DEFAULT 'FREE',
                ativo INTEGER NOT NULL DEFAULT 1,
                admin INTEGER NOT NULL DEFAULT 0,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Bancos ja existentes (criados antes desta coluna existir)
        # nao sao afetados pelo CREATE TABLE IF NOT EXISTS acima -
        # entao garantimos a coluna aqui tambem, de forma segura.
        conexao.execute(
            """
            ALTER TABLE usuarios
            ADD COLUMN IF NOT EXISTS admin INTEGER NOT NULL DEFAULT 0
            """
        )

        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS recuperacao_senha (
                id SERIAL PRIMARY KEY,
                usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
                token_hash TEXT NOT NULL,
                expira_em TIMESTAMP NOT NULL,
                usado INTEGER NOT NULL DEFAULT 0,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS assinaturas (
                id SERIAL PRIMARY KEY,
                usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
                provedor TEXT NOT NULL DEFAULT 'MERCADO_PAGO',
                assinatura_externa_id TEXT UNIQUE,
                plano_codigo TEXT NOT NULL,
                periodicidade TEXT NOT NULL,
                valor REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDENTE',
                inicio_em TIMESTAMP,
                proxima_cobranca_em TIMESTAMP,
                cancelado_em TIMESTAMP,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS pagamentos (
                id SERIAL PRIMARY KEY,
                usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
                assinatura_id INTEGER REFERENCES assinaturas(id),
                provedor TEXT NOT NULL DEFAULT 'MERCADO_PAGO',
                pagamento_externo_id TEXT UNIQUE,
                valor REAL NOT NULL,
                status TEXT NOT NULL,
                forma_pagamento TEXT,
                pago_em TIMESTAMP,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conexao.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_assinaturas_usuario ON assinaturas(usuario_id)
            """
        )
        conexao.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_pagamentos_usuario ON pagamentos(usuario_id)
            """
        )
        conexao.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_assinaturas_status ON assinaturas(status)
            """
        )
        conexao.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_pagamentos_status ON pagamentos(status)
            """
        )

        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS previsoes (
                id SERIAL PRIMARY KEY,
                fixture_id TEXT NOT NULL,
                mandante TEXT NOT NULL,
                visitante TEXT NOT NULL,
                mercado TEXT NOT NULL,
                odd REAL NOT NULL,
                probabilidade REAL NOT NULL,
                edge REAL NOT NULL,
                data_jogo TIMESTAMP,
                status TEXT NOT NULL DEFAULT 'PENDENTE',
                gols_casa_real INTEGER,
                gols_visitante_real INTEGER,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verificado_em TIMESTAMP,
                UNIQUE (fixture_id, mercado)
            )
            """
        )

        conexao.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_previsoes_status ON previsoes(status)
            """
        )

        conexao.commit()
