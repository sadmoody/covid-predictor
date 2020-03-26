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

def func_poly(x, a, b, c, d):
    return a * np.power(x, 3) + b * np.power(x, 2) + c * x + d

DAILYREPORTS=os.path.join(DATADIR, "*.csv") 
allreports = [] 
for filename in glob(DAILYREPORTS):
    print(filename) 
    df = pd.read_csv(filename, index_col=None, header=0) 
    allreports.append(df) 
df = pd.concat(allreports, axis=0, ignore_index=True) 
#df['Country'] = df['Country/Region'] or df['Country_Region']
#df['Country'] = df[['Country/Region', 'Country_Region']].apply(lambda x: ''.join(x), axis=1)
df['Country'] = df['Country/Region'].fillna(df['Country_Region'])
df['Last Update'] = pd.to_datetime(df['Last Update']) 
df['Date'] = df["Last Update"].dt.date 
bycountry = df.groupby(["Country", "Date"]).agg({'Confirmed':'sum','Deaths':'sum', 'Recovered': 'sum', "Active": 'sum'})
bycountry = bycountry.reset_index()
print(bycountry)
df_us = bycountry[bycountry['Country'] == 'South Korea'].tail(14)
df_us['y'] = (df_us['Date'] - df_us['Date'].iloc[0]).dt.days



ydata = df_us['Confirmed'].to_numpy()

xdata = df_us['y'].to_numpy()
print(xdata)
print()
print(df_us['y'])

plt.plot(xdata, ydata, 'b-', label='data')
popt, pcov = curve_fit(func_poly, xdata, ydata)
plt.plot(xdata, func_poly(xdata, *popt), 'r-', label='fit: a=%5.3f, b=%5.3f, c=%5.3f, d=%5.3f' % tuple(popt))
print(df_us)
print(popt)
print(f"next value is: {func_poly(df_us.iloc[df_us.shape[0]-1]['y']+1, *popt)}")
plt.show()