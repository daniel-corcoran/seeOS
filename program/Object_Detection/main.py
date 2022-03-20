from PIL import Image
from PIL import ImageDraw

from pycoral.adapters import common
from pycoral.adapters import detect
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter

from imutils.video import VideoStream
from PIL import Image
import imutils
import time
import cv2
from flask import request, render_template
from app import app

import cv2
from threading import Thread



confidence = 0.3
# initialize the labels dictionary

labels = read_label_file('program/Object_Detection/mobilenet_ssd_v2/coco_labels.txt')

interpreter = None
initialized = False
async_process_t = None

def initialize():
    global interpreter
    global initialized
    global async_process_t
    try:
        interpreter = make_interpreter(
            'program/Object_Detection/mobilenet_ssd_v2/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite')
        interpreter.allocate_tensors()
        initialized = True
        print("Initialized Object Detector")
        async_process_t = Thread(target=_async_process)
        async_process_t.start()
        return {'initialized': True}

    except Exception as E:
        print(E)
        return {'initialized': False, 'err': E}

def _destroy():
    global interpreter
    global initialized
    global async_process_t

    interpreter = None
    initialized = False
    async_process_t.join()


_overlayObjs = None

_frame = None

def _overlay(frame):
    return cv2.circle(frame, (100, 100), radius=100, thickness=-1, color=(255, 0, 0))


def _calculate_overlay(frame):
    global _overlayObjs
    global _overlay
    # Updates overlay_pane by inferencing the latest frame.
    # Runs on a mutex, so it will onyl run once at a time.
    # It runs in a thread so it is protecte

    # prepare the frame for classification by converting (1) it from
    # BGR to RGB channel ordering and then (2) from a NumPy array to
    # PIL image format
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = Image.fromarray(frame)

    start = time.perf_counter()
    if initialized:
        print("Initialized")
        if interpreter is None:
            print("Interpreter is none and this is initialized ERROR ERROR ERROR")
        else:
            print("Interpreter is not none")
            print(interpreter)
        _, scale = common.set_resized_input(
            interpreter, frame.size, lambda size: frame.resize(size, Image.ANTIALIAS))

        interpreter.invoke()
        inference_time = time.perf_counter() - start
        _overlayObjs = detect.get_objects(interpreter, confidence, scale)
        print(_overlayObjs)
        #print('%.2f ms' % (inference_time * 1000))

        def overlay_function(frame):
            # ensure at least one result was found
            for obj in _overlayObjs:
                bbox = obj.bbox
                frame = cv2.rectangle(frame, (bbox.xmin, bbox.ymin), (bbox.xmax, bbox.ymax), (0, 0, 255), 2)
                frame = cv2.putText(frame,
                        '%s %.2f' % (labels.get(obj.id, obj.id), obj.score),
                                    (bbox.xmin + 20, bbox.ymin + 20),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.5,
                                    (0, 0, 255))
                #draw.text((bbox.xmin + 10, bbox.ymin + 10),
                #          '%s\n%.2f' % (labels.get(obj.id, obj.id), obj.score),
                #          fill='red')

            return frame

        _overlay = overlay_function
    else:
        print("Uninitialized")

    # Do stuff to image


def _async_process():
    # $ This is the "while loop" for the overlay calculator which triggers a new overlay when the previous one is done calculating.
    while initialized:
        if _frame is not None:
            _calculate_overlay(_frame)






# Updates the frame within the app, doesn't mean it will actually get inferred though.

def _async_overlay(frame):
    global _frame
    _frame = frame
    return _overlay(frame)
