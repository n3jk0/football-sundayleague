import docx2txt
from io import BytesIO
import re
from sundayleagueApp.models import *
from services.common_service import *
import datetime
import logging
from os import walk
from difflib import SequenceMatcher

ROUND_THRESHOLD = 65
LEAGUE_THRESHOLD = 200
TEAM_NAME_SIMILARITY = 0.7

MATCH_HOURS = ['8:30', '9:40', '10:50', '12:00', '13:10', '14:20']


# todo: more seasons
def get_fixtures_text():
    files = File.objects.filter(is_fixture=True, already_read=False).all()
    for file in files:
        return file.text_content if bool(file.text_content) else read_file(file)
    logging.error("No fixtures files was found.")
    return ""


def get_fixtures_text_by_id(file_id):
    file = File.objects.filter(is_fixture=True, id=file_id)
    if file.exists():
        file = file.first()
    else:
        logging.error("File {} doesn't exists.".format(file_id))
        return None
    return file.text_content if bool(file.text_content) else read_file(file)


def save_teams(fixtures_text=""):
    if not fixtures_text:
        fixtures_text = get_fixtures_text()
    teams = re.findall('[0-9]+[\.][\n][0-9]*[A-Ž -]+[0-9A-Ž]*', fixtures_text)
    # Added [0] to return only saved object (without created flag)
    saved_teams = [Team.objects.get_or_create(name=team.split("\n")[1])[0] for team in teams]
    logging.debug("Teams {} found or saved.".format(saved_teams))
    return saved_teams


def find_almost_same_name(all_team_names, team_name):
    for name in all_team_names:
        r = SequenceMatcher(a=name, b=team_name).ratio()
        if r > TEAM_NAME_SIMILARITY:
            return name
    return ""


def save_rounds(fixtures_text=""):
    if not fixtures_text:
        fixtures_text = get_fixtures_text()
    rounds_blocks = re.findall("[0-9]+\.[ ]*KROG[\n].*[\n].*[\n].*[\n].*[\n].*", fixtures_text)
    prev_round = -1
    current_league = 1
    team_names = [team.name for team in Team.objects.all()]
    logging.debug("Start saving rounds from fixture file.")
    for i, block in enumerate(rounds_blocks):
        lines = block.split("\n")
        logging.debug("Round data: {}".format(lines))
        round_number = int(re.findall("[0-9]+", lines[0])[0])
        if round_number < prev_round:
            logging.debug("League number changed from {} to {}".format(current_league, current_league + 1))
            current_league += 1
        date = datetime.datetime.strptime(lines[1], '%d.%m.%Y')
        team_name = find_almost_same_name(team_names, lines[3])
        home_team = Team.objects.get(name=team_name)
        round, created = Round.objects.get_or_create(round_number=round_number, league_number=current_league,
                                                     defaults={'date': date, 'home_team': home_team, 'place': lines[5]})
        if not created:
            round.place = lines[5]
            round.date = date
            round.home_team = home_team
            round.save()
            logging.info("Round {} for league {} already exists. Place, date and home_team was changed.".format(round_number, current_league))
        logging.info("Round: {} saved.".format(round))
        prev_round = round_number
    return "DONE"


def save_matches(fixtures_text=""):
    if not fixtures_text:
        fixtures_text = get_fixtures_text()
    matches_blocks = re.findall("[0-9A-Ž -.]*[\n]:[\n][0-9A-Ž -.]*[\n]:", fixtures_text)
    prev_index = fixtures_text.index(matches_blocks[0])
    round_num = 1
    time_id = 0
    current_league = 1
    team_names = [team.name for team in Team.objects.all()]
    logging.debug("Saving matches from fixture file.")
    # TODO: Rewrite code without LEAGUE_THRESHOLD and ROUND_THRESHOLD
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
        logging.debug("Match data: {}".format(match_split))

        first_team_name = find_almost_same_name(team_names, match_split[0])
        first_team = Team.objects.get(name=first_team_name)
        if first_team.league < 1:
            first_team.league = current_league
            first_team.save()

        second_team_name = find_almost_same_name(team_names, match_split[1])
        second_team = Team.objects.get(name=second_team_name)
        if second_team.league < 1:
            second_team.league = current_league
            second_team.save()

        time = datetime.datetime.strptime(MATCH_HOURS[time_id], '%H:%M')
        football_round = Round.objects.get(round_number=round_num, league_number=current_league)
        logging.debug("Round {} found.".format(football_round))

        m, created = Match.objects.get_or_create(first_team=first_team, second_team=second_team, time=time, round=football_round)
        logging.info("Match {} {}.".format(m, "saved" if created else "already exists"))
        time_id += 1

    return "DONE"


def save_fixtures():
    fixtures_text = get_fixtures_text()
    saved_teams = save_teams(fixtures_text)
    logging.info("{} teams was saved.".format(len(saved_teams)))
    save_rounds(fixtures_text)
    save_matches(fixtures_text)

def save_fixtures_for_file(file_id=-1):
    fixtures_text = get_fixtures_text_by_id(file_id)
    saved_teams = save_teams(fixtures_text)
    logging.info("{} teams was saved.".format(len(saved_teams)))
    save_rounds(fixtures_text)
    save_matches(fixtures_text)
    return True
