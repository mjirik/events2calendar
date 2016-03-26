
from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

import datetime
from PyQt4 import QtGui, QtCore
import sys

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
# SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'




class Event2CalendarGUI(QtGui.QWidget):

    def __init__(self):
        super(Event2CalendarGUI, self).__init__()

        self.initUI()

    def initUI(self):

        self.btn = QtGui.QPushButton('Process', self)
        self.btn.move(20, 240)
        self.btn.clicked.connect(self.buttonProcess)

        self.btnQuit = QtGui.QPushButton('Quit', self)
        self.btnQuit.move(200, 240)
        self.btnQuit.clicked.connect(self.buttonQuit)
        # self.le = QtGui.QTextEdit(self)
        # self.le.move(130, 22)

        self.le = QtGui.QTextEdit(self)
        self.le.move(40, 22)

        self.textoutput = QtGui.QTextEdit(self)
        self.textoutput.move(440, 22)
        self.textoutput.setReadOnly(True)


        self.setGeometry(200, 200, 800, 500)
        self.setWindowTitle('Input dialog')
        self.show()

    def buttonQuit(self):
        QtCore.QCoreApplication.instance().quit()

    def buttonProcess(self):
        text = self.le.toPlainText()
        events = parse_text(str(text))
        self.textoutput.setText(str(events))
        # QtCore.QCoreApplication.instance().quit()

    def showDialog(self):

        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog',
            'Enter your name:')

        if ok:
            self.le.setText(str(text))


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials



def create_event(service):
    event = {
        'summary': 'Google I/O 2015',
        'location': '800 Howard St., San Francisco, CA 94103',
        'description': 'A chance to hear more about Google\'s developer products.',
        'start': {
            'dateTime': '2016-03-28T09:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': '2016-03-28T17:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
        'recurrence': [
            'RRULE:FREQ=DAILY;COUNT=2'
        ],
        'attendees': [
            {'email': 'lpage@example.com'},
            {'email': 'sbrin@example.com'},
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()

def create_event_all(service):
    event = {
    'summary': 'Google I/O 2015',
    'location': '800 Howard St., San Francisco, CA 94103',
    'description': 'A chance to hear more about Google\'s developer products.',
    'start': {
        'dateTime': '2016-03-28T09:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
    },
    'end': {
        'dateTime': '2016-03-28T17:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
    },
    'recurrence': [
        'RRULE:FREQ=DAILY;COUNT=2'
    ],
    'attendees': [
        {'email': 'lpage@example.com'},
        {'email': 'sbrin@example.com'},
    ],
    'reminders': {
        'useDefault': False,
        'overrides': [
        {'method': 'email', 'minutes': 24 * 60},
        {'method': 'popup', 'minutes': 10},
        ],
    },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    # print 'Event created: %s' % (event.get('htmlLink'))

def parse_line(linetext):
    """
    Nalezne na radce datum a cas. zbytek je povazovan za sumary
    Args:
        linetext:

    Returns:

    """
    import re
    import dateparser

    # pridej mezery vsude
    linetext = re.sub(r'\.', r'. ', linetext)
    # datum s teckami
    datere = r'\d{1,2}\. *\d{1,2}\.? *\d{0,4}'
    out = re.search(datere, linetext)
    if out is None:
        return None
    datum = out.group(0)
    print (datum)

    linetext = re.sub(datere, '', linetext)

    timere = r'\d{1,2}:\d{2}'

    out = re.search(timere, linetext)

    linetext = re.sub(timere, '', linetext)
    if out is None:
        cas = ''
    else:
        cas = out.group(0)

    # print cas

    parsed = datum + " " + cas
    # print parsed

    dt = dateparser.parse(parsed)
    # print dt
    # print linetext
    event = {
        'sumary': linetext,
        # 'description': 'A chance to hear more about Google\'s developer products.',
        'start': {
            'dateTime': dt.isoformat(),
            # 'timeZone': 'America/Los_Angeles',
        },

    }
    return event

def parse_text(text):
    events = []

    for linetext in text.splitlines():
        event = parse_line(linetext)
        # print event
        if event is not None:
            events.append(event)

    return events

def calendar_processing():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    create_event(service)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

def get_text():
    app = QtGui.QApplication(sys.argv)
    ex = Event2CalendarGUI()
    # sys.exit(app.exec_())
    app.exec_()

if __name__ == '__main__':
    get_text()
    # calendar_processing()
