from typing import List
from scipy.spatial import cKDTree
import numpy as np
from shapely.geometry import Point, Polygon

# need to sort out geometry vs. attr vs dict entry/column,
# and dataset vs dataframe!!

def _build_tree(d1, d2, x, y):
    n1 = np.array(list(zip(d1[x], d1[y])) )
    n2 = np.array(list(zip(d2[x], d2[y])) )
    btree = cKDTree(n2)
    return btree, n1, n2

def nearest(d1, d2, x='lon', y='lat'):
    """
    For each point in d1, find nearest point in d2.

    Parameters
    ----------
    d1, d2 : pandas dataframes

    Returns
    -------
    dist : distances to each nearest
    idx : indices of each nearest

    License
    -------
    GNU-GPLv3, (C) A. R.
    (https://github.com/poplarShift/python-data-science-utils)
        """
    btree, n1, _ = _build_tree(d1, d2, x, y)
    return btree.query(n1, k=1)

def points_within(d1, d2, radius, x='lon', y='lat'):
    """
    For each point in d1, find all points of d2 within given radius

    Parameters
    ----------
    d1, d2 : pandas dataframes

    Returns
    -------
    idx : indices

    License
    -------
    GNU-GPLv3, (C) A. R.
    (https://github.com/poplarShift/python-data-science-utils)
    """
    n1 = np.array(list(zip(d1.geometry.x, d1.geometry.y)) )
    n2 = np.array(list(zip(d2.geometry.x, d2.geometry.y)) )
    btree = cKDTree(n2)
    idx = btree.query_ball_point(n1, r=radius)
    return idx

def nearest_with_time_constraint(d1, d2, x, y, dist_tol=.1, t='date', t_tol=1):
    """
    For each point in d1, find nearest point in d2,
    and return a boolean index that is True iff their distance is less
    than dist_tol and they are not further apart in time than t_tol days.
    Confused yet?

    Parameters
    ----------
    d1, d2 : pandas dataframes
    dist_tol : float, units given by x, y
    t_tol : floats, allowed time difference in days
    x, y : Names of x and y columns

    Returns
    -------
    nearest :
    within_tol : bool array, True of nearest neighbour within dist_tol and t_tol

    License
    -------
    GNU-GPLv3, (C) A. R.
    (https://github.com/poplarShift/python-data-science-utils)
    """
    n1 = np.array(list(zip(d1[x], d1[y])) )
    n2 = np.array(list(zip(d2[x], d2[y])) )
    tree_spatial = cKDTree(n2)
    distances, nearest = tree_spatial.query(n1)

    # for each point in d1, find all points in d2 within ttol days
    t1_epoch_days = (d1[t].values[:, np.newaxis] - np.datetime64('1900-01-01'))/np.timedelta64(1, 'D')
    t2_epoch_days = (d2[t].values[:, np.newaxis] - np.datetime64('1900-01-01'))/np.timedelta64(1, 'D')
    tree_tmp = cKDTree(t2_epoch_days)
    within_t_tol = tree_tmp.query_ball_point(t1_epoch_days, r=t_tol) # array of lists of pot. candidates

    within_tol = [True if idx in candidates and dist<=dist_tol else False
                  for idx, dist, candidates
                  in zip(nearest, distances, within_t_tol)]
    return nearest, within_tol


def smoothen(g):
    """
    Insert new points along Polygon boundary.

    License
    -------
    GNU-GPLv3, (C) A. R.
    (https://github.com/poplarShift/python-data-science-utils)
    """
    newcoords = []
    for c in g.exterior.coords.xy:
        newc = []
        for c1, c2 in zip(c[:-1], c[1:]):
            newc += list(np.linspace(c1, c2, 50)[:-1])
        newcoords.append(newc)

    newcoords = [(x,y) for x, y in zip(*newcoords)]
    return Polygon(newcoords)


def find_nearest_lonlat(lon0: float, lat0: float, lons: List[float], lats: List[float]):
    """Find the point nearest to (lon0, lat0) among the points list(zip(lons, lats)).

    Automatically chooses appropriate UTM zone for coordinate transformations.

    Returns:
        nearest lon
        nearest lat
        distance to nearest
        index in lists `lons` and `lats`
        
    License
    -------
    GNU-GPLv3, (C) A. R.
    (https://github.com/poplarShift/python-data-science-utils)
    """
    from cartopy.crs import UTM, PlateCarree
    import utm
    from scipy.spatial import KDTree
    import numpy as np

    _, _, zone, letter = utm.from_latlon(latitude=lat0, longitude=lon0)
    crs = UTM(zone)
    x, y = crs.transform_point(lon0, lat0, PlateCarree())
    xyz = crs.transform_points(PlateCarree(), np.array(lons), np.array(lats))
    pts = xyz[:, :2]

    tree = KDTree(pts)
    dist, idx = tree.query((x, y))
    lon = lons[idx]
    lat = lats[idx]
    return lon, lat, dist, idx