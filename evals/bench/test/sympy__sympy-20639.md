# sympy__sympy-20639

**Repository**: sympy/sympy
**Created**: 2020-12-21T07:42:53Z
**Version**: 1.8

## Problem Statement

inaccurate rendering of pi**(1/E)
This claims to be version 1.5.dev; I just merged from the project master, so I hope this is current.  I didn't notice this bug among others in printing.pretty.

```
In [52]: pi**(1/E)                                                               
Out[52]: 
-1___
╲╱ π 

```
LaTeX and str not fooled:
```
In [53]: print(latex(pi**(1/E)))                                                 
\pi^{e^{-1}}

In [54]: str(pi**(1/E))                                                          
Out[54]: 'pi**exp(-1)'
```



## Hints

I can confirm this bug on master. Looks like it's been there a while
https://github.com/sympy/sympy/blob/2d700c4b3c0871a26741456787b0555eed9d5546/sympy/printing/pretty/pretty.py#L1814

`1/E` is `exp(-1)` which has totally different arg structure than something like `1/pi`:

```
>>> (1/E).args
(-1,)
>>> (1/pi).args
(pi, -1)
```
@ethankward nice!  Also, the use of `str` there isn't correct:
```
>>> pprint(7**(1/(pi)))                                                                                                                                                          
pi___
╲╱ 7 

>>> pprint(pi**(1/(pi)))                                                                                                                                                        
pi___
╲╱ π 

>>> pprint(pi**(1/(EulerGamma)))                                                                                                                                                
EulerGamma___
        ╲╱ π 
```
(`pi` and `EulerGamma` were not pretty printed)
I guess str is used because it's hard to put 2-D stuff in the corner of the radical like that. But I think it would be better to recursively call the pretty printer, and if it is multiline, or maybe even if it is a more complicated expression than just a single number or symbol name, then print it without the radical like

```
  1
  ─
  e
π
```

or

```
 ⎛ -1⎞
 ⎝e  ⎠
π

## Patch

```diff

diff --git a/sympy/printing/pretty/pretty.py b/sympy/printing/pretty/pretty.py
--- a/sympy/printing/pretty/pretty.py
+++ b/sympy/printing/pretty/pretty.py
@@ -1902,12 +1902,12 @@ def _print_Mul(self, product):
             return prettyForm.__mul__(*a)/prettyForm.__mul__(*b)
 
     # A helper function for _print_Pow to print x**(1/n)
-    def _print_nth_root(self, base, expt):
+    def _print_nth_root(self, base, root):
         bpretty = self._print(base)
 
         # In very simple cases, use a single-char root sign
         if (self._settings['use_unicode_sqrt_char'] and self._use_unicode
-            and expt is S.Half and bpretty.height() == 1
+            and root == 2 and bpretty.height() == 1
             and (bpretty.width() == 1
                  or (base.is_Integer and base.is_nonnegative))):
             return prettyForm(*bpretty.left('\N{SQUARE ROOT}'))
@@ -1915,14 +1915,13 @@ def _print_nth_root(self, base, expt):
         # Construct root sign, start with the \/ shape
         _zZ = xobj('/', 1)
         rootsign = xobj('\\', 1) + _zZ
-        # Make exponent number to put above it
-        if isinstance(expt, Rational):
-            exp = str(expt.q)
-            if exp == '2':
-                exp = ''
-        else:
-            exp = str(expt.args[0])
-        exp = exp.ljust(2)
+        # Constructing the number to put on root
+        rpretty = self._print(root)
+        # roots look bad if they are not a single line
+        if rpretty.height() != 1:
+            return self._print(base)**self._print(1/root)
+        # If power is half, no number should appear on top of root sign
+        exp = '' if root == 2 else str(rpretty).ljust(2)
         if len(exp) > 2:
             rootsign = ' '*(len(exp) - 2) + rootsign
         # Stack the exponent
@@ -1954,8 +1953,9 @@ def _print_Pow(self, power):
             if e is S.NegativeOne:
                 return prettyForm("1")/self._print(b)
             n, d = fraction(e)
-            if n is S.One and d.is_Atom and not e.is_Integer and self._settings['root_notation']:
-                return self._print_nth_root(b, e)
+            if n is S.One and d.is_Atom and not e.is_Integer and (e.is_Rational or d.is_Symbol) \
+                    and self._settings['root_notation']:
+                return self._print_nth_root(b, d)
             if e.is_Rational and e < 0:
                 return prettyForm("1")/self._print(Pow(b, -e, evaluate=False))
 


```

## Test Patch

```diff
diff --git a/sympy/printing/pretty/tests/test_pretty.py b/sympy/printing/pretty/tests/test_pretty.py
--- a/sympy/printing/pretty/tests/test_pretty.py
+++ b/sympy/printing/pretty/tests/test_pretty.py
@@ -5942,7 +5942,11 @@ def test_PrettyPoly():
 
 def test_issue_6285():
     assert pretty(Pow(2, -5, evaluate=False)) == '1 \n--\n 5\n2 '
-    assert pretty(Pow(x, (1/pi))) == 'pi___\n\\/ x '
+    assert pretty(Pow(x, (1/pi))) == \
+    ' 1 \n'\
+    ' --\n'\
+    ' pi\n'\
+    'x  '
 
 
 def test_issue_6359():
@@ -7205,6 +7209,51 @@ def test_is_combining():
         [False, True, False, False]
 
 
+def test_issue_17616():
+    assert pretty(pi**(1/exp(1))) == \
+   '  / -1\\\n'\
+   '  \e  /\n'\
+   'pi     '
+
+    assert upretty(pi**(1/exp(1))) == \
+   ' ⎛ -1⎞\n'\
+   ' ⎝ℯ  ⎠\n'\
+   'π     '
+
+    assert pretty(pi**(1/pi)) == \
+    '  1 \n'\
+    '  --\n'\
+    '  pi\n'\
+    'pi  '
+
+    assert upretty(pi**(1/pi)) == \
+    ' 1\n'\
+    ' ─\n'\
+    ' π\n'\
+    'π '
+
+    assert pretty(pi**(1/EulerGamma)) == \
+    '      1     \n'\
+    '  ----------\n'\
+    '  EulerGamma\n'\
+    'pi          '
+
+    assert upretty(pi**(1/EulerGamma)) == \
+    ' 1\n'\
+    ' ─\n'\
+    ' γ\n'\
+    'π '
+
+    z = Symbol("x_17")
+    assert upretty(7**(1/z)) == \
+    'x₁₇___\n'\
+    ' ╲╱ 7 '
+
+    assert pretty(7**(1/z)) == \
+    'x_17___\n'\
+    '  \\/ 7 '
+
+
 def test_issue_17857():
     assert pretty(Range(-oo, oo)) == '{..., -1, 0, 1, ...}'
     assert pretty(Range(oo, -oo, -1)) == '{..., 1, 0, -1, ...}'

```

## Test Information

**Tests that should FAIL→PASS**: ["test_issue_6285", "test_issue_17616"]

**Tests that should PASS→PASS**: ["test_pretty_ascii_str", "test_pretty_unicode_str", "test_upretty_greek", "test_upretty_multiindex", "test_upretty_sub_super", "test_upretty_subs_missing_in_24", "test_missing_in_2X_issue_9047", "test_upretty_modifiers", "test_pretty_Cycle", "test_pretty_Permutation", "test_pretty_basic", "test_negative_fractions", "test_issue_5524", "test_pretty_ordering", "test_EulerGamma", "test_GoldenRatio", "test_pretty_relational", "test_Assignment", "test_AugmentedAssignment", "test_pretty_rational", "test_pretty_functions", "test_pretty_sqrt", "test_pretty_sqrt_char_knob", "test_pretty_sqrt_longsymbol_no_sqrt_char", "test_pretty_KroneckerDelta", "test_pretty_product", "test_pretty_Lambda", "test_pretty_TransferFunction", "test_pretty_Series", "test_pretty_Parallel", "test_pretty_Feedback", "test_pretty_order", "test_pretty_derivatives", "test_pretty_integrals", "test_pretty_matrix", "test_pretty_ndim_arrays", "test_tensor_TensorProduct", "test_diffgeom_print_WedgeProduct", "test_Adjoint", "test_pretty_Trace_issue_9044", "test_MatrixSlice", "test_MatrixExpressions", "test_pretty_dotproduct", "test_pretty_piecewise", "test_pretty_ITE", "test_pretty_seq", "test_any_object_in_sequence", "test_print_builtin_set", "test_pretty_sets", "test_pretty_SetExpr", "test_pretty_ImageSet", "test_pretty_ConditionSet", "test_pretty_ComplexRegion", "test_pretty_Union_issue_10414", "test_pretty_Intersection_issue_10414", "test_ProductSet_exponent", "test_ProductSet_parenthesis", "test_ProductSet_prod_char_issue_10413", "test_pretty_sequences", "test_pretty_FourierSeries", "test_pretty_FormalPowerSeries", "test_pretty_limits", "test_pretty_ComplexRootOf", "test_pretty_RootSum", "test_GroebnerBasis", "test_pretty_UniversalSet", "test_pretty_Boolean", "test_pretty_Domain", "test_pretty_prec", "test_pprint", "test_pretty_class", "test_pretty_no_wrap_line", "test_settings", "test_pretty_sum", "test_units", "test_pretty_Subs", "test_gammas", "test_beta", "test_function_subclass_different_name", "test_SingularityFunction", "test_deltas", "test_hyper", "test_meijerg", "test_noncommutative", "test_pretty_special_functions", "test_pretty_geometry", "test_expint", "test_elliptic_functions", "test_RandomDomain", "test_PrettyPoly", "test_issue_6359", "test_issue_6739", "test_complicated_symbol_unchanged", "test_categories", "test_PrettyModules", "test_QuotientRing", "test_Homomorphism", "test_Tr", "test_pretty_Add", "test_issue_7179", "test_issue_7180", "test_pretty_Complement", "test_pretty_SymmetricDifference", "test_pretty_Contains", "test_issue_8292", "test_issue_4335", "test_issue_8344", "test_issue_6324", "test_issue_7927", "test_issue_6134", "test_issue_9877", "test_issue_13651", "test_pretty_primenu", "test_pretty_primeomega", "test_pretty_Mod", "test_issue_11801", "test_pretty_UnevaluatedExpr", "test_issue_10472", "test_MatrixElement_printing", "test_issue_12675", "test_MatrixSymbol_printing", "test_degree_printing", "test_vector_expr_pretty_printing", "test_pretty_print_tensor_expr", "test_pretty_print_tensor_partial_deriv", "test_issue_15560", "test_print_lerchphi", "test_issue_15583", "test_matrixSymbolBold", "test_center_accent", "test_imaginary_unit", "test_str_special_matrices", "test_pretty_misc_functions", "test_hadamard_power", "test_issue_17258", "test_is_combining", "test_issue_17857", "test_issue_18272", "test_Str"]

**Base Commit**: eb926a1d0c1158bf43f01eaf673dc84416b5ebb1
**Environment Setup Commit**: 3ac1464b8840d5f8b618a654f9fbf09c452fe969
