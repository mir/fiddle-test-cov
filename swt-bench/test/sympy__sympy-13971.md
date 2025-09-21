# sympy__sympy-13971

**Repository**: sympy/sympy
**Created**: 2018-01-20T10:03:44Z
**Version**: 1.1

## Problem Statement

Display of SeqFormula()
```
import sympy as sp
k, m, n = sp.symbols('k m n', integer=True)
sp.init_printing()

sp.SeqFormula(n**2, (n,0,sp.oo))
```

The Jupyter rendering of this command backslash-escapes the brackets producing:

`\left\[0, 1, 4, 9, \ldots\right\]`

Copying this output to a markdown cell this does not render properly.  Whereas:

`[0, 1, 4, 9, \ldots ]`

does render just fine.  

So - sequence output should not backslash-escape square brackets, or, `\]` should instead render?


## Patch

```diff

diff --git a/sympy/printing/latex.py b/sympy/printing/latex.py
--- a/sympy/printing/latex.py
+++ b/sympy/printing/latex.py
@@ -1657,9 +1657,9 @@ def _print_SeqFormula(self, s):
         else:
             printset = tuple(s)
 
-        return (r"\left\["
+        return (r"\left["
               + r", ".join(self._print(el) for el in printset)
-              + r"\right\]")
+              + r"\right]")
 
     _print_SeqPer = _print_SeqFormula
     _print_SeqAdd = _print_SeqFormula


```

## Test Patch

```diff
diff --git a/sympy/printing/tests/test_latex.py b/sympy/printing/tests/test_latex.py
--- a/sympy/printing/tests/test_latex.py
+++ b/sympy/printing/tests/test_latex.py
@@ -614,46 +614,46 @@ def test_latex_sequences():
     s1 = SeqFormula(a**2, (0, oo))
     s2 = SeqPer((1, 2))
 
-    latex_str = r'\left\[0, 1, 4, 9, \ldots\right\]'
+    latex_str = r'\left[0, 1, 4, 9, \ldots\right]'
     assert latex(s1) == latex_str
 
-    latex_str = r'\left\[1, 2, 1, 2, \ldots\right\]'
+    latex_str = r'\left[1, 2, 1, 2, \ldots\right]'
     assert latex(s2) == latex_str
 
     s3 = SeqFormula(a**2, (0, 2))
     s4 = SeqPer((1, 2), (0, 2))
 
-    latex_str = r'\left\[0, 1, 4\right\]'
+    latex_str = r'\left[0, 1, 4\right]'
     assert latex(s3) == latex_str
 
-    latex_str = r'\left\[1, 2, 1\right\]'
+    latex_str = r'\left[1, 2, 1\right]'
     assert latex(s4) == latex_str
 
     s5 = SeqFormula(a**2, (-oo, 0))
     s6 = SeqPer((1, 2), (-oo, 0))
 
-    latex_str = r'\left\[\ldots, 9, 4, 1, 0\right\]'
+    latex_str = r'\left[\ldots, 9, 4, 1, 0\right]'
     assert latex(s5) == latex_str
 
-    latex_str = r'\left\[\ldots, 2, 1, 2, 1\right\]'
+    latex_str = r'\left[\ldots, 2, 1, 2, 1\right]'
     assert latex(s6) == latex_str
 
-    latex_str = r'\left\[1, 3, 5, 11, \ldots\right\]'
+    latex_str = r'\left[1, 3, 5, 11, \ldots\right]'
     assert latex(SeqAdd(s1, s2)) == latex_str
 
-    latex_str = r'\left\[1, 3, 5\right\]'
+    latex_str = r'\left[1, 3, 5\right]'
     assert latex(SeqAdd(s3, s4)) == latex_str
 
-    latex_str = r'\left\[\ldots, 11, 5, 3, 1\right\]'
+    latex_str = r'\left[\ldots, 11, 5, 3, 1\right]'
     assert latex(SeqAdd(s5, s6)) == latex_str
 
-    latex_str = r'\left\[0, 2, 4, 18, \ldots\right\]'
+    latex_str = r'\left[0, 2, 4, 18, \ldots\right]'
     assert latex(SeqMul(s1, s2)) == latex_str
 
-    latex_str = r'\left\[0, 2, 4\right\]'
+    latex_str = r'\left[0, 2, 4\right]'
     assert latex(SeqMul(s3, s4)) == latex_str
 
-    latex_str = r'\left\[\ldots, 18, 4, 2, 0\right\]'
+    latex_str = r'\left[\ldots, 18, 4, 2, 0\right]'
     assert latex(SeqMul(s5, s6)) == latex_str
 
 

```

## Test Information

**Tests that should FAIL→PASS**: ["test_latex_sequences"]

**Tests that should PASS→PASS**: ["test_printmethod", "test_latex_basic", "test_latex_builtins", "test_latex_SingularityFunction", "test_latex_cycle", "test_latex_permutation", "test_latex_Float", "test_latex_vector_expressions", "test_latex_symbols", "test_latex_functions", "test_hyper_printing", "test_latex_bessel", "test_latex_fresnel", "test_latex_brackets", "test_latex_subs", "test_latex_integrals", "test_latex_sets", "test_latex_Range", "test_latex_intervals", "test_latex_AccumuBounds", "test_latex_emptyset", "test_latex_commutator", "test_latex_union", "test_latex_symmetric_difference", "test_latex_Complement", "test_latex_Complexes", "test_latex_productset", "test_latex_Naturals", "test_latex_Naturals0", "test_latex_Integers", "test_latex_ImageSet", "test_latex_ConditionSet", "test_latex_ComplexRegion", "test_latex_Contains", "test_latex_sum", "test_latex_product", "test_latex_limits", "test_issue_3568", "test_latex", "test_latex_dict", "test_latex_list", "test_latex_rational", "test_latex_inverse", "test_latex_DiracDelta", "test_latex_Heaviside", "test_latex_KroneckerDelta", "test_latex_LeviCivita", "test_mode", "test_latex_Piecewise", "test_latex_Matrix", "test_latex_mul_symbol", "test_latex_issue_4381", "test_latex_issue_4576", "test_latex_pow_fraction", "test_noncommutative", "test_latex_order", "test_latex_Lambda", "test_latex_PolyElement", "test_latex_FracElement", "test_latex_Poly", "test_latex_ComplexRootOf", "test_latex_RootSum", "test_settings", "test_latex_numbers", "test_latex_euler", "test_lamda", "test_custom_symbol_names", "test_matAdd", "test_matMul", "test_latex_MatrixSlice", "test_latex_RandomDomain", "test_PrettyPoly", "test_integral_transforms", "test_categories", "test_Modules", "test_QuotientRing", "test_Tr", "test_Adjoint", "test_Hadamard", "test_ZeroMatrix", "test_boolean_args_order", "test_imaginary", "test_builtins_without_args", "test_latex_greek_functions", "test_translate", "test_other_symbols", "test_modifiers", "test_greek_symbols", "test_builtin_no_args", "test_issue_6853", "test_Mul", "test_Pow", "test_issue_7180", "test_issue_8409", "test_issue_7117", "test_issue_2934", "test_issue_10489", "test_issue_12886", "test_issue_13651", "test_latex_UnevaluatedExpr", "test_MatrixElement_printing", "test_Quaternion_latex_printing"]

**Base Commit**: 84c125972ad535b2dfb245f8d311d347b45e5b8a
**Environment Setup Commit**: ec9e3c0436fbff934fa84e22bf07f1b3ef5bfac3
