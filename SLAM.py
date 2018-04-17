import sys
import driveLibrary
import time

CLEAR_CHAR = 'X'
WALL_CHAR = ' '

OPEN_KEY = 1
WALL_KEY = 0
ORIGIN_KEY = 10
BIO_KEY = 2
NH_KEY = 3
RAD_KEY = 4
MRI_KEY = 5
OS_KEY = 6
EXT_KEY = 7

resourceKeys = [
            ORIGIN_KEY,
            BIO_KEY,
            NH_KEY,
            RAD_KEY,
            MRI_KEY,
            OS_KEY,
            EXT_KEY
            ]


start_x = 0
start_y = 0
currentX = start_x
currentY = start_y
currentDir = "N"
scanDir = "N"
scanPos = "F"

unexploredPts = [[start_x, start_y + 1]]

pathMatrix = [[OPEN_KEY]] # Matrix that stores availble paths for mvmt
origin_coords = [start_x, start_y]
mri_coords = []
bio_coords = []
nh_coords = []
rad_coords =[]
ext_coords = []
os_coords = []
resourceList = []

def makeResourceList():
    resourceList = [
            origin_coords,
            bio_coords,
            nh_coords,
            rad_coords,
            mri_coords,
            os_coords,
            ext_coords
            ]
    return
def advance():
    moveForward()
    scanSurroundings()

def turnTowards(direction):
    print("Turning ", direction)
    while(currentDir != direction):
        turnRight()

def dispMap():
    checkEdges()
    global pathMatrix
    
    for row in pathMatrix:
        sys.stdout.write('|') # Vertical lines in grid
        for item in row:
            if item == WALL_KEY:
                sys.stdout.write(WALL_CHAR)
            elif item == OPEN_KEY:
                sys.stdout.write(CLEAR_CHAR)
            else:
                sys.stdout.write("ERROR, INVALID CHARACTER IN pathMatrix!")
            sys.stdout.write('|') # Vertical lines in grid
        print() # Newline for horizontal lines
        for item in row:
            sys.stdout.write('--') # Horizontal lines
        print() # Newline for next row of map

def completeMap():
    x_counter = 0
    y_counter = 0
    cat_counter = 0
    for row in pathMatrix:
        for item in row:
            cat_counter = 0
            for category in resourceList:
                resource = 0
                for coord in category:
                    if x_counter == coord[0] and y_counter == coord[1]:
                        sys.stdout.write(resourceKeys[cat_counter])
                        resource = 1
                cat_counter += 1
        x_counter += 1
    y_counter += 1

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

def emptyMap(x,y):
    
    FILL_NUM = OPEN_KEY
    
    for i in range(0, x):
        pathMatrix[0].append(FILL_NUM)
            
    tempList = []

    for item in pathMatrix[0]:
        tempList.append(FILL_NUM)
    
    for i in range(0, y):
        pathMatrix.append(tempList)

    dispMap()

def checkEdges():
    global currentX
    global currentY
    if currentX == 0:
        print("On west edge")
        addWalls("W")
        currentX = 1
    if currentX == len(pathMatrix[0]) - 1:
        print("On east edge")
        addWalls("E")
#    if currentY == 0:
#        print("On South edge")
#        addWalls("S")
#        currentY = 1
    if currentY == len(pathMatrix) - 1:
        print("On North edge")
        addWalls("N")
    
def moveForward():
    global currentX
    global currentY
    global currentDir
    global pathMatrix
    
    #checkEdges()
    driveLibrary.driveDistance()
    
    if currentDir == "N":
        currentY += 1
    elif currentDir == "E":
        currentX += 1
    elif currentDir == "S":
        currentY -= 1
    elif currentDir == "W":
        currentX -= 1
        
    pathMatrix[currentY][currentX] = OPEN_KEY
    #checkEdges()

    print("Moved to:", currentX, currentY)

def updateScanDir():
    global currentDir
    global scanDir
    global scanPos
    
    scanDir = numToDir(dirToNum(currentDir) + dirToNum(scanPos))
    
    return scanDir
    
def turnRight():
    global currentDir
    global scanDir

    driveLibrary.turnRight()
    
    currentDir = numToDir(dirToNum(currentDir) + 1)
    scanDir = currentDir
    print("Current Direction is:", currentDir)
    
def turnLeft():
    global currentDir
    global scanDir
    
    driveLibrary.turnLeft()
    
    currentDir = numToDir(dirToNum(currentDir) - 1)
    scanDir = currentDir
    print("Current Direction is:", currentDir)
    
def scanSurroundings():
    global scanDir
    global scanPos
    global unexploredPts
    
    checkEdges()
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

        checkEdges()
        
        if clear_var == 1:
            pathMatrix[check_y][check_x] = OPEN_KEY
            unexploredPts.append([check_x, check_y])
            
        elif clear_var == 2:
            pathMatrix[check_y][check_x] = WALL_KEY
            try:
                unexploredPts.remove([check_x, check_y])
            except:
                pass

        elif clear_var == 3:
            pathMatrix[check_y][check_x] = OPEN_KEY
            unexploredPts.append([check_x, check_y])

        unexploredPts = removeDuplicates(unexploredPts)
        
        dispMap()
        
        
def removeDuplicates(starting_list):
    final_list = []
    for i in starting_list:
        if i not in final_list:
            final_list.append(i)
    return final_list

def dirToNum(direction):
    
    if direction == "N" or direction == "F":
        return 0
    elif direction == "E" or direction == "R":
        return 1
    elif direction == "S" or direction == "B":
        return 2
    elif direction == "W" or direction == "L":
        return 3

def numToDirScanner(number):
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
    
def numToDir(number):
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

