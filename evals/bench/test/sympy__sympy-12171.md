# sympy__sympy-12171

**Repository**: sympy/sympy
**Created**: 2017-02-13T18:20:56Z
**Version**: 1.0

## Problem Statement

matematica code printer does not handle floats and derivatives correctly
In its current state the mathematica code printer does not handle Derivative(func(vars), deriver) 
e.g. Derivative(f(t), t) yields Derivative(f(t), t) instead of D[f[t],t]

Also floats with exponents are not handled correctly e.g. 1.0e-4 is not converted to 1.0*^-4

This has an easy fix by adding the following lines to MCodePrinter:


def _print_Derivative(self, expr):
        return "D[%s]" % (self.stringify(expr.args, ", "))

def _print_Float(self, expr):
        res =str(expr)
        return res.replace('e','*^') 





## Hints

I would like to work on this issue
So, should I add the lines in printing/mathematica.py ?
I've tested the above code by adding these methods to a class derived from MCodePrinter and I was able to export an ODE system straight to NDSolve in Mathematica.

So I guess simply adding them to MCodePrinter in in printing/mathematica.py would fix the issue

## Patch

```diff

diff --git a/sympy/printing/mathematica.py b/sympy/printing/mathematica.py
--- a/sympy/printing/mathematica.py
+++ b/sympy/printing/mathematica.py
@@ -109,6 +109,9 @@ def _print_Integral(self, expr):
     def _print_Sum(self, expr):
         return "Hold[Sum[" + ', '.join(self.doprint(a) for a in expr.args) + "]]"
 
+    def _print_Derivative(self, expr):
+        return "Hold[D[" + ', '.join(self.doprint(a) for a in expr.args) + "]]"
+
 
 def mathematica_code(expr, **settings):
     r"""Converts an expr to a string of the Wolfram Mathematica code


```

## Test Patch

```diff
diff --git a/sympy/printing/tests/test_mathematica.py b/sympy/printing/tests/test_mathematica.py
--- a/sympy/printing/tests/test_mathematica.py
+++ b/sympy/printing/tests/test_mathematica.py
@@ -1,5 +1,5 @@
 from sympy.core import (S, pi, oo, symbols, Function,
-                        Rational, Integer, Tuple)
+                        Rational, Integer, Tuple, Derivative)
 from sympy.integrals import Integral
 from sympy.concrete import Sum
 from sympy.functions import exp, sin, cos
@@ -74,6 +74,14 @@ def test_Integral():
         "{y, -Infinity, Infinity}]]"
 
 
+def test_Derivative():
+    assert mcode(Derivative(sin(x), x)) == "Hold[D[Sin[x], x]]"
+    assert mcode(Derivative(x, x)) == "Hold[D[x, x]]"
+    assert mcode(Derivative(sin(x)*y**4, x, 2)) == "Hold[D[y^4*Sin[x], x, x]]"
+    assert mcode(Derivative(sin(x)*y**4, x, y, x)) == "Hold[D[y^4*Sin[x], x, y, x]]"
+    assert mcode(Derivative(sin(x)*y**4, x, y, 3, x)) == "Hold[D[y^4*Sin[x], x, y, y, y, x]]"
+
+
 def test_Sum():
     assert mcode(Sum(sin(x), (x, 0, 10))) == "Hold[Sum[Sin[x], {x, 0, 10}]]"
     assert mcode(Sum(exp(-x**2 - y**2),

```

## Test Information

**Tests that should FAIL→PASS**: ["test_Derivative"]

**Tests that should PASS→PASS**: ["test_Integer", "test_Rational", "test_Function", "test_Pow", "test_Mul", "test_constants", "test_containers", "test_Integral"]

**Base Commit**: ca6ef27272be31c9dc3753ede9232c39df9a75d8
**Environment Setup Commit**: 50b81f9f6be151014501ffac44e5dc6b2416938f
