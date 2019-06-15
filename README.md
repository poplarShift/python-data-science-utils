Some utils to do data science in python. No warranties.

Modules:
- [holoviews](utils/holoviews/)

  Utils and own functions that do not warrant a PR for the [main holoviews library](https://github.com/pyviz/holoviews), or where the PR is not merged yet but I'm already using it.
  You may want to check out my [PyViz recipes](https://github.com/poplarShift/pyviz-recipes) too.

- [Standard Imports](utils/standard_imports.py)

  `from utils.standard_imports import *`. A bunch of earth/data science standard imports, suppressing possible `ImportError`s.

- [xarray](utils/xarray.py)

- [pandas](utils/pandas.py)

  Arithmetic with datetime columns, snap data ranges to specific dates, translate dataframe with lat/lon into geodataframe, ...

- [geometry](utils/geometry.py)

  Work with geographic data: nearest neighbour searches, ...

- [matplotlib](utils/mpl.py)

- [matlab](utils/matlab.py)

  Reading in .mat files I occasionally get from those collaborators who still use matlab
