import math

import numpy as np
import matplotlib.pyplot as plt

def conversion_func(num, coeff, coeff_2=0):
	return (100*np.exp(coeff *(1-((num-500.)/7500))) - coeff_2)/np.exp(coeff)

def get_ys(input_vals, coeff):
	return [conversion_func(n, coeff) for n in input_vals]

if __name__ == '__main__':
	inp = np.linspace(500,8000,8000)

	for n in range(2,10):
		plt.plot(inp, get_ys(inp,n), label='c = {}'.format(n))
	plt.legend(loc='upper right')
	plt.show()

