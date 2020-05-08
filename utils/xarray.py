import numpy as np
import xarray as xr
import pandas as pd

def apply_1d(over_da, func, dim, **kwargs):
    """
    For those occasions where you'd think that ds.reduce() should do the trick,
    but you somehow don't have a function that already handles ndarrays.

    Parameters
    ----------
    over_da : xarray DataArray or list thereof
    func : Function that can handle a 1-dimensional ndarray
    dim : Dimension over which to apply func

    Usage
    -----
    e.g.: apply_1d(da, ols, dim='Depth', param='slope')

    License
    -------
    GNU-GPLv3, (C) A. Randelhoff
    (https://github.com/poplarShift/python-data-science-utils)
    """
    if not isinstance(over_da, list):
        over_da = [over_da]

    da_dropped = over_da[0].isel({dim: 0}).drop(dim)
    dims = da_dropped.coords.dims

    results = np.nan * da_dropped
    for idx, _ in np.ndenumerate(da_dropped):
        sel_dict = {c: i for c, i in zip(dims, idx)}
        res = func(
            *(da[sel_dict] for da in over_da),
            **kwargs
        )
        # print(res)
        results[sel_dict] = res
    return results

def ols(da, param='slope'):
    """
    Apply statsmodel's OLS regression to a 1d DataArray.
    Handles datetimes (in that case, regression is against days).

    Parameters
    ----------
    data : xarray DataArray
    str, one of ['slope', 'intercept', 'slope_pvalue',
        'intercept_pvalue', 'slope_se', 'intercept_se',]
        sought-after regression parameter

    Notes
    -----
    https://www.statsmodels.org/dev/generated/statsmodels.regression.linear_model.OLS.html

    License
    -------
    GNU-GPLv3, (C) A. Randelhoff
    (https://github.com/poplarShift/python-data-science-utils)
    """
    import statsmodels.api as sm

    data = da.dropna(dim=da.dims[0])

    # specify function with which to retrieve sought-after
    # parameter from statsmodels RegressionResultsWrapper
    res_fn = {
        'intercept': lambda res: res.params[0],
        'slope': lambda res: res.params[1],
        'intercept_pvalue': lambda res: res.pvalues[0],
        'slope_pvalue': lambda res: res.pvalues[1],
        'intercept_se': lambda res: res.bse[0],
        'slope_se': lambda res: res.bse[1],
    }

    if len(data)>=2:
        y = data.values
        xdata = data[data.dims[0]]
        if xdata.dtype.kind in ['M']:
            x = xdata.astype(float).values/1e9/86400.
        else:
            x = xdata.values
        ols = sm.OLS(y, sm.add_constant(x))
        res = ols.fit()
        return res_fn[param](res)
    else:
        return np.nan


# implement precision for uniqueness?
# np.round(12.3456789, decimals=4)

# np.unique(ds.longitude.isel(profile_id=0))[2]

def get_unique(x, axis=0):
    """
    Return unique non-nan value along specified xarray axis.
    Use this to squeeze out dimensions with length>1.

    Raises
    ------
    ValueError: if there are more than one non-nan values

    Usage
    -----
    ds.reduce(get_unique, dim=some_dim)

    License
    -------
    GNU-GPLv3, (C) A. Randelhoff
    (https://github.com/poplarShift/python-data-science-utils)
    """
    is_obj = x.dtype.char == 'O'
    is_dt = np.issubdtype(x.dtype, np.datetime64)
    x_ = np.moveaxis(x, source=axis, destination=-1)
    iteridx = x_.shape[:-1]
    if is_dt:
        u = np.zeros(iteridx, dtype=x.dtype)
    elif is_obj:
        u = np.zeros(iteridx, dtype=x.dtype)
    else: # numeric
        u = np.nan*np.zeros(iteridx)

    if not isinstance(u, np.ndarray):
        # if iteridx was empty tuple
        u = np.array(u)

    isnull = lambda x: pd.isnull(x) | (x == '')

    for i in np.ndindex(iteridx):
        u_1dim = np.unique(x_[i])
        u_non_null = u_1dim[~isnull(u_1dim)]
        if len(u_non_null)==1:
            u[i] = u_non_null[0]
        elif isnull(u_1dim[0]):
            if is_dt:
                u[i] = np.datetime64('NaT')
            elif is_obj:
                u[i] = ''
            else:
                u[i] = np.nan
        else:
            raise ValueError(f'Non-unique slices encountered at {i}!')
    return u
