import csv
from collections import defaultdict
from pathlib import Path


STATUS_ENCERRADOS = {"FT", "AET", "PEN"}


class PreMatchFeatureBuilder:
    def __init__(
        self,
        partidas,
        janela_geral=5,
        janela_mando=3
    ):
        self.janela_geral = janela_geral
        self.janela_mando = janela_mando

        self.partidas = sorted(
            [
                partida
                for partida in partidas
                if partida["fixture"]["status"]["short"]
                in STATUS_ENCERRADOS
            ],
            key=lambda partida: partida["fixture"]["timestamp"]
        )

    def _calcular_estatisticas(self, historico, janela):
        ultimos_jogos = historico[-janela:]

        if len(ultimos_jogos) < janela:
            return None

        total = len(ultimos_jogos)

        gols_marcados = sum(
            jogo["gols_marcados"]
            for jogo in ultimos_jogos
        )

        gols_sofridos = sum(
            jogo["gols_sofridos"]
            for jogo in ultimos_jogos
        )

        pontos = sum(
            jogo["pontos"]
            for jogo in ultimos_jogos
        )

        jogos_over15 = sum(
            jogo["over15"]
            for jogo in ultimos_jogos
        )

        jogos_btts = sum(
            jogo["btts"]
            for jogo in ultimos_jogos
        )

        return {
            "media_gols_marcados": gols_marcados / total,
            "media_gols_sofridos": gols_sofridos / total,
            "media_pontos": pontos / total,
            "percentual_over15": jogos_over15 / total,
            "percentual_btts": jogos_btts / total
        }

    def criar_dataset(self):
        historico_geral = defaultdict(list)
        historico_casa = defaultdict(list)
        historico_fora = defaultdict(list)

        linhas = []

        for partida in self.partidas:
            time_casa = partida["teams"]["home"]
            time_fora = partida["teams"]["away"]

            id_casa = time_casa["id"]
            id_fora = time_fora["id"]

            gols_casa = partida["goals"]["home"]
            gols_fora = partida["goals"]["away"]

            if gols_casa is None or gols_fora is None:
                continue

            geral_casa = self._calcular_estatisticas(
                historico_geral[id_casa],
                self.janela_geral
            )

            geral_fora = self._calcular_estatisticas(
                historico_geral[id_fora],
                self.janela_geral
            )

            mando_casa = self._calcular_estatisticas(
                historico_casa[id_casa],
                self.janela_mando
            )

            visitante_fora = self._calcular_estatisticas(
                historico_fora[id_fora],
                self.janela_mando
            )

            possui_historico = all([
                geral_casa is not None,
                geral_fora is not None,
                mando_casa is not None,
                visitante_fora is not None
            ])

            if possui_historico:
                total_gols = gols_casa + gols_fora

                linhas.append({
                    "fixture_id": partida["fixture"]["id"],
                    "data": partida["fixture"]["date"],
                    "mandante": time_casa["name"],
                    "visitante": time_fora["name"],

                    "casa_geral_gols_marcados_5":
                    geral_casa["media_gols_marcados"],

                    "casa_geral_gols_sofridos_5":
                    geral_casa["media_gols_sofridos"],

                    "casa_geral_pontos_5":
                    geral_casa["media_pontos"],

                    "casa_geral_over15_5":
                    geral_casa["percentual_over15"],

                    "casa_geral_btts_5":
                    geral_casa["percentual_btts"],

                    "fora_geral_gols_marcados_5":
                    geral_fora["media_gols_marcados"],

                    "fora_geral_gols_sofridos_5":
                    geral_fora["media_gols_sofridos"],

                    "fora_geral_pontos_5":
                    geral_fora["media_pontos"],

                    "fora_geral_over15_5":
                    geral_fora["percentual_over15"],

                    "fora_geral_btts_5":
                    geral_fora["percentual_btts"],

                    "mandante_em_casa_gols_marcados_3":
                    mando_casa["media_gols_marcados"],

                    "mandante_em_casa_gols_sofridos_3":
                    mando_casa["media_gols_sofridos"],

                    "mandante_em_casa_pontos_3":
                    mando_casa["media_pontos"],

                    "mandante_em_casa_over15_3":
                    mando_casa["percentual_over15"],

                    "mandante_em_casa_btts_3":
                    mando_casa["percentual_btts"],

                    "visitante_fora_gols_marcados_3":
                    visitante_fora["media_gols_marcados"],

                    "visitante_fora_gols_sofridos_3":
                    visitante_fora["media_gols_sofridos"],

                    "visitante_fora_pontos_3":
                    visitante_fora["media_pontos"],

                    "visitante_fora_over15_3":
                    visitante_fora["percentual_over15"],

                    "visitante_fora_btts_3":
                    visitante_fora["percentual_btts"],

                    "target_over15": int(total_gols >= 2),

                    "target_btts": int(
                        gols_casa > 0 and gols_fora > 0
                    )
                })

            if gols_casa > gols_fora:
                pontos_casa = 3
                pontos_fora = 0
            elif gols_casa < gols_fora:
                pontos_casa = 0
                pontos_fora = 3
            else:
                pontos_casa = 1
                pontos_fora = 1

            resultado_over15 = int(
                gols_casa + gols_fora >= 2
            )

            resultado_btts = int(
                gols_casa > 0 and gols_fora > 0
            )

            registro_casa = {
                "gols_marcados": gols_casa,
                "gols_sofridos": gols_fora,
                "pontos": pontos_casa,
                "over15": resultado_over15,
                "btts": resultado_btts
            }

            registro_fora = {
                "gols_marcados": gols_fora,
                "gols_sofridos": gols_casa,
                "pontos": pontos_fora,
                "over15": resultado_over15,
                "btts": resultado_btts
            }

            historico_geral[id_casa].append(registro_casa)
            historico_geral[id_fora].append(registro_fora)

            historico_casa[id_casa].append(registro_casa)
            historico_fora[id_fora].append(registro_fora)

        return linhas

    def salvar_csv(self, caminho):
        dados = self.criar_dataset()

        if not dados:
            raise ValueError(
                "Nenhuma linha foi criada para o dataset."
            )

        caminho = Path(caminho)

        caminho.parent.mkdir(
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