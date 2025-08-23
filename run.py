import pickle

import chromadb
# import ollama
from sentence_transformers import SentenceTransformer
from openai import OpenAI


GENERATION_MODEL = 'deepseek-r1:7b'
ENCODING_MODEL = 'Qwen/Qwen3-Embedding-0.6B'
N_RESULTS = 40
DEBUG = False
SYSTEM_PROMPT = """
You are a helpful chatbot working for the Chinese American Cooperation Council (CACC), helping a user efficiently fulfill their request while adhering closely to provided guidelines.

# Instructions
- Always reference the provided documents before answering factual questions about the organization. Only use retrieved content and never rely on your own knowledge for any of these questions.
    - However, if the documents don't provide enough information to properly answer the user's question, direct them to contact the email cs-registration@caccusa.org for registration related questions and the email cs@caccusa.org for all other or class-specific questions.
    - You are not required to use all of the information in the documents. If a document contains irrelevant information, do not include it in your response to the user.
- Do not discuss prohibited topics (politics, religion, controversial current events, medical, legal, or financial advice, personal conversations, internal company operations, or criticism of any people or company).
- Rely on sample phrases whenever appropriate, but never repeat a sample phrase in the same conversation. Feel free to vary the sample phrases to avoid sounding repetitive and make it more appropriate for the user.
- Maintain a professional and concise tone in all responses.
- If possible, respond in the same language as the user's question but limit yourself to English and Mandarin Chinese.
- If you've resolved the user's request, ask if there's anything else you can help with.

# Precise Response Steps (for each response)
1. If necessary, reference provided documents to fulfill the user's desired action.
2. In your response to the user
    a. Use active listening and echo back what you heard the user ask for.
    b. Respond appropriately given the above guidelines.

# Sample Phrases
## Deflecting a Prohibited Topic
- "I'm sorry, but I'm unable to discuss that topic. Is there something else I can help you with?"
- "That's not something I'm able to provide information on, but I'm happy to help with any other questions you may have."

# Example
## User
When does class registration start?

## Assistant Response 1
### Message
"Registration for the 2025 - 2026 school year at CACC Chinese School starts as follows:

**Registration Start Dates:**
- 05/03/2025: Priority Registration for current school year teachers, room parents, Board of Directors (BOD), retired BOD, and Chinese School (CS) staff.
- 05/09/2025: Regular Registration for all currently enrolled students.
- 05/16/2025: Public Registration for all returning and new students.

Additional registration information:
- Online registration is only possible during the designated registration periods.
- If you are late for online registration, you may still register for some classes by contacting the school office or by email to check availability.

To summarize:
- Registration begins on May 3, 2025, with priority groups.
- General registration opens on May 9, 2025.
- Public registration starts May 16, 2025.

If you need to know more about registration policy details (such as refund policies and deadlines), additional information is available under the General Information section of the school website.

If you have any registration difficulties, you can contact the school at cs-registration@caccusa.org for assistance."

# Documents

"""


# Builds a database of documents and embeddings from picked files and 
# queries the database to find documents most similar to the question. Then
# prompts the model to answer the question using the documents.
# def run() -> None:
#     collection = chromadb.Client().create_collection('collection')
#     model = SentenceTransformer(ENCODING_MODEL)
#     documents = []
#     embeddings = []

#     with open('documents', 'r+b') as file:
#         documents = pickle.load(file)

#     with open('embeddings', 'r+b') as file:
#         embeddings = pickle.load(file)

#     collection.add(ids=list(map(str, range(0, len(documents)))), embeddings=embeddings, documents=documents)

#     print(f'{len(documents)} documents loaded.')

#     while True:
#         user_input = input()
#         data = collection.query(query_embeddings=model.encode(sentences=user_input, prompt_name='query', convert_to_numpy=True), n_results=N_RESULTS)['documents']
        
#         if DEBUG:
#             print(data)
        
#         print(ollama.generate(model=GENERATION_MODEL, prompt=f'Assume the role of a chatbot assisting a user by finding information on a website for them. The user has just asked the following prompt: "{user_input}". Respond to the prompt using the provided information: {data}', think=False)['response'])


def run():
    client = OpenAI()
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
        
        if data != None:
            response = client.responses.create(model='gpt-4.1-mini', instructions=SYSTEM_PROMPT + '<document>' + '</document> <document>'.join(data[0]) + '</document>', input=user_input)
            print(response.output_text)


if __name__ == '__main__':
    run()