# Test program main file
# The goal of this app is to demonstrate multi-threaded video processing.



# We want to show the latest inference on the current frame, not necessarily infer each frame (That would be too slow).
# So our application updates the overlay as frequently possible

import cv2
from threading import Thread

_frame = None
async_process_t = None
initialized = None

def initialize():
    global initialized
    global async_process_t
    try:
        initialized = True
        print("Initialized  Video Thread")
        async_process_t = Thread(target=_async_process)
        async_process_t.start()
        return {'initialized': True}

    except Exception as E:
        print(E)
        return {'initialized': False, 'err': E}

def _destroy():
    global initialized
    global async_process_t
    initialized = False
    async_process_t.join()

# This is the latest overlay
def _overlay(frame):
    return frame

def _calculate_overlay(frame):
    global _overlay
    # Updates _overlay by inferencing the latest frame.
    def overlay_function(frame):
        return frame

    _overlay = overlay_function


def _async_process():
    # $ This is the "while loop" for the overlay calculator which triggers a new overlay when the previous one is done calculating.
    while initialized:
        if _frame is not None:
            _calculate_overlay(_frame)




def _async_overlay(frame):
    global _frame
    _frame = frame
    return _overlay(frame)
