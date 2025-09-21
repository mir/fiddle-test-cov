# sympy__sympy-11400

**Repository**: sympy/sympy
**Created**: 2016-07-15T21:40:49Z
**Version**: 1.0

## Problem Statement

ccode(sinc(x)) doesn't work
```
In [30]: ccode(sinc(x))
Out[30]: '// Not supported in C:\n// sinc\nsinc(x)'
```

I don't think `math.h` has `sinc`, but it could print

```
In [38]: ccode(Piecewise((sin(theta)/theta, Ne(theta, 0)), (1, True)))
Out[38]: '((Ne(theta, 0)) ? (\n   sin(theta)/theta\n)\n: (\n   1\n))'
```



## Hints

@asmeurer I would like to fix this issue. Should I work upon  the codegen.py file ? If there's something else tell me how to start ?

The relevant file is sympy/printing/ccode.py

@asmeurer I am new here. I would like to work on this issue. Please tell me how to start?

Since there are two people asking, maybe one person can try #11286 which is very similar, maybe even easier.


## Patch

```diff

diff --git a/sympy/printing/ccode.py b/sympy/printing/ccode.py
--- a/sympy/printing/ccode.py
+++ b/sympy/printing/ccode.py
@@ -231,6 +231,20 @@ def _print_Symbol(self, expr):
         else:
             return name
 
+    def _print_Relational(self, expr):
+        lhs_code = self._print(expr.lhs)
+        rhs_code = self._print(expr.rhs)
+        op = expr.rel_op
+        return ("{0} {1} {2}").format(lhs_code, op, rhs_code)
+
+    def _print_sinc(self, expr):
+        from sympy.functions.elementary.trigonometric import sin
+        from sympy.core.relational import Ne
+        from sympy.functions import Piecewise
+        _piecewise = Piecewise(
+            (sin(expr.args[0]) / expr.args[0], Ne(expr.args[0], 0)), (1, True))
+        return self._print(_piecewise)
+
     def _print_AugmentedAssignment(self, expr):
         lhs_code = self._print(expr.lhs)
         op = expr.rel_op


```

## Test Patch

```diff
diff --git a/sympy/printing/tests/test_ccode.py b/sympy/printing/tests/test_ccode.py
--- a/sympy/printing/tests/test_ccode.py
+++ b/sympy/printing/tests/test_ccode.py
@@ -120,6 +120,16 @@ def test_ccode_boolean():
     assert ccode((x | y) & z) == "z && (x || y)"
 
 
+def test_ccode_Relational():
+    from sympy import Eq, Ne, Le, Lt, Gt, Ge
+    assert ccode(Eq(x, y)) == "x == y"
+    assert ccode(Ne(x, y)) == "x != y"
+    assert ccode(Le(x, y)) == "x <= y"
+    assert ccode(Lt(x, y)) == "x < y"
+    assert ccode(Gt(x, y)) == "x > y"
+    assert ccode(Ge(x, y)) == "x >= y"
+
+
 def test_ccode_Piecewise():
     expr = Piecewise((x, x < 1), (x**2, True))
     assert ccode(expr) == (
@@ -162,6 +172,18 @@ def test_ccode_Piecewise():
     raises(ValueError, lambda: ccode(expr))
 
 
+def test_ccode_sinc():
+    from sympy import sinc
+    expr = sinc(x)
+    assert ccode(expr) == (
+            "((x != 0) ? (\n"
+            "   sin(x)/x\n"
+            ")\n"
+            ": (\n"
+            "   1\n"
+            "))")
+
+
 def test_ccode_Piecewise_deep():
     p = ccode(2*Piecewise((x, x < 1), (x + 1, x < 2), (x**2, True)))
     assert p == (

```

## Test Information

**Tests that should FAIL→PASS**: ["test_ccode_Relational", "test_ccode_sinc"]

**Tests that should PASS→PASS**: ["test_printmethod", "test_ccode_sqrt", "test_ccode_Pow", "test_ccode_constants_mathh", "test_ccode_constants_other", "test_ccode_Rational", "test_ccode_Integer", "test_ccode_functions", "test_ccode_inline_function", "test_ccode_exceptions", "test_ccode_user_functions", "test_ccode_boolean", "test_ccode_Piecewise", "test_ccode_Piecewise_deep", "test_ccode_ITE", "test_ccode_settings", "test_ccode_Indexed", "test_ccode_Indexed_without_looking_for_contraction", "test_ccode_loops_matrix_vector", "test_dummy_loops", "test_ccode_loops_add", "test_ccode_loops_multiple_contractions", "test_ccode_loops_addfactor", "test_ccode_loops_multiple_terms", "test_dereference_printing", "test_Matrix_printing", "test_ccode_reserved_words", "test_ccode_sign", "test_ccode_Assignment"]

**Base Commit**: 8dcb12a6cf500e8738d6729ab954a261758f49ca
**Environment Setup Commit**: 50b81f9f6be151014501ffac44e5dc6b2416938f
