# pvlib__pvlib-python-1072

**Repository**: pvlib/pvlib-python
**Created**: 2020-10-01T00:53:14Z
**Version**: 0.7

## Problem Statement

temperature.fuentes errors when given tz-aware inputs on pandas>=1.0.0
**Describe the bug**
When the weather timeseries inputs to `temperature.fuentes` have tz-aware index, an internal call to `np.diff(index)` returns an array of `Timedelta` objects instead of an array of nanosecond ints, throwing an error immediately after.  The error only happens when using pandas>=1.0.0; using 0.25.3 runs successfully, but emits the warning:

```
  /home/kevin/anaconda3/envs/pvlib-dev/lib/python3.7/site-packages/numpy/lib/function_base.py:1243: FutureWarning: Converting timezone-aware DatetimeArray to timezone-naive ndarray with 'datetime64[ns]' dtype. In the future, this will return an ndarray with 'object' dtype where each element is a 'pandas.Timestamp' with the correct 'tz'.
  	To accept the future behavior, pass 'dtype=object'.
  	To keep the old behavior, pass 'dtype="datetime64[ns]"'.
    a = asanyarray(a)
```

**To Reproduce**
```python
In [1]: import pvlib
   ...: import pandas as pd
   ...: 
   ...: index_naive = pd.date_range('2019-01-01', freq='h', periods=3)
   ...: 
   ...: kwargs = {
   ...:     'poa_global': pd.Series(1000, index_naive),
   ...:     'temp_air': pd.Series(20, index_naive),
   ...:     'wind_speed': pd.Series(1, index_naive),
   ...:     'noct_installed': 45
   ...: }
   ...: 

In [2]: print(pvlib.temperature.fuentes(**kwargs))
2019-01-01 00:00:00    47.85
2019-01-01 01:00:00    50.85
2019-01-01 02:00:00    50.85
Freq: H, Name: tmod, dtype: float64

In [3]: kwargs['poa_global'].index = index_naive.tz_localize('UTC')
   ...: print(pvlib.temperature.fuentes(**kwargs))
   ...: 
Traceback (most recent call last):

  File "<ipython-input-3-ff99badadc91>", line 2, in <module>
    print(pvlib.temperature.fuentes(**kwargs))

  File "/home/kevin/anaconda3/lib/python3.7/site-packages/pvlib/temperature.py", line 602, in fuentes
    timedelta_hours = np.diff(poa_global.index).astype(float) / 1e9 / 60 / 60

TypeError: float() argument must be a string or a number, not 'Timedelta'
```

**Expected behavior**
`temperature.fuentes` should work with both tz-naive and tz-aware inputs.


**Versions:**
 - ``pvlib.__version__``: 0.8.0
 - ``pandas.__version__``: 1.0.0+
 - python: 3.7.4 (default, Aug 13 2019, 20:35:49) \n[GCC 7.3.0]




## Patch

```diff

diff --git a/pvlib/temperature.py b/pvlib/temperature.py
--- a/pvlib/temperature.py
+++ b/pvlib/temperature.py
@@ -599,8 +599,9 @@ def fuentes(poa_global, temp_air, wind_speed, noct_installed, module_height=5,
     # n.b. the way Fuentes calculates the first timedelta makes it seem like
     # the value doesn't matter -- rather than recreate it here, just assume
     # it's the same as the second timedelta:
-    timedelta_hours = np.diff(poa_global.index).astype(float) / 1e9 / 60 / 60
-    timedelta_hours = np.append([timedelta_hours[0]], timedelta_hours)
+    timedelta_seconds = poa_global.index.to_series().diff().dt.total_seconds()
+    timedelta_hours = timedelta_seconds / 3600
+    timedelta_hours.iloc[0] = timedelta_hours.iloc[1]
 
     tamb_array = temp_air + 273.15
     sun_array = poa_global * absorp


```

## Test Patch

```diff
diff --git a/pvlib/tests/test_temperature.py b/pvlib/tests/test_temperature.py
--- a/pvlib/tests/test_temperature.py
+++ b/pvlib/tests/test_temperature.py
@@ -190,3 +190,17 @@ def test_fuentes(filename, inoct):
     night_difference = expected_tcell[is_night] - actual_tcell[is_night]
     assert night_difference.max() < 6
     assert night_difference.min() > 0
+
+
+@pytest.mark.parametrize('tz', [None, 'Etc/GMT+5'])
+def test_fuentes_timezone(tz):
+    index = pd.date_range('2019-01-01', freq='h', periods=3, tz=tz)
+
+    df = pd.DataFrame({'poa_global': 1000, 'temp_air': 20, 'wind_speed': 1},
+                      index)
+
+    out = temperature.fuentes(df['poa_global'], df['temp_air'],
+                              df['wind_speed'], noct_installed=45)
+
+    assert_series_equal(out, pd.Series([47.85, 50.85, 50.85], index=index,
+                                       name='tmod'))

```

## Test Information

**Tests that should FAIL→PASS**: ["pvlib/tests/test_temperature.py::test_fuentes_timezone[Etc/GMT+5]"]

**Tests that should PASS→PASS**: ["pvlib/tests/test_temperature.py::test_sapm_cell", "pvlib/tests/test_temperature.py::test_sapm_module", "pvlib/tests/test_temperature.py::test_sapm_cell_from_module", "pvlib/tests/test_temperature.py::test_sapm_ndarray", "pvlib/tests/test_temperature.py::test_sapm_series", "pvlib/tests/test_temperature.py::test_pvsyst_cell_default", "pvlib/tests/test_temperature.py::test_pvsyst_cell_kwargs", "pvlib/tests/test_temperature.py::test_pvsyst_cell_ndarray", "pvlib/tests/test_temperature.py::test_pvsyst_cell_series", "pvlib/tests/test_temperature.py::test_faiman_default", "pvlib/tests/test_temperature.py::test_faiman_kwargs", "pvlib/tests/test_temperature.py::test_faiman_list", "pvlib/tests/test_temperature.py::test_faiman_ndarray", "pvlib/tests/test_temperature.py::test_faiman_series", "pvlib/tests/test_temperature.py::test__temperature_model_params", "pvlib/tests/test_temperature.py::test_fuentes[pvwatts_8760_rackmount.csv-45]", "pvlib/tests/test_temperature.py::test_fuentes[pvwatts_8760_roofmount.csv-49]", "pvlib/tests/test_temperature.py::test_fuentes_timezone[None]"]

**Base Commit**: 04a523fafbd61bc2e49420963b84ed8e2bd1b3cf
**Environment Setup Commit**: 6e5148f59c5050e8f7a0084b7ae39e93b80f72e6
