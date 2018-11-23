#this script runs image analysis on a set of frame in order to obtain the centroid of the distal part of the catheter in each frame.

#%% imports
import os
cwd = os.getcwd()
os.chdir(r'C:\Users\Edoardo\Google Drive\Uni Edo\Master\Semester 2\Semester Project\Python\Catheter calibration\Imgs and script for presentation')

import numpy as np
import cv2
from matplotlib import pyplot as plt
import pandas as pd

def nothing(x):
    pass

#%%
imgFixed = cv2.imread('imgs/frame0000.jpg', 3)
frameArray = []
cxArray = []
cyArray = []

for i in range(0,117):
    # read image
    if i<=9:
        imgPath = 'frame000' + str(i) + '.jpg'
    elif i<=99:
        imgPath = 'frame00' + str(i) + '.jpg'
    else:
        imgPath = 'frame0' + str(i) + '.jpg'
        
    img = cv2.imread('imgs/' + imgPath, 3)
    
    # Reduce image to interesting section
    Rx1 = 1100
    Rx2 = 1600
    Ry1 = 500
    Ry2 = 1900
    
    imgReduced = img[Ry1:Ry2, Rx1:Rx2]

    ######### median filtering
    iterat = 1
    for c in range(0, iterat):
        Median = cv2.medianBlur(imgReduced, 5)
        
    ############ thresholding
    ret, thresholded = cv2.threshold(Median, 65, 255,cv2.THRESH_BINARY_INV)
#    cv2.imwrite('cal_images #2 19-05/imgs/output folder/Thresholded_' + imgPath, thresholded)

    ########## dilation and erosion
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
    dilated = cv2.dilate(thresholded, kernel, iterations=10)
    eroded = cv2.erode(dilated, kernel, iterations=4)

    ####### Edge detection
    edges = cv2.Canny(eroded, 20, 120, True)
    
    ######## Find contours
    cnt, contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Choose only contours with a minimum area (keeps only the one around the magnet)
    threshold_area = 600     #threshold area 
    found = False
    for cont in contours:        
        area = cv2.contourArea(cont) 
        if area > threshold_area: 
            cnt = cont
            found = True 
    if found != True:
        print("Error, contour not found for " + imgPath)
            
 
    ####### Drawing rectangle around contour
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    cv2.drawContours(edges,[box],0,(255,255,255))
    
    # Save current image
    cv2.imwrite('imgs/output folder/Contour_' + imgPath, edges)

    ############ Bbtain centroid of the rectangle
    M = cv2.moments(cnt)

    # Centroid coordinates   
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])
    
    # Mark centroid on reduced image with a circle
    cv2.circle(edges, (cx,cy), 5, (255, 255, 255), 2)
    
    # Translate centre coordinates into original (not resized) image coordinates
    cxOriginal = cx + Rx1
    cyOriginal = cy + Ry1
    
    # Draw all centroids on originalimage
    cv2.circle(imgFixed, (cxOriginal, cyOriginal), 7, (0, 0, 255), -1)
    
    # Draw current centroid on current image
    cv2.circle(img, (cxOriginal, cyOriginal), 7, (0, 0, 255), -1)
    
#    # Save current image with centroid
    cv2.imwrite('imgs/output folder/Centroid_' + imgPath, img)
    
    ######## Store data
    frameArray.append(imgPath)
    cxArray.append(cxOriginal)
    cyArray.append(cyOriginal)

# Draw circle on attachment point
cv2.circle(imgFixed, (103, 1001), 11, (255, 0, 0), -1)
#%% Image display
cv2.namedWindow('Centroids', cv2.WINDOW_NORMAL)
cv2.imshow('Centroids', imgFixed)

cv2.waitKey(0)
cv2.destroyAllWindows()

#%% Save image
cv2.imwrite('imgs/output folder/ImgCentroids.jpg', imgFixed)

#%% Write results on spreadsheet
dfPreparation = {'Frame' : frameArray, 'cX' : cxArray, 'cY' : cyArray}
dataFrame = pd.DataFrame(dfPreparation)
dataFrame.to_excel('cal_images #2 19-05/Experiment results.xlsx', 'Sheet1', index = False)

