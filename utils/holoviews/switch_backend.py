from holoviews import Options

bokeh2mpl = {
    'force': {
        'backend': ('backend', 'matplotlib'),
    },
    'all': {
        'height': None,
        'width': None,
    },
    'Scatter': {
        'size': 's',
        'color': 'c',
        'line_width': 'markeredgewidth'
    },
    'Points': {'line_color': 'edgecolor'},
}

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
        if callable(new_value_or_fn):
            k_new, v_new = translate_to[0], new_value_or_fn(v)
        else:
            k_new, v_new = translate_to[0], new_value_or_fn
    else:
        # keep old key, translate only value
        new_value_or_fn = translate_to
        if callable(new_value_or_fn):
            k_new, v_new = k, new_value_or_fn(v)
        else:
            k_new, v_new = k, new_value_or_fn
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
        kwargs_new = update(o.key,
                            o.kwargs,
                            {**dictionaries['all'], **dictionaries[o.key]},
                            force={**dictionaries['force'],
                                   **override.get(o.key, {})}
                           )
        o_new = Options(o.key, **kwargs_new)
        options_new.append(o_new)
    return options_new
