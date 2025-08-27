from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from datetime import datetime, timezone
from dateutil import parser
import os

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Config directory for storing secrets/tokens
CONFIG_DIR = os.path.expanduser("~/.config/google/calendar")
CLIENT_SECRET_FILE = os.path.join(CONFIG_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(CONFIG_DIR, "token.json")

# Make sure directory exists
os.makedirs(CONFIG_DIR, exist_ok=True)

# Input date range
start_date = input("Periodo pradzia (YYYY-MM-DD): ")
end_date = input("Periodo pabaiga (YYYY-MM-DD): ")

dt_start = datetime.strptime(start_date, "%Y-%m-%d")
dt_end = datetime.strptime(end_date, "%Y-%m-%d")

# Ensure timezone-aware ISO format (UTC)
timeMin = dt_start.replace(tzinfo=timezone.utc).isoformat()
timeMax = dt_end.replace(tzinfo=timezone.utc).isoformat()

def main():
    creds = None

    # Load saved credentials if available
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If no valid creds, refresh or run browser auth once
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for next runs
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        os.chmod(TOKEN_FILE, 0o600)  # Restrict file permissions (owner read/write only)

    service = build('calendar', 'v3', credentials=creds)

    events_result = service.events().list(
        calendarId='primary',
        timeMin=timeMin,
        timeMax=timeMax,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    filtered_events = [
        e for e in events
        if e.get('summary', '').startswith(('NV', 'GV'))
    ]

    counts = {'NV': 0, 'GV': 0}
    durations = {'NV': 0, 'GV': 0}  # hours

    if not events:
        print('Nera ivykiu')

    for event in filtered_events:
        summary = event.get('summary', '')
        start_raw = event['start'].get('dateTime', event['start'].get('date'))
        end_raw = event['end'].get('dateTime', event['end'].get('date'))
        start = parser.isoparse(start_raw)
        end = parser.isoparse(end_raw)
        duration_valandos = (end - start).total_seconds() / 3600

        for prefix in counts.keys():
            if summary.startswith(prefix):
                counts[prefix] += 1
                durations[prefix] += duration_valandos

    print('Darbovietes:', counts)
    print("Isdirbta valandu:", {k: round(v, 2) for k, v in durations.items()})


if __name__ == '__main__':
    main()
