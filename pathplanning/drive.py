import wiringpi2
import time
import settings

def motor_go(TYPE,angle=90):
    ON=1
    OFF=0
    IN=0
    OUT=1

    M1=38
    M2=40
    PWMA=37
    M3=31
    M4=33
    PWMB=32

    wiringpi2.wiringPiSetupPhys()
    wiringpi2.pinMode(M1, OUT)
    wiringpi2.pinMode(M2, OUT)
    wiringpi2.pinMode(M3, OUT)
    wiringpi2.pinMode(M4, OUT)
    wiringpi2.pinMode(PWMA, OUT)
    wiringpi2.pinMode(PWMB, OUT)

    def stop():
        wiringpi2.digitalWrite(M1, OFF)
        wiringpi2.digitalWrite(M2, OFF)
        wiringpi2.digitalWrite(M3, OFF)
        wiringpi2.digitalWrite(M4, OFF)

    def front():
        wiringpi2.digitalWrite(M1, ON)
        wiringpi2.digitalWrite(M2, OFF)
        wiringpi2.digitalWrite(M3, ON)
        wiringpi2.digitalWrite(M4, OFF)

    def back():
        wiringpi2.digitalWrite(M1, OFF)
        wiringpi2.digitalWrite(M2, ON)
        wiringpi2.digitalWrite(M3, OFF)
        wiringpi2.digitalWrite(M4, ON)

    def left():
        wiringpi2.digitalWrite(M1, ON)
        wiringpi2.digitalWrite(M2, OFF)
        wiringpi2.digitalWrite(M3, OFF)
        wiringpi2.digitalWrite(M4, ON)

    def right():
        wiringpi2.digitalWrite(M1, OFF)
        wiringpi2.digitalWrite(M2, ON)
        wiringpi2.digitalWrite(M3, ON)
        wiringpi2.digitalWrite(M4, OFF)

    wiringpi2.digitalWrite(PWMA, ON)
    wiringpi2.digitalWrite(PWMB, ON)

    if TYPE=="front":
        front()
        time.sleep(settings.cell_lenght/settings.robot_speed)
    elif TYPE=="back":
        back()
        time.sleep(settings.cell_lenght/settings.robot_speed)
    elif TYPE=="left":
        left()
        time.sleep(angle * settings.time_full_left)
    elif TYPE=="right":
        right()
        time.sleep(angle * settings.time_full_right)
    else: pass

    stop()
    wiringpi2.digitalWrite(PWMA, OFF)
    wiringpi2.digitalWrite(PWMB, OFF)
