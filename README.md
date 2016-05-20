# events2calendar
add multiple events to google calendar. Czech data format is supported DD.MM.YYYY

Input text example:

    prefix zprávy (bude přidán ke všem popisům událostí)
    2.6. schůzka s MT
    3.7. 2016 v 18:30 valná hromada
    schuze bude v 16:30, 23.7.2016
        
        


You will need

1. Turn on the Google Calendar API
2. Install the Google Client Library
    
        pip install --upgrade google-api-python-client

See 

https://developers.google.com/google-apps/calendar/quickstart/python

Additional libraries

        conda install -c ioos httplib2
        pip install dateparser


