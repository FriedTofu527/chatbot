import numpy as np
import os
import pickle

from sentence_transformers import SentenceTransformer


ENCODING_MODEL = 'Qwen/Qwen3-Embedding-0.6B'
EMBEDDING_SIZE = 1024
DATA_DIRECTORY = os.getcwd() + '/data'
DEBUG = True


def document_parser(path: str) -> list[str]:
    documents = []
    
    with open(path, 'r') as file:
        documents.extend(map(str.strip, file.readlines()))

    return documents


# Takes a path to a CSV file stored as a string and returns a list of documents
# compiled from the file as a list of strings where each string represents a
# document. This CSV was exported from Excel. Not designed to handle other 
# formats!!!
def csv_parser(path: str) -> list[str]:
    documents = []

    with open(path, 'r') as file:
        categories = list(map(str.strip, file.readline().split(',')))
        current = list(map(str.strip, file.readline().split(',')))

        while current != ['']:
            document = []

            for i in range(len(categories)):
                document.append(f'{categories[i]}: {current[i] if current[i] else 'None'}.')

            documents.append(' '.join(document))
            current = list(map(str.strip, file.readline().split(',')))
    return documents


# Takes a path to a txt file stored as a string and returns a list containing
# a single string representing one document. 
def txt_parser(path: str) -> list[str]:
    documents = []

    with open(path, 'r') as file:
        current = file.readline()

        while current:
            if current.strip():
                documents.append(current.strip())
            current = file.readline()
    return [' '.join(documents)]


# Builds a list of documents as a list of strings where each string is a
# document. Also computes the embeddings of each document and stores them in an
# array. Both are then pickled and stored in files for later use.
def run() -> None:
    model = SentenceTransformer(ENCODING_MODEL)
    documents = []

    for filename in os.listdir(DATA_DIRECTORY + '/documents'):
        documents.extend(document_parser(DATA_DIRECTORY + '/documents/' + filename))
        if DEBUG:
            print(len(documents))

    for filename in os.listdir(DATA_DIRECTORY + '/csv'):
        documents.extend(csv_parser(DATA_DIRECTORY + '/csv/' + filename))
        if DEBUG:
            print(len(documents))
    
    for filename in os.listdir(DATA_DIRECTORY + '/txt'):
        if filename != '.DS_Store':
            documents.extend(txt_parser(DATA_DIRECTORY + '/txt/' + filename))
        if DEBUG:
            print(len(documents))

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