from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID of the spreadsheet.
spreadsheetID = '13Of_OBJgAeYbLtJurRItTpbZ5kEGN1UBjIqX1RrEYNU'

def getSheet():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'google.credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    return sheet

def getGoodreadsListID():
    sheet = getSheet()

    #get the ID
    sheetRange = "Setup!A1:B2"
    result = sheet.values().get(spreadsheetId=spreadsheetID,range=sheetRange).execute()
    values = result.get('values', [])
    goodReadsUserID = values[0][1]

    #check if there's a sheet if the proper name and create it if it doesn't exist
    spreadsheetName = values[1][1]
    createSheetIfItDoesntExist(sheet, spreadsheetName)

    return goodReadsUserID, spreadsheetName

#get all the books in the CSV
def get_book_titles_from_CSV():

    titles = []

    sheet = getSheet()

    #get the ID
    sheetRange = "Import from Goodreads!B2:S"
    result = sheet.values().get(spreadsheetId=spreadsheetID,range=sheetRange).execute()
    values = result.get('values', [])

    for book in values:
        #only worry about books on "to-read"
        if "to-read" in book[17]:
            title = book[0]
            avgRating = book[7]
            authors = book[1]
            isHugo = False
            if "hugo-winners" in book[15]:
                isHugo = True
            bookData = {
                "fullTitle" : title,
                "avgRating" : avgRating,
                "author" : authors,
                "isHugo" : isHugo
            }
            titles.append(bookData)

    return titles

def createSheetIfItDoesntExist(sheet, sheetTitle):
    try:
        sheetRange = sheetTitle + "!A1"
        result = sheet.values().get(spreadsheetId=spreadsheetID,range=sheetRange).execute()
        values = result.get('values', [])
    except HttpError:
        requests = []
        requests.append({
            "addSheet": {
                "properties": {
                    'title' : sheetTitle
                }
            }
        })
        body = {
            'requests': requests
        }
        result = sheet.batchUpdate(spreadsheetId=spreadsheetID, body=body).execute()

def getDesiredLibraries():
    sheet = getSheet()

    #get the ID
    sheetRange = "Setup!A7:B12"
    result = sheet.values().get(spreadsheetId=spreadsheetID,range=sheetRange).execute()
    values = result.get('values', [])
    desiredLibraries = []
    for value in values:
        if value:
            library = [value[0], value[1]]
            desiredLibraries.append(library)

    return desiredLibraries

def fillSheetWithBookData(booksWithTypeCount, booksMetaData, spreadsheetName, desiredLibraries):
    sheet = getSheet()
    purgeSheet(sheet, spreadsheetName)
    writeBookDataToSheet(booksWithTypeCount, booksMetaData, sheet, spreadsheetName, desiredLibraries)

def writeBookDataToSheet(booksWithTypeCount, booksMetaData, sheet, spreadsheetName, desiredLibraries):
    #write the headers first
    columnHeaders = ['Title', 'Avg Rating', 'Author', 'Is Hugo?', 'Num eBooks', 'Has Overdrive?', 'Num physical books', 'Num audio books', 'Num other types' ]

    for desiredLibrary in desiredLibraries:
        columnHeaders.append(desiredLibrary[0])

    values = [columnHeaders]
    body = {
        'values': values
    }
    header_range = spreadsheetName + '!A1'
    result = sheet.values().update(spreadsheetId=spreadsheetID, range=header_range,valueInputOption='USER_ENTERED', body=body).execute()

    #Now write all the books. This is assuming both arrays are sorted the same. Maybe bad assumption?
    value_range = spreadsheetName + '!A2'
    bookDataToWrite = []
    for bookCounts, bookMeta in zip(booksWithTypeCount,booksMetaData):
        bookData = [bookMeta["fullTitle"], bookMeta["avgRating"], bookMeta["author"], bookMeta["isHugo"], bookCounts["numEBooks"], bookCounts["hasOverdrive"], bookCounts["numBooks"],bookCounts["numAudioBooks"],bookCounts["numOther"]]#,bookCounts["jeffCoURL"],bookCounts["denverURL"]]
        for library in desiredLibraries:
            bookData.append(bookCounts[library[0]])
        bookDataToWrite.append(bookData)
    body = {
        'values': bookDataToWrite
    }
    result = sheet.values().update(spreadsheetId=spreadsheetID, range=value_range,valueInputOption='USER_ENTERED', body=body).execute()


def purgeSheet(sheet, spreadsheetName):
    try:
        clear_values_request_body = {}
        rangeToClear = spreadsheetName + '!A:K'
        request = sheet.values().clear(spreadsheetId=spreadsheetID, range=rangeToClear, body=clear_values_request_body)
        response = request.execute()
    except Exception as e:
        print(e)
        None
