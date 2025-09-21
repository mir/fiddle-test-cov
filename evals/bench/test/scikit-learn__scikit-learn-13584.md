# scikit-learn__scikit-learn-13584

**Repository**: scikit-learn/scikit-learn
**Created**: 2019-04-05T23:09:48Z
**Version**: 0.21

## Problem Statement

bug in print_changed_only in new repr: vector values
```python
import sklearn
import numpy as np
from sklearn.linear_model import LogisticRegressionCV
sklearn.set_config(print_changed_only=True)
print(LogisticRegressionCV(Cs=np.array([0.1, 1])))
```
> ValueError: The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()

ping @NicolasHug 



## Patch

```diff

diff --git a/sklearn/utils/_pprint.py b/sklearn/utils/_pprint.py
--- a/sklearn/utils/_pprint.py
+++ b/sklearn/utils/_pprint.py
@@ -95,7 +95,7 @@ def _changed_params(estimator):
     init_params = signature(init_func).parameters
     init_params = {name: param.default for name, param in init_params.items()}
     for k, v in params.items():
-        if (v != init_params[k] and
+        if (repr(v) != repr(init_params[k]) and
                 not (is_scalar_nan(init_params[k]) and is_scalar_nan(v))):
             filtered_params[k] = v
     return filtered_params


```

## Test Patch

```diff
diff --git a/sklearn/utils/tests/test_pprint.py b/sklearn/utils/tests/test_pprint.py
--- a/sklearn/utils/tests/test_pprint.py
+++ b/sklearn/utils/tests/test_pprint.py
@@ -4,6 +4,7 @@
 import numpy as np
 
 from sklearn.utils._pprint import _EstimatorPrettyPrinter
+from sklearn.linear_model import LogisticRegressionCV
 from sklearn.pipeline import make_pipeline
 from sklearn.base import BaseEstimator, TransformerMixin
 from sklearn.feature_selection import SelectKBest, chi2
@@ -212,6 +213,9 @@ def test_changed_only():
     expected = """SimpleImputer()"""
     assert imputer.__repr__() == expected
 
+    # make sure array parameters don't throw error (see #13583)
+    repr(LogisticRegressionCV(Cs=np.array([0.1, 1])))
+
     set_config(print_changed_only=False)
 
 

```

## Test Information

**Tests that should FAIL→PASS**: ["sklearn/utils/tests/test_pprint.py::test_changed_only", "sklearn/utils/tests/test_pprint.py::test_pipeline", "sklearn/utils/tests/test_pprint.py::test_deeply_nested", "sklearn/utils/tests/test_pprint.py::test_gridsearch", "sklearn/utils/tests/test_pprint.py::test_gridsearch_pipeline", "sklearn/utils/tests/test_pprint.py::test_n_max_elements_to_show"]

**Tests that should PASS→PASS**: ["sklearn/utils/tests/test_pprint.py::test_basic", "sklearn/utils/tests/test_pprint.py::test_length_constraint", "sklearn/utils/tests/test_pprint.py::test_builtin_prettyprinter"]

**Base Commit**: 0e3c1879b06d839171b7d0a607d71bbb19a966a9
**Environment Setup Commit**: 7813f7efb5b2012412888b69e73d76f2df2b50b6
