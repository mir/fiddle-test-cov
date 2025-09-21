# sympy__sympy-23117

**Repository**: sympy/sympy
**Created**: 2022-02-19T13:15:18Z
**Version**: 1.11

## Problem Statement

sympy.Array([]) fails, while sympy.Matrix([]) works
SymPy 1.4 does not allow to construct empty Array (see code below). Is this the intended behavior?

```
>>> import sympy
KeyboardInterrupt
>>> import sympy
>>> from sympy import Array
>>> sympy.__version__
'1.4'
>>> a = Array([])
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/Users/hcui7/miniconda3/envs/a/lib/python3.7/site-packages/sympy/tensor/array/dense_ndim_array.py", line 130, in __new__
    return cls._new(iterable, shape, **kwargs)
  File "/Users/hcui7/miniconda3/envs/a/lib/python3.7/site-packages/sympy/tensor/array/dense_ndim_array.py", line 136, in _new
    shape, flat_list = cls._handle_ndarray_creation_inputs(iterable, shape, **kwargs)
  File "/Users/hcui7/miniconda3/envs/a/lib/python3.7/site-packages/sympy/tensor/array/ndim_array.py", line 142, in _handle_ndarray_creation_inputs
    iterable, shape = cls._scan_iterable_shape(iterable)
  File "/Users/hcui7/miniconda3/envs/a/lib/python3.7/site-packages/sympy/tensor/array/ndim_array.py", line 127, in _scan_iterable_shape
    return f(iterable)
  File "/Users/hcui7/miniconda3/envs/a/lib/python3.7/site-packages/sympy/tensor/array/ndim_array.py", line 120, in f
    elems, shapes = zip(*[f(i) for i in pointer])
ValueError: not enough values to unpack (expected 2, got 0)
```

@czgdp1807 


## Hints

Technically, `Array([], shape=(0,))` works. It is just unable to understand the shape of `[]`.

## Patch

```diff

diff --git a/sympy/tensor/array/ndim_array.py b/sympy/tensor/array/ndim_array.py
--- a/sympy/tensor/array/ndim_array.py
+++ b/sympy/tensor/array/ndim_array.py
@@ -145,10 +145,12 @@ def __new__(cls, iterable, shape=None, **kwargs):
 
     def _parse_index(self, index):
         if isinstance(index, (SYMPY_INTS, Integer)):
-            raise ValueError("Only a tuple index is accepted")
+            if index >= self._loop_size:
+                raise ValueError("Only a tuple index is accepted")
+            return index
 
         if self._loop_size == 0:
-            raise ValueError("Index not valide with an empty array")
+            raise ValueError("Index not valid with an empty array")
 
         if len(index) != self._rank:
             raise ValueError('Wrong number of array axes')
@@ -194,6 +196,9 @@ def f(pointer):
             if not isinstance(pointer, Iterable):
                 return [pointer], ()
 
+            if len(pointer) == 0:
+                return [], (0,)
+
             result = []
             elems, shapes = zip(*[f(i) for i in pointer])
             if len(set(shapes)) != 1:
@@ -567,11 +572,11 @@ def _check_special_bounds(cls, flat_list, shape):
 
     def _check_index_for_getitem(self, index):
         if isinstance(index, (SYMPY_INTS, Integer, slice)):
-            index = (index, )
+            index = (index,)
 
         if len(index) < self.rank():
-            index = tuple([i for i in index] + \
-                          [slice(None) for i in range(len(index), self.rank())])
+            index = tuple(index) + \
+                          tuple(slice(None) for i in range(len(index), self.rank()))
 
         if len(index) > self.rank():
             raise ValueError('Dimension of index greater than rank of array')


```

## Test Patch

```diff
diff --git a/sympy/tensor/array/tests/test_ndim_array.py b/sympy/tensor/array/tests/test_ndim_array.py
--- a/sympy/tensor/array/tests/test_ndim_array.py
+++ b/sympy/tensor/array/tests/test_ndim_array.py
@@ -10,6 +10,11 @@
 
 from sympy.abc import x, y
 
+mutable_array_types = [
+    MutableDenseNDimArray,
+    MutableSparseNDimArray
+]
+
 array_types = [
     ImmutableDenseNDimArray,
     ImmutableSparseNDimArray,
@@ -46,7 +51,23 @@ def test_issue_18361():
     assert simplify(B) == Array([1, 0])
     assert simplify(C) == Array([x + 1, sin(2*x)])
 
+
 def test_issue_20222():
     A = Array([[1, 2], [3, 4]])
     B = Matrix([[1,2],[3,4]])
     raises(TypeError, lambda: A - B)
+
+
+def test_issue_17851():
+    for array_type in array_types:
+        A = array_type([])
+        assert isinstance(A, array_type)
+        assert A.shape == (0,)
+        assert list(A) == []
+
+
+def test_issue_and_18715():
+    for array_type in mutable_array_types:
+        A = array_type([0, 1, 2])
+        A[0] += 5
+        assert A[0] == 5

```

## Test Information

**Tests that should FAIL→PASS**: ["test_issue_17851"]

**Tests that should PASS→PASS**: ["test_array_negative_indices", "test_issue_18361", "test_issue_20222"]

**Base Commit**: c5cef2499d6eed024b0db5c792d6ec7c53baa470
**Environment Setup Commit**: 9a6104eab0ea7ac191a09c24f3e2d79dcd66bda5
