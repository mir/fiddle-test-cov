# mwaskom__seaborn-3190

**Repository**: mwaskom/seaborn
**Created**: 2022-12-18T17:13:51Z
**Version**: 0.12

## Problem Statement

Color mapping fails with boolean data
```python
so.Plot(["a", "b"], [1, 2], color=[True, False]).add(so.Bar())
```
```python-traceback
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
...
File ~/code/seaborn/seaborn/_core/plot.py:841, in Plot._plot(self, pyplot)
    838 plotter._compute_stats(self, layers)
    840 # Process scale spec for semantic variables and coordinates computed by stat
--> 841 plotter._setup_scales(self, common, layers)
    843 # TODO Remove these after updating other methods
    844 # ---- Maybe have debug= param that attaches these when True?
    845 plotter._data = common

File ~/code/seaborn/seaborn/_core/plot.py:1252, in Plotter._setup_scales(self, p, common, layers, variables)
   1250     self._scales[var] = Scale._identity()
   1251 else:
-> 1252     self._scales[var] = scale._setup(var_df[var], prop)
   1254 # Everything below here applies only to coordinate variables
   1255 # We additionally skip it when we're working with a value
   1256 # that is derived from a coordinate we've already processed.
   1257 # e.g., the Stat consumed y and added ymin/ymax. In that case,
   1258 # we've already setup the y scale and ymin/max are in scale space.
   1259 if axis is None or (var != coord and coord in p._variables):

File ~/code/seaborn/seaborn/_core/scales.py:351, in ContinuousBase._setup(self, data, prop, axis)
    349 vmin, vmax = axis.convert_units((vmin, vmax))
    350 a = forward(vmin)
--> 351 b = forward(vmax) - forward(vmin)
    353 def normalize(x):
    354     return (x - a) / b

TypeError: numpy boolean subtract, the `-` operator, is not supported, use the bitwise_xor, the `^` operator, or the logical_xor function instead.
```


## Hints

Would this simply mean refactoring the code to use `^` or `xor` functions instead?

## Patch

```diff

diff --git a/seaborn/_core/scales.py b/seaborn/_core/scales.py
--- a/seaborn/_core/scales.py
+++ b/seaborn/_core/scales.py
@@ -346,7 +346,7 @@ def _setup(
                 vmin, vmax = data.min(), data.max()
             else:
                 vmin, vmax = new.norm
-            vmin, vmax = axis.convert_units((vmin, vmax))
+            vmin, vmax = map(float, axis.convert_units((vmin, vmax)))
             a = forward(vmin)
             b = forward(vmax) - forward(vmin)
 


```

## Test Patch

```diff
diff --git a/tests/_core/test_scales.py b/tests/_core/test_scales.py
--- a/tests/_core/test_scales.py
+++ b/tests/_core/test_scales.py
@@ -90,6 +90,12 @@ def test_interval_with_range_norm_and_transform(self, x):
         s = Continuous((2, 3), (10, 100), "log")._setup(x, IntervalProperty())
         assert_array_equal(s(x), [1, 2, 3])
 
+    def test_interval_with_bools(self):
+
+        x = pd.Series([True, False, False])
+        s = Continuous()._setup(x, IntervalProperty())
+        assert_array_equal(s(x), [1, 0, 0])
+
     def test_color_defaults(self, x):
 
         cmap = color_palette("ch:", as_cmap=True)

```

## Test Information

**Tests that should FAIL→PASS**: ["tests/_core/test_scales.py::TestContinuous::test_interval_with_bools"]

**Tests that should PASS→PASS**: ["tests/_core/test_scales.py::TestContinuous::test_coordinate_defaults", "tests/_core/test_scales.py::TestContinuous::test_coordinate_transform", "tests/_core/test_scales.py::TestContinuous::test_coordinate_transform_with_parameter", "tests/_core/test_scales.py::TestContinuous::test_coordinate_transform_error", "tests/_core/test_scales.py::TestContinuous::test_interval_defaults", "tests/_core/test_scales.py::TestContinuous::test_interval_with_range", "tests/_core/test_scales.py::TestContinuous::test_interval_with_norm", "tests/_core/test_scales.py::TestContinuous::test_interval_with_range_norm_and_transform", "tests/_core/test_scales.py::TestContinuous::test_color_defaults", "tests/_core/test_scales.py::TestContinuous::test_color_named_values", "tests/_core/test_scales.py::TestContinuous::test_color_tuple_values", "tests/_core/test_scales.py::TestContinuous::test_color_callable_values", "tests/_core/test_scales.py::TestContinuous::test_color_with_norm", "tests/_core/test_scales.py::TestContinuous::test_color_with_transform", "tests/_core/test_scales.py::TestContinuous::test_tick_locator", "tests/_core/test_scales.py::TestContinuous::test_tick_locator_input_check", "tests/_core/test_scales.py::TestContinuous::test_tick_upto", "tests/_core/test_scales.py::TestContinuous::test_tick_every", "tests/_core/test_scales.py::TestContinuous::test_tick_every_between", "tests/_core/test_scales.py::TestContinuous::test_tick_at", "tests/_core/test_scales.py::TestContinuous::test_tick_count", "tests/_core/test_scales.py::TestContinuous::test_tick_count_between", "tests/_core/test_scales.py::TestContinuous::test_tick_minor", "tests/_core/test_scales.py::TestContinuous::test_log_tick_default", "tests/_core/test_scales.py::TestContinuous::test_log_tick_upto", "tests/_core/test_scales.py::TestContinuous::test_log_tick_count", "tests/_core/test_scales.py::TestContinuous::test_log_tick_format_disabled", "tests/_core/test_scales.py::TestContinuous::test_log_tick_every", "tests/_core/test_scales.py::TestContinuous::test_symlog_tick_default", "tests/_core/test_scales.py::TestContinuous::test_label_formatter", "tests/_core/test_scales.py::TestContinuous::test_label_like_pattern", "tests/_core/test_scales.py::TestContinuous::test_label_like_string", "tests/_core/test_scales.py::TestContinuous::test_label_like_function", "tests/_core/test_scales.py::TestContinuous::test_label_base", "tests/_core/test_scales.py::TestContinuous::test_label_unit", "tests/_core/test_scales.py::TestContinuous::test_label_unit_with_sep", "tests/_core/test_scales.py::TestContinuous::test_label_empty_unit", "tests/_core/test_scales.py::TestContinuous::test_label_base_from_transform", "tests/_core/test_scales.py::TestContinuous::test_label_type_checks", "tests/_core/test_scales.py::TestNominal::test_coordinate_defaults", "tests/_core/test_scales.py::TestNominal::test_coordinate_with_order", "tests/_core/test_scales.py::TestNominal::test_coordinate_with_subset_order", "tests/_core/test_scales.py::TestNominal::test_coordinate_axis", "tests/_core/test_scales.py::TestNominal::test_coordinate_axis_with_order", "tests/_core/test_scales.py::TestNominal::test_coordinate_axis_with_subset_order", "tests/_core/test_scales.py::TestNominal::test_coordinate_axis_with_category_dtype", "tests/_core/test_scales.py::TestNominal::test_coordinate_numeric_data", "tests/_core/test_scales.py::TestNominal::test_coordinate_numeric_data_with_order", "tests/_core/test_scales.py::TestNominal::test_color_defaults", "tests/_core/test_scales.py::TestNominal::test_color_named_palette", "tests/_core/test_scales.py::TestNominal::test_color_list_palette", "tests/_core/test_scales.py::TestNominal::test_color_dict_palette", "tests/_core/test_scales.py::TestNominal::test_color_numeric_data", "tests/_core/test_scales.py::TestNominal::test_color_numeric_with_order_subset", "tests/_core/test_scales.py::TestNominal::test_color_alpha_in_palette", "tests/_core/test_scales.py::TestNominal::test_color_unknown_palette", "tests/_core/test_scales.py::TestNominal::test_object_defaults", "tests/_core/test_scales.py::TestNominal::test_object_list", "tests/_core/test_scales.py::TestNominal::test_object_dict", "tests/_core/test_scales.py::TestNominal::test_object_order", "tests/_core/test_scales.py::TestNominal::test_object_order_subset", "tests/_core/test_scales.py::TestNominal::test_objects_that_are_weird", "tests/_core/test_scales.py::TestNominal::test_alpha_default", "tests/_core/test_scales.py::TestNominal::test_fill", "tests/_core/test_scales.py::TestNominal::test_fill_dict", "tests/_core/test_scales.py::TestNominal::test_fill_nunique_warning", "tests/_core/test_scales.py::TestNominal::test_interval_defaults", "tests/_core/test_scales.py::TestNominal::test_interval_tuple", "tests/_core/test_scales.py::TestNominal::test_interval_tuple_numeric", "tests/_core/test_scales.py::TestNominal::test_interval_list", "tests/_core/test_scales.py::TestNominal::test_interval_dict", "tests/_core/test_scales.py::TestNominal::test_interval_with_transform", "tests/_core/test_scales.py::TestNominal::test_empty_data", "tests/_core/test_scales.py::TestTemporal::test_coordinate_defaults", "tests/_core/test_scales.py::TestTemporal::test_interval_defaults", "tests/_core/test_scales.py::TestTemporal::test_interval_with_range", "tests/_core/test_scales.py::TestTemporal::test_interval_with_norm", "tests/_core/test_scales.py::TestTemporal::test_color_defaults", "tests/_core/test_scales.py::TestTemporal::test_color_named_values", "tests/_core/test_scales.py::TestTemporal::test_coordinate_axis", "tests/_core/test_scales.py::TestTemporal::test_tick_locator", "tests/_core/test_scales.py::TestTemporal::test_tick_upto", "tests/_core/test_scales.py::TestTemporal::test_label_formatter", "tests/_core/test_scales.py::TestTemporal::test_label_concise"]

**Base Commit**: 4a9e54962a29c12a8b103d75f838e0e795a6974d
**Environment Setup Commit**: d25872b0fc99dbf7e666a91f59bd4ed125186aa1
