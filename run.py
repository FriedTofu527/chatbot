import asyncio
import json
import numpy as np
import os

import chromadb
import openai
from openai import AsyncOpenAI


DEBUG = False
EMBEDDING_MODEL = 'text-embedding-3-large'
GENERATING_MODEL = 'gpt-4.1-mini'
N_RESULTS = 30
EMBEDDING_SIZE = 3072
PROMPTS_DIRECTORY = os.getcwd() + '/prompts'
JSON_SCHEMA = {
    'type': 'object',
    'properties': {
        'queries': {
            'type': 'array',
            'items': {
                'type': 'string',
                'description': 'The reformulated query'
            }
        }
    },
    'additionalProperties': False,
    'required': ['queries']
}


def load_prompt(path: str) -> str:
    with open(path, 'r') as file:
        return ''.join(file.readlines())


def parse_embedding_response(embedding_response: openai.types.CreateEmbeddingResponse) -> np.ndarray:
    embeddings = np.empty(shape=(len(embedding_response.data), EMBEDDING_SIZE), dtype=float)
    for i in range(0, len(embedding_response.data)):
        embeddings[i] = embedding_response.data[i].embedding
    return embeddings


async def rewrite_queries(client: AsyncOpenAI, prompt: str, query: str) -> list[str]:
    try:
        rewritten_queries = json.loads((await client.responses.create(model=GENERATING_MODEL, instructions=prompt, input=f'Original query: {query}', text={'format': {'type': 'json_schema', 'name': 'rewritten_queries', 'strict': True, 'schema': JSON_SCHEMA}})).output_text).get('queries')
        if DEBUG:
            print('-----------------------\nRewritten Queries Start\n-----------------------')
            for rewritten_query in rewritten_queries:
                print(rewritten_query)
            print('---------------------\nRewritten Queries End\n---------------------')
        return rewritten_queries
    except:
        print(f'OpenAI API error. Failed to rewrite query: {prompt}. Continuing with original query. This may result in reduced retrieval performance.')
        return [query]


async def embed_queries(client: AsyncOpenAI, queries: list[str]) -> np.ndarray:
    try:
        return parse_embedding_response((await client.embeddings.create(input=queries, model=EMBEDDING_MODEL)))
    except:
        print(f'OpenAI API error. Failed to embed queries: {f'\'{'\', \''.join(queries)}\''}. Aborting.')
        raise RuntimeError('Failed to embed queries.')


def query_database(collection: chromadb.Collection, query_embeddings: np.ndarray) -> set[str]:
    try:
        documents = set()
        query_response = collection.query(query_embeddings=query_embeddings, n_results=N_RESULTS)
        query_documents = query_response.get('documents')
        if query_documents is not None:
            for query_document in query_documents:
                documents.update(query_document)
        if DEBUG:
            print('-------------------------\nRetrieved Documents Start\n-------------------------')
            for document in documents:
                print(document)
            print('-----------------------\nRetrieved Documents End\n-----------------------')
            query_distances = query_response.get('distances')
            if query_distances is not None:
                print('-----------------------------------\nRetrieved Documents Distances Start\n-----------------------------------')
                for query_distance in query_distances:
                    print(query_distance)
                print('---------------------------------\nRetrieved Documents Distances End\n---------------------------------')
        return documents
    except:
        print(f'Database error. Failed to retrieve documents. Aborting.')
        raise RuntimeError('Failed to retrieve documents.')


async def generate_answer(client: AsyncOpenAI, prompt: str, documents: set[str], query: str) -> str:
    try:
        return (await client.responses.create(model=GENERATING_MODEL, instructions=prompt + '<document>' + '</document><document>'.join(documents) + '</document>', input=query)).output_text
    except:
        print(f'OpenAI API error. Failed to generate answer. Aborting.')
        raise RuntimeError('Failed to generate answer.')


async def main():
    client = AsyncOpenAI()
    collection = chromadb.PersistentClient().get_collection('collection')
    generating_prompt = load_prompt(PROMPTS_DIRECTORY + '/generating.txt')
    rewriting_prompt = load_prompt(PROMPTS_DIRECTORY + '/rewriting.txt')

    if DEBUG:
        print(f'{collection.count()} documents loaded.')
    print('Ready.')

    while True:
        query = input()
        rewritten_queries = await rewrite_queries(client, rewriting_prompt, query)
        embedded_rewritten_queries = await embed_queries(client, rewritten_queries)
        documents = query_database(collection, embedded_rewritten_queries)
        print(await generate_answer(client, generating_prompt, documents, query))


if __name__ == '__main__':
    asyncio.run(main())