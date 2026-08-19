from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional


class DatasetEngine:
    """
    Prepara, valida e indexa partidas no formato da API-Football.

    Responsabilidades:
    - normalizar a entrada do dataset;
    - manter somente partidas válidas;
    - ordenar partidas cronologicamente;
    - separar partidas encerradas e não encerradas;
    - indexar partidas por equipe;
    - entregar históricos anteriores a uma partida sem vazamento de dados.
    """

    STATUS_ENCERRADOS = {"FT", "AET", "PEN"}

    def __init__(self, dados: Any):
        self.dados_brutos = dados
        self.partidas: List[Dict[str, Any]] = []
        self.partidas_encerradas: List[Dict[str, Any]] = []
        self.partidas_nao_encerradas: List[Dict[str, Any]] = []
        self._indice_por_time: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
        self._indice_posicao_fixture: Dict[int, int] = {}
        self._erros: List[str] = []
        self._preparar()

    @staticmethod
    def _extrair_lista_partidas(dados: Any) -> List[Dict[str, Any]]:
        if isinstance(dados, list):
            return dados
        if isinstance(dados, dict):
            response = dados.get("response")
            if isinstance(response, list):
                return response
        raise ValueError(
            "O dataset deve ser uma lista de partidas ou um dicionário "
            "contendo a chave 'response' com uma lista."
        )

    @staticmethod
    def _obter_fixture_id(partida: Dict[str, Any]) -> Optional[int]:
        fixture_id = partida.get("fixture", {}).get("id")
        try:
            return int(fixture_id)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _obter_data(partida: Dict[str, Any]) -> Optional[datetime]:
        fixture = partida.get("fixture", {})
        timestamp = fixture.get("timestamp")
        if timestamp is not None:
            try:
                return datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
            except (TypeError, ValueError, OSError):
                pass

        data_texto = fixture.get("date")
        if not data_texto:
            return None
        try:
            data = datetime.fromisoformat(str(data_texto).replace("Z", "+00:00"))
            if data.tzinfo is None:
                data = data.replace(tzinfo=timezone.utc)
            return data.astimezone(timezone.utc)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _obter_status(partida: Dict[str, Any]) -> Optional[str]:
        short = partida.get("fixture", {}).get("status", {}).get("short")
        return str(short).upper().strip() if short is not None else None

    @staticmethod
    def _obter_times(partida: Dict[str, Any]) -> tuple[Optional[int], Optional[int]]:
        teams = partida.get("teams", {})
        try:
            home_id = int(teams.get("home", {}).get("id"))
        except (TypeError, ValueError):
            home_id = None
        try:
            away_id = int(teams.get("away", {}).get("id"))
        except (TypeError, ValueError):
            away_id = None
        return home_id, away_id

    @classmethod
    def _partida_valida(cls, partida: Any) -> tuple[bool, str]:
        if not isinstance(partida, dict):
            return False, "Partida não é um dicionário."
        fixture_id = cls._obter_fixture_id(partida)
        if fixture_id is None:
            return False, "Partida sem fixture.id válido."
        if cls._obter_data(partida) is None:
            return False, f"Fixture {fixture_id} sem data válida."
        home_id, away_id = cls._obter_times(partida)
        if home_id is None or away_id is None:
            return False, f"Fixture {fixture_id} sem IDs válidos dos times."
        if home_id == away_id:
            return False, f"Fixture {fixture_id} possui o mesmo time nos dois lados."
        return True, ""

    def _preparar(self) -> None:
        lista = self._extrair_lista_partidas(self.dados_brutos)
        fixture_ids = set()
        partidas_validas = []

        for indice, partida in enumerate(lista):
            valida, motivo = self._partida_valida(partida)
            if not valida:
                self._erros.append(f"Índice {indice}: {motivo}")
                continue
            fixture_id = self._obter_fixture_id(partida)
            if fixture_id in fixture_ids:
                self._erros.append(f"Índice {indice}: fixture duplicada {fixture_id}.")
                continue
            fixture_ids.add(fixture_id)
            partidas_validas.append(deepcopy(partida))

        partidas_validas.sort(
            key=lambda jogo: (self._obter_data(jogo), self._obter_fixture_id(jogo))
        )
        self.partidas = partidas_validas

        for posicao, partida in enumerate(self.partidas):
            fixture_id = self._obter_fixture_id(partida)
            status = self._obter_status(partida)
            home_id, away_id = self._obter_times(partida)
            self._indice_posicao_fixture[fixture_id] = posicao
            self._indice_por_time[home_id].append(partida)
            self._indice_por_time[away_id].append(partida)
            if status in self.STATUS_ENCERRADOS:
                self.partidas_encerradas.append(partida)
            else:
                self.partidas_nao_encerradas.append(partida)

    def resumo(self) -> Dict[str, Any]:
        return {
            "total_recebido": len(self._extrair_lista_partidas(self.dados_brutos)),
            "total_validas": len(self.partidas),
            "total_encerradas": len(self.partidas_encerradas),
            "total_nao_encerradas": len(self.partidas_nao_encerradas),
            "total_times_indexados": len(self._indice_por_time),
            "total_erros": len(self._erros),
            "erros": self._erros.copy(),
        }

    def obter_partidas(self, somente_encerradas: bool = False) -> List[Dict[str, Any]]:
        origem = self.partidas_encerradas if somente_encerradas else self.partidas
        return deepcopy(origem)

    def obter_partidas_do_time(
        self,
        team_id: int,
        somente_encerradas: bool = False,
    ) -> List[Dict[str, Any]]:
        try:
            team_id = int(team_id)
        except (TypeError, ValueError) as exc:
            raise ValueError("team_id deve ser um número inteiro.") from exc

        partidas = self._indice_por_time.get(team_id, [])
        if somente_encerradas:
            partidas = [
                partida
                for partida in partidas
                if self._obter_status(partida) in self.STATUS_ENCERRADOS
            ]
        return deepcopy(partidas)

    def obter_historico_anterior(
        self,
        team_id: int,
        fixture_id: int,
        janela: Optional[int] = None,
        somente_encerradas: bool = True,
    ) -> List[Dict[str, Any]]:
        """Retorna somente jogos anteriores à fixture informada."""
        try:
            team_id = int(team_id)
            fixture_id = int(fixture_id)
        except (TypeError, ValueError) as exc:
            raise ValueError("team_id e fixture_id devem ser números inteiros.") from exc

        if fixture_id not in self._indice_posicao_fixture:
            raise ValueError(f"A fixture {fixture_id} não existe no dataset preparado.")

        posicao_limite = self._indice_posicao_fixture[fixture_id]
        historico = []
        for partida in self._indice_por_time.get(team_id, []):
            partida_id = self._obter_fixture_id(partida)
            if self._indice_posicao_fixture[partida_id] >= posicao_limite:
                continue
            if somente_encerradas and self._obter_status(partida) not in self.STATUS_ENCERRADOS:
                continue
            historico.append(partida)

        if janela is not None:
            if not isinstance(janela, int) or janela <= 0:
                raise ValueError("janela deve ser um número inteiro maior que zero.")
            historico = historico[-janela:]
        return deepcopy(historico)

    def obter_contexto_partida(self, fixture_id: int, janela: int = 5) -> Dict[str, Any]:
        try:
            fixture_id = int(fixture_id)
        except (TypeError, ValueError) as exc:
            raise ValueError("fixture_id deve ser um número inteiro.") from exc

        posicao = self._indice_posicao_fixture.get(fixture_id)
        if posicao is None:
            raise ValueError(f"A fixture {fixture_id} não existe no dataset preparado.")

        partida = self.partidas[posicao]
        home_id, away_id = self._obter_times(partida)
        return {
            "partida": deepcopy(partida),
            "mandante_id": home_id,
            "visitante_id": away_id,
            "historico_mandante": self.obter_historico_anterior(
                home_id, fixture_id, janela, True
            ),
            "historico_visitante": self.obter_historico_anterior(
                away_id, fixture_id, janela, True
            ),
        }

    def iterar_partidas_backtest(
        self,
        minimo_jogos_anteriores: int = 5,
    ) -> Iterable[Dict[str, Any]]:
        if not isinstance(minimo_jogos_anteriores, int) or minimo_jogos_anteriores < 1:
            raise ValueError("minimo_jogos_anteriores deve ser inteiro e maior que zero.")

        for partida in self.partidas_encerradas:
            fixture_id = self._obter_fixture_id(partida)
            contexto = self.obter_contexto_partida(
                fixture_id=fixture_id,
                janela=minimo_jogos_anteriores,
            )
            if len(contexto["historico_mandante"]) < minimo_jogos_anteriores:
                continue
            if len(contexto["historico_visitante"]) < minimo_jogos_anteriores:
                continue
            yield contexto