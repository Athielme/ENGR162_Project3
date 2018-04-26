#TEAM 13 LAB 2

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import time     # import the time library for the sleep function
import grovepi
import brickpi3 # import the BrickPi3 drivers
import SLAM
import math
from MPU9250 import MPU9250
import IR_Functions

from IMUFilters import AvgCali
from IMUFilters import genWindow
from IMUFilters import WindowFilterDyn
from IMUFilters import KalmanFilter

from IMUFilters import FindSTD
from IMUFilters import InvGaussFilter


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

GRID_DIST = 40 #cm
FORWARD_DRIVE_SPEED = 40 #cm per second
TURN_CMPS = -10 #cm per second
STOP_DISTANCE = 15 #cm 15

###########PHYSICAL DIMENTIONS################

WHEEL_DIAMETER = 5.48 #cm
DISTANCE_BETWEEN_TIRES = 16.1 #cm
TURN_SPEED = float((TURN_CMPS*180)/((WHEEL_DIAMETER/2)*3.14))


##############BEACON SETUP####################

SCAN_F_ENCODER = 0
SCAN_R_ENCODER = 90
SCAN_L_ENCODER = -90
SCAN_MOVE_SPEED = 200 # dps
SCAN_TOLERANCE = 1


################SCANNING VARS#################
WALL_DISTANCE = 39
OBJ_DISTANCE = 39

BP.set_sensor_type(mag_sensor_port, BP.SENSOR_TYPE.CUSTOM, [(BP.SENSOR_CUSTOM.PIN1_ADC)]) # Configure for an analog on sensor port pin 1, and poll the analog line on pin 1.
BP.set_sensor_type(BUTTON, BP.SENSOR_TYPE.NXT_TOUCH)
#BP.set_sensor_type(mag_sensor_port, BP.SENSOR_TYPE.NXT_LIGHT_ON)
BP.set_sensor_type(LIGHT, BP.SENSOR_TYPE.NXT_LIGHT_ON)
IR_TOLERANCE = 1

#############IMU FILTERING####################

mpu9250 = MPU9250()

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

#while(1 == 1):
    #print(BP.get_sensor(mag_sensor_port))

def wallFollow():
    time_step = .01
    C = 20
    BASE = 100
    while(grovepi.ultrasonicRead(ultrasonic_sensor_port) > 0):
        ultra = grovepi.ultrasonicRead(ultrasonic_sensor_port)
        error = (ultra - 9)
        print("Ultra:", ultra, "Error", error)
        if(error == 0):
            BP.set_motor_dps(RIGHT_MOTOR + LEFT_MOTOR, BASE)
        if(error > 0):
            BP.set_motor_dps(RIGHT_MOTOR, BASE) 
            BP.set_motor_dps(LEFT_MOTOR, BASE + error*C)
        elif(error < 0):
            BP.set_motor_dps(LEFT_MOTOR, BASE) 
            BP.set_motor_dps(RIGHT_MOTOR, BASE + error*C)


def calibrateSensors():
    filename = input("Input file name:")
    fid = open(filename, 'w')
    header = "Time, Dist, Mag, , , Mag magnitude, IR 0, IR 1, Ultra\n"
    fid.write(header)
    encoder_start = BP.get_motor_encoder(RIGHT_MOTOR)
    BP.set_motor_dps(RIGHT_MOTOR + LEFT_MOTOR, 75)
    encoder_dif = 0
    dist = abs(3.14*WHEEL_DIAMETER*(float(encoder_dif)/360))
    t = 0
    time_step = .1
    while(dist < 40):
        time.sleep(time_step)
        t += time_step
        mag = mpu9250.readMagnet()
        mag_magnitude = math.sqrt(mag[0]**2 + mag[1]**2 + mag[2]**2)
        ir = IR_Functions.IR_Read(grovepi)
        encoder_dif = BP.get_motor_encoder(RIGHT_MOTOR) - encoder_start
        ultra = grovepi.ultrasonicRead(ultrasonic_sensor_port)
        dist = abs(3.14*WHEEL_DIAMETER*(float(encoder_dif)/360))
        output = str(t) + ',' + str(dist) + ',' + str(mag[0]) + ',' + str(mag[1]) + ',' + str(mag[2]) + ',' + str(mag_magnitude) + ',' +  str(ir[0]) + ',' +  str(ir[1]) + ',' +  str(ultra)
        fid.write(output)
        fid.write("\n")
    fid.close()
    BP.set_motor_dps(RIGHT_MOTOR + LEFT_MOTOR, 0)
    end()

def gridForward():
    rotateScanner("L")
    left_dist = grovepi.ultrasonicRead(ultrasonic_sensor_port) -7
    rotateScanner("R")
    right_dist = grovepi.ultrasonicRead(ultrasonic_sensor_port) - 2
    rotateScanner("F")
    grid_dist = GRID_DIST

    
    diff = abs(right_dist-left_dist)
    angle = math.degrees(math.atan(diff/grid_dist))
    hypot = math.hypot(grid_dist, diff)
    
    print("Right distance:", right_dist)
    print("Left distance:", left_dist)
    print("Correction:", diff)
    
    if right_dist < left_dist:
        print("Turning", angle, "degrees left")
        turnLeft(degrees = angle)
    
    elif left_dist < right_dist:
        print("Turning", angle, "degrees right")
        turnRight(degrees = angle)
    
    else:
        print("No correction needed")
    
    driveDistance(target_distance = hypot)

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
    
    if ultra <= WALL_DISTANCE:
        print("Wall detected!")
        return 2
    
    elif ultra > WALL_DISTANCE and ultra <= OBJ_DISTANCE:
        print("Object detected")
        return 3
    
    elif ultra > OBJ_DISTANCE:
        print("No wall detected")
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

def inspectCargo():
    arm_encoder_a = BP.get_motor_encoder(ARM_MOTOR)
    power = 7
    BP.set_motor_power(ARM_MOTOR, power)
    time.sleep(.1)
    while(abs(BP.get_motor_encoder(ARM_MOTOR) - arm_encoder_a) > 1 or power < 60):
        power += 1
        BP.set_motor_power(ARM_MOTOR, power)
        time.sleep(.1)
        arm_encoder_a = BP.get_motor_encoder(ARM_MOTOR)
    BP.set_motor_power(ARM_MOTOR, 0)
    print("Power level:", power)
    print("scanning cargo")
    if(BP.get_sensor(LIGHT) > 2080):
        print("Blue - Nonhazardous")
    else:
        print("Yellow")
    print(BP.get_sensor(LIGHT))
    
def gridCargo():
    ultra = 40
    target = 30
    target_dist = -15
    BP.set_motor_dps(RIGHT_MOTOR + LEFT_MOTOR, 150)
    while abs(ultra - target) > 2:
        ultra = grovepi.ultrasonicRead(ultrasonic_sensor_port)
        ir = IR_Functions.IR_Read(grovepi)
        mag = mpu9250.readMagnet()
        if(ir > 280):
            print("IR BEACON FOUND")
            SLAM.resourceDetails.append(["Cesium-137", "Radiation Strength(W)", ir, currentX, currentY])
            ultra = target
            BP.set_motor_dps(RIGHT_MOTOR + LEFT_MOTOR, 0)
            return
        elif(mag > 210):
            print("MRI FOUND")
            SLAM.resourceDetails. append(["MRI", "Field Strength(uT)", mag, currentX, currentY])            
            ultra = target
            BP.set_motor_dps(RIGHT_MOTOR + LEFT_MOTOR, 0)
            return
        print(ultra - target)
    BP.set_motor_dps(RIGHT_MOTOR + LEFT_MOTOR, 0)
    turnRight(degrees = 180)
    driveDistance(target_distance = target_dist)
    inspectCargo()

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

