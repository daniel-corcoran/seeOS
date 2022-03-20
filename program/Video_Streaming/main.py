# Test program main file
# The goal of this app is to technically demonstrate multi-threaded application process switcing
# This app processes one frame per second. So, it should be significantly slower at processing than our frontend.
# Accordingly, we want to show the latest inference on the current frame, not necessarily infer each frame.
# So our application has a function to apply the "overlay" per se to the latest frame.

import cv2
from threading import Thread

_frame = None


def _overlay(frame):
    return cv2.circle(frame, (100, 100), radius=100, thickness=-1, color=(255, 0, 0))

def _calculate_overlay(frame):
    global _overlay

    # Updates overlay_pane by inferencing the latest frame.
    # Runs on a mutex, so it will onyl run once at a time.
    # It runs in a thread so it is protecte

    def overlay_function(frame):
        print("Running overlay_function")
        return cv2.circle(frame, (100, 100), radius=100, thickness=-1, color=(255, 0, 0))

    _overlay = overlay_function
    # Do stuff to image


def _async_process():
    # $ This is the "while loop" for the overlay calculator which triggers a new overlay when the previous one is done calculating.
    while True:
        _calculate_overlay(_frame)


_async_process_t = Thread(target=_async_process)
_async_process_t.start()

def _async_overlay(frame):
    global _frame
    _frame = frame
    return _overlay(frame)
