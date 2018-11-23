import numpy as np
import rotations as rot


def image_point_to_sphere_coordinates(image_point, sphere, camera_calibration):
    """
    For a camera pointing at a hemisphere this function maps a pixel coordinate to a 3D point on the sphere.

    This function iteratively solves for the image point that lies on the closest point of the sphere to the camera.

    Params:
        -image_point: 2D tuple of image coordinates (x, y)
        -sphere: a sphere object containing the sphere parameters
        -camera_calibration: CameraCalibration object
    Returns:
        a dict containing
        'success':  True or False
        'iterations': number of iterations until stop
        'error': error string if there was a failure
        'result': tuple (x, y, z) of sphere point coordinates or None if failed
    """

    # start with a sensible guess of x, y, and z
    x = sphere.center[0] + 0.5 * sphere.r
    y = sphere.center[1] + 0.5 * sphere.r
    z = sphere.center[2] + 0.5 * sphere.r
    
    error = 15
    iteration = 0

    while error > 0.0000001:
        Xrel = x - camera_calibration.c[0]
        Yrel =y - camera_calibration.c[1]
        Zrel = z - camera_calibration.c[2]

        row = np.dot([Xrel, Yrel, Zrel], camera_calibration.KR[2,:]) # Obtain magnification factor in camera projection eqn
        [Xrel, Yrel, ZrelNew] = np.linalg.solve(camera_calibration.KR, row * np.array([image_point[0], image_point[1], 1])) # Solve projection eqn
        x = Xrel + camera_calibration.c[0]
        y = Yrel + camera_calibration.c[1]
        
        # sphere equation parameters
        c = sphere.e + y**2 + x**2 - 2*x*sphere.center[0] -2*y*sphere.center[1]
        delta = sphere.center[2]**2 - c

        if delta <= 0:
            res = {
                    'success': False,
                    'iterations': iteration,
                    'error': 'Error, delta < 0',
                    'result': None} 
            return res
        
        z1 = sphere.center[2] + np.sqrt(delta)
        z2 = sphere.center[2] - np.sqrt(delta)

        # choose point closest to the camera, difference in Z should be enough in most of the cases
        z_array = np.array([z1, z2])
        z_index = np.argmin([np.abs(z1-camera_calibration.c[2]), np.abs(z2-camera_calibration.c[2])]) #
        zUpdate = z_array[z_index]
            
        error = np.abs(zUpdate - z)
        z = zUpdate
        iteration += 1
    
    res = {
            'success': True,
            'iterations': iteration,
            'error': None,
            'result': (x, y, z)
            }

    return res


def distal_pose_to_sphere_coordinates(distal_translation, distal_rotation_matrix, sphere):
    """
    Projects the distal tangent forward to find intersection with sphere

    Params:
        - distal_translation: 3x1 numpy array of distal position
        - distal_rotation_matrix: 3x3 numpy array of distal orientation
        - sphere: Sphere object containing sphere coordinates
    Returns:
        - point on sphere that intersects distal tangent line
    """

    # distal tangent axis
    mag_z_axis = distal_rotation_matrix.dot(rot.ez())

    # solve system
    delta = (np.dot(mag_z_axis,(distal_translation - sphere.center)))**2 - (np.linalg.norm(distal_translation
        -sphere.center))**2 + sphere.r**2
    d1 = - (np.dot(mag_z_axis, (distal_translation - sphere.center))) + np.sqrt(delta)
    d2 = - (np.dot(mag_z_axis, (distal_translation - sphere.center))) - np.sqrt(delta)

    #choose point closer to magnet position
    d_array = np.array([d1, d2])
    d_index = np.argmin([np.abs(d1), np.abs(d2)]) #
    d = d_array[d_index]

    target = distal_translation + d * mag_z_axis

    return target