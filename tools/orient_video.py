import cv2
from app import app
from flask import request
import json
from tools.kiwilog import kiwi
log = kiwi.instance("tools.orient_video")
with open('database/see.json') as f:
    os_conf = json.load(f)
    orient = os_conf["counter_clockwise_rotation_count"]


@app.route("/get_orient", methods=['POST', 'GET'])
def get_orient():
    # Return the orientation
    return json.dumps({"orient": orient, 'angle': 90*orient})

@app.route("/set_orient", methods=['POST', 'GET'])
def set_orient():
    global orient
    dir = request.form['direction']
    # Dir is positive or negative 1.
    orient += int(dir)
    if orient > 3:
        orient = orient - 4
    elif orient < 0:
        orient = orient + 4
    global os_conf
    os_conf["counter_clockwise_rotation_count"] = orient
    with open('database/see.json', 'w') as f:
        print(f"Orient value is now {orient}")

        json.dump(os_conf, f)
    # set the global orientation variables.
    return json.dumps({"orient": orient, 'angle': 90*orient})


def orient_frame(frame):
    if orient == 0:
        return frame
    elif orient == 1:
        return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif orient == 2:
        return cv2.flip(frame, flipCode=0)
    elif orient == 3:
        return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    else:
        log.add_exception(f"Error: Orient key arg is {orient}")
        return frame
    # Orient a frame according to the user-defined preset.