import time
import math

import numpy as np

from pyfirmata import Arduino
from pyfirmata import util

from multiprocessing import Process
from multiprocessing import Value

def conversion_func(num, coeff, coeff_2=0):
	return int((100*np.exp(coeff *(1-((num-500.)/7500))) - coeff_2)/np.exp(coeff))

def pwm_loop(t_1, t_2):
	board = Arduino('COM7')

	time.perf_counter() #make sure counter started
	last = int((time.perf_counter() * 10 % 1) * 100)

	while True:
		current = int((time.perf_counter() * 10 % 1) * 100)
		if current < last:
			board.digital[13].write(1)
			board.digital[12].write(1)
		if current >= t_1.value:
			board.digital[13].write(0)
		if current >= t_2.value:
			board.digital[12].write(0)
		last = current
		#print(current) #to debug off trigger windowr

def input_loop(t_1, t_2):
	coeff = 3

	# t_1.value = 0
	# t_2.value = 50

	for i in range(500, 7500):
		t_1.value = conversion_func(i, coeff)
		t_2.value = conversion_func((8000-i), coeff)
		print("t1: {}\tt2: {}".format(t_1.value, t_2.value))
		time.sleep(.002)

	print("end")


if __name__ == '__main__':
	trigger_1 = Value('i', 0)
	trigger_2 = Value('i', 0)

	pwm_process = Process(target=pwm_loop, args=(trigger_1, trigger_2))
	input_process = Process(target=input_loop, args=(trigger_1, trigger_2))

	pwm_process.start()
	input_process.start()
	pwm_process.join()
	input_process.join()