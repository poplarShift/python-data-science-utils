from copy import deepcopy
from holoviews import Options, dim

def bokeh2mpl_markers(m):
    transl = {
        'cross': 'x',
        'square': 's',
        'diamond': 'd',
        'triangle': '<',
        'circle': 'o',
        'asterisk': '*'
        }
    if isinstance(m, str):
        return transl[m]
    elif isinstance(m, dim):
        d = deepcopy(m)
        kw = d.ops[0]['kwargs']
        kw_new = {k: {kk: bokeh2mpl_markers(vv) for kk, vv in v.items()}
            if isinstance(v, dict) else bokeh2mpl_markers(v)
            for k, v in kw.items() }
        d.ops[0]['kwargs'] = kw_new
        return d

bokeh2mpl = {
    'force': {
        'backend': ('backend', 'matplotlib'),
    },
    'all': {
        'height': None,
        'width': None,
        'shared_axes': None,
        'shared_datasource': None
    },
    'Scatter': {
        'size': 's',
        'color': 'c',
        'line_width': 'linewidth',
        'fill_color': 'facecolors',
        'marker': ('marker', bokeh2mpl_markers),
    },
    'Points': {
        'line_color': 'edgecolor',
    },
    'VLine': {
        'line_color': 'linecolor',
        'line_width': 'linewidth',
    }
}

def set_new_kwargs(k, new_value_or_fn, old_value):
    if callable(new_value_or_fn):
        k_new, v_new = k, new_value_or_fn(old_value)
    else:
        k_new, v_new = k, new_value_or_fn
    return k_new, v_new
            #
            # if callable(new_value_or_fn):
            #     print(k, v)
            #     k_new, v_new = translate_to[0], new_value_or_fn(v)
            # else:
            #     k_new, v_new = translate_to[0], new_value_or_fn



def parse_translation(lookup, k, v):
    """
    Given a lookup dictionary, translate a key-value pair.

    Parameters
    ----------
    lookup : dict
        {k: k_new} or {k: (k_new, v_new)} or {k: (k_new, lambda x: v_new)} or ...
    k : str
    v : dict value (if tuple, has to be of form (str, _))

    License
    -------
    GNU-GPL, see https://github.com/poplarShift/pyviz-recipes
    """
    translate_to = lookup[k]
    if translate_to is None:
        # eliminate kwarg
        k_new, v_new = None, None
    elif isinstance(translate_to, str):
        # translate kwarg, keep value
        k_new, v_new = translate_to, v
    elif isinstance(translate_to, tuple):
        # translate kwarg, set new value
        new_value_or_fn = translate_to[1]
        k_new, v_new = set_new_kwargs(translate_to[0], translate_to[1], v)
    else:
        # keep old key, translate only value
        k_new, v_new = set_new_kwargs(k, translate_to, v)
    return k_new, v_new

def update(name, kwargs, lookup, force={}):
    """
    Given kwargs, translate its key-value pairs using lookup
    and force them using dict `force`, as applicable.

    Parameters
    ----------
    name : str (e.g. 'Scatter')
    kwargs : dict
    lookup : dict
    force : dict, optional

    License
    -------
    GNU-GPL, see https://github.com/poplarShift/pyviz-recipes
    """
    updates = {}
    for k, v in kwargs.items():
        if k in lookup:
            # needs translation
            k_new, v_new = parse_translation(lookup, k, v)
            if k_new is not None:
                updates[k_new] = v_new
        else:
            updates[k] = v
    for k, v in force.items():
        k_new, v_new = parse_translation(force, k, v)
        if k_new is not None:
            updates[k_new] = v_new
    return updates

def translate_options(options, dictionaries=bokeh2mpl, override={}):
    """
    Translate a list of holoviews options using a given appropriate dictionaries.

    Parameters
    ----------
    options : list
        of `Options` objects
    dictionaries : dict of dicts
        Translations to be applied as needed
    override : dict of dicts
        overrides everything else

    License
    -------
    GNU-GPL, see https://github.com/poplarShift/pyviz-recipes
    """
    options_new = []
    for o in options:
        name_full = o.key
        name = name_full.split('.')[0]
        kwargs_new = update(name,
                            o.kwargs,
                            {**dictionaries['all'],
                             **dictionaries.get(name, {})
                            },
                            force={**dictionaries['force'],
                                   **override.get(name, {})}
                           )
        o_new = Options(o.key, **kwargs_new)
        options_new.append(o_new)
    return options_new
