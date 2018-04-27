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
