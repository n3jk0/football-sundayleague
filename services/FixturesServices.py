import docx2txt
from io import BytesIO
import re
from sundayleagueApp.models import *
import datetime
from os import walk
from difflib import SequenceMatcher

ROUND_THRESHOLD = 65
LEAGUE_THRESHOLD = 200
TEAM_NAME_SIMILARITY = 0.75

MATCH_HOURS = ['8:30', '9:40', '10:50', '12:00', '13:10', '14:20']


# todo: more seasons
def get_fixtures_text():
    for _, dirfile, files in walk('media/'):
        for file in files:
            if str(file).startswith('razpored'):
                file_name = 'media/' + file
                with open(file_name, 'rb') as f:
                    print("Start reading file", file_name)
                    doc = BytesIO(f.read())
                    text = docx2txt.process(doc)
                    text = re.sub(r'[\n\t]+', '\n', text)
                    text = re.sub(r'Š', 'S', text)
                    text = re.sub(r'Ž', 'Z', text)
                    text = re.sub(r'Č', 'C', text)
                    text = re.sub(r'–', '-', text)
                    return text
    return ""


def save_teams():
    fixtures_text = get_fixtures_text()
    teams = re.findall('[0-9]+[\.][\n][1-9]*[A-Z -]+[0-9]*', fixtures_text)
    [Team.objects.get_or_create(name=team.split("\n")[1]) for team in teams]
    return "DONE"


def find_almost_same_name(all_team_names, team_name):
    for name in all_team_names:
        r = SequenceMatcher(a=name, b=team_name).ratio()
        # print(name, team_name, r)
        if r > TEAM_NAME_SIMILARITY:
            return name
    # print("NOT FOUND", team_name)
    return ""


def save_rounds():
    fixtures_text = get_fixtures_text()
    rounds_blocks = re.findall("[0-9]+\.[ ]*KROG[\n].*[\n].*[\n].*[\n].*[\n].*", fixtures_text)
    prev_round = -1
    current_league = 1
    team_names = [team.name for team in Team.objects.all()]
    for i, block in enumerate(rounds_blocks):
        lines = block.split("\n")
        round_number = int(re.findall("[0-9]+", lines[0])[0])
        if round_number < prev_round:
            current_league += 1
        date = datetime.datetime.strptime(lines[1], '%d.%m.%Y')
        team_name = find_almost_same_name(team_names, lines[3])
        home_team = Team.objects.get(name=team_name)
        Round.objects.get_or_create(round_number=round_number, place=lines[5], date=date, league_number=current_league,
                                    home_team=home_team)

        prev_round = round_number
    return "DONE"


def save_matches():
    fixtures_text = get_fixtures_text()
    matches_blocks = re.findall("[0-9A-Z -.]*[\n]:[\n][0-9A-Z -.]*[\n]:", fixtures_text)
    prev_index = fixtures_text.index(matches_blocks[0])
    round_num = 1
    time_id = 0
    current_league = 1
    team_names = [team.name for team in Team.objects.all()]
    for i, match in enumerate(matches_blocks):
        index = fixtures_text.index(match, prev_index)
        if index - prev_index > LEAGUE_THRESHOLD:
            current_league += 1
            # increased in next if
            round_num = 0

        if index - prev_index > ROUND_THRESHOLD:
            time_id = 0
            round_num += 1
        prev_index = index
        match = re.sub(r'\n', '', match)
        match_split = match.split(":")

        first_team_name = find_almost_same_name(team_names, match_split[0])
        first_team = Team.objects.get(name=first_team_name)
        second_team_name = find_almost_same_name(team_names, match_split[1])
        second_team = Team.objects.get(name=second_team_name)
        time = datetime.datetime.strptime(MATCH_HOURS[time_id], '%H:%M')
        print(round_num, current_league, first_team_name, second_team_name)
        football_round = Round.objects.get(round_number=round_num, league_number=current_league)

        Match.objects.get_or_create(first_team=first_team, second_team=second_team, time=time, round=football_round)
        time_id += 1

    return "DONE"
