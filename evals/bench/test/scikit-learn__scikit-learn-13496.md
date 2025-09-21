# scikit-learn__scikit-learn-13496

**Repository**: scikit-learn/scikit-learn
**Created**: 2019-03-23T09:46:59Z
**Version**: 0.21

## Problem Statement

Expose warm_start in Isolation forest
It seems to me that `sklearn.ensemble.IsolationForest` supports incremental addition of new trees with the `warm_start` parameter of its parent class, `sklearn.ensemble.BaseBagging`.

Even though this parameter is not exposed in `__init__()` , it gets inherited from `BaseBagging` and one can use it by changing it to `True` after initialization. To make it work, you have to also increment `n_estimators` on every iteration. 

It took me a while to notice that it actually works, and I had to inspect the source code of both `IsolationForest` and `BaseBagging`. Also, it looks to me that the behavior is in-line with `sklearn.ensemble.BaseForest` that is behind e.g. `sklearn.ensemble.RandomForestClassifier`.

To make it more easier to use, I'd suggest to:
* expose `warm_start` in `IsolationForest.__init__()`, default `False`;
* document it in the same way as it is documented for `RandomForestClassifier`, i.e. say:
```py
    warm_start : bool, optional (default=False)
        When set to ``True``, reuse the solution of the previous call to fit
        and add more estimators to the ensemble, otherwise, just fit a whole
        new forest. See :term:`the Glossary <warm_start>`.
```
* add a test to make sure it works properly;
* possibly also mention in the "IsolationForest example" documentation entry;



## Hints

+1 to expose `warm_start` in `IsolationForest`, unless there was a good reason for not doing so in the first place. I could not find any related discussion in the IsolationForest PR #4163. ping @ngoix @agramfort?
no objection

>

PR welcome @petibear. Feel
free to ping me when it’s ready for reviews :).
OK, I'm working on it then. 
Happy to learn the process (of contributing) here. 

## Patch

```diff

diff --git a/sklearn/ensemble/iforest.py b/sklearn/ensemble/iforest.py
--- a/sklearn/ensemble/iforest.py
+++ b/sklearn/ensemble/iforest.py
@@ -120,6 +120,12 @@ class IsolationForest(BaseBagging, OutlierMixin):
     verbose : int, optional (default=0)
         Controls the verbosity of the tree building process.
 
+    warm_start : bool, optional (default=False)
+        When set to ``True``, reuse the solution of the previous call to fit
+        and add more estimators to the ensemble, otherwise, just fit a whole
+        new forest. See :term:`the Glossary <warm_start>`.
+
+        .. versionadded:: 0.21
 
     Attributes
     ----------
@@ -173,7 +179,8 @@ def __init__(self,
                  n_jobs=None,
                  behaviour='old',
                  random_state=None,
-                 verbose=0):
+                 verbose=0,
+                 warm_start=False):
         super().__init__(
             base_estimator=ExtraTreeRegressor(
                 max_features=1,
@@ -185,6 +192,7 @@ def __init__(self,
             n_estimators=n_estimators,
             max_samples=max_samples,
             max_features=max_features,
+            warm_start=warm_start,
             n_jobs=n_jobs,
             random_state=random_state,
             verbose=verbose)


```

## Test Patch

```diff
diff --git a/sklearn/ensemble/tests/test_iforest.py b/sklearn/ensemble/tests/test_iforest.py
--- a/sklearn/ensemble/tests/test_iforest.py
+++ b/sklearn/ensemble/tests/test_iforest.py
@@ -295,6 +295,28 @@ def test_score_samples():
                        clf2.score_samples([[2., 2.]]))
 
 
+@pytest.mark.filterwarnings('ignore:default contamination')
+@pytest.mark.filterwarnings('ignore:behaviour="old"')
+def test_iforest_warm_start():
+    """Test iterative addition of iTrees to an iForest """
+
+    rng = check_random_state(0)
+    X = rng.randn(20, 2)
+
+    # fit first 10 trees
+    clf = IsolationForest(n_estimators=10, max_samples=20,
+                          random_state=rng, warm_start=True)
+    clf.fit(X)
+    # remember the 1st tree
+    tree_1 = clf.estimators_[0]
+    # fit another 10 trees
+    clf.set_params(n_estimators=20)
+    clf.fit(X)
+    # expecting 20 fitted trees and no overwritten trees
+    assert len(clf.estimators_) == 20
+    assert clf.estimators_[0] is tree_1
+
+
 @pytest.mark.filterwarnings('ignore:default contamination')
 @pytest.mark.filterwarnings('ignore:behaviour="old"')
 def test_deprecation():

```

## Test Information

**Tests that should FAIL→PASS**: ["sklearn/ensemble/tests/test_iforest.py::test_iforest_warm_start"]

**Tests that should PASS→PASS**: ["sklearn/ensemble/tests/test_iforest.py::test_iforest", "sklearn/ensemble/tests/test_iforest.py::test_iforest_sparse", "sklearn/ensemble/tests/test_iforest.py::test_iforest_error", "sklearn/ensemble/tests/test_iforest.py::test_recalculate_max_depth", "sklearn/ensemble/tests/test_iforest.py::test_max_samples_attribute", "sklearn/ensemble/tests/test_iforest.py::test_iforest_parallel_regression", "sklearn/ensemble/tests/test_iforest.py::test_iforest_performance", "sklearn/ensemble/tests/test_iforest.py::test_iforest_works[0.25]", "sklearn/ensemble/tests/test_iforest.py::test_iforest_works[auto]", "sklearn/ensemble/tests/test_iforest.py::test_max_samples_consistency", "sklearn/ensemble/tests/test_iforest.py::test_iforest_subsampled_features", "sklearn/ensemble/tests/test_iforest.py::test_iforest_average_path_length", "sklearn/ensemble/tests/test_iforest.py::test_score_samples", "sklearn/ensemble/tests/test_iforest.py::test_deprecation", "sklearn/ensemble/tests/test_iforest.py::test_behaviour_param", "sklearn/ensemble/tests/test_iforest.py::test_iforest_chunks_works1[0.25-3]", "sklearn/ensemble/tests/test_iforest.py::test_iforest_chunks_works1[auto-2]", "sklearn/ensemble/tests/test_iforest.py::test_iforest_chunks_works2[0.25-3]", "sklearn/ensemble/tests/test_iforest.py::test_iforest_chunks_works2[auto-2]"]

**Base Commit**: 3aefc834dce72e850bff48689bea3c7dff5f3fad
**Environment Setup Commit**: 7813f7efb5b2012412888b69e73d76f2df2b50b6
