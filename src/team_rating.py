from dataclasses import dataclass


@dataclass
class TeamRating:

    nome: str

    ataque: float

    defesa: float

    forma: float

    casa: float

    fora: float

    rating: float

    categoria: str