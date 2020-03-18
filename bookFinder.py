from bs4 import BeautifulSoup
import requests
import numpy as np
import pandas as pd

def retrieve_book_listing_from_url(url):
    r = requests.get(url[2])
    soup = BeautifulSoup(r.text,'html.parser')
    results = extract_books_from_result(soup,url[0])
    return results

def extract_books_from_result(soup, desiredTitle):
    # title | ebook | book | audiobook | other (CD)
    returner = [desiredTitle, 0, 0, 0, 0]
    for book in soup.find_all('div', attrs={'class':'cp-search-result-item-content'}):
        try:
            title = book.find('span', attrs={'class':'title-content'}).text
            if title == returner[0]:
                bookFormats = get_book_formats_from_book(book)
                for bookFormat in bookFormats:
                    if bookFormat == "eBook":
                        returner[1] += 1
                    elif bookFormat == "Book":
                        returner[2] += 1
                    elif bookFormat == "Audiobook":
                        returner[3] += 1
                    else:
                        returner[4] += 1
        except:
            None
    return returner

def get_book_formats_from_book(book):
    formats = []
    for bookFormats in book.find_all('div', attrs={'class':'format-info-main-content'}):
        titleRecord = bookFormats.text
        format = titleRecord.split(' ')
        try:
            indexOfFormat = format.index("-") - 1
        except:
            indexOfFormat = -1
        formats.append(format[indexOfFormat])

    return formats

def build_full_results_from_search(urls):
    allBookData = []
    for url in urls:
        currentBookData = retrieve_book_listing_from_url(url)
        allBookData.append(currentBookData)
    print(allBookData)
    return allBookData
