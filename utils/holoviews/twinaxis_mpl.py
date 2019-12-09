from matplotlib.transforms import Bbox

import holoviews as hv
from holoviews import opts, Options

def save_legend_artists(plot, element):
    """
    Arguments
    ---------
    plot: Holoviews plotting class
    element: Holoviews Element

    License
    -------
    GNU-GPLv3, (C) A. R.
    (https://github.com/poplarShift/python-data-science-utils)
    """
    # register handle
    a = plot.handles['artist']
    if not hasattr(plot.handles['axis'], 'legend_artists'):
        plot.handles['axis'].legend_artists = [a]
    else:
        plot.handles['axis'].legend_artists.append(a)

    # register label
    label = element.vdims[0].label
    if not hasattr(plot.handles['axis'], 'legend_labels'):
        plot.handles['axis'].legend_labels = [label]
    else:
        plot.handles['axis'].legend_labels.append(label)

def set_twinaxis_options(l, labels_to_replace_by_yaxis_selector=None):
    """
    l: holoviews Layout
    labels_to_replace_by_yaxis_selector: holoviews Element

    License
    -------
    GNU-GPLv3, (C) A. R.
    (https://github.com/poplarShift/python-data-science-utils)
    """
    if labels_to_replace_by_yaxis_selector is None:
        labels_to_replace_by_yaxis_selector = lambda e: (
            issubclass(type(e), hv.element.Chart)
            or isinstance(e, (hv.Overlay, hv.NdOverlay))
        )
    options = []

    for el in set(l.traverse(
        lambda e: type(e).__name__,
        lambda e: (
            issubclass(type(e), hv.element.Chart)
            or isinstance(e, (hv.Overlay, hv.NdOverlay))
        ))
    ):
        option_dict = dict(
            backend='matplotlib',
            sublabel_format='',
            axiswise=True, framewise=True
        )
        options.append(Options(el, **option_dict))

    for el in set(l.traverse(
        lambda e: type(e).__name__, labels_to_replace_by_yaxis_selector)
    ):
        option_dict = dict(
            show_legend=False,
        )
        if 'Overlay' not in el:
            option_dict.update(dict(hooks=[save_legend_artists]))
        options.append(Options(el, **option_dict))

    return l.opts(*options)

def align_twinaxis(axs, offs=50):
    """
    Usage for two holoviews Overlays a and b,
    to give each their own axis:

    obj = a + b
    obj = set_twinaxis_options(obj)
    fig = hv.render(obj, backend='matplotlib')
    align_twinaxis(fig)

    License
    -------
    GNU-GPLv3, (C) A. R.
    (https://github.com/poplarShift/python-data-science-utils)
    """
    ax0, ax1 = axs[0], axs[1]

    # extents and scales
    def merge_bboxes(bbox0, bbox1):
        x0, y0, _, h = bbox0.bounds
        w = bbox1.bounds[2] + bbox1.bounds[0] - bbox0.bounds[0]
        return Bbox.from_bounds(x0, y0, w, h)

    merged_extents = merge_bboxes(*(ax.get_position() for ax in axs))
    for ax in axs:
        ax.set_position(merged_extents)

    _set_spine_position(ax1.spines['left'], ('outward', offs))

    # styling
    ax0.xaxis.set_visible(False)
    ax1.set_facecolor('none')
    for spine in ['top', 'right', 'bottom']:
        ax1.spines[spine].set_visible(False)
    ax1.xaxis.set_visible(True)
    ax1.yaxis.set_visible(True)

    # legend
    ax0.legend(ax0.legend_artists+ax1.legend_artists,
               ax0.legend_labels+ax1.legend_labels,
               bbox_to_anchor=(.95, .5)
               )

    return #merged_extents.bounds[0::2]



def _set_spine_position(spine, position):
    """
    This util function is taken from
    https://github.com/mwaskom/seaborn/blob/b9551aff1e2b020542a5fb610fec468b69b87c6e/seaborn/utils.py#L278

    Set the spine's position without resetting an associated axis.
    As of matplotlib v. 1.0.0, if a spine has an associated axis, then
    spine.set_position() calls axis.cla(), which resets locators, formatters,
    etc.  We temporarily replace that call with axis.reset_ticks(), which is
    sufficient for our purposes.

    Copyright (c) 2012-2019, Michael L. Waskom
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice, this
      list of conditions and the following disclaimer.

    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.

    * Neither the name of the project nor the names of its
      contributors may be used to endorse or promote products derived from
      this software without specific prior written permission.
    """
    axis = spine.axis
    if axis is not None:
        cla = axis.cla
        axis.cla = axis.reset_ticks
    spine.set_position(position)
    if axis is not None:
        axis.cla = cla
