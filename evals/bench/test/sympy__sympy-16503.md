# sympy__sympy-16503

**Repository**: sympy/sympy
**Created**: 2019-03-30T19:21:15Z
**Version**: 1.5

## Problem Statement

Bad centering for Sum pretty print
```
>>> pprint(Sum(x, (x, 1, oo)) + 3)
  ∞
 ___
 ╲
  ╲   x
  ╱     + 3
 ╱
 ‾‾‾
x = 1
```

The `x` and the `+ 3` should be aligned. I'm not sure if the `x` should be lower of if the `+ 3` should be higher. 


## Hints

```
>>> pprint(Sum(x**2, (x, 1, oo)) + 3)
 ∞         
 ___        
 ╲          
  ╲    2    
  ╱   x  + 3
 ╱          
 ‾‾‾        
x = 1
```
This works well. So, I suppose that `x`, in the above case should be lower.
Could you tell me, how I can correct it?
The issue might be with the way adjustments are calculated, and this definitely works for simpler expressions:
```diff
diff --git a/sympy/printing/pretty/pretty.py b/sympy/printing/pretty/pretty.py
index 7a3de3352..07198bea4 100644
--- a/sympy/printing/pretty/pretty.py
+++ b/sympy/printing/pretty/pretty.py
@@ -575,7 +575,7 @@ def adjust(s, wid=None, how='<^>'):
                 for i in reversed(range(0, d)):
                     lines.append('%s%s%s' % (' '*i, vsum[4], ' '*(w - i - 1)))
                 lines.append(vsum[8]*(w))
-                return d, h + 2*more, lines, more
+                return d, h + 2*more, lines, more // 2
 
         f = expr.function
```
as in
```python
>>> pprint(Sum(x ** n, (n, 1, oo)) + x)
      ∞     
     ___    
     ╲      
      ╲    n
x +   ╱   x 
     ╱      
     ‾‾‾    
    n = 1   

>>> pprint(Sum(n, (n, 1, oo)) + x)
      ∞    
     ___   
     ╲     
      ╲    
x +   ╱   n
     ╱     
     ‾‾‾   
    n = 1   
```

but this leads to test failures for more complex expressions. However, many of the tests look like they expect the misaligned sum.
The ascii printer also has this issue:
```
In [1]: pprint(x + Sum(x + Integral(x**2 + x + 1, (x, 0, n)), (n, 1, oo)), use_unicode=False)
       oo                            
    ______                           
    \     `                          
     \      /      n                \
      \     |      /                |
       \    |     |                 |
x +     \   |     |  / 2        \   |
        /   |x +  |  \x  + x + 1/ dx|
       /    |     |                 |
      /     |    /                  |
     /      \    0                  /
    /_____,                          
     n = 1                           

```

## Patch

```diff

diff --git a/sympy/printing/pretty/pretty.py b/sympy/printing/pretty/pretty.py
--- a/sympy/printing/pretty/pretty.py
+++ b/sympy/printing/pretty/pretty.py
@@ -564,7 +564,7 @@ def adjust(s, wid=None, how='<^>'):
                 for i in reversed(range(1, d)):
                     lines.append('%s/%s' % (' '*i, ' '*(w - i)))
                 lines.append("/" + "_"*(w - 1) + ',')
-                return d, h + more, lines, 0
+                return d, h + more, lines, more
             else:
                 w = w + more
                 d = d + more
@@ -619,7 +619,7 @@ def adjust(s, wid=None, how='<^>'):
             if first:
                 # change F baseline so it centers on the sign
                 prettyF.baseline -= d - (prettyF.height()//2 -
-                                         prettyF.baseline) - adjustment
+                                         prettyF.baseline)
                 first = False
 
             # put padding to the right
@@ -629,7 +629,11 @@ def adjust(s, wid=None, how='<^>'):
             # put the present prettyF to the right
             prettyF = prettyForm(*prettySign.right(prettyF))
 
-        prettyF.baseline = max_upper + sign_height//2
+        # adjust baseline of ascii mode sigma with an odd height so that it is
+        # exactly through the center
+        ascii_adjustment = ascii_mode if not adjustment else 0
+        prettyF.baseline = max_upper + sign_height//2 + ascii_adjustment
+
         prettyF.binding = prettyForm.MUL
         return prettyF
 


```

## Test Patch

```diff
diff --git a/sympy/printing/pretty/tests/test_pretty.py b/sympy/printing/pretty/tests/test_pretty.py
--- a/sympy/printing/pretty/tests/test_pretty.py
+++ b/sympy/printing/pretty/tests/test_pretty.py
@@ -4423,14 +4423,14 @@ def test_pretty_sum():
   n             \n\
 ______          \n\
 ╲               \n\
- ╲      ∞       \n\
-  ╲     ⌠       \n\
-   ╲    ⎮   n   \n\
-    ╲   ⎮  x  dx\n\
-    ╱   ⌡       \n\
-   ╱    -∞      \n\
-  ╱    k        \n\
- ╱              \n\
+ ╲              \n\
+  ╲     ∞       \n\
+   ╲    ⌠       \n\
+    ╲   ⎮   n   \n\
+    ╱   ⎮  x  dx\n\
+   ╱    ⌡       \n\
+  ╱     -∞      \n\
+ ╱     k        \n\
 ╱               \n\
 ‾‾‾‾‾‾          \n\
 k = 0           \
@@ -4474,14 +4474,14 @@ def test_pretty_sum():
 -∞                \n\
  ______           \n\
  ╲                \n\
-  ╲       ∞       \n\
-   ╲      ⌠       \n\
-    ╲     ⎮   n   \n\
-     ╲    ⎮  x  dx\n\
-     ╱    ⌡       \n\
-    ╱     -∞      \n\
-   ╱     k        \n\
-  ╱               \n\
+  ╲               \n\
+   ╲      ∞       \n\
+    ╲     ⌠       \n\
+     ╲    ⎮   n   \n\
+     ╱    ⎮  x  dx\n\
+    ╱     ⌡       \n\
+   ╱      -∞      \n\
+  ╱      k        \n\
  ╱                \n\
  ‾‾‾‾‾‾           \n\
  k = 0            \
@@ -4527,14 +4527,14 @@ def test_pretty_sum():
           -∞                         \n\
            ______                    \n\
            ╲                         \n\
-            ╲                ∞       \n\
-             ╲               ⌠       \n\
-              ╲              ⎮   n   \n\
-               ╲             ⎮  x  dx\n\
-               ╱             ⌡       \n\
-              ╱              -∞      \n\
-             ╱              k        \n\
-            ╱                        \n\
+            ╲                        \n\
+             ╲               ∞       \n\
+              ╲              ⌠       \n\
+               ╲             ⎮   n   \n\
+               ╱             ⎮  x  dx\n\
+              ╱              ⌡       \n\
+             ╱               -∞      \n\
+            ╱               k        \n\
            ╱                         \n\
            ‾‾‾‾‾‾                    \n\
      2        2       1   x          \n\
@@ -4572,14 +4572,14 @@ def test_pretty_sum():
                   x   n          \n\
          ______                  \n\
          ╲                       \n\
-          ╲              ∞       \n\
-           ╲             ⌠       \n\
-            ╲            ⎮   n   \n\
-             ╲           ⎮  x  dx\n\
-             ╱           ⌡       \n\
-            ╱            -∞      \n\
-           ╱            k        \n\
-          ╱                      \n\
+          ╲                      \n\
+           ╲             ∞       \n\
+            ╲            ⌠       \n\
+             ╲           ⎮   n   \n\
+             ╱           ⎮  x  dx\n\
+            ╱            ⌡       \n\
+           ╱             -∞      \n\
+          ╱             k        \n\
          ╱                       \n\
          ‾‾‾‾‾‾                  \n\
          k = 0                   \
@@ -4602,8 +4602,8 @@ def test_pretty_sum():
   ∞    \n\
  ___   \n\
  ╲     \n\
-  ╲   x\n\
-  ╱    \n\
+  ╲    \n\
+  ╱   x\n\
  ╱     \n\
  ‾‾‾   \n\
 x = 0  \
@@ -4655,10 +4655,10 @@ def test_pretty_sum():
   ∞    \n\
  ____  \n\
  ╲     \n\
-  ╲   x\n\
-   ╲  ─\n\
-   ╱  2\n\
-  ╱    \n\
+  ╲    \n\
+   ╲  x\n\
+   ╱  ─\n\
+  ╱   2\n\
  ╱     \n\
  ‾‾‾‾  \n\
 x = 0  \
@@ -4716,12 +4716,12 @@ def test_pretty_sum():
   ∞           \n\
 _____         \n\
 ╲             \n\
- ╲           n\n\
-  ╲   ⎛    x⎞ \n\
-   ╲  ⎜    ─⎟ \n\
-   ╱  ⎜ 3  2⎟ \n\
-  ╱   ⎝x ⋅y ⎠ \n\
- ╱            \n\
+ ╲            \n\
+  ╲          n\n\
+   ╲  ⎛    x⎞ \n\
+   ╱  ⎜    ─⎟ \n\
+  ╱   ⎜ 3  2⎟ \n\
+ ╱    ⎝x ⋅y ⎠ \n\
 ╱             \n\
 ‾‾‾‾‾         \n\
 x = 0         \
@@ -4844,14 +4844,14 @@ def test_pretty_sum():
     ∞          n                         \n\
   ______   ______                        \n\
   ╲        ╲                             \n\
-   ╲        ╲     ⎛        1    ⎞        \n\
-    ╲        ╲    ⎜1 + ─────────⎟        \n\
-     ╲        ╲   ⎜          1  ⎟        \n\
-      ╲        ╲  ⎜    1 + ─────⎟     1  \n\
-      ╱        ╱  ⎜            1⎟ + ─────\n\
-     ╱        ╱   ⎜        1 + ─⎟       1\n\
-    ╱        ╱    ⎝            k⎠   1 + ─\n\
-   ╱        ╱                           k\n\
+   ╲        ╲                            \n\
+    ╲        ╲    ⎛        1    ⎞        \n\
+     ╲        ╲   ⎜1 + ─────────⎟        \n\
+      ╲        ╲  ⎜          1  ⎟     1  \n\
+      ╱        ╱  ⎜    1 + ─────⎟ + ─────\n\
+     ╱        ╱   ⎜            1⎟       1\n\
+    ╱        ╱    ⎜        1 + ─⎟   1 + ─\n\
+   ╱        ╱     ⎝            k⎠       k\n\
   ╱        ╱                             \n\
   ‾‾‾‾‾‾   ‾‾‾‾‾‾                        \n\
       1   k = 111                        \n\

```

## Test Information

**Tests that should FAIL→PASS**: ["test_pretty_sum"]

**Tests that should PASS→PASS**: ["test_pretty_ascii_str", "test_pretty_unicode_str", "test_upretty_greek", "test_upretty_multiindex", "test_upretty_sub_super", "test_upretty_subs_missing_in_24", "test_missing_in_2X_issue_9047", "test_upretty_modifiers", "test_pretty_Cycle", "test_pretty_basic", "test_negative_fractions", "test_issue_5524", "test_pretty_ordering", "test_EulerGamma", "test_GoldenRatio", "test_pretty_relational", "test_Assignment", "test_AugmentedAssignment", "test_issue_7117", "test_pretty_rational", "test_pretty_functions", "test_pretty_sqrt", "test_pretty_sqrt_char_knob", "test_pretty_sqrt_longsymbol_no_sqrt_char", "test_pretty_KroneckerDelta", "test_pretty_product", "test_pretty_lambda", "test_pretty_order", "test_pretty_derivatives", "test_pretty_integrals", "test_pretty_matrix", "test_pretty_ndim_arrays", "test_tensor_TensorProduct", "test_diffgeom_print_WedgeProduct", "test_Adjoint", "test_pretty_Trace_issue_9044", "test_MatrixExpressions", "test_pretty_dotproduct", "test_pretty_piecewise", "test_pretty_ITE", "test_pretty_seq", "test_any_object_in_sequence", "test_print_builtin_set", "test_pretty_sets", "test_pretty_SetExpr", "test_pretty_ImageSet", "test_pretty_ConditionSet", "test_pretty_ComplexRegion", "test_pretty_Union_issue_10414", "test_pretty_Intersection_issue_10414", "test_ProductSet_paranthesis", "test_ProductSet_prod_char_issue_10413", "test_pretty_sequences", "test_pretty_FourierSeries", "test_pretty_FormalPowerSeries", "test_pretty_limits", "test_pretty_ComplexRootOf", "test_pretty_RootSum", "test_GroebnerBasis", "test_pretty_Boolean", "test_pretty_Domain", "test_pretty_prec", "test_pprint", "test_pretty_class", "test_pretty_no_wrap_line", "test_settings", "test_units", "test_pretty_Subs", "test_gammas", "test_beta", "test_function_subclass_different_name", "test_SingularityFunction", "test_deltas", "test_hyper", "test_meijerg", "test_noncommutative", "test_pretty_special_functions", "test_pretty_geometry", "test_expint", "test_elliptic_functions", "test_RandomDomain", "test_PrettyPoly", "test_issue_6285", "test_issue_6359", "test_issue_6739", "test_complicated_symbol_unchanged", "test_categories", "test_PrettyModules", "test_QuotientRing", "test_Homomorphism", "test_Tr", "test_pretty_Add", "test_issue_7179", "test_issue_7180", "test_pretty_Complement", "test_pretty_SymmetricDifference", "test_pretty_Contains", "test_issue_4335", "test_issue_6324", "test_issue_7927", "test_issue_6134", "test_issue_9877", "test_issue_13651", "test_pretty_primenu", "test_pretty_primeomega", "test_pretty_Mod", "test_issue_11801", "test_pretty_UnevaluatedExpr", "test_issue_10472", "test_MatrixElement_printing", "test_issue_12675", "test_MatrixSymbol_printing", "test_degree_printing", "test_vector_expr_pretty_printing", "test_pretty_print_tensor_expr", "test_pretty_print_tensor_partial_deriv", "test_issue_15560", "test_print_lerchphi", "test_issue_15583", "test_matrixSymbolBold", "test_center_accent"]

**Base Commit**: a7e6f093c98a3c4783848a19fce646e32b6e0161
**Environment Setup Commit**: 70381f282f2d9d039da860e391fe51649df2779d
