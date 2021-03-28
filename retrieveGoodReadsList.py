import requests
import json
import xml.etree.ElementTree as ET
import urllib.parse
import bookFinder as bookFinder
import googleSheets as gs
import math
from datetime import datetime

#old goodreads way to get it from their API
def get_book_titles_from_Goodreads(goodreadsListID):
    with open('goodreads.credentials.json') as f:
        goodreadsCreds = json.load(f)

    titles = []
    currentPageNum = 1
    maxPages = 1
    while currentPageNum <= maxPages:
        response = requests.get("https://www.goodreads.com/review/list?v=2&key=" + goodreadsCreds["api_key"] + "&id=" + goodreadsListID + "&shelf=to-read&per_page=200&page=" + str(currentPageNum))

        tree = ET.fromstring(response.text)

        reviews = tree.find('reviews')
        if currentPageNum == 1:
            total = reviews.attrib['total']
            maxPages = math.ceil(int(total) / 200)

        for review in reviews:
            book = review.find('book')
            title = book.find('title').text
            avgRating = book.find('average_rating').text
            authors = book.find('authors')
            authorsText = ""
            for author in authors:
                authorsText += author.find('name').text + " "
            isHugo = False
            shelves = review.find('shelves')
            for shelf in shelves:
                if shelf.attrib['name'] == "hugo-winners":
                    isHugo = True
                    break
            bookData = {
                "fullTitle" : title,
                "avgRating" : avgRating,
                "author" : authorsText,
                "isHugo" : isHugo
            }
            titles.append(bookData)
        currentPageNum += 1

    return titles

def add_search_URLs(listOfTitles, desiredLibraries):
    titlesWithURLs = []
    for bookData in listOfTitles:
        title = bookData["fullTitle"]
        #strip off the ( because the full title almost never returns something
        title = title.split('(')[0].strip()
        #need to just get the title before a : or a ! because later on in the process, we only grab the base title from the HTML parsing
        baseTitle = title.split(':')[0].split('!')[0].strip()
        titleWithURL = [baseTitle]
        for baseLibraryURL in desiredLibraries:
            if "bibliocommons" in baseLibraryURL[1]:
                encodedTitle = urllib.parse.quote_plus(baseTitle)
            else:
                encodedTitle = urllib.parse.quote(baseTitle)
            seachString = baseLibraryURL[1] + encodedTitle
            titleWithURL.append(seachString)

        titlesWithURLs.append(titleWithURL)

    return titlesWithURLs

startTime = datetime.now()
print(startTime)
goodreadsListID, spreadsheetName = gs.getGoodreadsListID()
listOfTitles = gs.get_book_titles_from_CSV()

#bookMetaData = {
#    "fullTitle" : "Hominids",
#    "avgRating" : "3.7",
#     "isHugo" : "False",
#     "author" : "Robert J. Sawyer"
#}
#listOfTitles = [bookMetaData]

desiredLibraries = gs.getDesiredLibraries()
titlesWithURLs = add_search_URLs(listOfTitles, desiredLibraries)
allBookData = bookFinder.build_full_results_from_search(titlesWithURLs, desiredLibraries)
gs.fillSheetWithBookData(allBookData, listOfTitles, spreadsheetName, desiredLibraries)

print(datetime.now() - startTime)
