# sympy__sympy-19007

**Repository**: sympy/sympy
**Created**: 2020-03-29T13:47:11Z
**Version**: 1.6

## Problem Statement

Wrong matrix element fetched from BlockMatrix
Given this code:
```
from sympy import *
n, i = symbols('n, i', integer=True)
A = MatrixSymbol('A', 1, 1)
B = MatrixSymbol('B', n, 1)
C = BlockMatrix([[A], [B]])
print('C is')
pprint(C)
print('C[i, 0] is')
pprint(C[i, 0])
```
I get this output:
```
C is
⎡A⎤
⎢ ⎥
⎣B⎦
C[i, 0] is
(A)[i, 0]
```
`(A)[i, 0]` is the wrong here. `C[i, 0]` should not be simplified as that element may come from either `A` or `B`.


## Hints

I was aware of the problem that the coordinates were loosely handled even if the matrix had symbolic dimensions
I also think that `C[3, 0]` should be undefined because there is no guarantee that n is sufficiently large to contain elements.
`C[3, 0]` should just stay unevaluated, since it might be valid (I assume that's what you mean by 'undefined'). It should be possible to handle some cases properly, for example `C[n, 0]` should return `B[n - 1, 0]`.

If I get some time I might have a go at it, seems to be a nice first PR.

**EDIT:** Sorry that's not even true. If `n` is zero, then `C[n, 0]` is not `B[n - 1, 0]`.

## Patch

```diff

diff --git a/sympy/matrices/expressions/blockmatrix.py b/sympy/matrices/expressions/blockmatrix.py
--- a/sympy/matrices/expressions/blockmatrix.py
+++ b/sympy/matrices/expressions/blockmatrix.py
@@ -7,7 +7,7 @@
 from sympy.utilities import sift
 from sympy.utilities.misc import filldedent
 
-from sympy.matrices.expressions.matexpr import MatrixExpr, ZeroMatrix, Identity
+from sympy.matrices.expressions.matexpr import MatrixExpr, ZeroMatrix, Identity, MatrixElement
 from sympy.matrices.expressions.matmul import MatMul
 from sympy.matrices.expressions.matadd import MatAdd
 from sympy.matrices.expressions.matpow import MatPow
@@ -234,16 +234,24 @@ def transpose(self):
 
     def _entry(self, i, j, **kwargs):
         # Find row entry
+        orig_i, orig_j = i, j
         for row_block, numrows in enumerate(self.rowblocksizes):
-            if (i < numrows) != False:
+            cmp = i < numrows
+            if cmp == True:
                 break
-            else:
+            elif cmp == False:
                 i -= numrows
+            elif row_block < self.blockshape[0] - 1:
+                # Can't tell which block and it's not the last one, return unevaluated
+                return MatrixElement(self, orig_i, orig_j)
         for col_block, numcols in enumerate(self.colblocksizes):
-            if (j < numcols) != False:
+            cmp = j < numcols
+            if cmp == True:
                 break
-            else:
+            elif cmp == False:
                 j -= numcols
+            elif col_block < self.blockshape[1] - 1:
+                return MatrixElement(self, orig_i, orig_j)
         return self.blocks[row_block, col_block][i, j]
 
     @property


```

## Test Patch

```diff
diff --git a/sympy/matrices/expressions/tests/test_blockmatrix.py b/sympy/matrices/expressions/tests/test_blockmatrix.py
--- a/sympy/matrices/expressions/tests/test_blockmatrix.py
+++ b/sympy/matrices/expressions/tests/test_blockmatrix.py
@@ -192,7 +192,6 @@ def test_BlockDiagMatrix():
 def test_blockcut():
     A = MatrixSymbol('A', n, m)
     B = blockcut(A, (n/2, n/2), (m/2, m/2))
-    assert A[i, j] == B[i, j]
     assert B == BlockMatrix([[A[:n/2, :m/2], A[:n/2, m/2:]],
                              [A[n/2:, :m/2], A[n/2:, m/2:]]])
 
diff --git a/sympy/matrices/expressions/tests/test_indexing.py b/sympy/matrices/expressions/tests/test_indexing.py
--- a/sympy/matrices/expressions/tests/test_indexing.py
+++ b/sympy/matrices/expressions/tests/test_indexing.py
@@ -1,7 +1,7 @@
 from sympy import (symbols, MatrixSymbol, MatPow, BlockMatrix, KroneckerDelta,
         Identity, ZeroMatrix, ImmutableMatrix, eye, Sum, Dummy, trace,
         Symbol)
-from sympy.testing.pytest import raises
+from sympy.testing.pytest import raises, XFAIL
 from sympy.matrices.expressions.matexpr import MatrixElement, MatrixExpr
 
 k, l, m, n = symbols('k l m n', integer=True)
@@ -83,6 +83,72 @@ def test_block_index():
     assert BI.as_explicit().equals(eye(6))
 
 
+def test_block_index_symbolic():
+    # Note that these matrices may be zero-sized and indices may be negative, which causes
+    # all naive simplifications given in the comments to be invalid
+    A1 = MatrixSymbol('A1', n, k)
+    A2 = MatrixSymbol('A2', n, l)
+    A3 = MatrixSymbol('A3', m, k)
+    A4 = MatrixSymbol('A4', m, l)
+    A = BlockMatrix([[A1, A2], [A3, A4]])
+    assert A[0, 0] == MatrixElement(A, 0, 0)  # Cannot be A1[0, 0]
+    assert A[n - 1, k - 1] == A1[n - 1, k - 1]
+    assert A[n, k] == A4[0, 0]
+    assert A[n + m - 1, 0] == MatrixElement(A, n + m - 1, 0)  # Cannot be A3[m - 1, 0]
+    assert A[0, k + l - 1] == MatrixElement(A, 0, k + l - 1)  # Cannot be A2[0, l - 1]
+    assert A[n + m - 1, k + l - 1] == MatrixElement(A, n + m - 1, k + l - 1)  # Cannot be A4[m - 1, l - 1]
+    assert A[i, j] == MatrixElement(A, i, j)
+    assert A[n + i, k + j] == MatrixElement(A, n + i, k + j)  # Cannot be A4[i, j]
+    assert A[n - i - 1, k - j - 1] == MatrixElement(A, n - i - 1, k - j - 1)  # Cannot be A1[n - i - 1, k - j - 1]
+
+
+def test_block_index_symbolic_nonzero():
+    # All invalid simplifications from test_block_index_symbolic() that become valid if all
+    # matrices have nonzero size and all indices are nonnegative
+    k, l, m, n = symbols('k l m n', integer=True, positive=True)
+    i, j = symbols('i j', integer=True, nonnegative=True)
+    A1 = MatrixSymbol('A1', n, k)
+    A2 = MatrixSymbol('A2', n, l)
+    A3 = MatrixSymbol('A3', m, k)
+    A4 = MatrixSymbol('A4', m, l)
+    A = BlockMatrix([[A1, A2], [A3, A4]])
+    assert A[0, 0] == A1[0, 0]
+    assert A[n + m - 1, 0] == A3[m - 1, 0]
+    assert A[0, k + l - 1] == A2[0, l - 1]
+    assert A[n + m - 1, k + l - 1] == A4[m - 1, l - 1]
+    assert A[i, j] == MatrixElement(A, i, j)
+    assert A[n + i, k + j] == A4[i, j]
+    assert A[n - i - 1, k - j - 1] == A1[n - i - 1, k - j - 1]
+    assert A[2 * n, 2 * k] == A4[n, k]
+
+
+def test_block_index_large():
+    n, m, k = symbols('n m k', integer=True, positive=True)
+    i = symbols('i', integer=True, nonnegative=True)
+    A1 = MatrixSymbol('A1', n, n)
+    A2 = MatrixSymbol('A2', n, m)
+    A3 = MatrixSymbol('A3', n, k)
+    A4 = MatrixSymbol('A4', m, n)
+    A5 = MatrixSymbol('A5', m, m)
+    A6 = MatrixSymbol('A6', m, k)
+    A7 = MatrixSymbol('A7', k, n)
+    A8 = MatrixSymbol('A8', k, m)
+    A9 = MatrixSymbol('A9', k, k)
+    A = BlockMatrix([[A1, A2, A3], [A4, A5, A6], [A7, A8, A9]])
+    assert A[n + i, n + i] == MatrixElement(A, n + i, n + i)
+
+
+@XFAIL
+def test_block_index_symbolic_fail():
+    # To make this work, symbolic matrix dimensions would need to be somehow assumed nonnegative
+    # even if the symbols aren't specified as such.  Then 2 * n < n would correctly evaluate to
+    # False in BlockMatrix._entry()
+    A1 = MatrixSymbol('A1', n, 1)
+    A2 = MatrixSymbol('A2', m, 1)
+    A = BlockMatrix([[A1], [A2]])
+    assert A[2 * n, 0] == A2[n, 0]
+
+
 def test_slicing():
     A.as_explicit()[0, :]  # does not raise an error
 

```

## Test Information

**Tests that should FAIL→PASS**: ["test_block_index_symbolic", "test_block_index_symbolic_nonzero", "test_block_index_large"]

**Tests that should PASS→PASS**: ["test_bc_matmul", "test_bc_matadd", "test_bc_transpose", "test_bc_dist_diag", "test_block_plus_ident", "test_BlockMatrix", "test_block_collapse_explicit_matrices", "test_issue_17624", "test_issue_18618", "test_BlockMatrix_trace", "test_BlockMatrix_Determinant", "test_squareBlockMatrix", "test_BlockDiagMatrix", "test_blockcut", "test_reblock_2x2", "test_deblock", "test_symbolic_indexing", "test_add_index", "test_mul_index", "test_pow_index", "test_transpose_index", "test_Identity_index", "test_block_index", "test_slicing", "test_errors", "test_matrix_expression_to_indices"]

**Base Commit**: f9e030b57623bebdc2efa7f297c1b5ede08fcebf
**Environment Setup Commit**: 28b41c73c12b70d6ad9f6e45109a80649c4456da
