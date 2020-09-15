import numpy as np
import pandas as pd
import functools
from shapely.geometry import Point
import geopandas as gpd
from fiona.crs import from_epsg

def decimal_day_of_year(times, wrap=True):
    """
    Convert pandas datetime series into decimal days of the year.

    Notes
    -----
        January 1 at noon corresponds to ddoy=0.5.

        wrap=True calculates day of the year for each year separately.
        wrap=False counts days from the earliest date in the series. Pay attention to
        leap years if you do so.
    """
    datatype = type(times)

    if wrap:
        ddoys = []
        for year in times.dt.year.unique():
            times_this_year = [t for t in times if t.year == year]
            ddoys += list(decimal_day_of_year(datatype(times_this_year), wrap=False))
        ddoys = datatype(ddoys)
    else:
        # First day of the earliest year in time series.
        epoch = pd.Timestamp(year=times.min().year, month=1, day=1)
        ddoys = (times - epoch)/pd.Timedelta(days=1)

    return ddoys


def bin_series(s, bins):
    """
    Sort pandas series into bins, labelling them by each bin's midpoint.

    Parameters
    ----------
    s: pandas Series
    bins: bins argument to pd.cut

    License
    -------
    GNU-GPLv3, (C) A. R.
    (https://github.com/poplarShift/python-data-science-utils)
    """
    labels = np.diff(bins)/2 + bins[:-1]
    return pd.to_numeric(pd.cut(s, bins=bins, labels=labels))

def date_range_with_fix(*args, fixed_date, **kwargs):
    """
    Force pandas' date_range function to contain a specific date
    by snapping to the closest date.

    Parameters
    ----------
    fixed_date : Anything that can be consumed by pd.Timestamp
    Other args: Anything else that goes into pd.date_range

    License
    -------
    GNU-GPLv3, (C) A. R.
    (https://github.com/poplarShift/python-data-science-utils)
    """
    t = pd.date_range(*args, **kwargs)

    diff = t - pd.Timestamp(fixed_date)

    idx = np.abs(diff).argmin()
    offset = diff[idx]

    return t - offset

def with_df_as_numeric(func):
    """
    Decorator to handle a temporary conversion from and back to potentially
    non-numeric columns. Enables e.g. arithmetic operations on datetime columns.

    Usage
    -----
    ```
    with_df_as_numeric(
        lambda d: d.groupby('CYCLE_NUMBER', as_index=False)[['LONGITUDE', 'LATITUDE', 'JULD']].mean(),
    )(df, 'JULD')
    ```

    License
    -------
    GNU-GPLv3, (C) A. R.
    (https://github.com/poplarShift/python-data-science-utils)
    """
    @functools.wraps(func)
    def wrapper(df, columns):
        df = df.copy()
        # convert to numeric
        if isinstance(columns, str):
            columns = [columns]
        dtypes = {c: df[c].dtype for c in columns}
        for c in columns:
            df[c] = np.where(~df[c].isna(), pd.to_numeric(df[c]), np.nan)
        # do actual operation
        df = func(df)
        # convert back
        for c in columns:
            df[c] = df[c].astype(dtypes[c])
        return df
    return wrapper

def df_to_gdf(df, lon='lon', lat='lat'):
    """
    Turn pandas dataframe with latitude, longitude columns into GeoDataFrame with according Point geometry.

    Parameters
    ----------
    df : pandas dataframe
    lon, lat : names of lon, lat columns

    Returns
    -------
    geopandas geodataframe

    License
    -------
    GNU-GPLv3, (C) A. R.
    (https://github.com/poplarShift/python-data-science-utils)
    """
    df = gpd.GeoDataFrame(df).copy()
    df['geometry'] = [Point(x, y) for x, y in zip(df[lon], df[lat])]
    df.crs = from_epsg(4326)
    return df

def pandas_df_to_markdown_table(df):
    """
    Modeled on https://stackoverflow.com/a/33869154

    License
    -------
    GNU-GPLv3, (C) A. R.
    (https://github.com/poplarShift/python-data-science-utils)
    """
    fmt = ['---' for i in range(len(df.columns))]
    df_fmt = pd.DataFrame([fmt], columns=df.columns)
    df_formatted = pd.concat([df_fmt, df])
    return df_formatted.to_csv(sep="|", index=False)
