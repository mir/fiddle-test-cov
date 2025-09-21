# sympy__sympy-14317

**Repository**: sympy/sympy
**Created**: 2018-02-24T10:05:10Z
**Version**: 1.1

## Problem Statement

LaTeX printer does not use the same order of monomials as pretty and str 
When printing a Poly, the str and pretty printers use the logical order of monomials, from highest to lowest degrees. But latex printer does not. 
```
>>> var('a b c x')
>>> p = Poly([a, 1, b, 2, c, 3], x)
>>> p
Poly(a*x**5 + x**4 + b*x**3 + 2*x**2 + c*x + 3, x, domain='ZZ[a,b,c]')
>>> pretty(p)
"Poly(a*x**5 + x**4 + b*x**3 + 2*x**2 + c*x + 3, x, domain='ZZ[a,b,c]')"
>>> latex(p)
'\\operatorname{Poly}{\\left( a x^{5} + b x^{3} + c x + x^{4} + 2 x^{2} + 3, x, domain=\\mathbb{Z}\\left[a, b, c\\right] \\right)}'
```


## Patch

```diff

diff --git a/sympy/printing/latex.py b/sympy/printing/latex.py
--- a/sympy/printing/latex.py
+++ b/sympy/printing/latex.py
@@ -1813,7 +1813,50 @@ def _print_PolynomialRingBase(self, expr):
 
     def _print_Poly(self, poly):
         cls = poly.__class__.__name__
-        expr = self._print(poly.as_expr())
+        terms = []
+        for monom, coeff in poly.terms():
+            s_monom = ''
+            for i, exp in enumerate(monom):
+                if exp > 0:
+                    if exp == 1:
+                        s_monom += self._print(poly.gens[i])
+                    else:
+                        s_monom += self._print(pow(poly.gens[i], exp))
+
+            if coeff.is_Add:
+                if s_monom:
+                    s_coeff = r"\left(%s\right)" % self._print(coeff)
+                else:
+                    s_coeff = self._print(coeff)
+            else:
+                if s_monom:
+                    if coeff is S.One:
+                        terms.extend(['+', s_monom])
+                        continue
+
+                    if coeff is S.NegativeOne:
+                        terms.extend(['-', s_monom])
+                        continue
+
+                s_coeff = self._print(coeff)
+
+            if not s_monom:
+                s_term = s_coeff
+            else:
+                s_term = s_coeff + " " + s_monom
+
+            if s_term.startswith('-'):
+                terms.extend(['-', s_term[1:]])
+            else:
+                terms.extend(['+', s_term])
+
+        if terms[0] in ['-', '+']:
+            modifier = terms.pop(0)
+
+            if modifier == '-':
+                terms[0] = '-' + terms[0]
+
+        expr = ' '.join(terms)
         gens = list(map(self._print, poly.gens))
         domain = "domain=%s" % self._print(poly.get_domain())
 


```

## Test Patch

```diff
diff --git a/sympy/printing/tests/test_latex.py b/sympy/printing/tests/test_latex.py
--- a/sympy/printing/tests/test_latex.py
+++ b/sympy/printing/tests/test_latex.py
@@ -1132,11 +1132,20 @@ def test_latex_Poly():
     assert latex(Poly(x**2 + 2 * x, x)) == \
         r"\operatorname{Poly}{\left( x^{2} + 2 x, x, domain=\mathbb{Z} \right)}"
     assert latex(Poly(x/y, x)) == \
-        r"\operatorname{Poly}{\left( \frac{x}{y}, x, domain=\mathbb{Z}\left(y\right) \right)}"
+        r"\operatorname{Poly}{\left( \frac{1}{y} x, x, domain=\mathbb{Z}\left(y\right) \right)}"
     assert latex(Poly(2.0*x + y)) == \
         r"\operatorname{Poly}{\left( 2.0 x + 1.0 y, x, y, domain=\mathbb{R} \right)}"
 
 
+def test_latex_Poly_order():
+    assert latex(Poly([a, 1, b, 2, c, 3], x)) == \
+        '\\operatorname{Poly}{\\left( a x^{5} + x^{4} + b x^{3} + 2 x^{2} + c x + 3, x, domain=\\mathbb{Z}\\left[a, b, c\\right] \\right)}'
+    assert latex(Poly([a, 1, b+c, 2, 3], x)) == \
+        '\\operatorname{Poly}{\\left( a x^{4} + x^{3} + \\left(b + c\\right) x^{2} + 2 x + 3, x, domain=\\mathbb{Z}\\left[a, b, c\\right] \\right)}'
+    assert latex(Poly(a*x**3 + x**2*y - x*y - c*y**3 - b*x*y**2 + y - a*x + b, (x, y))) == \
+        '\\operatorname{Poly}{\\left( a x^{3} + x^{2}y -  b xy^{2} - xy -  a x -  c y^{3} + y + b, x, y, domain=\\mathbb{Z}\\left[a, b, c\\right] \\right)}'
+
+
 def test_latex_ComplexRootOf():
     assert latex(rootof(x**5 + x + 3, 0)) == \
         r"\operatorname{CRootOf} {\left(x^{5} + x + 3, 0\right)}"

```

## Test Information

**Tests that should FAIL→PASS**: ["test_latex_Poly", "test_latex_Poly_order"]

**Tests that should PASS→PASS**: ["test_printmethod", "test_latex_basic", "test_latex_builtins", "test_latex_SingularityFunction", "test_latex_cycle", "test_latex_permutation", "test_latex_Float", "test_latex_vector_expressions", "test_latex_symbols", "test_latex_functions", "test_function_subclass_different_name", "test_hyper_printing", "test_latex_bessel", "test_latex_fresnel", "test_latex_brackets", "test_latex_indexed", "test_latex_derivatives", "test_latex_subs", "test_latex_integrals", "test_latex_sets", "test_latex_SetExpr", "test_latex_Range", "test_latex_sequences", "test_latex_FourierSeries", "test_latex_FormalPowerSeries", "test_latex_intervals", "test_latex_AccumuBounds", "test_latex_emptyset", "test_latex_commutator", "test_latex_union", "test_latex_symmetric_difference", "test_latex_Complement", "test_latex_Complexes", "test_latex_productset", "test_latex_Naturals", "test_latex_Naturals0", "test_latex_Integers", "test_latex_ImageSet", "test_latex_ConditionSet", "test_latex_ComplexRegion", "test_latex_Contains", "test_latex_sum", "test_latex_product", "test_latex_limits", "test_latex_log", "test_issue_3568", "test_latex", "test_latex_dict", "test_latex_list", "test_latex_rational", "test_latex_inverse", "test_latex_DiracDelta", "test_latex_Heaviside", "test_latex_KroneckerDelta", "test_latex_LeviCivita", "test_mode", "test_latex_Piecewise", "test_latex_Matrix", "test_latex_matrix_with_functions", "test_latex_NDimArray", "test_latex_mul_symbol", "test_latex_issue_4381", "test_latex_issue_4576", "test_latex_pow_fraction", "test_noncommutative", "test_latex_order", "test_latex_Lambda", "test_latex_PolyElement", "test_latex_FracElement", "test_latex_ComplexRootOf", "test_latex_RootSum", "test_settings", "test_latex_numbers", "test_latex_euler", "test_lamda", "test_custom_symbol_names", "test_matAdd", "test_matMul", "test_latex_MatrixSlice", "test_latex_RandomDomain", "test_PrettyPoly", "test_integral_transforms", "test_PolynomialRingBase", "test_categories", "test_Modules", "test_QuotientRing", "test_Tr", "test_Adjoint", "test_Hadamard", "test_ZeroMatrix", "test_boolean_args_order", "test_imaginary", "test_builtins_without_args", "test_latex_greek_functions", "test_translate", "test_other_symbols", "test_modifiers", "test_greek_symbols", "test_builtin_no_args", "test_issue_6853", "test_Mul", "test_Pow", "test_issue_7180", "test_issue_8409", "test_issue_7117", "test_issue_2934", "test_issue_10489", "test_issue_12886", "test_issue_13651", "test_latex_UnevaluatedExpr", "test_MatrixElement_printing", "test_MatrixSymbol_printing", "test_Quaternion_latex_printing", "test_TensorProduct_printing", "test_WedgeProduct_printing", "test_units"]

**Base Commit**: fb536869fb7aa28b2695ad7a3b70949926b291c4
**Environment Setup Commit**: ec9e3c0436fbff934fa84e22bf07f1b3ef5bfac3
