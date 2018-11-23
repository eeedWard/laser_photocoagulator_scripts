#this is used to obtain the pose of the catheter by knowing where the laser is hitting on the target surface

import numpy as np

targetPoint = np.array([-10, 2, 7]) # point on the eye hit by the laser
proximalPoint = np.array([8.24, 2.21, -8.44]) # attachment point of catheter

translationVector = targetPoint - proximalPoint # translation vector 
Zaxis = translationVector / np.linalg.norm(translationVector) # normalize translation vector to get Z axis direction

# model proximal orientation as the result two consecutive rotations about X  and Y (absolute axes)
thetaX =  - np.arcsin(Zaxis[1])
thetaY =  np.arcsin(Zaxis[0] / np.cos(thetaX))

# build full rotation matrix. R = RY * RX
RotX = np.array([[1, 0, 0], [0, np.cos(thetaX), -np.sin(thetaX)], [0, np.sin(thetaX), np.cos(thetaX)]])
RotY = np.array([[np.cos(thetaY), 0, np.sin(thetaY)], [0, 1, 0], [-np.sin(thetaY), 0, np.cos(thetaY)]])
Rot = np.matmul(RotY, RotX)

print("Proximal Z axis direction: ")
print(Zaxis)
print()
print("Proximal rotation matrix")
print(Rot)
print()
