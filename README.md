Some utils. No warranties.

Modules:
- [holoviews](utils/holoviews.py)

  Utils and own functions that do not warrant a PR for the [main holoviews library](https://github.com/pyviz/holoviews), or where the PR is not merged yet but I'm already using it.
  Make sure to check out [my PyViz recipes](https://github.com/poplarShift/pyviz-recipes).

- [ctd](utils/ctd.py)

  Utilities to derive data from hydrographic profiles in pandas dataframes. For a given function `func`, use e.g. as
  ```
  df.groupby(['Profile_number', 'Depth']).apply(func)
  ```

- [geometry](utils/geometry.py)

  Work with geographic data: nearest neighbour searches, translate dataframe with lat/lon into geodataframe, ...
