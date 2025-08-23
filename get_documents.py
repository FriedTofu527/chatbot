import requests
import bs4


DEBUG = True
SOURCES = ['https://www.caccusa.org/faq.php?p=1', 
           'https://www.caccusa.org/faq.php?p=2', 
           'https://www.caccusa.org/faq.php?p=3', 
           'https://www.caccusa.org/faq.php?p=4', 
           'https://www.caccusa.org/faq.php?p=5', 
           'https://www.caccusa.org/faq.php?p=6', 
           'https://www.caccusa.org/about.php?p=1', 
           'https://www.caccusa.org/about.php?p=2', 
           'https://www.caccusa.org/seminar.php', 
           'https://www.caccusa.org/calendar.php',
           'https://www.caccusa.org/program.php?p=10',
           'https://www.caccusa.org/program.php?p=11',
           'https://www.caccusa.org/program.php?p=12',
           'https://www.caccusa.org/program.php?p=14',
           'https://www.caccusa.org/program.php?p=16',
           'https://www.caccusa.org/school.php?p=3']


def run() -> None:
    for page in SOURCES:
        r = requests.get(url=page, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15'})
        if r.status_code == 200:
            documents = []
            b = bs4.BeautifulSoup(r.text, 'lxml')
            # for d in b.find_all('tr'):
            #     document = ''
            #     for s in d.stripped_strings:
            #         document += ' ' + s
            #     documents.append(document)
            for table in b.find_all('table'):
                if isinstance(table, bs4.Tag):
                    documents.append(parse_table(table))
            if DEBUG:
                print(documents)
        else:
            print('Connection Error')


def parse_table(t: bs4.Tag) -> list[str]:
    table = []
    
    return table


if __name__ == '__main__':
    run()