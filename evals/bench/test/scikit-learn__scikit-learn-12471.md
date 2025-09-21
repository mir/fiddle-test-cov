# scikit-learn__scikit-learn-12471

**Repository**: scikit-learn/scikit-learn
**Created**: 2018-10-27T10:43:48Z
**Version**: 0.21

## Problem Statement

OneHotEncoder ignore unknown error when categories are strings 
#### Description

This bug is very specific, but it happens when you set OneHotEncoder to ignore unknown entries.
and your labels are strings. The memory of the arrays is not handled safely and it can lead to a ValueError

Basically, when you call the transform method it will sets all the unknown strings on your array to OneHotEncoder.categories_[i][0] which is the first category alphabetically sorted given for fit
If this OneHotEncoder.categories_[i][0] is a long string, and the array that you want to transform has small strings, then it is impossible to fit the whole  OneHotEncoder.categories_[i][0] into the entries of the array we want to transform. So  OneHotEncoder.categories_[i][0]  is truncated and this raise the ValueError.



#### Steps/Code to Reproduce
```

import numpy as np
from sklearn.preprocessing import OneHotEncoder


# It needs to be numpy arrays, the error does not appear 
# is you have lists of lists because it gets treated like an array of objects.
train  = np.array([ '22','333','4444','11111111' ]).reshape((-1,1))
test   = np.array([ '55555',  '22' ]).reshape((-1,1))

ohe = OneHotEncoder(dtype=bool,handle_unknown='ignore')

ohe.fit( train )
enc_test = ohe.transform( test )

```


#### Expected Results
Here we should get an sparse matrix 2x4 false everywhere except at (1,1) the '22' that is known

#### Actual Results

> ValueError: y contains previously unseen labels: ['111111']


#### Versions
System:
    python: 2.7.12 (default, Dec  4 2017, 14:50:18)  [GCC 5.4.0 20160609]
   machine: Linux-4.4.0-138-generic-x86_64-with-Ubuntu-16.04-xenial
executable: /usr/bin/python

BLAS:
    macros: HAVE_CBLAS=None
cblas_libs: openblas, openblas
  lib_dirs: /usr/lib

Python deps:
    Cython: 0.25.2
     scipy: 0.18.1
setuptools: 36.7.0
       pip: 9.0.1
     numpy: 1.15.2
    pandas: 0.19.1
   sklearn: 0.21.dev0



#### Comments

I already implemented a fix for this issue, where I check the size of the elements in the array before, and I cast them into objects if necessary.


## Patch

```diff

diff --git a/sklearn/preprocessing/_encoders.py b/sklearn/preprocessing/_encoders.py
--- a/sklearn/preprocessing/_encoders.py
+++ b/sklearn/preprocessing/_encoders.py
@@ -110,7 +110,14 @@ def _transform(self, X, handle_unknown='error'):
                     # continue `The rows are marked `X_mask` and will be
                     # removed later.
                     X_mask[:, i] = valid_mask
-                    Xi = Xi.copy()
+                    # cast Xi into the largest string type necessary
+                    # to handle different lengths of numpy strings
+                    if (self.categories_[i].dtype.kind in ('U', 'S')
+                            and self.categories_[i].itemsize > Xi.itemsize):
+                        Xi = Xi.astype(self.categories_[i].dtype)
+                    else:
+                        Xi = Xi.copy()
+
                     Xi[~valid_mask] = self.categories_[i][0]
             _, encoded = _encode(Xi, self.categories_[i], encode=True)
             X_int[:, i] = encoded


```

## Test Patch

```diff
diff --git a/sklearn/preprocessing/tests/test_encoders.py b/sklearn/preprocessing/tests/test_encoders.py
--- a/sklearn/preprocessing/tests/test_encoders.py
+++ b/sklearn/preprocessing/tests/test_encoders.py
@@ -273,6 +273,23 @@ def test_one_hot_encoder_no_categorical_features():
     assert enc.categories_ == []
 
 
+def test_one_hot_encoder_handle_unknown_strings():
+    X = np.array(['11111111', '22', '333', '4444']).reshape((-1, 1))
+    X2 = np.array(['55555', '22']).reshape((-1, 1))
+    # Non Regression test for the issue #12470
+    # Test the ignore option, when categories are numpy string dtype
+    # particularly when the known category strings are larger
+    # than the unknown category strings
+    oh = OneHotEncoder(handle_unknown='ignore')
+    oh.fit(X)
+    X2_passed = X2.copy()
+    assert_array_equal(
+        oh.transform(X2_passed).toarray(),
+        np.array([[0.,  0.,  0.,  0.], [0.,  1.,  0.,  0.]]))
+    # ensure transformed data was not modified in place
+    assert_array_equal(X2, X2_passed)
+
+
 @pytest.mark.parametrize("output_dtype", [np.int32, np.float32, np.float64])
 @pytest.mark.parametrize("input_dtype", [np.int32, np.float32, np.float64])
 def test_one_hot_encoder_dtype(input_dtype, output_dtype):

```

## Test Information

**Tests that should FAIL→PASS**: ["sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_handle_unknown_strings"]

**Tests that should PASS→PASS**: ["sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_sparse", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_dense", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_deprecationwarnings", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_force_new_behaviour", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_categorical_features", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_handle_unknown", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_not_fitted", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_no_categorical_features", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_dtype[int32-int32]", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_dtype[int32-float32]", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_dtype[int32-float64]", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_dtype[float32-int32]", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_dtype[float32-float32]", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_dtype[float32-float64]", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_dtype[float64-int32]", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_dtype[float64-float32]", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_dtype[float64-float64]", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_dtype_pandas[int32]", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_dtype_pandas[float32]", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_dtype_pandas[float64]", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_set_params", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder[mixed]", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder[numeric]", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder[object]", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_inverse", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_categories[mixed]", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_categories[numeric]", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_categories[object]", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_categories[string]", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_specified_categories[object]", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_specified_categories[numeric]", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_specified_categories[object-string-cat]", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_unsorted_categories", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_specified_categories_mixed_columns", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_pandas", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_feature_names", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_feature_names_unicode", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_raise_missing[error-numeric]", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_raise_missing[error-object]", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_raise_missing[ignore-numeric]", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_raise_missing[ignore-object]", "sklearn/preprocessing/tests/test_encoders.py::test_ordinal_encoder[mixed]", "sklearn/preprocessing/tests/test_encoders.py::test_ordinal_encoder[numeric]", "sklearn/preprocessing/tests/test_encoders.py::test_ordinal_encoder[object]", "sklearn/preprocessing/tests/test_encoders.py::test_ordinal_encoder_specified_categories[object]", "sklearn/preprocessing/tests/test_encoders.py::test_ordinal_encoder_specified_categories[numeric]", "sklearn/preprocessing/tests/test_encoders.py::test_ordinal_encoder_specified_categories[object-string-cat]", "sklearn/preprocessing/tests/test_encoders.py::test_ordinal_encoder_inverse", "sklearn/preprocessing/tests/test_encoders.py::test_ordinal_encoder_raise_missing[numeric]", "sklearn/preprocessing/tests/test_encoders.py::test_ordinal_encoder_raise_missing[object]", "sklearn/preprocessing/tests/test_encoders.py::test_encoder_dtypes", "sklearn/preprocessing/tests/test_encoders.py::test_encoder_dtypes_pandas", "sklearn/preprocessing/tests/test_encoders.py::test_one_hot_encoder_warning"]

**Base Commit**: 02dc9ed680e7f53f1b0d410dcdd37341c7958eb1
**Environment Setup Commit**: 7813f7efb5b2012412888b69e73d76f2df2b50b6
