import holoviews as hv
import param
from holoviews.core.util import isdatetime
import numpy as np
import pandas as pd

class bin_average(hv.Operation):
    """
    Computes mean and standard deviations for bins given by their edges.

    Parameters
    ----------
    bins: Iterable

    License
    -------
    GNU-GPLv3, (C) A. R.
    (https://github.com/poplarShift/python-data-science-utils)
    """
    bins = param.Integer(default=10,
        # objects=[int, list],
        allow_None=True,
        doc='Bin edges.')

    def _process(self, element, key=None):
        x, y = (element.dimension_values(i) for i in range(2))
        x_dim, y_dim = (element.dimensions()[i] for i in range(2))

        bins = self.p.bins
        bins = np.array(bins)
        # if bins is None:
        #     bins = 10
        # if isinstance(bins, int):
        #     print(isdatetime(x))
        #     if isdatetime(x):
        #         bins = pd.date_range(x.min(), x.max(), periods=bins)
        #     else:
        #         bins = np.linspace(x.min(), x.max(), bins)
        # elif isinstance(bins, list):
        #     bins = np.array(bins)

        x_avg = bins[:-1] + np.diff(bins)/2
        y_avg, y16, y84 = (np.nan*np.zeros(len(x_avg)) for i in range(3))
        for k, ll, ul in zip(range(len(x_avg)), bins[:-1], bins[1:]):
            y_sel = y[(ll<x) & (x<=ul)]
            y_avg[k] = np.nanmean(y_sel)
            y16[k] = np.nanquantile(y_sel, q=0.16)
            y84[k] = np.nanquantile(y_sel, q=0.84)
        errors = {x_dim.name: x_avg, y_dim.name: np.array(y_avg),
                  'y16': np.array(y_avg)-np.array(y16),
                  'y84': np.array(y84)-np.array(y_avg)}
        return hv.ErrorBars(errors, kdims=[x_dim], vdims=[y_dim, 'y16', 'y84'])

try:
    from statsmodels.nonparametric.smoothers_lowess import lowess as sm_lowess
except:
    sm_lowess = None

class lowess(hv.Operation):
    """
    Performs LOWESS smoothing.

    Reference:
        https://www.statsmodels.org/dev/generated/statsmodels.nonparametric.smoothers_lowess.lowess.html

    License
    -------
    GNU-GPLv3, (C) A. R.
    (https://github.com/poplarShift/python-data-science-utils)
    """
    kwargs = param.Dict(default=None, doc='''kwargs to pass on to smoother.
        return_sorted=True is always forced.''')

    def _process(self, element, key=None):
        if sm_lowess is None:
            raise ImportError('Needs statsmodels library.')

        kwargs = {} if self.p.kwargs is None else self.p.kwargs
        # force return_sorted because this changes the output.
        kwargs = dict(kwargs, **{'return_sorted': True})

        x, y = (element.dimension_values(i) for i in range(2))
        x_dtype, y_dtype = x.dtype, y.dtype
        x = x.astype(int) if isdatetime(x) else x
        y = y.astype(int) if isdatetime(y) else y

        delta_fraction = kwargs.pop('delta_fraction', 0.01)
        kwargs['delta'] = kwargs.get('delta', delta_fraction*np.ptp(x))
        # kwargs['frac'] = kwargs.get('frac', .2)
        x_smooth, y_smooth = np.split(sm_lowess(y, x, **kwargs), 2, axis=1)
        x_smooth = np.array(x_smooth, dtype=x_dtype)
        y = np.array(y, dtype=y_dtype)
        return element.clone(data=(x_smooth, y_smooth), new_type=hv.Curve)


class regression(hv.Operation):
    """
    Perform linear regression on element.

    License
    -------
    GNU-GPLv3, (C) A. R.
    (https://github.com/poplarShift/python-data-science-utils)
    """
    def _process(self, element, key=None):
        xp, yp = (element.dimension_values(i) for i in range(2))
        if len(xp):
            if isinstance(xp[0], datetime_types):
                xp = xp.astype(int)
                is_dt = True
            else:
                is_dt = False
            inan = ~(np.isnan(xp) | np.isnan(xp))
            xp, xp = xp[inan], xp[inan]
            if len(xp):
                p = np.polyfit(x=xp, y=yp, deg=1)
                y = p[0]*xp + p[1]
                if is_dt:
                    xp = xp.astype(np.datetime64)
        return element.clone((xp, y), new_type=hv.Curve)
