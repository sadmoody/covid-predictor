from scipy.optimize import curve_fit
import numpy as np
import pandas as pd
import os
from glob import glob
from core.growth_functions import poly_three
import datetime
from .models import Entry, Formula, Country
import logging

def update_confirmed_stats():
    logging.debug("Setting constants")

    START_DATE = datetime.datetime.now(datetime.timezone.utc).date() - datetime.timedelta(days=14)
    END_DATE = START_DATE + datetime.timedelta(days=14)
    GRAPH_SHAPE = poly_three
    DEGREES = 3
    ROOT_THRESHOLD = 1.0
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
        for x in range(DEGREES,0,-1):
            coeff = np.polyfit(xdata, ydata, x)
            der_coeff = np.polyder(coeff)
            der_roots = np.roots(der_coeff)
            roots_at_end = False
            for root in der_roots:
                if np.isreal(root):
                    diff_low = abs(root - xdata[0])
                    diff_high = abs(root - xdata[len(xdata)-1])
                    if (diff_low <= ROOT_THRESHOLD or diff_high <= ROOT_THRESHOLD):
                        roots_at_end = True
            if roots_at_end:
                continue
            else:
                padded_coeff = np.pad(coeff,(DEGREES+1-len(coeff),0), constant_values=0)
                break
        lat = group['Lat'].iloc[0]
        long = group['Long'].iloc[0]
        country_model, created = Country.objects.get_or_create(name=name, defaults={ 'lat':lat, 'long':long})
        if country_model.confirmed_formula is None:
            confirmed_formula_model = Formula.objects.create(a=padded_coeff[0],b=padded_coeff[1],c=padded_coeff[2],d=padded_coeff[3])
        else:
            confirmed_formula_model = country_model.confirmed_formula
            confirmed_formula_model.a = padded_coeff[0]
            confirmed_formula_model.b = padded_coeff[1]
            confirmed_formula_model.c = padded_coeff[2]
            confirmed_formula_model.d = padded_coeff[3]
        confirmed_formula_model.save()
        country_model.confirmed_formula = confirmed_formula_model
        country_model.t_zero = START_DATE
        country_model.save()
        
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
        country_model.save()
    
    logging.debug("Done!")

def update_death_stats():
    logging.debug("Setting constants")

    START_DATE = datetime.datetime.now(datetime.timezone.utc).date() - datetime.timedelta(days=14)
    END_DATE = START_DATE + datetime.timedelta(days=14)
    GRAPH_SHAPE = poly_three
    DEGREES = 3
    ROOT_THRESHOLD = 1.0
    date_range = pd.date_range(START_DATE, END_DATE) 

    logging.debug("Downloading and reading latest data")
    df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')

    logging.debug("Cleaning data")
    df.rename(columns={'Country/Region':'Country'}, inplace=True)
    df = pd.melt(df, id_vars=["Country","Lat", "Long", "Province/State"], var_name="Date", value_name="Deaths")
    df['Date'] = pd.to_datetime(df['Date']) 

    logging.debug("Aggregating states into countries")
    aggregation_functions = {'Lat': 'mean', 'Long': 'mean', 'Deaths': 'sum'}
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
        ydata = filtered_df['Deaths'].to_numpy()
        xdata = filtered_df['x'].to_numpy()
        for x in range(DEGREES,0,-1):
            coeff = np.polyfit(xdata, ydata, x)
            der_coeff = np.polyder(coeff)
            der_roots = np.roots(der_coeff)
            roots_at_end = False
            for root in der_roots:
                if np.isreal(root):
                    diff_low = abs(root - xdata[0])
                    diff_high = abs(root - xdata[len(xdata)-1])
                    if (diff_low <= ROOT_THRESHOLD or diff_high <= ROOT_THRESHOLD):
                        roots_at_end = True
            if roots_at_end:
                continue
            else:
                padded_coeff = np.pad(coeff,(DEGREES+1-len(coeff),0), constant_values=0)
                break
        lat = group['Lat'].iloc[0]
        long = group['Long'].iloc[0]
        country_model, created = Country.objects.get_or_create(name=name, defaults={ 'lat':lat, 'long':long})
        if country_model.death_formula is None:
            death_formula_model = Formula.objects.create(a=padded_coeff[0],b=padded_coeff[1],c=padded_coeff[2],d=padded_coeff[3])
        else:
            death_formula_model = country_model.death_formula
            death_formula_model.a = padded_coeff[0]
            death_formula_model.b = padded_coeff[1]
            death_formula_model.c = padded_coeff[2]
            death_formula_model.d = padded_coeff[3]
        death_formula_model.save()
        country_model.death_formula = death_formula_model
        country_model.t_zero = START_DATE
        country_model.save()

        for index, row in group.iterrows():
            filter_result = country_model.death.filter(date=index.date())
            if filter_result:
                entry_model = filter_result[0]
                if (entry_model.value != row['Deaths']):
                    entry_model.value = row['Deaths']
                    entry_model.save()
            else:
                # Oh my god this is so slow for new entries
                entry_model = Entry.objects.create(date=index.date(), value=row['Deaths'])
            country_model.death.add(entry_model)
        country_model.save()
    
    logging.debug("Done!")