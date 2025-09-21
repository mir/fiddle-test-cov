# pydata__xarray-5131

**Repository**: pydata/xarray
**Created**: 2021-04-08T09:19:30Z
**Version**: 0.12

## Problem Statement

Trailing whitespace in DatasetGroupBy text representation
When displaying a DatasetGroupBy in an interactive Python session, the first line of output contains a trailing whitespace. The first example in the documentation demonstrate this:

```pycon
>>> import xarray as xr, numpy as np
>>> ds = xr.Dataset(
...     {"foo": (("x", "y"), np.random.rand(4, 3))},
...     coords={"x": [10, 20, 30, 40], "letters": ("x", list("abba"))},
... )
>>> ds.groupby("letters")
DatasetGroupBy, grouped over 'letters' 
2 groups with labels 'a', 'b'.
```

There is a trailing whitespace in the first line of output which is "DatasetGroupBy, grouped over 'letters' ". This can be seen more clearly by converting the object to a string (note the whitespace before `\n`):

```pycon
>>> str(ds.groupby("letters"))
"DatasetGroupBy, grouped over 'letters' \n2 groups with labels 'a', 'b'."
```


While this isn't a problem in itself, it causes an issue for us because we use flake8 in continuous integration to verify that our code is correctly formatted and we also have doctests that rely on DatasetGroupBy textual representation. Flake8 reports a violation on the trailing whitespaces in our docstrings. If we remove the trailing whitespaces, our doctests fail because the expected output doesn't match the actual output. So we have conflicting constraints coming from our tools which both seem reasonable. Trailing whitespaces are forbidden by flake8 because, among other reasons, they lead to noisy git diffs. Doctest want the expected output to be exactly the same as the actual output and considers a trailing whitespace to be a significant difference. We could configure flake8 to ignore this particular violation for the files in which we have these doctests, but this may cause other trailing whitespaces to creep in our code, which we don't want. Unfortunately it's not possible to just add `# NoQA` comments to get flake8 to ignore the violation only for specific lines because that creates a difference between expected and actual output from doctest point of view. Flake8 doesn't allow to disable checks for blocks of code either.

Is there a reason for having this trailing whitespace in DatasetGroupBy representation? Whould it be OK to remove it? If so please let me know and I can make a pull request.


## Hints

I don't think this is intentional and we are happy to take a PR. The problem seems to be here:

https://github.com/pydata/xarray/blob/c7c4aae1fa2bcb9417e498e7dcb4acc0792c402d/xarray/core/groupby.py#L439

You will also have to fix the tests (maybe other places):

https://github.com/pydata/xarray/blob/c7c4aae1fa2bcb9417e498e7dcb4acc0792c402d/xarray/tests/test_groupby.py#L391
https://github.com/pydata/xarray/blob/c7c4aae1fa2bcb9417e498e7dcb4acc0792c402d/xarray/tests/test_groupby.py#L408


## Patch

```diff

diff --git a/xarray/core/groupby.py b/xarray/core/groupby.py
--- a/xarray/core/groupby.py
+++ b/xarray/core/groupby.py
@@ -436,7 +436,7 @@ def __iter__(self):
         return zip(self._unique_coord.values, self._iter_grouped())
 
     def __repr__(self):
-        return "{}, grouped over {!r} \n{!r} groups with labels {}.".format(
+        return "{}, grouped over {!r}\n{!r} groups with labels {}.".format(
             self.__class__.__name__,
             self._unique_coord.name,
             self._unique_coord.size,


```

## Test Patch

```diff
diff --git a/xarray/tests/test_groupby.py b/xarray/tests/test_groupby.py
--- a/xarray/tests/test_groupby.py
+++ b/xarray/tests/test_groupby.py
@@ -388,7 +388,7 @@ def test_da_groupby_assign_coords():
 def test_groupby_repr(obj, dim):
     actual = repr(obj.groupby(dim))
     expected = "%sGroupBy" % obj.__class__.__name__
-    expected += ", grouped over %r " % dim
+    expected += ", grouped over %r" % dim
     expected += "\n%r groups with labels " % (len(np.unique(obj[dim])))
     if dim == "x":
         expected += "1, 2, 3, 4, 5."
@@ -405,7 +405,7 @@ def test_groupby_repr(obj, dim):
 def test_groupby_repr_datetime(obj):
     actual = repr(obj.groupby("t.month"))
     expected = "%sGroupBy" % obj.__class__.__name__
-    expected += ", grouped over 'month' "
+    expected += ", grouped over 'month'"
     expected += "\n%r groups with labels " % (len(np.unique(obj.t.dt.month)))
     expected += "1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12."
     assert actual == expected

```

## Test Information

**Tests that should FAIL→PASS**: ["xarray/tests/test_groupby.py::test_groupby_repr[obj0-x]", "xarray/tests/test_groupby.py::test_groupby_repr[obj0-y]", "xarray/tests/test_groupby.py::test_groupby_repr[obj0-z]", "xarray/tests/test_groupby.py::test_groupby_repr[obj0-month]", "xarray/tests/test_groupby.py::test_groupby_repr[obj1-x]", "xarray/tests/test_groupby.py::test_groupby_repr[obj1-y]", "xarray/tests/test_groupby.py::test_groupby_repr[obj1-z]", "xarray/tests/test_groupby.py::test_groupby_repr[obj1-month]", "xarray/tests/test_groupby.py::test_groupby_repr_datetime[obj0]", "xarray/tests/test_groupby.py::test_groupby_repr_datetime[obj1]"]

**Tests that should PASS→PASS**: ["xarray/tests/test_groupby.py::test_consolidate_slices", "xarray/tests/test_groupby.py::test_groupby_dims_property", "xarray/tests/test_groupby.py::test_multi_index_groupby_map", "xarray/tests/test_groupby.py::test_multi_index_groupby_sum", "xarray/tests/test_groupby.py::test_groupby_da_datetime", "xarray/tests/test_groupby.py::test_groupby_duplicate_coordinate_labels", "xarray/tests/test_groupby.py::test_groupby_input_mutation", "xarray/tests/test_groupby.py::test_groupby_map_shrink_groups[obj0]", "xarray/tests/test_groupby.py::test_groupby_map_shrink_groups[obj1]", "xarray/tests/test_groupby.py::test_groupby_map_change_group_size[obj0]", "xarray/tests/test_groupby.py::test_groupby_map_change_group_size[obj1]", "xarray/tests/test_groupby.py::test_da_groupby_map_func_args", "xarray/tests/test_groupby.py::test_ds_groupby_map_func_args", "xarray/tests/test_groupby.py::test_da_groupby_empty", "xarray/tests/test_groupby.py::test_da_groupby_quantile", "xarray/tests/test_groupby.py::test_ds_groupby_quantile", "xarray/tests/test_groupby.py::test_da_groupby_assign_coords", "xarray/tests/test_groupby.py::test_groupby_drops_nans", "xarray/tests/test_groupby.py::test_groupby_grouping_errors", "xarray/tests/test_groupby.py::test_groupby_reduce_dimension_error", "xarray/tests/test_groupby.py::test_groupby_multiple_string_args", "xarray/tests/test_groupby.py::test_groupby_bins_timeseries", "xarray/tests/test_groupby.py::test_groupby_none_group_name", "xarray/tests/test_groupby.py::test_groupby_getitem"]

**Base Commit**: e56905889c836c736152b11a7e6117a229715975
**Environment Setup Commit**: 1c198a191127c601d091213c4b3292a8bb3054e1
