from fastapi import FastAPI
from openai import OpenAI
import chromadb
import run


CLIENT = OpenAI()
COLLECTION = chromadb.PersistentClient().get_collection('collection')
GENERATING_PROMPT = run.load_prompt('prompts/generating.txt')
REWRITING_PROMPT = run.load_prompt('prompts/rewriting.txt')
API = FastAPI()


@API.get('/query')
async def query(q: str) -> dict[str, str]:
    rewritten_queries = run.rewrite_queries(CLIENT, REWRITING_PROMPT, q)
    embedded_rewritten_queries = run.embed_queries(CLIENT, rewritten_queries)
    documents = run.query_database(COLLECTION, embedded_rewritten_queries)
    return {'query': run.generate_answer(CLIENT, GENERATING_PROMPT, documents, q)}