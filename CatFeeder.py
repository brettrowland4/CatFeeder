from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from imutils.video import VideoStream
from threading import Thread
import numpy as np 
import imutils
import time
import cv2
import os
import RPi.GPIO as GPIO




# define the paths to the Not Santa Keras deep learning model and
# audio file
MODEL_PATH = "cat_detector.model"
# initialize the total number of frames that *consecutively* contain
# santa along with threshold required to trigger the santa alarm
TOTAL_CONSEC_WILSON = 0
TOTAL_CONSEC_OWEN = 0
TOTAL_THRESH = 20
# initialize is the santa alarm has been triggered
SANTA = False

WilsonFoodOpen = False
OwenFoodOpen = False

# initialize the servo
servoPIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

# configure GPIO17 for pwm with 50hz 
p = GPIO.PWM(servoPIN, 50)

# Test
p.start(0)

def open_wilson_food():
    p.ChangeDutyCycle(5)
    time.sleep(1)
    p.ChangeDutyCycle(0)

def close_wilson_food():
    p.ChangeDutyCycle(90)
    time.sleep(1)
    p.ChangeDutyCycle(0)

def open_owen_food():
    p.ChangeDutyCycle(90)
    time.sleep(1)
    p.ChangeDutyCycle(0)

def close_owen_food():
    p.ChangeDutyCycle(5)
    time.sleep(1)
    p.ChangeDutyCycle(0)

# load the model
print("[INFO] loading model...")
model = load_model(MODEL_PATH)

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
#vs = VideoStream(src=0).start()
vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)

# loop over the frames from the video stream
while True:
    # grab the frame from the threaded video stream and resize it
    # to have a maximum width of 400 pixels
    frame = vs.read()
    frame = imutils.resize(frame, width=400)

    # prepare the image to be classified by our deep learning network
    image = cv2.resize(frame, (28, 28))
    image = image.astype("float") / 255.0
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    # classify the input image and initialize the label and
    # probability of the prediction
    (nothing, owen, wilson) = model.predict(image)[0]
    label = "Nothing"
    proba = nothing

    # check to see if santa was detected using our convolutional
    # neural network
    if (wilson >= owen) and (wilson >= nothing):
        label = "Wilson"
        proba = wilson
        TOTAL_CONSEC_WILSON += 1
        TOTAL_CONSEC_OWEN = 0

    elif (owen >= wilson) and (owen >= nothing):
        label = "Owen"
        proba = owen
        TOTAL_CONSEC_WILSON = 0
        TOTAL_CONSEC_OWEN += 1
    else:
        label = "Nothing"
        proba = nothing
        TOTAL_CONSEC_WILSON = 0;
        TOTAL_CONSEC_OWEN = 0;

    if(TOTAL_CONSEC_WILSON > TOTAL_THRESH):
        if(WilsonFoodOpen == False):
            open_wilson_food()
            WilsonFoodOpen = True
    elif(WilsonFoodOpen == True):
        close_wilson_food()
        WilsonFoodOpen = False

    if(TOTAL_CONSEC_OWEN > TOTAL_THRESH):
        if(OwenFoodOpen == False):
            open_owen_food()
            OwenFoodOpen = True
    elif(OwenFoodOpen == True):
        close_owen_food()
        OwenFoodOpen = False

    # build the label and draw it on the frame
    label = "{}: {:.2f}%".format(label, proba * 100)
    frame = cv2.putText(frame, label, (10, 25),
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    # show the output frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
 
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
# do a bit of cleanup
p.stop()
GPIO.cleanup()
print("[INFO] cleaning up...")
cv2.destroyAllWindows()
vs.stop()
