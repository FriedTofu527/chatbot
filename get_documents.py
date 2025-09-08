import os
import urllib.parse

import bs4
import requests


DEBUG = False
PARSER = 'lxml'
TRIM_THRESHOLD = 20
DATA_DIRECTORY = os.getcwd() + '/data'
SCHEME = 'https'
NETLOC = 'www.caccusa.org'
IRRELEVANT_TAGS = {'header',
                   'footer', 
                   'style', 
                   'script'}
IGNORED_SCHEMES = {'javascript', 
                   'mailto'}
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15'}
FAQ_SOURCES = ['https://www.caccusa.org/faq.php?p=1', 
               'https://www.caccusa.org/faq.php?p=2', 
               'https://www.caccusa.org/faq.php?p=3', 
               'https://www.caccusa.org/faq.php?p=4', 
               'https://www.caccusa.org/faq.php?p=5', 
               'https://www.caccusa.org/faq.php?p=6']
ABOUT_SOURCES = ['https://www.caccusa.org/about.php?p=1', 
                 'https://www.caccusa.org/about.php?p=2']
SEMINAR_SOURCES = ['https://www.caccusa.org/seminar.php']
GENERAL_INFORMATION_SOURCES = ['https://www.caccusa.org/info.php?p=1']
PROGRAMS_SOURCES = ['https://www.caccusa.org/program.php?p=10',
                    'https://www.caccusa.org/program.php?p=11',
                    'https://www.caccusa.org/program.php?p=12',
                    'https://www.caccusa.org/program.php?p=14',
                    'https://www.caccusa.org/program.php?p=16']
OTHER_SOURCES = ['https://www.caccusa.org/event.php?p=1', 
                 'https://www.caccusa.org/faq.php?p=1', 
                 'https://www.caccusa.org/faq.php?p=2', 
                 'https://www.caccusa.org/faq.php?p=3', 
                 'https://www.caccusa.org/faq.php?p=4', 
                 'https://www.caccusa.org/faq.php?p=5', 
                 'https://www.caccusa.org/faq.php?p=6', 
                 'https://www.caccusa.org/about.php?p=1', 
                 'https://www.caccusa.org/about.php?p=2', 
                 'https://www.caccusa.org/seminar.php', 
                 'https://www.caccusa.org/info.php?p=1', 
                 'https://www.caccusa.org/program.php?p=10', 
                 'https://www.caccusa.org/program.php?p=11', 
                 'https://www.caccusa.org/program.php?p=12',
                 'https://www.caccusa.org/program.php?p=14', 
                 'https://www.caccusa.org/program.php?p=16']


def ignore_irrelevant_tags(tag: bs4.element.PageElement) -> bool:
    return isinstance(tag, bs4.Tag) and tag.name not in IRRELEVANT_TAGS


def clean_documents(documents: list[str]) -> list[str]:
    for i in range(0, len(documents)):
        if len(documents[i]) < 200:
            documents[i] = ''
        documents[i] = documents[i].removeprefix('Main Content ')
        documents[i] = documents[i].removeprefix('CACC Chinese School ')
        documents[i] = documents[i].removeprefix('School Day Holiday Special Day / Deadline ')
        documents[i] = documents[i].removeprefix('Toggle navigation ')
    return documents


def get_pages(urls: list[str]) -> list[str]:
    try:
        pages = []
        for url in urls:
            response = requests.get(url=url, headers=HEADERS)
            if response.status_code == 200:
                pages.append(response.text)
            else:
                print(f'Connection error. Failed to scrape URL: {url}. Continuing without scraping source.')
        return pages
    except:
        print(f'Connection error. Failed to scrape sources: \'{'\', \''.join(urls)}\'. Aborting.')
        raise RuntimeError('Failed to scrape sources.')


def parse_source(urls: list[str], search: tuple[str, dict], tag: str, recursive: bool) -> list[str]:
    try:
        documents = []
        for page in get_pages(urls):
            for result in bs4.BeautifulSoup(page, PARSER).find_all(*search):
                if isinstance(result, bs4.Tag):
                    for target in result.find_all(tag, recursive=recursive):
                        document = ' '.join(target.stripped_strings)
                        if len(document) > TRIM_THRESHOLD:
                            documents.append(document.replace('\n', '. '))
        if DEBUG:
            print(f'Parsed {len(documents)} sources.')
        return documents
    except:
        print(f'Parsing error. Failed to parse sources: \'{'\', \''.join(urls)}\'. Aborting.')
        raise RuntimeError('Failed to parse sources.')


def parse_programs(urls: list[str]) -> list[str]:
    try:
        documents = []
        for page in get_pages(urls):
            table = bs4.BeautifulSoup(page, PARSER).find('table', {'class': 'table table-condensed table-borderless'})
            if isinstance(table, bs4.Tag):
                trs = table.find_all('tr', recursive=False)
                for i in range(0, len(trs), 3):
                    cn = []
                    en = []
                    for j in range(i, i + 2):
                        tr = trs[j]
                        if isinstance(tr, bs4.Tag):
                            for th in tr.find_all('th', recursive=False):
                                if isinstance(th, bs4.Tag):
                                    cn.append(f'课程名称：{str(th.string).strip()}。课程说明：')
                                    en.append(f'Class name: {str(th.string).strip()}. Class description:')
                            for tag in tr.find_all(True, {'class': 'cn'}):
                                cn.extend(tag.stripped_strings)
                            for tag in tr.find_all(True, {'class': 'en'}):
                                en.extend(tag.stripped_strings)
                    documents.append(''.join(cn).replace('\n', '。'))
                    documents.append(' '.join(en).replace('\n', '. '))
        if DEBUG:
            print(f'Parsed {len(documents)} program sources.')
        return documents
    except:
        print(f'Parsing error. Failed to parse programs: \'{'\', \''.join(urls)}\'. Aborting.')
        raise RuntimeError('Failed to parse programs.')


def visit_source(unvisited_sources: list[str], discovered_sources: set[str]) -> list[str]:
    try:
        documents = []
        source = unvisited_sources.pop()
        body = bs4.BeautifulSoup(get_pages([source]).pop(), PARSER).find('body')
        if isinstance(body, bs4.Tag):
            for relevent_tag in body.find_all(ignore_irrelevant_tags, recursive=False):
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
                                if url.scheme not in IGNORED_SCHEMES and (url.netloc == NETLOC or not url.netloc) and url.path.endswith('php') and reformed_url not in discovered_sources:
                                    unvisited_sources.append(reformed_url)
                                    discovered_sources.add(reformed_url)
                    if source not in FAQ_SOURCES + ABOUT_SOURCES + SEMINAR_SOURCES + GENERAL_INFORMATION_SOURCES + PROGRAMS_SOURCES:
                        documents.append(' '.join(relevent_tag.stripped_strings).replace('\n', '. '))
        return documents
    except:
        print(f'Parsing error. Failed to parse other sources: \'{'\', \''.join(unvisited_sources)}\'. Aborting.')
        raise RuntimeError('Failed to parse other sources.')


def parse_others(urls: list[str]) -> list[str]:
    documents = []
    discovered_sources = set(urls)
    unvisited_sources = urls
    while unvisited_sources:
        documents.extend(visit_source(unvisited_sources, discovered_sources))
    if DEBUG:
        print(f'Parsed {len(documents)} other sources.')
    return clean_documents(documents)


def main() -> None:
    documents = []
    documents.extend(parse_source(FAQ_SOURCES, ('table', {}), 'tr', True))
    documents.extend(parse_source(ABOUT_SOURCES, ('main', {}), 'article', True))
    documents.extend(parse_source(SEMINAR_SOURCES, ('body', {}), 'div', False))
    documents.extend(parse_source(GENERAL_INFORMATION_SOURCES, ('div', {'class': 'panel panel-body'}), 'div', False))
    documents.extend(parse_programs(PROGRAMS_SOURCES))
    documents.extend(parse_others(OTHER_SOURCES))

    if DEBUG:
        print(f'Scraped {len(documents)} documents.')

    with open(DATA_DIRECTORY + '/documents/documents.txt', 'w') as file:
        for document in documents:
            if document:
                file.write(document + '\n')


if __name__ == '__main__':
    main()