from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
spreadsheetID = '13Of_OBJgAeYbLtJurRItTpbZ5kEGN1UBjIqX1RrEYNU'
spreadsheetName = 'Library List'

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

def fillSheetWithBookData(booksWithTypeCount):
    sheet = getSheet()
    purgeSheet(sheet)
    writeBookDataToSheet(booksWithTypeCount, sheet)

def writeBookDataToSheet(booksWithTypeCount, sheet):
    #write the headers first
    values = [
        [
            'Title', 'Num eBooks', 'Num physical books', 'Num audio books', 'Num other types', 'URL'
        ]
    ]
    body = {
        'values': values
    }
    header_range = spreadsheetName + '!A1'
    result = sheet.values().update(spreadsheetId=spreadsheetID, range=header_range,valueInputOption='USER_ENTERED', body=body).execute()

    #Now write all the books
    value_range = spreadsheetName + '!A2'
    body = {
        'values': booksWithTypeCount
    }
    result = sheet.values().update(spreadsheetId=spreadsheetID, range=value_range,valueInputOption='USER_ENTERED', body=body).execute()


def purgeSheet(sheet):
    try:
        clear_values_request_body = {}
        rangeToClear = spreadsheetName + '!A:F'
        request = sheet.values().clear(spreadsheetId=spreadsheetID, range=rangeToClear, body=clear_values_request_body)
        response = request.execute()
    except:
        print("error")
        None

if __name__ == '__main__':
    fillSheetWithBookData()
