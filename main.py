from http.cookiejar import month

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
date_from_console = input("data (YYYY-MM-DD):")
dt = datetime.strptime(date_from_console, "%Y-%m-%d")

def main():
    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('calendar', 'v3', credentials=creds)

    exact_date = dt.isoformat() + 'Z'

    events_result = service.events().list(
        calendarId = 'primary', timeMin=exact_date,
        maxResults=30, singleEvents=True,
        orderBy = 'startTime'
    ).execute()

    events = events_result.get('items', [])

    filtered_events = [
        e for e in events
        if e.get('summary', '').startswith(('NV', 'GV'))
    ]

    if not events:
        print('Nera ivykiu')
    for event in filtered_events:
        start = datetime.fromisoformat(event['start']['dateTime'])
        end = datetime.fromisoformat(event['end']['dateTime'])
        duration = end - start
        print(duration.total_seconds()/3600, event['summary'], event['start']['dateTime'])

if __name__ == '__main__':
    main()