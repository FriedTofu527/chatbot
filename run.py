import pickle

import chromadb
import ollama
from sentence_transformers import SentenceTransformer


GENERATION_MODEL = 'deepseek-r1:7b'
ENCODING_MODEL = 'Qwen/Qwen3-Embedding-0.6B'
N_RESULTS = 5
DEBUG = True


def run() -> None:
    collection = chromadb.Client().create_collection('collection')
    model = SentenceTransformer(ENCODING_MODEL)
    documents = []
    embeddings = []

    with open('documents', 'r+b') as file:
        documents = pickle.load(file)

    with open('embeddings', 'r+b') as file:
        embeddings = pickle.load(file)

    collection.add(ids=list(map(str, range(0, len(documents)))), embeddings=embeddings, documents=documents)

    print(f'{len(documents)} documents loaded.')

    while True:
        user_input = input()
        data = collection.query(query_embeddings=model.encode(sentences=user_input, prompt_name='query', convert_to_numpy=True), n_results=N_RESULTS)['documents']
        
        if DEBUG:
            print(data)
        
        print(ollama.generate(model=GENERATION_MODEL, prompt=f'Assume the role of a chatbot assisting a user by finding information on a website for them. The user has just asked the following prompt: "{user_input}". Respond to the prompt using the provided information: {data}', think=False)['response'])


if __name__ == '__main__':
    run()