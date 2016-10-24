# -*- coding: utf-8 -*-
from __future__ import print_function
import logging
logger = logging.getLogger(__name__)
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
import re
import copy

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
# SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'




class Event2CalendarGUI(QtGui.QWidget):

    def __init__(self):
        super(Event2CalendarGUI, self).__init__()
        # self.e2c = None
        self.e2c = Events2Calendar()
        self.mevents = self.e2c.mevents
        self.initUI()
        self._text_changed_and_events_not_updated = True

    def initUI(self):
        BUTTON_Y = 435

        self.BUTTON_Y = BUTTON_Y
        self.calendarId = 'primary'
        self.event_i = -1

        self.btn = QtGui.QPushButton('Debug parser', self)
        self.btn.move(300, BUTTON_Y)
        self.btn.clicked.connect(self.buttonCheck)

        self.btn = QtGui.QPushButton('Debug duplicities', self)
        self.btn.move(500, BUTTON_Y)
        self.btn.clicked.connect(self.buttonCheckDuplicities)

        self.btn = QtGui.QPushButton('Add all', self)
        self.btn.move(600, BUTTON_Y + 30)
        self.btn.clicked.connect(self.buttonEvents2Calendar)

        self.btnQuit = QtGui.QPushButton('Quit', self)
        self.btnQuit.move(750, BUTTON_Y + 30)
        self.btnQuit.clicked.connect(self.buttonQuit)
        # self.le = QtGui.QTextEdit(self)
        # self.le.move(130, 22)

        self.btn = QtGui.QPushButton('<', self)
        self.btn.move(300, BUTTON_Y + 30)
        self.btn.clicked.connect(self.buttonPrev)

        self.btn = QtGui.QPushButton('>', self)
        self.btn.move(400, BUTTON_Y + 30)
        self.btn.clicked.connect(self.buttonNext)


        self.btn = QtGui.QPushButton('Add', self)
        self.btn.move(500, BUTTON_Y + 30)
        self.btn.clicked.connect(self.buttonAdd)

        self.input_textbox = QtGui.QTextEdit(self)
        self.input_textbox.setMinimumSize(400, 400)
        self.input_textbox.move(20, 22)
        self.input_textbox.textChanged.connect(self.__text_is_changed)
        self.input_textbox.setText("one line summary prefix to all fallowing events\n1.1. event\nevent 2 2.1.2016 13:00")
        self.input_textbox.selectAll()
        self.input_textbox.setFocus()

        self.textoutput = QtGui.QTextEdit(self)
        self.textoutput.move(440, 22)
        self.textoutput.setMinimumSize(400,400)
        self.textoutput.setReadOnly(True)


        self.setGeometry(200, 200, 860, 500)
        self.setWindowTitle('Event2Calendar')
        self.__create_combobox()

        self.show()



    def __text_is_changed(self):
        self._text_changed_and_events_not_updated = True

    def __create_combobox(self):

        lid, lsummary = self.e2c.calendars_list()
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

    def buttonCheck(self):
        self.__update_events_parse_text()
        self.textoutput.setText(str(self.mevents).decode('utf-8'))
        self.mevents = self.mevents
        # QtCore.QCoreApplication.instance().quit()

    def __update_events(self):
        self.__update_events_parse_text()
        self.__update_events_check_duplicities()
        self._text_changed_and_events_not_updated = False

    def __update_events_if_necessary(self):
        if self._text_changed_and_events_not_updated is True:
            self.__update_events()


    def __update_events_parse_text(self):
        text = self.input_textbox.toPlainText().toUtf8()
        text = str(text).decode("utf8")
        self.mevents = self.e2c.parse_text(text)

    def __update_events_check_duplicities(self):
        if self.e2c is None:
            self.e2c = Events2Calendar()
        msg = self.e2c.update_events_for_duplicity(self.mevents, dryrun=True, calendarId=self.calendarId)

    def buttonNext(self):
        self.event_i += 1
        if self.event_i >= len(self.mevents):
            self.event_i = 0
        self.__show_event_i()

    def buttonPrev(self):
        self.event_i -= 1
        if self.event_i < 0:
            self.event_i = len(self.mevents) - 1
        self.__show_event_i()

    def _format_event(self, event):
        start = event['start'].get('dateTime', event['start'].get('date'))
        dt = start.split("T")
        # logger.debug("==== start")
        # logger.debug(str(start))
        # logger.debug(dt)
        # logger.debug(eventi["start"])
        # import ipdb; ipdb.set_trace()
        eisummary = event['summary']
        formated = "<b>" + str(dt[0]) + "</b><br></br>"
        if len(dt) > 1:
            formated += str(dt[1]) + "<br></br>"
        formated += eisummary

        return formated

    def _format_colliding_events(self, event_i=None):
        msg = ""
        if event_i is None:
            event_i = self.event_i
        mevent = self.mevents[event_i]
        for event in mevent["colliding events"]:
            text = self._format_event(event)
            msg = msg + "<br></br><br></br>" + text
        return msg


    def __show_event_i(self):
        import copy
        self.__update_events_if_necessary()
        if len(self.mevents) > 0:
            input_text = copy.copy(self.mevents[self.event_i]['input text'])
            # self.textoutput.setText(
            html_textoutput = \
                "" + str(self.event_i) + '<br></br>\n'\
                + input_text + '<br></br>\n' \
                + '<br></br>\n' \
                + "<b>" + self.mevents[self.event_i]['status'] + '</b><br></br>\n\n' \
                + "" + self._format_event(self.mevents[self.event_i]['new event']) + '<br></br><br></br>\n\n' \
                + ""\
                + "" + self._format_colliding_events(self.event_i) + '<br></br>\n'
                # + "" + self.mevents[self.event_i]['msg'] + '<br></br>\n'
                # "<b>" + self.mevents[self.event_i]['msg_collision'] + '</b><br></br>\n'
                #.decode('utf-8')

            self.textoutput.setHtml(html_textoutput)
            # make processed line bold
            text = str(self.input_textbox.toPlainText().toUtf8()).decode("utf8")
            print (" --------")
            print (text)
            print (" ---")
            print (input_text)
            input_text.encode("utf8")
            text.encode("utf8")
            html_text = re.compile('(' + input_text.encode("utf8") + ")").sub(r"<b>\1</b>", text.encode("utf8")).decode("utf8")
            print (html_text)
            html_text = re.compile(r'\n').sub(r"<br></br>\n", html_text)
            print (html_text)
            self.input_textbox.setHtml(html_text)

    def buttonAdd(self):
        self.e2c.insert_event(
            self.calendarId,
            self.mevents[self.event_i]['new event']
        )

    def buttonEvents2Calendar(self):
        msg = self.e2c.update_events_for_duplicity(self.mevents, dryrun=False, calendarId=self.calendarId)
        print (msg)
        self.textoutput.setText(str(msg).decode('utf-8'))

    def buttonCheckDuplicities(self):
        msg = self.e2c.update_events_for_duplicity(self.mevents, dryrun=True, calendarId=self.calendarId)
        self.textoutput.setText(str(msg).decode('utf-8'))

    def showDialog(self):

        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog',
            'Enter your name:')

        if ok:
            self.input_textbox.setText(str(text))

class Events2Calendar():
    def __init__(self):
        self.init_calendar()
        self.mevents = []

    def init_calendar(self):

        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)

        self.credentials = credentials
        self.service = service

    def parse_text(self, text):

        events = []
        summaryprefix = ''
        prev_line_date = ""
        print (text)

        for linetext in text.splitlines():
            print (linetext)
            # filtered_linetext = li
            filtered_linetext = self.filter_text(copy.copy(linetext))
            event, prev_line_date = parse_line(filtered_linetext, summaryprefix=summaryprefix, prev_line_date=prev_line_date)
            # print event
            if event is None:
                # print ("toto je prazdny radek")
                # print (linetext)
                summaryprefix = linetext
            else:
                events.append({'new event': event, 'input text': linetext, 'summaryprefix':summaryprefix})
                # this line is used as summaryprefix

        self.mevents = events
        return self.mevents

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

    def update_events_for_duplicity(self, mevents, calendarId='primary', dryrun=False):

        for meta_event in mevents:
            new_event = meta_event['new event']

            # print ('cal id')
            # print (calendarId)
            duplicity, msgi, collision_event_summary, events = self.check_duplicity(new_event, calendarId=calendarId)
            meta_event['duplicity'] = duplicity
            meta_event['msgi'] = msgi
            meta_event['collision_event_summary'] = collision_event_summary
            meta_event["colliding events"] = events

        self.__create_events_messages(mevents, calendarId=calendarId, dryrun=dryrun)

    def _format_event(self, event):
        eventi = event["new event"]
        start = eventi['start'].get('dateTime', eventi['start'].get('date'))
        # dt = start.split("T")
        # logger.debug("==== start")
        # logger.debug(str(start))
        # logger.debug(dt)
        # logger.debug(eventi["start"])
        # import ipdb; ipdb.set_trace()
        eisummary = str(eventi['summary'].encode('utf8'))
        formated = str(start) + "\n" + eisummary
        return formated

    def __create_events_messages(self, mevents, calendarId='primary', dryrun=False):
        msg1 = ''
        msg2 = ''
        for meta_event in mevents:
            new_event = meta_event['new event']
            duplicity = meta_event['duplicity']
            msgi = meta_event['msgi']
            collision_event_summary = meta_event['collision_event_summary']


            start = new_event['start'].get('dateTime', new_event['start'].get('date'))
            msg_event = ''
            msg_collision = ''
            if duplicity == 'full':
                msg_event = start + ' ' + new_event['summary'] + '\n\n'
                msg_status = 'Skipped'
            else:
                if (not dryrun):
                    print ("adding to calendar")
                    self.insert_event(calendarId, new_event)
                if duplicity == 'particular':
                    msg_status = 'Created (with collision)'
                    msg_event = start + ' ' + new_event['summary']
                    msg_collision = '\nCollision: ' + collision_event_summary + '\n\n'
                else:
                    msg_status = 'Created: '
                    msg_event = start + ' ' + new_event['summary'] + '\n\n'
            meta_event['msg'] = msg_event
            meta_event['status'] = msg_status
            meta_event['msg_collision'] = msg_collision

            msg1 = msg1 + msg_status + ": " + msg_event

            msg2 = msg2 + msgi # .decode("utf8")

        msg = msg1 + '\nEvents in calendar\n\n' +  msg2
        return msg

    def insert_event(self, calendarId, new_event):
        evnt = self.service.events().insert(calendarId=calendarId, body=new_event).execute()


    def check_duplicity(self, event, calendarId='primary'):
        msg = ''
        retval = 'no'
        eventisum_utf8 = ''

        esummary_utf8 = event['summary'].encode('utf8')
        print ("Checked event: " + esummary_utf8)

        start_dt, end_dt = self.event_time(event)
        print (start_dt)

        eventsResult = self.service.events().list(
            calendarId=calendarId, timeMin=start_dt, timeMax=end_dt,
            # timeZone=tz,
            maxResults=10, singleEvents=True,
            orderBy='startTime').execute()
        events = eventsResult.get('items', [])

        if not events:
            print('No upcoming events found.')
            return False, '', '', events
        for eventi in events:
            summary_utf8 = eventi["summary"].encode("utf8")
            msgprefix = ''
            start = eventi['start'].get('dateTime', eventi['start'].get('date'))
            eisummary = summary_utf8
            # eisummary = str(eventi['summary'].encode('utf8'))
            print (eisummary)
            if esummary_utf8 == eisummary:
                msgprefix = 'Duplicity found: '
                retval = "full"
            else:
                retval = 'particular'
                eventisum_utf8 = summary_utf8


            msg = msg + msgprefix + str(start) + ' '
            msg = msg + summary_utf8 + '\n'
            # print(start, event['summary'])

        return retval, msg.decode("utf8"), eventisum_utf8.decode("utf8"), events
        # print (events)

    def event_time(self, event):
        # start_dt = datetime.datetime.strptime(event['start']['dateTime'], "%Y-%m-%dT%H:%M:%S")
        # end_dt = datetime.datetime.strptime(event['end']['dateTime'], "%Y-%m-%dT%H:%M:%S")
        start_dt = event['start']['dateTime']
        end_dt = event['end']['dateTime']
        # tz = event['end']['timeZone']

        return start_dt, end_dt#, tz

    def filter_text(self, text):
        self.text_filters = [
            "\\bpo\\b\\.?",
            "\\bút\\b\\.?",
            "\\but\\b\\.?",
            "\\bst\\b\\.?",
            "\\bčt\\b\\.?",
            "\\bct\\b\\.?",
            "\\bpá\\b\\.?",
            "\\bpa\\b\\.?",
            "\\bso\\b\\.?",
            "\\bne\\b\\.?",
        ]
        for text_filter in self.text_filters:
            text = re.sub(text_filter, "", text, flags=re.IGNORECASE)
        return text





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


def parse_line(linetext, summaryprefix='', prev_line_date=""):
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

    timere = r' ?\d{1,2}:\d{2}'

    out_time = re.search(timere, linetext)

    linetext = re.sub(timere, '', linetext, 1)
    if out_time is None:
        cas = ''
    else:
        cas = out_time.group(0)

    # swap month and day and add spaces
    linetext = re.sub(r'(\d{1,2})\. *(\d{1,2})\.? *(\d{0,4})', r'\2. \1. \3', linetext)
    print ("date after day-month swap")
    print (linetext)
    print("================")
    # datum s teckami
    datere = r'\d{1,2}\. *\d{1,2}\.? *\d{0,4}'
    out_date = re.search(datere, linetext)
    
    if out_date is None:
        if out_time is None:
            return None, ""
        else:
            datum = prev_line_date
    else:
        datum = out_date.group(0)
    print (datum)

    prev_line_date = datum
    linetext = re.sub(datere, '', linetext)


    # print cas

    parsed = datum + " " + cas
    print (parsed)

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
    return event, prev_line_date

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
