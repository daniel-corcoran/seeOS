# modeSelector
# Contains the important URL endpoints for mode selection. Returns via AJAX the available modes and processes
# requests via AJAX to switch the app across devices.


import cv2
from app import app
from flask import request, render_template
import json
from tools.kiwilog import kiwi
import flask_login
from flask.json import jsonify
from tools.misc import list_apps
from tools.globals import default_app


log = kiwi.instance("tools.modeSelector")



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


@app.route("/_modeSelector", methods=['GET', 'POST'])
@flask_login.login_required
def ajax_ui_endpoint():
    # Javascript accesses this endpoint, gets the HTML, and renders it in the block
    return jsonify({'html': render_template("frameUnit/__modeSelector.html",current_app = default_app(),  list_apps = list_apps())})
