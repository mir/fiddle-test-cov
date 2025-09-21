# sympy__sympy-13647

**Repository**: sympy/sympy
**Created**: 2017-11-28T21:22:51Z
**Version**: 1.1

## Problem Statement

Matrix.col_insert() no longer seems to work correctly.
Example:

```
In [28]: import sympy as sm

In [29]: M = sm.eye(6)

In [30]: M
Out[30]: 
⎡1  0  0  0  0  0⎤
⎢                ⎥
⎢0  1  0  0  0  0⎥
⎢                ⎥
⎢0  0  1  0  0  0⎥
⎢                ⎥
⎢0  0  0  1  0  0⎥
⎢                ⎥
⎢0  0  0  0  1  0⎥
⎢                ⎥
⎣0  0  0  0  0  1⎦

In [31]: V = 2 * sm.ones(6, 2)

In [32]: V
Out[32]: 
⎡2  2⎤
⎢    ⎥
⎢2  2⎥
⎢    ⎥
⎢2  2⎥
⎢    ⎥
⎢2  2⎥
⎢    ⎥
⎢2  2⎥
⎢    ⎥
⎣2  2⎦

In [33]: M.col_insert(3, V)
Out[33]: 
⎡1  0  0  2  2  1  0  0⎤
⎢                      ⎥
⎢0  1  0  2  2  0  1  0⎥
⎢                      ⎥
⎢0  0  1  2  2  0  0  1⎥
⎢                      ⎥
⎢0  0  0  2  2  0  0  0⎥
⎢                      ⎥
⎢0  0  0  2  2  0  0  0⎥
⎢                      ⎥
⎣0  0  0  2  2  0  0  0⎦
In [34]: sm.__version__
Out[34]: '1.1.1'
```

The 3 x 3 identify matrix to the right of the columns of twos is shifted from the bottom three rows to the top three rows.

@siefkenj Do you think this has to do with your matrix refactor?


## Hints

It seems that `pos` shouldn't be [here](https://github.com/sympy/sympy/blob/master/sympy/matrices/common.py#L89).

## Patch

```diff

diff --git a/sympy/matrices/common.py b/sympy/matrices/common.py
--- a/sympy/matrices/common.py
+++ b/sympy/matrices/common.py
@@ -86,7 +86,7 @@ def entry(i, j):
                 return self[i, j]
             elif pos <= j < pos + other.cols:
                 return other[i, j - pos]
-            return self[i, j - pos - other.cols]
+            return self[i, j - other.cols]
 
         return self._new(self.rows, self.cols + other.cols,
                          lambda i, j: entry(i, j))


```

## Test Patch

```diff
diff --git a/sympy/matrices/tests/test_commonmatrix.py b/sympy/matrices/tests/test_commonmatrix.py
--- a/sympy/matrices/tests/test_commonmatrix.py
+++ b/sympy/matrices/tests/test_commonmatrix.py
@@ -200,6 +200,14 @@ def test_col_insert():
         l = [0, 0, 0]
         l.insert(i, 4)
         assert flatten(zeros_Shaping(3).col_insert(i, c4).row(0).tolist()) == l
+    # issue 13643
+    assert eye_Shaping(6).col_insert(3, Matrix([[2, 2], [2, 2], [2, 2], [2, 2], [2, 2], [2, 2]])) == \
+           Matrix([[1, 0, 0, 2, 2, 0, 0, 0],
+                   [0, 1, 0, 2, 2, 0, 0, 0],
+                   [0, 0, 1, 2, 2, 0, 0, 0],
+                   [0, 0, 0, 2, 2, 1, 0, 0],
+                   [0, 0, 0, 2, 2, 0, 1, 0],
+                   [0, 0, 0, 2, 2, 0, 0, 1]])
 
 def test_extract():
     m = ShapingOnlyMatrix(4, 3, lambda i, j: i*3 + j)

```

## Test Information

**Tests that should FAIL→PASS**: ["test_col_insert"]

**Tests that should PASS→PASS**: ["test__MinimalMatrix", "test_vec", "test_tolist", "test_row_col_del", "test_get_diag_blocks1", "test_get_diag_blocks2", "test_shape", "test_reshape", "test_row_col", "test_row_join", "test_col_join", "test_row_insert", "test_extract", "test_hstack", "test_vstack", "test_atoms", "test_free_symbols", "test_has", "test_is_anti_symmetric", "test_diagonal_symmetrical", "test_is_hermitian", "test_is_Identity", "test_is_symbolic", "test_is_upper", "test_is_lower", "test_is_square", "test_is_symmetric", "test_is_hessenberg", "test_is_zero", "test_values", "test_applyfunc", "test_adjoint", "test_as_real_imag", "test_conjugate", "test_doit", "test_evalf", "test_expand", "test_replace", "test_replace_map", "test_simplify", "test_subs", "test_trace", "test_xreplace", "test_permute", "test_abs", "test_add", "test_multiplication", "test_power", "test_neg", "test_sub", "test_div", "test_det", "test_adjugate", "test_cofactor_and_minors", "test_charpoly", "test_row_op", "test_col_op", "test_is_echelon", "test_echelon_form", "test_rref", "test_eye", "test_ones", "test_zeros", "test_diag", "test_jordan_block", "test_columnspace", "test_rowspace", "test_nullspace", "test_eigenvals", "test_eigenvects", "test_left_eigenvects", "test_diagonalize", "test_is_diagonalizable", "test_jordan_form", "test_singular_values", "test_integrate"]

**Base Commit**: 67e3c956083d0128a621f65ee86a7dacd4f9f19f
**Environment Setup Commit**: ec9e3c0436fbff934fa84e22bf07f1b3ef5bfac3
