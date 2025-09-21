# sympy__sympy-15308

**Repository**: sympy/sympy
**Created**: 2018-09-28T16:42:11Z
**Version**: 1.4

## Problem Statement

LaTeX printing for Matrix Expression
```py
>>> A = MatrixSymbol("A", n, n)
>>> latex(trace(A**2))
'Trace(A**2)'
```

The bad part is not only is Trace not recognized, but whatever printer is being used doesn't fallback to the LaTeX printer for the inner expression (it should be `A^2`). 


## Hints

What is the correct way to print the trace? AFAIK there isn't one built in to Latex. One option is ```\mathrm{Tr}```. Or ```\operatorname{Tr}```.
What's the difference between the two. It looks like we use both in different parts of the latex printer. 
\operatorname puts a thin space after the operator.

## Patch

```diff

diff --git a/sympy/printing/latex.py b/sympy/printing/latex.py
--- a/sympy/printing/latex.py
+++ b/sympy/printing/latex.py
@@ -289,6 +289,10 @@ def _do_exponent(self, expr, exp):
         else:
             return expr
 
+    def _print_Basic(self, expr):
+        l = [self._print(o) for o in expr.args]
+        return self._deal_with_super_sub(expr.__class__.__name__) + r"\left(%s\right)" % ", ".join(l)
+
     def _print_bool(self, e):
         return r"\mathrm{%s}" % e
 
@@ -1462,6 +1466,10 @@ def _print_Transpose(self, expr):
         else:
             return "%s^T" % self._print(mat)
 
+    def _print_Trace(self, expr):
+        mat = expr.arg
+        return r"\mathrm{tr}\left (%s \right )" % self._print(mat)
+
     def _print_Adjoint(self, expr):
         mat = expr.arg
         from sympy.matrices import MatrixSymbol


```

## Test Patch

```diff
diff --git a/sympy/printing/tests/test_latex.py b/sympy/printing/tests/test_latex.py
--- a/sympy/printing/tests/test_latex.py
+++ b/sympy/printing/tests/test_latex.py
@@ -1866,3 +1866,35 @@ def test_latex_printer_tensor():
 
     expr = TensorElement(K(i,j,-k,-l), {i:3})
     assert latex(expr) == 'K{}^{i=3,j}{}_{kl}'
+
+
+def test_trace():
+    # Issue 15303
+    from sympy import trace
+    A = MatrixSymbol("A", 2, 2)
+    assert latex(trace(A)) == r"\mathrm{tr}\left (A \right )"
+    assert latex(trace(A**2)) == r"\mathrm{tr}\left (A^{2} \right )"
+
+
+def test_print_basic():
+    # Issue 15303
+    from sympy import Basic, Expr
+
+    # dummy class for testing printing where the function is not implemented in latex.py
+    class UnimplementedExpr(Expr):
+        def __new__(cls, e):
+            return Basic.__new__(cls, e)
+
+    # dummy function for testing
+    def unimplemented_expr(expr):
+        return UnimplementedExpr(expr).doit()
+
+    # override class name to use superscript / subscript
+    def unimplemented_expr_sup_sub(expr):
+        result = UnimplementedExpr(expr)
+        result.__class__.__name__ = 'UnimplementedExpr_x^1'
+        return result
+
+    assert latex(unimplemented_expr(x)) == r'UnimplementedExpr\left(x\right)'
+    assert latex(unimplemented_expr(x**2)) == r'UnimplementedExpr\left(x^{2}\right)'
+    assert latex(unimplemented_expr_sup_sub(x)) == r'UnimplementedExpr^{1}_{x}\left(x\right)'

```

## Test Information

**Tests that should FAIL→PASS**: ["test_trace"]

**Tests that should PASS→PASS**: ["test_printmethod", "test_latex_basic", "test_latex_builtins", "test_latex_SingularityFunction", "test_latex_cycle", "test_latex_permutation", "test_latex_Float", "test_latex_vector_expressions", "test_latex_symbols", "test_latex_functions", "test_function_subclass_different_name", "test_hyper_printing", "test_latex_bessel", "test_latex_fresnel", "test_latex_brackets", "test_latex_indexed", "test_latex_derivatives", "test_latex_subs", "test_latex_integrals", "test_latex_sets", "test_latex_SetExpr", "test_latex_Range", "test_latex_sequences", "test_latex_FourierSeries", "test_latex_FormalPowerSeries", "test_latex_intervals", "test_latex_AccumuBounds", "test_latex_emptyset", "test_latex_commutator", "test_latex_union", "test_latex_symmetric_difference", "test_latex_Complement", "test_latex_Complexes", "test_latex_productset", "test_latex_Naturals", "test_latex_Naturals0", "test_latex_Integers", "test_latex_ImageSet", "test_latex_ConditionSet", "test_latex_ComplexRegion", "test_latex_Contains", "test_latex_sum", "test_latex_product", "test_latex_limits", "test_latex_log", "test_issue_3568", "test_latex", "test_latex_dict", "test_latex_list", "test_latex_rational", "test_latex_inverse", "test_latex_DiracDelta", "test_latex_Heaviside", "test_latex_KroneckerDelta", "test_latex_LeviCivita", "test_mode", "test_latex_Piecewise", "test_latex_Matrix", "test_latex_matrix_with_functions", "test_latex_NDimArray", "test_latex_mul_symbol", "test_latex_issue_4381", "test_latex_issue_4576", "test_latex_pow_fraction", "test_noncommutative", "test_latex_order", "test_latex_Lambda", "test_latex_PolyElement", "test_latex_FracElement", "test_latex_Poly", "test_latex_Poly_order", "test_latex_ComplexRootOf", "test_latex_RootSum", "test_settings", "test_latex_numbers", "test_latex_euler", "test_lamda", "test_custom_symbol_names", "test_matAdd", "test_matMul", "test_latex_MatrixSlice", "test_latex_RandomDomain", "test_PrettyPoly", "test_integral_transforms", "test_PolynomialRingBase", "test_categories", "test_Modules", "test_QuotientRing", "test_Tr", "test_Adjoint", "test_Hadamard", "test_ZeroMatrix", "test_boolean_args_order", "test_imaginary", "test_builtins_without_args", "test_latex_greek_functions", "test_translate", "test_other_symbols", "test_modifiers", "test_greek_symbols", "test_builtin_no_args", "test_issue_6853", "test_Mul", "test_Pow", "test_issue_7180", "test_issue_8409", "test_issue_7117", "test_issue_2934", "test_issue_10489", "test_issue_12886", "test_issue_13651", "test_latex_UnevaluatedExpr", "test_MatrixElement_printing", "test_MatrixSymbol_printing", "test_Quaternion_latex_printing", "test_TensorProduct_printing", "test_WedgeProduct_printing", "test_issue_14041", "test_issue_9216", "test_latex_printer_tensor"]

**Base Commit**: fb59d703e6863ed803c98177b59197b5513332e9
**Environment Setup Commit**: 73b3f90093754c5ed1561bd885242330e3583004
