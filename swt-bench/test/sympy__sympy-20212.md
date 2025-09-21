# sympy__sympy-20212

**Repository**: sympy/sympy
**Created**: 2020-10-06T11:34:13Z
**Version**: 1.7

## Problem Statement

0**-oo produces 0, the documentation says it should produce zoo
Using SymPy 1.5.1, evaluate `0**-oo` produces `0`.

The documentation for the Pow class states that it should return `ComplexInfinity`, aka `zoo`

| expr | value | reason |
| :-- | :-- | :--|
| `0**-oo` | `zoo` | This is not strictly true, as 0**oo may be oscillating between positive and negative values or rotating in the complex plane. It is convenient, however, when the base is positive.|



## Patch

```diff

diff --git a/sympy/core/power.py b/sympy/core/power.py
--- a/sympy/core/power.py
+++ b/sympy/core/power.py
@@ -291,6 +291,8 @@ def __new__(cls, b, e, evaluate=None):
             ).warn()
 
         if evaluate:
+            if b is S.Zero and e is S.NegativeInfinity:
+                return S.ComplexInfinity
             if e is S.ComplexInfinity:
                 return S.NaN
             if e is S.Zero:


```

## Test Patch

```diff
diff --git a/sympy/core/tests/test_power.py b/sympy/core/tests/test_power.py
--- a/sympy/core/tests/test_power.py
+++ b/sympy/core/tests/test_power.py
@@ -266,6 +266,9 @@ def test_zero():
     assert 0**(2*x*y) == 0**(x*y)
     assert 0**(-2*x*y) == S.ComplexInfinity**(x*y)
 
+    #Test issue 19572
+    assert 0 ** -oo is zoo
+    assert power(0, -oo) is zoo
 
 def test_pow_as_base_exp():
     x = Symbol('x')

```

## Test Information

**Tests that should FAIL→PASS**: ["test_zero"]

**Tests that should PASS→PASS**: ["test_rational", "test_large_rational", "test_negative_real", "test_expand", "test_issue_3449", "test_issue_3866", "test_negative_one", "test_issue_4362", "test_Pow_Expr_args", "test_Pow_signs", "test_power_with_noncommutative_mul_as_base", "test_power_rewrite_exp", "test_pow_as_base_exp", "test_nseries", "test_issue_6100_12942_4473", "test_issue_6208", "test_issue_6990", "test_issue_6068", "test_issue_6782", "test_issue_6653", "test_issue_6429", "test_issue_7638", "test_issue_8582", "test_issue_8650", "test_issue_13914", "test_better_sqrt", "test_issue_2993", "test_issue_17450", "test_issue_18190", "test_issue_14815", "test_issue_18509", "test_issue_18762"]

**Base Commit**: a106f4782a9dbe7f8fd16030f15401d977e03ae9
**Environment Setup Commit**: cffd4e0f86fefd4802349a9f9b19ed70934ea354
