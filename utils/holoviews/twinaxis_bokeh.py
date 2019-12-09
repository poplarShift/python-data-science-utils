from functools import partial
from holoviews import opts
from bokeh.models import Range1d

def twinaxis_hook(axis, label=None, pos=None, drop_default=False, bounds=None):
    """
    Create a hook that will create another axis.

    Args:
        axis (str): One of 'x', 'y'
        label (str): The label of the axis
        pos (str): Where to place the new axis
        drop_default (bool):

    Returns:
        hook that can be used as holoviews plot option.

    Notes:
        Bokeh does apparently not allow specifying different types of Axes for
        the same dimension (e.g. mixed linear and log).

        Bokeh does also apparently not allow the new axis range to be panned/
        zoomed independently of the default y_range.

    License
    -------
    GNU-GPLv3, (C) A. R.
    (https://github.com/poplarShift/python-data-science-utils)
    """
    if axis not in ['x', 'y']:
        raise ValueError()
    idx = slice(0 if axis == 'x' else 1, None, 2)
    range = f'{axis}_range' # e.g. y_range
    extra_ranges_attr = f'extra_{axis}_ranges' # e.g. extra_y_ranges
    range_name_attr = f'{axis}_range_name' # e.g. y_range_name
    if pos is None:
        pos = 'below' if axis == 'x' else 'left'

    def make_axis(plot, element, axis, label):
        bokeh_axis = plot.handles[axis+'axis']
        if label is None:
            # not ideal b/c in an overlay holoviews makes this the ylabel
            # of the first element of the overlay...
            label = bokeh_axis.axis_label
            # label = plot.ylabel
        AxisType = type(bokeh_axis)

        p = plot.state
        # create secondary range and axis
        extents = plot.get_extents(element, None)[idx]
        range_new = Range1d(start=extents[0], end=extents[1], bounds=bounds)

        # as an aside, we could replace existing yaxis/yrange like this:
        # (won't give a twin axis though)
        # range_name = 'default'
        # plot.handles[range_name] = range_new
        if drop_default:
            plot.handles['yaxis'].visible = False

        # insert new range
        range_name = label + '_range'
        getattr(p, extra_ranges_attr).update({
            range_name: range_new
        })
        # set glyph renderer to follow the new range
        setattr(plot.handles['glyph_renderer'], range_name_attr, range_name)

        # if no axis exists yet with the given label, create one
        if not any(
            range_name == getattr(ax, range_name_attr)
            for ax in p.select(dict(type=AxisType))
        ):

            p.add_layout(
                AxisType(**{range_name_attr: range_name, 'axis_label': label}),
                pos
            )

    return partial(make_axis, axis=axis, label=label)
