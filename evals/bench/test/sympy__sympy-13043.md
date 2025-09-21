# sympy__sympy-13043

**Repository**: sympy/sympy
**Created**: 2017-07-26T00:29:45Z
**Version**: 1.1

## Problem Statement

decompose() function in intpoly returns a list of arbitrary order
The decompose() function, with separate=True, returns `list(poly_dict.values())`, which is ordered arbitrarily.  

What is this used for? It should be sorted somehow, or returning a set (in which case, why not just use the returned dictionary and have the caller take the values). This is causing test failures for me after some changes to the core. 

CC @ArifAhmed1995 @certik 


## Patch

```diff

diff --git a/sympy/integrals/intpoly.py b/sympy/integrals/intpoly.py
--- a/sympy/integrals/intpoly.py
+++ b/sympy/integrals/intpoly.py
@@ -556,7 +556,7 @@ def decompose(expr, separate=False):
     >>> decompose(x**2 + x*y + x + y + x**3*y**2 + y**5)
     {1: x + y, 2: x**2 + x*y, 5: x**3*y**2 + y**5}
     >>> decompose(x**2 + x*y + x + y + x**3*y**2 + y**5, True)
-    [x, y, x**2, y**5, x*y, x**3*y**2]
+    {x, x**2, y, y**5, x*y, x**3*y**2}
     """
     expr = S(expr)
     poly_dict = {}
@@ -569,7 +569,7 @@ def decompose(expr, separate=False):
             degrees = [(sum(degree_list(monom, *symbols)), monom)
                        for monom in expr.args]
             if separate:
-                return [monom[1] for monom in degrees]
+                return {monom[1] for monom in degrees}
             else:
                 for monom in degrees:
                     degree, term = monom
@@ -593,7 +593,7 @@ def decompose(expr, separate=False):
         poly_dict[0] = expr
 
     if separate:
-        return list(poly_dict.values())
+        return set(poly_dict.values())
     return poly_dict
 
 


```

## Test Patch

```diff
diff --git a/sympy/integrals/tests/test_intpoly.py b/sympy/integrals/tests/test_intpoly.py
--- a/sympy/integrals/tests/test_intpoly.py
+++ b/sympy/integrals/tests/test_intpoly.py
@@ -26,15 +26,15 @@ def test_decompose():
     assert decompose(9*x**2 + y + 4*x + x**3 + y**2*x + 3) ==\
         {0: 3, 1: 4*x + y, 2: 9*x**2, 3: x**3 + x*y**2}
 
-    assert decompose(x, True) == [x]
-    assert decompose(x ** 2, True) == [x ** 2]
-    assert decompose(x * y, True) == [x * y]
-    assert decompose(x + y, True) == [x, y]
-    assert decompose(x ** 2 + y, True) == [y, x ** 2]
-    assert decompose(8 * x ** 2 + 4 * y + 7, True) == [7, 4*y, 8*x**2]
-    assert decompose(x ** 2 + 3 * y * x, True) == [x ** 2, 3 * x * y]
+    assert decompose(x, True) == {x}
+    assert decompose(x ** 2, True) == {x**2}
+    assert decompose(x * y, True) == {x * y}
+    assert decompose(x + y, True) == {x, y}
+    assert decompose(x ** 2 + y, True) == {y, x ** 2}
+    assert decompose(8 * x ** 2 + 4 * y + 7, True) == {7, 4*y, 8*x**2}
+    assert decompose(x ** 2 + 3 * y * x, True) == {x ** 2, 3 * x * y}
     assert decompose(9 * x ** 2 + y + 4 * x + x ** 3 + y ** 2 * x + 3, True) == \
-           [3, y, x**3, 4*x, 9*x**2, x*y**2]
+           {3, y, 4*x, 9*x**2, x*y**2, x**3}
 
 
 def test_best_origin():

```

## Test Information

**Tests that should FAIL→PASS**: ["test_decompose"]

**Tests that should PASS→PASS**: ["test_best_origin"]

**Base Commit**: a3389a25ec84d36f5cf04a4f2562d820f131db64
**Environment Setup Commit**: ec9e3c0436fbff934fa84e22bf07f1b3ef5bfac3
