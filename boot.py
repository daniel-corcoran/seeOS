import importlib
from app import app
from exceptionhandler import exceptions

import math
import os
import time

import psutil
from flask import flash, redirect, Response
from waitress import serve
from werkzeug.utils import secure_filename

import modules.networkui
from modules import LED
from modules import buzzer
from modules import login
from modules import camera
from modules.globals import getGlobalConfig
from modules.install import install
from modules.kiwilog import kiwi
from modules.misc import list_apps
from modules.modeSelector import *
from modules import settings
from modules import systemInformationAPI
from modules import frontend
from modules import gallery
from modules.power import reboot, power_off

log = kiwi.instance('sys.boot')
log.add_log("Welcome to seeOS (COS).")

app.secret_key = 'hello'
UPLOAD_FOLDER = 'database/tmp'
ALLOWED_EXTENSIONS = {'tree'}

sys_update_available = False

#Check if a system update is available

update = modules.update.check_update_api()
see_config = getGlobalConfig()

default_app = see_config['default_app']

# TODO: Is there a safer way to do this?
os.system('nohup python3 modules/terminal.py &')


log.add_log('attempting to load default app: {}'.format(default_app))
try:
    #my_program = importlib.import_module('programs.{}.main'.format(default_app))
    log.add_log('initial import of default app: {} was a success'.format(default_app))
except Exception as E:
    log.add_exception('import of {} failed, importing exceptionhandler.main instead. Exception: {}'.format(default_app, E))
    my_program = importlib.import_module('exceptionhandler.ui')
    with open("database/tmp/latest_logs", 'w') as f:
        json.dumps({"logs": log.get_logs(), "exceptions": log.get_exceptions()})


# TODO: Safely remove this.
ir = False


def exception_handler(e=None):
    # Start the exception handler if we can't load the main app.
    if e:
        global error
        error = e
    try:
        serve(exceptions, host='0.0.0.0', port=80)
    except:
        try:
            LED.blue()
            serve(exceptions, host='0.0.0.0', port=8000)
        except:
            LED.red()


if __name__ == '__main__':
    LED.green()
    time.sleep(0.161)
    LED.blue()
    time.sleep(0.161)
    LED.red()
    time.sleep(0.161)
    LED.green()
    buzzer.cooltone()


    log.add_log("Server program has begin. Beginning service.")
    try:
        log.add_log("Attempting to open on port 80")
        serve(app, host='0.0.0.0', port=80, threads=8)
    except Exception as E:
        log.add_exception('Opening on port 80 was unsucessful. Exception: {}'.format(E))
        try:
            log.add_log("Attempting to open on port 8000")
            LED.blue()
            serve(app, host='0.0.0.0', port=8000)
        except Exception as E:
            log.add_exception('Opening on port 8000 was unsucessful. Details: {}'.format(E))
            LED.red()
            exception_handler(E)

    log.add_log("Exiting.")
    LED.blue()
    exit()