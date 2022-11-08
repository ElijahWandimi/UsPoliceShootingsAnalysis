import numpy as np
import pandas as pd

def load_data(dt_file):
    dt = pd.read_csv(dt_file)
    return dt


# def extract_from_date(data, cols):
#     for col in cols:
#         data[col] = pd.to_datetime(data[col])
#         # for fet in ['year', 'month_name', 'day_name']:
#         data['year'] = data[col].dt.year
#         data['month'] = data[col].dt.month_name()
#         data['day_name'] = data['date'].dt.day_name()
#     return data

def convert_dtypes(data):
    for col in data.columns:
        if data[col].dtype not in ['float64', '<M8[ns]', 'bool']:
            data[col] = data[col].astype('category')
    return data

def treat_missing(data):
    for col in data.columns:
        if data[col].dtype == 'float64':
            data[col].fillna(data[col].mean(), inplace=True)
        if data[col].dtype == 'category':
            data[col].fillna(method='bfill', inplace=True)
    return data
