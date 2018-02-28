#TEAM 13 LAB 2

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import time     # import the time library for the sleep function
import grovepi
import brickpi3 # import the BrickPi3 drivers
import math

#from Lock import lock

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

ultrasonic_sensor_port = 2

#grovepi.ultrasonicRead(ultrasonic_sensor_port



#obs

def pathFind():
    while True:
        state = 0
        ultra = grovepi.ultrasonicRead(ultrasonic_sensor_port)
        if (ultra > 15):
            state = 0
            runA(50)
        else:
            if (state == 0):
                state = 1
                print(state)
                turnR90()
            if (state == 1):
                state = 2
                print(state)
                turnL90()
                turnL90()
            if (state == 2):
                state = 3
                print(state)
                print("turn around")
        time.sleep(.25)


#with ultrasonic

def wallStop(dps):
    runA(dps)
    ultra = 25
    while(ultra > 15):
        ultra = grovepi.ultrasonicRead(ultrasonic_sensor_port)
        print(ultra)
        time.sleep(.25)
    stop()


#run functions

def run(letter, dps):
    if (letter == "A"): #front right
        BP.set_motor_dps(BP.PORT_A, -1 * dps)
    elif (letter == "B"): #back right
        BP.set_motor_dps(BP.PORT_B, dps)
    elif (letter == "C"): #back left
        BP.set_motor_dps(BP.PORT_C, dps)
    elif (letter == "D"):
        BP.set_motor_dps(BP.PORT_D, -1 * dps)

def runA(dps):
    BP.set_motor_dps(BP.PORT_A, -1 * dps)
    BP.set_motor_dps(BP.PORT_B, dps)
    BP.set_motor_dps(BP.PORT_C, dps)
    BP.set_motor_dps(BP.PORT_D, -1 * dps)


#turn functions

def turnR(dps):
    stop()
    BP.set_motor_dps(BP.PORT_A, dps)
    BP.set_motor_dps(BP.PORT_B, -1 * dps)
    BP.set_motor_dps(BP.PORT_C, dps)
    BP.set_motor_dps(BP.PORT_D, -1 * dps)

def turnL(dps):
    stop()
    BP.set_motor_dps(BP.PORT_A, -1 * dps)
    BP.set_motor_dps(BP.PORT_B, dps)
    BP.set_motor_dps(BP.PORT_C, -1 *dps)
    BP.set_motor_dps(BP.PORT_D, dps)

def turn(dpsL, dpsR):
    stop()
    BP.set_motor_dps(BP.PORT_A, -1 * dpsR)
    BP.set_motor_dps(BP.PORT_B, dpsR)
    BP.set_motor_dps(BP.PORT_C, dpsL)
    BP.set_motor_dps(BP.PORT_D, -1 * dpsL)


#deg turns

def turnR90():
    dps = 50
    turnR(dps)
    time.sleep(215.0/dps)
    stop()

def turnL90():
    dps = 50
    turnL(dps)
    time.sleep(215.0/dps)
    stop()

def turnRdeg(deg):
    dps = 50
    turnR(dps)
    time.sleep(210.0*(deg/90.0)/dps)
    stop()

def turndeg(deg):
    dps = 50
    turnR(dps)
    time.sleep(210.0*(deg/90.0)/dps)
    stop()

#stop functions
        
def stop():
    BP.set_motor_dps(BP.PORT_A, 0)
    BP.set_motor_dps(BP.PORT_B, 0)
    BP.set_motor_dps(BP.PORT_C, 0)
    BP.set_motor_dps(BP.PORT_D, 0)

def s():
    stop()


