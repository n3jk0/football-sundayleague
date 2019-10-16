from os import walk
import docx2txt
from io import BytesIO
import re

from services.FixturesServices import find_almost_same_name
from sundayleagueApp.models import *
import datetime

ROUND_THRESHOLD = 65
LEAGUE_THRESHOLD = 200
TEAM_NAME_SIMILARITY = 0.7


def get_results_text():
    biltens = File.objects.filter(already_read=False, round_number__gt=0)
    biltens_names = [bilten.file_content.name for bilten in biltens]
    # for _, dirfile, files in walk('../media/'):
    for _, dirfile, files in walk('media/'):
        for file in files:
            if file in biltens_names:
                # if file.startswith("bilten"):
                #     file_name = '../media/' + file
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
                    f = File.objects.get(file_content=file)
                    f.already_read = True
                    f.save()
                    return text
    return ""


def get_results():
    results_text = get_results_text()
    while results_text:
        league_indexes = [m.start() for m in re.finditer('TRAVNA LIGA', results_text)]
        team_names = [team.name for team in Team.objects.all()]
        league_num = 1
        for i in range(len(league_indexes)):
            if i + 1 >= len(league_indexes):
                league_block = results_text[league_indexes[i]:]
            else:
                league_block = results_text[league_indexes[i]:league_indexes[i + 1]]

            rounds_indexes = [m.start() for m in re.finditer('[1-9. ]+KROG', league_block)]
            for j in range(len(rounds_indexes)):
                if j + 1 >= len(rounds_indexes):
                    round_block = league_block[rounds_indexes[j]:]
                else:
                    round_block = league_block[rounds_indexes[j]:rounds_indexes[j + 1]]
                # find number in first line
                round_num = int(re.findall('[1-9]+', round_block.split("\n")[0])[0])
                r = Round.objects.get(round_number=round_num, league_number=league_num)
                results_for_round = re.findall("[0-9A-Z -.]+\n:\n[0-9A-Z -.]+\n[0-9]+:[0-9]+", round_block)
                for result_per_round in results_for_round:
                    lines = result_per_round.split("\n")
                    matches_in_round = Match.objects.filter(round=r)
                    first_team = Team.objects.get(name=find_almost_same_name(team_names, lines[0]))
                    second_team = Team.objects.get(name=find_almost_same_name(team_names, lines[2]))
                    match = matches_in_round.get(first_team=first_team, second_team=second_team)
                    result = re.split(':', lines[3])
                    match.first_team_score = result[0]
                    match.second_team_score = result[1]
                    print(match)
                    match.save()
            league_num += 1
        results_text = get_results_text()

    # print(league_indexes)
    # league_blocks = re.findall("[1-9. ]+KROG", results_text)
    # print(results_text)

# print(get_results())
