import os
import pickle
import xml.etree.ElementTree as ET

from sentence_transformers import SentenceTransformer


ENCODING_MODEL = 'Qwen/Qwen3-Embedding-0.6B'
DATA_DIRECTORY = os.getcwd() + '/data'
DEBUG = False


def xml_parser(path: str) -> list:
    documents = []
    root = ET.parse(path).getroot()

    for problem in root:
        document = problem[0].text

        for answer in problem[1]:
            if answer.tag == 'answer_text':
                document += f' {answer.text}'
            elif answer.tag == 'answer_list':
                for item in answer:
                    for category in item:
                        document += f' {category.text}'
            else:
                for step in answer:
                    document += f'{step.text}'
        documents.append(document)
    return documents


def csv_parser(path: str) -> list:
    documents = []

    with open(path, 'r') as file:
        categories = file.readline().split(',')
        current = file.readline()

        while current != '':
            document = ''
            current = current.split(',')

            for i in range(len(categories)):
                document += f'{categories[i]} = {current[i]} '

            documents.append(document)
            current = file.readline()
    return documents


def run() -> None:
    model = SentenceTransformer(ENCODING_MODEL)
    documents = []

    for filename in os.listdir(DATA_DIRECTORY + '/xml'):
        documents += xml_parser(DATA_DIRECTORY + '/xml/' + filename)
    
    for filename in os.listdir(DATA_DIRECTORY + '/csv'):
        documents += csv_parser(DATA_DIRECTORY + '/csv/' + filename)
    
    embeddings = model.encode(sentences=documents, prompt_name='document')

    with open('documents', 'w+b') as file:
        pickle.dump(documents, file)
    
    with open('embeddings', 'w+b') as file:
        pickle.dump(embeddings, file)

    if DEBUG:
        for document in documents:
            print(document)
        print(str(len(documents)))


if __name__ == '__main__':
    run()