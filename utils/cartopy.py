import numpy as np


def transform_points(from_crs, to_crs, x, y):
    """
    Transform x, y from one cartopy CRS to another.
    """
    xy_new = to_crs.transform_points(from_crs, x, y)
    return xy_new[..., 0], xy_new[..., 1]

def calculate_deviation(proj, compass, x, y, xy_units, eps_ll=1e-9):
    """
    Calculate deviation of local x/y direction from north/east direction.

    In other words, let the deviation be `theta`. Then for an east/north velocity (u, v),
    the velocity in the projection proj will be
    (up, vp) = (u*cos(theta) - v*sin(theta), u*sin(theta) + v*cos(theta)),
    or, equivalently, array([[cos(dev), -sin(dev)], [sin(dev), cos(dev)]]) @ array([u, v]).

    In practice, deviation of North and East will vary, but not too much if the projection is
    appropriate for the data.

    Arguments
    ---------
        proj: Cartopy CRS
        compass: str {'N', 'E'}
        x, y: np arrays with coordinates
        xy_units: str {'lonlat', 'xy'}
        eps_ll: small longitude/latitude values to create local vectorsr

    Returns
    -------
        deviation theta (radians)
    """
    if compass == 'N':
        vector_dir = (0, 1)
    elif compass == 'E':
        vector_dir = (1, 0)
    else:
        raise ValueError

    plate_carree = ccrs.PlateCarree()

    if xy_units == 'xy':
        vector_orig_x = x
        vector_orig_y = y
        vector_orig_lon, vector_orig_lat = transform_points(proj, plate_carree, x, y)
    elif xy_units == 'lonlat':
        vector_orig_lon = x
        vector_orig_lat = y
        vector_orig_x, vector_orig_y = transform_points(plate_carree, proj, x, y)

    vector_head_lat = vector_orig_lat + eps_ll * vector_dir[1]
    vector_head_lon = vector_orig_lon + eps_ll * vector_dir[0]

    vector_head_x, vector_head_y = transform_points(plate_carree, proj, vector_head_lon, vector_head_lat)

    deviation = (
        np.arctan2(vector_head_y-vector_orig_y, vector_head_x-vector_orig_x) -
        np.arctan2(vector_dir[1], vector_dir[0])
    ) % (2*np.pi)

    return deviation
