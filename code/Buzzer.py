import RPi.GPIO as GPIO
import time

Buzzer = 11


def setup(pin):
    global BuzzerPin
    BuzzerPin = pin
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BuzzerPin, GPIO.OUT)
    GPIO.output(BuzzerPin, GPIO.HIGH)


def beep(x):
    GPIO.output(BuzzerPin, GPIO.LOW)
    time.sleep(x)
    GPIO.output(BuzzerPin, GPIO.HIGH)
    time.sleep(x)

        
if __name__ == '__main__':
    setup(Buzzer)
    while True:
        beep(3)
