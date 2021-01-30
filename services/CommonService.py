from io import BytesIO
import docx2txt
import re


def read_file(file):
    with file.file_content.open(mode='rb') as f:
        print("Start reading file", file.file_content.name)
        doc = BytesIO(f.read())
        text = docx2txt.process(doc)
        text = preprocess(text)

        file.already_read = True
        file.text_content = text
        file.save()
        return text


def preprocess(text):
    text = re.sub(r'[\n\t]+', '\n', text)
    text = re.sub(r'Š', 'S', text)
    text = re.sub(r'Ž', 'Z', text)
    text = re.sub(r'Č', 'C', text)
    text = re.sub(r'–', '-', text)
    return text
