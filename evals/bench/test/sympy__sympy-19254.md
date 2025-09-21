# sympy__sympy-19254

**Repository**: sympy/sympy
**Created**: 2020-05-04T13:38:13Z
**Version**: 1.7

## Problem Statement

sympy.polys.factortools.dmp_zz_mignotte_bound improvement
The method `dup_zz_mignotte_bound(f, K)` can be significantly improved by using the **Knuth-Cohen bound** instead. After our research with Prof. Ag.Akritas we have implemented the Knuth-Cohen bound among others, and compare them among dozens of polynomials with different degree, density and coefficients range. Considering the results and the feedback from Mr.Kalevi Suominen, our proposal is that the mignotte_bound should be replaced by the knuth-cohen bound.
Also, `dmp_zz_mignotte_bound(f, u, K)` for mutli-variants polynomials should be replaced appropriately.


## Patch

```diff

diff --git a/sympy/polys/factortools.py b/sympy/polys/factortools.py
--- a/sympy/polys/factortools.py
+++ b/sympy/polys/factortools.py
@@ -124,13 +124,64 @@ def dmp_trial_division(f, factors, u, K):
 
 
 def dup_zz_mignotte_bound(f, K):
-    """Mignotte bound for univariate polynomials in `K[x]`. """
-    a = dup_max_norm(f, K)
-    b = abs(dup_LC(f, K))
-    n = dup_degree(f)
+    """
+    The Knuth-Cohen variant of Mignotte bound for
+    univariate polynomials in `K[x]`.
 
-    return K.sqrt(K(n + 1))*2**n*a*b
+    Examples
+    ========
+
+    >>> from sympy.polys import ring, ZZ
+    >>> R, x = ring("x", ZZ)
+
+    >>> f = x**3 + 14*x**2 + 56*x + 64
+    >>> R.dup_zz_mignotte_bound(f)
+    152
+
+    By checking `factor(f)` we can see that max coeff is 8
+
+    Also consider a case that `f` is irreducible for example `f = 2*x**2 + 3*x + 4`
+    To avoid a bug for these cases, we return the bound plus the max coefficient of `f`
+
+    >>> f = 2*x**2 + 3*x + 4
+    >>> R.dup_zz_mignotte_bound(f)
+    6
+
+    Lastly,To see the difference between the new and the old Mignotte bound
+    consider the irreducible polynomial::
+
+    >>> f = 87*x**7 + 4*x**6 + 80*x**5 + 17*x**4 + 9*x**3 + 12*x**2 + 49*x + 26
+    >>> R.dup_zz_mignotte_bound(f)
+    744
+
+    The new Mignotte bound is 744 whereas the old one (SymPy 1.5.1) is 1937664.
+
+
+    References
+    ==========
+
+    ..[1] [Abbott2013]_
+
+    """
+    from sympy import binomial
+
+    d = dup_degree(f)
+    delta = _ceil(d / 2)
+    delta2 = _ceil(delta / 2)
+
+    # euclidean-norm
+    eucl_norm = K.sqrt( sum( [cf**2 for cf in f] ) )
+
+    # biggest values of binomial coefficients (p. 538 of reference)
+    t1 = binomial(delta - 1, delta2)
+    t2 = binomial(delta - 1, delta2 - 1)
+
+    lc = K.abs(dup_LC(f, K))   # leading coefficient
+    bound = t1 * eucl_norm + t2 * lc   # (p. 538 of reference)
+    bound += dup_max_norm(f, K) # add max coeff for irreducible polys
+    bound = _ceil(bound / 2) * 2   # round up to even integer
 
+    return bound
 
 def dmp_zz_mignotte_bound(f, u, K):
     """Mignotte bound for multivariate polynomials in `K[X]`. """


```

## Test Patch

```diff
diff --git a/sympy/polys/tests/test_factortools.py b/sympy/polys/tests/test_factortools.py
--- a/sympy/polys/tests/test_factortools.py
+++ b/sympy/polys/tests/test_factortools.py
@@ -27,7 +27,8 @@ def test_dmp_trial_division():
 
 def test_dup_zz_mignotte_bound():
     R, x = ring("x", ZZ)
-    assert R.dup_zz_mignotte_bound(2*x**2 + 3*x + 4) == 32
+    assert R.dup_zz_mignotte_bound(2*x**2 + 3*x + 4) == 6
+    assert R.dup_zz_mignotte_bound(x**3 + 14*x**2 + 56*x + 64) == 152
 
 
 def test_dmp_zz_mignotte_bound():

```

## Test Information

**Tests that should FAIL→PASS**: ["test_dup_zz_mignotte_bound"]

**Tests that should PASS→PASS**: ["test_dup_trial_division", "test_dmp_trial_division", "test_dmp_zz_mignotte_bound", "test_dup_zz_hensel_step", "test_dup_zz_hensel_lift", "test_dup_zz_irreducible_p", "test_dup_cyclotomic_p", "test_dup_zz_cyclotomic_poly", "test_dup_zz_cyclotomic_factor", "test_dup_zz_factor", "test_dmp_zz_wang", "test_issue_6355", "test_dmp_zz_factor", "test_dup_ext_factor", "test_dmp_ext_factor", "test_dup_factor_list", "test_dmp_factor_list", "test_dup_irreducible_p"]

**Base Commit**: e0ef1da13e2ab2a77866c05246f73c871ca9388c
**Environment Setup Commit**: cffd4e0f86fefd4802349a9f9b19ed70934ea354
