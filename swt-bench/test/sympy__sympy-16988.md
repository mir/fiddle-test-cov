# sympy__sympy-16988

**Repository**: sympy/sympy
**Created**: 2019-06-07T12:00:00Z
**Version**: 1.5

## Problem Statement

Intersection should remove duplicates
```python
>>> Intersection({1},{1},{x})
EmptySet()
>>> Intersection({1},{x})
{1}
```
The answer should be `Piecewise(({1}, Eq(x, 1)), (S.EmptySet, True))` or remain unevaluated.

The routine should give the same answer if duplicates are present; my initial guess is that duplicates should just be removed at the outset of instantiation. Ordering them will produce canonical processing.


## Patch

```diff

diff --git a/sympy/sets/sets.py b/sympy/sets/sets.py
--- a/sympy/sets/sets.py
+++ b/sympy/sets/sets.py
@@ -1260,7 +1260,7 @@ def __new__(cls, *args, **kwargs):
         evaluate = kwargs.get('evaluate', global_evaluate[0])
 
         # flatten inputs to merge intersections and iterables
-        args = _sympify(args)
+        args = list(ordered(set(_sympify(args))))
 
         # Reduce sets using known rules
         if evaluate:


```

## Test Patch

```diff
diff --git a/sympy/sets/tests/test_sets.py b/sympy/sets/tests/test_sets.py
--- a/sympy/sets/tests/test_sets.py
+++ b/sympy/sets/tests/test_sets.py
@@ -21,7 +21,7 @@ def test_imageset():
     assert imageset(x, abs(x), S.Integers) is S.Naturals0
     # issue 16878a
     r = symbols('r', real=True)
-    assert (1, r) not in imageset(x, (x, x), S.Reals)
+    assert (1, r) in imageset(x, (x, x), S.Reals) != False
     assert (r, r) in imageset(x, (x, x), S.Reals)
     assert 1 + I in imageset(x, x + I, S.Reals)
     assert {1} not in imageset(x, (x,), S.Reals)
@@ -342,6 +342,9 @@ def test_intersection():
     # issue 12178
     assert Intersection() == S.UniversalSet
 
+    # issue 16987
+    assert Intersection({1}, {1}, {x}) == Intersection({1}, {x})
+
 
 def test_issue_9623():
     n = Symbol('n')

```

## Test Information

**Tests that should FAIL→PASS**: ["test_imageset", "test_intersection"]

**Tests that should PASS→PASS**: ["test_interval_arguments", "test_interval_symbolic_end_points", "test_union", "test_union_iter", "test_difference", "test_Complement", "test_complement", "test_intersect1", "test_issue_9623", "test_is_disjoint", "test_ProductSet_of_single_arg_is_arg", "test_interval_subs", "test_interval_to_mpi", "test_measure", "test_is_subset", "test_is_proper_subset", "test_is_superset", "test_is_proper_superset", "test_contains", "test_interval_symbolic", "test_union_contains", "test_is_number", "test_Interval_is_left_unbounded", "test_Interval_is_right_unbounded", "test_Interval_as_relational", "test_Finite_as_relational", "test_Union_as_relational", "test_Intersection_as_relational", "test_EmptySet", "test_finite_basic", "test_powerset", "test_product_basic", "test_real", "test_supinf", "test_universalset", "test_Union_of_ProductSets_shares", "test_Interval_free_symbols", "test_image_interval", "test_image_piecewise", "test_image_FiniteSet", "test_image_Union", "test_image_EmptySet", "test_issue_5724_7680", "test_boundary", "test_boundary_Union", "test_boundary_ProductSet", "test_boundary_ProductSet_line", "test_is_open", "test_is_closed", "test_closure", "test_interior", "test_issue_7841", "test_Eq", "test_SymmetricDifference", "test_issue_9536", "test_issue_9637", "test_issue_9956", "test_issue_Symbol_inter", "test_issue_11827", "test_issue_10113", "test_issue_10248", "test_issue_9447", "test_issue_10337", "test_issue_10326", "test_issue_2799", "test_issue_9706", "test_issue_8257", "test_issue_10931", "test_issue_11174", "test_finite_set_intersection", "test_union_intersection_constructor", "test_Union_contains"]

**Base Commit**: e727339af6dc22321b00f52d971cda39e4ce89fb
**Environment Setup Commit**: 70381f282f2d9d039da860e391fe51649df2779d
