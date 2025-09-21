# scikit-learn__scikit-learn-11040

**Repository**: scikit-learn/scikit-learn
**Created**: 2018-04-28T07:18:33Z
**Version**: 0.20

## Problem Statement

Missing parameter validation in Neighbors estimator for float n_neighbors
```python
from sklearn.neighbors import NearestNeighbors
from sklearn.datasets import make_blobs
X, y = make_blobs()
neighbors = NearestNeighbors(n_neighbors=3.)
neighbors.fit(X)
neighbors.kneighbors(X)
```
```
~/checkout/scikit-learn/sklearn/neighbors/binary_tree.pxi in sklearn.neighbors.kd_tree.NeighborsHeap.__init__()

TypeError: 'float' object cannot be interpreted as an integer
```
This should be caught earlier and a more helpful error message should be raised (or we could be lenient and cast to integer, but I think a better error might be better).

We need to make sure that 
```python
neighbors.kneighbors(X, n_neighbors=3.)
```
also works.


## Hints

Hello, I would like to take this as my first issue. 
Thank you.
@amueller 
I added a simple check for float inputs for  n_neighbors in order to throw ValueError if that's the case.
@urvang96 Did say he was working on it first @Alfo5123  ..

@amueller I think there is a lot of other estimators and Python functions in general where dtype isn't explicitely checked and wrong dtype just raises an exception later on.

Take for instance,
```py
import numpy as np

x = np.array([1])
np.sum(x, axis=1.)
```
which produces,
```py
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "lib/python3.6/site-packages/numpy/core/fromnumeric.py", line 1882, in sum
    out=out, **kwargs)
  File "lib/python3.6/site-packages/numpy/core/_methods.py", line 32, in _sum
    return umr_sum(a, axis, dtype, out, keepdims)
TypeError: 'float' object cannot be interpreted as an integer
```
so pretty much the same exception as in the original post, with no indications of what is wrong exactly. Here it's straightforward because we only provided one parameter, but the same is true for more complex constructions. 

So I'm not sure that starting to enforce int/float dtype of parameters, estimator by estimator is a solution here. In general don't think there is a need to do more parameter validation than what is done e.g. in numpy or pandas. If we want to do it, some generic type validation based on annotaitons (e.g. https://github.com/agronholm/typeguard) might be easier but also require more maintenance time and probably harder to implement while Python 2.7 is supported. 

pandas also doesn't enforce it explicitely BTW,
```python
pd.DataFrame([{'a': 1, 'b': 2}]).sum(axis=0.)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "lib/python3.6/site-packages/pandas/core/generic.py", line 7295, in stat_func
    numeric_only=numeric_only, min_count=min_count)
  File "lib/python3.6/site-packages/pandas/core/frame.py", line 5695, in _reduce
    axis = self._get_axis_number(axis)
  File "lib/python3.6/site-packages/pandas/core/generic.py", line 357, in _get_axis_number
    .format(axis, type(self)))
ValueError: No axis named 0.0 for object type <class 'pandas.core.frame.DataFrame'>
```
@Alfo5123 I claimed the issue first and I was working on it. This is not how the community works.
@urvang96 Yes, I understand, my bad. Sorry for the inconvenient.  I won't continue on it. 
@Alfo5123  Thank You. Are to going to close the existing PR?

## Patch

```diff

diff --git a/sklearn/neighbors/base.py b/sklearn/neighbors/base.py
--- a/sklearn/neighbors/base.py
+++ b/sklearn/neighbors/base.py
@@ -258,6 +258,12 @@ def _fit(self, X):
                     "Expected n_neighbors > 0. Got %d" %
                     self.n_neighbors
                 )
+            else:
+                if not np.issubdtype(type(self.n_neighbors), np.integer):
+                    raise TypeError(
+                        "n_neighbors does not take %s value, "
+                        "enter integer value" %
+                        type(self.n_neighbors))
 
         return self
 
@@ -327,6 +333,17 @@ class from an array representing our data set and ask who's
 
         if n_neighbors is None:
             n_neighbors = self.n_neighbors
+        elif n_neighbors <= 0:
+            raise ValueError(
+                "Expected n_neighbors > 0. Got %d" %
+                n_neighbors
+            )
+        else:
+            if not np.issubdtype(type(n_neighbors), np.integer):
+                raise TypeError(
+                    "n_neighbors does not take %s value, "
+                    "enter integer value" %
+                    type(n_neighbors))
 
         if X is not None:
             query_is_train = False


```

## Test Patch

```diff
diff --git a/sklearn/neighbors/tests/test_neighbors.py b/sklearn/neighbors/tests/test_neighbors.py
--- a/sklearn/neighbors/tests/test_neighbors.py
+++ b/sklearn/neighbors/tests/test_neighbors.py
@@ -18,6 +18,7 @@
 from sklearn.utils.testing import assert_greater
 from sklearn.utils.testing import assert_in
 from sklearn.utils.testing import assert_raises
+from sklearn.utils.testing import assert_raises_regex
 from sklearn.utils.testing import assert_true
 from sklearn.utils.testing import assert_warns
 from sklearn.utils.testing import assert_warns_message
@@ -108,6 +109,21 @@ def test_unsupervised_inputs():
         assert_array_almost_equal(ind1, ind2)
 
 
+def test_n_neighbors_datatype():
+    # Test to check whether n_neighbors is integer
+    X = [[1, 1], [1, 1], [1, 1]]
+    expected_msg = "n_neighbors does not take .*float.* " \
+                   "value, enter integer value"
+    msg = "Expected n_neighbors > 0. Got -3"
+
+    neighbors_ = neighbors.NearestNeighbors(n_neighbors=3.)
+    assert_raises_regex(TypeError, expected_msg, neighbors_.fit, X)
+    assert_raises_regex(ValueError, msg,
+                        neighbors_.kneighbors, X=X, n_neighbors=-3)
+    assert_raises_regex(TypeError, expected_msg,
+                        neighbors_.kneighbors, X=X, n_neighbors=3.)
+
+
 def test_precomputed(random_state=42):
     """Tests unsupervised NearestNeighbors with a distance matrix."""
     # Note: smaller samples may result in spurious test success

```

## Test Information

**Tests that should FAIL→PASS**: ["sklearn/neighbors/tests/test_neighbors.py::test_n_neighbors_datatype"]

**Tests that should PASS→PASS**: ["sklearn/neighbors/tests/test_neighbors.py::test_unsupervised_kneighbors", "sklearn/neighbors/tests/test_neighbors.py::test_unsupervised_inputs", "sklearn/neighbors/tests/test_neighbors.py::test_precomputed", "sklearn/neighbors/tests/test_neighbors.py::test_precomputed_cross_validation", "sklearn/neighbors/tests/test_neighbors.py::test_unsupervised_radius_neighbors", "sklearn/neighbors/tests/test_neighbors.py::test_kneighbors_classifier", "sklearn/neighbors/tests/test_neighbors.py::test_kneighbors_classifier_float_labels", "sklearn/neighbors/tests/test_neighbors.py::test_kneighbors_classifier_predict_proba", "sklearn/neighbors/tests/test_neighbors.py::test_radius_neighbors_classifier", "sklearn/neighbors/tests/test_neighbors.py::test_radius_neighbors_classifier_when_no_neighbors", "sklearn/neighbors/tests/test_neighbors.py::test_radius_neighbors_classifier_outlier_labeling", "sklearn/neighbors/tests/test_neighbors.py::test_radius_neighbors_classifier_zero_distance", "sklearn/neighbors/tests/test_neighbors.py::test_neighbors_regressors_zero_distance", "sklearn/neighbors/tests/test_neighbors.py::test_radius_neighbors_boundary_handling", "sklearn/neighbors/tests/test_neighbors.py::test_RadiusNeighborsClassifier_multioutput", "sklearn/neighbors/tests/test_neighbors.py::test_kneighbors_classifier_sparse", "sklearn/neighbors/tests/test_neighbors.py::test_KNeighborsClassifier_multioutput", "sklearn/neighbors/tests/test_neighbors.py::test_kneighbors_regressor", "sklearn/neighbors/tests/test_neighbors.py::test_KNeighborsRegressor_multioutput_uniform_weight", "sklearn/neighbors/tests/test_neighbors.py::test_kneighbors_regressor_multioutput", "sklearn/neighbors/tests/test_neighbors.py::test_radius_neighbors_regressor", "sklearn/neighbors/tests/test_neighbors.py::test_RadiusNeighborsRegressor_multioutput_with_uniform_weight", "sklearn/neighbors/tests/test_neighbors.py::test_RadiusNeighborsRegressor_multioutput", "sklearn/neighbors/tests/test_neighbors.py::test_kneighbors_regressor_sparse", "sklearn/neighbors/tests/test_neighbors.py::test_neighbors_iris", "sklearn/neighbors/tests/test_neighbors.py::test_neighbors_digits", "sklearn/neighbors/tests/test_neighbors.py::test_kneighbors_graph", "sklearn/neighbors/tests/test_neighbors.py::test_kneighbors_graph_sparse", "sklearn/neighbors/tests/test_neighbors.py::test_radius_neighbors_graph", "sklearn/neighbors/tests/test_neighbors.py::test_radius_neighbors_graph_sparse", "sklearn/neighbors/tests/test_neighbors.py::test_neighbors_badargs", "sklearn/neighbors/tests/test_neighbors.py::test_neighbors_metrics", "sklearn/neighbors/tests/test_neighbors.py::test_callable_metric", "sklearn/neighbors/tests/test_neighbors.py::test_valid_brute_metric_for_auto_algorithm", "sklearn/neighbors/tests/test_neighbors.py::test_metric_params_interface", "sklearn/neighbors/tests/test_neighbors.py::test_predict_sparse_ball_kd_tree", "sklearn/neighbors/tests/test_neighbors.py::test_non_euclidean_kneighbors", "sklearn/neighbors/tests/test_neighbors.py::test_k_and_radius_neighbors_train_is_not_query", "sklearn/neighbors/tests/test_neighbors.py::test_k_and_radius_neighbors_X_None", "sklearn/neighbors/tests/test_neighbors.py::test_k_and_radius_neighbors_duplicates", "sklearn/neighbors/tests/test_neighbors.py::test_include_self_neighbors_graph", "sklearn/neighbors/tests/test_neighbors.py::test_dtype_convert", "sklearn/neighbors/tests/test_neighbors.py::test_sparse_metric_callable", "sklearn/neighbors/tests/test_neighbors.py::test_pairwise_boolean_distance"]

**Base Commit**: 96a02f3934952d486589dddd3f00b40d5a5ab5f2
**Environment Setup Commit**: 55bf5d93e5674f13a1134d93a11fd0cd11aabcd1
