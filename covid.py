import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
import pandas as pd
import os
from glob import glob
import growth_functions
import datetime

START_DATE = datetime.datetime.now().date() - datetime.timedelta(days=15)
END_DATE = START_DATE + datetime.timedelta(days=14)
GRAPH_SHAPE = growth_functions.poly_three

# Reading CSV
df = pd.read_csv('csse-confirmed.csv')

#Cleaning up of columns
df.rename(columns={'Country/Region':'Country'}, inplace=True)
df = pd.melt(df, id_vars=["Country","Lat", "Long", "Province/State"], var_name="Date", value_name="Confirmed")
df['Date'] = pd.to_datetime(df['Date']) 

# Merging states into countries
aggregation_functions = {'Lat': 'mean', 'Long': 'mean', 'Confirmed': 'sum'}
df = df.groupby(['Country', 'Date']).aggregate(aggregation_functions)

# Prepare for iterations
df = df.reset_index()
df.index = df['Date']
df.drop('Date', axis=1, inplace=True)
df['x'] = (df.index - pd.to_datetime(START_DATE)).days
date_range = pd.date_range(START_DATE, END_DATE) 
filtered_df = df[df.index.isin(date_range)]
grouped = filtered_df.groupby('Country')
formulas = {}

# Preparing poly formula for each country
for name, group in grouped:
    df_us = group
    ydata = df_us['Confirmed'].to_numpy()
    xdata = df_us['x'].to_numpy()
    popt, pcov = curve_fit(GRAPH_SHAPE, xdata, ydata)
    formulas[name] = {'confirmed':ydata, 'x':xdata, 'popt': popt, 'err': np.sqrt(np.diag(pcov))}

# Display Stuff
for country in formulas:
    if country == "US":
        current = formulas[country]
        today_x = 15
        print(f"COUNTRY: {country}\nerror:{abs(1.0-((GRAPH_SHAPE(today_x, *(current['popt'])))/(current['confirmed'][-1])))}")
        print(f"yesterday's value: {current['confirmed'][-1]}")
        print(f"today's estimate: {GRAPH_SHAPE(today_x, *(current['popt']))}")
        plt.plot(np.linspace(-6,21), GRAPH_SHAPE(np.linspace(-6,21), *(current['popt'])), 'r-', label='fit: a=%5.3f, b=%5.3f, c=%5.3f, d=%5.3f' % tuple(popt))
        plt.plot(current['x'], current['confirmed'], 'b-', label='data')
        plt.show()
