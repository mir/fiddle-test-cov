# sympy__sympy-14308

**Repository**: sympy/sympy
**Created**: 2018-02-22T16:54:06Z
**Version**: 1.1

## Problem Statement

vectors break pretty printing
```py
In [1]: from sympy.vector import *

In [2]: e = CoordSysCartesian('e')

In [3]: (x/y)**t*e.j
Out[3]:
⎛   t⎞ e_j
⎜⎛x⎞ e_j ⎟
⎜⎜─⎟ ⎟
⎝⎝y⎠ ⎠
```

Also, when it does print correctly, the baseline is wrong (it should be centered). 


## Hints

Hi @asmeurer . I would like to work on this issue . Could you help me with the same ? 

## Patch

```diff

diff --git a/sympy/printing/pretty/pretty.py b/sympy/printing/pretty/pretty.py
--- a/sympy/printing/pretty/pretty.py
+++ b/sympy/printing/pretty/pretty.py
@@ -931,26 +931,49 @@ def _print_BasisDependent(self, expr):
         #Fixing the newlines
         lengths = []
         strs = ['']
+        flag = []
         for i, partstr in enumerate(o1):
+            flag.append(0)
             # XXX: What is this hack?
             if '\n' in partstr:
                 tempstr = partstr
                 tempstr = tempstr.replace(vectstrs[i], '')
-                tempstr = tempstr.replace(u'\N{RIGHT PARENTHESIS UPPER HOOK}',
-                                          u'\N{RIGHT PARENTHESIS UPPER HOOK}'
-                                          + ' ' + vectstrs[i])
+                if u'\N{right parenthesis extension}' in tempstr:   # If scalar is a fraction
+                    for paren in range(len(tempstr)):
+                        flag[i] = 1
+                        if tempstr[paren] == u'\N{right parenthesis extension}':
+                            tempstr = tempstr[:paren] + u'\N{right parenthesis extension}'\
+                                         + ' '  + vectstrs[i] + tempstr[paren + 1:]
+                            break
+                elif u'\N{RIGHT PARENTHESIS LOWER HOOK}' in tempstr:
+                    flag[i] = 1
+                    tempstr = tempstr.replace(u'\N{RIGHT PARENTHESIS LOWER HOOK}',
+                                        u'\N{RIGHT PARENTHESIS LOWER HOOK}'
+                                        + ' ' + vectstrs[i])
+                else:
+                    tempstr = tempstr.replace(u'\N{RIGHT PARENTHESIS UPPER HOOK}',
+                                        u'\N{RIGHT PARENTHESIS UPPER HOOK}'
+                                        + ' ' + vectstrs[i])
                 o1[i] = tempstr
+
         o1 = [x.split('\n') for x in o1]
-        n_newlines = max([len(x) for x in o1])
-        for parts in o1:
-            lengths.append(len(parts[0]))
+        n_newlines = max([len(x) for x in o1])  # Width of part in its pretty form
+
+        if 1 in flag:                           # If there was a fractional scalar
+            for i, parts in enumerate(o1):
+                if len(parts) == 1:             # If part has no newline
+                    parts.insert(0, ' ' * (len(parts[0])))
+                    flag[i] = 1
+
+        for i, parts in enumerate(o1):
+            lengths.append(len(parts[flag[i]]))
             for j in range(n_newlines):
                 if j+1 <= len(parts):
                     if j >= len(strs):
                         strs.append(' ' * (sum(lengths[:-1]) +
                                            3*(len(lengths)-1)))
-                    if j == 0:
-                        strs[0] += parts[0] + ' + '
+                    if j == flag[i]:
+                        strs[flag[i]] += parts[flag[i]] + ' + '
                     else:
                         strs[j] += parts[j] + ' '*(lengths[-1] -
                                                    len(parts[j])+


```

## Test Patch

```diff
diff --git a/sympy/printing/pretty/tests/test_pretty.py b/sympy/printing/pretty/tests/test_pretty.py
--- a/sympy/printing/pretty/tests/test_pretty.py
+++ b/sympy/printing/pretty/tests/test_pretty.py
@@ -6089,6 +6089,28 @@ def test_MatrixElement_printing():
     assert upretty(F) == ucode_str1
 
 
+def test_issue_12675():
+    from sympy.vector import CoordSys3D
+    x, y, t, j = symbols('x y t j')
+    e = CoordSys3D('e')
+
+    ucode_str = \
+u("""\
+⎛   t⎞    \n\
+⎜⎛x⎞ ⎟ e_j\n\
+⎜⎜─⎟ ⎟    \n\
+⎝⎝y⎠ ⎠    \
+""")
+    assert upretty((x/y)**t*e.j) == ucode_str
+    ucode_str = \
+u("""\
+⎛1⎞    \n\
+⎜─⎟ e_j\n\
+⎝y⎠    \
+""")
+    assert upretty((1/y)*e.j) == ucode_str
+
+
 def test_MatrixSymbol_printing():
     # test cases for issue #14237
     A = MatrixSymbol("A", 3, 3)
diff --git a/sympy/vector/tests/test_printing.py b/sympy/vector/tests/test_printing.py
--- a/sympy/vector/tests/test_printing.py
+++ b/sympy/vector/tests/test_printing.py
@@ -37,8 +37,8 @@ def upretty(expr):
 v.append(N.j - (Integral(f(b)) - C.x**2)*N.k)
 upretty_v_8 = u(
 """\
-N_j + ⎛   2   ⌠        ⎞ N_k\n\
-      ⎜C_x  - ⎮ f(b) db⎟    \n\
+      ⎛   2   ⌠        ⎞    \n\
+N_j + ⎜C_x  - ⎮ f(b) db⎟ N_k\n\
       ⎝       ⌡        ⎠    \
 """)
 pretty_v_8 = u(
@@ -55,9 +55,9 @@ def upretty(expr):
 v.append((a**2 + b)*N.i + (Integral(f(b)))*N.k)
 upretty_v_11 = u(
 """\
-⎛ 2    ⎞ N_i + ⎛⌠        ⎞ N_k\n\
-⎝a  + b⎠       ⎜⎮ f(b) db⎟    \n\
-               ⎝⌡        ⎠    \
+⎛ 2    ⎞        ⎛⌠        ⎞    \n\
+⎝a  + b⎠ N_i  + ⎜⎮ f(b) db⎟ N_k\n\
+                ⎝⌡        ⎠    \
 """)
 pretty_v_11 = u(
 """\
@@ -85,8 +85,8 @@ def upretty(expr):
 # This is the pretty form for ((a**2 + b)*N.i + 3*(C.y - c)*N.k) | N.k
 upretty_d_7 = u(
 """\
-⎛ 2    ⎞ (N_i|N_k) + (3⋅C_y - 3⋅c) (N_k|N_k)\n\
-⎝a  + b⎠                                    \
+⎛ 2    ⎞                                     \n\
+⎝a  + b⎠ (N_i|N_k)  + (3⋅C_y - 3⋅c) (N_k|N_k)\
 """)
 pretty_d_7 = u(
 """\

```

## Test Information

**Tests that should FAIL→PASS**: ["test_issue_12675", "test_pretty_print_unicode"]

**Tests that should PASS→PASS**: ["test_pretty_ascii_str", "test_pretty_unicode_str", "test_upretty_greek", "test_upretty_multiindex", "test_upretty_sub_super", "test_upretty_subs_missing_in_24", "test_upretty_modifiers", "test_pretty_Cycle", "test_pretty_basic", "test_negative_fractions", "test_issue_5524", "test_pretty_ordering", "test_EulerGamma", "test_GoldenRatio", "test_pretty_relational", "test_Assignment", "test_AugmentedAssignment", "test_issue_7117", "test_pretty_rational", "test_pretty_functions", "test_pretty_sqrt", "test_pretty_sqrt_char_knob", "test_pretty_sqrt_longsymbol_no_sqrt_char", "test_pretty_KroneckerDelta", "test_pretty_product", "test_pretty_lambda", "test_pretty_order", "test_pretty_derivatives", "test_pretty_integrals", "test_pretty_matrix", "test_pretty_ndim_arrays", "test_tensor_TensorProduct", "test_diffgeom_print_WedgeProduct", "test_Adjoint", "test_pretty_Trace_issue_9044", "test_MatrixExpressions", "test_pretty_dotproduct", "test_pretty_piecewise", "test_pretty_ITE", "test_pretty_seq", "test_any_object_in_sequence", "test_print_builtin_set", "test_pretty_sets", "test_pretty_SetExpr", "test_pretty_ImageSet", "test_pretty_ConditionSet", "test_pretty_ComplexRegion", "test_pretty_Union_issue_10414", "test_pretty_Intersection_issue_10414", "test_ProductSet_paranthesis", "test_ProductSet_prod_char_issue_10413", "test_pretty_sequences", "test_pretty_FourierSeries", "test_pretty_FormalPowerSeries", "test_pretty_limits", "test_pretty_ComplexRootOf", "test_pretty_RootSum", "test_GroebnerBasis", "test_pretty_Boolean", "test_pretty_Domain", "test_pretty_prec", "test_pprint", "test_pretty_class", "test_pretty_no_wrap_line", "test_settings", "test_pretty_sum", "test_units", "test_pretty_Subs", "test_gammas", "test_beta", "test_function_subclass_different_name", "test_SingularityFunction", "test_deltas", "test_hyper", "test_meijerg", "test_noncommutative", "test_pretty_special_functions", "test_expint", "test_elliptic_functions", "test_RandomDomain", "test_PrettyPoly", "test_issue_6285", "test_issue_6359", "test_issue_6739", "test_complicated_symbol_unchanged", "test_categories", "test_PrettyModules", "test_QuotientRing", "test_Homomorphism", "test_Tr", "test_pretty_Add", "test_issue_7179", "test_issue_7180", "test_pretty_Complement", "test_pretty_SymmetricDifference", "test_pretty_Contains", "test_issue_4335", "test_issue_6324", "test_issue_7927", "test_issue_6134", "test_issue_9877", "test_issue_13651", "test_pretty_primenu", "test_pretty_primeomega", "test_pretty_Mod", "test_issue_11801", "test_pretty_UnevaluatedExpr", "test_issue_10472", "test_MatrixElement_printing", "test_MatrixSymbol_printing", "test_degree_printing", "test_str_printing", "test_latex_printing"]

**Base Commit**: fb536869fb7aa28b2695ad7a3b70949926b291c4
**Environment Setup Commit**: ec9e3c0436fbff934fa84e22bf07f1b3ef5bfac3
