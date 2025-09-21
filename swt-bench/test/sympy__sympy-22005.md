# sympy__sympy-22005

**Repository**: sympy/sympy
**Created**: 2021-09-02T13:05:27Z
**Version**: 1.9

## Problem Statement

detection of infinite solution request
```python
>>> solve_poly_system((x - 1,), x, y)
Traceback (most recent call last):
...
NotImplementedError:
only zero-dimensional systems supported (finite number of solutions)
>>> solve_poly_system((y - 1,), x, y)  <--- this is not handled correctly
[(1,)]
```
```diff
diff --git a/sympy/solvers/polysys.py b/sympy/solvers/polysys.py
index b9809fd4e9..674322d4eb 100644
--- a/sympy/solvers/polysys.py
+++ b/sympy/solvers/polysys.py
@@ -240,7 +240,7 @@ def _solve_reduced_system(system, gens, entry=False):
 
         univariate = list(filter(_is_univariate, basis))
 
-        if len(univariate) == 1:
+        if len(univariate) == 1 and len(gens) == 1:
             f = univariate.pop()
         else:
             raise NotImplementedError(filldedent('''
diff --git a/sympy/solvers/tests/test_polysys.py b/sympy/solvers/tests/test_polysys.py
index 58419f8762..9e674a6fe6 100644
--- a/sympy/solvers/tests/test_polysys.py
+++ b/sympy/solvers/tests/test_polysys.py
@@ -48,6 +48,10 @@ def test_solve_poly_system():
     raises(NotImplementedError, lambda: solve_poly_system(
         [z, -2*x*y**2 + x + y**2*z, y**2*(-z - 4) + 2]))
     raises(PolynomialError, lambda: solve_poly_system([1/x], x))
+    raises(NotImplementedError, lambda: solve_poly_system(
+        Poly(x - 1, x, y), (x, y)))
+    raises(NotImplementedError, lambda: solve_poly_system(
+        Poly(y - 1, x, y), (x, y)))
 
 
 def test_solve_biquadratic():
```


## Hints

This is not a possible solution i feel , since some of the tests are failing and also weirdly `solve_poly_system([2*x - 3, y*Rational(3, 2) - 2*x, z - 5*y], x, y, z)`  is throwing a `NotImplementedError` .
Hmm. Well, they should yield similar results: an error or a solution. Looks like maybe a solution, then, should be returned? I am not sure. Maybe @jksuom would have some idea.
It seems that the number of polynomials in the Gröbner basis should be the same as the number of variables so there should be something like
```
    if len(basis) != len(gens):
        raise NotImplementedError(...)
> It seems that the number of polynomials in the Gröbner basis should be the same as the number of variables

This raises a `NotImplementedError` for `solve_poly_system([x*y - 2*y, 2*y**2 - x**2], x, y)` but which isn't the case since it has a solution.
It looks like the test could be `if len(basis) < len(gens)` though I'm not sure if the implementation can handle all cases where `len(basis) > len(gens)`.
Yes this works and now `solve_poly_system((y - 1,), x, y)` also returns `NotImplementedError` , I'll open a PR for this.
I'm not sure but all cases of `len(basis) > len(gens)` are being handled.

## Patch

```diff

diff --git a/sympy/solvers/polysys.py b/sympy/solvers/polysys.py
--- a/sympy/solvers/polysys.py
+++ b/sympy/solvers/polysys.py
@@ -240,6 +240,12 @@ def _solve_reduced_system(system, gens, entry=False):
 
         univariate = list(filter(_is_univariate, basis))
 
+        if len(basis) < len(gens):
+            raise NotImplementedError(filldedent('''
+                only zero-dimensional systems supported
+                (finite number of solutions)
+                '''))
+
         if len(univariate) == 1:
             f = univariate.pop()
         else:


```

## Test Patch

```diff
diff --git a/sympy/solvers/tests/test_polysys.py b/sympy/solvers/tests/test_polysys.py
--- a/sympy/solvers/tests/test_polysys.py
+++ b/sympy/solvers/tests/test_polysys.py
@@ -49,6 +49,11 @@ def test_solve_poly_system():
         [z, -2*x*y**2 + x + y**2*z, y**2*(-z - 4) + 2]))
     raises(PolynomialError, lambda: solve_poly_system([1/x], x))
 
+    raises(NotImplementedError, lambda: solve_poly_system(
+          [x-1,], (x, y)))
+    raises(NotImplementedError, lambda: solve_poly_system(
+          [y-1,], (x, y)))
+
 
 def test_solve_biquadratic():
     x0, y0, x1, y1, r = symbols('x0 y0 x1 y1 r')

```

## Test Information

**Tests that should FAIL→PASS**: ["test_solve_poly_system"]

**Tests that should PASS→PASS**: ["test_solve_biquadratic", "test_solve_triangulated"]

**Base Commit**: 2c83657ff1c62fc2761b639469fdac7f7561a72a
**Environment Setup Commit**: f9a6f50ec0c74d935c50a6e9c9b2cb0469570d91
