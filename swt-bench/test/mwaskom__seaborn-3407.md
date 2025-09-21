# mwaskom__seaborn-3407

**Repository**: mwaskom/seaborn
**Created**: 2023-06-27T23:17:29Z
**Version**: 0.13

## Problem Statement

pairplot raises KeyError with MultiIndex DataFrame
When trying to pairplot a MultiIndex DataFrame, `pairplot` raises a `KeyError`:

MRE:

```python
import numpy as np
import pandas as pd
import seaborn as sns


data = {
    ("A", "1"): np.random.rand(100),
    ("A", "2"): np.random.rand(100),
    ("B", "1"): np.random.rand(100),
    ("B", "2"): np.random.rand(100),
}
df = pd.DataFrame(data)
sns.pairplot(df)
```

Output:

```
[c:\Users\KLuu\anaconda3\lib\site-packages\seaborn\axisgrid.py](file:///C:/Users/KLuu/anaconda3/lib/site-packages/seaborn/axisgrid.py) in pairplot(data, hue, hue_order, palette, vars, x_vars, y_vars, kind, diag_kind, markers, height, aspect, corner, dropna, plot_kws, diag_kws, grid_kws, size)
   2142     diag_kws.setdefault("legend", False)
   2143     if diag_kind == "hist":
-> 2144         grid.map_diag(histplot, **diag_kws)
   2145     elif diag_kind == "kde":
   2146         diag_kws.setdefault("fill", True)

[c:\Users\KLuu\anaconda3\lib\site-packages\seaborn\axisgrid.py](file:///C:/Users/KLuu/anaconda3/lib/site-packages/seaborn/axisgrid.py) in map_diag(self, func, **kwargs)
   1488                 plt.sca(ax)
   1489 
-> 1490             vector = self.data[var]
   1491             if self._hue_var is not None:
   1492                 hue = self.data[self._hue_var]

[c:\Users\KLuu\anaconda3\lib\site-packages\pandas\core\frame.py](file:///C:/Users/KLuu/anaconda3/lib/site-packages/pandas/core/frame.py) in __getitem__(self, key)
   3765             if is_iterator(key):
   3766                 key = list(key)
-> 3767             indexer = self.columns._get_indexer_strict(key, "columns")[1]
   3768 
   3769         # take() does not accept boolean indexers

[c:\Users\KLuu\anaconda3\lib\site-packages\pandas\core\indexes\multi.py](file:///C:/Users/KLuu/anaconda3/lib/site-packages/pandas/core/indexes/multi.py) in _get_indexer_strict(self, key, axis_name)
   2534             indexer = self._get_indexer_level_0(keyarr)
   2535 
-> 2536             self._raise_if_missing(key, indexer, axis_name)
   2537             return self[indexer], indexer
   2538 

[c:\Users\KLuu\anaconda3\lib\site-packages\pandas\core\indexes\multi.py](file:///C:/Users/KLuu/anaconda3/lib/site-packages/pandas/core/indexes/multi.py) in _raise_if_missing(self, key, indexer, axis_name)
   2552                 cmask = check == -1
   2553                 if cmask.any():
-> 2554                     raise KeyError(f"{keyarr[cmask]} not in index")
   2555                 # We get here when levels still contain values which are not
   2556                 # actually in Index anymore

KeyError: "['1'] not in index"
```

A workaround is to "flatten" the columns:

```python
df.columns = ["".join(column) for column in df.columns]
```


## Patch

```diff

diff --git a/seaborn/axisgrid.py b/seaborn/axisgrid.py
--- a/seaborn/axisgrid.py
+++ b/seaborn/axisgrid.py
@@ -1472,8 +1472,8 @@ def map_diag(self, func, **kwargs):
                 for ax in diag_axes[1:]:
                     share_axis(diag_axes[0], ax, "y")
 
-            self.diag_vars = np.array(diag_vars, np.object_)
-            self.diag_axes = np.array(diag_axes, np.object_)
+            self.diag_vars = diag_vars
+            self.diag_axes = diag_axes
 
         if "hue" not in signature(func).parameters:
             return self._map_diag_iter_hue(func, **kwargs)


```

## Test Patch

```diff
diff --git a/tests/test_axisgrid.py b/tests/test_axisgrid.py
--- a/tests/test_axisgrid.py
+++ b/tests/test_axisgrid.py
@@ -1422,6 +1422,13 @@ def test_pairplot_markers(self):
         with pytest.warns(UserWarning):
             g = ag.pairplot(self.df, hue="a", vars=vars, markers=markers[:-2])
 
+    def test_pairplot_column_multiindex(self):
+
+        cols = pd.MultiIndex.from_arrays([["x", "y"], [1, 2]])
+        df = self.df[["x", "y"]].set_axis(cols, axis=1)
+        g = ag.pairplot(df)
+        assert g.diag_vars == list(cols)
+
     def test_corner_despine(self):
 
         g = ag.PairGrid(self.df, corner=True, despine=False)

```

## Test Information

**Tests that should FAIL→PASS**: ["tests/test_axisgrid.py::TestPairGrid::test_pairplot_column_multiindex"]

**Tests that should PASS→PASS**: ["tests/test_axisgrid.py::TestFacetGrid::test_self_data", "tests/test_axisgrid.py::TestFacetGrid::test_self_figure", "tests/test_axisgrid.py::TestFacetGrid::test_self_axes", "tests/test_axisgrid.py::TestFacetGrid::test_axes_array_size", "tests/test_axisgrid.py::TestFacetGrid::test_single_axes", "tests/test_axisgrid.py::TestFacetGrid::test_col_wrap", "tests/test_axisgrid.py::TestFacetGrid::test_normal_axes", "tests/test_axisgrid.py::TestFacetGrid::test_wrapped_axes", "tests/test_axisgrid.py::TestFacetGrid::test_axes_dict", "tests/test_axisgrid.py::TestFacetGrid::test_figure_size", "tests/test_axisgrid.py::TestFacetGrid::test_figure_size_with_legend", "tests/test_axisgrid.py::TestFacetGrid::test_legend_data", "tests/test_axisgrid.py::TestFacetGrid::test_legend_data_missing_level", "tests/test_axisgrid.py::TestFacetGrid::test_get_boolean_legend_data", "tests/test_axisgrid.py::TestFacetGrid::test_legend_tuples", "tests/test_axisgrid.py::TestFacetGrid::test_legend_options", "tests/test_axisgrid.py::TestFacetGrid::test_legendout_with_colwrap", "tests/test_axisgrid.py::TestFacetGrid::test_legend_tight_layout", "tests/test_axisgrid.py::TestFacetGrid::test_subplot_kws", "tests/test_axisgrid.py::TestFacetGrid::test_gridspec_kws", "tests/test_axisgrid.py::TestFacetGrid::test_gridspec_kws_col_wrap", "tests/test_axisgrid.py::TestFacetGrid::test_data_generator", "tests/test_axisgrid.py::TestFacetGrid::test_map", "tests/test_axisgrid.py::TestFacetGrid::test_map_dataframe", "tests/test_axisgrid.py::TestFacetGrid::test_set", "tests/test_axisgrid.py::TestFacetGrid::test_set_titles", "tests/test_axisgrid.py::TestFacetGrid::test_set_titles_margin_titles", "tests/test_axisgrid.py::TestFacetGrid::test_set_ticklabels", "tests/test_axisgrid.py::TestFacetGrid::test_set_axis_labels", "tests/test_axisgrid.py::TestFacetGrid::test_axis_lims", "tests/test_axisgrid.py::TestFacetGrid::test_data_orders", "tests/test_axisgrid.py::TestFacetGrid::test_palette", "tests/test_axisgrid.py::TestFacetGrid::test_hue_kws", "tests/test_axisgrid.py::TestFacetGrid::test_dropna", "tests/test_axisgrid.py::TestFacetGrid::test_categorical_column_missing_categories", "tests/test_axisgrid.py::TestFacetGrid::test_categorical_warning", "tests/test_axisgrid.py::TestFacetGrid::test_refline", "tests/test_axisgrid.py::TestFacetGrid::test_apply", "tests/test_axisgrid.py::TestFacetGrid::test_pipe", "tests/test_axisgrid.py::TestFacetGrid::test_tick_params", "tests/test_axisgrid.py::TestPairGrid::test_self_data", "tests/test_axisgrid.py::TestPairGrid::test_ignore_datelike_data", "tests/test_axisgrid.py::TestPairGrid::test_self_figure", "tests/test_axisgrid.py::TestPairGrid::test_self_axes", "tests/test_axisgrid.py::TestPairGrid::test_default_axes", "tests/test_axisgrid.py::TestPairGrid::test_specific_square_axes[vars0]", "tests/test_axisgrid.py::TestPairGrid::test_specific_square_axes[vars1]", "tests/test_axisgrid.py::TestPairGrid::test_remove_hue_from_default", "tests/test_axisgrid.py::TestPairGrid::test_specific_nonsquare_axes[x_vars0-y_vars0]", "tests/test_axisgrid.py::TestPairGrid::test_specific_nonsquare_axes[x_vars1-z]", "tests/test_axisgrid.py::TestPairGrid::test_specific_nonsquare_axes[x_vars2-y_vars2]", "tests/test_axisgrid.py::TestPairGrid::test_corner", "tests/test_axisgrid.py::TestPairGrid::test_size", "tests/test_axisgrid.py::TestPairGrid::test_empty_grid", "tests/test_axisgrid.py::TestPairGrid::test_map", "tests/test_axisgrid.py::TestPairGrid::test_map_nonsquare", "tests/test_axisgrid.py::TestPairGrid::test_map_lower", "tests/test_axisgrid.py::TestPairGrid::test_map_upper", "tests/test_axisgrid.py::TestPairGrid::test_map_mixed_funcsig", "tests/test_axisgrid.py::TestPairGrid::test_map_diag", "tests/test_axisgrid.py::TestPairGrid::test_map_diag_rectangular", "tests/test_axisgrid.py::TestPairGrid::test_map_diag_color", "tests/test_axisgrid.py::TestPairGrid::test_map_diag_palette", "tests/test_axisgrid.py::TestPairGrid::test_map_diag_and_offdiag", "tests/test_axisgrid.py::TestPairGrid::test_diag_sharey", "tests/test_axisgrid.py::TestPairGrid::test_map_diag_matplotlib", "tests/test_axisgrid.py::TestPairGrid::test_palette", "tests/test_axisgrid.py::TestPairGrid::test_hue_kws", "tests/test_axisgrid.py::TestPairGrid::test_hue_order", "tests/test_axisgrid.py::TestPairGrid::test_hue_order_missing_level", "tests/test_axisgrid.py::TestPairGrid::test_hue_in_map", "tests/test_axisgrid.py::TestPairGrid::test_nondefault_index", "tests/test_axisgrid.py::TestPairGrid::test_dropna[scatterplot]", "tests/test_axisgrid.py::TestPairGrid::test_dropna[scatter]", "tests/test_axisgrid.py::TestPairGrid::test_histplot_legend", "tests/test_axisgrid.py::TestPairGrid::test_pairplot", "tests/test_axisgrid.py::TestPairGrid::test_pairplot_reg", "tests/test_axisgrid.py::TestPairGrid::test_pairplot_reg_hue", "tests/test_axisgrid.py::TestPairGrid::test_pairplot_diag_kde", "tests/test_axisgrid.py::TestPairGrid::test_pairplot_kde", "tests/test_axisgrid.py::TestPairGrid::test_pairplot_hist", "tests/test_axisgrid.py::TestPairGrid::test_pairplot_markers", "tests/test_axisgrid.py::TestPairGrid::test_corner_despine", "tests/test_axisgrid.py::TestPairGrid::test_corner_set", "tests/test_axisgrid.py::TestPairGrid::test_legend", "tests/test_axisgrid.py::TestPairGrid::test_tick_params", "tests/test_axisgrid.py::TestJointGrid::test_margin_grid_from_lists", "tests/test_axisgrid.py::TestJointGrid::test_margin_grid_from_arrays", "tests/test_axisgrid.py::TestJointGrid::test_margin_grid_from_series", "tests/test_axisgrid.py::TestJointGrid::test_margin_grid_from_dataframe", "tests/test_axisgrid.py::TestJointGrid::test_margin_grid_from_dataframe_bad_variable", "tests/test_axisgrid.py::TestJointGrid::test_margin_grid_axis_labels", "tests/test_axisgrid.py::TestJointGrid::test_dropna", "tests/test_axisgrid.py::TestJointGrid::test_axlims", "tests/test_axisgrid.py::TestJointGrid::test_marginal_ticks", "tests/test_axisgrid.py::TestJointGrid::test_bivariate_plot", "tests/test_axisgrid.py::TestJointGrid::test_univariate_plot", "tests/test_axisgrid.py::TestJointGrid::test_univariate_plot_distplot", "tests/test_axisgrid.py::TestJointGrid::test_univariate_plot_matplotlib", "tests/test_axisgrid.py::TestJointGrid::test_plot", "tests/test_axisgrid.py::TestJointGrid::test_space", "tests/test_axisgrid.py::TestJointGrid::test_hue[True]", "tests/test_axisgrid.py::TestJointGrid::test_hue[False]", "tests/test_axisgrid.py::TestJointGrid::test_refline", "tests/test_axisgrid.py::TestJointPlot::test_scatter", "tests/test_axisgrid.py::TestJointPlot::test_scatter_hue", "tests/test_axisgrid.py::TestJointPlot::test_reg", "tests/test_axisgrid.py::TestJointPlot::test_resid", "tests/test_axisgrid.py::TestJointPlot::test_hist", "tests/test_axisgrid.py::TestJointPlot::test_hex", "tests/test_axisgrid.py::TestJointPlot::test_kde", "tests/test_axisgrid.py::TestJointPlot::test_kde_hue", "tests/test_axisgrid.py::TestJointPlot::test_color", "tests/test_axisgrid.py::TestJointPlot::test_palette", "tests/test_axisgrid.py::TestJointPlot::test_hex_customise", "tests/test_axisgrid.py::TestJointPlot::test_bad_kind", "tests/test_axisgrid.py::TestJointPlot::test_unsupported_hue_kind", "tests/test_axisgrid.py::TestJointPlot::test_leaky_dict", "tests/test_axisgrid.py::TestJointPlot::test_distplot_kwarg_warning", "tests/test_axisgrid.py::TestJointPlot::test_ax_warning"]

**Base Commit**: 515286e02be3e4c0ff2ef4addb34a53c4a676ee4
**Environment Setup Commit**: 23860365816440b050e9211e1c395a966de3c403
