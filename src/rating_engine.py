from team_rating import TeamRating


class RatingEngine:

    def categoria(self, nota):

        if nota >= 90:
            return "Elite"

        if nota >= 80:
            return "Muito Forte"

        if nota >= 70:
            return "Forte"

        if nota >= 60:
            return "Competitivo"

        if nota >= 50:
            return "Regular"

        return "Em Má Fase"