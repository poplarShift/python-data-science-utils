# USAGE
# from utils.standard_imports import *

from contextlib import suppress

with suppress(ImportError):
    #BASIC

    from collections import OrderedDict
    import os
    import itertools
    from functools import reduce
    import datetime as dt
    import warnings

    # MISC

    from pysolar.solar import get_altitude
    import gsw
    from scipy.io import loadmat

    # DATA

    import pandas as pd
    import geopandas as gpd
    import numpy as np
    import xarray as xr
    # monkey patch xarray until https://github.com/pydata/xarray/pull/2917 is released
    def load_dataset(fname, **kwargs):
        with xr.open_dataset(fname, **kwargs) as ds:
            return ds.load()
    xr.load_dataset = load_dataset

    # GEO

    from fiona.crs import from_epsg

    from scipy.spatial import cKDTree

    import cartopy
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature

    import xesmf
    import shapely
    from shapely.ops import nearest_points
    from shapely.geometry import Point, MultiPoint, box, LinearRing, LineString, MultiLineString, Polygon

    ## VIZ

    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import seaborn as sns

    from bokeh.models import WMTSTileSource

    import holoviews as hv
    try:
        hv.extension('bokeh', 'matplotlib')
    except:
        pass

    from holoviews import dim, opts, Options, Dimension, Options, Cycle
    from holoviews.core.io import Pickler
    from holoviews.operation.datashader import datashade, rasterize, regrid, aggregate

    import datashader as dsh

    import hvplot.pandas
    import hvplot.xarray

    try:
        # extents=(-90, 65, -45, 78)
        bathy = gpd.read_file('/Users/doppler/database/IBCAO/IBCAO_1min.shp').set_index('contour').geometry
        # e.g. bathy200 = bathy.loc[200]
        # bathy = bathy.intersection(shapely.geometry.box(*extents))
        # bathy.crs = from_epsg(4326)
    except:
        pass


    # BOKEH STYLING

    from bokeh.themes import Theme
    theme = Theme(json={
    'attrs' : {
        'Figure' : {
    #         'background_fill_color': '#2F2F2F',
    #         'border_fill_color': '#2F2F2F',
            'outline_line_color': 'black',
            'outline_line_alpha': 1,
        },
        'Axis' : {
            'major_tick_in': 0,
            'major_tick_out': 8,
            'minor_tick_out': 4,
    #         'axis_label_standoff': 0,
            # 'axis_label_text_color': 'black',
            # 'axis_label_text_font_size': '15pt',
            'major_label_text_font_size': '13pt',
            'axis_label_text_font_style': 'normal',
        },
        'Legend': {
            'label_text_font_size': '12pt'
        },
        'Grid': {
            'grid_line_dash': [6, 4],
            'grid_line_alpha': .9,
        },
        'Title': {
    #         'text_color': 'red',
            'text_font_size': '15pt',
        },
        'ColorBar': {
            'major_label_text_font_size': '14pt',
        }
    }})
    try:
        hv.renderer('bokeh').theme = theme
    except:
        pass
