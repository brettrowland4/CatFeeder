import RPi.GPIO as GPIO
import time

# initialize the servo
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

#GPIO.setup(lightGatePIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
while(True):
    print(GPIO.input(rx_Activate))
    if(GPIO.input(rx_Activate) == GPIO.HIGH):
        print("RPI activated")
        while(1):
            try:
                #GPIO.output(food1, GPIO.LOW)
                #GPIO.output(food2, GPIO.LOW)
                #GPIO.output(fill1, GPIO.LOW)
                #GPIO.output(fill2, GPIO.LOW)
                #time.sleep(2)
                #GPIO.output(food1, GPIO.HIGH)
                #GPIO.output(food2, GPIO.HIGH)
                #GPIO.output(fill1, GPIO.HIGH)
                #GPIO.output(fill2, GPIO.HIGH)
                #time.sleep(2)
                
                GPIO.output(food2, GPIO.HIGH)
                time.sleep(5)
                GPIO.output(food2, GPIO.LOW)
                time.sleep(5)
                GPIO.output(fill2, GPIO.HIGH)
                time.sleep(5)
                GPIO.output(fill2, GPIO.LOW)
                time.sleep(5)
                GPIO.output(fill1, GPIO.HIGH)
                time.sleep(5)
                GPIO.output(fill1, GPIO.LOW)
                time.sleep(5)
                GPIO.output(food1, GPIO.HIGH)
                time.sleep(5)
                GPIO.output(food1, GPIO.LOW)
                time.sleep(5)
                
            except KeyboardInterrupt:
                GPIO.cleanup() # cleanup all GPIO
                GPIO.output(tx_Complete, GPIO.HIGH)
