import requests
import json
import xml.etree.ElementTree as ET
import urllib.parse
import bookFinder as bookFinder
import writeToGoogleSheets as wtgs
import math

def get_book_titles_from_Goodreads():
    with open('goodreads.credentials.json') as f:
        goodreadsCreds = json.load(f)

    titles = []
    currentPageNum = 1
    maxPages = 1
    while currentPageNum <= maxPages:
        response = requests.get("https://www.goodreads.com/review/list?v=2&key=" + goodreadsCreds["api_key"] + "&id=" + goodreadsCreds["user_id"] + "&shelf=to-read&per_page=200&page=" + str(currentPageNum))

        tree = ET.fromstring(response.text)

        reviews = tree.find('reviews')
        if currentPageNum == 1:
            total = reviews.attrib['total']
            maxPages = math.ceil(int(total) / 200)

        for review in reviews:
            book = review.find('book')
            title = book.find('title').text
            avgRating = book.find('average_rating').text
            bookData = {
                "fullTitle" : title,
                "avgRating" : avgRating
            }
            titles.append(bookData)
        currentPageNum += 1

    return titles

def add_search_URLs(listOfTitles, desiredLibraries):
    titlesWithURLs = []
    for bookData in listOfTitles:
        title = bookData["fullTitle"]
        #strip off the () because the full title almost never returns something
        title = title.split('()')[0]
        #need to just get the title before a : or a ! because later on in the process, we only grab the base title from the HTML parsing
        baseTitle = title.split(':')[0].split('!')[0].strip()
        titleWithURL = [baseTitle]
        for baseLibraryURL in desiredLibraries:
            if "bibliocommons" in baseLibraryURL[1]:
                encodedTitle = urllib.parse.quote_plus(title)
            else:
                encodedTitle = urllib.parse.quote(title)
            seachString = baseLibraryURL[1] + encodedTitle
            titleWithURL.append(seachString)

        titlesWithURLs.append(titleWithURL)

    return titlesWithURLs

listOfTitles = get_book_titles_from_Goodreads()
#bookMetaData = {
#    "fullTitle" : "How Not to Die: Discover the Foods Scientifically Proven to Prevent and Reverse Disease",
#    "avgRating" : "4.2"
#}
#listOfTitles = [bookMetaData]
desiredLibraries = wtgs.getDesiredLibraries()
titlesWithURLs = add_search_URLs(listOfTitles, desiredLibraries)
allBookData = bookFinder.build_full_results_from_search(titlesWithURLs)
wtgs.fillSheetWithBookData(allBookData, listOfTitles)
