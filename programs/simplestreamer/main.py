import imutils
import cv2
import time
from imutils.video import VideoStream
from app import app
from flask import Response, render_template
from tools.orient_video import orient_frame
from tools.buzzer import enable_buzzer, disable_buzzer, set_freq
from tools.LED import red, green, blue

vs = VideoStream(src=0).start()
recording = False
from os import listdir
import os
from random import randint
from tools.kiwilog import kiwi
import datetime
from threading import Thread, Lock
from flask import jsonify
import time
import sys

# TODO: Make the capture and record functions actually work.
# Capture will probably be easiest.
# save captures in /database/captures

log = kiwi.instance('apps.simplestreamer')
log.add_log('loaded simplestreamer dependencies')
out = None
eating_leftovers = False
camera_mutex = Lock()

fifo_queue = []
GLOBAL_FPS = 15
recording_start = datetime.datetime.now()
file_format = 'mp4'
import math
frame = None
buffer_file = '' # The name of a the buffering file (if there is one)
buffer_pct = 0 # The percentage of a buffer that has been cleared


def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

@app.route('/frame_buffer_size', methods=["POST", "GET"])
def frame_buffer_ajax():
    return jsonify({'frames': len(fifo_queue), 'size': convert_size(sys.getsizeof(fifo_queue))})

@app.route('/recording_status_ajax', methods=["POST", "GET"])
def recording_status_ajax():
    duration = datetime.datetime.now() - recording_start
    # Retrurns the recording duration length, and device recording status as JSON
    if recording:
        return jsonify({'recording': recording,
                        'duration': str(duration)[:-5]})
    else:
        return jsonify({'recording': recording})

def frame_cap_daemon():
    frame_cnt = 0
    # Captures the frames and also writes to the recording output buffer.
    # Remember we have a frame read/write mutex
    global frame

    dly = datetime.datetime.now()

    suma = datetime.timedelta()
    sumb = datetime.timedelta()
    sumc = datetime.timedelta()
    sumd = datetime.timedelta()
    dly_cnt = datetime.timedelta()

    start_time = datetime.datetime.now()
    framecnt = 0
    target_fps = GLOBAL_FPS
    target_frametime = datetime.timedelta(seconds=1 / GLOBAL_FPS)
    global fifo_queue
    frame_timer = datetime.datetime.now()
    while True:
        frame_cnt += 1
        #print("Frame count: ", frame_cnt)
        # If FPS > target FPS, we need to make the delay longer
        # If FPS < target fps, we need to make the delay shorter
        # If ==, don't change the delay

        # print(f"FRAME {framecnt}")
        framecnt += 1
        # print("A")
        a = datetime.datetime.now()
        camera_mutex.acquire()
        frame = orient_frame(vs.read())
        suma += (datetime.datetime.now() - a)

        # print("B")


        # print("C")
        a = datetime.datetime.now()
        #frame = imutils.resize(frame, width=720)  # To save bandwidth?
        camera_mutex.release()

        sumc += (datetime.datetime.now() - a)

        # print("D")
        a = datetime.datetime.now()




        sumd += (datetime.datetime.now() - a)


        a = datetime.datetime.now()
        if recording:
            fifo_queue.append(frame)  # add frame to frame buffer for encoding mutex IF WE ARE RECORDING
        sumb += (datetime.datetime.now() - a)

        # print("E")

        # print(f"SUM A: {suma}")
        # print(f"SUM B: {sumb}")
        # print(f"SUM C: {sumc}")
        # print(f"SUM D: {sumd}")
        # If we haven't met the target frametime, wait until satisfied and restart timer
        dly_cnt = datetime.datetime.now() - frame_timer
        time.sleep(
            max(target_frametime.total_seconds() - dly_cnt.total_seconds(), 0))  # We want FPS to equal target_fps
        frame_timer = datetime.datetime.now()
        FPS = datetime.timedelta(seconds=framecnt) / (datetime.datetime.now() - start_time)

frame_cap_daemon_thread = Thread(target=frame_cap_daemon)
frame_cap_daemon_thread.start()
def recording_daemon():
    log.add_log("Recording daemon checking in!")
    global out
    global fifo_queue
    global eating_leftovers
    global file_format
    global buffer_file

    while True:

        if recording and (int((datetime.datetime.now() - recording_start).total_seconds()) % 2):
            red()
        elif recording:
            blue()



        # If recording but no output object, create one
        if recording and out is None:
            # Create output object, also make thumbnail!
            timestamp = datetime.datetime.now()
            file_format = file_format
            file_path = f'app/static/appstatic/simplestreamer/{timestamp}.{file_format}'
            thumb_path = f'app/static/appstatic/simplestreamer/thumbnails/{timestamp}.jpg'
            buffer_file = file_path
            frame = orient_frame(vs.read())
            thumbnail = cv2.resize(frame, (144, 96), interpolation=cv2.INTER_AREA)
            cv2.imwrite(thumb_path, thumbnail)
            log.add_log("New VideoWriter object created")
            fourcc = cv2.VideoWriter_fourcc(*"H264")
            #fourcc = 0x00000021
            out = cv2.VideoWriter(file_path, fourcc, GLOBAL_FPS, (640, 480))

        # IF frame in queue, write it
        if len(fifo_queue) and out is not None:
            if not recording:
                pass
                # blue()
            time = datetime.datetime.now()
            eating_leftovers = not recording



            out.write(fifo_queue[0])

            #print("H.264 Write: ", datetime.datetime.now() - time)

            fifo_queue = fifo_queue[1:]
            # Write object


        elif not recording and out is not None:
            # green()
            # kill the output object
            buffer_file = 'wehdiuwenfbiuwencodwcniwuec'
            out.release()
            eating_leftovers = False
            out = None
    # We will turn this into a thread that processes frames in fifo_queue as quickly as possible
    # This thread will also terminate the output object
    # It will continue writing if recording is false but some frames are waiting to be parsed.


t = Thread(target=recording_daemon)
t.start()


@app.route("/delete_all", methods=['POST', 'GET'])
def delete_img():
    img_path = 'app/static/appstatic/simplestreamer/'
    thumb_path = 'app/static/appstatic/simplestreamer/thumbnails/'
    # Deletes all images in the gallery. This is a debug feature. FIXME
    delete_thumb_list = listdir(thumb_path)
    delete_img_list = listdir(img_path)
    delete_img_list = [x for x in delete_img_list if x != 'thumbnails']  # FIXME: This is trashy
    log.add_log(f"Deleting {delete_thumb_list} {delete_img_list}")
    for i in delete_img_list:
        os.remove(img_path + i)
    for j in delete_thumb_list:
        os.remove(thumb_path + j)
    return gallery()



@app.route('/gallery')
def gallery():
    # Return a gallery view of captured videos and images

    # Return a dic: Int (ordinal) : {thumb_url, src_url}
    # Get the list of files available to download
    # Maybe offer a preview?
    src_list = [f'static/appstatic/simplestreamer/{i}'
                for i in listdir('app/static/appstatic/simplestreamer') if "thumbnails" not in i]
    thumb_list = [f'static/appstatic/simplestreamer/thumbnails/{i}'
                  for i in listdir('app/static/appstatic/simplestreamer/thumbnails')]
    d = []
    # TODO: Add type (video or image) to this json
    src_list.sort()
    thumb_list.sort()
    for src, thumb in zip(src_list, thumb_list):
        if file_format in src:
            src_type = 'vid'
        else:
            src_type = 'img'



        if src == buffer_file: # If this file is currently being buffered by the buffer thread
            d.append({'src': 'https://homepages.cae.wisc.edu/~ece533/images/airplane.png', # TODO: Replace with a "buffering pls wait" image
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
    return render_template('simplestreamer/gallery.html', file_list=d)


@app.route('/capture', methods=['POST'])
def capture():
    # This sequence makes a capture flash.
    enable_buzzer()
    red()
    set_freq(1174.66)
    time.sleep(0.1)
    disable_buzzer()
    blue()
    time.sleep(0.05)
    enable_buzzer()
    set_freq(1174.66)
    time.sleep(0.1)
    disable_buzzer()
    green()
    # Save capture to database/captures/

    timestamp = datetime.datetime.now()
    # TODO: Implement a mutex on frame captues?
    frame = orient_frame(vs.read())
    # TODO: What is the file name format?
    # Let's number them ordinally, I guess
    file_num = len(listdir('app/static/appstatic/simplestreamer'))
    file_path = f'app/static/appstatic/simplestreamer/{timestamp}.jpg'
    thumb_path = f'app/static/appstatic/simplestreamer/thumbnails/{timestamp}.jpg'
    thumbnail = cv2.resize(frame, (144, 96), interpolation=cv2.INTER_AREA)
    log.add_log(f"saving image to path {file_path}. Thumbnail to path {thumb_path}")
    cv2.imwrite(file_path, frame)
    cv2.imwrite(thumb_path, thumbnail)

    return ''


@app.route('/stop_record', methods=['POST', 'GET'])
def stop_record():
    global recording

    recording = False
    enable_buzzer()
    green()
    set_freq(587.330)
    time.sleep(0.2)
    disable_buzzer()

    return "{'leftovers': 1}"


@app.route("/leftovers", methods=['POST', 'GET'])
def leftovers_ajax():
    # Tell if leftovers are being processed so we know to free the user
    if eating_leftovers:
        return jsonify({'eating_leftovers': True, 'leftovers_remaining': len(fifo_queue)})
    else:
        return jsonify({'eating_leftovers': False})


@app.route('/record', methods=["POST"])
def record():
    # Set new record output object
    global recording_start
    recording_start = datetime.datetime.now()

    enable_buzzer()
    red()
    set_freq(1174.66)
    time.sleep(0.2)
    disable_buzzer()

    global recording
    recording = True
    return jsonify({'success': True})


@app.route("/video_feed")
def video_feed():
    log.add_log("/video_feed has been pinged")
    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")




def generate():
    serv_count = 0
    while True:
        serv_count += 1
        #print("serv count ", serv_count)
        camera_mutex.acquire()
        ## """Video streaming generator function."""
        by = cv2.imencode('.jpg', frame)[1].tostring()
        camera_mutex.release()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + by + b'\r\n')


def main():
    if recording:
        r = 'true'
    else:
        r = 'false'
    return render_template('simplestreamer/template.html', recording=r)
