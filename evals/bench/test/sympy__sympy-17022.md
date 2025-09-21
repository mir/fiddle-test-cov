# sympy__sympy-17022

**Repository**: sympy/sympy
**Created**: 2019-06-12T21:54:57Z
**Version**: 1.5

## Problem Statement

Lambdify misinterprets some matrix expressions
Using lambdify on an expression containing an identity matrix gives us an unexpected result:

```python
>>> import numpy as np
>>> n = symbols('n', integer=True)
>>> A = MatrixSymbol("A", n, n)
>>> a = np.array([[1, 2], [3, 4]])
>>> f = lambdify(A, A + Identity(n))
>>> f(a)
array([[1.+1.j, 2.+1.j],
       [3.+1.j, 4.+1.j]])
```

Instead, the output should be  `array([[2, 2], [3, 5]])`, since we're adding an identity matrix to the array. Inspecting the globals and source code of `f` shows us why we get the result:

```python
>>> import inspect
>>> print(inspect.getsource(f))
def _lambdifygenerated(A):
    return (I + A)
>>> f.__globals__['I']
1j
```

The code printer prints `I`, which is currently being interpreted as a Python built-in complex number. The printer should support printing identity matrices, and signal an error for unsupported expressions that might be misinterpreted.


## Hints

If the shape is an explicit number, we can just print `eye(n)`. For unknown shape, it's harder. We can raise an exception for now. It's better to raise an exception than give a wrong answer. 

## Patch

```diff

diff --git a/sympy/printing/pycode.py b/sympy/printing/pycode.py
--- a/sympy/printing/pycode.py
+++ b/sympy/printing/pycode.py
@@ -608,6 +608,13 @@ def _print_MatrixBase(self, expr):
             func = self._module_format('numpy.array')
         return "%s(%s)" % (func, self._print(expr.tolist()))
 
+    def _print_Identity(self, expr):
+        shape = expr.shape
+        if all([dim.is_Integer for dim in shape]):
+            return "%s(%s)" % (self._module_format('numpy.eye'), self._print(expr.shape[0]))
+        else:
+            raise NotImplementedError("Symbolic matrix dimensions are not yet supported for identity matrices")
+
     def _print_BlockMatrix(self, expr):
         return '{0}({1})'.format(self._module_format('numpy.block'),
                                  self._print(expr.args[0].tolist()))


```

## Test Patch

```diff
diff --git a/sympy/printing/tests/test_numpy.py b/sympy/printing/tests/test_numpy.py
--- a/sympy/printing/tests/test_numpy.py
+++ b/sympy/printing/tests/test_numpy.py
@@ -1,6 +1,6 @@
 from sympy import (
     Piecewise, lambdify, Equality, Unequality, Sum, Mod, cbrt, sqrt,
-    MatrixSymbol, BlockMatrix
+    MatrixSymbol, BlockMatrix, Identity
 )
 from sympy import eye
 from sympy.abc import x, i, j, a, b, c, d
@@ -11,7 +11,7 @@
 from sympy.printing.lambdarepr import NumPyPrinter
 
 from sympy.utilities.pytest import warns_deprecated_sympy
-from sympy.utilities.pytest import skip
+from sympy.utilities.pytest import skip, raises
 from sympy.external import import_module
 
 np = import_module('numpy')
@@ -252,3 +252,21 @@ def test_16857():
 
     printer = NumPyPrinter()
     assert printer.doprint(A) == 'numpy.block([[a_1, a_2], [a_3, a_4]])'
+
+
+def test_issue_17006():
+    if not np:
+        skip("NumPy not installed")
+
+    M = MatrixSymbol("M", 2, 2)
+
+    f = lambdify(M, M + Identity(2))
+    ma = np.array([[1, 2], [3, 4]])
+    mr = np.array([[2, 2], [3, 5]])
+
+    assert (f(ma) == mr).all()
+
+    from sympy import symbols
+    n = symbols('n', integer=True)
+    N = MatrixSymbol("M", n, n)
+    raises(NotImplementedError, lambda: lambdify(N, N + Identity(n)))
diff --git a/sympy/printing/tests/test_pycode.py b/sympy/printing/tests/test_pycode.py
--- a/sympy/printing/tests/test_pycode.py
+++ b/sympy/printing/tests/test_pycode.py
@@ -7,7 +7,7 @@
 from sympy.core.numbers import pi
 from sympy.functions import acos, Piecewise, sign
 from sympy.logic import And, Or
-from sympy.matrices import SparseMatrix, MatrixSymbol
+from sympy.matrices import SparseMatrix, MatrixSymbol, Identity
 from sympy.printing.pycode import (
     MpmathPrinter, NumPyPrinter, PythonCodePrinter, pycode, SciPyPrinter
 )
@@ -49,6 +49,7 @@ def test_NumPyPrinter():
     A = MatrixSymbol("A", 2, 2)
     assert p.doprint(A**(-1)) == "numpy.linalg.inv(A)"
     assert p.doprint(A**5) == "numpy.linalg.matrix_power(A, 5)"
+    assert p.doprint(Identity(3)) == "numpy.eye(3)"
 
 
 def test_SciPyPrinter():

```

## Test Information

**Tests that should FAIL→PASS**: ["test_NumPyPrinter"]

**Tests that should PASS→PASS**: ["test_numpy_piecewise_regression", "test_PythonCodePrinter", "test_MpmathPrinter", "test_SciPyPrinter", "test_pycode_reserved_words", "test_printmethod", "test_codegen_ast_nodes", "test_issue_14283"]

**Base Commit**: f91de695585c1fbc7d4f49ee061f64fcb1c2c4d8
**Environment Setup Commit**: 70381f282f2d9d039da860e391fe51649df2779d
