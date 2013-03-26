from flask import Blueprint, render_template, request
public = Blueprint('crap', __name__, template_folder='templates')

@public.route('/example/<variable>')
def example(variable):
    try:
        return variable * request.form['data']
    except:
        return variable * data
