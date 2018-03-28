import sys
#import driveLibrary

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

currentX = 0
currentY = 0
currentDir = "S"
scanDir = "S"
scanPos = "F"

pathMatrix = [[OPEN_KEY]]

def dispMap():
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
    
    checkEdges()
    if currentDir == "N":
        currentY -= 1
    elif currentDir == "E":
        currentX += 1
    elif currentDir == "S":
        currentY += 1
    elif currentDir == "W":
        currentX -= 1
        
    pathMatrix[currentY][currentX] = OPEN_KEY
    checkEdges()

def updateScanDir():
    global currentDir
    global scanDir
    global scanPos
    
    scanDir = numToDir(dirToNum(currentDir) + dirToNum(scanPos))
    
    return scanDir
    
def turnRight():
    global currentDir
    global scanDir
    
    currentDir = numToDir(dirToNum(currentDir) + 1)
    scanDir = currentDir
    print("Current Direction is:", currentDir)
    
def turnLeft():
    global currentDir
    global scanDir
    
    currentDir = numToDir(dirToNum(currentDir) - 1)
    scanDir = currentDir
    print("Current Direction is:", currentDir)
    
def scanSurroundings():
    global scanDir
    
    checkEdges()
    updateScanDir()
    
    print("Current position: ", currentX, currentY)
    
    for i in ["F", "R", "L"]:
        driveLibrary.rotateScanner(i)
        
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