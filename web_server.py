from fastapi import FastAPI
from openai import OpenAI
import chromadb
import uvicorn

import run


API = FastAPI()
CLIENT = OpenAI()
COLLECTION = chromadb.PersistentClient().get_collection('collection')
GENERATING_PROMPT = run.load_prompt('prompts/generating.txt')
REWRITING_PROMPT = run.load_prompt('prompts/rewriting.txt')


@API.get('/query')
async def query(q: str) -> dict[str, str]:
    if q:
        rewritten_queries = run.rewrite_queries(CLIENT, REWRITING_PROMPT, q)
        embedded_rewritten_queries = run.embed_queries(CLIENT, rewritten_queries)
        documents = run.query_database(COLLECTION, embedded_rewritten_queries)
        return {'text': run.generate_answer(CLIENT, GENERATING_PROMPT, documents, q), 'error': ''}
    else:
        return {'text': '', 'error': 'Query string cannot be empty.'}


if __name__ == '__main__':
    uvicorn.run(API, host='0.0.0.0', port=25565)