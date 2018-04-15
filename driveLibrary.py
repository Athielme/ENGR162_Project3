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
mag_sensor_port = BP.PORT_4
BUTTON = BP.PORT_1
LIGHT = BP.PORT_3
RIGHT_MOTOR = BP.PORT_D
LEFT_MOTOR = BP.PORT_A
ARM_MOTOR = BP.PORT_B
BEACON_MOTOR = BP.PORT_C


################DRIVING#######################

GRID_DIST = 35 #cm
FORWARD_DRIVE_SPEED = 10 #cm per second
TURN_CMPS = -5 #cm per second
STOP_DISTANCE = 15 #cm 15

###########PHYSICAL DIMENTIONS################

WHEEL_DIAMETER = 5.75 #cm
DISTANCE_BETWEEN_TIRES = 16.5 #cm
TURN_SPEED = float((TURN_CMPS*180)/((WHEEL_DIAMETER/2)*3.14))


##############BEACON SETUP####################

SCAN_F_ENCODER = 0
SCAN_R_ENCODER = 90
SCAN_L_ENCODER = -90
SCAN_MOVE_SPEED = 50 # dps
SCAN_TOLERANCE = 1


BP.set_sensor_type(mag_sensor_port, BP.SENSOR_TYPE.CUSTOM, [(BP.SENSOR_CUSTOM.PIN1_ADC)]) # Configure for an analog on sensor port pin 1, and poll the analog line on pin 1.
BP.set_sensor_type(BUTTON, BP.SENSOR_TYPE.NXT_TOUCH)
#BP.set_sensor_type(mag_sensor_port, BP.SENSOR_TYPE.NXT_LIGHT_ON)
BP.set_sensor_type(LIGHT, BP.SENSOR_TYPE.NXT_LIGHT_ON)
IR_TOLERANCE = 1

#while(1 == 1):
    #print(BP.get_sensor(mag_sensor_port))

def waitForButtonPress():
    while(BP.get_sensor(BUTTON) == 0):
        print("Waiting for button press")
    print("Button pressed!")

def isClear():
    try:
        ultra = grovepi.ultrasonicRead(ultrasonic_sensor_port)
        ir = IR_Functions.IR_Read(grovepi)
        print(ultra)
    
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
        while(abs(BP.get_motor_encoder(BEACON_MOTOR)) > SCAN_TOLERANCE):
            if encoder_dif > 0:
                BP.set_motor_dps(BEACON_MOTOR, -SCAN_MOVE_SPEED)
            elif encoder_dif < 0:
                BP.set_motor_dps(BEACON_MOTOR, SCAN_MOVE_SPEED)
                
            encoder_dif = BP.get_motor_encoder(BEACON_MOTOR)
    
    elif direction == 1:
        print("Rotating scanner to face right")
        encoder_dif = BP.get_motor_encoder(BEACON_MOTOR) - SCAN_R_ENCODER
        
        while(abs(encoder_dif) > SCAN_TOLERANCE):
            BP.set_motor_dps(BEACON_MOTOR, SCAN_MOVE_SPEED)
            encoder_dif = BP.get_motor_encoder(BEACON_MOTOR) - SCAN_R_ENCODER
    
    elif direction == 2:
        print("ERROR. CANNOT SCAN BEHIND ROBOT")
        
    elif direction == 3:
        print("Rotating scanner to face left")
        encoder_dif = BP.get_motor_encoder(BEACON_MOTOR) - SCAN_L_ENCODER
        
        while(abs(encoder_dif) > SCAN_TOLERANCE):
            BP.set_motor_dps(BEACON_MOTOR, -SCAN_MOVE_SPEED)
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

    
def driveDistance(target_distance = GRID_DIST, cmps = None): #drives a given distance (cm) at speed (cm/s)
     if cmps == None:
          cmps = FORWARD_DRIVE_SPEED
     dps = (cmps*180)/((WHEEL_DIAMETER/2)*3.14)
     print("Traveling", target_distance, "cm")
     if target_distance > 0:     
         BP.set_motor_dps(RIGHT_MOTOR+LEFT_MOTOR, dps)
     elif target_distance < 0:
         BP.set_motor_dps(RIGHT_MOTOR+LEFT_MOTOR, -dps)
     distance_traveled = 0
     encoder_start = BP.get_motor_encoder(RIGHT_MOTOR)
     while(distance_traveled < abs(target_distance)):
          encoder_dif = BP.get_motor_encoder(RIGHT_MOTOR) - encoder_start
          distance_traveled = abs(3.14*WHEEL_DIAMETER*(float(encoder_dif)/360))
     BP.set_motor_dps(RIGHT_MOTOR+LEFT_MOTOR, 0)
     print("Traveled", distance_traveled, "cm")
     

def turnRight(degrees = 90):
    
    encoder_start = BP.get_motor_encoder(RIGHT_MOTOR)
    encoder_dif = BP.get_motor_encoder(RIGHT_MOTOR) - encoder_start

    target_arc_length = (DISTANCE_BETWEEN_TIRES/2)*(degrees*3.14)/180
    arc_length_traveled = abs(3.14*WHEEL_DIAMETER*(encoder_dif/180))
    
    print("Target arc length:", target_arc_length)
    
    while(arc_length_traveled < target_arc_length):
        BP.set_motor_dps(RIGHT_MOTOR, TURN_SPEED)
        BP.set_motor_dps(LEFT_MOTOR, -1*TURN_SPEED)
        
        encoder_dif = BP.get_motor_encoder(RIGHT_MOTOR) - encoder_start
        arc_length_traveled = abs(3.14*(WHEEL_DIAMETER/2)*(encoder_dif/180))

    print("Turn finished.")
    print("Arc length traveled:", arc_length_traveled)
    BP.set_motor_power(LEFT_MOTOR + RIGHT_MOTOR, 0)
    
def turnLeft(degrees = 90):
    
    encoder_start = BP.get_motor_encoder(LEFT_MOTOR)
    encoder_dif = BP.get_motor_encoder(LEFT_MOTOR) - encoder_start

    target_arc_length = (DISTANCE_BETWEEN_TIRES/2)*(degrees*3.14)/180
    arc_length_traveled = abs(3.14*WHEEL_DIAMETER*(encoder_dif/180))
    
    print("Target arc length:", target_arc_length)
    
    while(arc_length_traveled < target_arc_length):
        BP.set_motor_dps(LEFT_MOTOR, TURN_SPEED)
        BP.set_motor_dps(RIGHT_MOTOR, -1*TURN_SPEED)
        
        encoder_dif = BP.get_motor_encoder(LEFT_MOTOR) - encoder_start
        arc_length_traveled = abs(3.14*(WHEEL_DIAMETER/2)*(encoder_dif/180))

    print("Turn finished.")
    print("Arc length traveled:", arc_length_traveled)
    BP.set_motor_power(LEFT_MOTOR + RIGHT_MOTOR, 0)

def pathFind():
    state = 0
    while True:
        ultra = grovepi.ultrasonicRead(ultrasonic_sensor_port)
        print(ultra)
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
                #driveDistance(targetDistance = -10) #what is targetDistance?
                turnRight(180)
                state = 0

def inspectCargo():
    arm_encoder_a = BP.get_motor_encoder(ARM_MOTOR)
    power = 15
    BP.set_motor_power(ARM_MOTOR, -power)
    time.sleep(.1)
    while(abs(BP.get_motor_encoder(ARM_MOTOR) - arm_encoder_a) > 1):
        power += 10
        BP.set_motor_power(ARM_MOTOR, -power)
        time.sleep(.2)
        arm_encoder_a = BP.get_motor_encoder(ARM_MOTOR)
    BP.set_motor_power(ARM_MOTOR, 0)
    print("Power level:", power)
    print("scanning cargo")
    if(BP.get_sensor(LIGHT) > 2080):
        print("Blue - Nonhazardous")
    else:
        print("Yellow")
    print(BP.get_sensor(LIGHT))
    

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

def task6():
    driveDistance(target_distance = -38.5)
    inspectCargo()


def go():
    driveDistance()
    driveDistance()
    turnRight()
    driveDistance()
    driveDistance()
    driveDistance()
    turnLeft()
    driveDistance()

stop()
resetMotorEncoders()

