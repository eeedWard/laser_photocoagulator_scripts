import os
cwd = os.getcwd()
os.chdir(r'C:\Users\Edoardo\Google Drive\Uni Edo\Master\Semester 2\Semester Project\Python\Target points\Images')

import numpy as np
import cv2
import pickle

'''
This function generates target points in abs coordinates from a single frame and a set of camera calibration parameters
This script has to be run only once. Once the target points are obtained, they remain unvaried since the abs coordinates are attached to the sphere centre
'''
# Enter the specific frame used to generate target points
img = cv2.imread('paint2.png', 0)
# This defines how dense the target points in pixels are
pixelsPerPoint = 73


# use this fcn to obtain abs coordinates from image points
def image_point_to_sphere_coordinates(image_point):
    
    Xc = 0
    Yc = 0
    Zc = 0
    radius = 12

    #enter camera parameters
    [Xcamera, Ycamera, Zcamera] = [3.05094266, -3.51596125, 87.84327886]
    
    K = np.array([[5900.96368833862, 0.0, 1066.6240577486549], [0.0, 5887.803899984632, 1068.813084362308], [0.0, 0.0, 1.0]])
    KR = np.matmul(K, rotation_matrix)
    
    ###### solve the system iteratively
    # sphere equation constant parameter
    e = Xc**2 + Yc**2 + Zc**2 - radius**2
    
    # start with a sensible guess of x, y, and z
    z = Zc + 0.5 * radius
    x = Xc + 0.5 * radius
    y = Yc + 0.5 * radius
    
    error = 15
    iteration = 0
    deltaRet = True
    while error > 0.000000001:
        Zrel = z - Zcamera
        Yrel = y - Ycamera
        Xrel = x - Xcamera
        row = np.dot([Xrel, Yrel, Zrel], KR[2,:]) # Obtain magnification factor in camera projection eqn
        [Xrel, Yrel, ZrelNew] = np.linalg.solve(KR, row * np.array([image_point[0], image_point[1], 1])) # Solve projection eqn
        x = Xrel + Xcamera
        y = Yrel + Ycamera
        
        # Sphere equation parameter and delta
        c = e + y**2 + x**2 - 2*x*Xc -2*y*Yc
        delta = Zc**2 - c
        
              
        if delta <= 40:
#            print()
#            print("!!!!!!!!!!!!")
#            print ("Error, delta < 0, ignore the results below")
#            print("!!!!!!!!!!!!")
            deltaRet = False
            break
        
        z1 = Zc + np.sqrt(delta)
        z2 = Zc - np.sqrt(delta)
          
    
        # choose point closest to the camera, difference in Z should be enough in most of the cases
        z_array = np.array([z1, z2])
        z_index = np.argmin([np.abs(z1-Zcamera), np.abs(z2-Zcamera)]) #
        zUpdate = z_array[z_index]
            
        error = np.abs(zUpdate - z)
        z = zUpdate
        iteration += 1
        
#        print ("Iteration error = ", error)
    
    target = np.array([x, y, z])
    return target, deltaRet




# Creates a list with all the target points in pixels
py, px = np.mgrid[0:2048:pixelsPerPoint, 0:2048:pixelsPerPoint]
points = np.c_[py.ravel(), px.ravel()]

# Initialize lists of target points (in abs coords) and in pixels (keeping only the ones inside the sphere, avoiding the black spots, i.e. retina, optic disk etc)
targetPoints = []
targetPixels = []

#meidan fitering and thresholding
iterat = 3
for c in range(0, iterat):
    median = cv2.medianBlur(img, 3)

ret, thresh = cv2.threshold(median, 55, 255,cv2.THRESH_BINARY)
#thresh = cv2.adaptiveThreshold(median,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,353, 20)

# Use this function to dilate black areas, in order to create a margin around optic disk, macula etc
kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
dilated = cv2.erode(thresh, kernel, iterations=25)

deltaRet = False
#img = cv2.imread('perf9.bmp', 3)


for p in points[:,]:
    if dilated[p[1], p[0]] > 100: # if the point is not located on a black area 
        pointTemp, deltaRet = image_point_to_sphere_coordinates(p)
#        deltaRet = True
    if deltaRet == True and p[1]<2050 and p[0]<1950: #if the sphere conversion fcn worked, i.e. if the point is inside the sphere (eye)
        targetPoints.append(pointTemp)
        targetPixels.append(p)
        cv2.circle(img, (p[0], p[1] ), 6, (0, 255, 0), -1)
        deltaRet = False
        
print("Number of target points: ", len(targetPoints)) #should be around 1000 - 3000
print()

#%% display image

cv2.namedWindow('Targets', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Targets', 600, 600)
cv2.imshow('Targets', img)

cv2.namedWindow('Thresholded', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Thresholded', 600, 600)
cv2.imshow('Thresholded', dilated)

cv2.waitKey(0)
cv2.destroyAllWindows()

#%% store target poins in a file
os.chdir(r'C:\Users\Edoardo\Google Drive\Uni Edo\Master\Semester 2\Semester Project\Python\Target points')
with open("TPoints_SuperCoarse_veryCentral_halfEye_220.txt", 'wb') as file:
    pickle.dump(targetPoints, file)

#%%
cv2.destroyAllWindows()