from bs4 import BeautifulSoup
import requests
import numpy as np
import re
import pandas as pd

def extract_books_from_result(soup):
    returner = {'books': [], 'authors': []}
    for book in soup.find_all('div', attrs={'class':'cmp-text text'}):
        try:
            text = book.text
            pattern = re.compile(r'(?<=. ).+(?=\n)')
            appender = re.findall(pattern,text)[0].split(' by')

            if len(appender) > 1:
                returner['books'].append(appender[0])
                returner['authors'].append(appender[1])

        except:
            None

    returner_df = pd.DataFrame(returner, columns=['books','authors'])

    return returner_df

url = 'https://www.penguin.co.uk/articles/2018/100-must-read-classic-books/'
r = requests.get(url)
soup = BeautifulSoup(r.text,'html.parser')
results = extract_books_from_result(soup)

print(results)
