# sympy__sympy-21614

**Repository**: sympy/sympy
**Created**: 2021-06-14T07:56:59Z
**Version**: 1.9

## Problem Statement

Wrong Derivative kind attribute
I'm playing around with the `kind` attribute.

The following is correct:

```
from sympy import Integral, Derivative
from sympy import MatrixSymbol
from sympy.abc import x
A = MatrixSymbol('A', 2, 2)
i = Integral(A, x)
i.kind
# MatrixKind(NumberKind)
```

This one is wrong:
```
d = Derivative(A, x)
d.kind
# UndefinedKind
```


## Hints

As I dig deeper into this issue, the problem is much larger than `Derivative`. As a matter of facts, all functions should be able to deal with `kind`. At the moment:

```
from sympy import MatrixSymbol
A = MatrixSymbol('A', 2, 2)
sin(A).kind
# UndefinedKind
```
The kind attribute is new and is not fully implemented or used across the codebase.

For `sin` and other functions I don't think that we should allow the ordinary `sin` function to be used for the Matrix sin. There should be a separate `MatrixSin` function for that.

For Derivative the handler for kind just needs to be added.

## Patch

```diff

diff --git a/sympy/core/function.py b/sympy/core/function.py
--- a/sympy/core/function.py
+++ b/sympy/core/function.py
@@ -1707,6 +1707,10 @@ def free_symbols(self):
             ret.update(count.free_symbols)
         return ret
 
+    @property
+    def kind(self):
+        return self.args[0].kind
+
     def _eval_subs(self, old, new):
         # The substitution (old, new) cannot be done inside
         # Derivative(expr, vars) for a variety of reasons


```

## Test Patch

```diff
diff --git a/sympy/core/tests/test_kind.py b/sympy/core/tests/test_kind.py
--- a/sympy/core/tests/test_kind.py
+++ b/sympy/core/tests/test_kind.py
@@ -5,6 +5,7 @@
 from sympy.core.singleton import S
 from sympy.core.symbol import Symbol
 from sympy.integrals.integrals import Integral
+from sympy.core.function import Derivative
 from sympy.matrices import (Matrix, SparseMatrix, ImmutableMatrix,
     ImmutableSparseMatrix, MatrixSymbol, MatrixKind, MatMul)
 
@@ -39,6 +40,11 @@ def test_Integral_kind():
     assert Integral(comm_x, comm_x).kind is NumberKind
     assert Integral(A, comm_x).kind is MatrixKind(NumberKind)
 
+def test_Derivative_kind():
+    A = MatrixSymbol('A', 2,2)
+    assert Derivative(comm_x, comm_x).kind is NumberKind
+    assert Derivative(A, comm_x).kind is MatrixKind(NumberKind)
+
 def test_Matrix_kind():
     classes = (Matrix, SparseMatrix, ImmutableMatrix, ImmutableSparseMatrix)
     for cls in classes:

```

## Test Information

**Tests that should FAIL→PASS**: ["test_Derivative_kind"]

**Tests that should PASS→PASS**: ["test_NumberKind", "test_Add_kind", "test_mul_kind", "test_Symbol_kind", "test_Integral_kind", "test_Matrix_kind"]

**Base Commit**: b4777fdcef467b7132c055f8ac2c9a5059e6a145
**Environment Setup Commit**: f9a6f50ec0c74d935c50a6e9c9b2cb0469570d91
