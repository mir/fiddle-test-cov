# sympy__sympy-14774

**Repository**: sympy/sympy
**Created**: 2018-06-05T08:03:47Z
**Version**: 1.1

## Problem Statement

Latex printer does not support full inverse trig function names for acsc and asec
For example
`latex(asin(x), inv_trig_style="full")` works as expected returning `'\\arcsin{\\left (x \\right )}'`
But `latex(acsc(x), inv_trig_style="full")` gives `'\\operatorname{acsc}{\\left (x \\right )}'` instead of `'\\operatorname{arccsc}{\\left (x \\right )}'`

A fix seems to be to change line 743 of sympy/printing/latex.py from
`inv_trig_table = ["asin", "acos", "atan", "acot"]` to
`inv_trig_table = ["asin", "acos", "atan", "acsc", "asec", "acot"]`


## Patch

```diff

diff --git a/sympy/printing/latex.py b/sympy/printing/latex.py
--- a/sympy/printing/latex.py
+++ b/sympy/printing/latex.py
@@ -740,7 +740,7 @@ def _print_Function(self, expr, exp=None):
                 len(args) == 1 and \
                 not self._needs_function_brackets(expr.args[0])
 
-            inv_trig_table = ["asin", "acos", "atan", "acot"]
+            inv_trig_table = ["asin", "acos", "atan", "acsc", "asec", "acot"]
 
             # If the function is an inverse trig function, handle the style
             if func in inv_trig_table:


```

## Test Patch

```diff
diff --git a/sympy/printing/tests/test_latex.py b/sympy/printing/tests/test_latex.py
--- a/sympy/printing/tests/test_latex.py
+++ b/sympy/printing/tests/test_latex.py
@@ -6,7 +6,7 @@
     Lambda, LaplaceTransform, Limit, Matrix, Max, MellinTransform, Min, Mul,
     Order, Piecewise, Poly, ring, field, ZZ, Pow, Product, Range, Rational,
     RisingFactorial, rootof, RootSum, S, Shi, Si, SineTransform, Subs,
-    Sum, Symbol, ImageSet, Tuple, Union, Ynm, Znm, arg, asin, Mod,
+    Sum, Symbol, ImageSet, Tuple, Union, Ynm, Znm, arg, asin, acsc, Mod,
     assoc_laguerre, assoc_legendre, beta, binomial, catalan, ceiling, Complement,
     chebyshevt, chebyshevu, conjugate, cot, coth, diff, dirichlet_eta, euler,
     exp, expint, factorial, factorial2, floor, gamma, gegenbauer, hermite,
@@ -305,6 +305,8 @@ def test_latex_functions():
     assert latex(asin(x**2), inv_trig_style="power",
                  fold_func_brackets=True) == \
         r"\sin^{-1} {x^{2}}"
+    assert latex(acsc(x), inv_trig_style="full") == \
+        r"\operatorname{arccsc}{\left (x \right )}"
 
     assert latex(factorial(k)) == r"k!"
     assert latex(factorial(-k)) == r"\left(- k\right)!"

```

## Test Information

**Tests that should FAIL→PASS**: ["test_latex_functions"]

**Tests that should PASS→PASS**: ["test_printmethod", "test_latex_basic", "test_latex_builtins", "test_latex_SingularityFunction", "test_latex_cycle", "test_latex_permutation", "test_latex_Float", "test_latex_vector_expressions", "test_latex_symbols", "test_function_subclass_different_name", "test_hyper_printing", "test_latex_bessel", "test_latex_fresnel", "test_latex_brackets", "test_latex_indexed", "test_latex_derivatives", "test_latex_subs", "test_latex_integrals", "test_latex_sets", "test_latex_SetExpr", "test_latex_Range", "test_latex_sequences", "test_latex_FourierSeries", "test_latex_FormalPowerSeries", "test_latex_intervals", "test_latex_AccumuBounds", "test_latex_emptyset", "test_latex_commutator", "test_latex_union", "test_latex_symmetric_difference", "test_latex_Complement", "test_latex_Complexes", "test_latex_productset", "test_latex_Naturals", "test_latex_Naturals0", "test_latex_Integers", "test_latex_ImageSet", "test_latex_ConditionSet", "test_latex_ComplexRegion", "test_latex_Contains", "test_latex_sum", "test_latex_product", "test_latex_limits", "test_latex_log", "test_issue_3568", "test_latex", "test_latex_dict", "test_latex_list", "test_latex_rational", "test_latex_inverse", "test_latex_DiracDelta", "test_latex_Heaviside", "test_latex_KroneckerDelta", "test_latex_LeviCivita", "test_mode", "test_latex_Piecewise", "test_latex_Matrix", "test_latex_matrix_with_functions", "test_latex_NDimArray", "test_latex_mul_symbol", "test_latex_issue_4381", "test_latex_issue_4576", "test_latex_pow_fraction", "test_noncommutative", "test_latex_order", "test_latex_Lambda", "test_latex_PolyElement", "test_latex_FracElement", "test_latex_Poly", "test_latex_Poly_order", "test_latex_ComplexRootOf", "test_latex_RootSum", "test_settings", "test_latex_numbers", "test_latex_euler", "test_lamda", "test_custom_symbol_names", "test_matAdd", "test_matMul", "test_latex_MatrixSlice", "test_latex_RandomDomain", "test_PrettyPoly", "test_integral_transforms", "test_categories", "test_Modules", "test_QuotientRing", "test_Tr", "test_Adjoint", "test_Hadamard", "test_ZeroMatrix", "test_boolean_args_order", "test_imaginary", "test_builtins_without_args", "test_latex_greek_functions", "test_translate", "test_other_symbols", "test_modifiers", "test_greek_symbols", "test_builtin_no_args", "test_issue_6853", "test_Mul", "test_Pow", "test_issue_7180", "test_issue_8409", "test_issue_7117", "test_issue_2934", "test_issue_10489", "test_issue_12886", "test_issue_13651", "test_latex_UnevaluatedExpr", "test_MatrixElement_printing", "test_MatrixSymbol_printing", "test_Quaternion_latex_printing", "test_TensorProduct_printing"]

**Base Commit**: 8fc63c2d71752389a44367b8ef4aba8a91af6a45
**Environment Setup Commit**: ec9e3c0436fbff934fa84e22bf07f1b3ef5bfac3
