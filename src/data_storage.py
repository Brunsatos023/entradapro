import json
from pathlib import Path


# Pasta raiz do projeto FootballAI
PASTA_RAIZ = Path(__file__).resolve().parent.parent

# Caminho absoluto para FootballAI/data/raw
PASTA_DADOS_BRUTOS = PASTA_RAIZ / "data" / "raw"


def obter_caminho(nome_arquivo):
    return PASTA_DADOS_BRUTOS / nome_arquivo


def arquivo_existe(nome_arquivo):
    caminho_arquivo = obter_caminho(nome_arquivo)

    return caminho_arquivo.exists()


def salvar_json(dados, nome_arquivo):
    PASTA_DADOS_BRUTOS.mkdir(
        parents=True,
        exist_ok=True
    )

    caminho_arquivo = obter_caminho(nome_arquivo)

    with open(
        caminho_arquivo,
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=4
        )

    return caminho_arquivo


def carregar_json(nome_arquivo):
    caminho_arquivo = obter_caminho(nome_arquivo)

    if not caminho_arquivo.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho_arquivo}"
        )

    with open(
        caminho_arquivo,
        "r",
        encoding="utf-8"
    ) as arquivo:
        return json.load(arquivo)