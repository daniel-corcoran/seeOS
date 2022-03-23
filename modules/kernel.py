# This module handles the switching between and deployment of running applications in seeOS.
# Applicatons exist as threads, and can accordingly be killed / invoked at whim by the user.
# Applications have two major tasks to do, which is
#   - # make inferences on the video feed & write modifications to the frame buffer,
#   - present a frontend via AJAX call
#   - accept AJAX frontend API calls
#   - trigger record / capture / stop recording events if needed, for example capturing a point of interest



# Contain API pushes for application switching etc.

# Load calculate_overlay function as thread from specific package



import json
import importlib
from modules.kiwilog import kiwi
from modules.globals import getGlobalConfig

from program.Video_Streaming import main as video_streaming
from program.Object_Detection import main as object_detection
from program.Facial_Recognition import main as facial_recognition
from program.Motion_Detection import main as motion_detection


from threading import Lock
import time
switch_app_mutex = False

#from program.Facial_Recognition import main as facial_recognition


log = kiwi.instance('sys.modules.kernel')
see_config = getGlobalConfig()
default_app = see_config['default_app']



# TODO: This part needs to be abstracted/generalizable.
if default_app == 'Video Streaming':
    video_streaming.initialize()
elif default_app == 'Object Detection':
    object_detection.initialize()
elif default_app == 'Motion Detection':
    motion_detection.initialize()
elif default_app == 'Facial Recognition':
    facial_recognition.initialize()

#
#try:
#    my_program = importlib.import_module('program.{}.main'.format(default_app))
#    log.add_log('initial import of default app: {} was a success'.format(default_app))
#
#
#except Exception as E:
#    log.add_exception('import of {} failed, importing exceptionhandler.main instead. Exception: {}'.format(default_app, E))
#    my_program = importlib.import_module('exceptionhandler.ui')
#    with open("database/tmp/latest_logs", 'w') as f:
#        json.dumps({"logs": log.get_logs(), "exceptions": log.get_exceptions()})
#

# Change running app
def switch(target):
    global default_app
    global switch_app_mutex

    while switch_app_mutex:
        time.sleep(0.1)
    # Destroy currently running app and initialized new one

    if default_app == 'Video Streaming':
        video_streaming._destroy()

    elif default_app == 'Object Detection':
        object_detection._destroy()

    elif default_app == 'Facial Recognition':
        facial_recognition._destroy()

    elif default_app == 'Motion Detection':
        motion_detection._destroy()
    default_app = target

    with open("database/see.json") as f:
        data = json.load(f)
        data['default_app'] = target

    with open("database/see.json", "w") as f:
        json.dump(data, f)

    if default_app == 'Video Streaming':
        video_streaming.initialize()
    elif default_app == 'Object Detection':
        object_detection.initialize()
    elif default_app == 'Facial Recognition':
        facial_recognition.initialize()
    elif default_app == 'Motion Detection':
        motion_detection.initialize()

    switch_app_mutex = False


def __async_overlay(frame):
    global switch_app_mutex
    while switch_app_mutex:
        time.sleep(0.1)
    if default_app == 'Video Streaming':
        try:
            return video_streaming._async_overlay(frame)
        except Exception as E:
            print("Error 10456")
            print(E)
            return None
    elif default_app == 'Object Detection':
        try:
            return object_detection._async_overlay(frame)
        except Exception as E:
            print("Error 10456")
            print(E)
            return None
    elif default_app == 'Motion Detection':
        try:
            return motion_detection._async_overlay(frame)
        except Exception as E:
            print("Error 10456")
            print(E)
            return None
    elif default_app == 'Facial Recognition':
        try:
            return facial_recognition._async_overlay(frame)
        except Exception as E:
            print("Error 10456")
            print(E)
            return None
    switch_app_mutex = False
