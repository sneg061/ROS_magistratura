import RPi.GPIO as GPIO
import time

def servo(angle):

        port=18

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(port,GPIO.OUT)
        p=GPIO.PWM(port,50)
        p.start(7.5)
        p.ChangeDutyCycle(12.5-angle/18)
        time.sleep(1)
        p.stop()
        GPIO.cleanup()
