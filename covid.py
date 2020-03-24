import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np

def func(x, a, b, c):
    return a * np.exp(-b * x) + c

def func_poly(x, a, b, c, d):
    return a * np.power(x, 3) + b * np.power(x, 2) + c * x + d

xdata = np.linspace(-3, 5, 50)
y = func_poly(xdata, -0.2, 0.8, 1, 1.2)
np.random.seed(1729)
y_noise = 0.5 * np.random.normal(size=xdata.size)
ydata = y #+ y_noise
plt.plot(xdata, ydata, 'b-', label='data')

popt, pcov = curve_fit(func_poly, xdata, ydata)
plt.plot(xdata, func_poly(xdata, *popt), 'r-', label='fit: a=%5.3f, b=%5.3f, c=%5.3f, d=%5.3f' % tuple(popt))

plt.show()