# scikit-learn__scikit-learn-13497

**Repository**: scikit-learn/scikit-learn
**Created**: 2019-03-23T14:28:08Z
**Version**: 0.21

## Problem Statement

Comparing string to array in _estimate_mi
In ``_estimate_mi`` there is ``discrete_features == 'auto'`` but discrete features can be an array of indices or a boolean mask.
This will error in future versions of numpy.
Also this means we never test this function with discrete features != 'auto', it seems?


## Hints

I'll take this
@hermidalc go for it :)
i'm not sure ,but i think user will change the default value if it seem to be array or boolean mask....bcz auto is  default value it is not fixed.
I haven't understood, @punkstar25 

## Patch

```diff

diff --git a/sklearn/feature_selection/mutual_info_.py b/sklearn/feature_selection/mutual_info_.py
--- a/sklearn/feature_selection/mutual_info_.py
+++ b/sklearn/feature_selection/mutual_info_.py
@@ -10,7 +10,7 @@
 from ..preprocessing import scale
 from ..utils import check_random_state
 from ..utils.fixes import _astype_copy_false
-from ..utils.validation import check_X_y
+from ..utils.validation import check_array, check_X_y
 from ..utils.multiclass import check_classification_targets
 
 
@@ -247,14 +247,16 @@ def _estimate_mi(X, y, discrete_features='auto', discrete_target=False,
     X, y = check_X_y(X, y, accept_sparse='csc', y_numeric=not discrete_target)
     n_samples, n_features = X.shape
 
-    if discrete_features == 'auto':
-        discrete_features = issparse(X)
-
-    if isinstance(discrete_features, bool):
+    if isinstance(discrete_features, (str, bool)):
+        if isinstance(discrete_features, str):
+            if discrete_features == 'auto':
+                discrete_features = issparse(X)
+            else:
+                raise ValueError("Invalid string value for discrete_features.")
         discrete_mask = np.empty(n_features, dtype=bool)
         discrete_mask.fill(discrete_features)
     else:
-        discrete_features = np.asarray(discrete_features)
+        discrete_features = check_array(discrete_features, ensure_2d=False)
         if discrete_features.dtype != 'bool':
             discrete_mask = np.zeros(n_features, dtype=bool)
             discrete_mask[discrete_features] = True


```

## Test Patch

```diff
diff --git a/sklearn/feature_selection/tests/test_mutual_info.py b/sklearn/feature_selection/tests/test_mutual_info.py
--- a/sklearn/feature_selection/tests/test_mutual_info.py
+++ b/sklearn/feature_selection/tests/test_mutual_info.py
@@ -183,18 +183,26 @@ def test_mutual_info_options():
     X_csr = csr_matrix(X)
 
     for mutual_info in (mutual_info_regression, mutual_info_classif):
-        assert_raises(ValueError, mutual_info_regression, X_csr, y,
+        assert_raises(ValueError, mutual_info, X_csr, y,
                       discrete_features=False)
+        assert_raises(ValueError, mutual_info, X, y,
+                      discrete_features='manual')
+        assert_raises(ValueError, mutual_info, X_csr, y,
+                      discrete_features=[True, False, True])
+        assert_raises(IndexError, mutual_info, X, y,
+                      discrete_features=[True, False, True, False])
+        assert_raises(IndexError, mutual_info, X, y, discrete_features=[1, 4])
 
         mi_1 = mutual_info(X, y, discrete_features='auto', random_state=0)
         mi_2 = mutual_info(X, y, discrete_features=False, random_state=0)
-
-        mi_3 = mutual_info(X_csr, y, discrete_features='auto',
-                           random_state=0)
-        mi_4 = mutual_info(X_csr, y, discrete_features=True,
+        mi_3 = mutual_info(X_csr, y, discrete_features='auto', random_state=0)
+        mi_4 = mutual_info(X_csr, y, discrete_features=True, random_state=0)
+        mi_5 = mutual_info(X, y, discrete_features=[True, False, True],
                            random_state=0)
+        mi_6 = mutual_info(X, y, discrete_features=[0, 2], random_state=0)
 
         assert_array_equal(mi_1, mi_2)
         assert_array_equal(mi_3, mi_4)
+        assert_array_equal(mi_5, mi_6)
 
     assert not np.allclose(mi_1, mi_3)

```

## Test Information

**Tests that should FAIL→PASS**: ["sklearn/feature_selection/tests/test_mutual_info.py::test_mutual_info_options"]

**Tests that should PASS→PASS**: ["sklearn/feature_selection/tests/test_mutual_info.py::test_compute_mi_dd", "sklearn/feature_selection/tests/test_mutual_info.py::test_compute_mi_cc", "sklearn/feature_selection/tests/test_mutual_info.py::test_compute_mi_cd", "sklearn/feature_selection/tests/test_mutual_info.py::test_compute_mi_cd_unique_label", "sklearn/feature_selection/tests/test_mutual_info.py::test_mutual_info_classif_discrete", "sklearn/feature_selection/tests/test_mutual_info.py::test_mutual_info_regression", "sklearn/feature_selection/tests/test_mutual_info.py::test_mutual_info_classif_mixed"]

**Base Commit**: 26f690961a52946dd2f53bf0fdd4264b2ae5be90
**Environment Setup Commit**: 7813f7efb5b2012412888b69e73d76f2df2b50b6
