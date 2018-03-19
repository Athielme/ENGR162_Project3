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
RIGHT_MOTOR = BP.PORT_A
LEFT_MOTOR = BP.PORT_D

################DRIVING#######################

FORWARD_DRIVE_SPEED = -10 #cm per second
TURN_CMPS = -5 #cm per second
STOP_DISTANCE = 15 #cm

###########PHYSICAL DIMENTIONS################

WHEEL_DIAMETER = 6 #cm
DISTANCE_BETWEEN_TIRES = 13.5 #cm
TURN_SPEED = float((TURN_CMPS*180)/((WHEEL_DIAMETER/2)*3.14))

def resetMotorEncoders():
     #reset motor encoders
     BP.offset_motor_encoder(BP.PORT_A, BP.get_motor_encoder(BP.PORT_A))
     BP.offset_motor_encoder(BP.PORT_B, BP.get_motor_encoder(BP.PORT_B))
     BP.offset_motor_encoder(BP.PORT_C, BP.get_motor_encoder(BP.PORT_C))
     BP.offset_motor_encoder(BP.PORT_D, BP.get_motor_encoder(BP.PORT_D))

def printEncoders(): #used for debugging
     try:
          print("Encoder B: %6d C: %6d" % (BP.get_motor_encoder(BP.PORT_B), BP.get_motor_encoder(BP.PORT_C)))
     except IOError as error:
          print(error)  

def driveSpeed(cmps = None): #drives straight at given speed in cm/s
    if cmps == None:
        cmps = FORWARD_DRIVE_SPEED
    dps = (cmps*180)/((WHEEL_DIAMETER/2)*3.14)
    BP.set_motor_dps(RIGHT_MOTOR+LEFT_MOTOR, dps)
    
def driveDistance(target_distance, cmps = None): #drives a given distance (cm) at speed (cm/s)
     if cmps == None:
          cmps = FORWARD_DRIVE_SPEED
     dps = (cmps*180)/((WHEEL_DIAMETER/2)*3.14)
     print("Traveling", target_distance, "cm")
     BP.set_motor_dps(RIGHT_MOTOR+LEFT_MOTOR, dps)
     distance_traveled = 0
     encoder_start = BP.get_motor_encoder(RIGHT_MOTOR)
     while(distance_traveled < target_distance):
          encoder_dif = BP.get_motor_encoder(RIGHT_MOTOR) - encoder_start
          distance_traveled = abs(3.14*WHEEL_DIAMETER*(float(encoder_dif)/360))
          logAll()
          cargoBrake()
     BP.set_motor_dps(RIGHT_MOTOR+LEFT_MOTOR, 0)
     print("Traveled", distance_traveled, "cm")

def turnLeft(degrees):
    
    encoder_start = BP.get_motor_encoder(RIGHT_MOTOR)
    encoder_dif = BP.get_motor_encoder(RIGHT_MOTOR) - encoder_start

    target_arc_length = (DISTANCE_BETWEEN_TIRES/2)*(degrees*3.14)/180
    arc_length_traveled = abs(3.14*WHEEL_DIAMETER*(encoder_dif/360))
    
    print("Target arc length:", target_arc_length)
    
    while(arc_length_traveled < target_arc_length):
        BP.set_motor_dps(RIGHT_MOTOR, TURN_SPEED)
        BP.set_motor_dps(LEFT_MOTOR, -1*TURN_SPEED)
        
        encoder_dif = BP.get_motor_encoder(RIGHT_MOTOR) - encoder_start
        arc_length_traveled = abs(3.14*WHEEL_DIAMETER*(encoder_dif/360))

    print("Turn finished.")
    print("Arc length traveled:", arc_length_traveled)
    BP.set_motor_power(LEFT_MOTOR + RIGHT_MOTOR, 0)
    
def turnRight(degrees):
    
    encoder_start = BP.get_motor_encoder(LEFT_MOTOR)
    encoder_dif = BP.get_motor_encoder(LEFT_MOTOR) - encoder_start

    target_arc_length = (DISTANCE_BETWEEN_TIRES/2)*(degrees*3.14)/180
    arc_length_traveled = abs(3.14*WHEEL_DIAMETER*(encoder_dif/360))
    
    print("Target arc length:", target_arc_length)
    
    while(arc_length_traveled < target_arc_length):
        BP.set_motor_dps(LEFT_MOTOR, TURN_SPEED)
        BP.set_motor_dps(RIGHT_MOTOR, -1*TURN_SPEED)
        
        encoder_dif = BP.get_motor_encoder(LEFT_MOTOR) - encoder_start
        arc_length_traveled = abs(3.14*WHEEL_DIAMETER*(encoder_dif/360))

    print("Turn finished.")
    print("Arc length traveled:", arc_length_traveled)
    BP.set_motor_power(LEFT_MOTOR + RIGHT_MOTOR, 0)

def pathFind():
    while True:
        ultra = grovepi.ultrasonicRead(ultrasonic_sensor_port)
        if (ultra > STOP_DISTANCE):
            driveSpeed()
            state = 0
        else:
            stop()
            time.sleep(1)
            if (state == 0 and ultra <= STOP_DISTANCE):
                print("Checking Right")
                turnRight(90)
                state = 1
            elif (state == 1 and ultra <= STOP_DISTANCE):
                print("Checking Left from Right")
                turnLeft(180)
                state = 2
            elif (state == 2 and ultra <= STOP_DISTANCE):
                print("Turning around")
                turnRight(90)
                driveDistance(-10)
                turnRight(180)
                state = 0

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

#stop functions
        
def stop():
    BP.set_motor_dps(BP.PORT_A, 0)
    BP.set_motor_dps(BP.PORT_B, 0)
    BP.set_motor_dps(BP.PORT_C, 0)
    BP.set_motor_dps(BP.PORT_D, 0)

stop()
resetMotorEncoders()

