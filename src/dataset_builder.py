import csv
from pathlib import Path


class DatasetBuilder:

    def __init__(self, partidas):
        self.partidas = partidas

    def criar_dataset(self):

        linhas = []

        for partida in self.partidas:

            if partida["fixture"]["status"]["short"] not in [
                "FT",
                "AET",
                "PEN"
            ]:
                continue

            gols_casa = partida["goals"]["home"]
            gols_fora = partida["goals"]["away"]

            over15 = int((gols_casa + gols_fora) >= 2)

            btts = int(
                gols_casa > 0 and
                gols_fora > 0
            )

            linhas.append({

                "mandante":
                partida["teams"]["home"]["name"],

                "visitante":
                partida["teams"]["away"]["name"],

                "gols_casa":
                gols_casa,

                "gols_fora":
                gols_fora,

                "over15":
                over15,

                "btts":
                btts

            })

        return linhas

    def salvar_csv(self, caminho):

        dados = self.criar_dataset()

        Path(caminho).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            caminho,
            "w",
            newline="",
            encoding="utf-8"
        ) as arquivo:

            writer = csv.DictWriter(
                arquivo,
                fieldnames=dados[0].keys()
            )

            writer.writeheader()

            writer.writerows(dados)

        return len(dados)