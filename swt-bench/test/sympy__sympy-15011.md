# sympy__sympy-15011

**Repository**: sympy/sympy
**Created**: 2018-08-02T12:54:02Z
**Version**: 1.2

## Problem Statement

lambdify does not work with certain MatrixSymbol names even with dummify=True
`lambdify` is happy with curly braces in a symbol name and with `MatrixSymbol`s, but not with both at the same time, even if `dummify` is `True`.

Here is some basic code that gives the error.
```
import sympy as sy
curlyx = sy.symbols("{x}")
v = sy.MatrixSymbol("v", 2, 1)
curlyv = sy.MatrixSymbol("{v}", 2, 1)
```

The following two lines of code work:
```
curlyScalarId = sy.lambdify(curlyx, curlyx)
vectorId = sy.lambdify(v,v)
```

The following two lines of code give a `SyntaxError`:
```
curlyVectorId = sy.lambdify(curlyv, curlyv)
curlyVectorIdDummified = sy.lambdify(curlyv, curlyv, dummify=True)
```




## Hints

The default here should be to always dummify, unless dummify is explicitly False https://github.com/sympy/sympy/blob/a78cf1d3efe853f1c360f962c5582b1d3d29ded3/sympy/utilities/lambdify.py?utf8=%E2%9C%93#L742
Hi, I would like to work on this if possible

## Patch

```diff

diff --git a/sympy/utilities/lambdify.py b/sympy/utilities/lambdify.py
--- a/sympy/utilities/lambdify.py
+++ b/sympy/utilities/lambdify.py
@@ -700,14 +700,13 @@ def _is_safe_ident(cls, ident):
             return isinstance(ident, str) and cls._safe_ident_re.match(ident) \
                 and not (keyword.iskeyword(ident) or ident == 'None')
 
-
     def _preprocess(self, args, expr):
         """Preprocess args, expr to replace arguments that do not map
         to valid Python identifiers.
 
         Returns string form of args, and updated expr.
         """
-        from sympy import Dummy, Symbol, Function, flatten
+        from sympy import Dummy, Symbol, MatrixSymbol, Function, flatten
         from sympy.matrices import DeferredVector
 
         dummify = self._dummify
@@ -725,7 +724,7 @@ def _preprocess(self, args, expr):
                 argstrs.append(nested_argstrs)
             elif isinstance(arg, DeferredVector):
                 argstrs.append(str(arg))
-            elif isinstance(arg, Symbol):
+            elif isinstance(arg, Symbol) or isinstance(arg, MatrixSymbol):
                 argrep = self._argrepr(arg)
 
                 if dummify or not self._is_safe_ident(argrep):
@@ -739,7 +738,14 @@ def _preprocess(self, args, expr):
                 argstrs.append(self._argrepr(dummy))
                 expr = self._subexpr(expr, {arg: dummy})
             else:
-                argstrs.append(str(arg))
+                argrep = self._argrepr(arg)
+
+                if dummify:
+                    dummy = Dummy()
+                    argstrs.append(self._argrepr(dummy))
+                    expr = self._subexpr(expr, {arg: dummy})
+                else:
+                    argstrs.append(str(arg))
 
         return argstrs, expr
 


```

## Test Patch

```diff
diff --git a/sympy/utilities/tests/test_lambdify.py b/sympy/utilities/tests/test_lambdify.py
--- a/sympy/utilities/tests/test_lambdify.py
+++ b/sympy/utilities/tests/test_lambdify.py
@@ -728,6 +728,14 @@ def test_dummification():
     raises(SyntaxError, lambda: lambdify(2 * F(t), 2 * F(t) + 5))
     raises(SyntaxError, lambda: lambdify(2 * F(t), 4 * F(t) + 5))
 
+def test_curly_matrix_symbol():
+    # Issue #15009
+    curlyv = sympy.MatrixSymbol("{v}", 2, 1)
+    lam = lambdify(curlyv, curlyv)
+    assert lam(1)==1
+    lam = lambdify(curlyv, curlyv, dummify=True)
+    assert lam(1)==1
+
 def test_python_keywords():
     # Test for issue 7452. The automatic dummification should ensure use of
     # Python reserved keywords as symbol names will create valid lambda

```

## Test Information

**Tests that should FAIL→PASS**: ["test_curly_matrix_symbol"]

**Tests that should PASS→PASS**: ["test_no_args", "test_single_arg", "test_list_args", "test_nested_args", "test_str_args", "test_own_namespace_1", "test_own_namespace_2", "test_own_module", "test_bad_args", "test_atoms", "test_sympy_lambda", "test_math_lambda", "test_mpmath_lambda", "test_number_precision", "test_mpmath_precision", "test_math_transl", "test_mpmath_transl", "test_exponentiation", "test_sqrt", "test_trig", "test_vector_simple", "test_vector_discontinuous", "test_trig_symbolic", "test_trig_float", "test_docs", "test_math", "test_sin", "test_matrix", "test_issue9474", "test_integral", "test_sym_single_arg", "test_sym_list_args", "test_sym_integral", "test_namespace_order", "test_namespace_type", "test_imps", "test_imps_errors", "test_imps_wrong_args", "test_lambdify_imps", "test_dummification", "test_python_keywords", "test_lambdify_docstring", "test_special_printers", "test_true_false", "test_issue_2790", "test_issue_12092", "test_ITE", "test_Min_Max", "test_issue_12173", "test_sinc_mpmath", "test_lambdify_dummy_arg", "test_lambdify_mixed_symbol_dummy_args", "test_lambdify_inspect"]

**Base Commit**: b7c5ba2bf3ffd5cf453b25af7c8ddd9a639800cb
**Environment Setup Commit**: e53e809176de9aa0fb62e85689f8cdb669d4cacb
