import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
import pandas as pd
import os
from glob import glob
import datetime

def func(x, a, b, c):
    return a * np.exp(-b * x) + c

def func_poly_four(x, a, b, c, d, e):
    return a * np.power(x, 4) + b * np.power(x, 3) + c * np.power(x, 2) + d * x + e

def func_poly(x, a, b, c, d):
    return a * np.power(x, 3) + b * np.power(x, 2) + c * x + d

START_DATE = datetime.datetime.now().date() - datetime.timedelta(days=15)
END_DATE = START_DATE + datetime.timedelta(days=14)

df = pd.read_csv('csse-confirmed.csv')
df.rename(columns={'Country/Region':'Country'}, inplace=True)
df = pd.melt(df, id_vars=["Country","Lat", "Long", "Province/State"], var_name="Date", value_name="Confirmed")
df['Date'] = pd.to_datetime(df['Date']) 
aggregation_functions = {'Lat': 'mean', 'Long': 'mean', 'Confirmed': 'sum'}
df = df.groupby(['Country', 'Date']).aggregate(aggregation_functions)
df = df.reset_index()
df.index = df['Date']
df.drop('Date', axis=1, inplace=True)
df['x'] = (df.index - pd.to_datetime(START_DATE)).days
#df['x'] = (df['Date'] - pd.to_datetime(START_DATE)).days
#filtered_df = df.loc[START_DATE:END_DATE]
date_range = pd.date_range(START_DATE, END_DATE) 
filtered_df = df[df.index.isin(date_range)]
grouped = filtered_df.groupby('Country')
formulas = {}
for name, group in grouped: # do stuff.
    df_us = group
    ydata = df_us['Confirmed'].to_numpy()
    xdata = df_us['x'].to_numpy()
    popt, pcov = curve_fit(func_poly, xdata, ydata)
    formulas[name] = {'confirmed':ydata, 'x':xdata, 'popt': popt, 'err': np.sqrt(np.diag(pcov))}
    # print(f"{name}: {np.sqrt(np.diag(pcov))}")
    # plt.plot(xdata, ydata, 'b-', label='data')
    # plt.plot(np.linspace(-6,21), func_poly(np.linspace(-6,21), *popt), 'r-', label='fit: a=%5.3f, b=%5.3f, c=%5.3f, d=%5.3f' % tuple(popt))
    # print(popt)
    # print(f"today's value is: {df_us.iloc[df_us.shape[0]-1]['Confirmed']}")
    # print(f"next value is: {func_poly(df_us.iloc[df_us.shape[0]-1]['x']+1, *popt)}")
    # print(f"next value is: {func_poly(df_us.iloc[df_us.shape[0]-1]['x']+2, *popt)}")
    # print(f"next value is: {func_poly(df_us.iloc[df_us.shape[0]-1]['x']+3, *popt)}")
    # print(f"next value is: {func_poly(df_us.iloc[df_us.shape[0]-1]['x']+4, *popt)}")
    # plt.show()
for country in formulas:
    if country == "US":
        current = formulas[country]
        today_x = 14
        print(f"COUNTRY: {country}\nerror:{abs(1.0-((func_poly(today_x, *(current['popt'])))/(current['confirmed'][-1])))}")
        print(f"yesterday's value: {current['confirmed'][-1]}")
        print(f"today's estimate: {func_poly(today_x, *(current['popt']))}")
        plt.plot(np.linspace(-6,21), func_poly(np.linspace(-6,21), *(current['popt'])), 'r-', label='fit: a=%5.3f, b=%5.3f, c=%5.3f, d=%5.3f' % tuple(popt))
        plt.plot(current['x'], current['confirmed'], 'b-', label='data')
        plt.show()
        
