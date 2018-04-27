from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import time     # import the time library for the sleep function
import grovepi # import grovepi libaray
import brickpi3 # import the BrickPi3 drivers
import SLAM # import naviagtion library
import math
from MPU9250 import MPU9250 # library to use IMU
import IR_Functions # library for IR functions

# IMU filtering libraries
from IMUFilters import AvgCali
from IMUFilters import genWindow
from IMUFilters import WindowFilterDyn
from IMUFilters import KalmanFilter
from IMUFilters import FindSTD
from IMUFilters import InvGaussFilter


BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

IR_Functions.IR_setup(grovepi) # initialize grovepi

#########SENSOR PORTS###########################
ultrasonic_sensor_port = 2
mag_sensor_port = BP.PORT_4
BUTTON = BP.PORT_1
LIGHT = BP.PORT_3
RIGHT_MOTOR = BP.PORT_D
LEFT_MOTOR = BP.PORT_A
ARM_MOTOR = BP.PORT_B
BEACON_MOTOR = BP.PORT_C

################DRIVING#######################

GRID_DIST = 40 #cm, distance between centers of adjacent grid points
FORWARD_DRIVE_SPEED = 40 #cm per second, speed to drive forward
TURN_CMPS = -10 #cm per second, speed to turn
STOP_DISTANCE = 15 #cm 15, distance to stop for wallstop code

###########PHYSICAL DIMENTIONS################

WHEEL_DIAMETER = 5.48 #cm, diameter of drive wheels
DISTANCE_BETWEEN_TIRES = 16.1 #cm, distance between drive wheels
TURN_SPEED = float((TURN_CMPS*180)/((WHEEL_DIAMETER/2)*3.14)) # convert cmps to dps

##############BEACON SETUP####################

SCAN_F_ENCODER = 0 # encoder position for scanning front
SCAN_R_ENCODER = 90 # right position 
SCAN_L_ENCODER = -90 # left position
SCAN_MOVE_SPEED = 200 # dps, speed to move scanner
SCAN_TOLERANCE = 1 # degrees, tolerance for scanner movements

################SCANNING VARS#################

WALL_DISTANCE = 39 # Ultrasonic reading to determine something is a wall
OBJ_DISTANCE = 39 # Ultrasonic reading to determine something is a object

BP.set_sensor_type(mag_sensor_port, BP.SENSOR_TYPE.CUSTOM, [(BP.SENSOR_CUSTOM.PIN1_ADC)]) # Configure for an analog on sensor port pin 1, and poll the analog line on pin 1.
BP.set_sensor_type(BUTTON, BP.SENSOR_TYPE.NXT_TOUCH)
#BP.set_sensor_type(mag_sensor_port, BP.SENSOR_TYPE.NXT_LIGHT_ON)
BP.set_sensor_type(LIGHT, BP.SENSOR_TYPE.NXT_LIGHT_ON)
IR_TOLERANCE = 1

#############IMU FILTERING####################

mpu9250 = MPU9250() #initalize IMU

#Parameters
width=2
depth=100
dly=0.01
adv = True
#/////////

flter=[[0.7,1.0],[0.7,1.0],[0.7,1.0],[0.7,1.0],[0.7,1.0],[0.7,1.0]]# [r,q]Will need to play with each filter value
biases=AvgCali(mpu9250,depth,dly)
state=[[0.0,0.0,0.0,0.0,0.0,0.0],[0,0,0,0,0,0]]#Estimated error (p) and measurement state (x) 
out=[0,0,0,0,0,0]
std=FindSTD(biases,mpu9250,dly)
pick = 1 #1 uses window filter, anything else uses Kalman
count = 3 #Number of standard deviations used for filtering

#############################################

# Reads the right wall and uses proportional control to adjust angle of drive
def wallFollow():
    C = 20 # Proportional constant
    BASE = 100 # dps, base value
    while(grovepi.ultrasonicRead(ultrasonic_sensor_port) > 0): # zero to stop
        ultra = grovepi.ultrasonicRead(ultrasonic_sensor_port) # read ultrasonic ranger
        error = (ultra - 9) # calculate error
        print("Ultra:", ultra, "Error", error)
        if(error == 0):
            BP.set_motor_dps(RIGHT_MOTOR + LEFT_MOTOR, BASE)
        if(error > 0):
            BP.set_motor_dps(RIGHT_MOTOR, BASE) 
            BP.set_motor_dps(LEFT_MOTOR, BASE + error*C)
        elif(error < 0):
            BP.set_motor_dps(LEFT_MOTOR, BASE) 
            BP.set_motor_dps(RIGHT_MOTOR, BASE + error*C)

# Function used to generate object profiles
def calibrateSensors():
    # open file and write header
    filename = input("Input file name:")
    fid = open(filename, 'w')
    header = "Time, Dist, Mag, , , Mag magnitude, IR 0, IR 1, Ultra\n"
    fid.write(header)
    
    # start encoder for movement
    encoder_start = BP.get_motor_encoder(RIGHT_MOTOR)
    BP.set_motor_dps(RIGHT_MOTOR + LEFT_MOTOR, 75)
    encoder_dif = 0
    dist = abs(3.14*WHEEL_DIAMETER*(float(encoder_dif)/360))
    
    # time setup for recording
    t = 0
    time_step = .1
    
    while(dist < 40): # drive 40 cm
        # update time    
        time.sleep(time_step)
        t += time_step
        
        # Read sensors
        mag = mpu9250.readMagnet()
        mag_magnitude = math.sqrt(mag[0]**2 + mag[1]**2 + mag[2]**2)
        ir = IR_Functions.IR_Read(grovepi)
        encoder_dif = BP.get_motor_encoder(RIGHT_MOTOR) - encoder_start
        ultra = grovepi.ultrasonicRead(ultrasonic_sensor_port)
        dist = abs(3.14*WHEEL_DIAMETER*(float(encoder_dif)/360))
        
        # output to file
        output = str(t) + ',' + str(dist) + ',' + str(mag[0]) + ',' + str(mag[1]) + ',' + str(mag[2]) + ',' + str(mag_magnitude) + ',' +  str(ir[0]) + ',' +  str(ir[1]) + ',' +  str(ultra)
        fid.write(output)
        fid.write("\n")
    
    # close file and stop moving    
    fid.close()
    BP.set_motor_dps(RIGHT_MOTOR + LEFT_MOTOR, 0)
    end()

# move forward a grid point, correcting for errors
def gridForward():
    # Scan surroundings, adjust for physical ultrasonic asymetry
    rotateScanner("L")
    left_dist = grovepi.ultrasonicRead(ultrasonic_sensor_port) -7
    rotateScanner("R")
    right_dist = grovepi.ultrasonicRead(ultrasonic_sensor_port) - 2
    rotateScanner("F")
    grid_dist = GRID_DIST

    # Calculate required movement
    diff = abs(right_dist-left_dist)
    angle = math.degrees(math.atan(diff/grid_dist))
    hypot = math.hypot(grid_dist, diff)
    
    print("Right distance:", right_dist)
    print("Left distance:", left_dist)
    print("Correction:", diff)
    
    # Move to correct angle
    if right_dist < left_dist:
        print("Turning", angle, "degrees left")
        turnLeft(degrees = angle)
    
    elif left_dist < right_dist:
        print("Turning", angle, "degrees right")
        turnRight(degrees = angle)
    
    else:
        print("No correction needed")
    
    # drive forward
    driveDistance(target_distance = hypot)

# funciton used to determine offesets for utrasonic readings
def calibrateUltra():
    theoretical_dist = 20.29
    rotateScanner("R")
    right_reading = grovepi.ultrasonicRead(ultrasonic_sensor_port)
    rotateScanner("L")
    left_reading = grovepi.ultrasonicRead(ultrasonic_sensor_port)
    rotateScanner("F")
    
    left_correction = theoretical_dist - left_reading
    right_correction = theoretical_dist - right_reading

    print("Left correction:", left_correction)
    print("Right correciton:", right_correction)
    
# Scans and determines if surroundings are clear
def isClear():
    try:
        ultra = grovepi.ultrasonicRead(ultrasonic_sensor_port)
        print(ultra)

    except IOError:
        print("Error reading sensors in isClear()")
        return 0
    
    if ultra <= WALL_DISTANCE:
        print("Wall detected!")
        return 2
    
    elif ultra > WALL_DISTANCE and ultra <= OBJ_DISTANCE:
        print("Object detected")
        return 3
    
    elif ultra > OBJ_DISTANCE:
        print("No wall detected")
        return 1

# function to rotate scanner to specified direction
def rotateScanner(direction):
    # stop motors
    end()
    
    # validate input
    if type(direction) is str:
        direction = SLAM.dirToNum(direction)
    
    # Move scanner to face front
    if direction == 0:
        encoder_dif = BP.get_motor_encoder(BEACON_MOTOR) - SCAN_F_ENCODER
        print("Rotating scanner to face front")
        while(abs(BP.get_motor_encoder(BEACON_MOTOR)) > SCAN_TOLERANCE):
            if encoder_dif > 0:
                BP.set_motor_dps(BEACON_MOTOR, -SCAN_MOVE_SPEED)
            elif encoder_dif < 0:
                BP.set_motor_dps(BEACON_MOTOR, SCAN_MOVE_SPEED)
                
            encoder_dif = BP.get_motor_encoder(BEACON_MOTOR)
    
    # Move scanner to face right
    elif direction == 1:
        print("Rotating scanner to face right")
        encoder_dif = BP.get_motor_encoder(BEACON_MOTOR) - SCAN_R_ENCODER
        
        while(abs(encoder_dif) > SCAN_TOLERANCE):
            BP.set_motor_dps(BEACON_MOTOR, SCAN_MOVE_SPEED)
            encoder_dif = BP.get_motor_encoder(BEACON_MOTOR) - SCAN_R_ENCODER
    
    # Print error if trying to scan behind
    elif direction == 2:
        print("ERROR. CANNOT SCAN BEHIND ROBOT")
        
    # Move scanner to face left
    elif direction == 3:
        print("Rotating scanner to face left")
        encoder_dif = BP.get_motor_encoder(BEACON_MOTOR) - SCAN_L_ENCODER
        
        while(abs(encoder_dif) > SCAN_TOLERANCE):
            BP.set_motor_dps(BEACON_MOTOR, -SCAN_MOVE_SPEED)
            encoder_dif = BP.get_motor_encoder(BEACON_MOTOR) - SCAN_L_ENCODER
    
    # Update SLAM scanner status
    SLAM.scanPos = SLAM.numToDirScanner(direction)
    SLAM.updateScanDir()
    
    # stop moving
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
          
     dps = (cmps*180)/((WHEEL_DIAMETER/2)*3.14) # convert speed to dps
     
     print("Traveling", target_distance, "cm")
    
    # determine direction to drive
     if target_distance > 0:     
         BP.set_motor_dps(RIGHT_MOTOR+LEFT_MOTOR, dps)
     elif target_distance < 0:
         BP.set_motor_dps(RIGHT_MOTOR+LEFT_MOTOR, -dps)
     
     # drive until robot has reached target distance
     distance_traveled = 0
     encoder_start = BP.get_motor_encoder(RIGHT_MOTOR)
     while(distance_traveled < abs(target_distance)):
          encoder_dif = BP.get_motor_encoder(RIGHT_MOTOR) - encoder_start
          distance_traveled = abs(3.14*WHEEL_DIAMETER*(float(encoder_dif)/360))
     
     # stop moving
     BP.set_motor_dps(RIGHT_MOTOR+LEFT_MOTOR, 0)
     print("Traveled", distance_traveled, "cm")
     
# Turn right, defaults to 90 degrees
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

# Turn left, defaults to 90 degrees 
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

# lift cargo to determine mass and measure color
def inspectCargo():
    # setup movement
    arm_encoder_a = BP.get_motor_encoder(ARM_MOTOR)
    power = 7
    BP.set_motor_power(ARM_MOTOR, power)
    time.sleep(.1)
    
    # Increase power until object stops moving, minimum power level 60 to raise object
    while(abs(BP.get_motor_encoder(ARM_MOTOR) - arm_encoder_a) > 1 or power < 60):
        power += 1
        BP.set_motor_power(ARM_MOTOR, power)
        time.sleep(.1)
        arm_encoder_a = BP.get_motor_encoder(ARM_MOTOR)
    
    # Stop and output data
    BP.set_motor_power(ARM_MOTOR, 0)
    print("Power level:", power)
    print("scanning cargo")
    if(BP.get_sensor(LIGHT) > 2080):
        print("Blue - Nonhazardous")
    else:
        print("Yellow - Hazardous")
    print(BP.get_sensor(LIGHT))

# Procdedure for when cargo is in the grid point in front of LARIS    
def gridCargo():
    # initialize variables
    ultra = 40 # initial dummy utlrasonic reading
    target = 30 # target ultrasonic reading
    target_dist = -15 # distance to backtrack when target distance is reached
    
    # start moving ultil ultra reaches target
    BP.set_motor_dps(RIGHT_MOTOR + LEFT_MOTOR, 150)
    while abs(ultra - target) > 2:
        # read sensors
        ultra = grovepi.ultrasonicRead(ultrasonic_sensor_port)
        ir = IR_Functions.IR_Read(grovepi)
        mag = mpu9250.readMagnet()
        
        if(ir > 280):  # stop if beacon found
            print("IR BEACON FOUND")
            SLAM.resourceDetails.append(["Cesium-137", "Radiation Strength(W)", ir, currentX, currentY])
            ultra = target
            BP.set_motor_dps(RIGHT_MOTOR + LEFT_MOTOR, 0)
            return

        elif(mag > 210): # Stop if MRI found
            print("MRI FOUND")
            SLAM.resourceDetails. append(["MRI", "Field Strength(uT)", mag, currentX, currentY])            
            ultra = target
            BP.set_motor_dps(RIGHT_MOTOR + LEFT_MOTOR, 0)
            return
        
        print(ultra - target)
    
    # Stop moving, turn around, position for cargo lift, inspect cargo
    BP.set_motor_dps(RIGHT_MOTOR + LEFT_MOTOR, 0)
    turnRight(degrees = 180)
    driveDistance(target_distance = target_dist)
    inspectCargo()

def run(letter, dps): # debug function
    if (letter == "A"): #front right
        BP.set_motor_dps(BP.PORT_A, -1 * dps)
    elif (letter == "B"): #back right
        BP.set_motor_dps(BP.PORT_B, dps)
    elif (letter == "C"): #back left
        BP.set_motor_dps(BP.PORT_C, dps)
    elif (letter == "D"):
        BP.set_motor_dps(BP.PORT_D, -1 * dps)

        
def stop(): # halts all motors
    BP.set_motor_dps(BP.PORT_A, 0)
    BP.set_motor_dps(BP.PORT_B, 0)
    BP.set_motor_dps(BP.PORT_C, 0)
    BP.set_motor_dps(BP.PORT_D, 0)

def end(): # cuts off power to all motors
    BP.set_motor_power(BP.PORT_A, 0)
    BP.set_motor_power(BP.PORT_B, 0)
    BP.set_motor_power(BP.PORT_C, 0)
    BP.set_motor_power(BP.PORT_D, 0)

stop()
resetMotorEncoders()

