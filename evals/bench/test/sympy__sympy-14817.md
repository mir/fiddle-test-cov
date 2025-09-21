# sympy__sympy-14817

**Repository**: sympy/sympy
**Created**: 2018-06-21T08:34:37Z
**Version**: 1.1

## Problem Statement

Error pretty printing MatAdd
```py
>>> pprint(MatrixSymbol('x', n, n) + MatrixSymbol('y*', n, n))
Traceback (most recent call last):
  File "./sympy/core/sympify.py", line 368, in sympify
    expr = parse_expr(a, local_dict=locals, transformations=transformations, evaluate=evaluate)
  File "./sympy/parsing/sympy_parser.py", line 950, in parse_expr
    return eval_expr(code, local_dict, global_dict)
  File "./sympy/parsing/sympy_parser.py", line 863, in eval_expr
    code, global_dict, local_dict)  # take local objects in preference
  File "<string>", line 1
    Symbol ('y' )*
                 ^
SyntaxError: unexpected EOF while parsing

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "./sympy/printing/pretty/pretty.py", line 2371, in pretty_print
    use_unicode_sqrt_char=use_unicode_sqrt_char))
  File "./sympy/printing/pretty/pretty.py", line 2331, in pretty
    return pp.doprint(expr)
  File "./sympy/printing/pretty/pretty.py", line 62, in doprint
    return self._print(expr).render(**self._settings)
  File "./sympy/printing/printer.py", line 274, in _print
    return getattr(self, printmethod)(expr, *args, **kwargs)
  File "./sympy/printing/pretty/pretty.py", line 828, in _print_MatAdd
    if S(item.args[0]).is_negative:
  File "./sympy/core/sympify.py", line 370, in sympify
    raise SympifyError('could not parse %r' % a, exc)
sympy.core.sympify.SympifyError: Sympify of expression 'could not parse 'y*'' failed, because of exception being raised:
SyntaxError: unexpected EOF while parsing (<string>, line 1)
```

The code shouldn't be using sympify to handle string arguments from MatrixSymbol.

I don't even understand what the code is doing. Why does it omit the `+` when the first argument is negative? This seems to assume that the arguments of MatAdd have a certain form, and that they will always print a certain way if they are negative. 


## Hints

Looks like it comes from fbbbd392e6c which is from https://github.com/sympy/sympy/pull/14248. CC @jashan498 
`_print_MatAdd` should use the same methods as `_print_Add` to determine whether or not to include a plus or minus sign. If it's possible, it could even reuse the same code. 

## Patch

```diff

diff --git a/sympy/printing/pretty/pretty.py b/sympy/printing/pretty/pretty.py
--- a/sympy/printing/pretty/pretty.py
+++ b/sympy/printing/pretty/pretty.py
@@ -825,7 +825,8 @@ def _print_MatAdd(self, expr):
             if s is None:
                 s = pform     # First element
             else:
-                if S(item.args[0]).is_negative:
+                coeff = item.as_coeff_mmul()[0]
+                if _coeff_isneg(S(coeff)):
                     s = prettyForm(*stringPict.next(s, ' '))
                     pform = self._print(item)
                 else:


```

## Test Patch

```diff
diff --git a/sympy/printing/pretty/tests/test_pretty.py b/sympy/printing/pretty/tests/test_pretty.py
--- a/sympy/printing/pretty/tests/test_pretty.py
+++ b/sympy/printing/pretty/tests/test_pretty.py
@@ -6094,11 +6094,16 @@ def test_MatrixSymbol_printing():
     A = MatrixSymbol("A", 3, 3)
     B = MatrixSymbol("B", 3, 3)
     C = MatrixSymbol("C", 3, 3)
-
     assert pretty(-A*B*C) == "-A*B*C"
     assert pretty(A - B) == "-B + A"
     assert pretty(A*B*C - A*B - B*C) == "-A*B -B*C + A*B*C"
 
+    # issue #14814
+    x = MatrixSymbol('x', n, n)
+    y = MatrixSymbol('y*', n, n)
+    assert pretty(x + y) == "x + y*"
+    assert pretty(-a*x + -2*y*y) == "-a*x -2*y**y*"
+
 
 def test_degree_printing():
     expr1 = 90*degree

```

## Test Information

**Tests that should FAIL→PASS**: ["test_MatrixSymbol_printing"]

**Tests that should PASS→PASS**: ["test_pretty_ascii_str", "test_pretty_unicode_str", "test_upretty_greek", "test_upretty_multiindex", "test_upretty_sub_super", "test_upretty_subs_missing_in_24", "test_upretty_modifiers", "test_pretty_Cycle", "test_pretty_basic", "test_negative_fractions", "test_issue_5524", "test_pretty_ordering", "test_EulerGamma", "test_GoldenRatio", "test_pretty_relational", "test_Assignment", "test_AugmentedAssignment", "test_issue_7117", "test_pretty_rational", "test_pretty_functions", "test_pretty_sqrt", "test_pretty_sqrt_char_knob", "test_pretty_sqrt_longsymbol_no_sqrt_char", "test_pretty_KroneckerDelta", "test_pretty_product", "test_pretty_lambda", "test_pretty_order", "test_pretty_derivatives", "test_pretty_integrals", "test_pretty_matrix", "test_pretty_ndim_arrays", "test_tensor_TensorProduct", "test_diffgeom_print_WedgeProduct", "test_Adjoint", "test_pretty_Trace_issue_9044", "test_MatrixExpressions", "test_pretty_dotproduct", "test_pretty_piecewise", "test_pretty_ITE", "test_pretty_seq", "test_any_object_in_sequence", "test_print_builtin_set", "test_pretty_sets", "test_pretty_SetExpr", "test_pretty_ImageSet", "test_pretty_ConditionSet", "test_pretty_ComplexRegion", "test_pretty_Union_issue_10414", "test_pretty_Intersection_issue_10414", "test_ProductSet_paranthesis", "test_ProductSet_prod_char_issue_10413", "test_pretty_sequences", "test_pretty_FourierSeries", "test_pretty_FormalPowerSeries", "test_pretty_limits", "test_pretty_ComplexRootOf", "test_pretty_RootSum", "test_GroebnerBasis", "test_pretty_Boolean", "test_pretty_Domain", "test_pretty_prec", "test_pprint", "test_pretty_class", "test_pretty_no_wrap_line", "test_settings", "test_pretty_sum", "test_units", "test_pretty_Subs", "test_gammas", "test_beta", "test_function_subclass_different_name", "test_SingularityFunction", "test_deltas", "test_hyper", "test_meijerg", "test_noncommutative", "test_pretty_special_functions", "test_expint", "test_elliptic_functions", "test_RandomDomain", "test_PrettyPoly", "test_issue_6285", "test_issue_6359", "test_issue_6739", "test_complicated_symbol_unchanged", "test_categories", "test_PrettyModules", "test_QuotientRing", "test_Homomorphism", "test_Tr", "test_pretty_Add", "test_issue_7179", "test_issue_7180", "test_pretty_Complement", "test_pretty_SymmetricDifference", "test_pretty_Contains", "test_issue_4335", "test_issue_6324", "test_issue_7927", "test_issue_6134", "test_issue_9877", "test_issue_13651", "test_pretty_primenu", "test_pretty_primeomega", "test_pretty_Mod", "test_issue_11801", "test_pretty_UnevaluatedExpr", "test_issue_10472", "test_MatrixElement_printing", "test_issue_12675", "test_degree_printing"]

**Base Commit**: 0dbdc0ea83d339936da175f8c3a97d0d6bafb9f8
**Environment Setup Commit**: ec9e3c0436fbff934fa84e22bf07f1b3ef5bfac3
