# Activity Project 3.
# File: main.py
# Date: 27 April 2018
# By: Aaron Thielmeyer
# athielme
# Kat Li
# li2701
# Eveyln Shi
# shi360
# Zubin Kane
# kane44
# Section: 1
# Team: 13
#
# ELECTRONIC SIGNATURE
# Aaron Thielmeyer
# Kat Li
# Evelyn Shi
# Zubin Kane
#
# The electronic signatures above indicate that the program
# submitted for evaluation is the combined effort of all
# team members and that each member of the team was an
# equal participant in its creation. In addition, each
# member of the team has a general understanding of
# all aspects of the program development and execution.
#
# Main file used for final robot demo

import driveLibrary
import SLAM

# Create empty map the size of the demo map area
SLAM.emptyMap(SLAM.map_max_x, SLAM.map_max_y)

# Move forward and perform initial scan
SLAM.moveForward()
SLAM.scanSurroundings()

while(1 == 1): # Run indefinitely
    SLAM.completeMap() # Output map
    SLAM.drivePath(SLAM.pathToClosestPt()) # Drive to closest point
    SLAM.scanSurroundings() # Scan surroundings
