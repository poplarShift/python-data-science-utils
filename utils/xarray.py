import numpy as np
import xarray as xr
import pandas as pd

def get_unique(x, axis=0):
    """
    Return unique non-nan value along specified xarray axis.

    Raises
    ------
    ValueError: if there are more than one non-nan values

    Usage
    -----
    ds.reduce(get_unique, dim=some_dim)
    """
    is_dt = np.issubdtype(x.dtype, np.datetime64)
    x_ = np.moveaxis(x, source=axis, destination=-1)
    iteridx = x_.shape[:-1]
    u = np.zeros(iteridx, dtype=x.dtype) if is_dt else np.nan*np.zeros(iteridx)
    if not isinstance(u, np.ndarray):
        # if iteridx was empty tuple
        u = np.array(u)

    for i in np.ndindex(iteridx):
        u_ = np.unique(x_[i])
        nan_nat = pd.isnull(u_)
        uu_ = u_[~nan_nat]
        if len(uu_)==1:
            u[i] = uu_[0]
        elif pd.isnull(u_[0]):
            if is_dt:
                u[i] = np.datetime64('NaT')
            else:
                u[i] = np.nan
        else:
            raise ValueError('Non-unique slices encountered!')
    return u
