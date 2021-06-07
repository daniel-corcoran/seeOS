from app import app
import cv2
from app import app
from flask import request, render_template
import json
from modules.kiwilog import kiwi
import flask_login
from flask.json import jsonify
from modules.misc import list_apps
from modules.globals import default_app
from modules.camera import convert_size
from random import randint

from modules.camera import buffer_file
import os
log = kiwi.instance("modules.gallery")

file_format = 'mp4'

@app.route("/_delete_all", methods=['POST', 'GET'])
def delete_img():
    img_path = 'app/static/appstatic/simplestreamer/'
    thumb_path = 'app/static/appstatic/simplestreamer/thumbnails/'
    # Deletes all images in the gallery. This is a debug feature. FIXME
    delete_thumb_list = os.listdir(thumb_path)
    delete_img_list = os.listdir(img_path)
    delete_img_list = [x for x in delete_img_list if x != 'thumbnails']  # FIXME: This is trashy
    log.add_log(f"Deleting {delete_thumb_list} {delete_img_list}")
    for i in delete_img_list:
        os.remove(img_path + i)
    for j in delete_thumb_list:
        os.remove(thumb_path + j)
    return ajax_ui_endpoint_gallery()




@app.route("/_gallery", methods=['GET', 'POST'])
@flask_login.login_required
def ajax_ui_endpoint_gallery():
    # Return a gallery view of captured videos and images

    # Return a dic: Int (ordinal) : {thumb_url, src_url}
    # Get the list of files available to download
    # Maybe offer a preview?
    src_list = [f'static/appstatic/simplestreamer/{i}'
                for i in os.listdir('app/static/appstatic/simplestreamer') if "thumbnails" not in i]
    thumb_list = [f'static/appstatic/simplestreamer/thumbnails/{i}'
                  for i in os.listdir('app/static/appstatic/simplestreamer/thumbnails')]
    d = []
    # TODO: Add type (video or image) to this json
    src_list.sort()
    thumb_list.sort()
    for src, thumb in zip(src_list, thumb_list):
        if file_format in src:
            src_type = 'vid'
        else:
            src_type = 'img'

        if src == buffer_file:  # If this file is currently being buffered by the buffer thread
            d.append({'src': 'https://homepages.cae.wisc.edu/~ece533/images/airplane.png',
                      # TODO: Replace with a "buffering pls wait" image
                      'thumb': thumb,
                      'type': src_type,
                      'hash': randint(0, 9999999999),
                      'size': convert_size(os.path.getsize(f'app/{src}')),
                      'buffer': True})
        else:
            d.append({'src': src,
                      'thumb': thumb,
                      'type': src_type,
                      'hash': randint(0, 9999999999),
                      'size': convert_size(os.path.getsize(f'app/{src}')),
                      'buffer': False})
    z = jsonify({'html': render_template('frameUnit/__gallery.html', file_list=d)})
    print(z)
    return z
