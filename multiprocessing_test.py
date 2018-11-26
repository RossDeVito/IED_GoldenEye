import time

from multiprocessing import Process
from multiprocessing import Value

def print_loop(num):
	while True:
		print(num.value)
		time.sleep(1)

def increase_num(num):
	while True:
		time.sleep(1)
		num.value = num.value + 1

if __name__ == '__main__':
	num = Value('i', 0)

	loop_p = Process(target=print_loop, args=(num,))
	loop_i = Process(target=increase_num, args=(num,))

	loop_p.start()
	loop_i.start()
	loop_p.join()
	loop_i.join()
