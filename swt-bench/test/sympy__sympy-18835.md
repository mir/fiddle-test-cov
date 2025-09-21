# sympy__sympy-18835

**Repository**: sympy/sympy
**Created**: 2020-03-11T23:39:56Z
**Version**: 1.6

## Problem Statement

uniq modifies list argument
When you iterate over a dictionary or set and try to modify it while doing so you get an error from Python:
```python
>>> multiset('THISTLE')
{'T': 2, 'H': 1, 'I': 1, 'S': 1, 'L': 1, 'E': 1}
>>> for i in _:
...   _.pop(i)
...
2
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
RuntimeError: dictionary changed size during iteration
```
It would be good to do the same thing from within `uniq` because the output will silently be wrong if you modify a passed list:
```python
>>> f=list('THISTLE')
>>> for i in uniq(f):
...   f.remove(i)
...   i
...
'T'
'I'
'L'
```
I think this would entail recording the size at the start and then checking the size and raising a similar RuntimeError if the size changes.


## Hints

I'm not sure there is a need to handle this case. Users should know not to mutate something while iterating over it.
With regards to the above discussion, I believe it would indeed be helpful if modifying a passed list to ``uniq`` raises an error while iterating over it, because it does not immediately follow that ``uniq(f)`` would get updated if ``f`` gets updated, as the user might think something like ``uniq`` stores a copy of ``f``, computes the list of unique elements in it, and returns that list. The user may not know, that yield is being used internally instead of return.

I have a doubt regarding the implementation of ``uniq``:
[https://github.com/sympy/sympy/blob/5bfe93281866f0841b36a429f4090c04a0e81d21/sympy/utilities/iterables.py#L2109-L2124](url)
Here, if the first argument, ``seq`` in ``uniq`` does not have a ``__getitem__`` method, and a TypeError is raised somehow, then we call the ``uniq`` function again on ``seq`` with the updated ``result``, won't that yield ALL of the elements of ``seq`` again, even those which have already been _yielded_? 
So mainly what I wanted to point out was, that if we're assuming that the given ``seq`` is iterable (which we must, since we pass it on to the ``enumerate`` function), by definition, ``seq`` must have either ``__getitem__`` or ``__iter__``, both of which can be used to iterate over the **remaining elements** if the TypeError is raised. 
Also, I'm unable to understand the role of ``result`` in all of this, kindly explain.

So should I work on the error handling bit in this function?

## Patch

```diff

diff --git a/sympy/utilities/iterables.py b/sympy/utilities/iterables.py
--- a/sympy/utilities/iterables.py
+++ b/sympy/utilities/iterables.py
@@ -2088,8 +2088,13 @@ def has_variety(seq):
 def uniq(seq, result=None):
     """
     Yield unique elements from ``seq`` as an iterator. The second
-    parameter ``result``  is used internally; it is not necessary to pass
-    anything for this.
+    parameter ``result``  is used internally; it is not necessary
+    to pass anything for this.
+
+    Note: changing the sequence during iteration will raise a
+    RuntimeError if the size of the sequence is known; if you pass
+    an iterator and advance the iterator you will change the
+    output of this routine but there will be no warning.
 
     Examples
     ========
@@ -2106,15 +2111,27 @@ def uniq(seq, result=None):
     >>> list(uniq([[1], [2, 1], [1]]))
     [[1], [2, 1]]
     """
+    try:
+        n = len(seq)
+    except TypeError:
+        n = None
+    def check():
+        # check that size of seq did not change during iteration;
+        # if n == None the object won't support size changing, e.g.
+        # an iterator can't be changed
+        if n is not None and len(seq) != n:
+            raise RuntimeError('sequence changed size during iteration')
     try:
         seen = set()
         result = result or []
         for i, s in enumerate(seq):
             if not (s in seen or seen.add(s)):
                 yield s
+                check()
     except TypeError:
         if s not in result:
             yield s
+            check()
             result.append(s)
         if hasattr(seq, '__getitem__'):
             for s in uniq(seq[i + 1:], result):


```

## Test Patch

```diff
diff --git a/sympy/utilities/tests/test_iterables.py b/sympy/utilities/tests/test_iterables.py
--- a/sympy/utilities/tests/test_iterables.py
+++ b/sympy/utilities/tests/test_iterables.py
@@ -703,6 +703,10 @@ def test_uniq():
         [([1], 2, 2), (2, [1], 2), (2, 2, [1])]
     assert list(uniq([2, 3, 2, 4, [2], [1], [2], [3], [1]])) == \
         [2, 3, 4, [2], [1], [3]]
+    f = [1]
+    raises(RuntimeError, lambda: [f.remove(i) for i in uniq(f)])
+    f = [[1]]
+    raises(RuntimeError, lambda: [f.remove(i) for i in uniq(f)])
 
 
 def test_kbins():

```

## Test Information

**Tests that should FAIL→PASS**: ["test_uniq"]

**Tests that should PASS→PASS**: ["test_is_palindromic", "test_postorder_traversal", "test_flatten", "test_iproduct", "test_group", "test_subsets", "test_variations", "test_cartes", "test_filter_symbols", "test_numbered_symbols", "test_sift", "test_take", "test_dict_merge", "test_prefixes", "test_postfixes", "test_topological_sort", "test_strongly_connected_components", "test_connected_components", "test_rotate", "test_multiset_partitions", "test_multiset_combinations", "test_multiset_permutations", "test_partitions", "test_binary_partitions", "test_bell_perm", "test_involutions", "test_derangements", "test_necklaces", "test_bracelets", "test_generate_oriented_forest", "test_unflatten", "test_common_prefix_suffix", "test_minlex", "test_ordered", "test_runs", "test_reshape", "test_kbins", "test_has_dups", "test__partition", "test_ordered_partitions", "test_rotations"]

**Base Commit**: 516fa83e69caf1e68306cfc912a13f36c434d51c
**Environment Setup Commit**: 28b41c73c12b70d6ad9f6e45109a80649c4456da
