import os
from holoviews import render
from bokeh.io import export_svgs
from bokeh.plotting.figure import Figure

def save_bokeh_svg(obj, fname):
    if not fname[-4:] == '.svg':
        fname += '.svg'
    plot = render(obj)
    figs = list(plot.select(dict(type=Figure)))
    for k, _ in enumerate(figs):
        figs[k].output_backend = 'svg'
    return export_svgs(plot, filename=fname)

from svg_stack import (
    Document, HBoxLayout, VBoxLayout,
    AlignCenter, AlignRight, AlignLeft,
)

def save_bokeh_svg_multipanel(obj, fname, orientation='h', align='center'):
    """
    Parameters
    ----------
    orientation: {'h', 'v'}
    """
    if not fname[-4:] == '.svg':
        fname += '.svg'
    fname_root = fname[:-4]

    panels = save_bokeh_svg(obj, fname)

    # rename first output; would otherwise clash when using svg_stack
    os.rename(panels[0], fname_root+'_0.svg')
    panels[0] = fname_root+'_0.svg'

    doc = Document()
    if orientation == 'v':
        layout = VBoxLayout()
    elif orientation == 'h':
        layout = HBoxLayout()

    alignment = {
        'center': AlignCenter,
        'right': AlignRight,
        'left': AlignLeft
    }

    for panel in panels:
        layout.addSVG(panel, alignment=AlignRight)

    layout.setSpacing(0)
    doc.setLayout(layout)
    doc.save(fname)

    for panel in panels:
        os.remove(panel)
