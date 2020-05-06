

def transform_points(from_crs, to_crs, x, y):
    """
    Transform x, y from one cartopy CRS to another.
    """
    xy_new = to_crs.transform_points(from_crs, x, y)
    return xy_new[..., 0], xy_new[..., 1]
