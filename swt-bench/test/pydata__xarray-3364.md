# pydata__xarray-3364

**Repository**: pydata/xarray
**Created**: 2019-10-01T21:15:54Z
**Version**: 0.12

## Problem Statement

Ignore missing variables when concatenating datasets?
Several users (@raj-kesavan, @richardotis, now myself) have wondered about how to concatenate xray Datasets with different variables.

With the current `xray.concat`, you need to awkwardly create dummy variables filled with `NaN` in datasets that don't have them (or drop mismatched variables entirely). Neither of these are great options -- `concat` should have an option (the default?) to take care of this for the user.

This would also be more consistent with `pd.concat`, which takes a more relaxed approach to matching dataframes with different variables (it does an outer join).



## Hints

Closing as stale, please reopen if still relevant

## Patch

```diff

diff --git a/xarray/core/concat.py b/xarray/core/concat.py
--- a/xarray/core/concat.py
+++ b/xarray/core/concat.py
@@ -312,15 +312,9 @@ def _dataset_concat(
         to_merge = {var: [] for var in variables_to_merge}
 
         for ds in datasets:
-            absent_merge_vars = variables_to_merge - set(ds.variables)
-            if absent_merge_vars:
-                raise ValueError(
-                    "variables %r are present in some datasets but not others. "
-                    % absent_merge_vars
-                )
-
             for var in variables_to_merge:
-                to_merge[var].append(ds.variables[var])
+                if var in ds:
+                    to_merge[var].append(ds.variables[var])
 
         for var in variables_to_merge:
             result_vars[var] = unique_variable(


```

## Test Patch

```diff
diff --git a/xarray/tests/test_combine.py b/xarray/tests/test_combine.py
--- a/xarray/tests/test_combine.py
+++ b/xarray/tests/test_combine.py
@@ -782,12 +782,11 @@ def test_auto_combine_previously_failed(self):
         actual = auto_combine(datasets, concat_dim="t")
         assert_identical(expected, actual)
 
-    def test_auto_combine_still_fails(self):
-        # concat can't handle new variables (yet):
-        # https://github.com/pydata/xarray/issues/508
+    def test_auto_combine_with_new_variables(self):
         datasets = [Dataset({"x": 0}, {"y": 0}), Dataset({"x": 1}, {"y": 1, "z": 1})]
-        with pytest.raises(ValueError):
-            auto_combine(datasets, "y")
+        actual = auto_combine(datasets, "y")
+        expected = Dataset({"x": ("y", [0, 1])}, {"y": [0, 1], "z": 1})
+        assert_identical(expected, actual)
 
     def test_auto_combine_no_concat(self):
         objs = [Dataset({"x": 0}), Dataset({"y": 1})]
diff --git a/xarray/tests/test_concat.py b/xarray/tests/test_concat.py
--- a/xarray/tests/test_concat.py
+++ b/xarray/tests/test_concat.py
@@ -68,6 +68,22 @@ def test_concat_simple(self, data, dim, coords):
         datasets = [g for _, g in data.groupby(dim, squeeze=False)]
         assert_identical(data, concat(datasets, dim, coords=coords))
 
+    def test_concat_merge_variables_present_in_some_datasets(self, data):
+        # coordinates present in some datasets but not others
+        ds1 = Dataset(data_vars={"a": ("y", [0.1])}, coords={"x": 0.1})
+        ds2 = Dataset(data_vars={"a": ("y", [0.2])}, coords={"z": 0.2})
+        actual = concat([ds1, ds2], dim="y", coords="minimal")
+        expected = Dataset({"a": ("y", [0.1, 0.2])}, coords={"x": 0.1, "z": 0.2})
+        assert_identical(expected, actual)
+
+        # data variables present in some datasets but not others
+        split_data = [data.isel(dim1=slice(3)), data.isel(dim1=slice(3, None))]
+        data0, data1 = deepcopy(split_data)
+        data1["foo"] = ("bar", np.random.randn(10))
+        actual = concat([data0, data1], "dim1")
+        expected = data.copy().assign(foo=data1.foo)
+        assert_identical(expected, actual)
+
     def test_concat_2(self, data):
         dim = "dim2"
         datasets = [g for _, g in data.groupby(dim, squeeze=True)]
@@ -190,11 +206,6 @@ def test_concat_errors(self):
             concat([data0, data1], "dim1", compat="identical")
         assert_identical(data, concat([data0, data1], "dim1", compat="equals"))
 
-        with raises_regex(ValueError, "present in some datasets"):
-            data0, data1 = deepcopy(split_data)
-            data1["foo"] = ("bar", np.random.randn(10))
-            concat([data0, data1], "dim1")
-
         with raises_regex(ValueError, "compat.* invalid"):
             concat(split_data, "dim1", compat="foobar")
 

```

## Test Information

**Tests that should FAIL→PASS**: ["xarray/tests/test_combine.py::TestAutoCombineOldAPI::test_auto_combine_with_new_variables", "xarray/tests/test_concat.py::TestConcatDataset::test_concat_merge_variables_present_in_some_datasets"]

**Tests that should PASS→PASS**: ["xarray/tests/test_combine.py::TestTileIDsFromNestedList::test_1d", "xarray/tests/test_combine.py::TestTileIDsFromNestedList::test_2d", "xarray/tests/test_combine.py::TestTileIDsFromNestedList::test_3d", "xarray/tests/test_combine.py::TestTileIDsFromNestedList::test_single_dataset", "xarray/tests/test_combine.py::TestTileIDsFromNestedList::test_redundant_nesting", "xarray/tests/test_combine.py::TestTileIDsFromNestedList::test_ignore_empty_list", "xarray/tests/test_combine.py::TestTileIDsFromNestedList::test_uneven_depth_input", "xarray/tests/test_combine.py::TestTileIDsFromNestedList::test_uneven_length_input", "xarray/tests/test_combine.py::TestTileIDsFromNestedList::test_infer_from_datasets", "xarray/tests/test_combine.py::TestTileIDsFromCoords::test_1d", "xarray/tests/test_combine.py::TestTileIDsFromCoords::test_2d", "xarray/tests/test_combine.py::TestTileIDsFromCoords::test_no_dimension_coords", "xarray/tests/test_combine.py::TestTileIDsFromCoords::test_coord_not_monotonic", "xarray/tests/test_combine.py::TestTileIDsFromCoords::test_coord_monotonically_decreasing", "xarray/tests/test_combine.py::TestTileIDsFromCoords::test_no_concatenation_needed", "xarray/tests/test_combine.py::TestTileIDsFromCoords::test_2d_plus_bystander_dim", "xarray/tests/test_combine.py::TestTileIDsFromCoords::test_string_coords", "xarray/tests/test_combine.py::TestTileIDsFromCoords::test_lexicographic_sort_string_coords", "xarray/tests/test_combine.py::TestTileIDsFromCoords::test_datetime_coords", "xarray/tests/test_combine.py::TestNewTileIDs::test_new_tile_id[old_id0-new_id0]", "xarray/tests/test_combine.py::TestNewTileIDs::test_new_tile_id[old_id1-new_id1]", "xarray/tests/test_combine.py::TestNewTileIDs::test_new_tile_id[old_id2-new_id2]", "xarray/tests/test_combine.py::TestNewTileIDs::test_new_tile_id[old_id3-new_id3]", "xarray/tests/test_combine.py::TestNewTileIDs::test_new_tile_id[old_id4-new_id4]", "xarray/tests/test_combine.py::TestNewTileIDs::test_get_new_tile_ids", "xarray/tests/test_combine.py::TestCombineND::test_concat_once[dim1]", "xarray/tests/test_combine.py::TestCombineND::test_concat_once[new_dim]", "xarray/tests/test_combine.py::TestCombineND::test_concat_only_first_dim", "xarray/tests/test_combine.py::TestCombineND::test_concat_twice[dim1]", "xarray/tests/test_combine.py::TestCombineND::test_concat_twice[new_dim]", "xarray/tests/test_combine.py::TestCheckShapeTileIDs::test_check_depths", "xarray/tests/test_combine.py::TestCheckShapeTileIDs::test_check_lengths", "xarray/tests/test_combine.py::TestNestedCombine::test_nested_concat", "xarray/tests/test_combine.py::TestNestedCombine::test_combine_nested_join[outer-expected0]", "xarray/tests/test_combine.py::TestNestedCombine::test_combine_nested_join[inner-expected1]", "xarray/tests/test_combine.py::TestNestedCombine::test_combine_nested_join[left-expected2]", "xarray/tests/test_combine.py::TestNestedCombine::test_combine_nested_join[right-expected3]", "xarray/tests/test_combine.py::TestNestedCombine::test_combine_nested_join_exact", "xarray/tests/test_combine.py::TestNestedCombine::test_empty_input", "xarray/tests/test_combine.py::TestNestedCombine::test_nested_concat_along_new_dim", "xarray/tests/test_combine.py::TestNestedCombine::test_nested_merge", "xarray/tests/test_combine.py::TestNestedCombine::test_concat_multiple_dims", "xarray/tests/test_combine.py::TestNestedCombine::test_concat_name_symmetry", "xarray/tests/test_combine.py::TestNestedCombine::test_concat_one_dim_merge_another", "xarray/tests/test_combine.py::TestNestedCombine::test_auto_combine_2d", "xarray/tests/test_combine.py::TestNestedCombine::test_combine_nested_missing_data_new_dim", "xarray/tests/test_combine.py::TestNestedCombine::test_invalid_hypercube_input", "xarray/tests/test_combine.py::TestNestedCombine::test_merge_one_dim_concat_another", "xarray/tests/test_combine.py::TestNestedCombine::test_combine_concat_over_redundant_nesting", "xarray/tests/test_combine.py::TestNestedCombine::test_combine_nested_fill_value[fill_value0]", "xarray/tests/test_combine.py::TestNestedCombine::test_combine_nested_fill_value[2]", "xarray/tests/test_combine.py::TestNestedCombine::test_combine_nested_fill_value[2.0]", "xarray/tests/test_combine.py::TestCombineAuto::test_combine_by_coords", "xarray/tests/test_combine.py::TestCombineAuto::test_combine_coords_join[outer-expected0]", "xarray/tests/test_combine.py::TestCombineAuto::test_combine_coords_join[inner-expected1]", "xarray/tests/test_combine.py::TestCombineAuto::test_combine_coords_join[left-expected2]", "xarray/tests/test_combine.py::TestCombineAuto::test_combine_coords_join[right-expected3]", "xarray/tests/test_combine.py::TestCombineAuto::test_combine_coords_join_exact", "xarray/tests/test_combine.py::TestCombineAuto::test_infer_order_from_coords", "xarray/tests/test_combine.py::TestCombineAuto::test_combine_leaving_bystander_dimensions", "xarray/tests/test_combine.py::TestCombineAuto::test_combine_by_coords_previously_failed", "xarray/tests/test_combine.py::TestCombineAuto::test_combine_by_coords_still_fails", "xarray/tests/test_combine.py::TestCombineAuto::test_combine_by_coords_no_concat", "xarray/tests/test_combine.py::TestCombineAuto::test_check_for_impossible_ordering", "xarray/tests/test_combine.py::TestAutoCombineOldAPI::test_auto_combine", "xarray/tests/test_combine.py::TestAutoCombineOldAPI::test_auto_combine_previously_failed", "xarray/tests/test_combine.py::TestAutoCombineOldAPI::test_auto_combine_no_concat", "xarray/tests/test_combine.py::TestAutoCombineOldAPI::test_auto_combine_order_by_appearance_not_coords", "xarray/tests/test_combine.py::TestAutoCombineOldAPI::test_auto_combine_fill_value[fill_value0]", "xarray/tests/test_combine.py::TestAutoCombineOldAPI::test_auto_combine_fill_value[2]", "xarray/tests/test_combine.py::TestAutoCombineOldAPI::test_auto_combine_fill_value[2.0]", "xarray/tests/test_combine.py::TestAutoCombineDeprecation::test_auto_combine_with_concat_dim", "xarray/tests/test_combine.py::TestAutoCombineDeprecation::test_auto_combine_with_merge_and_concat", "xarray/tests/test_combine.py::TestAutoCombineDeprecation::test_auto_combine_with_coords", "xarray/tests/test_combine.py::TestAutoCombineDeprecation::test_auto_combine_without_coords", "xarray/tests/test_concat.py::test_concat_compat", "xarray/tests/test_concat.py::TestConcatDataset::test_concat_simple[dim1-different]", "xarray/tests/test_concat.py::TestConcatDataset::test_concat_simple[dim1-minimal]", "xarray/tests/test_concat.py::TestConcatDataset::test_concat_simple[dim2-different]", "xarray/tests/test_concat.py::TestConcatDataset::test_concat_simple[dim2-minimal]", "xarray/tests/test_concat.py::TestConcatDataset::test_concat_2", "xarray/tests/test_concat.py::TestConcatDataset::test_concat_coords_kwarg[dim1-different]", "xarray/tests/test_concat.py::TestConcatDataset::test_concat_coords_kwarg[dim1-minimal]", "xarray/tests/test_concat.py::TestConcatDataset::test_concat_coords_kwarg[dim1-all]", "xarray/tests/test_concat.py::TestConcatDataset::test_concat_coords_kwarg[dim2-different]", "xarray/tests/test_concat.py::TestConcatDataset::test_concat_coords_kwarg[dim2-minimal]", "xarray/tests/test_concat.py::TestConcatDataset::test_concat_coords_kwarg[dim2-all]", "xarray/tests/test_concat.py::TestConcatDataset::test_concat", "xarray/tests/test_concat.py::TestConcatDataset::test_concat_dim_precedence", "xarray/tests/test_concat.py::TestConcatDataset::test_concat_data_vars", "xarray/tests/test_concat.py::TestConcatDataset::test_concat_coords", "xarray/tests/test_concat.py::TestConcatDataset::test_concat_constant_index", "xarray/tests/test_concat.py::TestConcatDataset::test_concat_size0", "xarray/tests/test_concat.py::TestConcatDataset::test_concat_autoalign", "xarray/tests/test_concat.py::TestConcatDataset::test_concat_errors", "xarray/tests/test_concat.py::TestConcatDataset::test_concat_join_kwarg", "xarray/tests/test_concat.py::TestConcatDataset::test_concat_promote_shape", "xarray/tests/test_concat.py::TestConcatDataset::test_concat_do_not_promote", "xarray/tests/test_concat.py::TestConcatDataset::test_concat_dim_is_variable", "xarray/tests/test_concat.py::TestConcatDataset::test_concat_multiindex", "xarray/tests/test_concat.py::TestConcatDataset::test_concat_fill_value[fill_value0]", "xarray/tests/test_concat.py::TestConcatDataset::test_concat_fill_value[2]", "xarray/tests/test_concat.py::TestConcatDataset::test_concat_fill_value[2.0]", "xarray/tests/test_concat.py::TestConcatDataArray::test_concat", "xarray/tests/test_concat.py::TestConcatDataArray::test_concat_encoding", "xarray/tests/test_concat.py::TestConcatDataArray::test_concat_lazy", "xarray/tests/test_concat.py::TestConcatDataArray::test_concat_fill_value[fill_value0]", "xarray/tests/test_concat.py::TestConcatDataArray::test_concat_fill_value[2]", "xarray/tests/test_concat.py::TestConcatDataArray::test_concat_fill_value[2.0]", "xarray/tests/test_concat.py::TestConcatDataArray::test_concat_join_kwarg"]

**Base Commit**: 863e49066ca4d61c9adfe62aca3bf21b90e1af8c
**Environment Setup Commit**: 1c198a191127c601d091213c4b3292a8bb3054e1
