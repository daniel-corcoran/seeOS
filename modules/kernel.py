# This module handles the switching between and deployment of running applications in seeOS.
# Applicatons exist as threads, and can accordingly be killed / invoked at whim by the user.
# Applications have two major tasks to do, which is
#   - write modifications to the frame buffer,
#   - present a frontend via AJAX call
#   - accept AJAX frontend API calls
#   - make inferences on the video feed
#   - trigger record / capture / stop recording events
#
# Present a front endprocess input from the user

# Contain API pushes for application switching etc.

# Load calculate_overlay function as thread from specific package



import json
from program.test import main
from program.test.main import _async_overlay


def switch(target):
    target = target.replace('.x', '')
    with open("database/see.json") as f:
        data = json.load(f)
        data['default_app'] = target


    with open("database/see.json", "w") as f:
        json.dump(data, f)


def async_overlay(frame):
    # Pass to app async overlay
    return _async_overlay(frame)

