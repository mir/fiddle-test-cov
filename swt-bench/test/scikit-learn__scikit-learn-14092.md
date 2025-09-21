# scikit-learn__scikit-learn-14092

**Repository**: scikit-learn/scikit-learn
**Created**: 2019-06-14T14:16:17Z
**Version**: 0.22

## Problem Statement

NCA fails in GridSearch due to too strict parameter checks
NCA checks its parameters to have a specific type, which can easily fail in a GridSearch due to how param grid is made.

Here is an example:
```python
import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import NeighborhoodComponentsAnalysis
from sklearn.neighbors import KNeighborsClassifier

X = np.random.random_sample((100, 10))
y = np.random.randint(2, size=100)

nca = NeighborhoodComponentsAnalysis()
knn = KNeighborsClassifier()

pipe = Pipeline([('nca', nca),
                 ('knn', knn)])
                
params = {'nca__tol': [0.1, 0.5, 1],
          'nca__n_components': np.arange(1, 10)}
          
gs = GridSearchCV(estimator=pipe, param_grid=params, error_score='raise')
gs.fit(X,y)
```

The issue is that for `tol`: 1 is not a float, and for  `n_components`: np.int64 is not int

Before proposing a fix for this specific situation, I'd like to have your general opinion about parameter checking.  
I like this idea of common parameter checking tool introduced with the NCA PR. What do you think about extending it across the code-base (or at least for new or recent estimators) ?

Currently parameter checking is not always done or often partially done, and is quite redundant. For instance, here is the input validation of lda:
```python
def _check_params(self):
        """Check model parameters."""
        if self.n_components <= 0:
            raise ValueError("Invalid 'n_components' parameter: %r"
                             % self.n_components)

        if self.total_samples <= 0:
            raise ValueError("Invalid 'total_samples' parameter: %r"
                             % self.total_samples)

        if self.learning_offset < 0:
            raise ValueError("Invalid 'learning_offset' parameter: %r"
                             % self.learning_offset)

        if self.learning_method not in ("batch", "online"):
            raise ValueError("Invalid 'learning_method' parameter: %r"
                             % self.learning_method)
```
most params aren't checked and for those who are there's a lot of duplicated code.

A propose to be upgrade the new tool to be able to check open/closed intervals (currently only closed) and list membership.

The api would be something like that:
```
check_param(param, name, valid_options)
```
where valid_options would be a dict of `type: constraint`. e.g for the `beta_loss` param of `NMF`, it can be either a float or a string in a list, which would give
```
valid_options = {numbers.Real: None,  # None for no constraint
                 str: ['frobenius', 'kullback-leibler', 'itakura-saito']}
```
Sometimes a parameter can only be positive or within a given interval, e.g. `l1_ratio` of `LogisticRegression` must be between 0 and 1, which would give
```
valid_options = {numbers.Real: Interval(0, 1, closed='both')}
```
positivity of e.g. `max_iter` would be `numbers.Integral: Interval(left=1)`.


## Hints

I have developed a framework, experimenting with parameter verification: https://github.com/thomasjpfan/skconfig (Don't expect the API to be stable)

Your idea of using a simple dict for union types is really nice!

Edit: I am currently trying out another idea. I'll update this issue when it becomes something presentable.
If I understood correctly your package is designed for a sklearn user, who has to implement its validator for each estimator, or did I get it wrong ?
I think we want to keep the param validation inside the estimators.

> Edit: I am currently trying out another idea. I'll update this issue when it becomes something presentable.

maybe you can pitch me and if you want I can give a hand :)
I would have loved to using the typing system to get this to work:

```py
def __init__(
    self,
    C: Annotated[float, Range('[0, Inf)')],
    ...)
```

but that would have to wait for [PEP 593](https://www.python.org/dev/peps/pep-0593/). In the end, I would want the validator to be a part of sklearn estimators. Using typing (as above) is a natural choice, since it keeps the parameter and its constraint physically close to each other.

If we can't use typing, these constraints can be place in a `_validate_parameters` method. This will be called at the beginning of fit to do parameter validation. Estimators that need more validation will overwrite the method, call `super()._validate_parameters` and do more validation. For example, `LogesticRegression`'s `penalty='l2'` only works for specify solvers. `skconfig` defines a framework for handling these situations, but I think it would be too hard to learn.
>  Using typing (as above) is a natural choice

I agree, and to go further it would be really nice to use them for the coverage to check that every possible type of a parameter is covered by tests

> If we can't use typing, these constraints can be place in a _validate_parameters method. 

This is already the case for a subset of the estimators (`_check_params` or `_validate_input`). But it's often incomplete.

> skconfig defines a framework for handling these situations, but I think it would be too hard to learn.

Your framework does way more than what I proposed. Maybe we can do this in 2 steps:
First, a simple single param check which only checks its type and if its value is acceptable in general (e.g. positive for a number of clusters). This will raise a standard error message
Then a more advanced check, depending on the data (e.g. number of clusters should be < n_samples) or consistency across params (e.g. solver + penalty). These checks require more elaborate error messages.

wdyt ?

## Patch

```diff

diff --git a/sklearn/neighbors/nca.py b/sklearn/neighbors/nca.py
--- a/sklearn/neighbors/nca.py
+++ b/sklearn/neighbors/nca.py
@@ -13,6 +13,7 @@
 import numpy as np
 import sys
 import time
+import numbers
 from scipy.optimize import minimize
 from ..utils.extmath import softmax
 from ..metrics import pairwise_distances
@@ -299,7 +300,8 @@ def _validate_params(self, X, y):
 
         # Check the preferred dimensionality of the projected space
         if self.n_components is not None:
-            check_scalar(self.n_components, 'n_components', int, 1)
+            check_scalar(
+                self.n_components, 'n_components', numbers.Integral, 1)
 
             if self.n_components > X.shape[1]:
                 raise ValueError('The preferred dimensionality of the '
@@ -318,9 +320,9 @@ def _validate_params(self, X, y):
                                  .format(X.shape[1],
                                          self.components_.shape[1]))
 
-        check_scalar(self.max_iter, 'max_iter', int, 1)
-        check_scalar(self.tol, 'tol', float, 0.)
-        check_scalar(self.verbose, 'verbose', int, 0)
+        check_scalar(self.max_iter, 'max_iter', numbers.Integral, 1)
+        check_scalar(self.tol, 'tol', numbers.Real, 0.)
+        check_scalar(self.verbose, 'verbose', numbers.Integral, 0)
 
         if self.callback is not None:
             if not callable(self.callback):


```

## Test Patch

```diff
diff --git a/sklearn/neighbors/tests/test_nca.py b/sklearn/neighbors/tests/test_nca.py
--- a/sklearn/neighbors/tests/test_nca.py
+++ b/sklearn/neighbors/tests/test_nca.py
@@ -129,7 +129,7 @@ def test_params_validation():
     # TypeError
     assert_raises(TypeError, NCA(max_iter='21').fit, X, y)
     assert_raises(TypeError, NCA(verbose='true').fit, X, y)
-    assert_raises(TypeError, NCA(tol=1).fit, X, y)
+    assert_raises(TypeError, NCA(tol='1').fit, X, y)
     assert_raises(TypeError, NCA(n_components='invalid').fit, X, y)
     assert_raises(TypeError, NCA(warm_start=1).fit, X, y)
 
@@ -518,3 +518,17 @@ def test_convergence_warning():
     assert_warns_message(ConvergenceWarning,
                          '[{}] NCA did not converge'.format(cls_name),
                          nca.fit, iris_data, iris_target)
+
+
+@pytest.mark.parametrize('param, value', [('n_components', np.int32(3)),
+                                          ('max_iter', np.int32(100)),
+                                          ('tol', np.float32(0.0001))])
+def test_parameters_valid_types(param, value):
+    # check that no error is raised when parameters have numpy integer or
+    # floating types.
+    nca = NeighborhoodComponentsAnalysis(**{param: value})
+
+    X = iris_data
+    y = iris_target
+
+    nca.fit(X, y)

```

## Test Information

**Tests that should FAIL→PASS**: ["sklearn/neighbors/tests/test_nca.py::test_parameters_valid_types[n_components-value0]", "sklearn/neighbors/tests/test_nca.py::test_parameters_valid_types[max_iter-value1]", "sklearn/neighbors/tests/test_nca.py::test_parameters_valid_types[tol-value2]"]

**Tests that should PASS→PASS**: ["sklearn/neighbors/tests/test_nca.py::test_simple_example", "sklearn/neighbors/tests/test_nca.py::test_toy_example_collapse_points", "sklearn/neighbors/tests/test_nca.py::test_finite_differences", "sklearn/neighbors/tests/test_nca.py::test_params_validation", "sklearn/neighbors/tests/test_nca.py::test_transformation_dimensions", "sklearn/neighbors/tests/test_nca.py::test_n_components", "sklearn/neighbors/tests/test_nca.py::test_init_transformation", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-5-3-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-5-3-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-5-3-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-5-3-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-5-5-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-5-5-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-5-5-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-5-5-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-5-7-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-5-7-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-5-7-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-5-7-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-5-11-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-5-11-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-5-11-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-5-11-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-7-3-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-7-3-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-7-3-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-7-3-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-7-5-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-7-5-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-7-5-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-7-5-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-7-7-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-7-7-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-7-7-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-7-7-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-7-11-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-7-11-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-7-11-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-7-11-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-11-3-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-11-3-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-11-3-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-11-3-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-11-5-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-11-5-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-11-5-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-11-5-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-11-7-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-11-7-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-11-7-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-11-7-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-11-11-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-11-11-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-11-11-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[3-11-11-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-5-3-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-5-3-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-5-3-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-5-3-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-5-5-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-5-5-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-5-5-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-5-5-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-5-7-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-5-7-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-5-7-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-5-7-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-5-11-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-5-11-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-5-11-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-5-11-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-7-3-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-7-3-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-7-3-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-7-3-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-7-5-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-7-5-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-7-5-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-7-5-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-7-7-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-7-7-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-7-7-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-7-7-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-7-11-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-7-11-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-7-11-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-7-11-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-11-3-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-11-3-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-11-3-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-11-3-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-11-5-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-11-5-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-11-5-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-11-5-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-11-7-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-11-7-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-11-7-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-11-7-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-11-11-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-11-11-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-11-11-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[5-11-11-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-5-3-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-5-3-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-5-3-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-5-3-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-5-5-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-5-5-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-5-5-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-5-5-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-5-7-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-5-7-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-5-7-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-5-7-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-5-11-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-5-11-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-5-11-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-5-11-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-7-3-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-7-3-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-7-3-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-7-3-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-7-5-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-7-5-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-7-5-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-7-5-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-7-7-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-7-7-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-7-7-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-7-7-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-7-11-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-7-11-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-7-11-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-7-11-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-11-3-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-11-3-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-11-3-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-11-3-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-11-5-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-11-5-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-11-5-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-11-5-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-11-7-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-11-7-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-11-7-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-11-7-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-11-11-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-11-11-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-11-11-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[7-11-11-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-5-3-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-5-3-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-5-3-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-5-3-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-5-5-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-5-5-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-5-5-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-5-5-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-5-7-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-5-7-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-5-7-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-5-7-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-5-11-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-5-11-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-5-11-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-5-11-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-7-3-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-7-3-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-7-3-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-7-3-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-7-5-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-7-5-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-7-5-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-7-5-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-7-7-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-7-7-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-7-7-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-7-7-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-7-11-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-7-11-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-7-11-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-7-11-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-11-3-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-11-3-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-11-3-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-11-3-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-11-5-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-11-5-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-11-5-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-11-5-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-11-7-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-11-7-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-11-7-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-11-7-11]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-11-11-3]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-11-11-5]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-11-11-7]", "sklearn/neighbors/tests/test_nca.py::test_auto_init[11-11-11-11]", "sklearn/neighbors/tests/test_nca.py::test_warm_start_validation", "sklearn/neighbors/tests/test_nca.py::test_warm_start_effectiveness", "sklearn/neighbors/tests/test_nca.py::test_verbose[pca]", "sklearn/neighbors/tests/test_nca.py::test_verbose[lda]", "sklearn/neighbors/tests/test_nca.py::test_verbose[identity]", "sklearn/neighbors/tests/test_nca.py::test_verbose[random]", "sklearn/neighbors/tests/test_nca.py::test_verbose[precomputed]", "sklearn/neighbors/tests/test_nca.py::test_no_verbose", "sklearn/neighbors/tests/test_nca.py::test_singleton_class", "sklearn/neighbors/tests/test_nca.py::test_one_class", "sklearn/neighbors/tests/test_nca.py::test_callback", "sklearn/neighbors/tests/test_nca.py::test_expected_transformation_shape", "sklearn/neighbors/tests/test_nca.py::test_convergence_warning"]

**Base Commit**: df7dd8391148a873d157328a4f0328528a0c4ed9
**Environment Setup Commit**: 7e85a6d1f038bbb932b36f18d75df6be937ed00d
