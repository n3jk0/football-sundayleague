from io import BytesIO
import docx2txt
import re, logging


def read_file(file):
    with file.file_content.open(mode='rb') as f:
        logging.info("Start reading file: {}".format(file.file_content.name))
        doc = BytesIO(f.read())
        text = docx2txt.process(doc)
        text = preprocess(text)

        file.already_read = True
        file.text_content = text
        file.save()

        logging.info("File {} read.".format(file.file_content.name))
        return text


def preprocess(text):
    text = re.sub(r'[\n\t]+', '\n', text)
    text = re.sub(r'–', '-', text)
    return text
