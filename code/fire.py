import RPi.GPIO as GPIO
import time

pin_fire = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_fire, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
try:
    while True:
        status = GPIO.input(pin_fire)
        if status == True:
            print('没有检测到火')
        else:
            print('检测到火灾')
        time.sleep(0.5)
except KeyboradInterrupt:
    GPIO.cleanup()
