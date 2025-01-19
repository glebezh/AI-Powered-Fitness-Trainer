import numpy as np

def calculate_angle(x, y, z):
    """
    Calculate the angle between three points using the cosine formula.

    Parameters:
    - x: Coordinates of the first point (numpy array or list).
    - y: Coordinates of the midpoint (numpy array or list).
    - z: Coordinates of the last point (numpy array or list).

    Returns:
    - Angle in degrees (float).
    """
    # Convert points to numpy arrays
    x = np.array(x)
    y = np.array(y)
    z = np.array(z)

    # Vectors relative to the midpoint
    vector1 = x - y
    vector2 = z - y

    # Cosine of the angle using the dot product formula
    cos_theta = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))

    # Ensure cos_theta is within the valid range [-1, 1] to avoid domain errors
    cos_theta = np.clip(cos_theta, -1.0, 1.0)

    # Calculate the angle in radians and convert to degrees
    theta = np.arccos(cos_theta)
    angle = np.degrees(theta)

    return angle
