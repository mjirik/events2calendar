
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
        BUTTON_Y = 450

        self.BUTTON_Y = BUTTON_Y
        self.calendarId = 'primary'

        self.btn = QtGui.QPushButton('Check text', self)
        self.btn.move(300, BUTTON_Y)
        self.btn.clicked.connect(self.buttonProcess)

        self.btn = QtGui.QPushButton('Check duplicities', self)
        self.btn.move(450, BUTTON_Y)
        self.btn.clicked.connect(self.buttonCheckDuplicities)

        self.btn = QtGui.QPushButton('Add to calendar', self)
        self.btn.move(600, BUTTON_Y)
        self.btn.clicked.connect(self.buttonEvents2Calendar)

        self.btnQuit = QtGui.QPushButton('Quit', self)
        self.btnQuit.move(750, BUTTON_Y)
        self.btnQuit.clicked.connect(self.buttonQuit)
        # self.le = QtGui.QTextEdit(self)
        # self.le.move(130, 22)

        self.le = QtGui.QTextEdit(self)
        self.le.setMinimumSize(400,400)
        self.le.move(20, 22)

        self.textoutput = QtGui.QTextEdit(self)
        self.textoutput.move(440, 22)
        self.textoutput.setMinimumSize(400,400)
        self.textoutput.setReadOnly(True)


        self.setGeometry(200, 200, 860, 500)
        self.setWindowTitle('Event2Calendar')
        self.__create_combobox()

        self.events = []
        self.show()

    def __create_combobox(self):

        e2c = Events2Calendar()
        lid, lsummary = e2c.calendars_list()
        self.calendarsId = lid
        self.calendarsSummary = lsummary
        comboBox = QtGui.QComboBox(self)
        comboBox.addItems(lsummary)
        # comboBox.addItem("motif")
        # comboBox.addItem("Windows")
        # comboBox.addItem("cde")
        # comboBox.addItem("Plastique")
        # comboBox.addItem("Cleanlooks")
        # comboBox.addItem("windowsvista")
        comboBox.move(20, self.BUTTON_Y)
        comboBox.activated.connect(self.comboCalendarFcn)
        self.calendarIdCombo = comboBox

    def comboCalendarFcn(self):
        id = self.calendarIdCombo.currentIndex()
        self.calendarId = self.calendarsId[id]

    def buttonQuit(self):
        QtCore.QCoreApplication.instance().quit()

    def buttonProcess(self):
        text = self.le.toPlainText().toUtf8()
        text = str(text)
        events = parse_text(text)
        self.textoutput.setText(str(events).decode('utf-8'))
        self.events = events
        # QtCore.QCoreApplication.instance().quit()

    def buttonEvents2Calendar(self):
        e2c = Events2Calendar()
        msg = e2c.add_events(self.events, dryrun=False, calendarId=self.calendarId)
        print (msg)
        self.textoutput.setText(str(msg).decode('utf-8'))

    def buttonCheckDuplicities(self):
        e2c = Events2Calendar()
        msg = e2c.add_events(self.events, dryrun=True, calendarId=self.calendarId)
        self.textoutput.setText(str(msg).decode('utf-8'))

    def showDialog(self):

        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog',
            'Enter your name:')

        if ok:
            self.le.setText(str(text))

class Events2Calendar():
    def __init__(self):
        self.init_calendar()

    def init_calendar(self):

        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)

        self.credentials = credentials
        self.service = service


    def calendars_list(self):
        page_token = None
        lid = []
        lsummary = []
        while True:
            calendar_list = self.service.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                lid.append(calendar_list_entry['id'])
                lsummary.append(calendar_list_entry['summary'])
                print (calendar_list_entry['id'], '     ', calendar_list_entry['summary'])
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break
        return lid, lsummary

    def add_events(self, events, calendarId='primary', dryrun=False):

        msg1 = ''
        msg2 = ''
        for event in events:

            # print ('cal id')
            # print (calendarId)
            duplicity, msgi = self.check_duplicity(event, calendarId=calendarId)

            start = event['start'].get('dateTime', event['start'].get('date'))
            if duplicity:
                msg1 = msg1 + 'Skipped: ' + start + ' ' + event['summary'] + '\n'
            else:
                if (not dryrun):
                    print ("adding to calendar")
                    evnt = self.service.events().insert(calendarId=calendarId, body=event).execute()
                msg1 = msg1 + 'Created: ' + start + ' ' + event['summary'] + '\n'

            msg2 = msg2 + msgi

        msg = msg1 + '\nEvents in calendar\n\n' +  msg2
        return msg

    def check_duplicity(self, event, calendarId='primary'):
        msg = ''
        retval = False

        start_dt, end_dt = self.event_time(event)

        eventsResult = self.service.events().list(
            calendarId=calendarId, timeMin=start_dt, timeMax=end_dt,
            # timeZone=tz,
            maxResults=10, singleEvents=True,
            orderBy='startTime').execute()
        events = eventsResult.get('items', [])

        if not events:
            print('No upcoming events found.')
            return False, ''
        for eventi in events:
            msgprefix = ''
            start = eventi['start'].get('dateTime', eventi['start'].get('date'))
            if eventi['summary'] == event['summary']:
                msgprefix = 'Duplicity found: '
                retval = True

            msg = msg + msgprefix + str(start) + ' '
            msg = msg + str(eventi['summary'].encode('utf8')) + '\n'
            # print(start, event['summary'])

        return retval, msg
        # print (events)

    def event_time(self, event):
        # start_dt = datetime.datetime.strptime(event['start']['dateTime'], "%Y-%m-%dT%H:%M:%S")
        # end_dt = datetime.datetime.strptime(event['end']['dateTime'], "%Y-%m-%dT%H:%M:%S")
        start_dt = event['start']['dateTime']
        end_dt = event['end']['dateTime']
        # tz = event['end']['timeZone']

        return start_dt, end_dt#, tz




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


def parse_line(linetext, summaryprefix=''):
    """
    Nalezne na radce datum a cas. zbytek je povazovan za sumary
    Args:
        linetext:

    Returns:

    """
    import re
    import dateparser
    import datetime
    from pytz import timezone
    tzprague = timezone('Europe/Prague')


    # pridej mezery vsude
    # linetext = re.sub(r'\.', r'. ', linetext)
    # remove multiple spaces
    linetext = re.sub(r' +', r' ', linetext)

    timere = r'v? ?\d{1,2}:\d{2}'

    out = re.search(timere, linetext)

    linetext = re.sub(timere, '', linetext)
    if out is None:
        cas = ''
    else:
        cas = out.group(0)

    # swap month and day and add spaces
    linetext = re.sub(r'(\d{1,2})\. *(\d{1,2})\.? *(\d{0,4})', r'\2. \1. \3', linetext)
    # datum s teckami
    datere = r'\d{1,2}\. *\d{1,2}\.? *\d{0,4}'
    out = re.search(datere, linetext)
    if out is None:
        return None
    datum = out.group(0)
    print (datum)

    linetext = re.sub(datere, '', linetext)


    # print cas

    parsed = datum + " " + cas
    # print parsed

    dt = dateparser.parse(parsed)
    dt = tzprague.localize(dt)
    # print dt
    # print linetext
    event = {
        'summary': summaryprefix + ' ' + linetext,
        # 'description': 'A chance to hear more about Google\'s developer products.',
        'start': {
            'dateTime': dt.isoformat(),
            'timeZone': 'Europe/Prague',
        },
        'end': {
            'dateTime': (dt + datetime.timedelta(hours=1)).isoformat(),
            'timeZone': 'Europe/Prague',
            # 'timeZone': 'America/Los_Angeles',
        },


    }
    return event

def parse_text(text):
    events = []
    summaryprefix = ''
    print (text)

    for linetext in text.splitlines():
        print (linetext)
        event = parse_line(linetext, summaryprefix=summaryprefix)
        # print event
        if event is None:
            # print ("toto je prazdny radek")
            # print (linetext)
            summaryprefix = linetext
        else:
            events.append(event)
            # this line is used as summaryprefix


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
