import time
import RPi.GPIO as GPIO

# initialize the servo
servoPIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)
GPIO.setup(27, GPIO.IN)

# configure GPIO17 for pwm with 50hz 
p = GPIO.PWM(servoPIN, 50)

# Test
p.start(0)
count = 0


while True:
    input = GPIO.input(27)
    print(input)
    #time.sleep(.2)
    if(input == 0):
        count = count + 1
        if( count > 3):
            #we have stopped on a target
            p.ChangeDutyCycle(0)

            #sleep longer for first time stopping
            #if(count == 4):
                #time.sleep(1)

            count = count + 1

            #print("nothing")
            time.sleep(.01)

    elif(input == 1):
        count = 0
        p.ChangeDutyCycle(5)
        #time.sleep(.2)
        #p.ChangeDutyCycle(0)

# do a bit of cleanup
p.stop()
GPIO.cleanup()