import sys

CLEAR_CHAR = 'X'
WALL_CHAR = ' '

currentX = 0
currentY = 0
currentDir = "S"
scanDir = "S"

mapMatrix = [[0]]

def dispMap():
    for row in mapMatrix:
        sys.stdout.write('|') # Vertical lines in grid
        for item in row:
            if item == 1:    
                sys.stdout.write(WALL_CHAR)
            elif item == 0:
                sys.stdout.write(CLEAR_CHAR)
            else:
                sys.stdout.write("ERROR, INVALID CHARACTER IN mapMatrix!")
            sys.stdout.write('|') # Vertical lines in grid
        print() # Newline for horizontal lines
        for item in row:
            sys.stdout.write('--') # Horizontal lines
        print() # Newline for next row of map

def addWalls(direction):
    
    FILL_NUM = 1 # Number to fill lists with
    
    if direction == "N": # North
        tempList = [] # Create list of filler numbers
        for item in mapMatrix[0]: # number of columns
            tempList.append(FILL_NUM)
        mapMatrix.insert(0,tempList) # Set as top row
        
    elif direction == "S": # South
        tempList = [] # Create list of filler numbers
        for item in mapMatrix[0]: # number of columns
            tempList.append(FILL_NUM)
        mapMatrix.append(tempList) # Set as bottom row    
    
    elif direction == "E": # East
        for row in mapMatrix: 
            row.append(FILL_NUM) # Add filler at end of every row
    
    elif direction == "W": # West
        for row in mapMatrix:
            row.insert(0,FILL_NUM) # Add filler at start of every row 

def checkEdges():
    global currentX
    global currentY
    if currentX == 0:
        print("On west edge")
        addWalls("W")
        currentX = 1
    if currentX == len(mapMatrix[0]) - 1:
        print("On east edge")
        addWalls("E")
    if currentY == 0:
        print("On north edge")
        addWalls("N")
        currentY = 1
    if currentY == len(mapMatrix) - 1:
        print("On south edge")
        addWalls("S")
    
def moveForward():
    global currentX
    global currentY
    global currentDir
    global mapMatrix
    
    checkEdges()
    if currentDir == "N":
        currentY -= 1
    elif currentDir == "E":
        currentX += 1
    elif currentDir == "S":
        currentY += 1
    elif currentDir == "W":
        currentX -= 1
        
    mapMatrix[currentY][currentX] = 0
    checkEdges()
    
def isClear():
    return int(input("Clear? ")) # TEMPORARY!!!! NEEDS TO BE CODED

def rotateScanner():
    global scanDir
    
    curDirNum = dirToNum(currentDir)
    scanDirNum = dirToNum(scanDir)
    
    scanDir = numToDir(curDirNum + scanDirNum + 1)
    # TEMPORARY!!!! NEEDS TO BE CODED
    
def turnRight():
    global currentDir
    global scanDir
    
    currentDir = numToDir(dirToNum(currentDir) + 1)
    scanDir = currentDir
    
def turnLeft():
    global currentDir
    global scanDir
    
    currentDir = numToDir(dirToNum(currentDir) - 1)
    scanDir = currentDir
    
def scanSurroundings():
    global scanDir
    
    checkEdges()
    scanDir = currentDir
    print("Current position: ", currentX, currentY)
    
    for i in ["F", "R", "B", "L"]:
        print("Scanning: ", scanDir)
        if isClear():
            if scanDir == "N":
                mapMatrix[currentY - 1][currentX] = 0
                
            elif scanDir == "E":
                mapMatrix[currentY][currentX + 1] = 0
                
            elif scanDir == "S":
                mapMatrix[currentY + 1][currentX] = 0
                
            elif scanDir == "W":
                mapMatrix[currentY][currentX - 1] = 0
                
        else:
            if scanDir == "N":
                mapMatrix[currentY - 1][currentX] = 1
                
            elif scanDir == "E":
                mapMatrix[currentY][currentX + 1] = 1
                
            elif scanDir == "S":
                mapMatrix[currentY + 1][currentX] = 1
                
            elif scanDir == "W":
                mapMatrix[currentY][currentX - 1] = 1      
                
        rotateScanner()
        
    
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