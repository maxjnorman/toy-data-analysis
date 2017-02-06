# -*- coding: utf-8 -*-
"""
Created on Mon Feb  6 12:07:40 2017

@author: maxjn
"""
import pandas as pd

def build_transaction_dataframe(xls_loc, sheet_number):
    xls_file = pd.ExcelFile(xls_loc)
    worksheet = xls_file.sheet_names[sheet_number]
    data_frame = xls_file.parse(worksheet)
    if data_frame.empty:
        return None
    else:
        pass
    data_frame.columns = [
        'trans_date',
        'description',
        'money_in',
        'money_out',
        'balance',
    ]
    data_frame = data_frame.fillna(0.00)
    data_frame['net_input'] = data_frame['money_in'] - data_frame['money_out']
    data_frame['month_dates'] = [
        month_date.replace(day=1)
        for month_date
        in data_frame['trans_date'].tolist()
    ]
    unique_months = list(data_frame['month_dates'].drop_duplicates())
    return data_frame, unique_months
