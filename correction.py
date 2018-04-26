# Activity HW05
# File: HW05_athielme.py
# Date: 11 February 2018
# By: Aaron Thielmeyer
# athielme
# Section: 1
# Team: 13
#
# ELECTRONIC SIGNATURE
# Aaron Thielmeyer
#
# The electronic signature above indicates that the program
# submitted for evaluation is my individual work. I have
# a general understanding of all aspects of its development
# and execution.
#
# This program calculates the average hardness and strength of different steels
# given a very large data set. 

import numpy
import math

def scanLeft():
    error = numpy.random.randint(5,10)
    return error

def scanRight():
    error = numpy.random.randint(5, 10)
    return error

def turnLeft(degrees = 0):
    return

def turnRight(degrees = 0):
    return

def driveForward(distance = 0):
    return

def gridForward():
    left_dist = scanLeft()
    right_dist = scanRight()
    grid_dist = 20
    
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
    
    driveForward(distance = hypot)
    
def flipMatrix(matrix):
    newMatrix = []
    for row in matrix:
        newMatrix.insert(0, row)
    return newMatrix