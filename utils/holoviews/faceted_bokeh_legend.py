from itertools import product
from copy import deepcopy

import holoviews as hv
from holoviews import opts

def faceted_legend_opts(kdim_opts):
    """
    Cycle across all combinations of styling options and return the holoviews `opts` object.

    TO DO: exclude variations that don't exist in the data

    License
    -------
    GNU-GPLv3, (C) A. R.
    (https://github.com/poplarShift/python-data-science-utils)
    """
    options = (list(l) for l in zip(*product(*(list(x.values())[0] for x in kdim_opts.values()))))
    options = {list(k.keys())[0]: hv.Cycle(v) for k, v in zip(kdim_opts.values(), options)}
    return options

def faceted_legend(layout, kdim_opts, hw={'width':150, 'height': 250},
                    defaults={'color': 'k', 'line_width':7, 'alpha':1, 'size':100}):
    """
    Create a legend where each tuple of legend entries corresponds to the style variations across one kdim at a time.

    Parameters
    ----------
    layout : A Holoviews container of different elements
    kdim_opts : dict
        In the form {kdim: {property: [styles]}}
    hw : dict
        Set maximum height and width of legend
    defaults : dict
        Set defaults for the styling of the options that are not varied for a specific kdim

    License
    -------
    GNU-GPLv3, (C) A. R.
    (https://github.com/poplarShift/python-data-science-utils)
    """
    need_defaults_for = [list(d.keys())[0] for d in list(kdim_opts.values())]
    other_kdim_defaults = {k:v for k, v in defaults.items() if k in need_defaults_for}
    def get_single_legend(layout, kdim_opts, kdim):
        """
        Create the portion of a legend pertaining to a single kdim.
        """
        other_kdims = [kd.name for kd in layout.kdims if kd.name!=kdim]
        l = deepcopy(layout).drop_dimension(other_kdims)
        return l.opts(
            getattr(opts, type(l).name)(xaxis=None, yaxis=None, legend_position='top_left',
                                        show_frame=False, **hw),
            getattr(opts,  l.type.name)(**{**other_kdim_defaults,
                                           **{k: hv.Cycle(v) for k, v in kdim_opts[kdim].items()}}),
          ).map(lambda x: x.iloc[:0], l.type)

    return hv.Overlay([get_single_legend(layout, kdim_opts, kdim)
                       for kdim in kdim_opts.keys()])
