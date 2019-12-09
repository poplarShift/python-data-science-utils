import holoviews as hv

class StyleLink():
    """
    Class that fixes style options across holoviews elements.

    Init e.g. like so:

    sl = StyleLink(
        [
            [styling_group_A_element_1, styling_group_A_element_2],
            [styling_group_B_element_1, styling_group_B_element_2],
        ],
        {
            'line_color': hv.Cycle(['blue', 'orange', 'salmon']),
            'line_dash': hv.Cycle(['dotted', 'solid'])
        }
    )
    Elements are given as a list of lists. The hv.Cycle instances will then cycle
    through the outer level of the nested list, giving the same styling options to
    every item of the inner list nesting level.

    License
    -------
    GNU-GPLv3, (C) A. R.
    (https://github.com/poplarShift/python-data-science-utils)
    """
    def __init__(self, elements, link_options):
        self.default_options = hv.Store.options(hv.Store.current_backend)
        self.elements = elements
        self.link_options = link_options
        self.linked = list(link_options.keys())
        self.link()

    def link(self):
        elements, link_options = self.elements, self.link_options
        for k, es in enumerate(elements):
            if not isinstance(es, list):
                es = [es]
            for m, e in enumerate(es):
                etype = type(e).__name__

                opt_dict = {}
                for opt, cyc in link_options.items():
                    if cyc is None:
                        cyc = getattr(self.default_options, etype)['style'].kwargs[opt]
                    N = len(cyc.values)

                    opt_dict[opt] = cyc.values[k%N]

                elements[k][m].opts(**opt_dict)


    def unlink(self):
        elements, linked = self.elements, self.linked
        for k, es in enumerate(elements):
            if not isinstance(es, list):
                es = [es]
            for e in es:
                etype = type(e).__name__
                opt_dict = {}
                for opt in linked:
                    opt_dict[opt] = getattr(self.default_options, etype)['style'].kwargs[opt]

                e.opts(**opt_dict)
