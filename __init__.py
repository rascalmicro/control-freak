from flask import Flask
from www.public import public
from www.editor import editor

app = Flask(__name__)
app.register_blueprint(public)
app.register_blueprint(editor)
