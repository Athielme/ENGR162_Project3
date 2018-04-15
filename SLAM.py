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

start_x = 3
start_y = 0
currentX = start_x
currentY = start_y
currentDir = "S"
scanDir = "S"
scanPos = "F"

unexploredMatrix = [[start_x, start_y + 1]]

pathMatrix = [[OPEN_KEY]]

def advance():
    moveForward()
    scanSurroundings()

def goToFourPoints(x1,y1,x2,y2,x3,y3,x4,y4):
    global currentX
    global currentY
    global pathMatrix
    
    xlist = [x1,x2,x3,x4]
    ylist = [y1,y2,y3,y4]

    xmax = x1
    for x in xlist:
        if x > xmax:
            xmax = x

    ymax = y1
    for y in ylist:
        if y > ymax:
            ymax = y

    emptyMap(xmax, ymax)

    currentX = 1
    currentY = 1

    for i in range(currentY, y1):
        moveForward()

    
    turnTowards("W")

    for i in range(currentX, x1):
        moveForward()
    time.sleep(5)
    #POINT 2
    if y1 - y2 > 0:
        turnTowards("N")
    else:
        turnTowards("S")
    for i in range(currentY, currentY + abs(y1 - y2)):
        moveForward()

    if x1 - x2 > 0:
        turnTowards("W")
    else:
        turnTowards("E")

    for i in range(currentX, currentX + abs(x1-x2)):
        moveForward()

    time.sleep(5)
    #POINT 3
    if y2 - y3 > 0:
        turnTowards("N")
    else:
        turnTowards("S")
    for i in range(currentY, currentY + abs(y2 - y3)):
        moveForward()

    if x2 - x3 > 0:
        turnTowards("W")
    else:
        turnTowards("E")

    for i in range(currentX, currentX + abs(x2-x3)):
        moveForward()
    time.sleep(5)
    #POINT 3
    if y3 - y4 > 0:
        turnTowards("N")
    else:
        turnTowards("S")
    for i in range(currentY, currentY + abs(y3 - y4)):
        moveForward()

    if x3 - x4 > 0:
        turnTowards("W")
    else:
        turnTowards("E")

    for i in range(currentX, currentX + abs(x3-x4)):
        moveForward()

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

def addWalls(direction):
    
    FILL_NUM = WALL_KEY # Number to fill lists with
    
    if direction == "N": # North
        tempList = [] # Create list of filler numbers
        for item in pathMatrix[0]: # number of columns
            tempList.append(FILL_NUM)
        pathMatrix.insert(0,tempList) # Set as top row
        
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
    if currentY == 0:
        print("On north edge")
        addWalls("N")
        currentY = 1
    if currentY == len(pathMatrix) - 1:
        print("On south edge")
        addWalls("S")
    
def moveForward():
    global currentX
    global currentY
    global currentDir
    global pathMatrix
    
    #checkEdges()
    driveLibrary.driveDistance()
    
    if currentDir == "N":
        currentY -= 1
    elif currentDir == "E":
        currentX += 1
    elif currentDir == "S":
        currentY += 1
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

    checkEdges()
    updateScanDir()
    
    print("Current position: ", currentX, currentY)
    
    for i in ["F", "R", "L", "F"]:
        driveLibrary.rotateScanner(i)
        scanPos = i
        scanDir = updateScanDir()
        print("Scanning: ", scanDir)
        if driveLibrary.isClear():
            if scanDir == "N":
                pathMatrix[currentY - 1][currentX] = OPEN_KEY
                
            elif scanDir == "E":
                pathMatrix[currentY][currentX + 1] = OPEN_KEY
                
            elif scanDir == "S":
                pathMatrix[currentY + 1][currentX] = OPEN_KEY
                
            elif scanDir == "W":
                pathMatrix[currentY][currentX - 1] = OPEN_KEY
                
        else:
            if scanDir == "N":
                pathMatrix[currentY - 1][currentX] = WALL_KEY
                
            elif scanDir == "E":
                pathMatrix[currentY][currentX + 1] = WALL_KEY
                
            elif scanDir == "S":
                pathMatrix[currentY + 1][currentX] = WALL_KEY
                
            elif scanDir == "W":
                pathMatrix[currentY][currentX - 1] = WALL_KEY      
                
        dispMap()
        
        
    
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
