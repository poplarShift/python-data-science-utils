import numpy as np
import pandas as pd
import functools
from shapely.geometry import Point
import geopandas as gpd
from fiona.crs import from_epsg

def date_range_with_fix(*args, fixed_date, **kwargs):
    """
    Force pandas' date_range function to contain a specific date
    by snapping to the closest date.

    Parameters
    ----------
    fixed_date : Anything that can be consumed by pd.Timestamp
    Other args: Anything else that goes into pd.date_range
    """
    t = pd.date_range(*args, **kwargs)

    diff = t - pd.Timestamp(fixed_date)

    idx = np.abs(diff).argmin()
    offset = diff[idx]

    return t - offset

def with_df_as_numeric(func):
    """
    Decorator to handle a temporary conversion from and back to potentially
    non-numeric columns. Enables arithmetic operations on datetime columns.

    Usage
    -----
    ```
    with_df_as_numeric(
        lambda d: d.groupby('CYCLE_NUMBER', as_index=False)[['LONGITUDE', 'LATITUDE', 'JULD']].mean(),
    )(df, 'JULD')
    ```
    """
    @functools.wraps(func)
    def wrapper(df, columns):
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
    """
    df = gpd.GeoDataFrame(df).copy()
    df['geometry'] = [Point(x, y) for x, y in zip(df[lon], df[lat])]
    df.crs = from_epsg(4326)
    return df
