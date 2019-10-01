class LeagueTable:
    def __init__(self, league_id, league_name, table_rows):
        self.league_id = league_id
        self.league_name = league_name
        self.table_rows = table_rows


class TableRows:
    def __init__(self, position, team_id, played, wins, draws, lost, goals_for, goals_against, goal_dif, points):
        self.position = position
        self.team_id = team_id
        self.played = played
        self.wins = wins
        self.draws = draws
        self.lost = lost
        self.goals_for = goals_for
        self.goals_against = goals_against
        self.goal_dif = goal_dif
        self.points = points
