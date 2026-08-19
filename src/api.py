import requests
from config import API_KEY, BASE_URL


def make_request(endpoint, parameters=None):
    url = f"{BASE_URL}/{endpoint}"

    headers = {
        "x-apisports-key": API_KEY
    }

    response = requests.get(
        url,
        headers=headers,
        params=parameters,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def get_status():
    return make_request("status")


def get_fixtures_by_date(date):
    parameters = {
        "date": date
    }

    return make_request("fixtures", parameters)


def get_team(team_id):
    parameters = {
        "id": team_id
    }

    return make_request("teams", parameters)


def search_team(nome):
    parameters = {
        "search": nome
    }

    return make_request("teams", parameters)


def get_team_season_games(team_id, league_id, season):
    parameters = {
        "team": team_id,
        "league": league_id,
        "season": season
    }

    return make_request("fixtures", parameters)


def get_teams_by_league(league_id, season):
    parameters = {
        "league": league_id,
        "season": season
    }

    return make_request("teams", parameters)


def get_league_season_games(league_id, season):
    parameters = {
        "league": league_id,
        "season": season
    }

    return make_request("fixtures", parameters)