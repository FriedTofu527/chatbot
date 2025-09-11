from openai import AsyncOpenAI
import chromadb
import fastapi
import typing
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

import run


API = fastapi.FastAPI()
CLIENT = AsyncOpenAI()
COLLECTION = chromadb.PersistentClient().get_collection('collection')
GENERATING_PROMPT = run.load_prompt('prompts/generating.txt')
REWRITING_PROMPT = run.load_prompt('prompts/rewriting.txt')
WHITELISTED_IPS = ['66.96.130.58', '73.170.102.89']
ALLOWED_ORIGINS = ['https://www.caccusa.org', 'https://dev.caccusa.org']


API.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS, allow_credentials=True, allow_methods=['*'], allow_headers=['*'],)


# @API.middleware('http')
# async def validata_ip(request: fastapi.Request, call_next: typing.Callable) -> fastapi.responses.JSONResponse:
#     if request.client:
#         ip = str(request.client.host)
#         if ip not in WHITELISTED_IPS:
#             return fastapi.responses.JSONResponse(status_code=fastapi.status.HTTP_400_BAD_REQUEST, content={'message': f'IP {ip} is not allowed to access this resource.'})
#     return call_next(request)


@API.get('/query')
async def get_query(q: str) -> dict[str, str]:
    if q:
        rewritten_queries = await run.rewrite_queries(CLIENT, REWRITING_PROMPT, q)
        embedded_rewritten_queries = await run.embed_queries(CLIENT, rewritten_queries)
        documents = run.query_database(COLLECTION, embedded_rewritten_queries)
        return {'text': await run.generate_answer(CLIENT, GENERATING_PROMPT, documents, q), 'error': ''}
    else:
        return {'text': '', 'error': 'Query string cannot be empty.'}


@API.post('/query')
async def post_query(q: str) -> dict[str, str]:
    if q:
        rewritten_queries = await run.rewrite_queries(CLIENT, REWRITING_PROMPT, q)
        embedded_rewritten_queries = await run.embed_queries(CLIENT, rewritten_queries)
        documents = run.query_database(COLLECTION, embedded_rewritten_queries)
        return {'text': await run.generate_answer(CLIENT, GENERATING_PROMPT, documents, q), 'error': ''}
    else:
        return {'text': '', 'error': 'Query string cannot be empty.'}


if __name__ == '__main__':
    uvicorn.run(API, host='0.0.0.0', port=25565, log_level='debug')