# scikit-learn__scikit-learn-25500

**Repository**: scikit-learn/scikit-learn
**Created**: 2023-01-27T19:49:28Z
**Version**: 1.3

## Problem Statement

CalibratedClassifierCV doesn't work with `set_config(transform_output="pandas")`
### Describe the bug

CalibratedClassifierCV with isotonic regression doesn't work when we previously set `set_config(transform_output="pandas")`.
The IsotonicRegression seems to return a dataframe, which is a problem for `_CalibratedClassifier`  in `predict_proba` where it tries to put the dataframe in a numpy array row `proba[:, class_idx] = calibrator.predict(this_pred)`.

### Steps/Code to Reproduce

```python
import numpy as np
from sklearn import set_config
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import SGDClassifier

set_config(transform_output="pandas")
model = CalibratedClassifierCV(SGDClassifier(), method='isotonic')
model.fit(np.arange(90).reshape(30, -1), np.arange(30) % 2)
model.predict(np.arange(90).reshape(30, -1))
```

### Expected Results

It should not crash.

### Actual Results

```
../core/model_trainer.py:306: in train_model
    cv_predictions = cross_val_predict(pipeline,
../../../../.anaconda3/envs/strategy-training/lib/python3.9/site-packages/sklearn/model_selection/_validation.py:968: in cross_val_predict
    predictions = parallel(
../../../../.anaconda3/envs/strategy-training/lib/python3.9/site-packages/joblib/parallel.py:1085: in __call__
    if self.dispatch_one_batch(iterator):
../../../../.anaconda3/envs/strategy-training/lib/python3.9/site-packages/joblib/parallel.py:901: in dispatch_one_batch
    self._dispatch(tasks)
../../../../.anaconda3/envs/strategy-training/lib/python3.9/site-packages/joblib/parallel.py:819: in _dispatch
    job = self._backend.apply_async(batch, callback=cb)
../../../../.anaconda3/envs/strategy-training/lib/python3.9/site-packages/joblib/_parallel_backends.py:208: in apply_async
    result = ImmediateResult(func)
../../../../.anaconda3/envs/strategy-training/lib/python3.9/site-packages/joblib/_parallel_backends.py:597: in __init__
    self.results = batch()
../../../../.anaconda3/envs/strategy-training/lib/python3.9/site-packages/joblib/parallel.py:288: in __call__
    return [func(*args, **kwargs)
../../../../.anaconda3/envs/strategy-training/lib/python3.9/site-packages/joblib/parallel.py:288: in <listcomp>
    return [func(*args, **kwargs)
../../../../.anaconda3/envs/strategy-training/lib/python3.9/site-packages/sklearn/utils/fixes.py:117: in __call__
    return self.function(*args, **kwargs)
../../../../.anaconda3/envs/strategy-training/lib/python3.9/site-packages/sklearn/model_selection/_validation.py:1052: in _fit_and_predict
    predictions = func(X_test)
../../../../.anaconda3/envs/strategy-training/lib/python3.9/site-packages/sklearn/pipeline.py:548: in predict_proba
    return self.steps[-1][1].predict_proba(Xt, **predict_proba_params)
../../../../.anaconda3/envs/strategy-training/lib/python3.9/site-packages/sklearn/calibration.py:477: in predict_proba
    proba = calibrated_classifier.predict_proba(X)
../../../../.anaconda3/envs/strategy-training/lib/python3.9/site-packages/sklearn/calibration.py:764: in predict_proba
    proba[:, class_idx] = calibrator.predict(this_pred)
E   ValueError: could not broadcast input array from shape (20,1) into shape (20,)
```

### Versions

```shell
System:
    python: 3.9.15 (main, Nov 24 2022, 14:31:59)  [GCC 11.2.0]
executable: /home/philippe/.anaconda3/envs/strategy-training/bin/python
   machine: Linux-5.15.0-57-generic-x86_64-with-glibc2.31

Python dependencies:
      sklearn: 1.2.0
          pip: 22.2.2
   setuptools: 62.3.2
        numpy: 1.23.5
        scipy: 1.9.3
       Cython: None
       pandas: 1.4.1
   matplotlib: 3.6.3
       joblib: 1.2.0
threadpoolctl: 3.1.0

Built with OpenMP: True

threadpoolctl info:
       user_api: openmp
   internal_api: openmp
         prefix: libgomp
       filepath: /home/philippe/.anaconda3/envs/strategy-training/lib/python3.9/site-packages/scikit_learn.libs/libgomp-a34b3233.so.1.0.0
        version: None
    num_threads: 12

       user_api: blas
   internal_api: openblas
         prefix: libopenblas
       filepath: /home/philippe/.anaconda3/envs/strategy-training/lib/python3.9/site-packages/numpy.libs/libopenblas64_p-r0-742d56dc.3.20.so
        version: 0.3.20
threading_layer: pthreads
   architecture: Haswell
    num_threads: 12

       user_api: blas
   internal_api: openblas
         prefix: libopenblas
       filepath: /home/philippe/.anaconda3/envs/strategy-training/lib/python3.9/site-packages/scipy.libs/libopenblasp-r0-41284840.3.18.so
        version: 0.3.18
threading_layer: pthreads
   architecture: Haswell
    num_threads: 12
```



## Hints

I can reproduce it. We need to investigate but I would expect the inner estimator not being able to handle some dataframe because we expected NumPy arrays before.
This could be a bit like https://github.com/scikit-learn/scikit-learn/pull/25370 where things get confused when pandas output is configured. I think the solution is different (TSNE's PCA is truely "internal only") but it seems like there might be something more general to investigate/think about related to pandas output and nested estimators.
There is something quite smelly regarding the interaction between `IsotonicRegression` and pandas output:

<img width="1079" alt="image" src="https://user-images.githubusercontent.com/7454015/215147695-8aa08b83-705b-47a4-ab7c-43acb222098f.png">

It seems that we output a pandas Series when calling `predict` which is something that we don't do for any other estimator. `IsotonicRegression` is already quite special since it accepts a single feature. I need to investigate more to understand why we wrap the output of the `predict` method.
OK the reason is that `IsotonicRegression().predict(X)` call `IsotonicRegression().transform(X)` ;)
I don't know if we should have:

```python
def predict(self, T):
    with config_context(transform_output="default"):
        return self.transform(T)
```

or

```python
def predict(self, T):
    return np.array(self.transform(T), copy=False).squeeze()
```
Another solution would be to have a private `_transform` function called by both `transform` and `predict`. In this way, the `predict` call will not call the wrapper that is around the public `transform` method. I think this is even cleaner than the previous code.
/take

## Patch

```diff

diff --git a/sklearn/isotonic.py b/sklearn/isotonic.py
--- a/sklearn/isotonic.py
+++ b/sklearn/isotonic.py
@@ -360,23 +360,16 @@ def fit(self, X, y, sample_weight=None):
         self._build_f(X, y)
         return self
 
-    def transform(self, T):
-        """Transform new data by linear interpolation.
-
-        Parameters
-        ----------
-        T : array-like of shape (n_samples,) or (n_samples, 1)
-            Data to transform.
+    def _transform(self, T):
+        """`_transform` is called by both `transform` and `predict` methods.
 
-            .. versionchanged:: 0.24
-               Also accepts 2d array with 1 feature.
+        Since `transform` is wrapped to output arrays of specific types (e.g.
+        NumPy arrays, pandas DataFrame), we cannot make `predict` call `transform`
+        directly.
 
-        Returns
-        -------
-        y_pred : ndarray of shape (n_samples,)
-            The transformed data.
+        The above behaviour could be changed in the future, if we decide to output
+        other type of arrays when calling `predict`.
         """
-
         if hasattr(self, "X_thresholds_"):
             dtype = self.X_thresholds_.dtype
         else:
@@ -397,6 +390,24 @@ def transform(self, T):
 
         return res
 
+    def transform(self, T):
+        """Transform new data by linear interpolation.
+
+        Parameters
+        ----------
+        T : array-like of shape (n_samples,) or (n_samples, 1)
+            Data to transform.
+
+            .. versionchanged:: 0.24
+               Also accepts 2d array with 1 feature.
+
+        Returns
+        -------
+        y_pred : ndarray of shape (n_samples,)
+            The transformed data.
+        """
+        return self._transform(T)
+
     def predict(self, T):
         """Predict new data by linear interpolation.
 
@@ -410,7 +421,7 @@ def predict(self, T):
         y_pred : ndarray of shape (n_samples,)
             Transformed data.
         """
-        return self.transform(T)
+        return self._transform(T)
 
     # We implement get_feature_names_out here instead of using
     # `ClassNamePrefixFeaturesOutMixin`` because `input_features` are ignored.


```

## Test Patch

```diff
diff --git a/sklearn/tests/test_isotonic.py b/sklearn/tests/test_isotonic.py
--- a/sklearn/tests/test_isotonic.py
+++ b/sklearn/tests/test_isotonic.py
@@ -5,6 +5,7 @@
 
 import pytest
 
+import sklearn
 from sklearn.datasets import make_regression
 from sklearn.isotonic import (
     check_increasing,
@@ -680,3 +681,24 @@ def test_get_feature_names_out(shape):
     assert isinstance(names, np.ndarray)
     assert names.dtype == object
     assert_array_equal(["isotonicregression0"], names)
+
+
+def test_isotonic_regression_output_predict():
+    """Check that `predict` does return the expected output type.
+
+    We need to check that `transform` will output a DataFrame and a NumPy array
+    when we set `transform_output` to `pandas`.
+
+    Non-regression test for:
+    https://github.com/scikit-learn/scikit-learn/issues/25499
+    """
+    pd = pytest.importorskip("pandas")
+    X, y = make_regression(n_samples=10, n_features=1, random_state=42)
+    regressor = IsotonicRegression()
+    with sklearn.config_context(transform_output="pandas"):
+        regressor.fit(X, y)
+        X_trans = regressor.transform(X)
+        y_pred = regressor.predict(X)
+
+    assert isinstance(X_trans, pd.DataFrame)
+    assert isinstance(y_pred, np.ndarray)

```

## Test Information

**Tests that should FAIL→PASS**: ["sklearn/tests/test_isotonic.py::test_isotonic_regression_output_predict"]

**Tests that should PASS→PASS**: ["sklearn/tests/test_isotonic.py::test_permutation_invariance", "sklearn/tests/test_isotonic.py::test_check_increasing_small_number_of_samples", "sklearn/tests/test_isotonic.py::test_check_increasing_up", "sklearn/tests/test_isotonic.py::test_check_increasing_up_extreme", "sklearn/tests/test_isotonic.py::test_check_increasing_down", "sklearn/tests/test_isotonic.py::test_check_increasing_down_extreme", "sklearn/tests/test_isotonic.py::test_check_ci_warn", "sklearn/tests/test_isotonic.py::test_isotonic_regression", "sklearn/tests/test_isotonic.py::test_isotonic_regression_ties_min", "sklearn/tests/test_isotonic.py::test_isotonic_regression_ties_max", "sklearn/tests/test_isotonic.py::test_isotonic_regression_ties_secondary_", "sklearn/tests/test_isotonic.py::test_isotonic_regression_with_ties_in_differently_sized_groups", "sklearn/tests/test_isotonic.py::test_isotonic_regression_reversed", "sklearn/tests/test_isotonic.py::test_isotonic_regression_auto_decreasing", "sklearn/tests/test_isotonic.py::test_isotonic_regression_auto_increasing", "sklearn/tests/test_isotonic.py::test_assert_raises_exceptions", "sklearn/tests/test_isotonic.py::test_isotonic_sample_weight_parameter_default_value", "sklearn/tests/test_isotonic.py::test_isotonic_min_max_boundaries", "sklearn/tests/test_isotonic.py::test_isotonic_sample_weight", "sklearn/tests/test_isotonic.py::test_isotonic_regression_oob_raise", "sklearn/tests/test_isotonic.py::test_isotonic_regression_oob_clip", "sklearn/tests/test_isotonic.py::test_isotonic_regression_oob_nan", "sklearn/tests/test_isotonic.py::test_isotonic_regression_pickle", "sklearn/tests/test_isotonic.py::test_isotonic_duplicate_min_entry", "sklearn/tests/test_isotonic.py::test_isotonic_ymin_ymax", "sklearn/tests/test_isotonic.py::test_isotonic_zero_weight_loop", "sklearn/tests/test_isotonic.py::test_fast_predict", "sklearn/tests/test_isotonic.py::test_isotonic_copy_before_fit", "sklearn/tests/test_isotonic.py::test_isotonic_dtype", "sklearn/tests/test_isotonic.py::test_isotonic_mismatched_dtype[int32]", "sklearn/tests/test_isotonic.py::test_isotonic_mismatched_dtype[int64]", "sklearn/tests/test_isotonic.py::test_isotonic_mismatched_dtype[float32]", "sklearn/tests/test_isotonic.py::test_isotonic_mismatched_dtype[float64]", "sklearn/tests/test_isotonic.py::test_make_unique_dtype", "sklearn/tests/test_isotonic.py::test_make_unique_tolerance[float64]", "sklearn/tests/test_isotonic.py::test_make_unique_tolerance[float32]", "sklearn/tests/test_isotonic.py::test_isotonic_make_unique_tolerance", "sklearn/tests/test_isotonic.py::test_isotonic_non_regression_inf_slope", "sklearn/tests/test_isotonic.py::test_isotonic_thresholds[True]", "sklearn/tests/test_isotonic.py::test_isotonic_thresholds[False]", "sklearn/tests/test_isotonic.py::test_input_shape_validation", "sklearn/tests/test_isotonic.py::test_isotonic_2darray_more_than_1_feature", "sklearn/tests/test_isotonic.py::test_isotonic_regression_sample_weight_not_overwritten", "sklearn/tests/test_isotonic.py::test_get_feature_names_out[1d]", "sklearn/tests/test_isotonic.py::test_get_feature_names_out[2d]"]

**Base Commit**: 4db04923a754b6a2defa1b172f55d492b85d165e
**Environment Setup Commit**: 1e8a5b833d1b58f3ab84099c4582239af854b23a
