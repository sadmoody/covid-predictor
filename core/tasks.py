from scipy.optimize import curve_fit
import numpy as np
import pandas as pd
import os
from glob import glob
from core.growth_functions import poly_three
import datetime
from .models import Entry, Formula, Country
import logging

def update_stats():
    logging.debug("Setting constants")

    START_DATE = datetime.datetime.now(datetime.timezone.utc).date() - datetime.timedelta(days=14)
    END_DATE = START_DATE + datetime.timedelta(days=14)
    GRAPH_SHAPE = poly_three
    date_range = pd.date_range(START_DATE, END_DATE) 

    logging.debug("Downloading and reading latest data")
    df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')

    logging.debug("Cleaning data")
    df.rename(columns={'Country/Region':'Country'}, inplace=True)
    df = pd.melt(df, id_vars=["Country","Lat", "Long", "Province/State"], var_name="Date", value_name="Confirmed")
    df['Date'] = pd.to_datetime(df['Date']) 

    logging.debug("Aggregating states into countries")
    aggregation_functions = {'Lat': 'mean', 'Long': 'mean', 'Confirmed': 'sum'}
    df = df.groupby(['Country', 'Date']).aggregate(aggregation_functions)

    logging.debug("Preparing data for iterations")
    df = df.reset_index()
    df.index = df['Date']
    df.drop('Date', axis=1, inplace=True)
    df['x'] = (df.index - pd.to_datetime(START_DATE)).days
    grouped = df.groupby('Country')
    formulas = {}

    logging.debug("Processing...")
    for name, group in grouped:
        logging.debug(f"Processing {name}")
        
        filtered_df = group[group.index.isin(date_range)]
        ydata = filtered_df['Confirmed'].to_numpy()
        xdata = filtered_df['x'].to_numpy()
        popt, pcov = curve_fit(GRAPH_SHAPE, xdata, ydata)
        lat = group['Lat'].iloc[0]
        long = group['Long'].iloc[0]
        country_model, created = Country.objects.get_or_create(name=name, defaults={ 'lat':lat, 'long':long})
        if country_model.confirmed_formula is None:
            confirmed_formula_model = Formula.objects.create(a=popt[0],b=popt[1],c=popt[2],d=popt[3])
        else:
            confirmed_formula_model = country_model.confirmed_formula
            confirmed_formula_model.a = popt[0]
            confirmed_formula_model.b = popt[1]
            confirmed_formula_model.c = popt[2]
            confirmed_formula_model.d = popt[3]
        confirmed_formula_model.save()
        country_model.confirmed_formula = confirmed_formula_model
        
        for index, row in group.iterrows():
            filter_result = country_model.confirmed.filter(date=index.date())
            if filter_result:
                entry_model = filter_result[0]
                if (entry_model.value != row['Confirmed']):
                    entry_model.value = row['Confirmed']
                    entry_model.save()
            else:
                # Oh my god this is so slow for new entries
                entry_model = Entry.objects.create(date=index.date(), value=row['Confirmed'])
            country_model.confirmed.add(entry_model)
        country_model.t_zero = START_DATE
        country_model.save()
    
    logging.debug("Done!")