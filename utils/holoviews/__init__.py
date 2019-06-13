from .switch_backend import *
from .element.py import *


import holoviews as hv
import pandas as pd
import numpy as np
import param

### make faceted legends

def get_kdim_legend(layout, kdim_opts, hw={'width':150, 'height': 250},
                    defaults={'color': 'k', 'line_width':7, 'alpha':1, 'size':6}):
    raise NotImplementedError('copy over from notebook')

### Add datetime accessor to dim transforms:

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
