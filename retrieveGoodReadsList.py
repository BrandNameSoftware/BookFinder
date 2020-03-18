import requests
import json
import xml.etree.ElementTree as ET
import urllib.parse

def get_book_titles_from_Goodreads():
    with open('goodreads.credentials.json') as f:
        goodreadsCreds = json.load(f)

    response = requests.get("https://www.goodreads.com/review/list?v=2&key=" + goodreadsCreds["api_key"] + "&id=" + goodreadsCreds["user_id"] + "&shelf=to-read&per_page=200")

    tree = ET.fromstring(response.text)
    #root = tree.getroot()
    reviews = tree.find('reviews')
    titles = []
    for review in reviews:
        title = review.find('book').find('title').text
        titles.append(title)

    #print(titles)
    return titles

def add_search_URLs(listOfTitles, baseLibraryURL):
    titlesWithURLs = []
    for title in listOfTitles:
        #need to just get the title before a : or a () because later on in the process, we only grab the base title from the HTML parsing
        baseTitle = title.split(':')[0].split('(')[0].strip()
        encodedTitle = urllib.parse.quote_plus(title)
        titleWithURL = [baseTitle, title, baseLibraryURL + encodedTitle]
        titlesWithURLs.append(titleWithURL)

    print(titlesWithURLs)
    return titlesWithURLs

listOfTitles = get_book_titles_from_Goodreads()
add_search_URLs(listOfTitles, "https://jeffcolibrary.bibliocommons.com/v2/search?searchType=smart&query=")
