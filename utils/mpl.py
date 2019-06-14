import cartopy.crs as ccrs
import matplotlib.ticker as mticker
import numpy as np

def set_cartopy_grid(ax, lons, lats, label_opts=None, grid_opts=None, **kwargs):
    """
    Add graticules and label them
    """
    if label_opts is None:
        label_opts = {}
    if grid_opts is None:
        grid_opts = {}
    label_offset = kwargs.pop('label_offset', 1e-4)

    proj = ax.projection
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False,
                      linewidth=1, color='gray', alpha=0.5, linestyle='--',
                      **grid_opts)

    gl.xlocator = mticker.FixedLocator(lons)
    gl.ylocator = mticker.FixedLocator(lats)

    # W, E, S, N
    map_extent = ax.get_extent()

    # LATITUDE LABELS
    x0,_ = ax.get_xlim()
    some_lons = np.arange(gl.xlocator.locs.min(), gl.xlocator.locs.max(), 1)
    for lat in gl.ylocator.locs:
        # interpolate latitude circle to map boundary
        xyz_projected = proj.transform_points(
            ccrs.PlateCarree(), some_lons, lat*np.ones_like(some_lons)
        )
        x = xyz_projected[:, 0]
        y = xyz_projected[:, 1]
        y0 = np.interp(x0, x ,y)
        if map_extent[2]<y0<map_extent[3]:
            ax.text(x0-label_offset, y0, '{:2d}$^\circ$N'.format(lat), horizontalalignment = 'right', verticalalignment='center', **label_opts)

    # LONGITUDE LABELS / COMPLETELY ANALOGOUS TO ABOVE
    y0,_ = ax.get_ylim()
    some_lats = np.arange(gl.ylocator.locs.min(), gl.ylocator.locs.max(), 1)
    for lon in gl.xlocator.locs:
        xyz_projected = proj.transform_points(
            ccrs.PlateCarree(), lon*np.ones_like(some_lats), some_lats
        )
        x = xyz_projected[:, 0]
        y = xyz_projected[:, 1]

        x0 = np.interp(y0, y, x)
        if map_extent[0]<x0<map_extent[1]:
            ax.text(x0, y0-label_offset, '{:2d}$^\circ$W'.format(-lon), horizontalalignment = 'center', verticalalignment='top', **label_opts)
