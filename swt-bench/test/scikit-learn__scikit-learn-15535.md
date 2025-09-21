# scikit-learn__scikit-learn-15535

**Repository**: scikit-learn/scikit-learn
**Created**: 2019-11-05T02:09:55Z
**Version**: 0.22

## Problem Statement

regression in input validation of clustering metrics
```python
from sklearn.metrics.cluster import mutual_info_score
import numpy as np

x = np.random.choice(['a', 'b'], size=20).astype(object)
mutual_info_score(x, x)
```
ValueError: could not convert string to float: 'b'

while
```python
x = np.random.choice(['a', 'b'], size=20)
mutual_info_score(x, x)
```
works with a warning?

this worked in 0.21.1 without a warning (as I think it should)


Edit by @ogrisel: I removed the `.astype(object)` in the second code snippet.


## Hints

broke in #10830 ping @glemaitre 

## Patch

```diff

diff --git a/sklearn/metrics/cluster/_supervised.py b/sklearn/metrics/cluster/_supervised.py
--- a/sklearn/metrics/cluster/_supervised.py
+++ b/sklearn/metrics/cluster/_supervised.py
@@ -43,10 +43,10 @@ def check_clusterings(labels_true, labels_pred):
         The predicted labels.
     """
     labels_true = check_array(
-        labels_true, ensure_2d=False, ensure_min_samples=0
+        labels_true, ensure_2d=False, ensure_min_samples=0, dtype=None,
     )
     labels_pred = check_array(
-        labels_pred, ensure_2d=False, ensure_min_samples=0
+        labels_pred, ensure_2d=False, ensure_min_samples=0, dtype=None,
     )
 
     # input checks


```

## Test Patch

```diff
diff --git a/sklearn/metrics/cluster/tests/test_common.py b/sklearn/metrics/cluster/tests/test_common.py
--- a/sklearn/metrics/cluster/tests/test_common.py
+++ b/sklearn/metrics/cluster/tests/test_common.py
@@ -161,7 +161,9 @@ def generate_formats(y):
         y = np.array(y)
         yield y, 'array of ints'
         yield y.tolist(), 'list of ints'
-        yield [str(x) for x in y.tolist()], 'list of strs'
+        yield [str(x) + "-a" for x in y.tolist()], 'list of strs'
+        yield (np.array([str(x) + "-a" for x in y.tolist()], dtype=object),
+               'array of strs')
         yield y - 1, 'including negative ints'
         yield y + 1, 'strictly positive ints'
 

```

## Test Information

**Tests that should FAIL→PASS**: ["sklearn/metrics/cluster/tests/test_common.py::test_format_invariance[adjusted_mutual_info_score]", "sklearn/metrics/cluster/tests/test_common.py::test_format_invariance[adjusted_rand_score]", "sklearn/metrics/cluster/tests/test_common.py::test_format_invariance[completeness_score]", "sklearn/metrics/cluster/tests/test_common.py::test_format_invariance[homogeneity_score]", "sklearn/metrics/cluster/tests/test_common.py::test_format_invariance[mutual_info_score]", "sklearn/metrics/cluster/tests/test_common.py::test_format_invariance[normalized_mutual_info_score]", "sklearn/metrics/cluster/tests/test_common.py::test_format_invariance[v_measure_score]", "sklearn/metrics/cluster/tests/test_common.py::test_format_invariance[fowlkes_mallows_score]"]

**Tests that should PASS→PASS**: ["sklearn/metrics/cluster/tests/test_common.py::test_symmetric_non_symmetric_union", "sklearn/metrics/cluster/tests/test_common.py::test_symmetry[adjusted_rand_score-y10-y20]", "sklearn/metrics/cluster/tests/test_common.py::test_symmetry[v_measure_score-y11-y21]", "sklearn/metrics/cluster/tests/test_common.py::test_symmetry[mutual_info_score-y12-y22]", "sklearn/metrics/cluster/tests/test_common.py::test_symmetry[adjusted_mutual_info_score-y13-y23]", "sklearn/metrics/cluster/tests/test_common.py::test_symmetry[normalized_mutual_info_score-y14-y24]", "sklearn/metrics/cluster/tests/test_common.py::test_symmetry[fowlkes_mallows_score-y15-y25]", "sklearn/metrics/cluster/tests/test_common.py::test_non_symmetry[homogeneity_score-y10-y20]", "sklearn/metrics/cluster/tests/test_common.py::test_non_symmetry[completeness_score-y11-y21]", "sklearn/metrics/cluster/tests/test_common.py::test_normalized_output[adjusted_rand_score]", "sklearn/metrics/cluster/tests/test_common.py::test_normalized_output[homogeneity_score]", "sklearn/metrics/cluster/tests/test_common.py::test_normalized_output[completeness_score]", "sklearn/metrics/cluster/tests/test_common.py::test_normalized_output[v_measure_score]", "sklearn/metrics/cluster/tests/test_common.py::test_normalized_output[adjusted_mutual_info_score]", "sklearn/metrics/cluster/tests/test_common.py::test_normalized_output[fowlkes_mallows_score]", "sklearn/metrics/cluster/tests/test_common.py::test_normalized_output[normalized_mutual_info_score]", "sklearn/metrics/cluster/tests/test_common.py::test_permute_labels[adjusted_mutual_info_score]", "sklearn/metrics/cluster/tests/test_common.py::test_permute_labels[adjusted_rand_score]", "sklearn/metrics/cluster/tests/test_common.py::test_permute_labels[completeness_score]", "sklearn/metrics/cluster/tests/test_common.py::test_permute_labels[homogeneity_score]", "sklearn/metrics/cluster/tests/test_common.py::test_permute_labels[mutual_info_score]", "sklearn/metrics/cluster/tests/test_common.py::test_permute_labels[normalized_mutual_info_score]", "sklearn/metrics/cluster/tests/test_common.py::test_permute_labels[v_measure_score]", "sklearn/metrics/cluster/tests/test_common.py::test_permute_labels[fowlkes_mallows_score]", "sklearn/metrics/cluster/tests/test_common.py::test_permute_labels[silhouette_score]", "sklearn/metrics/cluster/tests/test_common.py::test_permute_labels[silhouette_manhattan]", "sklearn/metrics/cluster/tests/test_common.py::test_permute_labels[calinski_harabasz_score]", "sklearn/metrics/cluster/tests/test_common.py::test_permute_labels[davies_bouldin_score]", "sklearn/metrics/cluster/tests/test_common.py::test_format_invariance[silhouette_score]", "sklearn/metrics/cluster/tests/test_common.py::test_format_invariance[silhouette_manhattan]", "sklearn/metrics/cluster/tests/test_common.py::test_format_invariance[calinski_harabasz_score]", "sklearn/metrics/cluster/tests/test_common.py::test_format_invariance[davies_bouldin_score]", "sklearn/metrics/cluster/tests/test_common.py::test_single_sample[adjusted_mutual_info_score]", "sklearn/metrics/cluster/tests/test_common.py::test_single_sample[adjusted_rand_score]", "sklearn/metrics/cluster/tests/test_common.py::test_single_sample[completeness_score]", "sklearn/metrics/cluster/tests/test_common.py::test_single_sample[homogeneity_score]", "sklearn/metrics/cluster/tests/test_common.py::test_single_sample[mutual_info_score]", "sklearn/metrics/cluster/tests/test_common.py::test_single_sample[normalized_mutual_info_score]", "sklearn/metrics/cluster/tests/test_common.py::test_single_sample[v_measure_score]", "sklearn/metrics/cluster/tests/test_common.py::test_single_sample[fowlkes_mallows_score]", "sklearn/metrics/cluster/tests/test_common.py::test_inf_nan_input[adjusted_mutual_info_score-adjusted_mutual_info_score]", "sklearn/metrics/cluster/tests/test_common.py::test_inf_nan_input[adjusted_rand_score-adjusted_rand_score]", "sklearn/metrics/cluster/tests/test_common.py::test_inf_nan_input[completeness_score-completeness_score]", "sklearn/metrics/cluster/tests/test_common.py::test_inf_nan_input[homogeneity_score-homogeneity_score]", "sklearn/metrics/cluster/tests/test_common.py::test_inf_nan_input[mutual_info_score-mutual_info_score]", "sklearn/metrics/cluster/tests/test_common.py::test_inf_nan_input[normalized_mutual_info_score-normalized_mutual_info_score]", "sklearn/metrics/cluster/tests/test_common.py::test_inf_nan_input[v_measure_score-v_measure_score]", "sklearn/metrics/cluster/tests/test_common.py::test_inf_nan_input[fowlkes_mallows_score-fowlkes_mallows_score]", "sklearn/metrics/cluster/tests/test_common.py::test_inf_nan_input[silhouette_score-silhouette_score]", "sklearn/metrics/cluster/tests/test_common.py::test_inf_nan_input[silhouette_manhattan-metric_func9]", "sklearn/metrics/cluster/tests/test_common.py::test_inf_nan_input[calinski_harabasz_score-calinski_harabasz_score]", "sklearn/metrics/cluster/tests/test_common.py::test_inf_nan_input[davies_bouldin_score-davies_bouldin_score]"]

**Base Commit**: 70b0ddea992c01df1a41588fa9e2d130fb6b13f8
**Environment Setup Commit**: 7e85a6d1f038bbb932b36f18d75df6be937ed00d
