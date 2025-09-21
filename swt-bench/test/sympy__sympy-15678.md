# sympy__sympy-15678

**Repository**: sympy/sympy
**Created**: 2018-12-20T18:11:56Z
**Version**: 1.4

## Problem Statement

Some issues with idiff
idiff doesn't support Eq, and it also doesn't support f(x) instead of y. Both should be easy to correct.

```
>>> idiff(Eq(y*exp(y), x*exp(x)), y, x)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "./sympy/geometry/util.py", line 582, in idiff
    yp = solve(eq.diff(x), dydx)[0].subs(derivs)
IndexError: list index out of range
>>> idiff(f(x)*exp(f(x)) - x*exp(x), f(x), x)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "./sympy/geometry/util.py", line 574, in idiff
    raise ValueError("expecting x-dependent symbol(s) but got: %s" % y)
ValueError: expecting x-dependent symbol(s) but got: f(x)
>>> idiff(y*exp(y)- x*exp(x), y, x)
(x + 1)*exp(x - y)/(y + 1)
```


## Hints

Hi i am a beginner and i would like to work on this issue.
@krishna-akula are you still working on this?... I'd like to work on it too

## Patch

```diff

diff --git a/sympy/geometry/util.py b/sympy/geometry/util.py
--- a/sympy/geometry/util.py
+++ b/sympy/geometry/util.py
@@ -570,12 +570,19 @@ def idiff(eq, y, x, n=1):
         y = y[0]
     elif isinstance(y, Symbol):
         dep = {y}
+    elif isinstance(y, Function):
+        pass
     else:
-        raise ValueError("expecting x-dependent symbol(s) but got: %s" % y)
+        raise ValueError("expecting x-dependent symbol(s) or function(s) but got: %s" % y)
 
     f = dict([(s, Function(
         s.name)(x)) for s in eq.free_symbols if s != x and s in dep])
-    dydx = Function(y.name)(x).diff(x)
+
+    if isinstance(y, Symbol):
+        dydx = Function(y.name)(x).diff(x)
+    else:
+        dydx = y.diff(x)
+
     eq = eq.subs(f)
     derivs = {}
     for i in range(n):


```

## Test Patch

```diff
diff --git a/sympy/geometry/tests/test_util.py b/sympy/geometry/tests/test_util.py
--- a/sympy/geometry/tests/test_util.py
+++ b/sympy/geometry/tests/test_util.py
@@ -1,5 +1,5 @@
-from sympy import Symbol, sqrt, Derivative, S
-from sympy.geometry import Point, Point2D, Line, Circle ,Polygon, Segment, convex_hull, intersection, centroid
+from sympy import Symbol, sqrt, Derivative, S, Function, exp
+from sympy.geometry import Point, Point2D, Line, Circle, Polygon, Segment, convex_hull, intersection, centroid
 from sympy.geometry.util import idiff, closest_points, farthest_points, _ordered_points
 from sympy.solvers.solvers import solve
 from sympy.utilities.pytest import raises
@@ -9,6 +9,8 @@ def test_idiff():
     x = Symbol('x', real=True)
     y = Symbol('y', real=True)
     t = Symbol('t', real=True)
+    f = Function('f')
+    g = Function('g')
     # the use of idiff in ellipse also provides coverage
     circ = x**2 + y**2 - 4
     ans = -3*x*(x**2 + y**2)/y**5
@@ -19,6 +21,10 @@ def test_idiff():
     assert ans.subs(y, solve(circ, y)[0]).equals(explicit)
     assert True in [sol.diff(x, 3).equals(explicit) for sol in solve(circ, y)]
     assert idiff(x + t + y, [y, t], x) == -Derivative(t, x) - 1
+    assert idiff(f(x) * exp(f(x)) - x * exp(x), f(x), x) == (x + 1) * exp(x - f(x))/(f(x) + 1)
+    assert idiff(f(x) - y * exp(x), [f(x), y], x) == (y + Derivative(y, x)) * exp(x)
+    assert idiff(f(x) - y * exp(x), [y, f(x)], x) == -y + exp(-x) * Derivative(f(x), x)
+    assert idiff(f(x) - g(x), [f(x), g(x)], x) == Derivative(g(x), x)
 
 
 def test_intersection():

```

## Test Information

**Tests that should FAIL→PASS**: ["test_idiff"]

**Tests that should PASS→PASS**: ["test_intersection", "test_convex_hull", "test_centroid"]

**Base Commit**: 31c68eef3ffef39e2e792b0ec92cd92b7010eb2a
**Environment Setup Commit**: 73b3f90093754c5ed1561bd885242330e3583004
