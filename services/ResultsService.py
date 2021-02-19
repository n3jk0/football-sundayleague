import docx2txt
from io import BytesIO
import re

from services.CommonService import *
from services.FixturesService import find_almost_same_name
from sundayleagueApp.models import *

ROUND_THRESHOLD = 65
LEAGUE_THRESHOLD = 200
TEAM_NAME_SIMILARITY = 0.7


def get_results_text():
    files = File.objects.filter(already_read=False, is_fixture=False).all()
    for file in files:
        return file.text_content if bool(file.text_content) else read_file(file)
    return ""


def get_results_text_by_id(file_id):
    file = File.objects.filter(is_fixture=False, id=file_id)
    if file.exists():
        file = file.first()
    else:
        print("File", file_id, "doesn't exists.")
        return None

    return file.text_content if bool(file.text_content) else read_file(file)


def save_results():
    results_text = get_results_text()
    saved_results = []
    while results_text:
        saved_results.append(save_result_from_text(results_text))
        save_information(results_text)
        results_text = get_results_text()
    return saved_results


def save_result_from_text(results_text):
    league_indexes = [m.start() for m in re.finditer('TRAVNA LIGA', results_text)]
    team_names = [team.name for team in Team.objects.all()]
    league_num = 1
    saved_results = []
    for i in range(len(league_indexes)):
        if i + 1 >= len(league_indexes):
            league_block = results_text[league_indexes[i]:]
        else:
            league_block = results_text[league_indexes[i]:league_indexes[i + 1]]

        rounds_indexes = [m.start() for m in re.finditer('[0-9. ]+KROG', league_block)]
        for j in range(len(rounds_indexes)):
            if j + 1 >= len(rounds_indexes):
                round_block = league_block[rounds_indexes[j]:]
            else:
                round_block = league_block[rounds_indexes[j]:rounds_indexes[j + 1]]
            # find number in first line
            round_num = int(re.findall('[0-9]+', round_block.split("\n")[0])[0])
            r = Round.objects.get(round_number=round_num, league_number=league_num)
            results_for_round = re.findall("[0-9A-Z -.]+\n:\n[0-9A-Z -.]+\n[0-9]+:[0-9]+[(b.b.)]*", round_block)
            for result_per_round in results_for_round:
                lines = result_per_round.split("\n")
                matches_in_round = Match.objects.filter(round=r)
                first_team = Team.objects.get(name=find_almost_same_name(team_names, lines[0]))
                second_team = Team.objects.get(name=find_almost_same_name(team_names, lines[2]))
                match = matches_in_round.get(first_team=first_team, second_team=second_team)
                result = re.split(':', lines[3])
                match.first_team_score = result[0]
                if str(result[1]).endswith('(b.b.)'):
                    match.is_surrendered = True
                    result[1] = result[1].split('(b.b.)')[0]
                match.second_team_score = result[1]
                saved_results.append(match)
                match.status = Match.MatchStatus.CONFIRMED
                match.save()
        league_num += 1
    return saved_results


def save_results_for_file(file_id):
    results_text = get_results_text_by_id(file_id)
    if not results_text:
        return []
    save_information(results_text)
    return save_result_from_text(results_text)


def update_table():
    matches = Match.objects.exclude(first_team_score__isnull=True).exclude(second_team_score__isnull=True).all()
    if len(matches) < 1:
        empty_table()
        return {}

    matches_grouped_by_team = {}
    for m in matches:
        matches_grouped_by_team.setdefault(m.first_team_id, []).append(m)
        matches_grouped_by_team.setdefault(m.second_team_id, []).append(m)
    teams = Team.objects.all()

    response = {}

    for team in teams:
        row, created = TableRow.objects.get_or_create(team=team)
        # clean
        if not created:
            row.match_played = 0
            row.wins = 0
            row.losses = 0
            row.draws = 0
            row.goals_against = 0
            row.goals_for = 0
            row.points = 0
            row.penalty_points = 0
        else:
            row.team = team
            row.league = team.league

        matches_for_team = matches_grouped_by_team.get(team.id)
        if matches_for_team is None:
            row.save()
            continue
        for match in matches_for_team:
            if match.first_team_id == team.id:
                res = match.first_team_score - match.second_team_score
                row.goals_for += match.first_team_score
                row.goals_against += match.second_team_score
            elif match.second_team_id == team.id:
                res = match.second_team_score - match.first_team_score
                row.goals_for += match.second_team_score
                row.goals_against += match.first_team_score
            else:
                print("Shouldn't get there ({})".format(team))
                return

            row.match_played += 1
            # res > 0 win ; res == 0 draw ; res < 0 loss
            if res > 0:
                row.wins += 1
                row.points += 3
            elif res < 0:
                row.losses += 1
            else:
                row.draws += 1
                row.points += 1
            # penalty points
            if match.is_surrendered and res < 0:
                if row.penalty_points == 0:
                    row.penalty_points = -1
                elif row.penalty_points == -1:
                    row.penalty_points = -3
        row.points += row.penalty_points
        row.save()
    return response


def empty_table():
    teams = Team.objects.all()
    for team in teams:
        row, created = TableRow.objects.get_or_create(team=team, league=team.league)
        print(row, created)
        # clean
        if not created:
            row.match_played = 0
            row.wins = 0
            row.losses = 0
            row.draws = 0
            row.goals_against = 0
            row.goals_for = 0
            row.points = 0
            row.penalty_points = 0
        else:
            row.team = team
            row.league = team.league

        row.points += row.penalty_points
        row.save()


def save_information(results_text):
    information_index = [m.start() for m in re.finditer('Obvestila', results_text)]
    for i in information_index:
        info_text = results_text[i:]

        # todo: temp solution
        end_index = info_text.index("Rekreacijska liga v nogometu")
        info_text = info_text[:end_index]

        info_text = info_text.replace("Obvestila:", "")
        info_text = info_text.replace("\n", "\n\n")
        info_text = info_text.strip()
        information = Information(info=info_text)
        information.save()

