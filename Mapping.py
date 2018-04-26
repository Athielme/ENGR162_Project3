# Team13

# Brute Force (if one exit/entrance)

import driveLibrary as l
import SLAM as s

def leftFace():
    global facing
    return [-facing[1],facing[0]]

def rightFace():
    global facing
    return [facing[1],-facing[0]]

def frontFace():
    global facing
    return facing

def forward():
    global pos
    l.driveDistance()
    face = frontFace()
    pos[0] += face[0]
    pos[1] += face[1]
    
    
def turnLeft():
    l.turnLeft()

def turnRight():
    l.turnRight()

def checkLeft():
    global m
    tempFacing = leftFace()
    if m[pos[0]+tempFacing[0]][pos[1]+tempFacing[1]] == 0:
        l.rotateScanner("L")
        clear = l.isClear()
        if clear:
            m[pos[0]+tempFacing[0]][pos[1]+tempFacing[1]] = 1
        else:
            m[pos[0] + tempFacing[0]][pos[1] + tempFacing[1]] = 5
    return

def checkFront():
    global m
    tempFacing = frontFace()
    if m[pos[0]+tempFacing[0]][pos[1]+tempFacing[1]] == 0:
        l.rotateScanner("F")
        clear = l.isClear()
        if clear:
            m[pos[0]+tempFacing[0]][pos[1]+tempFacing[1]] = 1
        else:
            m[pos[0] + tempFacing[0]][pos[1] + tempFacing[1]] = 5
    return

def checkRight():
    global m
    tempFacing = rightFace()
    if m[pos[0]+tempFacing[0]][pos[1]+tempFacing[1]] == 0:
        l.rotateScanner("R")
        clear = l.isClear()
        if clear:
            m[pos[0]+tempFacing[0]][pos[1]+tempFacing[1]] = 1
        else:
            m[pos[0] + tempFacing[0]][pos[1] + tempFacing[1]] = 5
    return

def leftPriority():
    global m
    tempFacing = leftFace()
    if m[pos[0] + tempFacing[0]][pos[1] + tempFacing[1]] == 0:
        return True
    else:
        return False

def frontPriority():
    global m
    tempFacing = frontFace()
    if m[pos[0] + tempFacing[0]][pos[1] + tempFacing[1]] == 0:
        return True
    else:
        return False

def rightPriority():
    global m
    tempFacing = rightFace()
    if m[pos[0] + tempFacing[0]][pos[1] + tempFacing[1]] == 0:
        return True
    else:
        return False

def fillOutside():
    global m
    for row in range(0,len(m)):
        for j in range(0,len(m[0])):
            if m[row][j] == 0:
                m[row][j] == 7
            else:
                break
        for j in range(len(m[0])-1,-1):
            if m[row][j] == 0:
                m[row][j] == 7
            else:
                break

def mapFull():
    global m
    for i in m:
        if j in i:
            if j == 0:
                return False
    return True


def printMap():
    global m
    for row in m:
        print(row)

#PROGRAM STARTS
#------------------------------------------------------------------------------

mode = "outside"
m = []
for i in range(0,50):
    m.append([])
    for j in range(0,50):
        m[i].append(0)

startPos = [25,25]
facing = [0,1] #up on map
pos = startPos

while mode == "outside":
    if checkLeft():
        turnLeft()
        forward()
    elif checkFront():
        forward()
    elif checkRight():
        turnRight()
        forward()
    else:
        turnRight()
        turnRight()
        forward()

    if pos == startPos:
        mode = "inside"

fillOutside()
print("outside filled")
#loop inside hug left priority if possible, otherwise hug right non-priority but check priority every step

while mode == "inside":
    if checkLeft() and leftPriority():
        turnLeft()
        forward()
    elif checkFront() and frontPriority():
        forward()
    elif checkRight() and rightPriority():
        turnRight()
        forward()
    elif checkRight():
        turnRight()
        forward()
    elif checkFront():
        forward()
    elif checkLeft():
        turnLeft()
        forward()
    else:
        turnRight()
        turnRight()
        forward()

    if mapFull():
        mode = "collection"

printMap()
