from app import app
import cv2
from app import app
from flask import request, render_template
import json
from modules.kiwilog import kiwi
import flask_login
from flask.json import jsonify

log = kiwi.instance("modules.gallery")

file_format = 'mp4'

@app.route("/_settings", methods=['GET', 'POST'])
@flask_login.login_required
def ajax_ui_endpoint_settings():
    # Return a gallery view of captured videos and images

    return jsonify({'html': render_template('frameUnit/__settings.html')})
