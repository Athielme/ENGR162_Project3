#TEAM 13 LAB 2

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import time     # import the time library for the sleep function
import grovepi
import brickpi3 # import the BrickPi3 drivers
import SLAM
import IR_Functions


BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

IR_Functions.IR_setup(grovepi)


ultrasonic_sensor_port = 2
RIGHT_MOTOR = BP.PORT_D
LEFT_MOTOR = BP.PORT_A
BEACON_MOTOR = BP.PORT_C

################DRIVING#######################

GRID_DIST = 10 #cm
FORWARD_DRIVE_SPEED = -10 #cm per second
TURN_CMPS = -5 #cm per second
STOP_DISTANCE = 15 #cm

###########PHYSICAL DIMENTIONS################

WHEEL_DIAMETER = 2.9 #cm
DISTANCE_BETWEEN_TIRES = 12 #cm
TURN_SPEED = float((TURN_CMPS*180)/((WHEEL_DIAMETER/2)*3.14))


##############BEACON SETUP####################

SCAN_F_ENCODER = 0
SCAN_R_ENCODER = -90
SCAN_L_ENCODER = 90
SCAN_MOVE_SPEED = 50 # dps
SCAN_TOLERANCE = 1
IR_TOLERANCE = 10

def isClear():
    try:
        ultra = grovepi.ultrasonicRead(ultrasonic_sensor_port)
        ir = IR_Functions.IR_Read(grovepi)
    
    except IOError:
        print("Error reading sensors in isClear()")
        return 0
    
    if ultra > STOP_DISTANCE and ir[0] < IR_TOLERANCE:
        print("No wall or beacon detected")
        return 1
    
    elif ultra < STOP_DISTANCE and ir[0] < IR_TOLERANCE:
        print("Wall detected")
        return 0
    
    elif ultra < STOP_DISTANCE and ir[0] > IR_TOLERANCE:
        print("Beacon detected")
        return 1

def rotateScanner(direction):
    end()
    
    if type(direction) is str:
        direction = SLAM.dirToNum(direction)
    
    if direction == 0:
        encoder_dif = BP.get_motor_encoder(BEACON_MOTOR) - SCAN_F_ENCODER
        print("Rotating scanner to face front")
        while(abs(encoder_dif) > SCAN_TOLERANCE):
            if encoder_dif < 0:
                BP.set_motor_dps(BEACON_MOTOR, SCAN_MOVE_SPEED)
            elif encoder_dif > 0:
                BP.set_motor_dps(BEACON_MOTOR, SCAN_MOVE_SPEED)
                
            encoder_dif = BP.get_motor_encoder(BEACON_MOTOR) - SCAN_F_ENCODER
    
    elif direction == 1:
        print("Rotating scanner to face right")
        encoder_dif = BP.get_motor_encoder(BEACON_MOTOR) - SCAN_R_ENCODER
        
        while(abs(encoder_dif) > SCAN_TOLERANCE):
            BP.set_motor_dps(BEACON_MOTOR, -SCAN_MOVE_SPEED)
            encoder_dif = BP.get_motor_encoder(BEACON_MOTOR) - SCAN_R_ENCODER
    
    elif direction == 2:
        print("ERROR. CANNOT SCAN BEHIND ROBOT")
        
    elif direction == 3:
        print("Rotating scanner to face left")
        encoder_dif = BP.get_motor_encoder(BEACON_MOTOR) - SCAN_L_ENCODER
        
        while(abs(encoder_dif) > SCAN_TOLERANCE):
            BP.set_motor_dps(BEACON_MOTOR, SCAN_MOVE_SPEED)
            encoder_dif = BP.get_motor_encoder(BEACON_MOTOR) - SCAN_L_ENCODER
    
    SLAM.scanPos = SLAM.numToDirScanner(direction)
    SLAM.updateScanDir()
    
    stop()
        
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

def goToPoint(x,y):
    relativeX = x - SLAM.currentX
    relaticeY = y - SLAM.currentY
    
    for a in range(0, x):
        driveForward()


def turnTo(direction):
    while SLAM.currentDir != direction:
        turnRight()
    
def driveDistance(target_distance = GRID_DIST, cmps = None): #drives a given distance (cm) at speed (cm/s)
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
     BP.set_motor_dps(RIGHT_MOTOR+LEFT_MOTOR, 0)
     print("Traveled", distance_traveled, "cm")
     SLAM.moveForward()
     SLAM.dispMap()

def turnLeft(degrees = 90):
    
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
    SLAM.turnLeft()
    BP.set_motor_power(LEFT_MOTOR + RIGHT_MOTOR, 0)
    
def turnRight(degrees = 360):
    
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
    SLAM.turnRight()
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
                turnRight()
                state = 1
            elif (state == 1 and ultra <= STOP_DISTANCE):
                print("Checking Left from Right")
                turnLeft()
                state = 2
            elif (state == 2 and ultra <= STOP_DISTANCE):
                print("Turning around")
                turnRight()
                driveDistance(targetDistance = -10)
                turnRight(180)
                state = 0

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

def end():
    BP.set_motor_power(BP.PORT_A, 0)
    BP.set_motor_power(BP.PORT_B, 0)
    BP.set_motor_power(BP.PORT_C, 0)
    BP.set_motor_power(BP.PORT_D, 0)


stop()
resetMotorEncoders()

