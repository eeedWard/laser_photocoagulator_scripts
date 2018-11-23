import numpy as np
import cv2

def calibrator_external(objpoints, checkboardShape,  camera_calibration): 
    """
    For a camera pointing at a chess board, this function continuosly evaluates the external parameters.
    Use CTRL + C to stop the function and store the last external parameters acquired
    
    Params:
        - objpoints: 1D list or numpy array of sets of absolute coordinates of chessboard corners,
         for current set up use: objpoints = np.array([[-7.5, 8, 0], [-3.5, 8, 0], [0.5, 8, 0], [4.5, 8, 0], [-7.5, 4, 0], [-3.5, 4, 0.], [0.5, 4, 0], [4.5, 4, 0], [-7.5, 0, 0], [-3.5, 0, 0], [0.5, 0, 0], [4.5, 0, 0], [-7.5, -4, 0], [-3.5, -4, 0], [0.5, -4, 0], [4.5, -4, 0], [-7.5, -8, 0], [-3.5, -8, 0], [0.5, -8, 0], [4.5, -8, 0]])
        - checkboardShape: 2D tuple of calibration checkboard dimension: number of internal corners (row, col),
         for current set up use: checkboardShape = (4, 5)
        - camera_calibration: CameraCalibration object
        
    Returns:
        a dict containing:
        'success':  True or False
        'iterations': number of frames analysed before interrupting the loop
        'error': error string if there was a failure
        'translation': translation vector
        'rotation_matrix': rotation matrix
    """

    # Initialize array to store image points: 2d points in image plane, pixel coords.
    imgpoints = [] 
    
    # termination criteria used to refine corner pixels (used later)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 300, 0.0001) #criteria for corner reduction
    
    ### Live video
    
    # Set frame dimensions
    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2048)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2048)
    
    # Check that camera is opened
    ret = cap.isOpened()
    print("Camera in operation: ", ret)
    
    # Prepare preview window
    cv2.namedWindow('Reduced size detection preview', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Reduced size detection preview', 600, 600)
    
    #resize image by a factor to speed up the process (crashes with 2048 x 2048), Introduces an accuracy error, careful!
    resizeFactor = 1
    dim = int(2048 / resizeFactor)
    
    iterat = 1
    try:
        while ret:
            ret, original = cap.read()
            original = original[:,:,0] # Eliminates RGB channels
            
            original = cv2.resize(original, (2048, 2048)) # Needed (for some unknown reasons) to later run cv2.cornerSubPix, otherwise crashes 
            img = cv2.resize(original, (dim, dim)) # Resize image to speed up. Introduces an accuracy error, careful!
            
            #Find chessboard corners
            retCorner, corners = cv2.findChessboardCorners(img, (checkboardShape[0], checkboardShape[1]), cv2.CALIB_CB_NORMALIZE_IMAGE + cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK)
            
            # If found, refine corners store image points
            print(retCorner, iterat)
            
            if retCorner == True:
                imgpoints = []
                imgpoints = cv2.cornerSubPix(img,corners,(11,11),(-1,-1),criteria)
                imgpoints = imgpoints.reshape(20,2)
                imgpoints = resizeFactor * imgpoints #to account for image resize above. Not sure if this is totally correct --> CHECK!
                
                
                #draw corners on image
                cv2.drawChessboardCorners(img, (4,5), corners, ret)
                cv2.drawChessboardCorners(original, (4,5), imgpoints, ret)
                
                #evaluate extrinsic params
                #in rot matrix : each ROW represents the camera axis in absolute coords
                retExtCalib, rotation_Vector, translation = cv2.solvePnP(objpoints, imgpoints, camera_calibration.K, camera_calibration.D)
                rotation_matrix, jacobian = cv2.Rodrigues(rotation_Vector)
                
                
                ext_calib = {
                'success': True,
                'iterations': iterat,
                'error': None,
                'translation': translation,
                'rotation_matrix': rotation_matrix,
                }
                
                
            cv2.imshow('Reduced size detection preview', img)
            
        # waits some ms before updating the preview window
            cv2.waitKey(50)
            iterat += 1
    
    #Stop iteration with Ctrl + C
    except KeyboardInterrupt:
        pass
        
    # Closes camera and preview window
    cap.release()
    cv2.destroyAllWindows()
    
    return ext_calib
