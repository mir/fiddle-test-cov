# scikit-learn__scikit-learn-11281

**Repository**: scikit-learn/scikit-learn
**Created**: 2018-06-15T17:15:25Z
**Version**: 0.20

## Problem Statement

Should mixture models have a clusterer-compatible interface
Mixture models are currently a bit different. They are basically clusterers, except they are probabilistic, and are applied to inductive problems unlike many clusterers. But they are unlike clusterers in API:
* they have an `n_components` parameter, with identical purpose to `n_clusters`
* they do not store the `labels_` of the training data
* they do not have a `fit_predict` method

And they are almost entirely documented separately.

Should we make the MMs more like clusterers?


## Hints

In my opinion, yes.

I wanted to compare K-Means, GMM and HDBSCAN and was very disappointed that GMM does not have a `fit_predict` method. The HDBSCAN examples use `fit_predict`, so I was expecting GMM to have the same interface.
I think we should add ``fit_predict`` at least. I wouldn't rename ``n_components``.
I would like to work on this!
@Eight1911 go for it. It is probably relatively simple but maybe not entirely trivial.
@Eight1911 Mind if I take a look at this?
@Eight1911 Do you mind if I jump in as well?

## Patch

```diff

diff --git a/sklearn/mixture/base.py b/sklearn/mixture/base.py
--- a/sklearn/mixture/base.py
+++ b/sklearn/mixture/base.py
@@ -172,7 +172,7 @@ def _initialize(self, X, resp):
     def fit(self, X, y=None):
         """Estimate model parameters with the EM algorithm.
 
-        The method fit the model `n_init` times and set the parameters with
+        The method fits the model `n_init` times and set the parameters with
         which the model has the largest likelihood or lower bound. Within each
         trial, the method iterates between E-step and M-step for `max_iter`
         times until the change of likelihood or lower bound is less than
@@ -188,6 +188,32 @@ def fit(self, X, y=None):
         -------
         self
         """
+        self.fit_predict(X, y)
+        return self
+
+    def fit_predict(self, X, y=None):
+        """Estimate model parameters using X and predict the labels for X.
+
+        The method fits the model n_init times and sets the parameters with
+        which the model has the largest likelihood or lower bound. Within each
+        trial, the method iterates between E-step and M-step for `max_iter`
+        times until the change of likelihood or lower bound is less than
+        `tol`, otherwise, a `ConvergenceWarning` is raised. After fitting, it
+        predicts the most probable label for the input data points.
+
+        .. versionadded:: 0.20
+
+        Parameters
+        ----------
+        X : array-like, shape (n_samples, n_features)
+            List of n_features-dimensional data points. Each row
+            corresponds to a single data point.
+
+        Returns
+        -------
+        labels : array, shape (n_samples,)
+            Component labels.
+        """
         X = _check_X(X, self.n_components, ensure_min_samples=2)
         self._check_initial_parameters(X)
 
@@ -240,7 +266,7 @@ def fit(self, X, y=None):
         self._set_parameters(best_params)
         self.n_iter_ = best_n_iter
 
-        return self
+        return log_resp.argmax(axis=1)
 
     def _e_step(self, X):
         """E step.


```

## Test Patch

```diff
diff --git a/sklearn/mixture/tests/test_bayesian_mixture.py b/sklearn/mixture/tests/test_bayesian_mixture.py
--- a/sklearn/mixture/tests/test_bayesian_mixture.py
+++ b/sklearn/mixture/tests/test_bayesian_mixture.py
@@ -1,12 +1,16 @@
 # Author: Wei Xue <xuewei4d@gmail.com>
 #         Thierry Guillemot <thierry.guillemot.work@gmail.com>
 # License: BSD 3 clause
+import copy
 
 import numpy as np
 from scipy.special import gammaln
 
 from sklearn.utils.testing import assert_raise_message
 from sklearn.utils.testing import assert_almost_equal
+from sklearn.utils.testing import assert_array_equal
+
+from sklearn.metrics.cluster import adjusted_rand_score
 
 from sklearn.mixture.bayesian_mixture import _log_dirichlet_norm
 from sklearn.mixture.bayesian_mixture import _log_wishart_norm
@@ -14,7 +18,7 @@
 from sklearn.mixture import BayesianGaussianMixture
 
 from sklearn.mixture.tests.test_gaussian_mixture import RandomData
-from sklearn.exceptions import ConvergenceWarning
+from sklearn.exceptions import ConvergenceWarning, NotFittedError
 from sklearn.utils.testing import assert_greater_equal, ignore_warnings
 
 
@@ -419,3 +423,49 @@ def test_invariant_translation():
             assert_almost_equal(bgmm1.means_, bgmm2.means_ - 100)
             assert_almost_equal(bgmm1.weights_, bgmm2.weights_)
             assert_almost_equal(bgmm1.covariances_, bgmm2.covariances_)
+
+
+def test_bayesian_mixture_fit_predict():
+    rng = np.random.RandomState(0)
+    rand_data = RandomData(rng, scale=7)
+    n_components = 2 * rand_data.n_components
+
+    for covar_type in COVARIANCE_TYPE:
+        bgmm1 = BayesianGaussianMixture(n_components=n_components,
+                                        max_iter=100, random_state=rng,
+                                        tol=1e-3, reg_covar=0)
+        bgmm1.covariance_type = covar_type
+        bgmm2 = copy.deepcopy(bgmm1)
+        X = rand_data.X[covar_type]
+
+        Y_pred1 = bgmm1.fit(X).predict(X)
+        Y_pred2 = bgmm2.fit_predict(X)
+        assert_array_equal(Y_pred1, Y_pred2)
+
+
+def test_bayesian_mixture_predict_predict_proba():
+    # this is the same test as test_gaussian_mixture_predict_predict_proba()
+    rng = np.random.RandomState(0)
+    rand_data = RandomData(rng)
+    for prior_type in PRIOR_TYPE:
+        for covar_type in COVARIANCE_TYPE:
+            X = rand_data.X[covar_type]
+            Y = rand_data.Y
+            bgmm = BayesianGaussianMixture(
+                n_components=rand_data.n_components,
+                random_state=rng,
+                weight_concentration_prior_type=prior_type,
+                covariance_type=covar_type)
+
+            # Check a warning message arrive if we don't do fit
+            assert_raise_message(NotFittedError,
+                                 "This BayesianGaussianMixture instance"
+                                 " is not fitted yet. Call 'fit' with "
+                                 "appropriate arguments before using "
+                                 "this method.", bgmm.predict, X)
+
+            bgmm.fit(X)
+            Y_pred = bgmm.predict(X)
+            Y_pred_proba = bgmm.predict_proba(X).argmax(axis=1)
+            assert_array_equal(Y_pred, Y_pred_proba)
+            assert_greater_equal(adjusted_rand_score(Y, Y_pred), .95)
diff --git a/sklearn/mixture/tests/test_gaussian_mixture.py b/sklearn/mixture/tests/test_gaussian_mixture.py
--- a/sklearn/mixture/tests/test_gaussian_mixture.py
+++ b/sklearn/mixture/tests/test_gaussian_mixture.py
@@ -3,6 +3,7 @@
 # License: BSD 3 clause
 
 import sys
+import copy
 import warnings
 
 import numpy as np
@@ -569,6 +570,26 @@ def test_gaussian_mixture_predict_predict_proba():
         assert_greater(adjusted_rand_score(Y, Y_pred), .95)
 
 
+def test_gaussian_mixture_fit_predict():
+    rng = np.random.RandomState(0)
+    rand_data = RandomData(rng)
+    for covar_type in COVARIANCE_TYPE:
+        X = rand_data.X[covar_type]
+        Y = rand_data.Y
+        g = GaussianMixture(n_components=rand_data.n_components,
+                            random_state=rng, weights_init=rand_data.weights,
+                            means_init=rand_data.means,
+                            precisions_init=rand_data.precisions[covar_type],
+                            covariance_type=covar_type)
+
+        # check if fit_predict(X) is equivalent to fit(X).predict(X)
+        f = copy.deepcopy(g)
+        Y_pred1 = f.fit(X).predict(X)
+        Y_pred2 = g.fit_predict(X)
+        assert_array_equal(Y_pred1, Y_pred2)
+        assert_greater(adjusted_rand_score(Y, Y_pred2), .95)
+
+
 def test_gaussian_mixture_fit():
     # recover the ground truth
     rng = np.random.RandomState(0)

```

## Test Information

**Tests that should FAIL→PASS**: ["sklearn/mixture/tests/test_bayesian_mixture.py::test_bayesian_mixture_fit_predict", "sklearn/mixture/tests/test_gaussian_mixture.py::test_gaussian_mixture_fit_predict"]

**Tests that should PASS→PASS**: ["sklearn/mixture/tests/test_bayesian_mixture.py::test_log_dirichlet_norm", "sklearn/mixture/tests/test_bayesian_mixture.py::test_log_wishart_norm", "sklearn/mixture/tests/test_bayesian_mixture.py::test_bayesian_mixture_covariance_type", "sklearn/mixture/tests/test_bayesian_mixture.py::test_bayesian_mixture_weight_concentration_prior_type", "sklearn/mixture/tests/test_bayesian_mixture.py::test_bayesian_mixture_weights_prior_initialisation", "sklearn/mixture/tests/test_bayesian_mixture.py::test_bayesian_mixture_means_prior_initialisation", "sklearn/mixture/tests/test_bayesian_mixture.py::test_bayesian_mixture_precisions_prior_initialisation", "sklearn/mixture/tests/test_bayesian_mixture.py::test_bayesian_mixture_check_is_fitted", "sklearn/mixture/tests/test_bayesian_mixture.py::test_bayesian_mixture_weights", "sklearn/mixture/tests/test_bayesian_mixture.py::test_monotonic_likelihood", "sklearn/mixture/tests/test_bayesian_mixture.py::test_compare_covar_type", "sklearn/mixture/tests/test_bayesian_mixture.py::test_check_covariance_precision", "sklearn/mixture/tests/test_bayesian_mixture.py::test_invariant_translation", "sklearn/mixture/tests/test_bayesian_mixture.py::test_bayesian_mixture_predict_predict_proba", "sklearn/mixture/tests/test_gaussian_mixture.py::test_gaussian_mixture_attributes", "sklearn/mixture/tests/test_gaussian_mixture.py::test_check_X", "sklearn/mixture/tests/test_gaussian_mixture.py::test_check_weights", "sklearn/mixture/tests/test_gaussian_mixture.py::test_check_means", "sklearn/mixture/tests/test_gaussian_mixture.py::test_check_precisions", "sklearn/mixture/tests/test_gaussian_mixture.py::test_suffstat_sk_full", "sklearn/mixture/tests/test_gaussian_mixture.py::test_suffstat_sk_tied", "sklearn/mixture/tests/test_gaussian_mixture.py::test_suffstat_sk_diag", "sklearn/mixture/tests/test_gaussian_mixture.py::test_gaussian_suffstat_sk_spherical", "sklearn/mixture/tests/test_gaussian_mixture.py::test_compute_log_det_cholesky", "sklearn/mixture/tests/test_gaussian_mixture.py::test_gaussian_mixture_log_probabilities", "sklearn/mixture/tests/test_gaussian_mixture.py::test_gaussian_mixture_estimate_log_prob_resp", "sklearn/mixture/tests/test_gaussian_mixture.py::test_gaussian_mixture_predict_predict_proba", "sklearn/mixture/tests/test_gaussian_mixture.py::test_gaussian_mixture_fit", "sklearn/mixture/tests/test_gaussian_mixture.py::test_gaussian_mixture_fit_best_params", "sklearn/mixture/tests/test_gaussian_mixture.py::test_gaussian_mixture_fit_convergence_warning", "sklearn/mixture/tests/test_gaussian_mixture.py::test_multiple_init", "sklearn/mixture/tests/test_gaussian_mixture.py::test_gaussian_mixture_n_parameters", "sklearn/mixture/tests/test_gaussian_mixture.py::test_bic_1d_1component", "sklearn/mixture/tests/test_gaussian_mixture.py::test_gaussian_mixture_aic_bic", "sklearn/mixture/tests/test_gaussian_mixture.py::test_gaussian_mixture_verbose", "sklearn/mixture/tests/test_gaussian_mixture.py::test_warm_start", "sklearn/mixture/tests/test_gaussian_mixture.py::test_score", "sklearn/mixture/tests/test_gaussian_mixture.py::test_score_samples", "sklearn/mixture/tests/test_gaussian_mixture.py::test_monotonic_likelihood", "sklearn/mixture/tests/test_gaussian_mixture.py::test_regularisation", "sklearn/mixture/tests/test_gaussian_mixture.py::test_property", "sklearn/mixture/tests/test_gaussian_mixture.py::test_sample", "sklearn/mixture/tests/test_gaussian_mixture.py::test_init"]

**Base Commit**: 4143356c3c51831300789e4fdf795d83716dbab6
**Environment Setup Commit**: 55bf5d93e5674f13a1134d93a11fd0cd11aabcd1
