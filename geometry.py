import numpy as np 
from scipy.spatial.transform import Rotation

class GeomtryFunctions:
    '''
        Given an array of possible source positions (measured HRTFs in a sphere)
        calculate the apparent source position between the listener and the source
        when the user rotates their head
    '''
    def __init__(self, posArray, src_azim, src_elev):
        self.src_r = posArray[0, 2]
        src_azim = np.deg2rad(src_azim)
        src_elev = np.deg2rad(src_elev)
        src_x = self.src_r * np.cos(src_elev) * np.cos(src_azim)
        src_y = self.src_r * np.cos(src_elev) * np.sin(src_azim)
        src_z = self.src_r * np.sin(src_elev)
        self.src_pos = np.array([src_x, src_y, src_z])
        self.posArray = np.deg2rad(posArray)

    def haversine(self, lon1, lat1, lon2, lat2):
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)
        """
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
        c = 2 * np.arcsin(np.sqrt(a))
        self.dist = self.src_r * c


    def cart2sph(self, x, y, z):
        azimuth = np.arctan2(y, x)
        elevation = np.arctan2(z, np.sqrt(x**2 + y**2))
        return azimuth, elevation  # radians


    def closestPosIdx(self, yaw=0, pitch=0, roll=0):
        rot = Rotation.from_euler('zyx', [yaw, pitch, roll], degrees=True)  # create rotation transform 
        APR_xyz = rot.apply(self.src_pos)  # apply rotation over source position 
        (aparent_azi, aparent_ele) = self.cart2sph(*APR_xyz)  # bring it back to spherical coordinates

        # select position that matches the apparent source position
        self.haversine(self.posArray[:, 0], self.posArray[:, 1], aparent_azi, aparent_ele)
        return np.argmin(self.dist)
  