import numpy as np
import os
import pickle
import xml.etree.ElementTree as ET

from sentence_transformers import SentenceTransformer


ENCODING_MODEL = 'Qwen/Qwen3-Embedding-0.6B'
EMBEDDING_SIZE = 1024
DATA_DIRECTORY = os.getcwd() + '/data'
DEBUG = True


# Takes a path to an XML file stored as a string and returns a list of documents
# compiled from the file as a list of strings where each string represents a
# document.
def xml_parser(path: str) -> list[str]:
    documents = []
    root = ET.parse(path).getroot()

    for problem in root:
        document = str(problem[0].text)

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


# Takes a path to a CSV file stored as a string and returns a list of documents
# compiled from the file as a list of strings where each string represents a
# document.
def csv_parser(path: str) -> list[str]:
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


# 
def txt_parser(path: str) -> list[str]:
    documents = []

    with open(path, 'r') as file:
        current = file.readline()

        while current != '':
            documents.append(current.strip())
            current = file.readline()
    return [' '.join(documents)]


# Builds a list of documents as a list of strings where each string is a
# document. Also computes the embeddings of each document and stores them in an
# array. Both are then pickled and stored in files for later use.
def run() -> None:
    model = SentenceTransformer(ENCODING_MODEL)
    documents = []

    for filename in os.listdir(DATA_DIRECTORY + '/xml'):
        documents.extend(xml_parser(DATA_DIRECTORY + '/xml/' + filename))
        if DEBUG:
            print(str(len(documents)))

    for filename in os.listdir(DATA_DIRECTORY + '/csv'):
        documents.extend(csv_parser(DATA_DIRECTORY + '/csv/' + filename))
        if DEBUG:
            print(str(len(documents)))
    
    for filename in os.listdir(DATA_DIRECTORY + '/txt'):
        if filename != '.DS_Store':
            documents.extend(txt_parser(DATA_DIRECTORY + '/txt/' + filename))
        if DEBUG:
            print(str(len(documents)))

    embeddings = np.empty(shape=(len(documents), EMBEDDING_SIZE), dtype=float)

    for i in range(0, len(embeddings)):
        embeddings[0] = model.encode(sentences=documents[i], prompt_name='document')
        if DEBUG:
            print(str((i * 100.0 / len(embeddings)) // 1) + '%')

    with open('documents', 'w+b') as file:
        pickle.dump(documents, file)
    
    with open('embeddings', 'w+b') as file:
        pickle.dump(embeddings, file)


if __name__ == '__main__':
    run()