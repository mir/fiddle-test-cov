# scikit-learn__scikit-learn-14983

**Repository**: scikit-learn/scikit-learn
**Created**: 2019-09-14T15:31:18Z
**Version**: 0.22

## Problem Statement

RepeatedKFold and RepeatedStratifiedKFold do not show correct __repr__ string
#### Description

`RepeatedKFold` and `RepeatedStratifiedKFold` do not show correct \_\_repr\_\_ string.

#### Steps/Code to Reproduce

```python
>>> from sklearn.model_selection import RepeatedKFold, RepeatedStratifiedKFold
>>> repr(RepeatedKFold())
>>> repr(RepeatedStratifiedKFold())
```

#### Expected Results

```python
>>> repr(RepeatedKFold())
RepeatedKFold(n_splits=5, n_repeats=10, random_state=None)
>>> repr(RepeatedStratifiedKFold())
RepeatedStratifiedKFold(n_splits=5, n_repeats=10, random_state=None)
```

#### Actual Results

```python
>>> repr(RepeatedKFold())
'<sklearn.model_selection._split.RepeatedKFold object at 0x0000016421AA4288>'
>>> repr(RepeatedStratifiedKFold())
'<sklearn.model_selection._split.RepeatedStratifiedKFold object at 0x0000016420E115C8>'
```

#### Versions
```
System:
    python: 3.7.4 (default, Aug  9 2019, 18:34:13) [MSC v.1915 64 bit (AMD64)]
executable: D:\anaconda3\envs\xyz\python.exe
   machine: Windows-10-10.0.16299-SP0

BLAS:
    macros:
  lib_dirs:
cblas_libs: cblas

Python deps:
       pip: 19.2.2
setuptools: 41.0.1
   sklearn: 0.21.2
     numpy: 1.16.4
     scipy: 1.3.1
    Cython: None
    pandas: 0.24.2
```


## Hints

The `__repr__` is not defined in the `_RepeatedSplit` class from which these cross-validation are inheriting. A possible fix should be:

```diff
diff --git a/sklearn/model_selection/_split.py b/sklearn/model_selection/_split.py
index ab681e89c..8a16f68bc 100644
--- a/sklearn/model_selection/_split.py
+++ b/sklearn/model_selection/_split.py
@@ -1163,6 +1163,9 @@ class _RepeatedSplits(metaclass=ABCMeta):
                      **self.cvargs)
         return cv.get_n_splits(X, y, groups) * self.n_repeats
 
+    def __repr__(self):
+        return _build_repr(self)
+
 
 class RepeatedKFold(_RepeatedSplits):
     """Repeated K-Fold cross validator.
```

We would need to have a regression test to check that we print the right representation.
Hi @glemaitre, I'm interested in working on this fix and the regression test. I've never contributed here so I'll check the contribution guide and tests properly before starting.
Thanks @DrGFreeman, go ahead. 
After adding the `__repr__` method to the `_RepeatedSplit`, the `repr()` function returns `None` for the `n_splits` parameter. This is because the `n_splits` parameter is not an attribute of the class itself but is stored in the `cvargs` class attribute.

I will modify the `_build_repr` function to include the values of the parameters stored in the `cvargs` class attribute if the class has this attribute.

## Patch

```diff

diff --git a/sklearn/model_selection/_split.py b/sklearn/model_selection/_split.py
--- a/sklearn/model_selection/_split.py
+++ b/sklearn/model_selection/_split.py
@@ -1163,6 +1163,9 @@ def get_n_splits(self, X=None, y=None, groups=None):
                      **self.cvargs)
         return cv.get_n_splits(X, y, groups) * self.n_repeats
 
+    def __repr__(self):
+        return _build_repr(self)
+
 
 class RepeatedKFold(_RepeatedSplits):
     """Repeated K-Fold cross validator.
@@ -2158,6 +2161,8 @@ def _build_repr(self):
         try:
             with warnings.catch_warnings(record=True) as w:
                 value = getattr(self, key, None)
+                if value is None and hasattr(self, 'cvargs'):
+                    value = self.cvargs.get(key, None)
             if len(w) and w[0].category == DeprecationWarning:
                 # if the parameter is deprecated, don't show it
                 continue


```

## Test Patch

```diff
diff --git a/sklearn/model_selection/tests/test_split.py b/sklearn/model_selection/tests/test_split.py
--- a/sklearn/model_selection/tests/test_split.py
+++ b/sklearn/model_selection/tests/test_split.py
@@ -980,6 +980,17 @@ def test_repeated_cv_value_errors():
         assert_raises(ValueError, cv, n_repeats=1.5)
 
 
+@pytest.mark.parametrize(
+    "RepeatedCV", [RepeatedKFold, RepeatedStratifiedKFold]
+)
+def test_repeated_cv_repr(RepeatedCV):
+    n_splits, n_repeats = 2, 6
+    repeated_cv = RepeatedCV(n_splits=n_splits, n_repeats=n_repeats)
+    repeated_cv_repr = ('{}(n_repeats=6, n_splits=2, random_state=None)'
+                        .format(repeated_cv.__class__.__name__))
+    assert repeated_cv_repr == repr(repeated_cv)
+
+
 def test_repeated_kfold_determinstic_split():
     X = [[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]]
     random_state = 258173307

```

## Test Information

**Tests that should FAIL→PASS**: ["sklearn/model_selection/tests/test_split.py::test_repeated_cv_repr[RepeatedKFold]", "sklearn/model_selection/tests/test_split.py::test_repeated_cv_repr[RepeatedStratifiedKFold]"]

**Tests that should PASS→PASS**: ["sklearn/model_selection/tests/test_split.py::test_cross_validator_with_default_params", "sklearn/model_selection/tests/test_split.py::test_2d_y", "sklearn/model_selection/tests/test_split.py::test_kfold_valueerrors", "sklearn/model_selection/tests/test_split.py::test_kfold_indices", "sklearn/model_selection/tests/test_split.py::test_kfold_no_shuffle", "sklearn/model_selection/tests/test_split.py::test_stratified_kfold_no_shuffle", "sklearn/model_selection/tests/test_split.py::test_stratified_kfold_ratios[4-False]", "sklearn/model_selection/tests/test_split.py::test_stratified_kfold_ratios[4-True]", "sklearn/model_selection/tests/test_split.py::test_stratified_kfold_ratios[5-False]", "sklearn/model_selection/tests/test_split.py::test_stratified_kfold_ratios[5-True]", "sklearn/model_selection/tests/test_split.py::test_stratified_kfold_ratios[6-False]", "sklearn/model_selection/tests/test_split.py::test_stratified_kfold_ratios[6-True]", "sklearn/model_selection/tests/test_split.py::test_stratified_kfold_ratios[7-False]", "sklearn/model_selection/tests/test_split.py::test_stratified_kfold_ratios[7-True]", "sklearn/model_selection/tests/test_split.py::test_stratified_kfold_ratios[8-False]", "sklearn/model_selection/tests/test_split.py::test_stratified_kfold_ratios[8-True]", "sklearn/model_selection/tests/test_split.py::test_stratified_kfold_ratios[9-False]", "sklearn/model_selection/tests/test_split.py::test_stratified_kfold_ratios[9-True]", "sklearn/model_selection/tests/test_split.py::test_stratified_kfold_ratios[10-False]", "sklearn/model_selection/tests/test_split.py::test_stratified_kfold_ratios[10-True]", "sklearn/model_selection/tests/test_split.py::test_stratified_kfold_label_invariance[4-False]", "sklearn/model_selection/tests/test_split.py::test_stratified_kfold_label_invariance[4-True]", "sklearn/model_selection/tests/test_split.py::test_stratified_kfold_label_invariance[6-False]", "sklearn/model_selection/tests/test_split.py::test_stratified_kfold_label_invariance[6-True]", "sklearn/model_selection/tests/test_split.py::test_stratified_kfold_label_invariance[7-False]", "sklearn/model_selection/tests/test_split.py::test_stratified_kfold_label_invariance[7-True]", "sklearn/model_selection/tests/test_split.py::test_kfold_balance", "sklearn/model_selection/tests/test_split.py::test_stratifiedkfold_balance", "sklearn/model_selection/tests/test_split.py::test_shuffle_kfold", "sklearn/model_selection/tests/test_split.py::test_shuffle_kfold_stratifiedkfold_reproducibility", "sklearn/model_selection/tests/test_split.py::test_shuffle_stratifiedkfold", "sklearn/model_selection/tests/test_split.py::test_kfold_can_detect_dependent_samples_on_digits", "sklearn/model_selection/tests/test_split.py::test_shuffle_split", "sklearn/model_selection/tests/test_split.py::test_shuffle_split_default_test_size[None-9-1-ShuffleSplit]", "sklearn/model_selection/tests/test_split.py::test_shuffle_split_default_test_size[None-9-1-StratifiedShuffleSplit]", "sklearn/model_selection/tests/test_split.py::test_shuffle_split_default_test_size[8-8-2-ShuffleSplit]", "sklearn/model_selection/tests/test_split.py::test_shuffle_split_default_test_size[8-8-2-StratifiedShuffleSplit]", "sklearn/model_selection/tests/test_split.py::test_shuffle_split_default_test_size[0.8-8-2-ShuffleSplit]", "sklearn/model_selection/tests/test_split.py::test_shuffle_split_default_test_size[0.8-8-2-StratifiedShuffleSplit]", "sklearn/model_selection/tests/test_split.py::test_group_shuffle_split_default_test_size[None-8-2]", "sklearn/model_selection/tests/test_split.py::test_group_shuffle_split_default_test_size[7-7-3]", "sklearn/model_selection/tests/test_split.py::test_group_shuffle_split_default_test_size[0.7-7-3]", "sklearn/model_selection/tests/test_split.py::test_stratified_shuffle_split_init", "sklearn/model_selection/tests/test_split.py::test_stratified_shuffle_split_respects_test_size", "sklearn/model_selection/tests/test_split.py::test_stratified_shuffle_split_iter", "sklearn/model_selection/tests/test_split.py::test_stratified_shuffle_split_even", "sklearn/model_selection/tests/test_split.py::test_stratified_shuffle_split_overlap_train_test_bug", "sklearn/model_selection/tests/test_split.py::test_stratified_shuffle_split_multilabel", "sklearn/model_selection/tests/test_split.py::test_stratified_shuffle_split_multilabel_many_labels", "sklearn/model_selection/tests/test_split.py::test_predefinedsplit_with_kfold_split", "sklearn/model_selection/tests/test_split.py::test_group_shuffle_split", "sklearn/model_selection/tests/test_split.py::test_leave_one_p_group_out", "sklearn/model_selection/tests/test_split.py::test_leave_group_out_changing_groups", "sklearn/model_selection/tests/test_split.py::test_leave_one_p_group_out_error_on_fewer_number_of_groups", "sklearn/model_selection/tests/test_split.py::test_repeated_cv_value_errors", "sklearn/model_selection/tests/test_split.py::test_repeated_kfold_determinstic_split", "sklearn/model_selection/tests/test_split.py::test_get_n_splits_for_repeated_kfold", "sklearn/model_selection/tests/test_split.py::test_get_n_splits_for_repeated_stratified_kfold", "sklearn/model_selection/tests/test_split.py::test_repeated_stratified_kfold_determinstic_split", "sklearn/model_selection/tests/test_split.py::test_train_test_split_errors", "sklearn/model_selection/tests/test_split.py::test_train_test_split_invalid_sizes1[1.2-0.8]", "sklearn/model_selection/tests/test_split.py::test_train_test_split_invalid_sizes1[1.0-0.8]", "sklearn/model_selection/tests/test_split.py::test_train_test_split_invalid_sizes1[0.0-0.8]", "sklearn/model_selection/tests/test_split.py::test_train_test_split_invalid_sizes1[-0.2-0.8]", "sklearn/model_selection/tests/test_split.py::test_train_test_split_invalid_sizes1[0.8-1.2]", "sklearn/model_selection/tests/test_split.py::test_train_test_split_invalid_sizes1[0.8-1.0]", "sklearn/model_selection/tests/test_split.py::test_train_test_split_invalid_sizes1[0.8-0.0]", "sklearn/model_selection/tests/test_split.py::test_train_test_split_invalid_sizes1[0.8--0.2]", "sklearn/model_selection/tests/test_split.py::test_train_test_split_invalid_sizes2[-10-0.8]", "sklearn/model_selection/tests/test_split.py::test_train_test_split_invalid_sizes2[0-0.8]", "sklearn/model_selection/tests/test_split.py::test_train_test_split_invalid_sizes2[11-0.8]", "sklearn/model_selection/tests/test_split.py::test_train_test_split_invalid_sizes2[0.8--10]", "sklearn/model_selection/tests/test_split.py::test_train_test_split_invalid_sizes2[0.8-0]", "sklearn/model_selection/tests/test_split.py::test_train_test_split_invalid_sizes2[0.8-11]", "sklearn/model_selection/tests/test_split.py::test_train_test_split_default_test_size[None-7-3]", "sklearn/model_selection/tests/test_split.py::test_train_test_split_default_test_size[8-8-2]", "sklearn/model_selection/tests/test_split.py::test_train_test_split_default_test_size[0.8-8-2]", "sklearn/model_selection/tests/test_split.py::test_train_test_split", "sklearn/model_selection/tests/test_split.py::test_train_test_split_pandas", "sklearn/model_selection/tests/test_split.py::test_train_test_split_sparse", "sklearn/model_selection/tests/test_split.py::test_train_test_split_mock_pandas", "sklearn/model_selection/tests/test_split.py::test_train_test_split_list_input", "sklearn/model_selection/tests/test_split.py::test_shufflesplit_errors[2.0-None]", "sklearn/model_selection/tests/test_split.py::test_shufflesplit_errors[1.0-None]", "sklearn/model_selection/tests/test_split.py::test_shufflesplit_errors[0.1-0.95]", "sklearn/model_selection/tests/test_split.py::test_shufflesplit_errors[None-train_size3]", "sklearn/model_selection/tests/test_split.py::test_shufflesplit_errors[11-None]", "sklearn/model_selection/tests/test_split.py::test_shufflesplit_errors[10-None]", "sklearn/model_selection/tests/test_split.py::test_shufflesplit_errors[8-3]", "sklearn/model_selection/tests/test_split.py::test_shufflesplit_reproducible", "sklearn/model_selection/tests/test_split.py::test_stratifiedshufflesplit_list_input", "sklearn/model_selection/tests/test_split.py::test_train_test_split_allow_nans", "sklearn/model_selection/tests/test_split.py::test_check_cv", "sklearn/model_selection/tests/test_split.py::test_cv_iterable_wrapper", "sklearn/model_selection/tests/test_split.py::test_group_kfold", "sklearn/model_selection/tests/test_split.py::test_time_series_cv", "sklearn/model_selection/tests/test_split.py::test_time_series_max_train_size", "sklearn/model_selection/tests/test_split.py::test_nested_cv", "sklearn/model_selection/tests/test_split.py::test_build_repr", "sklearn/model_selection/tests/test_split.py::test_shuffle_split_empty_trainset[ShuffleSplit]", "sklearn/model_selection/tests/test_split.py::test_shuffle_split_empty_trainset[GroupShuffleSplit]", "sklearn/model_selection/tests/test_split.py::test_shuffle_split_empty_trainset[StratifiedShuffleSplit]", "sklearn/model_selection/tests/test_split.py::test_train_test_split_empty_trainset", "sklearn/model_selection/tests/test_split.py::test_leave_one_out_empty_trainset", "sklearn/model_selection/tests/test_split.py::test_leave_p_out_empty_trainset"]

**Base Commit**: 06632c0d185128a53c57ccc73b25b6408e90bb89
**Environment Setup Commit**: 7e85a6d1f038bbb932b36f18d75df6be937ed00d
