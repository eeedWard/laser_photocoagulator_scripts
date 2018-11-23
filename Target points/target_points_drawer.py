#this scripts projects the target points (in absolute coordinates) onto the camera image,
#using the camera projection equation. 

import numpy as np
import cv2
import pickle

#%% live video


# Load target points in abs coordinates form txt files
with open("TargetPoints.txt", 'rb') as file:
    targetPoints = pickle.load(file)


# Set frame dimensions
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2048)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2048)

# Check that camera is opened
ret = cap.isOpened()
print("Opened: ", ret)

# Prepare preview window
cv2.namedWindow('Target points', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Target points', 600, 600)

# Just to keep track of the number of frames analysed
iterat = 1

try:
    while ret:
        ret, original = cap.read()
        original = original[:,:,0]
        img = cv2.resize(original, (2048, 2048))
        
        for p in targetPoints:
            # Project target point onto image plane
            s = np.matmul(CameraCalibration.KRt[2,:], [p[0], p[1], p[2], 1])
            [Xpixel, Ypixel, ones] = s**-1 * np.matmul(CameraCalibration.KRt, [p[0], p[1], p[2], 1])
            #Get integer pixels values
            [Xpixel, Ypixel] = [int(Xpixel), int(Ypixel)]
            # Draw target point
            cv2.circle(img, (Xpixel, Ypixel), 4, (255, 255, 255), 2)
            
        cv2.imshow('Target points', img)
        
    # waits some ms before updating the preview window
        cv2.waitKey(10)
        iterat += 1

#Stop iteration with Ctrl + C
except KeyboardInterrupt:
    pass
    
# Closes camera and preview window
cap.release()
cv2.destroyAllWindows()