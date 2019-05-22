from .switch_backend import *


import holoviews as hv
import pandas as pd
import numpy as np
import param

def get_kdim_legend(layout, kdim_opts, hw={'width':150, 'height': 250},
                    defaults={'color': 'k', 'line_width':7, 'alpha':1, 'size':6}):
    raise NotImplementedError('copy over from notebook')

### SEGMENTS element

from holoviews.plotting.bokeh.chart import line_properties, fill_properties
from holoviews.plotting.bokeh.element import ColorbarPlot
from holoviews.element.geom import Geometry
from holoviews import Store, Dimension
from holoviews.core.util import max_range

class SegmentPlot(ColorbarPlot):
    """
    Segments are lines in 2D space where each two each dimensions specify a
    (x, y) node of the line.
    """
    style_opts = line_properties + ['cmap']

    _nonvectorized_styles = ['cmap']

    _plot_methods = dict(single='segment')

    def get_data(self, element, ranges, style):
        # Get [x0, y0, x1, y1]
        x0idx, y0idx, x1idx, y1idx = (
            (1, 0, 3, 2) if self.invert_axes else (0, 1, 2, 3)
        )

        # Compute segments
        x0s, y0s, x1s, y1s = (
            element.dimension_values(x0idx),
            element.dimension_values(y0idx),
            element.dimension_values(x1idx),
            element.dimension_values(y1idx)
        )

        data = {'x0': x0s, 'x1': x1s, 'y0': y0s, 'y1': y1s}
        mapping = dict(x0='x0', x1='x1', y0='y0', y1='y1')
        return (data, mapping, style)

    def get_extents(self, element, ranges, range_type='combined'):
        """
        Use first two key dimensions to set names, and all four
        to set the data range.
        """
        kdims = element.kdims
        # loop over start and end points of segments
        # simultaneously in each dimension
        for kdim0, kdim1 in zip([kdims[i].name for i in range(2)],
                                [kdims[i].name for i in range(2,4)]):
            new_range = {}
            for kdim in [kdim0, kdim1]:
                # for good measure, update ranges for both start and end kdim
                for r in ranges[kdim]:
                    # combine (x0, x1) and (y0, y1) in range calculation
                    new_range[r] = max_range([ranges[kd][r]
                                              for kd in [kdim0, kdim1]])
            ranges[kdim0] = new_range
            ranges[kdim1] = new_range
        return super(SegmentPlot, self).get_extents(element, ranges, range_type)



class Segments(Geometry):
    """
    Segments represent a collection of lines in 2D space.
    """
    group = param.String(default='Segments', constant=True)

    kdims = param.List(default=[Dimension('x0'), Dimension('y0'),
                                Dimension('x1'), Dimension('y1')],
                       bounds=(4, 4), constant=True, doc="""
        Segments represent lines given by x- and y-
        coordinates in 2D space.""")


hv.Store.register({Segments: SegmentPlot}, 'bokeh')
hv.Store.set_current_backend('bokeh')
# works too:
# options = Store.options(backend='bokeh')
# options.Segments = hv.Options('style')

### BIN AVERAGE

import param
class bin_average(hv.Operation):
    """
    Computes mean and standard deviations for bins given by their edges.

    Parameters
    ----------
    bins: Iterable
    """
    bins = param.List(doc='Bin edges.')

    def _process(self, element, key=None):
        x, y = (element.dimension_values(i) for i in range(2))
        x_dim, y_dim = (element.dimensions()[i] for i in range(2))

        bins = np.array(self.p.bins)
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

class pimped_bin_average(hv.Operation):
    """
    Computes mean and standard deviations for bins given by their edges.

    Parameters
    ----------
    bins: Iterable
    """
    bins = param.List(doc='Bin edges.')

    groupby = param.String(default=None, allow_None=True,
        doc='Extra key dimension to group by.')

    # collapse = param.String(default=None,
    #     doc="""Extra key dimension to collapse into the bins.
    #     At least one of collapse and binby has to be given.""")

    binby = param.String(default=None, allow_None=True,
        doc="""Key dimension to bin by bins. At least one of
        collapse and binby has to be given if len(kdims)>1.""")

    def _compute_bin_average(self, bins, x, y):
        x_avg = bins[:-1] + np.diff(bins)/2
        y_avg, y_std = (np.nan*np.zeros(len(x_avg)) for i in range(2))
        for k, lo, hi in zip(range(len(x_avg)), bins[:-1], bins[1:]):
            y_sel = y[(lo<x) & (x<=hi)]
            y_avg[k] = np.nanmean(y_sel)
            y_std[k] = np.nanstd(y_sel)
        return (x_avg, np.array(y_avg), np.array(y_std))

    def _process(self, element, key=None):
        dims = element.dimensions()
        xi = dims.index(hv.Dimension(self.p.binby))
        yi = xi + 1
        # x, y = (element.dimension_values(i) for i in [xi, yi])
        x_dim, y_dim = (element.dimensions()[i] for i in [xi, yi])
        df = element.dframe()
        x, y = df[x_dim.name], df[y_dim.name]
        bins = self.p.bins
        if isinstance(bins[0], pd.Timestamp):
            bins = bins.to_numpy()

        if self.p.groupby:
            errors = dict()
            groupby = self.p.groupby
            # gi = dims.index(hv.Dimension(groupby))
            # groups = element.dimension_values(gi)
            groups = df[groupby].values
            for group in groups:
                # this part written without pandas .loc b/c I'll want to avoid it
                idx = groups == group
                errors[group] = dict(zip(
                    [x_dim.name, y_dim.name, 'yerror'],
                    self._compute_bin_average(bins, x[idx], y[idx])
                ))
            return hv.HoloMap({g:
                hv.ErrorBars(e, x_dim, [y_dim, 'yerror'])
                for g, e in errors.items()
            })
        else:
            errors = dict(zip(
                [x_dim.name, y_dim.name, 'yerror'],
                self._compute_bin_average(bins, x, y)
            ))
            print(errors)
            # return element.clone(errors, new_type=hv.ErrorBars)
            return hv.ErrorBars(errors, x_dim, [y_dim, 'yerror'])

### REGRESSION element
from holoviews.core import Store
from holoviews.core.options import Compositor
from holoviews.operation import gridmatrix

from holoviews.core.util import datetime_types

class regression(hv.Operation):
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


from holoviews.plotting.bokeh import CurvePlot

#unsure if necessary?
class Regression(hv.Curve):

    group = param.String(default='Regression')

class RegressionPlot(CurvePlot):
    """
    RegressionPlot visualizes a distribution of values as a KDE.
    """

hv.Store.register({Regression: RegressionPlot}, 'bokeh')

Compositor.register(Compositor("Regression", regression, None,
                               'data', transfer_options=True,
                               transfer_parameters=True,
                               output_type=hv.Curve,
                               backends=['bokeh', 'matplotlib']))


# ---------------------------------

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
