# sympy__sympy-13031

**Repository**: sympy/sympy
**Created**: 2017-07-23T15:48:13Z
**Version**: 1.1

## Problem Statement

Behavior of Matrix hstack and vstack changed in sympy 1.1
In sympy 1.0:
```
import sympy as sy
M1 = sy.Matrix.zeros(0, 0)
M2 = sy.Matrix.zeros(0, 1)
M3 = sy.Matrix.zeros(0, 2)
M4 = sy.Matrix.zeros(0, 3)
sy.Matrix.hstack(M1, M2, M3, M4).shape
```
returns 
`(0, 6)`

Now, same in sympy 1.1:
```
import sympy as sy
M1 = sy.Matrix.zeros(0, 0)
M2 = sy.Matrix.zeros(0, 1)
M3 = sy.Matrix.zeros(0, 2)
M4 = sy.Matrix.zeros(0, 3)
sy.Matrix.hstack(M1, M2, M3, M4).shape
```
returns
`(0, 3)
`
whereas:
```
import sympy as sy
M1 = sy.Matrix.zeros(1, 0)
M2 = sy.Matrix.zeros(1, 1)
M3 = sy.Matrix.zeros(1, 2)
M4 = sy.Matrix.zeros(1, 3)
sy.Matrix.hstack(M1, M2, M3, M4).shape
```
returns
`(1, 6)
`


## Hints

CC @siefkenj 
I update my comment in case someone already read it. We still have an issue with matrices shape in [pyphs](https://github.com/pyphs/pyphs/issues/49#issuecomment-316618994), but hstack and vstack seem ok in sympy 1.1.1rc1:

```
>>> import sympy as sy
>>> sy.__version__
'1.1.1rc1'
>>> '1.1.1rc1'
'1.1.1rc1'
>>> matrices = [sy.Matrix.zeros(0, n) for n in range(4)]
>>> sy.Matrix.hstack(*matrices).shape
(0, 6)
>>> matrices = [sy.Matrix.zeros(1, n) for n in range(4)]
>>> sy.Matrix.hstack(*matrices).shape
(1, 6)
>>> matrices = [sy.Matrix.zeros(n, 0) for n in range(4)]
>>> sy.Matrix.vstack(*matrices).shape
(6, 0)
>>> matrices = [sy.Matrix.zeros(1, n) for n in range(4)]
>>> sy.Matrix.hstack(*matrices).shape
(1, 6)
>>> 
```
The problem is solved with Matrix but not SparseMatrix:
```
>>> import sympy as sy
>>> sy.__version__
'1.1.1rc1'
>>> matrices = [Matrix.zeros(0, n) for n in range(4)]
>>> Matrix.hstack(*matrices)
Matrix(0, 6, [])
>>> sparse_matrices = [SparseMatrix.zeros(0, n) for n in range(4)]
>>> SparseMatrix.hstack(*sparse_matrices)
Matrix(0, 3, [])
>>> 
```
Bisected to 27e9ee425819fa09a4cbb8179fb38939cc693249. Should we revert that commit? CC @aravindkanna
Any thoughts? This is the last fix to potentially go in the 1.1.1 release, but I want to cut a release candidate today or tomorrow, so speak now, or hold your peace (until the next major release).
I am away at a conference. The change should be almost identical to the fix for dense matrices, if someone can manage to get a patch in. I *might* be able to do it tomorrow.
Okay.  I've looked this over and its convoluted...

`SparseMatrix` should impliment `_eval_col_join`.  `col_join` should not be implemented.  It is, and that is what `hstack` is calling, which is why my previous patch didn't fix `SparseMatrix`s as well.  However, the patch that @asmeurer referenced ensures that `SparseMatrix.row_join(DenseMatrix)` returns a `SparseMatrix` whereas `CommonMatrix.row_join(SparseMatrix, DenseMatrix)` returns a `classof(SparseMatrix, DenseMatrix)` which happens to be a `DenseMatrix`.  I don't think that these should behave differently.  This API needs to be better thought out.
So is there a simple fix that can be made for the release or should this be postponed?

## Patch

```diff

diff --git a/sympy/matrices/sparse.py b/sympy/matrices/sparse.py
--- a/sympy/matrices/sparse.py
+++ b/sympy/matrices/sparse.py
@@ -985,8 +985,10 @@ def col_join(self, other):
         >>> C == A.row_insert(A.rows, Matrix(B))
         True
         """
-        if not self:
-            return type(self)(other)
+        # A null matrix can always be stacked (see  #10770)
+        if self.rows == 0 and self.cols != other.cols:
+            return self._new(0, other.cols, []).col_join(other)
+
         A, B = self, other
         if not A.cols == B.cols:
             raise ShapeError()
@@ -1191,8 +1193,10 @@ def row_join(self, other):
         >>> C == A.col_insert(A.cols, B)
         True
         """
-        if not self:
-            return type(self)(other)
+        # A null matrix can always be stacked (see  #10770)
+        if self.cols == 0 and self.rows != other.rows:
+            return self._new(other.rows, 0, []).row_join(other)
+
         A, B = self, other
         if not A.rows == B.rows:
             raise ShapeError()


```

## Test Patch

```diff
diff --git a/sympy/matrices/tests/test_sparse.py b/sympy/matrices/tests/test_sparse.py
--- a/sympy/matrices/tests/test_sparse.py
+++ b/sympy/matrices/tests/test_sparse.py
@@ -26,6 +26,12 @@ def sparse_zeros(n):
     assert type(a.row_join(b)) == type(a)
     assert type(a.col_join(b)) == type(a)
 
+    # make sure 0 x n matrices get stacked correctly
+    sparse_matrices = [SparseMatrix.zeros(0, n) for n in range(4)]
+    assert SparseMatrix.hstack(*sparse_matrices) == Matrix(0, 6, [])
+    sparse_matrices = [SparseMatrix.zeros(n, 0) for n in range(4)]
+    assert SparseMatrix.vstack(*sparse_matrices) == Matrix(6, 0, [])
+
     # test element assignment
     a = SparseMatrix((
         (1, 0),

```

## Test Information

**Tests that should FAIL→PASS**: ["test_sparse_matrix"]

**Tests that should PASS→PASS**: ["test_transpose", "test_trace", "test_CL_RL", "test_add", "test_errors", "test_len", "test_sparse_zeros_sparse_eye", "test_copyin", "test_sparse_solve"]

**Base Commit**: 2dfa7457f20ee187fbb09b5b6a1631da4458388c
**Environment Setup Commit**: ec9e3c0436fbff934fa84e22bf07f1b3ef5bfac3
