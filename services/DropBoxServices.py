# Include the Dropbox SDK
import dropbox
import docx2txt
from io import BytesIO
import re
from model.Team import Team
from model.Host import HostRow
import json

SEASON_DATA_PATH = '/data/season19_20/data/'
SEASON_METADATA_PATH = '/data/season19_20/metadata/'
SEASON_DIV1_PATH = '/data/season19_20/div1'
SEASON_DIV2_PATH = '/data/season19_20/div2'
SEASON_DIV3_PATH = '/data/season19_20/div3'
SEASON_DIV4_PATH = '/data/season19_20/div4'

code = 'RIP4CxhBtsUAAAAAAAAB0y49pGha3C22-hOFE2MvTrnPOZFzuFbCeLKkfAuQruIj'


def create_teams_file(teams, dbx):
    payload = {
        'teams': [Team(i, team.split("\n")[1]).__dict__ for i, team in enumerate(teams)],
    }
    update_file("teams.json", dbx, payload)


def create_hosts_file(hosts, dbx):
    update_file("hosts.json", dbx, hosts)


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


def get_hosts(schedule_text):
    hosts_blocks = re.findall("[0-9]+\.[ ]*KROG[\n].*[\n].*[\n].*[\n].*[\n].*", schedule_text)
    prev_round = -1
    current_league = 1
    hosts = {}
    rows = []
    for i, block in enumerate(hosts_blocks):
        lines = block.split("\n")
        round_number = int(re.findall("[0-9]+", lines[0])[0])
        row = HostRow(i, round_number, lines[3], lines[5], lines[1]).__dict__
        if round_number < prev_round:
            hosts["div" + str(current_league)] = rows
            current_league += 1
            rows = []
        rows.append(row)
        prev_round = round_number
    hosts["div" + str(current_league)] = rows
    return hosts


def preprocess_doc_file(file_name):
    _, res = dbx.files_download(SEASON_DATA_PATH + file_name)
    doc = BytesIO(res.content)
    text = docx2txt.process(doc)
    text = re.sub(r'[\n\t]+', '\n', text)
    text = re.sub(r'Š', 'S', text)
    text = re.sub(r'Ž', 'Z', text)
    text = re.sub(r'Č', 'C', text)
    return text


def get_teams_from_schedule(schedule_text):
    return re.findall('[0-9]+[\.][\n][1-9]*[A-Z -]+[0-9]*', schedule_text)


dbx = dropbox.Dropbox(code)
folders = dbx.files_list_folder(SEASON_DATA_PATH)

file_names = [e.name for e in folders.entries]

# todo: iterate trough file_names
for file_name in file_names:
    if file_name.startswith('razpored'):
        schedule_text = preprocess_doc_file(file_name)
        teams = get_teams_from_schedule(schedule_text)
        # create_teams_file(teams, dbx)
        hosts = get_hosts(schedule_text)
        create_hosts_file(hosts, dbx)
    else:
        print('File ' + file_name + " is not implemented yet.")
# for line in text.splitlines():
#     print(line)
# print(text)
