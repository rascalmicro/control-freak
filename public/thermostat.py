TARGET_PATH = '/var/www/public/thermostat-target.txt'
DEFAULT_TEMPERATURE = 56.0

def update_calendar_file():
    import urllib
    urllib.urlretrieve(CALENDAR_URL, LOCAL_CALENDAR)

def get_target_temp(calendar_path, timezone_name):
    import datetime, icalendar, pytz

    f = open(TARGET_PATH, 'r')
    override = f.read()
    if (override[0:5] != 'abort'):
        return str(override)

    days = list(['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'])

    now = datetime.datetime.now(pytz.timezone(timezone_name))
    today = days[now.weekday()]
    events = icalendar.Calendar.from_string(open(calendar_path,'rb').read()).walk('VEVENT')
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
    import subprocess
    cmd = 'i2cget -y 0 ' + hex(address) + ' 0x00 w'
    subp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    try: 
        data = int(subp.communicate()[0].strip(), 16)
    except ValueError:
        print 'Couldn\'t get reading from sensor'
        return float('NaN')
    return ((data % 0x0100 * 16) + (data / 0x1000)) * 0.0625
