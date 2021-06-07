from modules import camera
from app import app
import flask_login
from flask import render_template
from modules.kiwilog import kiwi
from modules import LED
from flask import Response

log = kiwi.instance('apps.simplestreamer')
log.add_log('loaded simplestreamer dependencies')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Load default app from database




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





@app.route('/config')
@flask_login.login_required
def init_config(up_to_date=False):
    x = list_apps()
    print("Update: ", update)
    return render_template('config.html', list_apps=x, current_app=default_app, ir=ir,
                           netui_dir='netui', update=update)


@app.route('/view')
@flask_login.login_required
# FIXME: why do we need this page
def init_view():
    return home_page()

@app.route("/video_feed")
def video_feed():
    log.add_log("/video_feed has been pinged")
    return Response(camera.generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/")
@flask_login.login_required
def home_page():
    if camera.recording:
        r = 'true'
    else:
        r = 'false'
    return render_template('base.html', recording=r)