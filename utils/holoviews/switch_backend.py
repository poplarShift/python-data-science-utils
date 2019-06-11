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
            for k, v in kw.items()}
        d.ops[0]['kwargs'] = kw_new
        return d

bokeh2mpl = {
    'force': {
        'backend': 'matplotlib',
    },
    'all': {
        'height': None,
        'width': None,
        'shared_axes': None,
        'shared_datasource': None
    },
    'Scatter,Points,ErrorBars': {
        'size': 's',
        'color': 'c',
        'line_color': 'edgecolor',
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

def set_new_value(new_value_or_fn, old_value):
    """
    Either replace or transform the old value using the new value or function.
    """
    if callable(new_value_or_fn):
        return new_value_or_fn(old_value)
    else:
        return new_value_or_fn


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
    elif (
        isinstance(translate_to, tuple)
        and len(translate_to)==2
        and isinstance(translate_to[0], str)
        ):
        # translate kwarg, set new value
        k_new, v_new = translate_to[0], set_new_value(translate_to[1], v)
    else:
        # keep old key, translate only value
        k_new, v_new = k, set_new_value(translate_to, v)
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
        directly set entries as key-value pairs

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
        updates[k] = v
        # k_new, v_new = parse_translation(force, k, v)
        # if k_new is not None:
        #     updates[k_new] = v_new
    return updates

def extract_if_key_is_substr(d, name):
    """
    Parameters
    ----------
    d: dict
        where keys can be of the form 'name1,name2,...'
    name: str
        name to match
    """
    return dict(kv for k, v in d.items() if name in k.split(',')+['all']
                for kv in v.items())

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
        # lookup dictionary; look in here for keys to check whether
        # translation for a given kwarg is available
        lookup = {
            **dictionaries['all'],
            **extract_if_key_is_substr(dictionaries, name)
        }

        # presets forced on some options across all Element types:
        force1 = dictionaries['force']
        force2 = override.get('all', {})
        force3 = extract_if_key_is_substr(override, name)
        kwargs_new = update(name,
                            o.kwargs,
                            lookup,
                            force={**force1, **force2, **force3}
                           )
        o_new = Options(o.key, **kwargs_new)
        options_new.append(o_new)
    return options_new
