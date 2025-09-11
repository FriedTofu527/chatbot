# Documentation

## Overview

I'm going to start with an overview of the design of this chatbot program. 
This type of chatbot runs on a system called retrieval augmented generation or
RAG for short. The major components of an RAG system consist of a database of
short-ish documents, a large language model (LLM) responsible for generating
responses, and another LLM for generating embeddings. The basic way this thing
works is that when a user asks a question, that question is fed into an LLM to
generate text embedding. Embeddings are really high dimentional vectors that
represent the meaning of a string of text. This is really just a way of
encoding information in a way that lets us easily find different strings with
similar meaning. This lets us find related pieces of text in a database by
comparing the embedding of the query with the embeddings of the pieces of text
in the database. The way it does this is by calculating the distances between
the vectors and picking the ones with the shortest distance (most similar
content). This is why it is important to have shorter peices of text that are
more focused on a single topic in the database. If you don't separate documents
by meaning, it can be hard to generate effective embeddings which makes
searching the database less effective. It is also important to not have a bunch
of repetitive or generic content in each document because this makes all of the
embeddings closer together which again makes retrieval less effective. Querying
the database with the embedding of the question returns the x most similar
documents in the database. The amount of documents returned, x, can be
configured. We then take these documents we found and pass them to another LLM
along with the original question and guidelines on how to answer the question.
The LLM then returns an answer and we give that answer to the user. I'm leaving
out a lot of details here but that's the basic overview. 


## Installation Guide

You need to have Python installed. I'm using a mac so I used the homebrew
package manager to do that. You can find the installation instructions for
homebrew on their page here: https://brew.sh. Just run the command to install
it. Then after you have homebrew installed. run the command
```brew install python3``` to get the newest version of Python.
    Next You will need to set up a Python virtual environment. I don't know why
but you are supposed to have a separate Python environment for every project. 
This way you can keep everything separate and manage different versions of
libraries. This is done through a virtual environment. Before you make the
environment, clone this repo. You can do this by running this command
```git clone https://github.com/FriedTofu527/chatbot.git```. This will create a
new directory called chatbot that contains the repo. Then you want to move into
the directory and make the virtual environment there. You can do this with the
command ```cd chatbot```. Now that you are in the directory, you can make the
virtual environment with this command ```python3 -m venv .venv```. This will
make a directory in the current directory called .venv. This contains your
virtual environment.
    Now you want to activate the virtual environment. In the same directory,
chatbot, enter this command to activate it: ```source .venv/bin/activate```.
this will run the activation script in the virtual environment. You should now
see (.venv) before your username in the shell.
    Now that the virtual environment is activated, you can install all the
external dependencies. This just means we need to install all of the third
party libraries the program needs that aren't included in Python's standard
library. To do this, simply run ```pip install -r requirements.txt```. This
will get you everything you need. It might take a while though since each third
party library has their own dependencies. 
    Now everything should be just works<sup>TM</sup>.
    To start the server you can run the run.sh script or use the command
```uvicorn web_server:API --port=<open_port> --host=0.0.0.0```. Make sure you
use 0.0.0.0 for host. 127.0.0.1 or my public ip did not work. I'm pretty sure
the port can be any port you have open.
    To summarize, I'm going to list all of the commands you need to set
everything up.

    brew install python3```
    git clone https://github.com/FriedTofu527/chatbot.git```
    cd chatbot```
    python3 -m venv .venv```
    source .venv/bin/activate```
    pip install -r requirements.txt```
    uvicorn web_server:API --port=<open_port> --host=0.0.0.0```

## run.py

I'm going to start with run.py because it is the simplest. This contains all of
the code that runs when the chatbot is running. All the code in the other
modules is only run when you want to update the database contents. run.py
starts by loading up the database of documents and embeddings. This will crash
if the database isn't in the expected location. Make sure you run the other two
modules to create the database before trying to run the chatbot. It also loads
the prompts from the prompts directory and will crash if those are missing. It
also creates an OpenAI client object. This object requires that you have an
OPENAI_API_KEY. Get ahold of one and set it as an environment variable before
trying to run anything. After loading up all of the required stuff it will ask
for user input as text through the termainal. Whatever gets answered will be
the query. The program then makes an API call to OpenAI's responses API asking
the LLM to generate multiple more detailed questions to help with retrieval.
This is because if the user asks a question with an unclear meaning or a
question that contains very little text, it can be difficult to generate
meaningful embeddings from that question and find similar documents withthose
embeddings. This is done using the prompt contained in prompts/rewriting.txt.
I chose to include parts of cacc's about page so the LLM has more context. I'm
hoping that this would allow the LLM to generate questions that make more
sense. The response format is JSON. Now that the query has been rewritten to
get better retrieval performance, we can generate embeddings for the queries
and query the database. There's not much to say about generating embeddings.
It's just an API call to the model 'text-embedding-3-large' to get the
embedding. The size of the embedding is 3072. This means the embedding is a
vector with 3072 values. Any time you query the database, an embedding size of
3072 has to be used otherwise it will crash. The value can be changed by there
isn't really any reason to because the API for generating embeddings is plenty
fast and higher values give better performance. Maybe you can get better
performance querying the database with lower dimention embeddings but I have
not tested that. The next step is querying the database with the embeddings
from the rewritten prompts. Theres not a whole lot to this step because it is
all handled by the chromadb libary. The amount of documents returned by the
query can be controlled by changing the N_RESULTS constant. I set it to 30 by
default but you can change it to pretty much anything. Higher numbers mean
slower database searches but you cast a wider net so it is more likely that the
documents retrieved contain the answer. This actually has kind of a large 
effect on response speed so this is the main lever you can adjust to generate
responses faster. This is because the less results you retrieve the less
documents are passed to the LLM for the final response generation step. Sending
the LLM less text significantly speeds up generation. Another way you could
tune speed is by changing which LLM to use. The current one being used is 
'gpt-4.1-mini'. The last step is generating an answer. This works by passing
the retrieved documents, the user's original question, and a system prompt with
detailed instructions on how to respond to an LLM. The LLM then digests
everything and generates a response. As of now, the prompts are pretty basic.
The structure of the prompt is taken from OpenAI's cookbook on prompting so
there probably are improvements to the prompt that can be made. I haven't
really looked into this at all because I've never worked with anything AI
related. The response from the LLM is then printed through the terminal. I
don't have any details on how this Python script is supposed to be integrated
into everything else so I don't know how I'm supposed to receive prompts and
give responses. This will probably have to be changed in the future but that
shouldn't be too much work since all of the logic remains the same. As with all
of the modules I wrote, there is a dubug mode that can be activated by setting
DEBUG to True.  This will cause a bunch of extra print statements to go off
that should make it easier to diagnose problems.