# sympy__sympy-18532

**Repository**: sympy/sympy
**Created**: 2020-02-01T17:26:30Z
**Version**: 1.6

## Problem Statement

expr.atoms() should return objects with no args instead of subclasses of Atom
`expr.atoms()` with no arguments returns subclasses of `Atom` in `expr`. But the correct definition of a leaf node should be that it has no `.args`. 

This should be easy to fix, but one needs to check that this doesn't affect the performance. 



## Hints

The docstring should also be updated. 

Hi, can i work on this?

Sure. Did you read https://github.com/sympy/sympy/wiki/Introduction-to-contributing? 

How should I remove .args? Should I try to remove ._args from object instance or add a new attribute to class Atom(), is_leave. Which when assigned as false, will raise attribute error on .args. Or if creating a new object, what attributes should it have?

I think you're misunderstanding the issue. The issue is not to remove .args. Indeed, every SymPy object should have .args in order to be valid. 

The issue is that the `atoms()` method currently uses `x.is_Atom` to check for "atomic" expressions (expressions with no subexpressions), but it really should be checking `not x.args`. It should be a simple one-line fix to the `atoms` function definition, but a new test should be added, and the full test suite run to make sure it doesn't break anything (`./bin/test` from the sympy directory). 

Okay. But, Basic() also return .args to be null. So will not that also appear in the result of .atoms()?

Yes, that's an example of an object with no args but that isn't a subclass of Atom. `atoms` should return that, because it's a leaf in the expression tree. 

Okay, but if I am understanding you correct, won't this test fail?
https://github.com/sympy/sympy/blob/master/sympy/core/tests/test_basic.py#L73

Yes, it would need to be changed. This is a slight redefinition of what `atoms` means (although hopefully not enough of a breaking behavior to require deprecation). 

Can you look over it once and look if it is okay?
https://github.com/sympy/sympy/pull/10246

@asmeurer 
When I ran the full suite of tests, sympy/vector/tests/test_field_functions.py failed on all the tests. 

```
     Original-
            if not (types or expr.args):
                result.add(expr)

     Case 1-     
            if not types:
                if isinstance(expr, Atom):
                    result.add(expr)

     Case 2-
            if not (types or expr.args):
                if isinstance(expr, Atom):
                    result.add(expr)
```

I saw that fails even on the second case. Then I saw the items that case1 had but case2 did not. Which were all either `C.z <class 'sympy.vector.scalar.BaseScalar'>` or `C.k <class 'sympy.vector.vector.BaseVector'>`. 

Elements of the class sympy.vector.scaler.BaseScalar or class sympy.vector.vector.BaseVector were earlier considered but not now, as they were Atom but had arguments. So what should we do?

I want to fix this if no one is working on it.

I am unable to figure out why 'Atom' has been assigned to 'types' . We can add the result while checking for the types and if there are no types then we can simply add x.args to the result. That way it will return null and we will not be having subclasses of Atom.

ping @asmeurer 

@darkcoderrises I have some fixes at https://github.com/sympy/sympy/pull/10084 which might make your issues go away. Once that is merged you should try merging your branch into master and see if it fixes the problems. 

ok

I merged the pull requests, and now the tests are passing. What should be my next step.
https://github.com/sympy/sympy/pull/10246

I am working on this issue

## Patch

```diff

diff --git a/sympy/core/basic.py b/sympy/core/basic.py
--- a/sympy/core/basic.py
+++ b/sympy/core/basic.py
@@ -503,12 +503,11 @@ def atoms(self, *types):
         if types:
             types = tuple(
                 [t if isinstance(t, type) else type(t) for t in types])
+        nodes = preorder_traversal(self)
+        if types:
+            result = {node for node in nodes if isinstance(node, types)}
         else:
-            types = (Atom,)
-        result = set()
-        for expr in preorder_traversal(self):
-            if isinstance(expr, types):
-                result.add(expr)
+            result = {node for node in nodes if not node.args}
         return result
 
     @property


```

## Test Patch

```diff
diff --git a/sympy/codegen/tests/test_cnodes.py b/sympy/codegen/tests/test_cnodes.py
--- a/sympy/codegen/tests/test_cnodes.py
+++ b/sympy/codegen/tests/test_cnodes.py
@@ -1,6 +1,6 @@
 from sympy.core.symbol import symbols
 from sympy.printing.ccode import ccode
-from sympy.codegen.ast import Declaration, Variable, float64, int64
+from sympy.codegen.ast import Declaration, Variable, float64, int64, String
 from sympy.codegen.cnodes import (
     alignof, CommaOperator, goto, Label, PreDecrement, PostDecrement, PreIncrement, PostIncrement,
     sizeof, union, struct
@@ -66,7 +66,7 @@ def test_sizeof():
     assert ccode(sz) == 'sizeof(%s)' % typename
     assert sz.func(*sz.args) == sz
     assert not sz.is_Atom
-    assert all(atom == typename for atom in sz.atoms())
+    assert sz.atoms() == {String('unsigned int'), String('sizeof')}
 
 
 def test_struct():
diff --git a/sympy/core/tests/test_basic.py b/sympy/core/tests/test_basic.py
--- a/sympy/core/tests/test_basic.py
+++ b/sympy/core/tests/test_basic.py
@@ -137,7 +137,7 @@ def test_subs_with_unicode_symbols():
 
 
 def test_atoms():
-    assert b21.atoms() == set()
+    assert b21.atoms() == set([Basic()])
 
 
 def test_free_symbols_empty():

```

## Test Information

**Tests that should FAIL→PASS**: ["test_sizeof", "test_atoms"]

**Tests that should PASS→PASS**: ["test_alignof", "test_CommaOperator", "test_goto_Label", "test_PreDecrement", "test_PostDecrement", "test_PreIncrement", "test_PostIncrement", "test_struct", "test__aresame", "test_structure", "test_equality", "test_matches_basic", "test_has", "test_subs", "test_subs_with_unicode_symbols", "test_free_symbols_empty", "test_doit", "test_S", "test_xreplace", "test_preorder_traversal", "test_sorted_args", "test_call", "test_rewrite", "test_literal_evalf_is_number_is_zero_is_comparable", "test_as_Basic", "test_atomic", "test_as_dummy", "test_canonical_variables"]

**Base Commit**: 74227f900b05009d4eed62e34a166228788a32ca
**Environment Setup Commit**: 28b41c73c12b70d6ad9f6e45109a80649c4456da
