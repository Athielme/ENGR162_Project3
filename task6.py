import driveLibrary

BP.set_motor_dps(RIGHT_MOTOR + LEFT_MOTOR, 10)
waitForButtonPress()
driveDistance(target_distance = -20)
turnRight()
turnRight()
