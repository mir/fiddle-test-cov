# sympy__sympy-21055

**Repository**: sympy/sympy
**Created**: 2021-03-07T21:08:36Z
**Version**: 1.8

## Problem Statement

`refine()` does not understand how to simplify complex arguments
Just learned about the refine-function, which would come in handy frequently for me.  But
`refine()` does not recognize that argument functions simplify for real numbers.

```
>>> from sympy import *                                                     
>>> var('a,x')                                                              
>>> J = Integral(sin(x)*exp(-a*x),(x,0,oo))                                     
>>> J.doit()
	Piecewise((1/(a**2 + 1), 2*Abs(arg(a)) < pi), (Integral(exp(-a*x)*sin(x), (x, 0, oo)), True))
>>> refine(J.doit(),Q.positive(a))                                                 
        Piecewise((1/(a**2 + 1), 2*Abs(arg(a)) < pi), (Integral(exp(-a*x)*sin(x), (x, 0, oo)), True))
>>> refine(abs(a),Q.positive(a))                                            
	a
>>> refine(arg(a),Q.positive(a))                                            
	arg(a)
```
I cann't find any open issues identifying this.  Easy to fix, though.




## Patch

```diff

diff --git a/sympy/assumptions/refine.py b/sympy/assumptions/refine.py
--- a/sympy/assumptions/refine.py
+++ b/sympy/assumptions/refine.py
@@ -297,6 +297,28 @@ def refine_im(expr, assumptions):
         return - S.ImaginaryUnit * arg
     return _refine_reim(expr, assumptions)
 
+def refine_arg(expr, assumptions):
+    """
+    Handler for complex argument
+
+    Explanation
+    ===========
+
+    >>> from sympy.assumptions.refine import refine_arg
+    >>> from sympy import Q, arg
+    >>> from sympy.abc import x
+    >>> refine_arg(arg(x), Q.positive(x))
+    0
+    >>> refine_arg(arg(x), Q.negative(x))
+    pi
+    """
+    rg = expr.args[0]
+    if ask(Q.positive(rg), assumptions):
+        return S.Zero
+    if ask(Q.negative(rg), assumptions):
+        return S.Pi
+    return None
+
 
 def _refine_reim(expr, assumptions):
     # Helper function for refine_re & refine_im
@@ -379,6 +401,7 @@ def refine_matrixelement(expr, assumptions):
     'atan2': refine_atan2,
     're': refine_re,
     'im': refine_im,
+    'arg': refine_arg,
     'sign': refine_sign,
     'MatrixElement': refine_matrixelement
 }  # type: Dict[str, Callable[[Expr, Boolean], Expr]]


```

## Test Patch

```diff
diff --git a/sympy/assumptions/tests/test_refine.py b/sympy/assumptions/tests/test_refine.py
--- a/sympy/assumptions/tests/test_refine.py
+++ b/sympy/assumptions/tests/test_refine.py
@@ -1,5 +1,5 @@
 from sympy import (Abs, exp, Expr, I, pi, Q, Rational, refine, S, sqrt,
-                   atan, atan2, nan, Symbol, re, im, sign)
+                   atan, atan2, nan, Symbol, re, im, sign, arg)
 from sympy.abc import w, x, y, z
 from sympy.core.relational import Eq, Ne
 from sympy.functions.elementary.piecewise import Piecewise
@@ -160,6 +160,10 @@ def test_sign():
     x = Symbol('x', complex=True)
     assert refine(sign(x), Q.zero(x)) == 0
 
+def test_arg():
+    x = Symbol('x', complex = True)
+    assert refine(arg(x), Q.positive(x)) == 0
+    assert refine(arg(x), Q.negative(x)) == pi
 
 def test_func_args():
     class MyClass(Expr):

```

## Test Information

**Tests that should FAIL→PASS**: ["test_arg"]

**Tests that should PASS→PASS**: ["test_Abs", "test_pow1", "test_pow2", "test_exp", "test_Piecewise", "test_atan2", "test_re", "test_im", "test_complex", "test_sign", "test_func_args", "test_eval_refine", "test_refine_issue_12724"]

**Base Commit**: 748ce73479ee2cd5c861431091001cc18943c735
**Environment Setup Commit**: 3ac1464b8840d5f8b618a654f9fbf09c452fe969
