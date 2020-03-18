import requests
import json
import xml.etree.ElementTree as ET

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
        print(title)
        titles.append(title)

    #print(titles)
    return titles

get_book_titles_from_Goodreads()
