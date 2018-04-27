# Activity Project 3.
# File: SLAM.py
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
# Library that holds functions related to navigation and mapping

import sys
import driveLibrary
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

# Character keys for dispMap()
CLEAR_CHAR = 'X'
WALL_CHAR = ' '

# Robot starting point and orientations
start_x = 7
start_y = 0
currentX = start_x
currentY = start_y
currentDir = "N"
scanDir = "N"
scanPos = "F"

# Point lists
unexploredPts = [[start_x, start_y + 1]]
exploredPts = [[start_x, start_y]]

# Resource information

# map keys for resources and paths
OPEN_KEY = 1
WALL_KEY = 0
ORIGIN_KEY = 10
BIO_KEY = 2
NH_KEY = 3
RAD_KEY = 4
MRI_KEY = 5
OS_KEY = 6
EXT_KEY = 7

# compile full list
resourceKeys = [
            OPEN_KEY,
            ORIGIN_KEY,
            BIO_KEY,
            NH_KEY,
            RAD_KEY,
            MRI_KEY,
            OS_KEY,
            EXT_KEY
            ]

pathMatrix = [[OPEN_KEY]] # Matrix that stores availble paths for mvmt
origin_coords = [[start_x, start_y]]
mri_coords = []
bio_coords = []
nh_coords = []
rad_coords =[]
ext_coords = []
os_coords = []
resourceList = []
mapList = []
unknownObjs = []
resourceDetails = []

# Map overall dimentions 
map_max_x = 10
map_max_y = 10

def findPath(start, end): # Function that queries the pathfinding library for path
    global pathMatrix

    grid = Grid(matrix = pathMatrix)

    start = grid.node(start[0],start[1])
    end = grid.node(end[0],end[1])

    finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
    path, runs = finder.find_path(start, end, grid)

    print('operations:', runs, 'path length:', len(path))   
    print(grid.grid_str(path=path, start=start, end=end))
    print(path)
    
    return path

def pathToClosestPt(): # determine path to closest point
    global currentX
    global currentY
    global unexploredPts
    min_length = 100 # dummy starting value
    path = [] # empty list to store path
    
    for pt in unexploredPts: # calculate distance to each unexplored point
        length = len(findPath([currentX, currentY], pt))
        if length > 1 and length < min_length:
            # set optimal path to closest point
            path = findPath([currentX, currentY], pt)
            
    return path

def drivePath(path): # drive to all the points in given path
    for pt in path:
        goTo(pt)


def goTo(pt): # Drive to specified point
    global exploredPts
    global unexplredPts
    
    if pt[0] - currentX > 0:
        turnTowards("E")
    elif pt[0] - currentX < 0:
        turnTowards("W")
    elif pt[1] - currentY > 0:
        turnTowards("N")
    elif pt[1] - currentY < 0:
        turnTowards("S")
    if pt[0] == currentX and pt[1] == currentY:
        return
    
    if(pt in unexploredPts):
        print("Not correcting")
            #driveLibrary.driveDistance()
        moveForward()
    else:
        print("Correcting")
        #driveLibrary.gridForward
        moveForward()

    

def makeResourceList(): # compile list of resources
    global resourceList
    
    resourceList = [
            exploredPts,
            origin_coords,
            bio_coords,
            nh_coords,
            rad_coords,
            mri_coords,
            os_coords,
            ext_coords
            ]
    
    for category in resourceList:
        for item in category:
            if exploredPts.count(item) == 0:
                exploredPts.append(item)
    return

def advance(): # Advance a grid point
    moveForward()
    scanSurroundings()

def turnTowards(direction): # Turn the LARIS in given direction
    print("Turning ", direction)
    current = dirToNum(currentDir)
    target = dirToNum(direction)
    if(target - current == 1):
        turnRight()
    elif(target- current == 2):
        turnRight()
        turnRight()
    elif(target- current == 3):
        turnLeft()
    elif(target - current == -1):
        turnLeft()
    elif(target - current == -2):
        turnLeft()
        turnLeft()
    elif(target - current == -3):
        turnRight()
        
def flipMatrix(matrix): # reverse y values of a matrix
    newMatrix = []
    for i in range(len(matrix) -1, -1, -1):
        newMatrix.append(matrix[i])
    return newMatrix

def dispMap(): # print basic map without resources, useful for debug
    global pathMatrix
    
    for row in pathMatrix:
#        sys.stdout.write('|') # Vertical lines in grid
        for item in row:
            if item == WALL_KEY:
                sys.stdout.write(WALL_CHAR)
            elif item == OPEN_KEY:
                sys.stdout.write(CLEAR_CHAR)
            else:
                sys.stdout.write("ERROR, INVALID CHARACTER IN pathMatrix!")
#            sys.stdout.write('|') # Vertical lines in grid
#        print() # Newline for horizontal lines
#        for item in row:
#            sys.stdout.write('--') # Horizontal lines
        print() # Newline for next row of map

def completeMap(): # compile map
    global resourceList
    file_header = "Team: 13\nMap: 4\nUnit Length: 40\nUnit: cm\nOrigin: (" + str(start_x) + " , " + str(start_y) + ")\n"
    
    # compile resource list
    makeResourceList()
    
    cat_counter = 0 # counter for categories
    for category in resourceList:
        for pt in category:
            try:
                mapList[pt[1]][pt[0]] = resourceKeys[cat_counter] # put category at correct pt
            except:
                pass
        cat_counter += 1 # increase cat counter
    
    # write to file
    fid = open('team13_map.csv', 'w')
    fid.write(file_header)
    for i in range(len(mapList) - 1, -1, -1):
        fid.write(str(mapList[i]))
        fid.write("\n")
        print(mapList[i])
    fid.close()

def resourceFile(): # write resource information to resource file
    global resourceDetails
    file_header = "Team: 13\nMap: 0\nNotes: Final Demo Resource Information\n"
    resources_header = "Resource Type, Parameter of Interest, Parameter, Resource X Coordinate, Resource Y Coordinate\n\n"
    fid = open('team13_resources.csv','w')
    fid.write(file_header)
    fid.write(resources_header)
    for category in resourceDetails:
        for item in category:
            fid.write(str(item))
            fid.write(", ")
        fid.write("\n")
    fid.close()

def addWalls(direction):
    
    FILL_NUM = WALL_KEY # Number to fill lists with
    
    if direction == "N": # North
        tempList = [] # Create list of filler numbers
        for item in pathMatrix[0]: # number of columns
            tempList.append(FILL_NUM)
        pathMatrix.append(tempList) # Set as top row
        
    elif direction == "S": # South
        tempList = [] # Create list of filler numbers
        for item in pathMatrix[0]: # number of columns
            tempList.append(FILL_NUM)
        pathMatrix.append(tempList) # Set as bottom row    
    
    elif direction == "E": # East
        for row in pathMatrix: 
            row.append(FILL_NUM) # Add filler at end of every row
    
    elif direction == "W": # West
        for row in pathMatrix:
            row.insert(0,FILL_NUM) # Add filler at start of every row 

def emptyMap(x,y): # Create an empty map 
    global pathMatrix
    global mapList
    
    FILL_NUM = WALL_KEY

    pathMatrix = [[FILL_NUM] * x for i in range(y)]
    pathMatrix[start_y][start_x] = 1
    mapList = [[FILL_NUM] * x for i in range(y)]
    
    completeMap()

def checkEdges(): # check if LARIS has reached edge of map
    global currentX
    global currentY
    if currentX == 0:
        print("On west edge")
        addWalls("W")
        currentX = 1
    if currentX == len(pathMatrix[0]) - 1:
        print("On east edge")
        addWalls("E")
    if currentY == 0:
        print("On South edge")
        addWalls("S")
        currentY = 1
    if currentY == len(pathMatrix) - 1:
        print("On North edge")
        addWalls("N")
    
def moveForward(): # move SLAM position forward one point
    global currentX
    global currentY
    global currentDir
    global pathMatrix
    global exploredPts
    
    if currentDir == "N":
        currentY += 1
    elif currentDir == "E":
        currentX += 1
    elif currentDir == "S":
        currentY -= 1
    elif currentDir == "W":
        currentX -= 1

    # Update pathMatrix
    pathMatrix[currentY][currentX] = OPEN_KEY
    
    # Update explored pts
    exploredPts.append([currentX, currentY])
    
    # call driveLibrary
    driveLibrary.driveDistance()
    
    print("Moved to:", currentX, currentY)

def updateScanDir(): # update scanner direction
    global currentDir
    global scanDir
    global scanPos
    
    scanDir = numToDir(dirToNum(currentDir) + dirToNum(scanPos))
    
    return scanDir
    
def turnRight(): # turn SLAM orientation to right
    global currentDir
    global scanDir

    driveLibrary.turnRight()
    
    currentDir = numToDir(dirToNum(currentDir) + 1)
    scanDir = currentDir
    print("Current Direction is:", currentDir)
    
def turnLeft(): # Turn SLAM orientation to left
    global currentDir
    global scanDir
    
    driveLibrary.turnLeft()
    
    currentDir = numToDir(dirToNum(currentDir) - 1)
    scanDir = currentDir
    print("Current Direction is:", currentDir)
    
def scanSurroundings(): # Scan surrounding and add data to lists
    global scanDir
    global scanPos
    global unexploredPts
    
    updateScanDir()
    
    print("Current position: ", currentX, currentY)
    
    for i in ["F", "R", "L", "F"]:
        driveLibrary.rotateScanner(i)
        scanPos = i
        scanDir = updateScanDir()
        print("Scanning: ", scanDir)
        
        if scanDir == "N":
            check_x = currentX
            check_y = currentY + 1
                
        elif scanDir == "E":
            check_x = currentX + 1
            check_y = currentY
            
        elif scanDir == "S":
            check_x = currentX
            check_y = currentY - 1
                
        elif scanDir == "W":
            check_x = currentX - 1
            check_y = currentY

        clear_var = driveLibrary.isClear()
        
        if clear_var == 1: # if clear
            pathMatrix[check_y][check_x] = OPEN_KEY
            unexploredPts.append([check_x, check_y])
            
        elif clear_var == 2: # if wall 
            pathMatrix[check_y][check_x] = WALL_KEY
            try:
                unexploredPts.remove([check_x, check_y])
            except:
                pass

        elif clear_var == 3: # if object
            pathMatrix[check_y][check_x] = OPEN_KEY
            unexploredPts.append([check_x, check_y])
            unknownObjs.append([check_x, check_y])
        
        # check for duplicates
        unexploredPts = removeDuplicates(unexploredPts)
    
    # compile map and output
    completeMap()
        
def removeDuplicates(starting_list): # remove duplicates from a list
    final_list = []
    for i in starting_list:
        if i not in final_list:
            final_list.append(i)
    return final_list

def dirToNum(direction): # convert direction to number
    
    if direction == "N" or direction == "F":
        return 0
    elif direction == "E" or direction == "R":
        return 1
    elif direction == "S" or direction == "B":
        return 2
    elif direction == "W" or direction == "L":
        return 3

def numToDirScanner(number): # convert number to scanner direction
    while number < 0:
        number += 4
        
    number %= 4 
    
    if number == 0:
        return "F"
    elif number == 1:
        return "R"
    elif number == 2:
        return "B"
    elif number == 3:
        return "L"
    
def numToDir(number): # convert num to cardinal direction
    while number < 0:
        number += 4
        
    number %= 4
    
    if number == 0:
        return "N"
    elif number == 1:
        return "E"
    elif number == 2:
        return "S"
    elif number == 3:
        return "W"

