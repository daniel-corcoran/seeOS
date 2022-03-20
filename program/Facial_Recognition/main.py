from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import cv2
from twilio.rest import Client
from imgurpython import ImgurClient

tw_account_sid = 'AC187864d6bb8a603665d83632571f02cc'
tw_auth_token = '3d7951e1fc7ef42813c4e44ec9417654'
tw_client = Client(tw_account_sid, tw_auth_token)

im_client_id = 'd6464f94c8eea45'
im_client_secret = 'db8c63ebe9477b934333a8f27fded489252a5e97'

im_client = ImgurClient(im_client_id, im_client_secret)



data = pickle.loads(open('programs/face_friend/encodings.pickle', "rb").read())
detector = cv2.CascadeClassifier('programs/face_friend/haarcascade_frontalface_default.xml')

# initialize the video Video_Streaming and allow the camera sensor to warm up
print("[INFO] starting video Video_Streaming...")
vs = VideoStream(src=0).start()
# vs = VideoStream(usePiCamera=True).start()

queue = [None, None, None]
# start the FPS counter
fps = FPS().start()

def generate():
    global queue
    while True:
        # grab the frame from the threaded video Video_Streaming and resize it
        # to 500px (to speedup processing)
        frame = vs.read()
        frame = imutils.resize(frame, width=500)

        # convert the input frame from (1) BGR to grayscale (for face
        # detection) and (2) from BGR to RGB (for face recognition)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # detect faces in the grayscale frame
        rects = detector.detectMultiScale(gray, scaleFactor=1.1,
                                          minNeighbors=5, minSize=(30, 30),
                                          flags=cv2.CASCADE_SCALE_IMAGE)

        # OpenCV returns bounding box coordinates in (x, y, w, h) order
        # but we need them in (top, right, bottom, left) order, so we
        # need to do a bit of reordering
        boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

        # compute the facial embeddings for each face bounding box
        encodings = face_recognition.face_encodings(rgb, boxes)
        names = []

        # loop over the facial embeddings
        for encoding in encodings:
            # attempt to match each face in the input image to our known
            # encodings
            matches = face_recognition.compare_faces(data["encodings"],
                                                     encoding)
            name = "Unknown"

            # check to see if we have found a match
            if True in matches:
                # find the indexes of all matched faces then initialize a
                # dictionary to count the total number of times each face
                # was matched
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                # loop over the matched indexes and maintain a count for
                # each recognized face face
                for i in matchedIdxs:
                    name = data["names"][i]
                    counts[name] = counts.get(name, 0) + 1

                # determine the recognized face with the largest number
                # of votes (note: in the event of an unlikely tie Python
                # will select first entry in the dictionary)
                name = max(counts, key=counts.get)

            # update the list of names
            names.append(name)
        queue.append(names)
        queue = queue[1:]
        print(queue)

        if queue == [['Unknown'],['Unknown'],['Unknown']]:
            try:
                im = im_client.upload_from_path('pic.jpg')
                url = im['link']


                # Send a text
                message = tw_client.messages \
                    .create(
                    body="Tree Camera detected an unknown face.",
                    media_url=url,
                    from_='+12058968162',
                    to='+15138509006'
                )

                print(message.sid)
            except Exception as E:
                print(E)
        # loop over the recognized faces
        for ((top, right, bottom, left), name) in zip(boxes, names):
            # draw the predicted face name on the image
            cv2.rectangle(frame, (left, top), (right, bottom),
                          (0, 255, 0), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                        0.75, (0, 255, 0), 2)

        # display the image to our screen
        cv2.imwrite('pic.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + open('pic.jpg', 'rb').read() + b'\r\n')



