from app import app
from flask import render_template
from modules.kiwilog import kiwi

log = kiwi.instance('exceptionhandler.ui')

def main():
    logs = log.get_exceptions()
    print(logs)
    print(len(logs))
    html = ''
    for l in logs:
        html += render_template('exceptionhandler/err_frame.html', src=l, details=logs[l])
    # If we reach this point, it means there was an exception.
    return render_template('exceptionhandler/import_err.html', html=html)