import os

import requests
import bs4


PARSER = 'lxml'
TRIM_THRESHOLD = 20
DATA_DIRECTORY = os.getcwd() + '/data'
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
DEBUG = False


def page_getter(urls: list[str]) -> dict[str, str]:
    pages = {}

    for url in urls:
        response = requests.get(url=url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15'})
        if response.status_code == 200:
            pages[url] = response.text
        else:
            if DEBUG:
                print(f'Connection error. Skipping URL = {url}')
    return pages


def page_parser(sources: list[str], search: tuple[str, dict], tag: str, recursive: bool, trim: bool) -> list[str]:
    documents = []
    pages = page_getter(sources)

    for url in sources:
        for result in bs4.BeautifulSoup(pages[url], PARSER).find_all(*search):
            if isinstance(result, bs4.Tag):
                for target in result.find_all(tag, recursive=recursive):
                    document = ' '.join(target.stripped_strings)
                    if not trim or len(document) > TRIM_THRESHOLD:
                        documents.append(document.replace('\n', ' '))
            else:
                if DEBUG:
                    print(f'Parsing error. Skipping URL = {url}')
    return documents


def programs_parser() -> list[str]:
    documents = []
    pages = page_getter(PROGRAMS_SOURCES)

    for url in PROGRAMS_SOURCES:
        table = bs4.BeautifulSoup(pages[url], PARSER).find('table', {'class': 'table table-condensed table-borderless'})
        if isinstance(table, bs4.Tag):
            rows = table.find_all('tr', recursive=False)
            for i in range(0, len(rows), 3):
                cn = []
                en = []
                for j in range(i, i + 2):
                    row = rows[j]
                    if isinstance(row, bs4.Tag):
                        for header in row.find_all('th', recursive=False):
                            if isinstance(header, bs4.Tag):
                                cn.append(f'课程名称：{str(header.string).strip()}。课程说明：')
                                en.append(f'Class name: {str(header.string).strip()}. Class description:')
                        for tag in row.find_all(True, {'class': 'cn'}):
                            cn.extend(tag.stripped_strings)
                        for tag in row.find_all(True, {'class': 'en'}):
                            en.extend(tag.stripped_strings)
                documents.append(''.join(cn).replace('\n', '。'))
                documents.append(' '.join(en).replace('\n', '. '))
        else:
            if DEBUG:
                print(f'Parsing error. Skipping URL = {url}.')
    return documents


def run() -> None:
    documents = []

    documents.extend(page_parser(FAQ_SOURCES, ('table', {}), 'tr', True, True))
    documents.extend(page_parser(ABOUT_SOURCES, ('main', {}), 'article', True, True))
    documents.extend(page_parser(FAQ_SOURCES, ('body', {}), 'div', False, True))
    documents.extend(page_parser(FAQ_SOURCES, ('div', {'class': 'panel panel-body'}), 'div', False, True))
    documents.extend(programs_parser())

    if DEBUG:
        print(len(documents))

    with open(DATA_DIRECTORY + '/documents/documents.txt', 'w') as file:
        for document in documents:
            file.write(document)
            file.write('\n')


if __name__ == '__main__':
    run()