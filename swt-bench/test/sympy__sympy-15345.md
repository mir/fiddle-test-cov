# sympy__sympy-15345

**Repository**: sympy/sympy
**Created**: 2018-10-05T06:00:31Z
**Version**: 1.4

## Problem Statement

mathematica_code gives wrong output with Max
If I run the code

```
x = symbols('x')
mathematica_code(Max(x,2))
```

then I would expect the output `'Max[x,2]'` which is valid Mathematica code but instead I get `'Max(2, x)'` which is not valid Mathematica code.


## Hints

Hi, I'm new (to the project and development in general, but I'm a long time Mathematica user) and have been looking into this problem.

The `mathematica.py` file goes thru a table of known functions (of which neither Mathematica `Max` or `Min` functions are in) that are specified with lowercase capitalization, so it might be that doing `mathematica_code(Max(x,2))` is just yielding the unevaluated expression of `mathematica_code`. But there is a problem when I do `mathematica_code(max(x,2))` I get an error occurring in the Relational class in `core/relational.py`

Still checking it out, though.
`max` (lowercase `m`) is the Python builtin which tries to compare the items directly and give a result. Since `x` and `2` cannot be compared, you get an error. `Max` is the SymPy version that can return unevaluated results. 

## Patch

```diff

diff --git a/sympy/printing/mathematica.py b/sympy/printing/mathematica.py
--- a/sympy/printing/mathematica.py
+++ b/sympy/printing/mathematica.py
@@ -31,7 +31,8 @@
     "asech": [(lambda x: True, "ArcSech")],
     "acsch": [(lambda x: True, "ArcCsch")],
     "conjugate": [(lambda x: True, "Conjugate")],
-
+    "Max": [(lambda *x: True, "Max")],
+    "Min": [(lambda *x: True, "Min")],
 }
 
 
@@ -101,6 +102,8 @@ def _print_Function(self, expr):
                     return "%s[%s]" % (mfunc, self.stringify(expr.args, ", "))
         return expr.func.__name__ + "[%s]" % self.stringify(expr.args, ", ")
 
+    _print_MinMaxBase = _print_Function
+
     def _print_Integral(self, expr):
         if len(expr.variables) == 1 and not expr.limits[0][1:]:
             args = [expr.args[0], expr.variables[0]]


```

## Test Patch

```diff
diff --git a/sympy/printing/tests/test_mathematica.py b/sympy/printing/tests/test_mathematica.py
--- a/sympy/printing/tests/test_mathematica.py
+++ b/sympy/printing/tests/test_mathematica.py
@@ -2,7 +2,7 @@
                         Rational, Integer, Tuple, Derivative)
 from sympy.integrals import Integral
 from sympy.concrete import Sum
-from sympy.functions import exp, sin, cos, conjugate
+from sympy.functions import exp, sin, cos, conjugate, Max, Min
 
 from sympy import mathematica_code as mcode
 
@@ -28,6 +28,7 @@ def test_Function():
     assert mcode(f(x, y, z)) == "f[x, y, z]"
     assert mcode(sin(x) ** cos(x)) == "Sin[x]^Cos[x]"
     assert mcode(conjugate(x)) == "Conjugate[x]"
+    assert mcode(Max(x,y,z)*Min(y,z)) == "Max[x, y, z]*Min[y, z]"
 
 
 def test_Pow():

```

## Test Information

**Tests that should FAIL→PASS**: ["test_Function"]

**Tests that should PASS→PASS**: ["test_Integer", "test_Rational", "test_Pow", "test_Mul", "test_constants", "test_containers", "test_Integral", "test_Derivative"]

**Base Commit**: 9ef28fba5b4d6d0168237c9c005a550e6dc27d81
**Environment Setup Commit**: 73b3f90093754c5ed1561bd885242330e3583004
