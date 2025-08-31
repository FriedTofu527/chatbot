import pickle

import chromadb
from sentence_transformers import SentenceTransformer
from openai import OpenAI


ENCODING_MODEL = 'Qwen/Qwen3-Embedding-0.6B'
N_RESULTS = 80
DEBUG = False


def run():
    client = OpenAI()
    collection = chromadb.Client().create_collection('collection')
    model = SentenceTransformer(ENCODING_MODEL)
    documents = []
    embeddings = []

    with open('system_prompt.txt', 'r') as file:
        system_prompt = ' '.join(file.readlines())

    with open('query_rewriting_prompt.txt', 'r') as file:
        query_rewriting_prompt = ' '.join(file.readlines())

    with open('documents', 'r+b') as file:
        documents = pickle.load(file)

    with open('embeddings', 'r+b') as file:
        embeddings = pickle.load(file)

    collection.add(ids=list(map(str, range(0, len(documents)))), embeddings=embeddings, documents=documents)

    if DEBUG:
        print(f'{len(documents)} documents loaded.')

    print('Ready')

    while True:
        data = set()
        user_input = input()
        rewritten_query = client.responses.create(model='gpt-4.1-mini', instructions=query_rewriting_prompt, input='Original query: ' + user_input).output_text.split('\n')
        
        if DEBUG:
            print(rewritten_query)
            print('\n')
        
        query_results = collection.query(query_embeddings=model.encode(sentences=rewritten_query, prompt_name='query', convert_to_numpy=True), n_results=N_RESULTS)['documents']
        if query_results:
            for query_result in  query_results:
                data.update(query_result)

        if DEBUG:
            print(data)
            print('\n')

        if data:
            response = client.responses.create(model='gpt-4.1-mini', instructions=system_prompt + '<document>' + '</document> <document>'.join(data) + '</document>', input=user_input)
            print(response.output_text)


if __name__ == '__main__':
    run()