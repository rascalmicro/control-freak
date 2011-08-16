from flask import Blueprint, render_template, request, abort
from jinja2 import TemplateNotFound
from werkzeug import secure_filename

editor = Blueprint('editor', __name__, static_folder='static', template_folder='templates')

def secure_path(path): # Version of Werkzeug's secure_filename trimmed to allow paths through (could be a bad idea)
    if isinstance(path, unicode):
        from unicodedata import normalize
        path = normalize('NFKD', path).encode('ascii', 'ignore')
    return path

@editor.route('/config')
def config():
    try:
        return render_template('config.html')
    except TemplateNotFound:
        abort(404)

@editor.route('/log')
def log():
    try:
        return render_template('log.html')
    except TemplateNotFound:
        abort(404)

@editor.route('/monitor')
def log():
    try:
        return render_template('monitor.html')
    except TemplateNotFound:
        abort(404)

@editor.route('/edit/')
def start_edit():
    try:
        return render_template('editor.html', text_to_edit='No file selected')
    except TemplateNotFound:
        abort(404)

@editor.route('/edit/<path:path>')
def edit(path):
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
    return render_template('editor.html', sourcefile=sourcefile)

@editor.route('/new_folder', methods=['POST'])
def new_folder():
    import subprocess
    result = subprocess.Popen(['mkdir', '/var/www/public/' + secure_path(request.form['name'])])
    print result
    return render_template('editor.html', sourcefile=sourcefile)

@editor.route('/reload', methods=['POST'])
def reload():
    f = open('/etc/uwsgi.reload', 'w')
    f.write(request.form['text'])
    f.close()
    return render_template('editor.html', sourcefile=sourcefile)

@editor.route('/save', methods=['POST'])
def save():
    root = '/var/www/public/'
    path = request.form['path']
    f = open(root + secure_path(str(path)), 'w')
    f.write(request.form['text'])
    f.close()
    return redirect('/edit', 200)
