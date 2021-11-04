import RPi.GPIO as GPIO
import time

CHANNEL = 4
GPIO.setmode(GPIO.BCM)  
GPIO.setup(CHANNEL, GPIO.IN)
 
while True:
    status = GPIO.input(CHANNEL)
    if not status:
        print("ok")
    else:
        print("Loud voice")
    

