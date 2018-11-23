#this script extracts frames from a live video where the camera is able to detect the chess board corners.
#the extracted frames are then used for intrinsic calibration (performed with Matlab)

import os
cwd = os.getcwd()
os.chdir(r'C:\Users\Edoardo\Desktop\GDrive not synced\Calibration not synced\Image_extractor_auto')


import numpy as np
import cv2

iterat = 1
iterat2 = 1

#%%

####calibration checkboard dimensions
checkboardShape = np.array([4, 5]) #internal number of points on checkboard (row, col)


# Set frame dimensions
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2048)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2048)
#cap.set(cv2.CAP_PROP_AUTO_EXPOSURE = 21) #this doesnt seem to work

cap.set(cv2.CAP_PROP_CONVERT_RGB, False)

# Check that camera is opened
ret = cap.isOpened()
print("Opened: ", ret)

# Prepare preview window
cv2.namedWindow('Preview', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Preview', 600, 600)
#cv2.namedWind1ow('Original', cv2.WINDOW_NORMAL)
#cv2.resizeWindow('Original', 600, 600)
# Just to keep track of the number of frames analysed


#resize image by a factor speed up the process (crashes with 2048 x 2048)
resizeFactor = 2
dim = int(2048 / resizeFactor)

try:
    while ret:
        ret, original = cap.read()
        original = original[:,:,0]
        
#        original = cv2.resize(original, (2048, 2048))
        img = cv2.resize(original, (dim, dim)) 
        #Find the chess board corners
        retCorner, corners = cv2.findChessboardCorners(img, (checkboardShape[0], checkboardShape[1]), cv2.CALIB_CB_NORMALIZE_IMAGE + cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK)

        # If found, refine corners store image points
        print(retCorner, iterat)
        if retCorner == True:
            written = cv2.imwrite("Image_extracted_auto" + str(iterat2) + ".jpg", original)
            if written != True:
                print("-------------")
                print("Error, not saving")
                print("-------------")

            iterat2 +=1
            
        cv2.imshow('Preview', img)
#        cv2.imshow('Original', original)
    # waits some ms before updating the preview window
        cv2.waitKey(200)
        iterat += 1

#Stop iteration with Ctrl + C
except KeyboardInterrupt:
    pass
    
# Closes camera and preview window
cap.release()
cv2.destroyAllWindows()

#%%
# Closes camera and preview window
cap.release()
cv2.destroyAllWindows()
rett = cv2.imwrite("Image_extracted_auto" + str(iterat2) + ".jpg", original)
print(rett)