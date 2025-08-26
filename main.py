from flask import Flask
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime
from dateutil import parser

app = Flask(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
start_date = input("Periodo pradzia (YYYY-MM-DD):")
end_date = input("Periodo pabaiga (YYYY-MM-DD):")

dt_start = datetime.strptime(start_date, "%Y-%m-%d")
dt_end = datetime.strptime(end_date, "%Y-%m-%d")

timeMin = dt_start.isoformat() + 'Z'
timeMax = dt_end.isoformat() + 'Z'

@app.route("/")
def main():
    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('calendar', 'v3', credentials=creds)

    events_result = service.events().list(
        calendarId = 'primary', timeMin=timeMin,
        timeMax=timeMax, maxResults=30, singleEvents=True,
        orderBy = 'startTime'
    ).execute()

    events = events_result.get('items', [])

    filtered_events = [
        e for e in events
        if e.get('summary', '').startswith(('NV', 'GV'))
    ]

    counts = {'NV': 0, 'GV': 0}
    durations = {'NV':0, 'GV': 0} #issaugoti valandomis

    if not events:
        print('Nera ivykiu')
    for event in filtered_events:
        summary = event.get('summary', '')
        start = parser.isoparse(event['start']['dateTime'])
        end = parser.isoparse(event['end']['dateTime'])
        duration_valandos = (end - start).total_seconds() / 3600

        for prefix in counts.keys():
            if summary.startswith(prefix):
                counts[prefix] += 1
                durations[prefix] += duration_valandos

    print('Darbovietes:', counts)
    print("isdirbta valandu:", durations)



if __name__ == '__main__':
    app.run()
