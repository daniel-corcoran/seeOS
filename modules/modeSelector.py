# modeSelector
# Contains the important URL endpoints for mode selection. Returns via AJAX the available modes and processes
# requests via AJAX to switch the app across devices.


import cv2
from app import app
from flask import request, render_template
import json
from modules.kiwilog import kiwi
import flask_login
from flask.json import jsonify
from modules.misc import list_apps
from modules.globals import default_app
from modules.kernel import switch
log = kiwi.instance("modules.modeSelector")



@app.route("/_app_change_request", methods=['GET', 'POST'])
@flask_login.login_required
def app_mod_process():
    # TODO: Do this without restarting the device?

    app_req = request.args.get('app', 'Video Streaming', type=str)
    print("Requested to change app to ")
    print(app_req)
    switch(app_req)
    return '{}'

@app.route("/_modeSelector", methods=['GET', 'POST'])
@flask_login.login_required
def ajax_ui_endpoint():
    l = list_apps()
    l = [i.replace('_', ' ') for i in l]
    # Javascript accesses this endpoint, gets the HTML, and renders it in the block
    return jsonify({'html': render_template("frameUnit/__modeSelector.html",current_app = default_app(),  list_apps = l)})
