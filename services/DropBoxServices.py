# Include the Dropbox SDK
import dropbox
import docx2txt
from io import BytesIO
import re
from model.Team import Team
from model.Round import RoundRow
from model.Match import Match
import json

SEASON_DATA_PATH = '/data/season19_20/data/'
SEASON_METADATA_PATH = '/data/season19_20/metadata/'
SEASON_DIV1_PATH = '/data/season19_20/div1'
SEASON_DIV2_PATH = '/data/season19_20/div2'
SEASON_DIV3_PATH = '/data/season19_20/div3'
SEASON_DIV4_PATH = '/data/season19_20/div4'

ROUND_THRESHOLD = 65
LEAGUE_THRESHOLD = 200

MATCH_HOURS = ['8:30', '9:40', '10:50', '12:00', '13:10', '14:20']

code = 'RIP4CxhBtsUAAAAAAAAB0y49pGha3C22-hOFE2MvTrnPOZFzuFbCeLKkfAuQruIj'


def create_teams_file(teams, dbx):
    payload = {
        'teams': [Team(i, team.split("\n")[1]).__dict__ for i, team in enumerate(teams)],
    }
    update_file("teams.json", dbx, payload)


def create_rounds_file(hosts, dbx):
    update_file("rounds.json", dbx, hosts)


def create_matches_file(matches, dbx):
    update_file("matches.json", dbx, matches)


def update_file(file_name, dbx, payload):
    with open(file_name, 'w') as file:
        json.dump(payload, file)
    with open(file_name, 'rb') as file:
        path_to_file = SEASON_METADATA_PATH + file_name
        try:
            dbx.files_delete(path_to_file)
            print("File " + path_to_file + " is removed.")
        except:
            print("File " + path_to_file + " doesn't exist.")
        dbx.files_upload(file.read(), path_to_file, mute=True)
        print("File " + path_to_file + " is saved.")


def get_rounds(fixtures_text):
    rounds_blocks = re.findall("[0-9]+\.[ ]*KROG[\n].*[\n].*[\n].*[\n].*[\n].*", fixtures_text)
    prev_round = -1
    current_league = 1
    rounds = {}
    rows = []
    for i, block in enumerate(rounds_blocks):
        lines = block.split("\n")
        round_number = int(re.findall("[0-9]+", lines[0])[0])
        if round_number < prev_round:
            rounds["div" + str(current_league)] = rows
            current_league += 1
            rows = []
        row = RoundRow(i, current_league, round_number, lines[3], lines[5], lines[1]).__dict__
        rows.append(row)
        prev_round = round_number
    rounds["div" + str(current_league)] = rows
    return rounds


def get_matches(fixtures_text):
    matches_blocks = re.findall("[0-9A-Z -.]*[\n]:[\n][0-9A-Z -.]*[\n]:", fixtures_text)
    prev_index = fixtures_text.index(matches_blocks[0])
    round_num = 0
    time_id = 0
    current_league = 1
    matches = {}
    matches_league = []
    for i, match in enumerate(matches_blocks):
        index = fixtures_text.index(match, prev_index)
        if index - prev_index > LEAGUE_THRESHOLD:
            matches["div" + str(current_league)] = matches_league
            matches_league = []
            current_league += 1

        if index - prev_index > ROUND_THRESHOLD:
            time_id = 0
            round_num += 1
        prev_index = index
        match = re.sub(r'\n', '', match)
        match_split = match.split(":")
        matches_league.append(Match(i, round_num, match_split[0], match_split[1], MATCH_HOURS[time_id]).__dict__)
        time_id += 1
    matches["div" + str(current_league)] = matches_league

    return matches


def preprocess_doc_file(file_name):
    _, res = dbx.files_download(SEASON_DATA_PATH + file_name)
    doc = BytesIO(res.content)
    text = docx2txt.process(doc)
    text = re.sub(r'[\n\t]+', '\n', text)
    text = re.sub(r'Š', 'S', text)
    text = re.sub(r'Ž', 'Z', text)
    text = re.sub(r'Č', 'C', text)
    text = re.sub(r'–', '-', text)
    return text


def get_teams(fixtures_text):
    return re.findall('[0-9]+[\.][\n][1-9]*[A-Z -]+[0-9]*', fixtures_text)


dbx = dropbox.Dropbox(code)
folders = dbx.files_list_folder(SEASON_DATA_PATH)

file_names = [e.name for e in folders.entries]

for file_name in file_names:
    if file_name.startswith('razpored'):
        fixtures_text = preprocess_doc_file(file_name)
        # -----------TEAMS data--------------------
        teams = get_teams(fixtures_text)
        # create_teams_file(teams, dbx)
        # -----------HOSTS data--------------------
        rounds = get_rounds(fixtures_text)
        # create_rounds_file(rounds, dbx)
        # -----------MATCHES data------------------
        matches = get_matches(fixtures_text)
        # create_matches_file(matches, dbx)

    else:
        print('File ' + file_name + " is not implemented yet.")
