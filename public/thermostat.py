TARGET_PATH = '/var/www/public/thermostat-target.txt'
DEFAULT_TEMPERATURE = 56.0
LOCAL_CALENDAR = '/var/www/public/static/basic.ics'
CALENDAR_URL = 'https://www.google.com/calendar/ical/0c3lie03m3ajg6j6numm2gf1l4%40group.calendar.google.com/public/basic.ics'

def update_calendar_file():
    import urllib
    urllib.urlretrieve(CALENDAR_URL, LOCAL_CALENDAR)

def get_event_list(calendar_path):
    import icalendar
    cal = icalendar.Calendar.from_string(open(calendar_path,'rb').read())
    return cal.walk('VEVENT')

def get_target_temp(calendar_path, timezone_name):
    import datetime, pytz

    f = open(TARGET_PATH, 'r')
    override = f.read()
    if (override[0:2] != 'ab'):
        return str(override)

    days = list(['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'])

    now = datetime.datetime.now(pytz.timezone(timezone_name))
    today = days[now.weekday()]
    events = get_event_list(calendar_path)
    for event in events:
        if event_is_today(event, today) and event_is_now(event, now):
            return float(event.decoded('summary'))
    print "Temperature not found in calendar. Using default."
    return DEFAULT_TEMPERATURE

def event_is_today(event, today):
    try:
        freq = event.decoded('rrule')['FREQ'].pop()
    except KeyError:
        freq = None
    try:
        byday = event.decoded('rrule')['BYDAY']
    except KeyError:
        byday = []
    if (freq == 'DAILY') or (today in byday):
        return True
    else:
        return False

def event_is_now(event, now):
    start = event.decoded('dtstart').time()
    end = event.decoded('dtend').time()
    if start < now.time() and end > now.time():
        return True
    else:
        return False

def read_sensor(address):
    import pytronics
    try: 
        data = pytronics.i2cRead(address, size = 'W')
    except:
        print 'Couldn\'t get reading from sensor'
        return 0.0
    return ((data % 0x0100 * 16) + (data / 0x1000)) * 0.0625
