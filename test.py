from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime

import ctypes
import _ctypes
import pygame
import sys

import numpy as np
import matplotlib.pyplot as plt

if sys.hexversion >= 0x03000000:
    import _thread as thread
else:
    import thread



if __name__ == '__main__':
    #kinect = PyKinectRuntime.PyKinectRuntime(FrameSourceTypes_Depth)

    fig = plt.figure()

    cmap = plt.cm.OrRd
    cmap.set_under(color='black')

    #depth_matrix = np.reshape(kinect.get_last_depth_frame(), (424, 512))
    depth_matrix = np.random.randint(500,8000,(424,512))
    im = plt.imshow(depth_matrix, interpolation='none', cmap=cmap, vmin=1)


    while True:
        if True:#kinect.has_new_depth_frame():
            #500 min distance
            #8000 max distance?
            #depth_matrix = np.reshape(kinect.get_last_depth_frame(), (424, 512))
            depth_matrix = np.random.randint(500,8000,(424,512))
            im = plt.imshow(depth_matrix, interpolation='none', cmap=cmap, vmin=1, animated=True)
            plt.draw()
            plt.pause(0.1)
            plt.cla()