from waitress import serve
from flask import render_template
from app import app
from exceptionhandler import exceptions
from tools.power import reboot, power_off, restart_client
from tools import LED
import importlib
import os
from werkzeug.utils import secure_filename
from flask import flash, request, redirect, url_for
from tools.switch import switch
from tools.uninstall import uninstall
from tools.install import install
from flask import jsonify
from tools import buzzer, temp, login
from tools.misc import list_apps
from imutils.video import VideoStream
import cv2
import tools.networkui
from tools.kiwilog import kiwi
import flask_login
import flask
import json
from tools import orient_video
import psutil

log = kiwi.instance('sys.boot')
log.add_log("Welcome to seeOS (COS).")

app.secret_key = 'hello'
UPLOAD_FOLDER = 'database/tmp'
ALLOWED_EXTENSIONS = {'tree'}

sys_update_available = False

#Check if a system update is available

update = tools.update.check_update_api()
with open('database/see.json') as f:
    see_config = json.load(f)

default_app = see_config['default_app']

# TODO: Is there a safer way to do this?
os.system('nohup python3 tools/terminal.py &')



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Load default app from database

log.add_log('attempting to load default app: {}'.format(default_app))
try:
    my_program = importlib.import_module('programs.{}.main'.format(default_app))
    log.add_log('initial import of default app: {} was a success'.format(default_app))

except Exception as E:
    log.add_exception('import of {} failed, importing exceptionhandler.main instead. Exception: {}'.format(default_app, E))
    my_program = importlib.import_module('exceptionhandler.ui')
    with open("database/tmp/latest_logs", 'w') as f:
        json.dumps({"logs": log.get_logs(), "exceptions": log.get_exceptions()})


# TODO: Safely remove this.
ir = False

def irOFF():
    LED.IRoff()


def irON():
    LED.IRon()


import math

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])


@app.route("/cpu_load", methods=['POST', 'GET'])
def cpu_load():
    # Return CPU load statistics via json
    pct = psutil.cpu_percent(percpu=True)
    d = {'a': pct[0], 'b': pct[1], 'c': pct[2], 'd': pct[3]}
    return jsonify(d)


@app.route("/memory", methods=['POST', 'GET'])
def memory():
    # Return memory
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    d = {'mem_total': convert_size(mem.total),
         'mem_used':  convert_size(mem.used),
         'mem_free': convert_size(mem.free),
         'swap_total': convert_size(swap.total),
         'swap_used': convert_size(swap.used),
         'swap_free': convert_size(swap.free)}
    return jsonify(d)



@app.route("/disk_capacity", methods=['POST', 'GET'])
def disk_capacity():
    # AJAX call to know how much space is remaining on the SD card.
    try:

        hdd = psutil.disk_usage('/home/mendel/sdcard')

        return jsonify({'total':convert_size(int(hdd.total)),
                        'used': convert_size(int(hdd.used)),
                        'free': convert_size(int(hdd.free))})
    except:
        hdd = psutil.disk_usage('/')

        return jsonify({'total': convert_size(int(hdd.total)),
                        'used': convert_size(int(hdd.used)),
                        'free': convert_size(int(hdd.free))})

@app.route("/update")
@flask_login.login_required
def update_helper():
    p = None
    # TODO: This needs to be fixed. IMPORTANT
    LED.blue()
    LED.green()
    if p == "Already up to date.":
        return init_config(up_to_date=True)
    else:
        return reboot_helper()


@app.route("/upload", methods=['GET', 'POST'])
@flask_login.login_required
def upload():
    print("File uploaded")
    LED.blue()
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files['file']
        print(file)
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.ses_config['UPLOAD_FOLDER'], filename))
            install(filename)

        else:
            print("Not allowed")
        return init_config()
    else:
        print(request.method)
        return 'there was an error. Error: POST method required to install applications. '


@app.route("/app_change_request", methods=['GET', 'POST'])
@flask_login.login_required
def app_mod_process():
    # TODO: Do this without restarting the device?

    x = request.form
    cmd = [i for i in x]
    print("Command received:", cmd)
    do = cmd[0].split()[0]
    target = cmd[0].split()[1]
    log.add_log('user wants to {} application {}'.format(do, target))
    # Should be "Switch" x
    # or "Uninstall x"
    if do == "switch":
        # Switch target
        switch(target)
        # FIXME
        reboot()
        return render_template('connect.html')

    elif do == "uninstall":
        # Uninstall target
        uninstall(target)
        return init_config()


@app.route("/reboot")
@flask_login.login_required
def reboot_helper():
    LED.red()
    reboot()
    return render_template("connect.html", action='localAPI/power/reboot')


@app.route("/power_off")
@flask_login.login_required
def power_off_helper():
    power_off()
    return render_template("connect.html", action='localAPI/power/off')


@app.route('/debug')
@flask_login.login_required
def debug():
    logs = log.get_exceptions()
    print(logs)
    print(len(logs))
    html = '<h4>Exceptions [ Possibly fatal ]</h4>'
    for l in logs:
        html += render_template('exceptionhandler/err_frame.html', src=l, details=logs[l])

    logs = log.get_logs()
    print(logs)
    print(len(logs))
    html += '<h4>Logs [ Non-fatal ] </h4>'
    for l in logs:
        html += render_template('exceptionhandler/err_frame.html', src=l, details=logs[l])
    # If we reach this point, it means there was an exception.

    return render_template("debug.html", table=html)


@app.route("/")
@flask_login.login_required
def home_page():
    return my_program.main()


@app.route('/config')
@flask_login.login_required
def init_config(up_to_date=False):
    x = list_apps()
    print("Update: ", update)
    return render_template('config.html', list_apps=x, current_app=default_app, ir=ir,
                           netui_dir='netui', update=update)


@app.route('/view')
@flask_login.login_required
def init_view():
    return my_program.main()


def exception_handler(error=None):
    # Start the exception handler if we can't load the main app.
    if error:
        exceptions.set_error(error)
    try:
        serve(exceptions, host='0.0.0.0', port=80)
    except:
        try:
            LED.blue()
            serve(exceptions, host='0.0.0.0', port=8000)
        except:
            LED.red()


if __name__ == '__main__':
    import time
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
            exception_handler(error=E)

    log.add_log("Exiting.")
    LED.blue()
    exit()