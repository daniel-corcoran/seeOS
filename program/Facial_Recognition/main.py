from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import cv2
from threading import Thread

#data = pickle.loads(open('programs/face_friend/encodings.pickle', "rb").read())

detector = None
initialized = False
async_process_t = None

def initialize():
    global detector
    global initialized
    global async_process_t

    try:
        detector = cv2.CascadeClassifier('program/Facial_Recognition/haarcascade_frontalface_default.xml')
        initialized = True
        async_process_t = Thread(target=_async_process)
        async_process_t.start()
        return {'initialized': True}
    except Exception as E:
        print(E)
        return {'initialized': False, 'err': E}

def _destroy():
    global detector
    global initialized
    global async_process_t

    detector = None
    initialized = False
    async_process_t.join()

queue = [None, None, None]
# start the FPS counter
fps = FPS().start()


_frame = None


def _overlay(frame):
    return frame

def _calculate_overlay(frame):
    global _overlay

    #frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rects = detector.detectMultiScale(gray, scaleFactor=1.1,
                                      minNeighbors=5, minSize=(30, 30),
                                      flags=cv2.CASCADE_SCALE_IMAGE)

    boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

    # Updates overlay_pane by inferencing the latest frame.
    def overlay_function(frame):

        for (top, right, bottom, left) in boxes:
            # draw the predicted face name on the image
            cv2.rectangle(frame, (left, top), (right, bottom),
                          (0, 255, 0), 2)

        return frame

    _overlay = overlay_function


def _async_process():
    while initialized:
        if _frame is not None:
            _calculate_overlay(_frame)


def _async_overlay(frame):
    global _frame
    _frame = frame
    return _overlay(frame)
