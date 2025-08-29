from collections.abc import Iterator

import requests
import bs4


TRIM_THRESHOLD = 20
DEBUG = True
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


def html_parser(root: bs4.Tag, tag: str, recursive: bool, trim: bool) -> list[str]:
    documents = []
    
    for target in root.find_all(tag, recursive=recursive):
        document = ' '.join(target.stripped_strings)
        if not trim or len(document) > TRIM_THRESHOLD:
            documents.append(document)

    return documents


def page_getter(urls: list[str]) -> list[str]:
    pages = []

    for url in urls:
        response = requests.get(url=url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15'})
        if response.status_code == 200:
            pages.append(response.text)
        else:
            if DEBUG:
                print(f'Connection Error. Skipping URL={url}')
            pages.append('')
    return pages


def faq_parser() -> list[str]:
    documents = []

    for faq in page_getter(FAQ_SOURCES):
        for table in bs4.BeautifulSoup(faq, 'lxml').find_all('table'):
            if isinstance(table, bs4.Tag):
                documents.extend(html_parser(table, 'tr', True, True))
            else:
                if DEBUG:
                    print('Parsing error. Skipping FAQ page.')
    return documents


def about_parser() -> list[str]:
    documents = []

    for about in page_getter(ABOUT_SOURCES):
        for main in bs4.BeautifulSoup(about, 'lxml').find_all('main'):
            if isinstance(main, bs4.Tag):
                documents.extend(html_parser(main, 'article', True, True))
            else:
                if DEBUG:
                    print('Parsing error. Skipping about page.')
    return documents


def seminar_parser() -> list[str]:
    documents = []

    for seminar in page_getter(SEMINAR_SOURCES):
        for body in bs4.BeautifulSoup(seminar, 'lxml').find_all('body'):
            if isinstance(body, bs4.Tag):
                documents.extend(html_parser(body, 'div', False, True))
            else:
                if DEBUG:
                    print('Parsing error. Skipping seminar page.')
    return documents


def general_information_parser() -> list[str]:
    documents = []

    for gi in page_getter(GENERAL_INFORMATION_SOURCES):
        for div in bs4.BeautifulSoup(gi, 'lxml').find_all('div', {'class': 'panel panel-body'}):
            if isinstance(div, bs4.Tag):
                documents.extend(html_parser(div, 'div', False, True))
            else:
                if DEBUG:
                    print('Parsing error. Skipping general information page.')
    return documents


def programs_parser() -> list[str]:
    documents = []

    for program in page_getter(PROGRAMS_SOURCES):
        table = bs4.BeautifulSoup(program, 'lxml').find('table', {'class': 'table table-condensed table-borderless'})
        if isinstance(table, bs4.Tag):
            rows = table.find_all('tr', recursive=False)
            for i in range(0, len(rows), 3):
                cn = []
                en = []
                for j in range(i, i + 2):
                    row = rows[j]
                    if isinstance(row, bs4.Tag):
                        for header in row.find_all('th'):
                            if isinstance(header, bs4.Tag):
                                cn.append(f'课程名称：{str(header.string).strip()}。')
                                en.append(f'Class name: {str(header.string).strip()}.')
                        for tag in row.find_all(True, {'class': 'cn'}):
                            cn.extend(tag.stripped_strings)
                        for tag in row.find_all(True, {'class': 'en'}):
                            en.extend(tag.stripped_strings)
                documents.append(' '.join(cn))
                documents.append(' '.join(en))
        else:
            if DEBUG:
                print('Parsing error. Skipping program page.')
    return documents


def run() -> None:
    documents = []

    documents.extend(faq_parser())
    documents.extend(about_parser())
    documents.extend(seminar_parser())
    documents.extend(general_information_parser())
    documents.extend(programs_parser())

    print(len(documents))


if __name__ == '__main__':
    run()