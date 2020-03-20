from bs4 import BeautifulSoup
import requests
import numpy as np
import pandas as pd
import sys
import string
from selenium import webdriver

def retrieve_book_listing_from_url(url):
    desiredTitle = url[0]
    librarySearchURLs = url[1:]
    results = returner = {
        "shortTitle" : desiredTitle,
        "numEBooks" : 0,
        "numBooks" : 0,
        "numAudioBooks" : 0,
        "numOther" : 0
    }
    for libraryURL in librarySearchURLs:
        driver = webdriver.Firefox()
        driver.get('https://catalog.denverlibrary.org/search/searchresults.aspx?ctx=1.1033.0.0.6&type=Keyword&term=How%20Not%20to%20Die&by=TI&sort=RELEVANCE&limit=TOM=*&query=&page=0&searchid=1')
        driver.implicitly_wait(1000)

        soup = BeautifulSoup(driver.page_source,'html.parser')
        print(soup)


        #session = requests.Session()
        #r = session.get("https://catalog.denverlibrary.org/search/searchresults.aspx?ctx=1.1033.0.0.6&type=Keyword&term=How%20Not%20to%20Die&by=TI&sort=RELEVANCE&limit=TOM=*&query=&page=0&searchid=1")
        #soup = BeautifulSoup(r.text,'html.parser')
        #with open("libraryResults.html", "w") as file:
        #    file.write(str(soup))
        #print(soup)
        if "bibliocommons" in libraryURL:
            results = extract_books_from_bibliocommons_result(soup,desiredTitle, results)
            results["jeffCoURL"] = libraryURL
        else:
            results = extract_books_from_denver_result(soup, desiredTitle, results)
            results["denverURL"] = libraryURL
    return results

def extract_books_from_denver_result(soup, desiredTitle, existingData):
    existingData.update({"denverURL" : ""})
    for book in soup.find_all('span', attrs={'class':'nsm-e135'}):
        print("found class")
        try:
            #extract a short title (bibliocommons only returns the short title)
            baseTitle = book.text.split(':')[0].split('(')[0].split('!')[0].strip()
            #remove any formatting before comparison
            removeChars = string.punctuation + string.whitespace
            noPunctuationDesiredTitle = baseTitle.translate(str.maketrans('', '', removeChars)).lower()
            htmlTitleWithoutPunctuation = existingData["shortTitle"].translate(str.maketrans('', '', removeChars)).lower()
            if noPunctuationDesiredTitle == htmlTitleWithoutPunctuation:
                bookFormats = get_book_formats_from_book(book)
                for bookFormat in bookFormats:
                    if bookFormat == "eBook":
                        existingData["numEBooks"] += 1
                    elif bookFormat == "Book":
                        existingData["numBooks"] += 1
                    elif bookFormat == "Audiobook":
                        existingData["numAudioBooks"] += 1
                    else:
                        existingData["numOther"] += 1
        except:
            print("error")
            None
    return existingData

def extract_books_from_bibliocommons_result(soup, desiredTitle, existingData):
    existingData.update({"jeffCoURL" : ""})
    for book in soup.find_all('div', attrs={'class':'cp-search-result-item-content'}):
        try:
            title = book.find('span', attrs={'class':'title-content'}).text
            removeChars = string.punctuation + string.whitespace
            noPunctuationDesiredTitle = title.translate(str.maketrans('', '', removeChars)).lower()
            htmlTitleWithoutPunctuation = existingData["shortTitle"].translate(str.maketrans('', '', removeChars)).lower()
            if noPunctuationDesiredTitle == htmlTitleWithoutPunctuation:
                bookFormats = get_book_formats_from_book(book)
                for bookFormat in bookFormats:
                    if bookFormat == "eBook":
                        existingData["numEBooks"] += 1
                    elif bookFormat == "Book":
                        existingData["numBooks"] += 1
                    elif bookFormat == "Audiobook":
                        existingData["numAudioBooks"] += 1
                    else:
                        existingData["numOther"] += 1
        except:
            print("error")
            None
    return existingData

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
