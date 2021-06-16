import math
import random
import point
import settings
import drive
import distancesensor
import servo
import RPi.GPIO as GPIO
import time
import wiringpi2
import main_functions

history = []
open = []


finishX = math.floor((settings.x_finish - settings.x_start)/settings.cell_lenght)
finishY = math.floor((settings.y_finish - settings.y_start)/settings.cell_lenght)
finishPoint = point.StartPoint(finishX, finishY, False)
main_functions.d_Star(finishPoint, 0, 0)
