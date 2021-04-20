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
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from time import sleep
import uuid
import shutil

# define the paths to the Not Santa Keras deep learning model and
# audio file
MODEL_PATH = "cat_detector.model"
# initialize the total number of frames that *consecutively* contain
# santa along with threshold required to trigger the santa alarm
TOTAL_CONSEC_WILSON = 0
TOTAL_CONSEC_OWEN = 0
TOTAL_CONSEC_NOTHING = 0
TOTAL_CONSEC_BOTHCATS = 0
TOTAL_THRESH = 20
TOTAL_THRESH_NOTHING = 200
TOTAL_THRESH_STOPARDUINO = 202
TOTAL_THRESH_RETURNFROMBOTH = 100
TOTAL_THRESH_BOTHCATS = 20

#Email Variables
SMTP_SERVER = 'smtp.gmail.com' #Email Server (don't change!)
SMTP_PORT = 587 #Server Port (don't change!)
GMAIL_USERNAME = 'abc@gmail.com' #change this to match your gmail account
GMAIL_PASSWORD = 'password'  #change this to match your gmail password
recipient = "xyz@gmail.com"
# initialize is the santa alarm has been triggered
SANTA = False

emailNextFrame = False
emailSubject = "empty"
emailContent = "empty"
emailImage = "attachment_image.jpg"

#InformationFile
info_file_name = "log.txt"

#Set this to false normally!!! Set to True for testing of training model
run_training_seq = False


def SendMail(ImgFileName, subject, contents):
    img_data = open(ImgFileName, 'rb').read()
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = GMAIL_USERNAME
    msg['To'] = recipient

    text = MIMEText(contents)
    msg.attach(text)
    image = MIMEImage(img_data, name=os.path.basename(ImgFileName))
    msg.attach(image)

    s = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(GMAIL_USERNAME, GMAIL_PASSWORD)
    try:
        s.sendmail(GMAIL_USERNAME, recipient, msg.as_string())
        print("email sent")
    except:
        print("email failed trying again 1/3")
        try:
            s.sendmail(GMAIL_USERNAME, recipient, msg.as_string())
            print("email sent")
        except:
            print("email failed trying again 2/3")
            try:
                s.sendmail(GMAIL_USERNAME, recipient, msg.as_string())
                print("email sent")
            except:
                print("email failed trying again 3/3")
        
    s.quit()

WilsonFoodOpen = False
OwenFoodOpen = False
arduinoActive = False

# initialize the GPIOs
food1 = 23
food2 = 24
fill1 = 25
fill2 = 1
rx_Activate = 12
tx_Complete = 16

GPIO.setmode(GPIO.BCM)

GPIO.setup(food1, GPIO.OUT)
GPIO.setup(food2, GPIO.OUT)
GPIO.setup(fill1, GPIO.OUT)
GPIO.setup(fill2, GPIO.OUT)
GPIO.setup(tx_Complete, GPIO.OUT)
GPIO.setup(rx_Activate, GPIO.IN)
GPIO.output(tx_Complete, GPIO.LOW)

#servoPIN = 17
#GPIO.setup(servoPIN, GPIO.OUT)

# configure GPIO17 for pwm with 50hz 

#configure angle measurements
current_angle = 180
new_angle = 180
angleDiff = 20

def open_owen_food():
    global current_angle

def open_wilson_food():
    global current_angle

def close_food():
    global current_angle


#Look through information file to find state of the feeder
#if not os.path.isfile(info_file_name):
#    print('Information file does not exist.')
#else:
#    with open(info_file_name) as f:
#        info_file_content = f.read().splitlines()

f = open(info_file_name, "r")
list_of_lines = f.readlines()
f.close()

for line in list_of_lines:
    print(line)
    if(line == "init = 0"):
        run_training_seq = True
        list_of_lines[0] = "init = 1"

f = open(info_file_name, "w")
f.writelines(list_of_lines)
f.close()

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
#vs = VideoStream(src=0).start()
vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)

if(run_training_seq == True): 
    # define the name of the directory to be created
    path_owen = "owen"
    path_wilson = "wilson"
    path_nothing = "nothing"

    try:
        os.mkdir(path_owen)
    except OSError:
        print ("Creation of the directory %s failed" % path_owen)
    else:
        print ("Successfully created the directory %s " % path_owen)

    try:
        os.mkdir(path_wilson)
    except OSError:
        print ("Creation of the directory %s failed" % path_wilson)
    else:
        print ("Successfully created the directory %s " % path_wilson)

    try:
        os.mkdir(path_nothing)

    except OSError:
        print ("Creation of the directory %s failed" % path_nothing)
    else:
        print ("Successfully created the directory %s " % path_nothing)

    #Start with nothing in the room wait for space bar to be pressed on the keyboard
    input("Press any key to continue...")
    for x in range(0,5):
        unique_filename = str(uuid.uuid4()) + ".jpg"

        #temp = "nothing%s.jpg" % x
        frame = vs.read()
        cv2.imwrite(('nothing/' + unique_filename), frame)
        cv2.imshow('frame', frame)
        key = cv2.waitKey(1) & 0xFF
        time.sleep(.5)

    input("Press any key to continue...")
    for x in range(0,5):
        unique_filename = str(uuid.uuid4()) + ".jpg"

        #temp = "nothing%s.jpg" % x
        frame = vs.read()
        cv2.imwrite(('owen/' + unique_filename), frame)
        cv2.imshow('frame', frame)
        key = cv2.waitKey(1) & 0xFF
        time.sleep(.5)

    input("Press any key to continue...")
    for x in range(0,5):
        unique_filename = str(uuid.uuid4()) + ".jpg"

        #temp = "nothing%s.jpg" % x
        frame = vs.read()
        cv2.imwrite(('wilson/' + unique_filename), frame)
        cv2.imshow('frame', frame)
        key = cv2.waitKey(1) & 0xFF
        time.sleep(.5)
    
    input("Review images and press enter when done...")

    try:
        os.remove('nothing.zip')
    except OSError:
        print ("No zip file to remove")

    try:
        os.remove('owen.zip')
    except OSError:
        print ("No zip file to remove")

    try:
        os.remove('wilson.zip')
    except OSError:
        print ("No zip file to remove")

    shutil.make_archive('nothing', 'zip', 'nothing')
    shutil.make_archive('owen', 'zip', 'owen')
    shutil.make_archive('wilson', 'zip', 'wilson')




# load the model
print("[INFO] loading model...")
model = load_model(MODEL_PATH)

#SetAngle(180)

# loop over the frames from the video stream
while True:
    if(GPIO.input(rx_Activate) == GPIO.HIGH):
        arduinoActive = True
        print("RPI activated")
        while(arduinoActive == True):
            # grab the frame from the threaded video stream and resize it
            # to have a maximum width of 400 pixels
            frame = vs.read()
            frame = imutils.resize(frame, width=400)

            if(emailNextFrame == True):
                cv2.imwrite("attachment_image.jpg", frame)
             #   SendMail("attachment_image.jpg", emailSubject, emailContent)
                emailNextFrame = False

            # prepare the image to be classified by our deep learning network
            image = cv2.resize(frame, (28, 28))
            image = image.astype("float") / 255.0
            image = img_to_array(image)
            image = np.expand_dims(image, axis=0)
            # classify the input image and initialize the label and
            # probability of the prediction
            (nothing, bothcats, owen, wilson) = model.predict(image)[0]
            label = "Nothing"
            proba = nothing

            # check to see if cat was detected using our convolutional
            # neural network
            if (wilson >= owen) and (wilson >= nothing) and (wilson >= bothcats) and (wilson >= .6):
                label = "Wilson"
                proba = wilson
                if(TOTAL_CONSEC_WILSON < TOTAL_THRESH):
                    if(OwenFoodOpen == True):
                        TOTAL_CONSEC_WILSON += 5
                        TOTAL_CONSEC_OWEN  -= 5
                    else:
                        TOTAL_CONSEC_WILSON += 1
                        TOTAL_CONSEC_OWEN  -= 1
                        #treat both cats as nothing
                        TOTAL_CONSEC_NOTHING  -= 1
                        TOTAL_CONSEC_BOTHCATS  -= 1
                else:
                    #Clear All others
                    TOTAL_CONSEC_OWEN  = 0
                    #treat both cats as nothing
                    TOTAL_CONSEC_NOTHING  = 0
                    TOTAL_CONSEC_BOTHCATS  = 0

            elif (owen >= wilson) and (owen >= nothing) and (owen >= bothcats) and (owen >= .6):
                label = "Owen"
                proba = owen

                if(TOTAL_CONSEC_OWEN < TOTAL_THRESH):
                    if(WilsonFoodOpen == True):
                        TOTAL_CONSEC_WILSON -= 5
                        TOTAL_CONSEC_OWEN  += 5
                    else:
                        TOTAL_CONSEC_WILSON -= 1
                        TOTAL_CONSEC_OWEN  += 1
                        TOTAL_CONSEC_NOTHING  -= 1
                        TOTAL_CONSEC_BOTHCATS  -= 1

                else:
                    #Clear All others
                    TOTAL_CONSEC_WILSON  = 0
                    #treat both cats as nothing
                    TOTAL_CONSEC_NOTHING  = 0
                    TOTAL_CONSEC_BOTHCATS  = 0

            elif (bothcats >= wilson) and (bothcats >= nothing) and (bothcats >= owen) and (bothcats >= .9):
                label = "BothCats"
                proba = bothcats

                if(TOTAL_CONSEC_BOTHCATS < TOTAL_THRESH_BOTHCATS):
                    if((OwenFoodOpen == True) or (WilsonFoodOpen == True)):
                        TOTAL_CONSEC_BOTHCATS += 5
                        TOTAL_CONSEC_WILSON -= 5
                        TOTAL_CONSEC_OWEN -= 5
                        #don't clear nothing count it
                        TOTAL_CONSEC_NOTHING += 5
                    else:
                        TOTAL_CONSEC_BOTHCATS += 1
                        TOTAL_CONSEC_WILSON -= 1
                        TOTAL_CONSEC_OWEN -= 1
                        #don't clear nothing count it
                        TOTAL_CONSEC_NOTHING += 1
                else:
                    #Clear All others
                    TOTAL_CONSEC_WILSON  = 0
                    TOTAL_CONSEC_OWEN  = 0
                    #treat both cats as nothing
                    TOTAL_CONSEC_NOTHING  = TOTAL_THRESH_NOTHING
                    TOTAL_CONSEC_BOTHCATS  = TOTAL_THRESH_BOTHCATS

            else:
                label = "Nothing"
                proba = nothing
                TOTAL_CONSEC_WILSON -= 1
                TOTAL_CONSEC_OWEN -= 1
                #Do not clear bothcats count detection gets screwed up when both cats are there because they're in and out of the frame so much
                #TOTAL_CONSEC_BOTHCATS = 0

                if(TOTAL_CONSEC_NOTHING < TOTAL_THRESH_STOPARDUINO):
                    TOTAL_CONSEC_NOTHING += 1
                    GPIO.output(tx_Complete, GPIO.HIGH)


            TOTAL_CONSEC_OWEN = max(0,TOTAL_CONSEC_OWEN)
            TOTAL_CONSEC_WILSON = max(0,TOTAL_CONSEC_WILSON)
            TOTAL_CONSEC_NOTHING = max(0,TOTAL_CONSEC_NOTHING)
            TOTAL_CONSEC_BOTHCATS = max(0,TOTAL_CONSEC_BOTHCATS)

            if(TOTAL_CONSEC_WILSON >= TOTAL_THRESH):
                if(OwenFoodOpen == True):
                    #close_owen_food()
                    OwenFoodOpen = False
                if(WilsonFoodOpen == False):
                    emailSubject = "Wilson Is Eating!"
                    emailContent = "Wilson is eating at: " + time.ctime()
                    emailNextFrame = True
                    print("print next frame")
                    #open_wilson_food()
                    GPIO.output(food1, GPIO.HIGH)
                    WilsonFoodOpen = True    
            elif(WilsonFoodOpen == True):
                if(TOTAL_CONSEC_NOTHING >= TOTAL_THRESH_NOTHING) or (TOTAL_CONSEC_BOTHCATS >= TOTAL_THRESH_BOTHCATS):
                    #close_food()
                    GPIO.output(food1, GPIO.LOW)
                    WilsonFoodOpen = False

            if(TOTAL_CONSEC_OWEN >= TOTAL_THRESH):
                if(WilsonFoodOpen == True):
                    #close_wilson_food()
                    WilsonFoodOpen = False
                if(OwenFoodOpen == False):
                    emailSubject = "Owen Is Eating!"
                    emailContent = "Owen is eating at: " + time.ctime()
                    emailNextFrame = True
                    print("print next frame")
                    #open_owen_food()
                    GPIO.output(food2, GPIO.HIGH)
                    OwenFoodOpen = True
            elif(OwenFoodOpen == True):
                if(TOTAL_CONSEC_NOTHING >= TOTAL_THRESH_NOTHING) or (TOTAL_CONSEC_BOTHCATS >= TOTAL_THRESH_BOTHCATS):
                    close_food()
                    #GPIO.output(food1, GPIO.LOW)
                    OwenFoodOpen = False

            #if(TOTAL_CONSEC_NOTHING > TOTAL_THRESH):
            #    if(OwenFoodOpen == True):
            #        close_owen_food()
            #        OwenFoodOpen = False
            #    if(WilsonFoodOpen == True):
            #        close_wilson_food()
            #        WilsonFoodOpen = False

            # build the label and draw it on the frame

            print("Owen:     %r \n", TOTAL_CONSEC_OWEN)
            print("Wilson:   %r \n", TOTAL_CONSEC_WILSON)
            print("BothCats: %r \n", TOTAL_CONSEC_BOTHCATS)
            print("Nothing:  %r \n", TOTAL_CONSEC_NOTHING)
            owenprogress = TOTAL_CONSEC_OWEN * 5
            wilsonprogress = TOTAL_CONSEC_WILSON * 5
            bothcatsprogress = TOTAL_CONSEC_BOTHCATS * 5
            nothingprogress = TOTAL_CONSEC_NOTHING / 2

            # Stop Arduino commands if nothing present
            if(TOTAL_CONSEC_NOTHING >= TOTAL_THRESH_STOPARDUINO):
                arduinoActive = False

            #nothingprogress_string = "[" + ('|' * int(nothingprogress)) + (' ' * 100-int(nothingprogress)) + "]"

            owenprogress_string = "["
            for x in range(int((int(owenprogress))/10)):
                owenprogress_string = owenprogress_string + "|"
            for x in range(int(10 - (int(owenprogress)/10))):
                owenprogress_string = owenprogress_string + " "
            owenprogress_string = owenprogress_string + "]" 

            wilsonprogress_string = "["
            for x in range(int((int(wilsonprogress))/10)):
                wilsonprogress_string = wilsonprogress_string + "|"
            for x in range(int(10 - (int(wilsonprogress)/10))):
                wilsonprogress_string = wilsonprogress_string + " "
            wilsonprogress_string = wilsonprogress_string + "]" 

            bothcatsprogress_string = "["
            for x in range(int((int(bothcatsprogress))/10)):
                bothcatsprogress_string = bothcatsprogress_string + "|"
            for x in range(int(10 - (int(bothcatsprogress)/10))):
                bothcatsprogress_string = bothcatsprogress_string + " "
            bothcatsprogress_string = bothcatsprogress_string + "]" 

            nothingprogress_string = "["
            for x in range(int((int(nothingprogress))/10)):
                nothingprogress_string = nothingprogress_string + "|"
            for x in range(int(10 - (int(nothingprogress)/10))):
                nothingprogress_string = nothingprogress_string + " "
            nothingprogress_string = nothingprogress_string + "]" 




            label = "{}: {:.2f}%".format(label, proba * 100)
            label1 = "Owen    :" + owenprogress_string
            label2 = "Wilson   :" + wilsonprogress_string
            label3 = "Both    :" + bothcatsprogress_string
            label4 = "Nothing :" + nothingprogress_string
            frame = cv2.putText(frame, label, (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            frame = cv2.putText(frame, label1, (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            frame = cv2.putText(frame, label2, (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            frame = cv2.putText(frame, label3, (10, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            frame = cv2.putText(frame, label4, (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            # show the output frame
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF
            #print("%r Owen, %r Wilson", OwenFoodOpen, WilsonFoodOpen)
            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break
            elif key == ord("v"):
                OwenFoodOpen = False
                WilsonFoodOpen = True
                open_wilson_food()
            elif key == ord("b"):
                OwenFoodOpen = True
                WilsonFoodOpen = False
                open_owen_food()

# do a bit of cleanup
GPIO.cleanup()
print("[INFO] cleaning up...")
cv2.destroyAllWindows()
vs.stop()
