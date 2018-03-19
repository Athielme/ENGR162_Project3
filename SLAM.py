import sys

CLEAR_CHAR = 'X'
WALL_CHAR = ' '
global currentX 
currentX = 0
global currentY 
currentY = 0
global currentDir
currentDir = "S"

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
    return input("Clear? ") # TEMPORARY!!!! NEEDS TO BE CODED

def rotateScanner(position):
    return # TEMPORARY!!!! NEEDS TO BE CODED
    
def scanSurroundings():
    checkEdges()
    scanDir = currentDir
    for i in range(0, 4):
        if isClear():
            if scanDir == "N":
                mapMatrix[currentY - 1][currentX] = 0
                
            elif scanDir == "E":
                mapMatrix[currentY][currentX - 1] = 0
                
            elif scanDir == "S":
                mapMatrix[currentY + 1][currentX] = 0
                
            elif scanDir == "W":
                mapMatrix[currentY][currentX + 1] = 0
        rotateScanner(i)
    dispMap()
    