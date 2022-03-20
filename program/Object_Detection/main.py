from edgetpu.detection.engine import DetectionEngine
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
labels = {}
for row in open('program/mobilenet_detect_demo/mobilenet_ssd_v2/coco_labels.txt'):
	# unpack the row and update the labels dictionary
	(classID, label) = row.strip().split(maxsplit=1)
	labels[int(classID)] = label.strip()
model = DetectionEngine('program/mobilenet_detect_demo/mobilenet_ssd_v2/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite')

whitelist = []
beep_mode = False

def generate():
	#####
# loop over the frames from the video Video_Streaming
	while True:
		# grab the frame from the threaded video Video_Streaming and resize it
		# to have a maximum width of 500 pixels
		frame = vs.read()
		frame = imutils.resize(frame, width=500)
		orig = frame.copy()

		# prepare the frame for classification by converting (1) it from
		# BGR to RGB channel ordering and then (2) from a NumPy array to
		# PIL image format
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		frame = Image.fromarray(frame)

		# make predictions on the input frame
		start = time.time()
		results = model.detect_with_image(frame, threshold=confidence,
										keep_aspect_ratio=True, relative_coord=False)
		end = time.time()
		# ensure at least one result was found
		for r in results:
			# extract the bounding box and box and predicted class label
			box = r.bounding_box.flatten().astype("int")
			(startX, startY, endX, endY) = box
			label = labels[r.label_id]
			if label in whitelist:
				if beep_mode:
					b_tone()
				# draw the bounding box and label on the image
				cv2.rectangle(orig, (startX, startY), (endX, endY),
							  (0, 255, 0), 2)
				y = startY - 15 if startY - 15 > 15 else startY + 15
				text = "{}: {:.2f}%".format(label, r.score * 100)
				cv2.putText(orig, text, (startX, y),
							cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

		cv2.imwrite('pic.jpg', orig)
		yield (b'--frame\r\n'
			   b'Content-Type: image/jpeg\r\n\r\n' + open('pic.jpg', 'rb').read() + b'\r\n')

@app.route('/beeptoggle',  methods=["GET", "POST"])
def beep_toggle():
	global beep_mode
	beep_mode = not beep_mode
	return render_template('mobilenet_detect_demo/template.html', labels=[labels[x] for x in labels])


@app.route('/update_checkbox', methods=["GET", "POST"])
def update_checkbox():
	print("Fixme")
	x = request.form
	print("Selected elements")
	for i in list(x):
		print(i)
	global whitelist
	whitelist = list(x)
	cmd = [i for i in x]
	print(cmd)
	return render_template('mobilenet_detect_demo/template.html', labels = [labels[x] for x in labels])



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
