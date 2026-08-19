import re
import subprocess
import unicodedata
from pathlib import Path

from data_storage import carregar_json


ARQUIVO_JSON = "brasileirao_serie_a_2024.json"

DOMINIO_ESCUDOS = "media.api-sports.io"

IPS_ALTERNATIVOS = [
    "172.66.164.245",
    "104.20.39.36"
]

PASTA_DESTINO = (
    Path(__file__).resolve().parent
    / "assets"
    / "teams"
)


def normalizar_nome(nome):
    nome = unicodedata.normalize(
        "NFKD",
        nome
    ).encode(
        "ascii",
        "ignore"
    ).decode(
        "ascii"
    )

    nome = nome.lower()

    nome = re.sub(
        r"[^a-z0-9]+",
        "_",
        nome
    )

    return nome.strip("_")


def listar_times(partidas):
    times = {}

    for partida in partidas:
        for lado in ("home", "away"):
            time = partida.get(
                "teams",
                {}
            ).get(
                lado,
                {}
            )

            team_id = time.get("id")
            nome = time.get("name")

            if team_id is None or not nome:
                continue

            times[team_id] = {
                "id": team_id,
                "nome": nome
            }

    return sorted(
        times.values(),
        key=lambda item: item["nome"]
    )


def arquivo_png_valido(caminho):
    if not caminho.exists():
        return False

    if caminho.stat().st_size == 0:
        return False

    assinatura_png = b"\x89PNG\r\n\x1a\n"

    with caminho.open("rb") as arquivo:
        assinatura = arquivo.read(8)

    return assinatura == assinatura_png


def baixar_com_curl(
    team_id,
    caminho_destino,
    ip
):
    url = (
        f"https://{DOMINIO_ESCUDOS}"
        f"/football/teams/{team_id}.png"
    )

    resolucao = (
        f"{DOMINIO_ESCUDOS}:443:{ip}"
    )

    comando = [
        "curl.exe",
        "--silent",
        "--show-error",
        "--fail",
        "--location",
        "--connect-timeout",
        "20",
        "--max-time",
        "40",
        "--resolve",
        resolucao,
        "--output",
        str(caminho_destino),
        url
    ]

    processo = subprocess.run(
        comando,
        capture_output=True,
        text=True,
        check=False
    )

    if processo.returncode != 0:
        if caminho_destino.exists():
            caminho_destino.unlink()

        return False, processo.stderr.strip()

    if not arquivo_png_valido(caminho_destino):
        if caminho_destino.exists():
            caminho_destino.unlink()

        return False, "O arquivo recebido não é um PNG válido."

    return True, None


def baixar_escudo(time):
    team_id = time["id"]
    nome = time["nome"]

    nome_arquivo = (
        f"{normalizar_nome(nome)}.png"
    )

    caminho_destino = (
        PASTA_DESTINO
        / nome_arquivo
    )

    if arquivo_png_valido(caminho_destino):
        print(
            f"Já existe: {nome_arquivo}"
        )
        return True

    ultimo_erro = None

    for ip in IPS_ALTERNATIVOS:
        sucesso, erro = baixar_com_curl(
            team_id=team_id,
            caminho_destino=caminho_destino,
            ip=ip
        )

        if sucesso:
            print(
                f"Baixado: {nome} "
                f"→ {nome_arquivo}"
            )
            return True

        ultimo_erro = erro

    print(
        f"Erro ao baixar {nome}: "
        f"{ultimo_erro}"
    )

    return False


def main():
    try:
        dados = carregar_json(
            ARQUIVO_JSON
        )

        if not isinstance(dados, dict):
            raise TypeError(
                "O JSON não retornou um "
                "dicionário válido."
            )

        partidas = dados.get(
            "response",
            []
        )

        if not isinstance(partidas, list):
            raise TypeError(
                "A chave 'response' precisa "
                "conter uma lista."
            )

        if not partidas:
            raise ValueError(
                "Nenhuma partida foi encontrada."
            )

        PASTA_DESTINO.mkdir(
            parents=True,
            exist_ok=True
        )

        times = listar_times(
            partidas
        )

        print("=" * 60)
        print("FOOTBALLAI — DOWNLOAD DE ESCUDOS")
        print("=" * 60)

        print(
            f"Times encontrados: {len(times)}"
        )

        print(
            "Método: curl.exe com DNS alternativo"
        )

        print()

        baixados = 0
        falhas = 0

        for time in times:
            if baixar_escudo(time):
                baixados += 1
            else:
                falhas += 1

        print("\n" + "=" * 60)

        print(
            f"Concluído: {baixados} de "
            f"{len(times)} escudos."
        )

        print(
            f"Falhas: {falhas}"
        )

        print(
            f"Pasta: {PASTA_DESTINO}"
        )

        print("=" * 60)

    except FileNotFoundError:
        print(
            f"ERRO: o arquivo '{ARQUIVO_JSON}' "
            "não foi encontrado."
        )

    except Exception as erro:
        print(
            f"ERRO: {type(erro).__name__}: "
            f"{erro}"
        )


if __name__ == "__main__":
    main()