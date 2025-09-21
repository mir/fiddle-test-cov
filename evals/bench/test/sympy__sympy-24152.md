# sympy__sympy-24152

**Repository**: sympy/sympy
**Created**: 2022-10-21T13:47:03Z
**Version**: 1.12

## Problem Statement

Bug in expand of TensorProduct + Workaround + Fix
### Error description
The expansion of a TensorProduct object stops incomplete if summands in the tensor product factors have (scalar) factors, e.g.
```
from sympy import *
from sympy.physics.quantum import *
U = Operator('U')
V = Operator('V')
P = TensorProduct(2*U - V, U + V)
print(P) 
# (2*U - V)x(U + V)
print(P.expand(tensorproduct=True)) 
#result: 2*Ux(U + V) - Vx(U + V) #expansion has missed 2nd tensor factor and is incomplete
```
This is clearly not the expected behaviour. It also effects other functions that rely on .expand(tensorproduct=True), as e.g. qapply() .

### Work around
Repeat .expand(tensorproduct=True) as may times as there are tensor factors, resp. until the expanded term does no longer change. This is however only reasonable in interactive session and not in algorithms.

### Code Fix
.expand relies on the method TensorProduct._eval_expand_tensorproduct(). The issue arises from an inprecise check in TensorProduct._eval_expand_tensorproduct() whether a recursive call is required; it fails when the creation of a TensorProduct object returns commutative (scalar) factors up front: in that case the constructor returns a Mul(c_factors, TensorProduct(..)).
I thus propose the following  code fix in TensorProduct._eval_expand_tensorproduct() in quantum/tensorproduct.py.  I have marked the four lines to be added / modified:
```
    def _eval_expand_tensorproduct(self, **hints):
                ...
                for aa in args[i].args:
                    tp = TensorProduct(*args[:i] + (aa,) + args[i + 1:])
                    c_part, nc_part = tp.args_cnc() #added
                    if len(nc_part)==1 and isinstance(nc_part[0], TensorProduct): #modified
                        nc_part = (nc_part[0]._eval_expand_tensorproduct(), ) #modified
                    add_args.append(Mul(*c_part)*Mul(*nc_part)) #modified
                break
                ...
```
The fix splits of commutative (scalar) factors from the tp returned. The TensorProduct object will be the one nc factor in nc_part (see TensorProduct.__new__ constructor), if any. Note that the constructor will return 0 if a tensor factor is 0, so there is no guarantee that tp contains a TensorProduct object (e.g. TensorProduct(U-U, U+V).





## Hints

Can you make a pull request with this fix?
Will do. I haven't worked with git before, so bear with me.

But as I'm currently digging into some of the quantum package and have more and larger patches in the pipeline, it seems worth the effort to get git set up on my side. So watch out :-)

## Patch

```diff

diff --git a/sympy/physics/quantum/tensorproduct.py b/sympy/physics/quantum/tensorproduct.py
--- a/sympy/physics/quantum/tensorproduct.py
+++ b/sympy/physics/quantum/tensorproduct.py
@@ -246,9 +246,12 @@ def _eval_expand_tensorproduct(self, **hints):
             if isinstance(args[i], Add):
                 for aa in args[i].args:
                     tp = TensorProduct(*args[:i] + (aa,) + args[i + 1:])
-                    if isinstance(tp, TensorProduct):
-                        tp = tp._eval_expand_tensorproduct()
-                    add_args.append(tp)
+                    c_part, nc_part = tp.args_cnc()
+                    # Check for TensorProduct object: is the one object in nc_part, if any:
+                    # (Note: any other object type to be expanded must be added here)
+                    if len(nc_part) == 1 and isinstance(nc_part[0], TensorProduct):
+                        nc_part = (nc_part[0]._eval_expand_tensorproduct(), )
+                    add_args.append(Mul(*c_part)*Mul(*nc_part))
                 break
 
         if add_args:


```

## Test Patch

```diff
diff --git a/sympy/physics/quantum/tests/test_tensorproduct.py b/sympy/physics/quantum/tests/test_tensorproduct.py
--- a/sympy/physics/quantum/tests/test_tensorproduct.py
+++ b/sympy/physics/quantum/tests/test_tensorproduct.py
@@ -44,6 +44,13 @@ def test_tensor_product_abstract():
 def test_tensor_product_expand():
     assert TP(A + B, B + C).expand(tensorproduct=True) == \
         TP(A, B) + TP(A, C) + TP(B, B) + TP(B, C)
+    #Tests for fix of issue #24142
+    assert TP(A-B, B-A).expand(tensorproduct=True) == \
+        TP(A, B) - TP(A, A) - TP(B, B) + TP(B, A)
+    assert TP(2*A + B, A + B).expand(tensorproduct=True) == \
+        2 * TP(A, A) + 2 * TP(A, B) + TP(B, A) + TP(B, B)
+    assert TP(2 * A * B + A, A + B).expand(tensorproduct=True) == \
+        2 * TP(A*B, A) + 2 * TP(A*B, B) + TP(A, A) + TP(A, B)
 
 
 def test_tensor_product_commutator():

```

## Test Information

**Tests that should FAIL→PASS**: ["test_tensor_product_expand"]

**Tests that should PASS→PASS**: ["test_sparse_matrices", "test_tensor_product_dagger", "test_tensor_product_abstract", "test_tensor_product_commutator", "test_tensor_product_simp", "test_issue_5923"]

**Base Commit**: b9af885473ad7e34b5b0826cb424dd26d8934670
**Environment Setup Commit**: c6cb7c5602fa48034ab1bd43c2347a7e8488f12e
