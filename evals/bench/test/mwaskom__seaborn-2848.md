# mwaskom__seaborn-2848

**Repository**: mwaskom/seaborn
**Created**: 2022-06-11T18:21:32Z
**Version**: 0.12

## Problem Statement

PairGrid errors with `hue` assigned in `map`
In seaborn version 0.9.0 I was able to use the following Code to plot scatterplots across a PairGrid with categorical hue. The reason I am not using the "hue" keyword in creating the PairGrid is, that I want one regression line (with regplot) and not one regression per hue-category.
```python
import seaborn as sns
iris = sns.load_dataset("iris")
g = sns.PairGrid(iris, y_vars=["sepal_length","sepal_width"], x_vars=["petal_length","petal_width"])
g.map(sns.scatterplot, hue=iris["species"])
g.map(sns.regplot, scatter=False)
```

However, since I updated to searbon 0.11.1 the following Error message occurs:
```
---------------------------------------------------------------------------
KeyError                                  Traceback (most recent call last)
~/.Software/miniforge3/envs/py3.9/lib/python3.8/site-packages/seaborn/_core.py in _lookup_single(self, key)
    143             # Use a value that's in the original data vector
--> 144             value = self.lookup_table[key]
    145         except KeyError:

KeyError: 'setosa'

During handling of the above exception, another exception occurred:

TypeError                                 Traceback (most recent call last)
~/.Software/miniforge3/envs/py3.9/lib/python3.8/site-packages/seaborn/_core.py in _lookup_single(self, key)
    148             try:
--> 149                 normed = self.norm(key)
    150             except TypeError as err:

TypeError: 'NoneType' object is not callable

During handling of the above exception, another exception occurred:

TypeError                                 Traceback (most recent call last)
<ipython-input-3-46dd21e9c95a> in <module>
      2 iris = sns.load_dataset("iris")
      3 g = sns.PairGrid(iris, y_vars=["sepal_length","sepal_width"], x_vars=["petal_length","species"])
----> 4 g.map(sns.scatterplot, hue=iris["species"])
      5 

~/.Software/miniforge3/envs/py3.9/lib/python3.8/site-packages/seaborn/axisgrid.py in map(self, func, **kwargs)
   1263         row_indices, col_indices = np.indices(self.axes.shape)
   1264         indices = zip(row_indices.flat, col_indices.flat)
-> 1265         self._map_bivariate(func, indices, **kwargs)
   1266 
   1267         return self

~/.Software/miniforge3/envs/py3.9/lib/python3.8/site-packages/seaborn/axisgrid.py in _map_bivariate(self, func, indices, **kwargs)
   1463             if ax is None:  # i.e. we are in corner mode
   1464                 continue
-> 1465             self._plot_bivariate(x_var, y_var, ax, func, **kws)
   1466         self._add_axis_labels()
   1467 

~/.Software/miniforge3/envs/py3.9/lib/python3.8/site-packages/seaborn/axisgrid.py in _plot_bivariate(self, x_var, y_var, ax, func, **kwargs)
   1503         kwargs.setdefault("hue_order", self._hue_order)
   1504         kwargs.setdefault("palette", self._orig_palette)
-> 1505         func(x=x, y=y, **kwargs)
   1506 
   1507         self._update_legend_data(ax)

~/.Software/miniforge3/envs/py3.9/lib/python3.8/site-packages/seaborn/_decorators.py in inner_f(*args, **kwargs)
     44             )
     45         kwargs.update({k: arg for k, arg in zip(sig.parameters, args)})
---> 46         return f(**kwargs)
     47     return inner_f
     48 

~/.Software/miniforge3/envs/py3.9/lib/python3.8/site-packages/seaborn/relational.py in scatterplot(x, y, hue, style, size, data, palette, hue_order, hue_norm, sizes, size_order, size_norm, markers, style_order, x_bins, y_bins, units, estimator, ci, n_boot, alpha, x_jitter, y_jitter, legend, ax, **kwargs)
    818     p._attach(ax)
    819 
--> 820     p.plot(ax, kwargs)
    821 
    822     return ax

~/.Software/miniforge3/envs/py3.9/lib/python3.8/site-packages/seaborn/relational.py in plot(self, ax, kws)
    626         # Apply the mapping from semantic variables to artist attributes
    627         if "hue" in self.variables:
--> 628             c = self._hue_map(data["hue"])
    629 
    630         if "size" in self.variables:

~/.Software/miniforge3/envs/py3.9/lib/python3.8/site-packages/seaborn/_core.py in __call__(self, key, *args, **kwargs)
     61         """Get the attribute(s) values for the data key."""
     62         if isinstance(key, (list, np.ndarray, pd.Series)):
---> 63             return [self._lookup_single(k, *args, **kwargs) for k in key]
     64         else:
     65             return self._lookup_single(key, *args, **kwargs)

~/.Software/miniforge3/envs/py3.9/lib/python3.8/site-packages/seaborn/_core.py in <listcomp>(.0)
     61         """Get the attribute(s) values for the data key."""
     62         if isinstance(key, (list, np.ndarray, pd.Series)):
---> 63             return [self._lookup_single(k, *args, **kwargs) for k in key]
     64         else:
     65             return self._lookup_single(key, *args, **kwargs)

~/.Software/miniforge3/envs/py3.9/lib/python3.8/site-packages/seaborn/_core.py in _lookup_single(self, key)
    149                 normed = self.norm(key)
    150             except TypeError as err:
--> 151                 if np.isnan(key):
    152                     value = (0, 0, 0, 0)
    153                 else:

TypeError: ufunc 'isnan' not supported for the input types, and the inputs could not be safely coerced to any supported types according to the casting rule ''safe''
```

My further observations are:
- the error does not occur when using the "hue" keyword when creating PairGrid
- the error does not occur for numerical values for hue
- changing the dtype to "categorical" does not help

Edit:
I tried all versions between 0.9.0 and the current release (0.11.1) and the error only occurs in the current release. If I use 0.11.0, the plot seems to work.


## Hints

The following workarounds seem to work:
```
g.map(sns.scatterplot, hue=iris["species"], hue_order=iris["species"].unique())
```
or
```
g.map(lambda x, y, **kwargs: sns.scatterplot(x=x, y=y, hue=iris["species"]))
```
> ```
> g.map(sns.scatterplot, hue=iris["species"], hue_order=iris["species"].unique())
> ```

The workaround fixes the problem for me.
Thank you very much!

@mwaskom Should I close the Issue or leave it open until the bug is fixed?
That's a good workaround, but it's still a bug. The problem is that `PairGrid` now lets `hue` at the grid-level delegate to the axes-level functions if they have `hue` in their signature. But it's not properly handling the case where `hue` is *not* set for the grid, but *is* specified for one mapped function. @jhncls's workaround suggests the fix.

An easier workaround would have been to set `PairGrid(..., hue="species")` and then pass `.map(..., hue=None)` where you don't want to separate by species. But `regplot` is the one axis-level function that does not yet handle hue-mapping internally, so it doesn't work for this specific case. It would have if you wanted a single bivariate density over hue-mapped scatterplot points (i.e. [this example](http://seaborn.pydata.org/introduction.html#classes-and-functions-for-making-complex-graphics) or something similar.

## Patch

```diff

diff --git a/seaborn/_oldcore.py b/seaborn/_oldcore.py
--- a/seaborn/_oldcore.py
+++ b/seaborn/_oldcore.py
@@ -149,6 +149,13 @@ def _lookup_single(self, key):
             # Use a value that's in the original data vector
             value = self.lookup_table[key]
         except KeyError:
+
+            if self.norm is None:
+                # Currently we only get here in scatterplot with hue_order,
+                # because scatterplot does not consider hue a grouping variable
+                # So unused hue levels are in the data, but not the lookup table
+                return (0, 0, 0, 0)
+
             # Use the colormap to interpolate between existing datapoints
             # (e.g. in the context of making a continuous legend)
             try:


```

## Test Patch

```diff
diff --git a/tests/test_relational.py b/tests/test_relational.py
--- a/tests/test_relational.py
+++ b/tests/test_relational.py
@@ -9,6 +9,7 @@
 
 from seaborn.external.version import Version
 from seaborn.palettes import color_palette
+from seaborn._oldcore import categorical_order
 
 from seaborn.relational import (
     _RelationalPlotter,
@@ -1623,6 +1624,16 @@ def test_supplied_color_array(self, long_df):
         _draw_figure(ax.figure)
         assert_array_equal(ax.collections[0].get_facecolors(), colors)
 
+    def test_hue_order(self, long_df):
+
+        order = categorical_order(long_df["a"])
+        unused = order.pop()
+
+        ax = scatterplot(data=long_df, x="x", y="y", hue="a", hue_order=order)
+        points = ax.collections[0]
+        assert (points.get_facecolors()[long_df["a"] == unused] == 0).all()
+        assert [t.get_text() for t in ax.legend_.texts] == order
+
     def test_linewidths(self, long_df):
 
         f, ax = plt.subplots()

```

## Test Information

**Tests that should FAIL→PASS**: ["tests/test_relational.py::TestScatterPlotter::test_hue_order"]

**Tests that should PASS→PASS**: ["tests/test_relational.py::TestRelationalPlotter::test_wide_df_variables", "tests/test_relational.py::TestRelationalPlotter::test_wide_df_with_nonnumeric_variables", "tests/test_relational.py::TestRelationalPlotter::test_wide_array_variables", "tests/test_relational.py::TestRelationalPlotter::test_flat_array_variables", "tests/test_relational.py::TestRelationalPlotter::test_flat_list_variables", "tests/test_relational.py::TestRelationalPlotter::test_flat_series_variables", "tests/test_relational.py::TestRelationalPlotter::test_wide_list_of_series_variables", "tests/test_relational.py::TestRelationalPlotter::test_wide_list_of_arrays_variables", "tests/test_relational.py::TestRelationalPlotter::test_wide_list_of_list_variables", "tests/test_relational.py::TestRelationalPlotter::test_wide_dict_of_series_variables", "tests/test_relational.py::TestRelationalPlotter::test_wide_dict_of_arrays_variables", "tests/test_relational.py::TestRelationalPlotter::test_wide_dict_of_lists_variables", "tests/test_relational.py::TestRelationalPlotter::test_relplot_complex", "tests/test_relational.py::TestRelationalPlotter::test_relplot_vectors[series]", "tests/test_relational.py::TestRelationalPlotter::test_relplot_vectors[numpy]", "tests/test_relational.py::TestRelationalPlotter::test_relplot_vectors[list]", "tests/test_relational.py::TestRelationalPlotter::test_relplot_wide", "tests/test_relational.py::TestRelationalPlotter::test_relplot_hues", "tests/test_relational.py::TestRelationalPlotter::test_relplot_sizes", "tests/test_relational.py::TestRelationalPlotter::test_relplot_styles", "tests/test_relational.py::TestRelationalPlotter::test_relplot_stringy_numerics", "tests/test_relational.py::TestRelationalPlotter::test_relplot_data", "tests/test_relational.py::TestRelationalPlotter::test_facet_variable_collision", "tests/test_relational.py::TestRelationalPlotter::test_ax_kwarg_removal", "tests/test_relational.py::TestLinePlotter::test_legend_data", "tests/test_relational.py::TestLinePlotter::test_plot", "tests/test_relational.py::TestLinePlotter::test_axis_labels", "tests/test_relational.py::TestScatterPlotter::test_color", "tests/test_relational.py::TestScatterPlotter::test_legend_data", "tests/test_relational.py::TestScatterPlotter::test_plot", "tests/test_relational.py::TestScatterPlotter::test_axis_labels", "tests/test_relational.py::TestScatterPlotter::test_scatterplot_axes", "tests/test_relational.py::TestScatterPlotter::test_literal_attribute_vectors", "tests/test_relational.py::TestScatterPlotter::test_supplied_color_array", "tests/test_relational.py::TestScatterPlotter::test_linewidths", "tests/test_relational.py::TestScatterPlotter::test_size_norm_extrapolation", "tests/test_relational.py::TestScatterPlotter::test_datetime_scale", "tests/test_relational.py::TestScatterPlotter::test_scatterplot_vs_relplot[long_semantics0]", "tests/test_relational.py::TestScatterPlotter::test_scatterplot_vs_relplot[long_semantics1]", "tests/test_relational.py::TestScatterPlotter::test_scatterplot_vs_relplot[long_semantics2]", "tests/test_relational.py::TestScatterPlotter::test_scatterplot_vs_relplot[long_semantics3]", "tests/test_relational.py::TestScatterPlotter::test_scatterplot_vs_relplot[long_semantics4]", "tests/test_relational.py::TestScatterPlotter::test_scatterplot_vs_relplot[long_semantics5]", "tests/test_relational.py::TestScatterPlotter::test_scatterplot_vs_relplot[long_semantics6]", "tests/test_relational.py::TestScatterPlotter::test_scatterplot_vs_relplot[long_semantics7]", "tests/test_relational.py::TestScatterPlotter::test_scatterplot_vs_relplot[long_semantics8]", "tests/test_relational.py::TestScatterPlotter::test_scatterplot_vs_relplot[long_semantics9]", "tests/test_relational.py::TestScatterPlotter::test_scatterplot_vs_relplot[long_semantics10]", "tests/test_relational.py::TestScatterPlotter::test_scatterplot_vs_relplot[long_semantics11]", "tests/test_relational.py::TestScatterPlotter::test_scatterplot_smoke"]

**Base Commit**: 94621cef29f80282436d73e8d2c0aa76dab81273
**Environment Setup Commit**: d25872b0fc99dbf7e666a91f59bd4ed125186aa1
