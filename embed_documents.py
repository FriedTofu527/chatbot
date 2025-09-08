import numpy as np
import os
import typing

import chromadb
import openai
from openai import OpenAI


DEBUG = False
EMBEDDING_SIZE = 3072
EF_CONSTRUCTION = 200
MAX_NEIGHBORS = 32
EMBEDDING_MODEL = 'text-embedding-3-large'
DATA_DIRECTORY = os.getcwd() + '/data'


def parse_embedding_response(embedding_response: openai.types.CreateEmbeddingResponse) -> np.ndarray:
    embeddings = np.empty(shape=(len(embedding_response.data), EMBEDDING_SIZE), dtype=float)
    for i in range(0, len(embedding_response.data)):
        embeddings[i] = embedding_response.data[i].embedding
    return embeddings


def parse_document(path: str) -> list[str]:
    documents = []
    with open(path, 'r') as file:
        documents.extend(map(str.strip, file.readlines()))
    return documents


def parse_csv(path: str) -> list[str]:
    documents = []
    with open(path, 'r') as file:
        try:
            categories = list(map(str.strip, file.readline().split(',')))
            current = list(map(str.strip, file.readline().split(',')))
            while current != ['']:
                document = []
                for i in range(len(categories)):
                    document.append(f'{categories[i]}: {current[i] if current[i] else 'None'}.')
                documents.append(' '.join(document))
                current = list(map(str.strip, file.readline().split(',')))
        except:
            print(f'Parsing error. Failed to parse file: {path}. Aborting.')
            raise RuntimeError('Failed to parse file.')
    return documents


def parse_txt(path: str) -> list[str]:
    documents = []
    with open(path, 'r') as file:
        current = file.readline()
        while current:
            if current.strip():
                documents.append(current.strip())
            current = file.readline()
    return [' '.join(documents)]


def load_documents(directory: str, parsing_function: typing.Callable[[str], list[str]]) -> list[str]:
    try:
        documents = []
        for file_name in os.listdir(directory):
            if file_name != '.DS_Store':
                documents.extend(parsing_function(directory + '/' + file_name))
        return documents
    except:
        print(f'Parsing Error. Failed to load documents in directory: {directory} with parsing function {parsing_function}. Aborting.')
        raise RuntimeError('Failed to load documents.')


def embed_documents(client: OpenAI, documents: list[str]) -> np.ndarray:
    try:
        return parse_embedding_response(client.embeddings.create(input=documents, model=EMBEDDING_MODEL))
    except:
        print(f'OpenAI API error. Failed to embed documents: \'{'\', \''.join(documents)}\'. Aborting.')
        raise RuntimeError('Failed to embed documents.')


def main() -> None:
    client = OpenAI()
    documents = []
    collection = chromadb.PersistentClient().get_or_create_collection('collection', {'hnsw': {'space': 'cosine', 'ef_construction': EF_CONSTRUCTION, 'max_neighbors': MAX_NEIGHBORS}})

    documents.extend(load_documents(DATA_DIRECTORY + '/documents', parse_document))
    documents.extend(load_documents(DATA_DIRECTORY + '/csv', parse_csv))
    documents.extend(load_documents(DATA_DIRECTORY + '/txt', parse_txt))
    embeddings = embed_documents(client, documents)
    collection.upsert(ids=list(map(str, range(0, len(documents)))), embeddings=embeddings, documents=documents)

    if DEBUG:
        print(f'Database contains {collection.count()} documents.')


if __name__ == '__main__':
    main()