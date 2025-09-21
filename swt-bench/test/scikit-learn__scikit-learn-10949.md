# scikit-learn__scikit-learn-10949

**Repository**: scikit-learn/scikit-learn
**Created**: 2018-04-10T15:30:56Z
**Version**: 0.20

## Problem Statement

warn_on_dtype with DataFrame
#### Description

``warn_on_dtype`` has no effect when input is a pandas ``DataFrame``

#### Steps/Code to Reproduce
```python
from sklearn.utils.validation import check_array
import pandas as pd
df = pd.DataFrame([[1, 2, 3], [2, 3, 4]], dtype=object)
checked = check_array(df, warn_on_dtype=True)
```

#### Expected result: 

```python-traceback
DataConversionWarning: Data with input dtype object was converted to float64.
```

#### Actual Results
No warning is thrown

#### Versions
Linux-4.4.0-116-generic-x86_64-with-debian-stretch-sid
Python 3.6.3 |Anaconda, Inc.| (default, Nov  3 2017, 19:19:16) 
[GCC 7.2.0]
NumPy 1.13.1
SciPy 0.19.1
Scikit-Learn 0.20.dev0
Pandas 0.21.0

warn_on_dtype with DataFrame
#### Description

``warn_on_dtype`` has no effect when input is a pandas ``DataFrame``

#### Steps/Code to Reproduce
```python
from sklearn.utils.validation import check_array
import pandas as pd
df = pd.DataFrame([[1, 2, 3], [2, 3, 4]], dtype=object)
checked = check_array(df, warn_on_dtype=True)
```

#### Expected result: 

```python-traceback
DataConversionWarning: Data with input dtype object was converted to float64.
```

#### Actual Results
No warning is thrown

#### Versions
Linux-4.4.0-116-generic-x86_64-with-debian-stretch-sid
Python 3.6.3 |Anaconda, Inc.| (default, Nov  3 2017, 19:19:16) 
[GCC 7.2.0]
NumPy 1.13.1
SciPy 0.19.1
Scikit-Learn 0.20.dev0
Pandas 0.21.0



## Patch

```diff

diff --git a/sklearn/utils/validation.py b/sklearn/utils/validation.py
--- a/sklearn/utils/validation.py
+++ b/sklearn/utils/validation.py
@@ -466,6 +466,12 @@ def check_array(array, accept_sparse=False, accept_large_sparse=True,
         # not a data type (e.g. a column named dtype in a pandas DataFrame)
         dtype_orig = None
 
+    # check if the object contains several dtypes (typically a pandas
+    # DataFrame), and store them. If not, store None.
+    dtypes_orig = None
+    if hasattr(array, "dtypes") and hasattr(array, "__array__"):
+        dtypes_orig = np.array(array.dtypes)
+
     if dtype_numeric:
         if dtype_orig is not None and dtype_orig.kind == "O":
             # if input is object, convert to float.
@@ -581,6 +587,16 @@ def check_array(array, accept_sparse=False, accept_large_sparse=True,
     if copy and np.may_share_memory(array, array_orig):
         array = np.array(array, dtype=dtype, order=order)
 
+    if (warn_on_dtype and dtypes_orig is not None and
+            {array.dtype} != set(dtypes_orig)):
+        # if there was at the beginning some other types than the final one
+        # (for instance in a DataFrame that can contain several dtypes) then
+        # some data must have been converted
+        msg = ("Data with input dtype %s were all converted to %s%s."
+               % (', '.join(map(str, sorted(set(dtypes_orig)))), array.dtype,
+                  context))
+        warnings.warn(msg, DataConversionWarning, stacklevel=3)
+
     return array
 
 


```

## Test Patch

```diff
diff --git a/sklearn/utils/tests/test_validation.py b/sklearn/utils/tests/test_validation.py
--- a/sklearn/utils/tests/test_validation.py
+++ b/sklearn/utils/tests/test_validation.py
@@ -7,6 +7,7 @@
 from itertools import product
 
 import pytest
+from pytest import importorskip
 import numpy as np
 import scipy.sparse as sp
 from scipy import __version__ as scipy_version
@@ -713,6 +714,38 @@ def test_suppress_validation():
     assert_raises(ValueError, assert_all_finite, X)
 
 
+def test_check_dataframe_warns_on_dtype():
+    # Check that warn_on_dtype also works for DataFrames.
+    # https://github.com/scikit-learn/scikit-learn/issues/10948
+    pd = importorskip("pandas")
+
+    df = pd.DataFrame([[1, 2, 3], [4, 5, 6]], dtype=object)
+    assert_warns_message(DataConversionWarning,
+                         "Data with input dtype object were all converted to "
+                         "float64.",
+                         check_array, df, dtype=np.float64, warn_on_dtype=True)
+    assert_warns(DataConversionWarning, check_array, df,
+                 dtype='numeric', warn_on_dtype=True)
+    assert_no_warnings(check_array, df, dtype='object', warn_on_dtype=True)
+
+    # Also check that it raises a warning for mixed dtypes in a DataFrame.
+    df_mixed = pd.DataFrame([['1', 2, 3], ['4', 5, 6]])
+    assert_warns(DataConversionWarning, check_array, df_mixed,
+                 dtype=np.float64, warn_on_dtype=True)
+    assert_warns(DataConversionWarning, check_array, df_mixed,
+                 dtype='numeric', warn_on_dtype=True)
+    assert_warns(DataConversionWarning, check_array, df_mixed,
+                 dtype=object, warn_on_dtype=True)
+
+    # Even with numerical dtypes, a conversion can be made because dtypes are
+    # uniformized throughout the array.
+    df_mixed_numeric = pd.DataFrame([[1., 2, 3], [4., 5, 6]])
+    assert_warns(DataConversionWarning, check_array, df_mixed_numeric,
+                 dtype='numeric', warn_on_dtype=True)
+    assert_no_warnings(check_array, df_mixed_numeric.astype(int),
+                       dtype='numeric', warn_on_dtype=True)
+
+
 class DummyMemory(object):
     def cache(self, func):
         return func

```

## Test Information

**Tests that should FAIL→PASS**: ["sklearn/utils/tests/test_validation.py::test_check_dataframe_warns_on_dtype"]

**Tests that should PASS→PASS**: ["sklearn/utils/tests/test_validation.py::test_as_float_array", "sklearn/utils/tests/test_validation.py::test_as_float_array_nan[X0]", "sklearn/utils/tests/test_validation.py::test_as_float_array_nan[X1]", "sklearn/utils/tests/test_validation.py::test_np_matrix", "sklearn/utils/tests/test_validation.py::test_memmap", "sklearn/utils/tests/test_validation.py::test_ordering", "sklearn/utils/tests/test_validation.py::test_check_array_force_all_finite_valid[asarray-inf-False]", "sklearn/utils/tests/test_validation.py::test_check_array_force_all_finite_valid[asarray-nan-allow-nan]", "sklearn/utils/tests/test_validation.py::test_check_array_force_all_finite_valid[asarray-nan-False]", "sklearn/utils/tests/test_validation.py::test_check_array_force_all_finite_valid[csr_matrix-inf-False]", "sklearn/utils/tests/test_validation.py::test_check_array_force_all_finite_valid[csr_matrix-nan-allow-nan]", "sklearn/utils/tests/test_validation.py::test_check_array_force_all_finite_valid[csr_matrix-nan-False]", "sklearn/utils/tests/test_validation.py::test_check_array", "sklearn/utils/tests/test_validation.py::test_check_array_pandas_dtype_object_conversion", "sklearn/utils/tests/test_validation.py::test_check_array_on_mock_dataframe", "sklearn/utils/tests/test_validation.py::test_check_array_dtype_stability", "sklearn/utils/tests/test_validation.py::test_check_array_dtype_warning", "sklearn/utils/tests/test_validation.py::test_check_array_accept_sparse_type_exception", "sklearn/utils/tests/test_validation.py::test_check_array_accept_sparse_no_exception", "sklearn/utils/tests/test_validation.py::test_check_array_accept_large_sparse_no_exception[csr]", "sklearn/utils/tests/test_validation.py::test_check_array_accept_large_sparse_no_exception[csc]", "sklearn/utils/tests/test_validation.py::test_check_array_accept_large_sparse_no_exception[coo]", "sklearn/utils/tests/test_validation.py::test_check_array_accept_large_sparse_no_exception[bsr]", "sklearn/utils/tests/test_validation.py::test_check_array_accept_large_sparse_raise_exception[csr]", "sklearn/utils/tests/test_validation.py::test_check_array_accept_large_sparse_raise_exception[csc]", "sklearn/utils/tests/test_validation.py::test_check_array_accept_large_sparse_raise_exception[coo]", "sklearn/utils/tests/test_validation.py::test_check_array_accept_large_sparse_raise_exception[bsr]", "sklearn/utils/tests/test_validation.py::test_check_array_large_indices_non_supported_scipy_version[csr]", "sklearn/utils/tests/test_validation.py::test_check_array_large_indices_non_supported_scipy_version[csc]", "sklearn/utils/tests/test_validation.py::test_check_array_large_indices_non_supported_scipy_version[coo]", "sklearn/utils/tests/test_validation.py::test_check_array_large_indices_non_supported_scipy_version[bsr]", "sklearn/utils/tests/test_validation.py::test_check_array_min_samples_and_features_messages", "sklearn/utils/tests/test_validation.py::test_check_array_complex_data_error", "sklearn/utils/tests/test_validation.py::test_has_fit_parameter", "sklearn/utils/tests/test_validation.py::test_check_symmetric", "sklearn/utils/tests/test_validation.py::test_check_is_fitted", "sklearn/utils/tests/test_validation.py::test_check_consistent_length", "sklearn/utils/tests/test_validation.py::test_check_dataframe_fit_attribute", "sklearn/utils/tests/test_validation.py::test_suppress_validation", "sklearn/utils/tests/test_validation.py::test_check_memory", "sklearn/utils/tests/test_validation.py::test_check_array_memmap[True]", "sklearn/utils/tests/test_validation.py::test_check_array_memmap[False]"]

**Base Commit**: 3b5abf76597ce6aff76192869f92647c1b5259e7
**Environment Setup Commit**: 55bf5d93e5674f13a1134d93a11fd0cd11aabcd1
