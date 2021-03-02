from flask import Flask
from flask import render_template

from app import app
exceptions = Flask(__name__)
error = 'No error message reported'

def set_error(er):
    global error
    error = er

@exceptions.route('/')
def exception():
    return render_template('exceptionhandler/main.html', error=error)

@app.errorhandler(404)
def page_not_round(e):
    return render_template("exceptionhandler/404.html")

@app.errorhandler(500)
def err_500(e):
    return render_template("exceptionhandler/500.html"), 500
