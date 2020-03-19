import requests
import json
import xml.etree.ElementTree as ET
import urllib.parse
import bookFinder as bookFinder
import writeToGoogleSheets as wtgs

def get_book_titles_from_Goodreads():
    with open('goodreads.credentials.json') as f:
        goodreadsCreds = json.load(f)

    response = requests.get("https://www.goodreads.com/review/list?v=2&key=" + goodreadsCreds["api_key"] + "&id=" + goodreadsCreds["user_id"] + "&shelf=to-read&per_page=200")

    tree = ET.fromstring(response.text)
    #root = tree.getroot()
    reviews = tree.find('reviews')
    titles = []
    for review in reviews:
        book = review.find('book')
        title = book.find('title').text
        avgRating = book.find('average_rating').text
        bookData = {
            "fullTitle" : title,
            "avgRating" : avgRating
        }
        titles.append(bookData)

    return titles

def add_search_URLs(listOfTitles, baseLibraryURL):
    titlesWithURLs = []
    for bookData in listOfTitles:
        title = bookData["fullTitle"]
        #need to just get the title before a : or a () because later on in the process, we only grab the base title from the HTML parsing
        baseTitle = title.split(':')[0].split('(')[0].split('!')[0].strip()
        encodedTitle = urllib.parse.quote_plus(title)
        titleWithURL = [baseTitle, baseLibraryURL + encodedTitle]
        titlesWithURLs.append(titleWithURL)

    return titlesWithURLs

listOfTitles = get_book_titles_from_Goodreads()
#bookMetaData = {
#    "fullTitle" : "How Not to Die: Discover the Foods Scientifically Proven to Prevent and Reverse Disease",
#    "avgRating" : "4.2"
#}
l#istOfTitles = [bookMetaData]
titlesWithURLs = add_search_URLs(listOfTitles, "https://jeffcolibrary.bibliocommons.com/v2/search?searchType=smart&query=")
allBookData = bookFinder.build_full_results_from_search(titlesWithURLs)
wtgs.fillSheetWithBookData(allBookData, listOfTitles)
