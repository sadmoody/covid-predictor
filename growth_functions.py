import numpy as np

def func(x, a, b, c):
    return a * np.exp(-b * x) + c

def poly_four(x, a, b, c, d, e):
    return a * np.power(x, 4) + b * np.power(x, 3) + c * np.power(x, 2) + d * x + e

def poly_three(x, a, b, c, d):
    return a * np.power(x, 3) + b * np.power(x, 2) + c * x + d