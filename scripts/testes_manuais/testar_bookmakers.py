import os
import requests
from dotenv import load_dotenv


load_dotenv()


API_KEY = os.getenv(
    "API_FOOTBALL_KEY"
)

URL = (
    "https://v3.football.api-sports.io/"
    "odds/bookmakers"
)


def main():
    if not API_KEY:
        print(
            "ERRO: API_FOOTBALL_KEY "
            "não encontrada no .env."
        )
        return

    headers = {
        "x-apisports-key": API_KEY
    }

    try:
        resposta = requests.get(
            URL,
            headers=headers,
            timeout=20
        )

    except requests.RequestException as erro:
        print(
            "Erro de conexão:",
            erro
        )
        return

    print(
        "Status HTTP:",
        resposta.status_code
    )

    try:
        dados = resposta.json()

    except Exception:
        print(
            "Resposta inválida da API."
        )
        print(
            resposta.text
        )
        return

    erros = dados.get(
        "errors"
    )

    if erros:
        print()
        print(
            "ERROS DA API:"
        )
        print(
            erros
        )

    resultado = dados.get(
        "response",
        []
    )

    print()
    print(
        "Total de bookmakers:",
        len(resultado)
    )
    print()

    for bookmaker in resultado:
        bookmaker_id = bookmaker.get(
            "id"
        )

        bookmaker_name = bookmaker.get(
            "name"
        )

        print(
            f"{bookmaker_id} - "
            f"{bookmaker_name}"
        )


if __name__ == "__main__":
    main()