from flask import abort, Blueprint, redirect, render_template, request
from jinja2 import TemplateNotFound
from werkzeug import secure_filename

editor = Blueprint('editor', __name__, static_url_path='/editor/', static_folder='static', template_folder='templates')

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

@editor.route('/config')
def config():
    try:
        import subprocess
        process_table = subprocess.Popen('ifconfig', stdout=subprocess.PIPE)
        return render_template('config.html', processes=process_table.communicate()[0])
    except TemplateNotFound:
        abort(404)

@editor.route('/log')
def log():
    try:
        f = open('/var/log/uwsgi.log', 'r')
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

@editor.route('/monitor')
def monitor():
    try:
        import subprocess
        process_list = subprocess.Popen('ps', stdout=subprocess.PIPE).communicate()[0].split('\n')
        table = '</td></tr>\n<tr><td>'.join(process_list).replace(' ', '&nbsp;')
        return render_template('monitor.html', processes=table)
    except TemplateNotFound:
        abort(404)

@editor.route('/edit/')
def start_edit():
    try:
        return render_template('editor.html', text_to_edit='No file selected')
    except TemplateNotFound:
        abort(404)

@editor.route('/edit/<path:path>', methods=['GET', 'POST']) # POST added because
def edit(path):                            # of redirects from /save route POSTs
    try:
        path = secure_path(path)
        f = open('/var/www/public/' + path, 'r')
        print '/var/www/public/' + path
        return render_template('editor.html', text_to_edit=f.read(), path=path, fileext=path.split('.').pop())
    except TemplateNotFound:
        abort(404)

@editor.route('/get_dirlist', methods=['POST'])
def get_dirlist():
    try:
        import filetree
    except ImportError:
        print("Import error: can't find filetree")
    try:
        request.form['dir']
    except KeyError:
        print("Key error in attempt to list directory contents.")
    return str(filetree.dirlist(request.form['dir']))

@editor.route('/new_file', methods=['POST'])
def new_file():
    import subprocess
    subprocess.Popen(['touch', '/var/www/public/' + secure_path(request.form['filename'])])
    return render_template('editor.html')

@editor.route('/new_folder', methods=['POST'])
def new_folder():
    import subprocess
    result = subprocess.Popen(['mkdir', '/var/www/public/' + secure_path(request.form['filename'])])
    return render_template('editor.html')

@editor.route('/reload', methods=['POST'])
def reload():
    f = open('/etc/uwsgi.reload', 'w')
    f.write(request.form['text'])
    f.close()
    return render_template('editor.html', sourcefile=sourcefile)

@editor.route('/save', methods=['POST'])
def save():
    root = '/var/www/public/'
    path = secure_path(request.form['path'])
    f = open(root + path, 'w')
    f.write(request.form['text'])
    f.close()
    return redirect('/edit/' + path, 302)
