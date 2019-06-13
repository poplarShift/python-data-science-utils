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
