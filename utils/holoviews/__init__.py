from .switch_backend import *
from .element import *
from .operation import *

from functools import reduce

import holoviews as hv
import pandas as pd
import numpy as np
import param

### make faceted legends

def get_kdim_legend(layout, kdim_opts, hw={'width':150, 'height': 250},
                    defaults={'color': 'k', 'line_width':7, 'alpha':1, 'size':6}):
    raise NotImplementedError('copy over from notebook')

### Add datetime accessor to dim transforms:

# some pandas source code to try and implement dt as accessor class on dim...
# https://github.com/pandas-dev/pandas/blob/master/pandas/core/indexes/accessors.py
# from pandas.core.arrays import DatetimeArray
# from pandas.core.accessor import delegate_names
#
# @delegate_names(delegate=DatetimeArray,
#                 accessors=DatetimeArray._datetimelike_ops,
#                 typ="property")

def _dt(self, attr='month'):
    def get_dt(x, attr):
        # allowed = [attr for attr in dir(a.dt) if not attr.startswith('_')]
        return getattr(pd.Series(x).dt, attr).values
    return dim(self, get_dt, attr)

hv.dim.dt = _dt

### FLATTEN

def flatten(l):
    """
    Collapse data of a dimensioned container one level down
    """
    target = l.traverse()[1]
    return target.clone(data=l.dframe())

### extract all data from object

_sanitize_units = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻μ", "0123456789-u")
_sanitize_units.update({176: 'deg'}) # degree symbol

def _create_column_header(d):
    """
    Convert hv.Dimension into descriptive string
    """
    s = d.label
    if d.unit is not None:
        s += '_' + d.unit
    return s.translate(_sanitize_units).replace(' ', '_')

def _to_dframe(e):
    translate_dimensions_dict = {
            d.name: _create_column_header(d)
            for d in e.dimensions() if d.label is not None
        }
    dims = [d.name for d in e.dimensions()[:2]]
    df = e.dframe().dropna(subset=dims, how='any')
    # df = df.assign(Element=e.group)
    return df.rename(columns=translate_dimensions_dict)

def get_all_data(obj):
    """
    Produce pandas DataFrame from any holoviews object.
    """

    df_list = obj.traverse(fn=_to_dframe, specs=lambda x: not x._deep_indexable)
    # specs=lambda x: hasattr(x, 'dframe')
    # too permissive, both nd containers and elements have it

    # do not separate between frames for now, in principle each dimension
    # should be unique w/r/t values they represent...
    # df_list = [df.assign(Frame=i) for i, df in enumerate(df_list)]

    return reduce(lambda df1, df2: df1.merge(df2, how='outer'), df_list)

### aggregate & compare vdims over a number of elements

import holoviews.operation.datashader as hd
import datashader as dsh

# import numpy as np, datashader as sh, xarray as xr
# from datashader import transfer_functions as tf
# import reductions as rd

def agg_vdims(elements, vdims=None, N=100):
    """
    Spatially aggregate vdims from a number of holoviews Elements.

    Parameters:
    -----------
    elements : list
        List of holoviews Elements
    vdims : list
        List of vdim names over which to aggregate for each Element
    N : int
        Number of bins (in each kdim) to aggegrate
    """
    data = []
    kdims0 = [kd.name for kd in elements[0].kdims]
    for k, e in enumerate(elements):
        if vdims is None:
            vdim = e.vdims[0].name
        else:
            vdim = vdims[k]
        kdims = [kd.name for kd in e.kdims]
        dims = [d.name for d in e.dimensions()]
        data.append(
            e.data[dims].rename(columns={kd: kd0 for kd, kd0 in zip(kdims, kdims0)}).copy()
        )

    df = pd.concat(data, sort=False).dropna(how='all')
    for kd in kdims0:
        df[kd] = pd.IntervalIndex(pd.cut(df[kd], bins=N)).mid
    return df.groupby(kdims0).mean()
