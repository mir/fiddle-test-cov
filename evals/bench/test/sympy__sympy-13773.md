# sympy__sympy-13773

**Repository**: sympy/sympy
**Created**: 2017-12-19T10:44:38Z
**Version**: 1.1

## Problem Statement

@ (__matmul__) should fail if one argument is not a matrix
```
>>> A = Matrix([[1, 2], [3, 4]])
>>> B = Matrix([[2, 3], [1, 2]])
>>> A@B
Matrix([
[ 4,  7],
[10, 17]])
>>> 2@B
Matrix([
[4, 6],
[2, 4]])
```

Right now `@` (`__matmul__`) just copies `__mul__`, but it should actually only work if the multiplication is actually a matrix multiplication. 

This is also how NumPy works

```
>>> import numpy as np
>>> a = np.array([[1, 2], [3, 4]])
>>> 2*a
array([[2, 4],
       [6, 8]])
>>> 2@a
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ValueError: Scalar operands are not allowed, use '*' instead
```


## Hints

Note to anyone fixing this: `@`/`__matmul__` only works in Python 3.5+. 
I would like to work on this issue.

## Patch

```diff

diff --git a/sympy/matrices/common.py b/sympy/matrices/common.py
--- a/sympy/matrices/common.py
+++ b/sympy/matrices/common.py
@@ -1973,6 +1973,10 @@ def __div__(self, other):
 
     @call_highest_priority('__rmatmul__')
     def __matmul__(self, other):
+        other = _matrixify(other)
+        if not getattr(other, 'is_Matrix', False) and not getattr(other, 'is_MatrixLike', False):
+            return NotImplemented
+
         return self.__mul__(other)
 
     @call_highest_priority('__rmul__')
@@ -2066,6 +2070,10 @@ def __radd__(self, other):
 
     @call_highest_priority('__matmul__')
     def __rmatmul__(self, other):
+        other = _matrixify(other)
+        if not getattr(other, 'is_Matrix', False) and not getattr(other, 'is_MatrixLike', False):
+            return NotImplemented
+
         return self.__rmul__(other)
 
     @call_highest_priority('__mul__')


```

## Test Patch

```diff
diff --git a/sympy/matrices/tests/test_commonmatrix.py b/sympy/matrices/tests/test_commonmatrix.py
--- a/sympy/matrices/tests/test_commonmatrix.py
+++ b/sympy/matrices/tests/test_commonmatrix.py
@@ -674,6 +674,30 @@ def test_multiplication():
         assert c[1, 0] == 3*5
         assert c[1, 1] == 0
 
+def test_matmul():
+    a = Matrix([[1, 2], [3, 4]])
+
+    assert a.__matmul__(2) == NotImplemented
+
+    assert a.__rmatmul__(2) == NotImplemented
+
+    #This is done this way because @ is only supported in Python 3.5+
+    #To check 2@a case
+    try:
+        eval('2 @ a')
+    except SyntaxError:
+        pass
+    except TypeError:  #TypeError is raised in case of NotImplemented is returned
+        pass
+
+    #Check a@2 case
+    try:
+        eval('a @ 2')
+    except SyntaxError:
+        pass
+    except TypeError:  #TypeError is raised in case of NotImplemented is returned
+        pass
+
 def test_power():
     raises(NonSquareMatrixError, lambda: Matrix((1, 2))**2)
 

```

## Test Information

**Tests that should FAIL→PASS**: ["test_matmul"]

**Tests that should PASS→PASS**: ["test__MinimalMatrix", "test_vec", "test_tolist", "test_row_col_del", "test_get_diag_blocks1", "test_get_diag_blocks2", "test_shape", "test_reshape", "test_row_col", "test_row_join", "test_col_join", "test_row_insert", "test_col_insert", "test_extract", "test_hstack", "test_vstack", "test_atoms", "test_free_symbols", "test_has", "test_is_anti_symmetric", "test_diagonal_symmetrical", "test_is_hermitian", "test_is_Identity", "test_is_symbolic", "test_is_upper", "test_is_lower", "test_is_square", "test_is_symmetric", "test_is_hessenberg", "test_is_zero", "test_values", "test_adjoint", "test_as_real_imag", "test_conjugate", "test_doit", "test_evalf", "test_expand", "test_replace", "test_replace_map", "test_simplify", "test_subs", "test_trace", "test_xreplace", "test_permute", "test_abs", "test_add", "test_power", "test_neg", "test_sub", "test_det", "test_adjugate", "test_cofactor_and_minors", "test_charpoly", "test_row_op", "test_col_op", "test_is_echelon", "test_echelon_form", "test_rref", "test_eye", "test_ones", "test_zeros", "test_diag", "test_jordan_block", "test_columnspace", "test_rowspace", "test_nullspace", "test_eigenvals", "test_singular_values", "test_integrate"]

**Base Commit**: 7121bdf1facdd90d05b6994b4c2e5b2865a4638a
**Environment Setup Commit**: ec9e3c0436fbff934fa84e22bf07f1b3ef5bfac3
