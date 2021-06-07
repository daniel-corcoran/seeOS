# Copyright (c) 2020 Daniel Corcoran

import os
import urllib.request, json
from modules.kiwilog import kiwi
from app import app
import requests
import sys
from flask import render_template, request
import threading
log = kiwi.instance("update")

global_update_status = False # True if we are doing a system update

update_pct = 0
update_size = 0
update_done = 0
total_size = 0


def request(url):
    try:
        global global_update_status
        global total_size

        global_update_status = True
        file_path = 'sys_flash.tar.xz'
        with open(file_path, 'wb') as f:
            log.add_log(f"Downloading {file_path}")
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length'))
            log.add_log(f"Total size: {total_size}")

            if total_size is None:  # no content length header
                f.write(response.content)
                log.add_exception("The length of the API file is 0. ")
            else:
                global update_done
                global update_pct
                update_done = 0

                for data in response.iter_content(chunk_size=4096):
                    update_pct = int(100 * (update_done / total_size))

                    update_done += len(data)
                    f.write(data)
                    done = int(50 * update_done / total_size)
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                    sys.stdout.flush()
        global_update_status = False
        # yield download progress
    except Exception as e:
        global_update_status = True
        log.add_exception("Error placing request: " + str(e))


@app.context_processor
def update_callback():
    return dict(update=check_update_api())


@app.route('/localAPI/update/update_download_status', methods=['POST', 'GET'])
def update_status():
    # Return update status via AJAX
    return json.dumps({"update_pct": update_pct, "update_size": total_size, "update_done": update_done})


@app.route('/localAPI/update/apply_update')
def apply_update():
    try:
        # TODO: Apply update from server API
        url = check_update_api()['url']
        if global_update_status == False:
            log.add_log(f"Querying remote API for update file from {url}")
            job = threading.Thread(target=request, args=(url, ))
            job.start()
            return render_template('update.html')
        else:
            log.add_exception(f"The system is already downloading an update!! This is a bug...")
            return "FATAL ERROR APPLYING UPDATE. System is already downloading an update."
    except Exception as e:
        log.add_exception(f"Error applying update: {e}")
        return f"FATAL ERROR APPLYING UPDATE: {e}"


@app.route('/localAPI/update/detail_div')
def detail_div():
    update = check_update_api()
    details = update['details']
    html = f"<p><b>Update Details</b></p><p>{details}</p>" \
           f'''<button class='update-button' onclick='location.href="/localAPI/update/apply_update"'>Update</button><button class='update-button' id='close-update-overlay' onclick='close_update_bar();'>Cancel</button>'''
    data = {"HTML": html}
    # Return details on the available update in HTML format.
    return json.dumps(data)


@app.route('/localAPI/update/update_div')
def update_div():
    html = '''<p>Ready to update? <button class='update-button' onclick='location.href="/localAPI/update/apply_update"'>Yes</button> <button class='update-button' id='close-update-overlay' onclick='close_update_bar();'>Cancel</button></p>'''
    data = {"HTML": html}
    # Return details on the available update in HTML format.
    return json.dumps(data)


def check_update_api():
    import json
    with open('database/see.json') as f:
        dic = json.load(f)
    ## FIXME
    sys_v = dic['sys_v']
    url = "http://treecamera.xyz:8001/apis/latest_version"
    log.add_log(f"Current system version. {sys_v}")
    log.add_log("Contacting remote update API...")

    try:
        response = urllib.request.urlopen(url)
        log.add_log(f"Sucessfully got response from API. Loading JSON... ")
        data = json.loads(response.read())
        log.add_log(f"JSON loaded from remote API. Hooray!")

    except Exception as e:
        log.add_exception(f"There was an error contacting the API. Exception: {e}")
        return {"update": False, "error": True, "msg": f'''Current system version: {sys_v}'''}

    if 'latest_version' in data:
        latest_v = float(data['latest_version'])

        if latest_v > sys_v:
            # Update available
            log.add_log(f"An update is avaliable. Update version: {latest_v}")

            if 'description' in data:
                description = data['description']
                log.add_log(f"Description: {description}")

            else:
                description = "No description was provided by the API. This is probably a bug. "
                log.add_exception(f"No description was provided")

            return {"update": True, "error": False, "msg": f"seeOS {latest_v} is available for download.", "url": data['url'], "details": description}

        else:
            log.add_log(f"Your system is up-to-date. API says latest system update is {latest_v}")
            return {"update": False, "error": False, "msg": f"seeOS {latest_v} is up-to-date."}
    else:
        log.add_exception(f"Could not retrieve latest_version from api data. api response: {data}")
        return {"update": False, "error": True, "msg": f"Could not check for update. Current system version: {sys_v}"}

