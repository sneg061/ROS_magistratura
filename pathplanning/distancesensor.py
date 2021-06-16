import wiringpi2
import time

def findDistance(TYPE):
    ON=1
    OFF=0
    IN=0
    OUT=1
    PULSE=0.00001
    SPEED_OF_SOUND=34029

    if TYPE == "front":
        TRIG = 15
        ECHO = 13
    elif TYPE == "back":
        TRIG = 16
        ECHO = 18
    elif TYPE != "stop":
        return False
    else: return True

    wiringpi2.wiringPiSetupPhys()
    wiringpi2.pinMode(TRIG, OUT)
    wiringpi2.pinMode(ECHO, IN)
    wiringpi2.digitalWrite(TRIG, OFF)

    wiringpi2.digitalWrite(TRIG, ON)
    time.sleep(PULSE)
    wiringpi2.digitalWrite(TRIG, OFF)
    starttime=time.time()
    stop=starttime
    start=starttime

    while wiringpi2.digitalRead(ECHO)==0 and start<starttime+2:
        start=time.time()
    while wiringpi2.digitalRead(ECHO)==1 and stop<starttime+2:
        stop=time.time()
    delta=stop-start
    resultDistance=delta*SPEED_OF_SOUND
    return resultDistance/2.0


