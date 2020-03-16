from bs4 import BeautifulSoup
import requests
import numpy as np
import re
import pandas as pd

def extract_books_from_result(soup):
    returner = {'books': [], 'urls': []}
    for book in soup.find_all('h2', attrs={'class':'cp-title'}):
        try:

            title = book.find('span', attrs={'class':'title-content'})
            print(title.text)
            for link in book.find_all('a'):
                print(link.get('href'))
            pattern = re.compile(r'(?<=. ).+(?=\n)')
            appender = re.findall(pattern,text)[0].split(' by')

            if len(appender) > 1:
                returner['books'].append(appender[0])
                returner['authors'].append(appender[1])
        except:
            None

    print(returner)
    returner_df = pd.DataFrame(returner, columns=['books','authors'])
    return returner_df

url = 'https://jeffcolibrary.bibliocommons.com/v2/search?_ga=2.235076483.345186168.1583638760-1327672773.1570233965&query=Siddhartha&searchType=title'
r = requests.get(url)
soup = BeautifulSoup(r.text,'html.parser')
results = extract_books_from_result(soup)
