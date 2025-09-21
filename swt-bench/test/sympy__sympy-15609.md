# sympy__sympy-15609

**Repository**: sympy/sympy
**Created**: 2018-12-09T12:27:08Z
**Version**: 1.4

## Problem Statement

Indexed matrix-expression LaTeX printer is not compilable
```python
i, j, k = symbols("i j k")
M = MatrixSymbol("M", k, k)
N = MatrixSymbol("N", k, k)
latex((M*N)[i, j])
```

The LaTeX string produced by the last command is:
```
\sum_{i_{1}=0}^{k - 1} M_{i, _i_1} N_{_i_1, j}
```
LaTeX complains about a double subscript `_`. This expression won't render in MathJax either.


## Hints

Related to https://github.com/sympy/sympy/issues/15059
It's pretty simple to solve, `_print_MatrixElement` of `LatexPrinter` is not calling `self._print` on the indices.
I'd like to work on this. When adding a test, should I expand `test_MatrixElement_printing` or add `test_issue_15595` just for this issue? Or both?
The correct one should be `\sum_{i_{1}=0}^{k - 1} M_{i, i_1} N_{i_1, j}`.
Is that right?
Tests can be put everywhere. I'd prefer to have them next to the other ones.

## Patch

```diff

diff --git a/sympy/printing/latex.py b/sympy/printing/latex.py
--- a/sympy/printing/latex.py
+++ b/sympy/printing/latex.py
@@ -1438,7 +1438,10 @@ def _print_MatrixBase(self, expr):
 
     def _print_MatrixElement(self, expr):
         return self.parenthesize(expr.parent, PRECEDENCE["Atom"], strict=True) \
-            + '_{%s, %s}' % (expr.i, expr.j)
+            + '_{%s, %s}' % (
+            self._print(expr.i),
+            self._print(expr.j)
+        )
 
     def _print_MatrixSlice(self, expr):
         def latexslice(x):


```

## Test Patch

```diff
diff --git a/sympy/printing/tests/test_latex.py b/sympy/printing/tests/test_latex.py
--- a/sympy/printing/tests/test_latex.py
+++ b/sympy/printing/tests/test_latex.py
@@ -1738,6 +1738,11 @@ def test_MatrixElement_printing():
     F = C[0, 0].subs(C, A - B)
     assert latex(F) == r"\left(A - B\right)_{0, 0}"
 
+    i, j, k = symbols("i j k")
+    M = MatrixSymbol("M", k, k)
+    N = MatrixSymbol("N", k, k)
+    assert latex((M*N)[i, j]) == r'\sum_{i_{1}=0}^{k - 1} M_{i, i_{1}} N_{i_{1}, j}'
+
 
 def test_MatrixSymbol_printing():
     # test cases for issue #14237

```

## Test Information

**Tests that should FAIL→PASS**: ["test_MatrixElement_printing"]

**Tests that should PASS→PASS**: ["test_printmethod", "test_latex_basic", "test_latex_builtins", "test_latex_SingularityFunction", "test_latex_cycle", "test_latex_permutation", "test_latex_Float", "test_latex_vector_expressions", "test_latex_symbols", "test_latex_functions", "test_function_subclass_different_name", "test_hyper_printing", "test_latex_bessel", "test_latex_fresnel", "test_latex_brackets", "test_latex_indexed", "test_latex_derivatives", "test_latex_subs", "test_latex_integrals", "test_latex_sets", "test_latex_SetExpr", "test_latex_Range", "test_latex_sequences", "test_latex_FourierSeries", "test_latex_FormalPowerSeries", "test_latex_intervals", "test_latex_AccumuBounds", "test_latex_emptyset", "test_latex_commutator", "test_latex_union", "test_latex_symmetric_difference", "test_latex_Complement", "test_latex_Complexes", "test_latex_productset", "test_latex_Naturals", "test_latex_Naturals0", "test_latex_Integers", "test_latex_ImageSet", "test_latex_ConditionSet", "test_latex_ComplexRegion", "test_latex_Contains", "test_latex_sum", "test_latex_product", "test_latex_limits", "test_latex_log", "test_issue_3568", "test_latex", "test_latex_dict", "test_latex_list", "test_latex_rational", "test_latex_inverse", "test_latex_DiracDelta", "test_latex_Heaviside", "test_latex_KroneckerDelta", "test_latex_LeviCivita", "test_mode", "test_latex_Piecewise", "test_latex_Matrix", "test_latex_matrix_with_functions", "test_latex_NDimArray", "test_latex_mul_symbol", "test_latex_issue_4381", "test_latex_issue_4576", "test_latex_pow_fraction", "test_noncommutative", "test_latex_order", "test_latex_Lambda", "test_latex_PolyElement", "test_latex_FracElement", "test_latex_Poly", "test_latex_Poly_order", "test_latex_ComplexRootOf", "test_latex_RootSum", "test_settings", "test_latex_numbers", "test_latex_euler", "test_lamda", "test_custom_symbol_names", "test_matAdd", "test_matMul", "test_latex_MatrixSlice", "test_latex_RandomDomain", "test_PrettyPoly", "test_integral_transforms", "test_PolynomialRingBase", "test_categories", "test_Modules", "test_QuotientRing", "test_Tr", "test_Adjoint", "test_Hadamard", "test_ZeroMatrix", "test_boolean_args_order", "test_imaginary", "test_builtins_without_args", "test_latex_greek_functions", "test_translate", "test_other_symbols", "test_modifiers", "test_greek_symbols", "test_builtin_no_args", "test_issue_6853", "test_Mul", "test_Pow", "test_issue_7180", "test_issue_8409", "test_issue_7117", "test_issue_15439", "test_issue_2934", "test_issue_10489", "test_issue_12886", "test_issue_13651", "test_latex_UnevaluatedExpr", "test_MatrixSymbol_printing", "test_Quaternion_latex_printing", "test_TensorProduct_printing", "test_WedgeProduct_printing", "test_issue_14041", "test_issue_9216", "test_latex_printer_tensor", "test_trace"]

**Base Commit**: 15f56f3b0006d2ed2c29bde3c43e91618012c849
**Environment Setup Commit**: 73b3f90093754c5ed1561bd885242330e3583004
