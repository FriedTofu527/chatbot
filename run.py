import json
import numpy as np
import os

import chromadb
from openai import OpenAI


N_RESULTS = 20
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
DEBUG = True


def run():
    client = OpenAI()
    collection = chromadb.PersistentClient().get_collection('collection')

    with open(PROMPTS_DIRECTORY + '/generating.txt', 'r') as file:
        generating_prompt = ''.join(file.readlines())

    with open(PROMPTS_DIRECTORY + '/rewriting.txt', 'r') as file:
        rewriting_prompt = ''.join(file.readlines())

    if DEBUG:
        print(f'{collection.count()} documents loaded.')

    print('Ready.')

    while True:
        data = set()
        query = input()

        rewritten_queries = json.loads(client.responses.create(model='gpt-4.1-mini', instructions=rewriting_prompt, input=f'Original query: {query}', text={'format': {'type': 'json_schema', 'name': 'rewritten_queries', 'strict': True, 'schema': JSON_SCHEMA}}).output_text).get('queries')
        if DEBUG:
            for rewritten_query in rewritten_queries:
                print(rewritten_query)
        
        embedded_rewritten_queries = client.embeddings.create(input=rewritten_queries, model='text-embedding-3-large').data
        query_embeddings = np.empty(shape=(len(embedded_rewritten_queries), EMBEDDING_SIZE), dtype=float)
        for i in range(0, len(embedded_rewritten_queries)):
            query_embeddings[i] = embedded_rewritten_queries[i].embedding

        query_results = collection.query(query_embeddings=query_embeddings, n_results=N_RESULTS)['documents']
        if query_results is not None:
            for query_result in query_results:
                data.update(query_result)

        if DEBUG:
            for item in data:
                print(item)

        if data is not None:
            print(client.responses.create(model='gpt-4.1-mini', instructions=generating_prompt + '<document>' + '</document> <document>'.join(data) + '</document>', input=query).output_text)


if __name__ == '__main__':
    run()