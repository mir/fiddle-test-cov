# sympy__sympy-13437

**Repository**: sympy/sympy
**Created**: 2017-10-12T18:21:19Z
**Version**: 1.1

## Problem Statement

bell(n).limit(n, oo) should be oo rather than bell(oo)
`bell(n).limit(n,oo)` should take the value infinity, but the current output is `bell(oo)`. As the Bell numbers represent the number of partitions of a set, it seems natural that `bell(oo)` should be able to be evaluated rather than be returned unevaluated. This issue is also in line with the recent fixes to the corresponding limit for the Fibonacci numbers and Lucas numbers.

```
from sympy import *
n = symbols('n')
bell(n).limit(n,oo)

Output:
bell(oo)
```

I'm new to Sympy, so I'd appreciate the opportunity to fix this bug myself if that's alright.



## Patch

```diff

diff --git a/sympy/functions/combinatorial/numbers.py b/sympy/functions/combinatorial/numbers.py
--- a/sympy/functions/combinatorial/numbers.py
+++ b/sympy/functions/combinatorial/numbers.py
@@ -424,6 +424,15 @@ def _bell_incomplete_poly(n, k, symbols):
 
     @classmethod
     def eval(cls, n, k_sym=None, symbols=None):
+        if n is S.Infinity:
+            if k_sym is None:
+                return S.Infinity
+            else:
+                raise ValueError("Bell polynomial is not defined")
+
+        if n.is_negative or n.is_integer is False:
+            raise ValueError("a non-negative integer expected")
+
         if n.is_Integer and n.is_nonnegative:
             if k_sym is None:
                 return Integer(cls._bell(int(n)))


```

## Test Patch

```diff
diff --git a/sympy/functions/combinatorial/tests/test_comb_numbers.py b/sympy/functions/combinatorial/tests/test_comb_numbers.py
--- a/sympy/functions/combinatorial/tests/test_comb_numbers.py
+++ b/sympy/functions/combinatorial/tests/test_comb_numbers.py
@@ -73,6 +73,11 @@ def test_bell():
     assert bell(1, x) == x
     assert bell(2, x) == x**2 + x
     assert bell(5, x) == x**5 + 10*x**4 + 25*x**3 + 15*x**2 + x
+    assert bell(oo) == S.Infinity
+    raises(ValueError, lambda: bell(oo, x))
+
+    raises(ValueError, lambda: bell(-1))
+    raises(ValueError, lambda: bell(S(1)/2))
 
     X = symbols('x:6')
     # X = (x0, x1, .. x5)
@@ -99,9 +104,9 @@ def test_bell():
     for i in [0, 2, 3, 7, 13, 42, 55]:
         assert bell(i).evalf() == bell(n).rewrite(Sum).evalf(subs={n: i})
 
-    # For negative numbers, the formula does not hold
-    m = Symbol('m', integer=True)
-    assert bell(-1).evalf() == bell(m).rewrite(Sum).evalf(subs={m: -1})
+    # issue 9184
+    n = Dummy('n')
+    assert bell(n).limit(n, S.Infinity) == S.Infinity
 
 
 def test_harmonic():

```

## Test Information

**Tests that should FAIL→PASS**: ["test_bell"]

**Tests that should PASS→PASS**: ["test_bernoulli", "test_fibonacci", "test_harmonic", "test_harmonic_rational", "test_harmonic_evalf", "test_harmonic_rewrite_polygamma", "test_harmonic_rewrite_sum", "test_euler", "test_euler_odd", "test_euler_polynomials", "test_euler_polynomial_rewrite", "test_catalan", "test_genocchi", "test_nC_nP_nT", "test_issue_8496"]

**Base Commit**: 674afc619d7f5c519b6a5393a8b0532a131e57e0
**Environment Setup Commit**: ec9e3c0436fbff934fa84e22bf07f1b3ef5bfac3
