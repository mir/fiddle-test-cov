# sympy__sympy-21171

**Repository**: sympy/sympy
**Created**: 2021-03-26T07:48:35Z
**Version**: 1.8

## Problem Statement

_print_SingularityFunction() got an unexpected keyword argument 'exp'
On a Jupyter Notebook cell, type the following:

```python
from sympy import *
from sympy.physics.continuum_mechanics import Beam
# Young's modulus
E = symbols("E")
# length of the beam
L = symbols("L")
# concentrated load at the end tip of the beam
F = symbols("F")
# square cross section
B, H = symbols("B, H")
I = B * H**3 / 12
# numerical values (material: steel)
d = {B: 1e-02, H: 1e-02, E: 210e09, L: 0.2, F: 100}

b2 = Beam(L, E, I)
b2.apply_load(-F, L / 2, -1)
b2.apply_support(0, "fixed")
R0, M0 = symbols("R_0, M_0")
b2.solve_for_reaction_loads(R0, M0)
```

Then:

```
b2.shear_force()
```

The following error appears:
```
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
/usr/local/lib/python3.8/dist-packages/IPython/core/formatters.py in __call__(self, obj)
    343             method = get_real_method(obj, self.print_method)
    344             if method is not None:
--> 345                 return method()
    346             return None
    347         else:

/usr/local/lib/python3.8/dist-packages/sympy/interactive/printing.py in _print_latex_png(o)
    184         """
    185         if _can_print(o):
--> 186             s = latex(o, mode=latex_mode, **settings)
    187             if latex_mode == 'plain':
    188                 s = '$\\displaystyle %s$' % s

/usr/local/lib/python3.8/dist-packages/sympy/printing/printer.py in __call__(self, *args, **kwargs)
    371 
    372     def __call__(self, *args, **kwargs):
--> 373         return self.__wrapped__(*args, **kwargs)
    374 
    375     @property

/usr/local/lib/python3.8/dist-packages/sympy/printing/latex.py in latex(expr, **settings)
   2913 
   2914     """
-> 2915     return LatexPrinter(settings).doprint(expr)
   2916 
   2917 

/usr/local/lib/python3.8/dist-packages/sympy/printing/latex.py in doprint(self, expr)
    252 
    253     def doprint(self, expr):
--> 254         tex = Printer.doprint(self, expr)
    255 
    256         if self._settings['mode'] == 'plain':

/usr/local/lib/python3.8/dist-packages/sympy/printing/printer.py in doprint(self, expr)
    289     def doprint(self, expr):
    290         """Returns printer's representation for expr (as a string)"""
--> 291         return self._str(self._print(expr))
    292 
    293     def _print(self, expr, **kwargs):

/usr/local/lib/python3.8/dist-packages/sympy/printing/printer.py in _print(self, expr, **kwargs)
    327                 printmethod = '_print_' + cls.__name__
    328                 if hasattr(self, printmethod):
--> 329                     return getattr(self, printmethod)(expr, **kwargs)
    330             # Unknown object, fall back to the emptyPrinter.
    331             return self.emptyPrinter(expr)

/usr/local/lib/python3.8/dist-packages/sympy/printing/latex.py in _print_Add(self, expr, order)
    381             else:
    382                 tex += " + "
--> 383             term_tex = self._print(term)
    384             if self._needs_add_brackets(term):
    385                 term_tex = r"\left(%s\right)" % term_tex

/usr/local/lib/python3.8/dist-packages/sympy/printing/printer.py in _print(self, expr, **kwargs)
    327                 printmethod = '_print_' + cls.__name__
    328                 if hasattr(self, printmethod):
--> 329                     return getattr(self, printmethod)(expr, **kwargs)
    330             # Unknown object, fall back to the emptyPrinter.
    331             return self.emptyPrinter(expr)

/usr/local/lib/python3.8/dist-packages/sympy/printing/latex.py in _print_Mul(self, expr)
    565             # use the original expression here, since fraction() may have
    566             # altered it when producing numer and denom
--> 567             tex += convert(expr)
    568 
    569         else:

/usr/local/lib/python3.8/dist-packages/sympy/printing/latex.py in convert(expr)
    517                                isinstance(x.base, Quantity)))
    518 
--> 519                 return convert_args(args)
    520 
    521         def convert_args(args):

/usr/local/lib/python3.8/dist-packages/sympy/printing/latex.py in convert_args(args)
    523 
    524                 for i, term in enumerate(args):
--> 525                     term_tex = self._print(term)
    526 
    527                     if self._needs_mul_brackets(term, first=(i == 0),

/usr/local/lib/python3.8/dist-packages/sympy/printing/printer.py in _print(self, expr, **kwargs)
    327                 printmethod = '_print_' + cls.__name__
    328                 if hasattr(self, printmethod):
--> 329                     return getattr(self, printmethod)(expr, **kwargs)
    330             # Unknown object, fall back to the emptyPrinter.
    331             return self.emptyPrinter(expr)

/usr/local/lib/python3.8/dist-packages/sympy/printing/latex.py in _print_Add(self, expr, order)
    381             else:
    382                 tex += " + "
--> 383             term_tex = self._print(term)
    384             if self._needs_add_brackets(term):
    385                 term_tex = r"\left(%s\right)" % term_tex

/usr/local/lib/python3.8/dist-packages/sympy/printing/printer.py in _print(self, expr, **kwargs)
    327                 printmethod = '_print_' + cls.__name__
    328                 if hasattr(self, printmethod):
--> 329                     return getattr(self, printmethod)(expr, **kwargs)
    330             # Unknown object, fall back to the emptyPrinter.
    331             return self.emptyPrinter(expr)

/usr/local/lib/python3.8/dist-packages/sympy/printing/latex.py in _print_Mul(self, expr)
    569         else:
    570             snumer = convert(numer)
--> 571             sdenom = convert(denom)
    572             ldenom = len(sdenom.split())
    573             ratio = self._settings['long_frac_ratio']

/usr/local/lib/python3.8/dist-packages/sympy/printing/latex.py in convert(expr)
    505         def convert(expr):
    506             if not expr.is_Mul:
--> 507                 return str(self._print(expr))
    508             else:
    509                 if self.order not in ('old', 'none'):

/usr/local/lib/python3.8/dist-packages/sympy/printing/printer.py in _print(self, expr, **kwargs)
    327                 printmethod = '_print_' + cls.__name__
    328                 if hasattr(self, printmethod):
--> 329                     return getattr(self, printmethod)(expr, **kwargs)
    330             # Unknown object, fall back to the emptyPrinter.
    331             return self.emptyPrinter(expr)

/usr/local/lib/python3.8/dist-packages/sympy/printing/latex.py in _print_Add(self, expr, order)
    381             else:
    382                 tex += " + "
--> 383             term_tex = self._print(term)
    384             if self._needs_add_brackets(term):
    385                 term_tex = r"\left(%s\right)" % term_tex

/usr/local/lib/python3.8/dist-packages/sympy/printing/printer.py in _print(self, expr, **kwargs)
    327                 printmethod = '_print_' + cls.__name__
    328                 if hasattr(self, printmethod):
--> 329                     return getattr(self, printmethod)(expr, **kwargs)
    330             # Unknown object, fall back to the emptyPrinter.
    331             return self.emptyPrinter(expr)

/usr/local/lib/python3.8/dist-packages/sympy/printing/latex.py in _print_Pow(self, expr)
    649         else:
    650             if expr.base.is_Function:
--> 651                 return self._print(expr.base, exp=self._print(expr.exp))
    652             else:
    653                 tex = r"%s^{%s}"

/usr/local/lib/python3.8/dist-packages/sympy/printing/printer.py in _print(self, expr, **kwargs)
    327                 printmethod = '_print_' + cls.__name__
    328                 if hasattr(self, printmethod):
--> 329                     return getattr(self, printmethod)(expr, **kwargs)
    330             # Unknown object, fall back to the emptyPrinter.
    331             return self.emptyPrinter(expr)

TypeError: _print_SingularityFunction() got an unexpected keyword argument 'exp'
```


## Hints

Could you provide a fully working example? Copying and pasting your code leaves a number of non-defined variables. Thanks for the report.
@moorepants Sorry for that, I've just updated the code in the original post.
This is the string printed version from `b2..shear_force()`:

```
Out[5]: -F*SingularityFunction(x, L/2, 0) + (F*SingularityFunction(L, 0, -1)*SingularityFunction(L, L/2, 1)/(SingularityFunction(L, 0, -1)*SingularityFunction(L, 0, 1) - SingularityFunction(L, 0, 0)**2) - F*SingularityFunction(L, 0, 0)*SingularityFunction(L, L/2, 0)/(SingularityFunction(L, 0, -1)*SingularityFunction(L, 0, 1) - SingularityFunction(L, 0, 0)**2))*SingularityFunction(x, 0, 0) + (-F*SingularityFunction(L, 0, 0)*SingularityFunction(L, L/2, 1)/(SingularityFunction(L, 0, -1)*SingularityFunction(L, 0, 1) - SingularityFunction(L, 0, 0)**2) + F*SingularityFunction(L, 0, 1)*SingularityFunction(L, L/2, 0)/(SingularityFunction(L, 0, -1)*SingularityFunction(L, 0, 1) - SingularityFunction(L, 0, 0)**2))*SingularityFunction(x, 0, -1)
```
Yes works correctly if you print the string. It throws the error when you display the expression on a jupyter notebook with latex
It errors on this term: `SingularityFunction(L, 0, 0)**2`. For some reasons the latex printer fails on printing a singularity function raised to a power.

## Patch

```diff

diff --git a/sympy/printing/latex.py b/sympy/printing/latex.py
--- a/sympy/printing/latex.py
+++ b/sympy/printing/latex.py
@@ -1968,10 +1968,12 @@ def _print_DiracDelta(self, expr, exp=None):
             tex = r"\left(%s\right)^{%s}" % (tex, exp)
         return tex
 
-    def _print_SingularityFunction(self, expr):
+    def _print_SingularityFunction(self, expr, exp=None):
         shift = self._print(expr.args[0] - expr.args[1])
         power = self._print(expr.args[2])
         tex = r"{\left\langle %s \right\rangle}^{%s}" % (shift, power)
+        if exp is not None:
+            tex = r"{\left({\langle %s \rangle}^{%s}\right)}^{%s}" % (shift, power, exp)
         return tex
 
     def _print_Heaviside(self, expr, exp=None):


```

## Test Patch

```diff
diff --git a/sympy/printing/tests/test_latex.py b/sympy/printing/tests/test_latex.py
--- a/sympy/printing/tests/test_latex.py
+++ b/sympy/printing/tests/test_latex.py
@@ -214,6 +214,19 @@ def test_latex_SingularityFunction():
     assert latex(SingularityFunction(x, 4, -1)) == \
         r"{\left\langle x - 4 \right\rangle}^{-1}"
 
+    assert latex(SingularityFunction(x, 4, 5)**3) == \
+        r"{\left({\langle x - 4 \rangle}^{5}\right)}^{3}"
+    assert latex(SingularityFunction(x, -3, 4)**3) == \
+        r"{\left({\langle x + 3 \rangle}^{4}\right)}^{3}"
+    assert latex(SingularityFunction(x, 0, 4)**3) == \
+        r"{\left({\langle x \rangle}^{4}\right)}^{3}"
+    assert latex(SingularityFunction(x, a, n)**3) == \
+        r"{\left({\langle - a + x \rangle}^{n}\right)}^{3}"
+    assert latex(SingularityFunction(x, 4, -2)**3) == \
+        r"{\left({\langle x - 4 \rangle}^{-2}\right)}^{3}"
+    assert latex((SingularityFunction(x, 4, -1)**3)**3) == \
+        r"{\left({\langle x - 4 \rangle}^{-1}\right)}^{9}"
+
 
 def test_latex_cycle():
     assert latex(Cycle(1, 2, 4)) == r"\left( 1\; 2\; 4\right)"

```

## Test Information

**Tests that should FAIL→PASS**: ["test_latex_SingularityFunction"]

**Tests that should PASS→PASS**: ["test_printmethod", "test_latex_basic", "test_latex_builtins", "test_latex_cycle", "test_latex_permutation", "test_latex_Float", "test_latex_vector_expressions", "test_latex_symbols", "test_latex_functions", "test_function_subclass_different_name", "test_hyper_printing", "test_latex_bessel", "test_latex_fresnel", "test_latex_brackets", "test_latex_indexed", "test_latex_derivatives", "test_latex_subs", "test_latex_integrals", "test_latex_sets", "test_latex_SetExpr", "test_latex_Range", "test_latex_sequences", "test_latex_FourierSeries", "test_latex_FormalPowerSeries", "test_latex_intervals", "test_latex_AccumuBounds", "test_latex_emptyset", "test_latex_universalset", "test_latex_commutator", "test_latex_union", "test_latex_intersection", "test_latex_symmetric_difference", "test_latex_Complement", "test_latex_productset", "test_set_operators_parenthesis", "test_latex_Complexes", "test_latex_Naturals", "test_latex_Naturals0", "test_latex_Integers", "test_latex_ImageSet", "test_latex_ConditionSet", "test_latex_ComplexRegion", "test_latex_Contains", "test_latex_sum", "test_latex_product", "test_latex_limits", "test_latex_log", "test_issue_3568", "test_latex", "test_latex_dict", "test_latex_list", "test_latex_rational", "test_latex_inverse", "test_latex_DiracDelta", "test_latex_Heaviside", "test_latex_KroneckerDelta", "test_latex_LeviCivita", "test_mode", "test_latex_mathieu", "test_latex_Piecewise", "test_latex_Matrix", "test_latex_matrix_with_functions", "test_latex_NDimArray", "test_latex_mul_symbol", "test_latex_issue_4381", "test_latex_issue_4576", "test_latex_pow_fraction", "test_noncommutative", "test_latex_order", "test_latex_Lambda", "test_latex_PolyElement", "test_latex_FracElement", "test_latex_Poly", "test_latex_Poly_order", "test_latex_ComplexRootOf", "test_latex_RootSum", "test_settings", "test_latex_numbers", "test_latex_euler", "test_lamda", "test_custom_symbol_names", "test_matAdd", "test_matMul", "test_latex_MatrixSlice", "test_latex_RandomDomain", "test_PrettyPoly", "test_integral_transforms", "test_PolynomialRingBase", "test_categories", "test_Modules", "test_QuotientRing", "test_Tr", "test_Adjoint", "test_Transpose", "test_Hadamard", "test_ElementwiseApplyFunction", "test_ZeroMatrix", "test_OneMatrix", "test_Identity", "test_boolean_args_order", "test_imaginary", "test_builtins_without_args", "test_latex_greek_functions", "test_translate", "test_other_symbols", "test_modifiers", "test_greek_symbols", "test_fancyset_symbols", "test_builtin_no_args", "test_issue_6853", "test_Mul", "test_Pow", "test_issue_7180", "test_issue_8409", "test_issue_8470", "test_issue_15439", "test_issue_2934", "test_issue_10489", "test_issue_12886", "test_issue_13559", "test_issue_13651", "test_latex_UnevaluatedExpr", "test_MatrixElement_printing", "test_MatrixSymbol_printing", "test_KroneckerProduct_printing", "test_Series_printing", "test_TransferFunction_printing", "test_Parallel_printing", "test_Feedback_printing", "test_Quaternion_latex_printing", "test_TensorProduct_printing", "test_WedgeProduct_printing", "test_issue_9216", "test_latex_printer_tensor", "test_multiline_latex", "test_issue_15353", "test_trace", "test_print_basic", "test_MatrixSymbol_bold", "test_AppliedPermutation", "test_PermutationMatrix", "test_imaginary_unit", "test_text_re_im", "test_latex_diffgeom", "test_unit_printing", "test_issue_17092", "test_latex_decimal_separator", "test_Str", "test_latex_escape", "test_emptyPrinter", "test_global_settings", "test_pickleable"]

**Base Commit**: aa22709cb7df2d7503803d4b2c0baa7aa21440b6
**Environment Setup Commit**: 3ac1464b8840d5f8b618a654f9fbf09c452fe969
