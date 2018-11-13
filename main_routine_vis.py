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

def get_depth_matrix(kinect):
    #500 min distance
    #8000 max distance?

    #for testing not connected to kinect:
    #   np.random.randint(500,8000,(424,512))
    return np.fliplr(np.reshape(kinect.get_last_depth_frame(), (424, 512)))

def get_frame_maxes(frames, matrix):
    '''
    returns max value in each frame and location of that max value.

    args:
        frames: iterable of coords bounding region fromatted as 
            (xmin,xmax,ymin,ymax)
        matrix: matrix of depth values
    '''
    for frame in frames:
        submatrix = matrix[frame[2]:frame[3]+1, frame[0]:frame[1]+1]
        np.place(submatrix, submatrix<1, 9000)

        #trivial approach for demo
        # y,x = np.unravel_index(submatrix.argmin(), submatrix.shape)
        # yield submatrix[y, x], np.add([x, y], [frame[0], frame[2]])

        yield find_max_X_mask(submatrix, frame[0], frame[2])

def find_max_X_mask(matrix, x_offset, y_offset):
    min_sum = 999999999
    min_index = [x_offset, y_offset]
    for x in range(1, matrix.shape[1]-1):
        for y in range(1, matrix.shape[0]-1):
            this_sum = (matrix[y,x] 
                        + matrix[y+1,x+1]
                        + matrix[y-1,x+1]
                        + matrix[y-1,x-1]
                        + matrix[y+1,x-1])
            if this_sum < min_sum:
                min_sum = this_sum
                min_index = [x+x_offset, y+y_offset]
    return min_sum/5, min_index


if __name__ == '__main__':
    frames = [[0, 179, 0, 167], [180, 321, 0, 167], [332, 511, 0, 167],
                [0, 179, 168, 295], [180, 250, 168, 295], 
                [251, 321, 168, 295], [332, 511, 168, 295],
                [0, 179, 296, 423], [180, 321, 296, 423], [332, 511, 296, 423]]

    kinect = PyKinectRuntime.PyKinectRuntime(FrameSourceTypes_Depth)

    fig = plt.figure()

    #viridis_r, Spectral *,RdYlBu, rainbow_r, nipy_spectral_r, plasma_r
    cmap = plt.cm.gist_rainbow
    cmap.set_under(color='black')

    depth_matrix = get_depth_matrix(kinect)
    im = plt.imshow(depth_matrix, interpolation='none', cmap=cmap, vmin=1, vmax=8000)
    im = plt.plot([179.5,179.5], [0,423], 'k-')
    im = plt.plot([321.5,321.5], [0,423], 'k-')
    im = plt.plot([0,511], [167.5,167.5], 'k-')
    im = plt.plot([0,511], [295.5,295.5], 'k-')
    im = plt.plot([250.5,250.5], [167.5,295.5], 'k-')
    for max_val in get_frame_maxes(frames, depth_matrix):
        im = plt.plot(max_val[1][0], max_val[1][1], marker='x', color='red')


    while True:
        if kinect.has_new_depth_frame():
            #500 min distance
            #8000 max distance?
            depth_matrix = get_depth_matrix(kinect)
            im = plt.imshow(depth_matrix, interpolation='none', cmap=cmap, vmin=1, vmax=8000)
            im = plt.plot([179.5,179.5], [0,423], 'k-')
            im = plt.plot([321.5,321.5], [0,423], 'k-')
            im = plt.plot([0,511], [167.5,167.5], 'k-')
            im = plt.plot([0,511], [295.5,295.5], 'k-')
            im = plt.plot([250.5,250.5], [167.5,295.5], 'k-')
            for max_val in get_frame_maxes(frames, depth_matrix):
                im = plt.plot(max_val[1][0], max_val[1][1], marker='o', color='darkred', 
                    markersize=10, mew=5, fillstyle='none')
            plt.draw()
            plt.pause(0.01)
            plt.cla()