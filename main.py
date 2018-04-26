import driveLibrary
import SLAM

SLAM.emptyMap(SLAM.map_max_x, SLAM.map_max_y)


SLAM.moveForward()
SLAM.scanSurroundings()
while(1 == 1):
    SLAM.completeMap()
    SLAM.drivePath(SLAM.pathToClosestPt())
    SLAM.scanSurroundings()
