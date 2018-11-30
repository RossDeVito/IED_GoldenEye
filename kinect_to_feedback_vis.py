import time
import math
import sys
import ctypes
import _ctypes

import matplotlib.pyplot as plt
import numpy as np
import pygame

from pyfirmata import Arduino
from pyfirmata import util

from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime

from multiprocessing import Process
from multiprocessing import Value

if sys.hexversion >= 0x03000000:
	import _thread as thread
else:
	import thread

def conversion_func(num, coeff, coeff_2=0):
	return 100-int((100*np.exp(coeff *(1-((num-500.)/7500))) - coeff_2)/np.exp(coeff))

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

		yield find_max_X_mask_w_coords(submatrix, frame[0], frame[2])

def find_max_X_mask_w_coords(matrix, x_offset, y_offset):
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

def find_max_X_mask(matrix):
	min_sum = 999999999
	for x in range(1, matrix.shape[1]-1):
		for y in range(1, matrix.shape[0]-1):
			this_sum = (matrix[y,x] 
						+ matrix[y+1,x+1]
						+ matrix[y-1,x+1]
						+ matrix[y-1,x-1]
						+ matrix[y+1,x-1])
			if this_sum < min_sum:
				min_sum = this_sum
	return min_sum/5

def pwm_loop(t_0, t_1, t_2, t_3, t_4, t_5, t_6, t_7, t_8, t_9):
	board = Arduino('COM7')

	time.perf_counter() #make sure counter started
	last = int((time.perf_counter() * 10 % 1) * 100)

	while True:
		current = int((time.perf_counter() * 10 % 1) * 100)

		if current < last:
			board.digital[13].write(0)
			board.digital[12].write(0)
			board.digital[11].write(0)
			board.digital[10].write(0)
			board.digital[9].write(0)
			board.digital[8].write(0)
			board.digital[7].write(0)
			board.digital[6].write(0)
			board.digital[5].write(0)
			board.digital[4].write(0)

		#for below, <= could be < mathmatically, can change if performance difference
		if current >= t_0.value:
			board.digital[13].write(1)
		if current >= t_1.value:
			board.digital[12].write(1)
		if current >= t_2.value:
			board.digital[11].write(1)
		if current >= t_3.value:
			board.digital[10].write(1)
		if current >= t_4.value:
			board.digital[9].write(1)
		if current >= t_5.value:
			board.digital[8].write(1)
		if current >= t_6.value:
			board.digital[7].write(1)
		if current >= t_7.value:
			board.digital[6].write(1)
		if current >= t_8.value:
			board.digital[5].write(1)
		if current >= t_9.value:
			board.digital[4].write(1)

		last = current
		#print(current) #to debug off trigger window

def input_loop(t_0, t_1, t_2, t_3, t_4, t_5, t_6, t_7, t_8, t_9):
	coeff = 6
	frames = {
		0: [0, 179, 0, 167],
		1: [180, 321, 0, 167], 
		2: [332, 511, 0, 167],
		3: [0, 179, 168, 295],
		4: [180, 250, 168, 295], 
		5: [251, 321, 168, 295], 
		6: [332, 511, 168, 295],
		7: [0, 179, 296, 423], 
		8: [180, 321, 296, 423], 
		9: [332, 511, 296, 423]
	}
	triggers = {
		0: t_0,
		1: t_1, 
		2: t_2,
		3: t_3,
		4: t_4, 
		5: t_5, 
		6: t_6,
		7: t_7, 
		8: t_8, 
		9: t_9
	}

	kinect = PyKinectRuntime.PyKinectRuntime(FrameSourceTypes_Depth)

	cmap = plt.cm.gist_rainbow
	cmap.set_under(color='black')

	while True:
		depth_matrix = np.fliplr(np.reshape(kinect.get_last_depth_frame(), (424, 512)))

		im = plt.imshow(depth_matrix, interpolation='none', cmap=cmap, vmin=1, vmax=8000)
		im = plt.plot([179.5,179.5], [0,423], 'k-')
		im = plt.plot([321.5,321.5], [0,423], 'k-')
		im = plt.plot([0,511], [167.5,167.5], 'k-')
		im = plt.plot([0,511], [295.5,295.5], 'k-')
		im = plt.plot([250.5,250.5], [167.5,295.5], 'k-')

		for max_val in get_frame_maxes(frames.values(), depth_matrix):
			im = plt.plot(max_val[1][0], max_val[1][1], marker='o', color='darkred', 
				markersize=10, mew=5, fillstyle='none')

		for num, frame_coords in frames.items():
			submatrix = depth_matrix[frame_coords[2]:frame_coords[3]+1, 
								frame_coords[0]:frame_coords[1]+1]
			np.place(submatrix, submatrix<1, 50000)
			triggers[num].value = conversion_func(find_max_X_mask(submatrix), coeff)
			if num == 1:
				print(triggers[num].value)

		plt.draw()
		plt.pause(0.01)
		plt.cla()



if __name__ == '__main__':
	trigger_0 = Value('i', 0)
	trigger_1 = Value('i', 0)
	trigger_2 = Value('i', 0)
	trigger_3 = Value('i', 0)
	trigger_4 = Value('i', 0)
	trigger_5 = Value('i', 0)
	trigger_6 = Value('i', 0)
	trigger_7 = Value('i', 0)
	trigger_8 = Value('i', 0)
	trigger_9 = Value('i', 0)

	pwm_process = Process(
		target=pwm_loop, 
		args=(trigger_0, trigger_1, trigger_2, trigger_3, trigger_4, 
				trigger_5, trigger_6, trigger_7, trigger_8, trigger_9))
	input_process = Process(
		target=input_loop, 
		args=(trigger_0, trigger_1, trigger_2, trigger_3, trigger_4, 
				trigger_5,trigger_6, trigger_7, trigger_8, trigger_9))

	pwm_process.start()
	input_process.start()
	pwm_process.join()
	input_process.join()