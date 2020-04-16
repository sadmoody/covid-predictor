import numpy as np

def func(x, a, b, c):
    return a * np.exp(-b * x) + c

def poly_four(x, a, b, c, d, e):
    return a * np.power(x, 4) + b * np.power(x, 3) + c * np.power(x, 2) + d * x + e

def poly_three(x, a, b, c, d):
    return a * np.power(x, 3) + b * np.power(x, 2) + c * x + d

def poly_two(x, a, b, c):
    return a * np.power(x, 2) + b * x + c

def poly_two_dx(x, a, b, c):
    return 2 * a * x + b

def poly_three_dx(x, a, b, c, d):
    return 3 * a * np.power(x, 2) + 2 * b * x + c