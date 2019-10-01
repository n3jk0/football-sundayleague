# Include the Dropbox SDK
import dropbox
import docx2txt
from io import BytesIO
import re
import model.Team as Team


def create_teams_file(teams):
    for i, team in teams:
        Team(i, team.split("\n")[1])


SEASON_DATA_PATH = '/data/season19_20/data'
SEASON_DIV1_PATH = '/data/season19_20/div1'
SEASON_DIV2_PATH = '/data/season19_20/div2'
SEASON_DIV3_PATH = '/data/season19_20/div3'
SEASON_DIV4_PATH = '/data/season19_20/div4'

code = 'RIP4CxhBtsUAAAAAAAAB0y49pGha3C22-hOFE2MvTrnPOZFzuFbCeLKkfAuQruIj'

dbx = dropbox.Dropbox(code)
folders = dbx.files_list_folder(SEASON_DATA_PATH)
file_names = [e.name for e in folders.entries]

_, res = dbx.files_download(SEASON_DATA_PATH + "/razpored RNL JESEN 2019 20.docx")
doc = BytesIO(res.content)
text = docx2txt.process(doc)
text = re.sub(r'[\n\t]+', '\n', text)
text = re.sub(r'Š', 'S', text)
text = re.sub(r'Ž', 'Z', text)
text = re.sub(r'Č', 'C', text)
teams = re.findall('[0-9]+[\.][\n][1-9]*[A-Z -]+[0-9]*', text)
# for line in text.splitlines():
#     print(line)
print(text)
