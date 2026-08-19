from footballai_engine import FootballAIEngine


class EngineValidator:

    def __init__(self, partidas):
        self.partidas = partidas

    def validar_time(self, team_id, nome_time="Time", janela=5):
        engine = FootballAIEngine(
            partidas=self.partidas,
            team_id=team_id,
            janela=janela
        )

        resultado = engine.analisar()

        print("\n" + "=" * 60)
        print(f"VALIDAÇÃO DO FOOTBALLAI — {nome_time}")
        print(f"TEAM ID: {team_id}")
        print("=" * 60)

        if resultado.get("erro"):
            print("\nERRO NA ANÁLISE")
            print(resultado["erro"])

            detalhes = resultado.get("detalhes", {})

            self._mostrar_detalhes_erro(detalhes)

            print("=" * 60)

            return resultado

        notas = resultado.get("notas_resumidas", {})

        rating = notas.get("rating", 0)
        forma = notas.get("forma", 0)
        pulse = notas.get("pulse", 0)
        home_away = notas.get("home_away", 0)
        opponent = notas.get("opponent", 0)

        intelligence_score = resultado.get(
            "intelligence_score",
            0
        )

        categoria = resultado.get(
            "categoria_intelligence",
            "Sem categoria"
        )

        print("\nNOTAS DOS MOTORES")
        print("-" * 60)

        print(f"Rating:                          {rating:>8.2f}")
        print(f"Forma:                           {forma:>8.2f}")
        print(f"Pulse:                           {pulse:>8.2f}")
        print(f"Casa/Fora:                       {home_away:>8.2f}")
        print(f"Força dos adversários:           {opponent:>8.2f}")

        print("-" * 60)

        print(
            f"Intelligence Score:              "
            f"{intelligence_score:>8.2f}"
        )

        print(
            f"Categoria:                        "
            f"{categoria}"
        )

        self._mostrar_detalhes_rating(resultado)

        self._mostrar_detalhes_opponent(resultado)

        self._mostrar_detalhes_pulse(resultado)

        self._verificar_alertas(
            rating=rating,
            forma=forma,
            pulse=pulse,
            home_away=home_away,
            opponent=opponent
        )

        print("=" * 60)

        return resultado

    def validar_varios_times(self, times, janela=5):
        resultados = []

        for time in times:
            team_id = time["id"]

            nome_time = time.get(
                "nome",
                f"Time {team_id}"
            )

            resultado = self.validar_time(
                team_id=team_id,
                nome_time=nome_time,
                janela=janela
            )

            resultados.append({
                "team_id": team_id,
                "nome": nome_time,
                "resultado": resultado
            })

        self._mostrar_resumo_geral(resultados)

        return resultados

    def _mostrar_detalhes_rating(self, resultado):
        rating_detalhes = resultado.get("rating", {})

        print("\nDIAGNÓSTICO DO RATING ENGINE")
        print("-" * 60)

        if not isinstance(rating_detalhes, dict):
            print(
                "O Rating Engine não retornou "
                "um dicionário válido."
            )
            return

        if rating_detalhes.get("erro"):
            print(
                "Erro do Rating Engine: "
                f"{rating_detalhes['erro']}"
            )
            return

        print(
            "Nota de ataque:            "
            f"{rating_detalhes.get('ataque', 0):.2f}"
        )

        print(
            "Nota de defesa:            "
            f"{rating_detalhes.get('defesa', 0):.2f}"
        )

        print(
            "Nota de forma:             "
            f"{rating_detalhes.get('forma', 0):.2f}"
        )

        print(
            "Nota em casa:              "
            f"{rating_detalhes.get('casa', 0):.2f}"
        )

        print(
            "Nota fora:                 "
            f"{rating_detalhes.get('fora', 0):.2f}"
        )

        print(
            "Nota de consistência:      "
            f"{rating_detalhes.get('consistencia', 0):.2f}"
        )

        print(
            "Rating final:              "
            f"{rating_detalhes.get('rating', 0):.2f}"
        )

        print(
            "Categoria do Rating:       "
            f"{rating_detalhes.get('categoria', '-')}"
        )

    def _mostrar_detalhes_opponent(self, resultado):
        opponent_detalhes = resultado.get("opponent", {})

        print("\nDIAGNÓSTICO DO OPPONENT STRENGTH ENGINE")
        print("-" * 60)

        if not isinstance(opponent_detalhes, dict):
            print(
                "O Opponent Strength Engine não retornou "
                "um dicionário válido."
            )
            return

        if opponent_detalhes.get("erro"):
            print(
                "Erro do Opponent Strength Engine: "
                f"{opponent_detalhes['erro']}"
            )
            return

        adversarios = opponent_detalhes.get(
            "adversarios",
            []
        )

        quantidade = opponent_detalhes.get(
            "quantidade_analisada",
            0
        )

        print(
            "Quantidade analisada:      "
            f"{quantidade}"
        )

        print("\nADVERSÁRIOS ANALISADOS")
        print("-" * 60)

        if not adversarios:
            print("Nenhum adversário foi retornado.")
        else:
            for indice, adversario in enumerate(
                adversarios,
                start=1
            ):
                print(
                    f"{indice}. "
                    f"{adversario.get('nome', 'Desconhecido')}"
                )

                print(
                    "   Rating:                "
                    f"{adversario.get('rating', 0):.2f}"
                )

                print(
                    "   Categoria:             "
                    f"{adversario.get('categoria', '-')}"
                )

                print(
                    "   Data do confronto:     "
                    f"{adversario.get('data_confronto', '-')}"
                )

                print("-" * 60)

        print(
            "Rating médio:              "
            f"{opponent_detalhes.get(
                'rating_medio_adversarios',
                0
            ):.2f}"
        )

        print(
            "Maior rating:              "
            f"{opponent_detalhes.get(
                'maior_rating',
                0
            ):.2f}"
        )

        print(
            "Menor rating:              "
            f"{opponent_detalhes.get(
                'menor_rating',
                0
            ):.2f}"
        )

        print(
            "Dificuldade:               "
            f"{opponent_detalhes.get(
                'dificuldade',
                '-'
            )}"
        )

        print(
            "Opponent Strength Score:   "
            f"{opponent_detalhes.get(
                'opponent_strength_score',
                0
            ):.2f}"
        )

    def _mostrar_detalhes_pulse(self, resultado):
        pulse_detalhes = resultado.get("pulse", {})

        print("\nDIAGNÓSTICO DO PULSE ENGINE")
        print("-" * 60)

        if not isinstance(pulse_detalhes, dict):
            print(
                "O Pulse Engine não retornou "
                "um dicionário válido."
            )
            return

        if pulse_detalhes.get("erro"):
            print(
                "Erro do Pulse Engine: "
                f"{pulse_detalhes['erro']}"
            )
            return

        print(
            "Jogos analisados:          "
            f"{pulse_detalhes.get('jogos_analisados', 0)}"
        )

        print(
            "Resultados recentes:       "
            f"{pulse_detalhes.get('resultados', [])}"
        )

        print(
            "Pontos por jogo:           "
            f"{pulse_detalhes.get('pontos_por_jogo', [])}"
        )

        print(
            "Saldo por jogo:            "
            f"{pulse_detalhes.get('saldo_por_jogo', [])}"
        )

        print(
            "Pontos ponderados:         "
            f"{pulse_detalhes.get('pontos_ponderados', 0)}"
        )

        print(
            "Saldo ponderado:           "
            f"{pulse_detalhes.get('saldo_ponderado', 0)}"
        )

        print(
            "Nota de desempenho:        "
            f"{pulse_detalhes.get('nota_desempenho', 0)}"
        )

        print(
            "Nota de saldo:             "
            f"{pulse_detalhes.get('nota_saldo', 0)}"
        )

        print(
            "Nota de tendência:         "
            f"{pulse_detalhes.get('nota_tendencia', 0)}"
        )

        print(
            "Tendência de pontos:       "
            f"{pulse_detalhes.get('tendencia_pontos', 0)}"
        )

        print(
            "Tendência de saldo:        "
            f"{pulse_detalhes.get('tendencia_saldo', 0)}"
        )

        print(
            "Pulse Score final:         "
            f"{pulse_detalhes.get('pulse_score', 0)}"
        )

        print(
            "Classificação da tendência: "
            f"{pulse_detalhes.get('tendencia', '-')}"
        )

    def _mostrar_detalhes_erro(self, detalhes):
        print("\nDETALHES DOS MOTORES")
        print("-" * 60)

        for nome_motor, resultado_motor in detalhes.items():

            if not isinstance(resultado_motor, dict):
                continue

            if resultado_motor.get("erro"):
                print(
                    f"{nome_motor.upper()}: "
                    f"{resultado_motor['erro']}"
                )

            if nome_motor == "home_away":
                casa = resultado_motor.get("casa", {})
                fora = resultado_motor.get("fora", {})

                if casa.get("erro"):
                    print(
                        "HOME/AWAY CASA: "
                        f"{casa['erro']}"
                    )

                if fora.get("erro"):
                    print(
                        "HOME/AWAY FORA: "
                        f"{fora['erro']}"
                    )

    def _verificar_alertas(
        self,
        rating,
        forma,
        pulse,
        home_away,
        opponent
    ):
        alertas = []

        if rating == 0:
            alertas.append(
                "O Rating Engine retornou 0."
            )

        if forma == 0:
            alertas.append(
                "O Form Engine retornou 0."
            )

        if pulse == 0:
            alertas.append(
                "O Pulse Engine retornou 0."
            )

        if home_away == 0:
            alertas.append(
                "O Home/Away Engine retornou 0."
            )

        if opponent == 0:
            alertas.append(
                "O Opponent Strength Engine retornou 0."
            )

        notas = [
            rating,
            forma,
            pulse,
            home_away,
            opponent
        ]

        diferenca = max(notas) - min(notas)

        if diferenca >= 50:
            alertas.append(
                "Existe uma diferença superior a 50 pontos "
                "entre os motores."
            )

        if pulse < 20 and rating >= 50:
            alertas.append(
                "O Pulse está muito abaixo do Rating."
            )

        if alertas:
            print("\nALERTAS")
            print("-" * 60)

            for alerta in alertas:
                print(f"- {alerta}")

        else:
            print(
                "\nNenhuma inconsistência evidente encontrada."
            )

    def _mostrar_resumo_geral(self, resultados):
        print("\n" + "=" * 75)
        print("RESUMO GERAL DA VALIDAÇÃO")
        print("=" * 75)

        print(
            f"{'TIME':<28}"
            f"{'SCORE':>12}"
            f"{'CATEGORIA':>25}"
        )

        print("-" * 75)

        for item in resultados:
            nome = item["nome"]
            resultado = item["resultado"]

            if resultado.get("erro"):
                score_formatado = "ERRO"
                categoria = "Não calculado"

            else:
                score = resultado.get(
                    "intelligence_score",
                    0
                )

                score_formatado = f"{score:.2f}"

                categoria = resultado.get(
                    "categoria_intelligence",
                    "-"
                )

            print(
                f"{nome:<28}"
                f"{score_formatado:>12}"
                f"{categoria:>25}"
            )

        print("=" * 75)


if __name__ == "__main__":
    print(
        "O engine_validator.py deve ser executado "
        "através do main.py."
    )