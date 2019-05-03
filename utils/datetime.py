import datetime as dt
import numpy as np

def matlab2datetime(matlab_datenum):
    day = dt.datetime.fromordinal(int(matlab_datenum))
    dayfrac = dt.timedelta(days=matlab_datenum%1) - dt.timedelta(days = 366)
    return day + dayfrac

def datetime2doy(datetime):
    doys = np.zeros_like(np.array(datetime))
    for k in range(len(doys)):
        y0=datetime[k].year
        datetime_startofyear=dt.datetime(year=y0, month=1, day=1)
        doys[k] = (datetime[k] - datetime_startofyear)/dt.timedelta(days=1)
    return doys

def hrssince2datetime(hrs,epoch):
    return epoch + dt.timedelta(hours=1) * hrs

import pandas as pd


def date2doy(date, format='%Y%m%d'):
    date = pd.to_datetime(date, format=format)
    new_year_day = pd.Timestamp(year=date.year, month=1, day=1)
    return (date - new_year_day).days + 1

# if __name__ == '__main__':
#     print(date_to_nth_day('20170201'))
