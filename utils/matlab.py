import datetime as dt
import numpy as np

def matlab2datetime(matlab_datenum):
    if np.isnan(matlab_datenum):
        return np.NaN
    else:
        day = dt.datetime.fromordinal(int(matlab_datenum))
        dayfrac = dt.timedelta(days=matlab_datenum%1) - dt.timedelta(days = 366)
        return day + dayfrac
