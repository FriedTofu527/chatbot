import os
import urllib.parse

import bs4
import requests


DATA_DIRECTORY = os.getcwd() + '/data'
SCHEME = 'https'
NETLOC = 'www.caccusa.org'
IRRELEVANT_TAGS = {'header',
                   'footer', 
                   'style', 
                   'script'}
IGNORED_SCHEMES = {'javascript', 
                   'mailto'}
PAGES = {'https://www.caccusa.org/event.php?p=1',
         'https://www.caccusa.org/faq.php?p=1', 
         'https://www.caccusa.org/faq.php?p=2', 
         'https://www.caccusa.org/faq.php?p=3', 
         'https://www.caccusa.org/faq.php?p=4', 
         'https://www.caccusa.org/faq.php?p=5', 
         'https://www.caccusa.org/faq.php?p=6', 
         'https://www.caccusa.org/about.php?p=1', 
         'https://www.caccusa.org/about.php?p=2', 
         'https://www.caccusa.org/seminar.php', 
         'https://www.caccusa.org/program.php?p=10', 
         'https://www.caccusa.org/program.php?p=11', 
         'https://www.caccusa.org/program.php?p=12',
         'https://www.caccusa.org/program.php?p=14', 
         'https://www.caccusa.org/program.php?p=16'}
IGNORED_PAGES = {'https://www.caccusa.org/faq.php?p=1', 
                 'https://www.caccusa.org/faq.php?p=2', 
                 'https://www.caccusa.org/faq.php?p=3', 
                 'https://www.caccusa.org/faq.php?p=4', 
                 'https://www.caccusa.org/faq.php?p=5', 
                 'https://www.caccusa.org/faq.php?p=6', 
                 'https://www.caccusa.org/about.php?p=1', 
                 'https://www.caccusa.org/about.php?p=2', 
                 'https://www.caccusa.org/seminar.php', 
                 'https://www.caccusa.org/program.php?p=10', 
                 'https://www.caccusa.org/program.php?p=11', 
                 'https://www.caccusa.org/program.php?p=12',
                 'https://www.caccusa.org/program.php?p=14', 
                 'https://www.caccusa.org/program.php?p=16'}
DEBUG = False


def only_relevant_tags(tag: bs4.element.PageElement) -> bool:
    return isinstance(tag, bs4.Tag) and tag.name not in IRRELEVANT_TAGS


# def parse_article(article: bs4.element.PageElement) -> list[str]:
#     if isinstance(article, bs4.Tag):
#         return list(' '.join(article.stripped_strings))
#     return []


# def parse_table(table: bs4.element.PageElement) -> list[str]:
#     documents = []

#     if isinstance(table, bs4.Tag):
#         for tr in table.find_all('tr', recursive=False):
#             if isinstance(tr, bs4.Tag):
#                 # documents.append(' '.join(tr.stripped_strings))
#                 if tr.find('th') is not None:

#     return documents


def visit(to_be_visited: list[str], discovered: set[str]) -> list[str]:
    documents = []
    current_url = to_be_visited.pop()

    if DEBUG:
        print(f'----------------------------------------\ncurrent url: {current_url}\n----------------------------------------')
    
    try:
        html = requests.get(url=current_url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15'}).text
    except:
        print(f'Connection error. Skipping URL = {current_url}')
        html = ''
    tree = bs4.BeautifulSoup(html, 'lxml', parse_only=bs4.filter.SoupStrainer('body')).find('body')
    
    if isinstance(tree, bs4.Tag):
        for relevent_tag in tree.find_all(only_relevant_tags, recursive=False):
            if isinstance(relevent_tag, bs4.Tag):
                for tag in relevent_tag.find_all(['a', 'iframe']):
                    if isinstance(tag, bs4.Tag):
                        if tag.name == 'a':
                            url = tag.get('href')
                        else:
                            url = tag.get('src')
                        if isinstance(url, str):
                            url = urllib.parse.urlsplit(url)
                            reformed_url = urllib.parse.urlunsplit((SCHEME, NETLOC, url.path, url.query, url.fragment))
                            if url.scheme not in IGNORED_SCHEMES and (url.netloc == NETLOC or not url.netloc) and url.path.endswith('php') and reformed_url not in discovered:
                                to_be_visited.append(reformed_url)
                                discovered.add(reformed_url)
                if current_url not in IGNORED_PAGES:
                    documents.append(' '.join(relevent_tag.stripped_strings).replace('\n', ' '))
    return documents


def main() -> None:
    to_be_visited = list()
    discovered = set()
    documents = list('')

    for url in PAGES:
        to_be_visited.append(url)
        discovered.add(url)
    while to_be_visited:
        documents.extend(visit(to_be_visited, discovered))
    
    if DEBUG:
        print(len(documents))

    with open(DATA_DIRECTORY + '/documents/automatic.txt', 'w') as file:
        for document in documents:
            document = document.removeprefix('Main Content CACC Chinese School ')
            document = document.removeprefix('School Day Holiday Special Day / Deadline ')
            if len(document) < 200:
                document = ''
            if document:
                file.write(document)
                file.write('\n')


if __name__ == '__main__':
    main()