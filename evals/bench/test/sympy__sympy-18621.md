# sympy__sympy-18621

**Repository**: sympy/sympy
**Created**: 2020-02-10T05:36:30Z
**Version**: 1.6

## Problem Statement

BlockDiagMatrix with one element cannot be converted to regular Matrix
Creating a BlockDiagMatrix with one Matrix element will raise if trying to convert it back to a regular Matrix:

```python
M = sympy.Matrix([[1, 2], [3, 4]])
D = sympy.BlockDiagMatrix(M)
B = sympy.Matrix(D)
```

```
Traceback (most recent call last):

  File "<ipython-input-37-5b65c1f8f23e>", line 3, in <module>
    B = sympy.Matrix(D)

  File "/home/rikard/.local/lib/python3.7/site-packages/sympy/matrices/dense.py", line 430, in __new__
    return cls._new(*args, **kwargs)

  File "/home/rikard/.local/lib/python3.7/site-packages/sympy/matrices/dense.py", line 442, in _new
    rows, cols, flat_list = cls._handle_creation_inputs(*args, **kwargs)

  File "/home/rikard/.local/lib/python3.7/site-packages/sympy/matrices/matrices.py", line 2528, in _handle_creation_inputs
    return args[0].rows, args[0].cols, args[0].as_explicit()._mat

  File "/home/rikard/.local/lib/python3.7/site-packages/sympy/matrices/expressions/matexpr.py", line 340, in as_explicit
    for i in range(self.rows)])

  File "/home/rikard/.local/lib/python3.7/site-packages/sympy/matrices/expressions/matexpr.py", line 340, in <listcomp>
    for i in range(self.rows)])

  File "/home/rikard/.local/lib/python3.7/site-packages/sympy/matrices/expressions/matexpr.py", line 339, in <listcomp>
    for j in range(self.cols)]

  File "/home/rikard/.local/lib/python3.7/site-packages/sympy/matrices/expressions/matexpr.py", line 289, in __getitem__
    return self._entry(i, j)

  File "/home/rikard/.local/lib/python3.7/site-packages/sympy/matrices/expressions/blockmatrix.py", line 248, in _entry
    return self.blocks[row_block, col_block][i, j]

TypeError: 'One' object is not subscriptable
```

Instead having two elements will work as expected:

```python
M = sympy.Matrix([[1, 2], [3, 4]])
D = sympy.BlockDiagMatrix(M, M)
B = sympy.Matrix(D)
```

```
Matrix([
[1, 2, 0, 0],
[3, 4, 0, 0],
[0, 0, 1, 2],
[0, 0, 3, 4]])
```
This issue exists for sympy 1.5.1 but not for sympy 1.4


## Hints

```diff
diff --git a/sympy/matrices/expressions/blockmatrix.py b/sympy/matrices/expressions/blockmatrix.py
index 11aebbc59f..b821c42845 100644
--- a/sympy/matrices/expressions/blockmatrix.py
+++ b/sympy/matrices/expressions/blockmatrix.py
@@ -301,7 +301,7 @@ def blocks(self):
         data = [[mats[i] if i == j else ZeroMatrix(mats[i].rows, mats[j].cols)
                         for j in range(len(mats))]
                         for i in range(len(mats))]
-        return ImmutableDenseMatrix(data)
+        return ImmutableDenseMatrix(data, evaluate=False)

     @property
     def shape(self):
```

Okay, someone should do the workaround and add some tests about the issue.
i will submit a pr today.

## Patch

```diff

diff --git a/sympy/matrices/expressions/blockmatrix.py b/sympy/matrices/expressions/blockmatrix.py
--- a/sympy/matrices/expressions/blockmatrix.py
+++ b/sympy/matrices/expressions/blockmatrix.py
@@ -301,7 +301,7 @@ def blocks(self):
         data = [[mats[i] if i == j else ZeroMatrix(mats[i].rows, mats[j].cols)
                         for j in range(len(mats))]
                         for i in range(len(mats))]
-        return ImmutableDenseMatrix(data)
+        return ImmutableDenseMatrix(data, evaluate=False)
 
     @property
     def shape(self):


```

## Test Patch

```diff
diff --git a/sympy/matrices/expressions/tests/test_blockmatrix.py b/sympy/matrices/expressions/tests/test_blockmatrix.py
--- a/sympy/matrices/expressions/tests/test_blockmatrix.py
+++ b/sympy/matrices/expressions/tests/test_blockmatrix.py
@@ -110,6 +110,10 @@ def test_issue_17624():
     assert block_collapse(b * b) == BlockMatrix([[a**2, z], [z, z]])
     assert block_collapse(b * b * b) == BlockMatrix([[a**3, z], [z, z]])
 
+def test_issue_18618():
+    A = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
+    assert A == Matrix(BlockDiagMatrix(A))
+
 def test_BlockMatrix_trace():
     A, B, C, D = [MatrixSymbol(s, 3, 3) for s in 'ABCD']
     X = BlockMatrix([[A, B], [C, D]])

```

## Test Information

**Tests that should FAIL→PASS**: ["test_issue_18618"]

**Tests that should PASS→PASS**: ["test_bc_matmul", "test_bc_matadd", "test_bc_transpose", "test_bc_dist_diag", "test_block_plus_ident", "test_BlockMatrix", "test_block_collapse_explicit_matrices", "test_issue_17624", "test_BlockMatrix_trace", "test_BlockMatrix_Determinant", "test_squareBlockMatrix", "test_BlockDiagMatrix", "test_blockcut", "test_reblock_2x2", "test_deblock"]

**Base Commit**: b17ef6effe278d5b861d65896cc53442a6370d8f
**Environment Setup Commit**: 28b41c73c12b70d6ad9f6e45109a80649c4456da
