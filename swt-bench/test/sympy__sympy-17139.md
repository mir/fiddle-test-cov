# sympy__sympy-17139

**Repository**: sympy/sympy
**Created**: 2019-07-01T19:17:18Z
**Version**: 1.5

## Problem Statement

simplify(cos(x)**I): Invalid comparison of complex I (fu.py)
```
>>> from sympy import *
>>> x = Symbol('x')
>>> print(simplify(cos(x)**I))
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/e/se/sympy/simplify/simplify.py", line 587, in simplify
    expr = trigsimp(expr, deep=True)
  File "/home/e/se/sympy/simplify/trigsimp.py", line 508, in trigsimp
    return trigsimpfunc(expr)
  File "/home/e/se/sympy/simplify/trigsimp.py", line 501, in <lambda>
    'matching': (lambda x: futrig(x)),
  File "/home/e/se/sympy/simplify/trigsimp.py", line 1101, in futrig
    e = bottom_up(e, lambda x: _futrig(x, **kwargs))
  File "/home/e/se/sympy/simplify/simplify.py", line 1081, in bottom_up
    rv = F(rv)
  File "/home/e/se/sympy/simplify/trigsimp.py", line 1101, in <lambda>
    e = bottom_up(e, lambda x: _futrig(x, **kwargs))
  File "/home/e/se/sympy/simplify/trigsimp.py", line 1169, in _futrig
    e = greedy(tree, objective=Lops)(e)
  File "/home/e/se/sympy/strategies/core.py", line 115, in minrule
    return min([rule(expr) for rule in rules], key=objective)
  File "/home/e/se/sympy/strategies/core.py", line 115, in <listcomp>
    return min([rule(expr) for rule in rules], key=objective)
  File "/home/e/se/sympy/strategies/core.py", line 44, in chain_rl
    expr = rule(expr)
  File "/home/e/se/sympy/simplify/fu.py", line 566, in TR6
    return _TR56(rv, cos, sin, lambda x: 1 - x, max=max, pow=pow)
  File "/home/e/se/sympy/simplify/fu.py", line 524, in _TR56
    return bottom_up(rv, _f)
  File "/home/e/se/sympy/simplify/simplify.py", line 1081, in bottom_up
    rv = F(rv)
  File "/home/e/se/sympy/simplify/fu.py", line 504, in _f
    if (rv.exp < 0) == True:
  File "/home/e/se/sympy/core/expr.py", line 406, in __lt__
    raise TypeError("Invalid comparison of complex %s" % me)
TypeError: Invalid comparison of complex I
```


## Patch

```diff

diff --git a/sympy/simplify/fu.py b/sympy/simplify/fu.py
--- a/sympy/simplify/fu.py
+++ b/sympy/simplify/fu.py
@@ -500,6 +500,8 @@ def _f(rv):
         # change is not going to allow a simplification as far as I can tell.
         if not (rv.is_Pow and rv.base.func == f):
             return rv
+        if not rv.exp.is_real:
+            return rv
 
         if (rv.exp < 0) == True:
             return rv


```

## Test Patch

```diff
diff --git a/sympy/simplify/tests/test_fu.py b/sympy/simplify/tests/test_fu.py
--- a/sympy/simplify/tests/test_fu.py
+++ b/sympy/simplify/tests/test_fu.py
@@ -76,6 +76,10 @@ def test__TR56():
     assert T(sin(x)**6, sin, cos, h, 6, True) == sin(x)**6
     assert T(sin(x)**8, sin, cos, h, 10, True) == (-cos(x)**2 + 1)**4
 
+    # issue 17137
+    assert T(sin(x)**I, sin, cos, h, 4, True) == sin(x)**I
+    assert T(sin(x)**(2*I + 1), sin, cos, h, 4, True) == sin(x)**(2*I + 1)
+
 
 def test_TR5():
     assert TR5(sin(x)**2) == -cos(x)**2 + 1
diff --git a/sympy/simplify/tests/test_simplify.py b/sympy/simplify/tests/test_simplify.py
--- a/sympy/simplify/tests/test_simplify.py
+++ b/sympy/simplify/tests/test_simplify.py
@@ -811,6 +811,11 @@ def test_issue_15965():
     assert simplify(B) == bnew
 
 
+def test_issue_17137():
+    assert simplify(cos(x)**I) == cos(x)**I
+    assert simplify(cos(x)**(2 + 3*I)) == cos(x)**(2 + 3*I)
+
+
 def test_issue_7971():
     z = Integral(x, (x, 1, 1))
     assert z != 0

```

## Test Information

**Tests that should FAIL→PASS**: ["test__TR56", "test_issue_17137"]

**Tests that should PASS→PASS**: ["test_TR1", "test_TR2", "test_TR2i", "test_TR3", "test_TR5", "test_TR6", "test_TR7", "test_TR8", "test_TR9", "test_TR10", "test_TR10i", "test_TR11", "test_TR12", "test_TR13", "test_L", "test_fu", "test_objective", "test_process_common_addends", "test_trig_split", "test_TRmorrie", "test_TRpower", "test_hyper_as_trig", "test_TR12i", "test_TR14", "test_TR15_16_17", "test_issue_7263", "test_simplify_expr", "test_issue_3557", "test_simplify_other", "test_simplify_complex", "test_simplify_ratio", "test_simplify_measure", "test_simplify_rational", "test_simplify_issue_1308", "test_issue_5652", "test_simplify_fail1", "test_nthroot", "test_nthroot1", "test_separatevars", "test_separatevars_advanced_factor", "test_hypersimp", "test_nsimplify", "test_issue_9448", "test_extract_minus_sign", "test_diff", "test_logcombine_1", "test_logcombine_complex_coeff", "test_issue_5950", "test_posify", "test_issue_4194", "test_as_content_primitive", "test_signsimp", "test_besselsimp", "test_Piecewise", "test_polymorphism", "test_issue_from_PR1599", "test_issue_6811", "test_issue_6920", "test_issue_7001", "test_inequality_no_auto_simplify", "test_issue_9398", "test_issue_9324_simplify", "test_issue_13474", "test_simplify_function_inverse", "test_clear_coefficients", "test_nc_simplify", "test_issue_15965"]

**Base Commit**: 1d3327b8e90a186df6972991963a5ae87053259d
**Environment Setup Commit**: 70381f282f2d9d039da860e391fe51649df2779d
