import sqlite3
import datetime

sql_live = """SELECT
    strftime('%Y-%m-%d %H:%M GMT', logdate) AS logdate,
    avg(value) AS value
FROM log
WHERE logdate >= datetime('now', '-180 minutes')
GROUP BY strftime('%Y-%m-%d %H:%M', logdate)
ORDER BY 1;"""

sql_pastday = """SELECT
    strftime('%Y-%m-%d %H:%M GMT', min(logdate)) AS logdate,
    avg(value) AS value
FROM log
WHERE logdate >= datetime('now', '-24 hours')
GROUP BY strftime('%Y-%m-%d %H', logdate), strftime('%M', logdate) / 10
ORDER BY 1;"""

sql_pastweek = """SELECT
    strftime('%Y-%m-%d %H:%M GMT', logdate) AS logdate,
    value
FROM log_byhour
WHERE logdate >= datetime('now', '-7 days')
ORDER BY 1;"""

sql_pastyear = """SELECT
    strftime('%Y-%m-%d 00:00:00 GMT', logdate) AS logdate,
    avg(value) AS value
FROM log_byhour
GROUP BY strftime('%Y-%m-%d', logdate)
HAVING logdate < date('now')
ORDER BY 1;"""

band_pastyear = """SELECT
    min(value) AS min,
    max(value) AS max
FROM log_byhour
GROUP BY strftime('%Y-%m-%d', logdate)
HAVING logdate < date('now')
ORDER BY logdate;"""

sql_update = """INSERT INTO log_byhour
(logdate, value)
SELECT
    strftime('%Y-%m-%d %H:00:00', logdate) AS logdate,
    avg(value) AS value
FROM log
WHERE logdate >= ? AND logdate < ?
GROUP BY strftime('%Y-%m-%d %H', logdate)
ORDER BY 1;"""

def log(value):
    logdate = datetime.datetime.utcnow()
    try:
        con = sqlite3.connect('/var/log/datalog.db')
        with con:
            cur = con.cursor()
            cur.execute('INSERT INTO log (logdate, value) VALUES(?, ?)', (logdate, value))
    except Exception, e:
        print '## datalogger.log ## {0}'.format(e)

def getlog(period):
    import json
    data = {}
    if period == 'pastyear':
        sql = sql_pastyear
        band = band_pastyear
    elif period == 'pastweek':
        sql = sql_pastweek
        band = ''
    elif period == 'pastday':
        sql = sql_pastday
        band = ''
    else:
        sql = sql_live
        band = ''
    con = sqlite3.connect('/var/log/datalog.db', detect_types=sqlite3.PARSE_DECLTYPES)
    with con:
        c = con.cursor()
        c.execute(sql)
        rr = c.fetchall()
        data['series'] = rr
        if band != '':
            c.execute(band)
            rr = c.fetchall()
            data['band'] = rr
        return json.dumps(data)

def update_byhour():
    con = sqlite3.connect('/var/log/datalog.db', detect_types=sqlite3.PARSE_DECLTYPES)
    with con:
        c = con.cursor()
        # Get startDate for incremental update
        c.execute('SELECT MAX(logdate) FROM log_byhour;')
        startDate = c.fetchone()[0]
        if startDate == None:
            # Rascal24 arrival in UK
            startDate = datetime.datetime(2011, 12, 30)
        else:
            startDate = datetime.datetime.strptime(startDate, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours = 1)
        # Get endDate
        c.execute("SELECT strftime('%Y-%m-%d %H:00:00','now');")
        endDate = c.fetchone()[0]
        # Update log_byhour
        c.execute(sql_update, (startDate, endDate))
        rows = c.rowcount
        if rows > 0:
            c.execute("DELETE FROM log WHERE logdate < datetime('now', '-36 hours');")
            # print '## update_byhour ## deleted ' + str(c.rowcount)
        return rows

def init(confirm):
    if confirm:
        logdate = datetime.datetime.utcnow()
        value = 21.2
        con = sqlite3.connect('/var/log/datalog.db')
        with con:
            cur = con.cursor()
            cur.execute('DROP TABLE IF EXISTS log;')
            cur.execute('CREATE TABLE log(logdate TIMESTAMP, value REAL);')
            cur.execute('INSERT INTO log (logdate, value) VALUES(?, ?)', (logdate, value))
        # Read back row to check, then delete
        con = sqlite3.connect('/var/log/datalog.db', detect_types=sqlite3.PARSE_DECLTYPES)
        con.row_factory = sqlite3.Row
        with con:
            c = con.cursor()
            c.execute('select * from log;')
            r = c.fetchone()
            print 'Logdate: ' + r['logdate'].strftime('%a, %d %b %Y %H:%M %Z')
            print 'Value: {0}'.format(r['value'])
            c.execute('delete from log;')
    else:
        print 'Set arg to True to initialise (deletes all data)'

def init_byhour(confirm):
    if confirm:
        logdate = datetime.datetime.utcnow()
        value = 21.2
        con = sqlite3.connect('/var/log/datalog.db')
        with con:
            cur = con.cursor()
            cur.execute('DROP TABLE IF EXISTS log_byhour;')
            cur.execute('CREATE TABLE log_byhour(logdate TIMESTAMP, value REAL);')
            cur.execute('INSERT INTO log_byhour (logdate, value) VALUES(?, ?)', (logdate, value))
        # Read back row to check, then delete
        con = sqlite3.connect('/var/log/datalog.db', detect_types=sqlite3.PARSE_DECLTYPES)
        con.row_factory = sqlite3.Row
        with con:
            c = con.cursor()
            c.execute('select * from log_byhour;')
            r = c.fetchone()
            print 'Logdate: ' + r['logdate'].strftime('%a, %d %b %Y %H:%M %Z')
            print 'Value: {0}'.format(r['value'])
            c.execute('delete from log_byhour;')
    else:
        print 'Set arg to True to initialise (deletes all data)'
