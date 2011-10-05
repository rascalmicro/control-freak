from flask import abort, Blueprint, flash, redirect, render_template, request
from flaskext.login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin, AnonymousUser,
                            confirm_login, fresh_login_required)
from jinja2 import TemplateNotFound
from werkzeug import secure_filename

class User(UserMixin):
    def __init__(self, name, id, active=True):
        self.name = name
        self.id = id
        self.active = active
    
    def is_active(self):
        return self.active


class Anonymous(AnonymousUser):
    name = u"Anonymous"


USERS = {
    1: User(u"rascal", 1),
}

USER_NAMES = dict((u.name, u) for u in USERS.itervalues())

editor = Blueprint('editor', __name__, static_url_path='/editor/', static_folder='static', template_folder='templates')

BOILERPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title></title>
    <link rel="stylesheet" type="text/css" href="http://fonts.googleapis.com/css?family=Droid+Sans|Molengo">
    <link rel="stylesheet" type="text/css" href="/static/demo.css">
    <link rel="shortcut icon" href="/static/favicon.ico">
    <script src="/static/jquery-1.5.js"></script>
    <!--[if IE]><script language="javascript" type="text/javascript" src="/excanvas.js"></script><![endif]-->
    <script language="javascript" type="text/javascript" src="/static/jquery.jqplot.js"></script>
    <link rel="stylesheet" type="text/css" href="/static/jquery.jqplot.css" />
</head>
<body>
    <div class="rascalcontent">
        <h1>This is your new page.</h1>
        You can add some text here, or use template variables: {{magic}}
    </div>
    <script language="javascript" type="text/javascript">
    // You could add some Javascript between these script tags, if you want.
    // jQuery and jqPlot are already included in the header above.
    </script>
</body>
</html>
"""

def dirlist(d): # This function heavily based on Martin Skou's connector script for jQuery File Tree
    import os
    noneditable = ["pyc", "pyo"]
    r=['<ul class="jqueryFileTree" style="display: none;">']
    try:
        r=['<ul class="jqueryFileTree" style="display: none;">']
        for f in os.listdir(d):
            ff=os.path.join(d,f)
            if os.path.isdir(ff):
                r.append('<li class="directory collapsed"><img class="delete" src="/editor/static/file-icons/delete.png"><a href="#" rel="%s/">%s</a></li>' % (ff,f))
            else:
                e=os.path.splitext(f)[1][1:] # get .ext and remove dot
                if (e not in noneditable and f != '__init__.py'):
                    r.append('<li class="file ext_%s"><img class="delete" src="/editor/static/file-icons/delete.png" rel="%s"><a href="#" rel="%s">%s</a></li>' % (e,ff,ff,f))
        r.append('</ul>')
    except Exception,e:
        r.append('Could not load directory: %s' % str(e))
        print 'Error: ' + str(e)
    r.append('</ul>')
    return ''.join(r)

def secure_path(path): # Version of Werkzeug's secure_filename trimmed to allow paths through (could be a bad idea)
    if isinstance(path, unicode):
        from unicodedata import normalize
        path = normalize('NFKD', path).encode('ascii', 'ignore')
    return path

def tail(f, n, offset=None):
    """Reads a n lines from f with an offset of offset lines.  The return
    value is a tuple in the form ``(lines, has_more)`` where `has_more` is
    an indicator that is `True` if there are more lines in the file.
    From Armin Ronacher on Stack Overflow: http://stackoverflow.com/questions/136168/get-last-n-lines-of-a-file-with-python-similar-to-tail/692616#692616
    """
    avg_line_length = 74
    to_read = n + (offset or 0)

    while 1:
        try:
            f.seek(int(-(avg_line_length * to_read)), 2)
        except IOError:
            # woops.  apparently file is smaller than what we want
            # to step back, go to the beginning instead
            f.seek(0)
        pos = f.tell()
        lines = f.read().splitlines()
        if len(lines) >= to_read or pos == 0:
            return lines[-to_read:offset and -offset or None], \
                   len(lines) > to_read or pos > 0
        avg_line_length *= 1.3

@editor.route('/editor/config')
@login_required
def config():
    try:
        import subprocess
        process_table = subprocess.Popen('ifconfig', stdout=subprocess.PIPE)
        return render_template('config.html', processes=process_table.communicate()[0])
    except TemplateNotFound:
        abort(404)

@editor.route('/editor/log')
@login_required
def log():
    print("rendering /editor/log")
    try:
        f = open('/var/log/uwsgi/public.log', 'r')
        app_log = '</td></tr>\n<tr><td>'.join(tail(f, 10)[0])
        f.close()
        f = open('/var/log/nginx/access', 'r')
        access_log = '</td></tr>\n<tr><td>'.join(tail(f, 10)[0])
        f.close()
        f = open('/var/log/nginx/error', 'r')
        error_log = '</td></tr>\n<tr><td>'.join(tail(f, 10)[0])
        f.close()
        return render_template('log.html', app=app_log, access=access_log, error=error_log)
    except TemplateNotFound:
        abort(404)

@editor.route('/editor/monitor')
@login_required
def monitor():
    try:
        import subprocess
        process_list = subprocess.Popen('ps', stdout=subprocess.PIPE).communicate()[0].split('\n')
        table = '</td></tr>\n<tr><td>'.join(process_list).replace(' ', '&nbsp;')
        return render_template('monitor.html', processes=table)
    except TemplateNotFound:
        abort(404)

@editor.route('/editor/')
@login_required
def start_edit():
    try:
        return render_template('editor.html', text_to_edit='No file selected')
    except TemplateNotFound:
        abort(404)

@editor.route('/editor/file_delete', methods=['POST'])
@login_required
def file_delete():
    import subprocess
    # subprocess.Popen(['rm', request.form['filename']])
    return redirect('/editor/', 302)

@editor.route('/editor/file_rename', methods=['POST'])
@login_required
def file_rename():
    import subprocess
    # subprocess.Popen(['mv', request.form['old_filename'], request.form['new_filename']])
    return redirect('/editor/', 302)

@editor.route('/editor/get_dirlist', methods=['POST'])
@login_required
def get_dirlist():
    try:
        request.form['dir']
    except KeyError:
        print("Key error in attempt to list directory contents.")
    return str(dirlist(request.form['dir']))

@editor.route('/editor/mark', methods=['POST'])
@login_required
def mark():
    fake = request.form['fake']
    import time
    logfiles = ['/var/log/nginx/access', '/var/log/nginx/error', '/var/log/uwsgi/public.log']
    for file in logfiles:
        f = open(file, 'a')
        f.write('<div class="log-mark">## MARK ## Rascal time: ' + time.strftime('%X %x %Z') + '</div>\n')
        f.close()
    return redirect('/editor/log', 302)

@editor.route('/editor/new_template', methods=['POST'])
@login_required
def new_template():
    name = secure_path(request.form['template-name'])
    f = open('/var/www/public/templates/' + name, 'w')
    f.write(BOILERPLATE)
    f.close()
    return redirect('/editor/', 302)


@editor.route('/editor/read', methods=['POST'])
@login_required
def read_contents():
    path = secure_path(request.form['path'])
    f = open('/var/www/public/' + path, 'r')
    return f.read()

@editor.route('/editor/reload', methods=['POST'])
@login_required
def reload():
    import subprocess
    subprocess.Popen(['touch', '/etc/uwsgi/public.ini'])
    return render_template('editor.html')

@editor.route('/editor/save', methods=['POST'])
@login_required
def save():
    root = '/var/www/public/'
    path = secure_path(request.form['path'])
    f = open(root + path, 'w')
    f.write(request.form['text'])
    f.close()
    return '0'

def get_hash(username):
    f = open('/etc/passwd', 'r')
    accounts = f.readlines()
    for account in accounts:
        if account.startswith(username):
            return account.split(':')[1]
    import os
    return os.urandom(13) # In the event that the account doesn't exist, return random noise to prevent login

@editor.route("/editor/login", methods=["GET", "POST"])
def login():
    import crypt
    if request.method == "POST" and "password" in request.form:
        pw = request.form["password"]
        hash = get_hash('root')
        salt = hash[0:2]
        if crypt.crypt(pw, salt) == hash:
            if login_user(USER_NAMES['rascal']):
                flash("Logged in!")
                return redirect(request.args.get("next") or "/")
            else:
                flash("Sorry, but you could not log in.")
        else:
            flash("Sorry, but you could not log in.")
    return render_template("login.html")


@editor.route("/editor/reauth", methods=["GET", "POST"])
@login_required
def reauth():
    if request.method == "POST":
        confirm_login()
        flash(u"Reauthenticated.")
        return redirect(request.args.get("next") or "/")
    return render_template("reauth.html")


@editor.route("/editor/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect("/")

