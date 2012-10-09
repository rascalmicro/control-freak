from flask import abort, Blueprint, flash, Flask, redirect, render_template, request, url_for
from flask.ext.login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin, AnonymousUser,
                            confirm_login, fresh_login_required)
from jinja2 import TemplateNotFound
from werkzeug import secure_filename

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'ico', 'html', 'css', 'js', 'py'])
CONFIG_FILE = '/var/www/editor/static/editor.conf'

editor = Flask(__name__)

# Include "no-cache" header in all POST responses
@editor.after_request
def add_no_cache(response):
    if request.method == 'POST':
        response.cache_control.no_cache = True
    return response

class User(UserMixin):
    def __init__(self, name, id, active=True):
        self.name = name
        self.id = id
        self.active = active
    
    def is_active(self):
        return self.active

# The redirect for static files below is only needed when using Flask's
# built-in server for debugging. Normally, Nginx serves all of the
# static files, bypassing uWSGI entirely.

@editor.route('/editor/static/<path:path>')
def redirect_to_static(path):
    return redirect('/static/' + path, 302)

## login support
class Anonymous(AnonymousUser):
    name = u'Anonymous'

PASSWD_FILE = '/etc/passwd'
# PASSWD_FILE = '/var/www/passwd'

USERS = {
    1: User(u'rascal', 1),
}

USER_NAMES = dict((u.name, u) for u in USERS.itervalues())

SECRET_KEY = 'rascal'
DEBUG = True

editor.config.from_object(__name__)

login_manager = LoginManager()

login_manager.anonymous_user = Anonymous
login_manager.login_view = '/editor/auth'
login_manager.login_message = u'Please log in to access this page.'
login_manager.refresh_view = '/editor/reauth'

@login_manager.user_loader
def load_user(id):
    return USERS.get(int(id))

login_manager.setup_app(editor)

def get_hash(username):
#     f = open('/etc/passwd', 'r')
    f = open(PASSWD_FILE, 'r')
    accounts = f.readlines()
    for account in accounts:
        if account.startswith(username):
            return account.split(':')[1]
    import os
    return os.urandom(13) # In the event that the account doesn't exist, return random noise to prevent login

@editor.route('/editor/auth', methods=['GET', 'POST'])
def auth():
    import crypt, ConfigParser
    section = 'Login'
    key = 'showPassword'
    if request.method == 'POST' and 'password' in request.form:
        # Save show password preference in editor config
        showPassword = True if 'showPassword' in request.form else False
        try:
            config = ConfigParser.SafeConfigParser()
            config.optionxform = str    # Don't convert to lower case
            config.read(CONFIG_FILE)
            if not config.has_section(section):
                config.add_section(section)
            config.set(section, key, str(showPassword))
            with open(CONFIG_FILE, 'wb') as configfile:
                config.write(configfile)
        except Exception, e:
            print '## auth save_pref ## Unexpected error: %s' % str(e)
        # Validate password
        pw = request.form['password']
        hash = get_hash('root')
        salt = hash[0:2]
        if crypt.crypt(pw, salt) == hash:
            if login_user(USER_NAMES['rascal']):
                flash('Logged in!')
                return redirect(request.args.get('next') or '/')
            else:
                flash('Sorry, but you could not log in.')
        else:
            flash('Sorry, but you could not log in.')
    # Get show password preference
    config = ConfigParser.SafeConfigParser()
    config.read(CONFIG_FILE)
    try:
        showPassword = config.getboolean(section, key)
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        showPassword = False
    # Set type of password input element (auth page uses this to sets checkbox state)
    pwtype = 'text' if showPassword else 'password'            
    return render_template('auth.html', type=pwtype)

@editor.route('/editor/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.')
    return redirect('/')

## editor functions
# Start editor specified by editor-xx file
# editor-cm (CodeMirror) is the default
@editor.route('/editor/')
@login_required
def start_edit():
    import ConfigParser
    config = ConfigParser.SafeConfigParser()
    config.read(CONFIG_FILE)
    try:
        editor = config.get('Advanced', 'editor')
    except:
        editor = 'editor-cm'
    try:
        return render_template(editor + '.html', text_to_edit='No file selected')
    except TemplateNotFound:
        abort(404)

# Directory management
def dirlist(d): # This function heavily based on Martin Skou's connector script for jQuery File Tree
    import os
    print '## dirlist ## ' + d
    noneditable = ['pyc', 'pyo']
    r=['<ul class="jqueryFileTree" style="display: none;">']
    s=[]
    try:
        for f in sorted(os.listdir(d), key=unicode.lower):
            ff=os.path.join(d,f)
            if os.path.isdir(ff):
                r.append('<li class="directory collapsed"><img src="/editor/static/images/file-icons/delete.png"><a href="#" rel="%s/">%s</a></li>' % (ff,f))
            else:
                e=os.path.splitext(f)[1][1:] # get .ext and remove dot
                if (e not in noneditable and f != '__init__.py'):
                    s.append('<li class="file ext_%s"><img src="/editor/static/images/file-icons/delete.png" rel="%s"><a href="#" rel="%s">%s</a></li>' % (e,ff,ff,f))
        r += s
    except Exception,e:
        r.append('Could not load directory: %s' % str(e))
        print 'Error: ' + str(e)
    r.append('</ul>')
    return ''.join(r)

@editor.route('/editor/get_dirlist', methods=['POST'])
@login_required
def get_dirlist():
    try:
        request.form['dir']
    except KeyError:
        print('Key error in attempt to list directory contents.')
    return str(dirlist(request.form['dir']))

@editor.route('/editor/move_item', methods=['POST'])
@login_required
def move_item():
    import subprocess
    src = request.form['src']
    dst = request.form['dst']
    print '## move_item ## ' + src + ' to ' + dst
    res = subprocess.call(['mv', src, dst])
    if res <> 0:
        return 'Bad request', 400
    return 'OK', 200

# File management
def secure_path(path): # Version of Werkzeug's secure_filename trimmed to allow paths through (could be a bad idea)
    if isinstance(path, unicode):
        from unicodedata import normalize
        path = normalize('NFKD', path).encode('ascii', 'ignore')
    return path

@editor.route('/editor/read', methods=['POST'])
@login_required
def read_contents():
    path = secure_path(request.form['path'])
    f = open('/var/www/public/' + path, 'r')
    return f.read()

BOILERPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <title></title>
    {% include "include/rascal-head.html" %}
</head>
<body>
    {% include "include/rascal-topbar.html" %}
    <div class="container">
        <div class="well rascal">
            <h1>This is your new page.</h1>
            You can add some text here, or use template variables: {{magic}}
        </div>
    </div>
    <!-- DOCTAB --> 
    <script type="text/javascript">
    // You could add some Javascript between these script tags, if you want.
    // jQuery and jqPlot are already included in the header above.
    </script>
</body>
</html>
"""
DOCTAB = '{% include "include/doc-tab.html" %}'

MARKDOWN = """Edit Me!
========

--

#### Formatted Text
Rascal documentation is formatted using Markdown, a text-to-HTML conversion
tool which allows you to write in plain text format and converts it to HTML
when viewed in a web browser.

Leave a blank line to start a new paragraph.

#### Lists

1. One potato
2. Two potatoes

* Oranges
* Lemons

#### Miscellaneous

> This is a blockquote

    This could be an example of some code

See the [Markdown web page][mwp] for more information.

[mwp]: http://daringfireball.net/projects/markdown/
"""

@editor.route('/editor/new_template', methods=['POST'])
@login_required
def new_template():
    import os
    name = secure_path(request.form['templateName'])
    option = request.form['templateOption']
    if option == 'other':
        path = '/var/www/public/static/' + name
    elif option == 'markdown':
        path = '/var/www/public/templates/docs/' + name
    else:
        path = '/var/www/public/templates/' + name
    if os.path.exists(path):
        return 'Conflict', 409
    else:
        f = open(path, 'w')
        if option == 'html':
            f.write(BOILERPLATE.replace('DOCTAB', DOCTAB))
        elif option == 'doctab':
            f.write(BOILERPLATE.replace('<!-- DOCTAB -->', DOCTAB))
        elif option == 'markdown':
            f.write(MARKDOWN)
        f.close()
    return 'OK', 200

@editor.route('/editor/delete_file', methods=['POST'])
@login_required
def delete_file():
    import subprocess
    fname = request.form['filename']
    print 'Deleting file: ' + fname
    res = subprocess.call(['rm', '/var/www/public/' + fname])
    if res <> 0:
        return 'Bad Request', 400
    return 'OK', 200

@editor.route('/editor/new_folder', methods=['POST'])
@login_required
def new_folder():
    import os, subprocess
    name = secure_path(request.form['folderName'])
    path = '/var/www/public/static/' + name
    if os.path.exists(path):
        return 'Conflict', 409
    else:
        res = subprocess.call(['mkdir', path])
        if res <> 0:
            return 'Bad Request', 400
    return 'OK', 200

@editor.route('/editor/delete_folder', methods=['POST'])
@login_required
def delete_folder():
    import subprocess
    fname = request.form['filename']
    print 'Deleting folder: ' + fname
    res = subprocess.call(['rm', '-rf', '/var/www/public/' + fname])
    if res <> 0:
        return 'Bad Request', 400
    return 'OK', 200

# Save button
@editor.route('/editor/save', methods=['POST'])
@login_required
def save():
    root = '/var/www/public/'
    try:
        path = secure_path(request.form['path'])
        f = open(root + path, 'w')
        f.write(request.form['text'])
        f.close()
    except:
        return 'Bad Request', 400
    return 'OK', 200

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@editor.route('/editor/xupload', methods=['POST'])
@login_required
def xupload_file():
    import os
    from werkzeug.exceptions import RequestEntityTooLarge
    if request.method == 'POST':
        try:
            root = '/var/www/public/'
            # Check file type and folder
            filename = secure_filename(request.headers['X-File-Name'])
            if not allowed_file(filename):
                print '## xupload ## bad file type ' + filename
                return 'Forbidden', 403
            try:
                folder = request.headers['X-Folder']
            except:
                folder = ''
            fpath = os.path.join(root, os.path.join(folder, filename))
            # Write out the stream
            f = file(fpath, 'wb')
            f.write(request.stream.read())
            f.close()
            print '## xupload ## ' + fpath
        except RequestEntityTooLarge:
            return 'File too large', 413
        except:
            return 'Bad request', 400
    return 'OK', 200

# Reload pytronics button
@editor.route('/editor/reload', methods=['POST'])
@login_required
def reload():
    import subprocess
    res = subprocess.call(['logrotate', '-f', '/var/www/rotate_public.conf'])
    if res <> 0:
        return 'Bad request', 400
    else:
        res = subprocess.call(['touch', '/etc/uwsgi/public.ini'])
        if res <> 0:
            return 'Bad request', 400
    return 'OK', 200

# Save prefs in editor.config
@editor.route('/editor/save_prefs', methods=['POST'])
@login_required
def save_prefs():
    import json, ConfigParser
    try:
        section = request.form['section']
        prefs = json.loads(request.form['prefs'])
        config = ConfigParser.SafeConfigParser()
        config.optionxform = str    # Don't convert to lower case
        config.read(CONFIG_FILE)
        if not config.has_section(section):
            config.add_section(section)
        for k, v in prefs.iteritems():
            config.set(section, k, str(v))
        with open(CONFIG_FILE, 'wb') as configfile:
            config.write(configfile)
    except Exception, e:
        print '## save_prefs ## Unexpected error: %s' % str(e)
        return 'Bad request', 400
    return 'OK', 200

# Read prefs, returning data of the requested types (int, float, boolean or string)
# If file or section or an option doesn't exist, return default  
@editor.route('/editor/read_prefs', methods=['POST'])
@login_required
def read_prefs():
    import json, ConfigParser
    section = request.form['section']
    types = json.loads(request.form['types'])
    defaults = json.loads(request.form['defaults'])
    config = ConfigParser.SafeConfigParser()
    config.read(CONFIG_FILE)
    d = {}
    for k, v in types.iteritems():
        try:
            if v == 'int':
                d[k] = config.getint(section, k)
            elif v == 'float':
                d[k] = config.getfloat(section, k)
            elif v == 'boolean':
                d[k] = config.getboolean(section, k)
            else:
                d[k] = config.get(section, k)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            d[k] = defaults[k]
        except Exception, e:
            print '## read_prefs ## Unexpected error: %s' % str(e)
    return json.dumps(d)

## log page functions
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

@editor.route('/editor/log')
@login_required
def log():
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

## config page functions
# Return editor-xx (see also /editor/)
@editor.route('/editor/config')
@login_required
def config():
    import ConfigParser
    config = ConfigParser.SafeConfigParser()
    config.read(CONFIG_FILE)
    try:
        editor = config.get('Advanced', 'editor')
        advanced = '1'
    except ConfigParser.NoSectionError:
        editor = 'editor-cm'
        advanced = '0'
    except ConfigParser.NoOptionError:
        editor = 'editor-cm'
        advanced = '1'
    except Exception, e:
        print '## config ## Unexpected error: %s' % str(e)
        editor = 'editor-cm'
        advanced = '0'
    try:
        import subprocess
        process_table = subprocess.Popen('ifconfig', stdout=subprocess.PIPE)
        return render_template('config.html', processes=(process_table.communicate()[0]).strip(), advanced=advanced, editor=editor)
    except TemplateNotFound:
        abort(404)

@editor.route('/editor/reset', methods=['POST'])
@login_required
def reset():
    import subprocess
    subprocess.Popen(['git checkout .'], cwd='/var/www', shell=True)
    subprocess.Popen(['git clean -dxf'], cwd='/var/www', shell=True)
    return render_template('config.html')

@editor.route('/editor/set_editor', methods=['POST'])
@login_required
def set_editor():
    import ConfigParser
    section = 'Advanced'
    editor = request.form['editor']
    try:
        config = ConfigParser.SafeConfigParser()
        config.optionxform = str    # Don't convert to lower case
        config.read(CONFIG_FILE)
        if not config.has_section(section):
            config.add_section(section)
        config.set(section, 'editor', editor)
        with open(CONFIG_FILE, 'wb') as configfile:
            config.write(configfile)
    except Exception, e:
        print '## set_editor ## Unexpected error: %s' % str(e)
        return 'Bad request', 400
    return 'OK', 200

## monitor page functions
@editor.route('/editor/monitor')
@login_required
def monitor():
    try:
        import subprocess
        process_list = subprocess.Popen(['ps', '-ww'], stdout=subprocess.PIPE).communicate()[0].split('\n')
        table = '</td></tr>\n<tr><td>'.join(process_list).replace(' ', '&nbsp;')
        print table
        return render_template('monitor.html', processes=table)
    except TemplateNotFound:
        abort(404)


if __name__ == '__main__':
    editor.run(host='127.0.0.1:5001', debug=True)
