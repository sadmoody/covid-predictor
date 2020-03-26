import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
import pandas as pd
import os
from glob import glob
import datetime

DATADIR = "COVID-19\csse_covid_19_data\csse_covid_19_daily_reports"

def func(x, a, b, c):
    return a * np.exp(-b * x) + c

def func_poly_four(x, a, b, c, d, e):
    return a * np.power(x, 4) + b * np.power(x, 3) + c * np.power(x, 2) + d * x + e

def func_poly(x, a, b, c, d):
    return a * np.power(x, 3) + b * np.power(x, 2) + c * x + d

df = pd.read_json('data.min.json')
df_us = df[df['Country'] == 'US'].tail(14)
print(df_us)
df_us['y'] = (df_us['Date'] - df_us['Date'].iloc[0]).dt.days

ydata = df_us['Confirmed'].to_numpy()

xdata = df_us['y'].to_numpy()
print(xdata)
print()
print(df_us['y'])

plt.plot(xdata, ydata, 'b-', label='data')
popt, pcov = curve_fit(func_poly, xdata, ydata)
plt.plot(np.linspace(-6,21), func_poly(np.linspace(-6,21), *popt), 'r-', label='fit: a=%5.3f, b=%5.3f, c=%5.3f, d=%5.3f' % tuple(popt))
print(df_us)
print(popt)
print(f"next value is: {func_poly(df_us.iloc[df_us.shape[0]-1]['y']+1, *popt)}")
print(f"next value is: {func_poly(df_us.iloc[df_us.shape[0]-1]['y']+2, *popt)}")
print(f"next value is: {func_poly(df_us.iloc[df_us.shape[0]-1]['y']+3, *popt)}")
plt.show()