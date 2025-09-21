# sympy__sympy-18698

**Repository**: sympy/sympy
**Created**: 2020-02-21T05:46:56Z
**Version**: 1.6

## Problem Statement

sqf and sqf_list output is not consistant
The example below is wrong in the sense that we should have (x*_2 - 5_x + 6, 3) and not 2 factors of multiplicity 3.

```
>  sqf_list(  (x**2 + 1)  * (x - 1)**2 * (x - 2)**3 * (x - 3)**3  )

>  (1, [(x**2 + 1, 1), (x - 1, 2), (x - 3, 3), (x - 2, 3)])
```

whereas below is correct --- one factor of multiplicity 2

```
>  sqf_list( x**5 - 2*x**4 - 2*x**3 + 4*x**2 + x - 2 )

>  (1, [(x - 2, 1), (x**2 - 1, 2)])
```



## Hints

I guess correct can be either the first or the second. But we should stick to it.

This [SO post](https://stackoverflow.com/questions/57536689/sympys-sqf-and-sqf-list-give-different-results-once-i-use-poly-or-as-pol) highlights another problem, too:

```python
>>> v = (x1 + 2) ** 2 * (x2 + 4) ** 5
>>> sqf(v)
(x1 + 2)**2*(x2 + 4)**5
>>> sqf(v.expand())
(x1 + 2)**2  <-- where is the x2 factor?
```
The documentation is incomplete. The docstrings for low level methods in `sqfreetools` show that they are for univariate polynomials only but that is missing from `polytools`. The docstrings should be amended.

The issue in OP is valid. The `Poly` method works as expected:
```
>>> Poly((x**2 + 1)*(x - 1)**2*(x - 2)**3*(x - 3)**3, x).sqf_list()
(1, [(Poly(x**2 + 1, x, domain='ZZ'), 1), (Poly(x - 1, x, domain='ZZ'), 2), (Poly(x**2 - 5*x + 6, x, domain='ZZ'), 3)])
```
The two factors of multiplicity 3 are combined as they should be.

The `sqf_list` function fails to do that.
```
>>> sqf_list((x**2 + 1)*(x - 1)**2*(x - 2)**3*(x - 3)**3, x)
(1, [(x**2 + 1, 1), (x - 1, 2), (x - 3, 3), (x - 2, 3)])
```
It should scan the generic factor list and combine factors of same multiplicity before returning the list.
https://github.com/sympy/sympy/blob/e4259125f63727b76d0a0c4743ba1cd8d433d3ea/sympy/polys/polytools.py#L6218
Hi, I am new to the sympy community and was looking to contribute to the project. I wanted to ask @akritas what's wrong in having 2 factors of multiplicity 3? Also, if the second issue (on SO) is still open, then I would like to work on it, @jksuom can you guide me from where I should start? 


Sent from my iPad

> On 15 Dec 2019, at 5:24 PM, Akhil Rajput <notifications@github.com> wrote:
> 
> ﻿
> Hi, I am new to the sympy community and was looking to contribute to the project. I wanted to ask @akritas what's wrong in having 2 factors of multiplicity 3?
> 
Hi, 

The square free algorithm should pull out all factors of _same_ degree and present them as one product of given multiplicity (in this case one factor with roots of multiplicity 3).
> Also, if the second issue (on SO) is still open, then I would like to work on it, @jksuom can you guide me from where I should start?
> 
> —
> You are receiving this because you were mentioned.
> Reply to this email directly, view it on GitHub, or unsubscribe.

I would start with the docstrings. The squarefree methods are intended for univariate polynomials. The generator should be given as an input parameter. It may be omitted if there is no danger of confusion (only one symbol in the expression). Otherwise the result may be indeterminate as shown by the [example above](https://github.com/sympy/sympy/issues/8695#issuecomment-522278244).
@jksuom, I'm still unclear. There is already an option to pass generators as an argument to sqf_list(). Should the function automatically find the generators present in the expression? Please guide me what should I do. 
If there is only one symbol in the expression, then the function can find the generator automatically. Otherwise I think that exactly one symbol should be given as the generator.

Moreover, I would like to change the implementations of `sqf_list()` and related functions so that they would be based on the corresponding `Poly` methods. Then they would start by converting the input expression into `p = Poly(f, *gens, **args)` and check that `p` has exactly one generator. Then `p.sqf_list()` etc, would be called.
Then what will happen in case of multiple generators? Just confirming, generators here refer to symbols/variables.
> generators here refer to symbols/variables.

Yes.
> Then what will happen in case of multiple generators?

I think that ValueError could be raised. It seems that some kind of result is currently returned but there is no documentation, and I don't know of any reasonable use where the ordinary factorization would not suffice.
> If there is only one symbol in the expression, then the function can find the generator automatically. Otherwise I think that exactly one symbol should be given as the generator.
> 
> Moreover, I would like to change the implementations of `sqf_list()` and related functions so that they would be based on the corresponding `Poly` methods. Then they would start by converting the input expression into `p = Poly(f, *gens, **args)` and check that `p` has exactly one generator. Then `p.sqf_list()` etc, would be called.

@jksuom  In the helper function __symbolic_factor_list_ of sqf_list, the expression is already being converted to polynomial and then corresponding _sqf_list_ function is called. So, I should just ensure if the number of generators passed is one?
> I should just ensure if the number of generators passed is one?

If there is exactly one generator passed, then it is possible to call `_generic_factor_list` with the given arguments. However, it is necessary to post-process the result. In the example above, it returns

    (1, [(x**2 + 1, 1), (x - 1, 2), (x - 3, 3), (x - 2, 3)])

while `sqf_list` should return only one polynomial for each power. Therefore the two threefold factors `x - 3` and `x - 2` should be combined to give a single `(x**2 - 5*x + 6, 3)`.

It is probably quite common that no generators are given, in particular, when the expression looks like a univariate polynomial. This should be acceptable but more work is then necessary to find the number of generators. I think that it is best to convert the expression to a `Poly` object to see the generators. If there is only one, then the `sqf_list` method can be called, otherwise a `ValueError` should be raised.

It is possible that the latter procedure will be more efficient even if a single generator is given.
@jksuom I have created a PR (#18307)for the issue. I haven't done anything for multiple generator case as it was ambiguous. It would be great if you could review it. Thank you. 
@jksuom what can be done in case if the expression given is a constant (without any generators)? For example:  `sqf_list(1)`. We won't be able to construct a polynomial and PolificationFailed error will be raised.
I think that the error can be raised. It is typical of many polynomial functions that they don't work with constant expressions.

## Patch

```diff

diff --git a/sympy/polys/polytools.py b/sympy/polys/polytools.py
--- a/sympy/polys/polytools.py
+++ b/sympy/polys/polytools.py
@@ -2,7 +2,8 @@
 
 from __future__ import print_function, division
 
-from functools import wraps
+from functools import wraps, reduce
+from operator import mul
 
 from sympy.core import (
     S, Basic, Expr, I, Integer, Add, Mul, Dummy, Tuple
@@ -5905,10 +5906,7 @@ def _symbolic_factor_list(expr, opt, method):
         if arg.is_Number:
             coeff *= arg
             continue
-        if arg.is_Mul:
-            args.extend(arg.args)
-            continue
-        if arg.is_Pow:
+        elif arg.is_Pow:
             base, exp = arg.args
             if base.is_Number and exp.is_Number:
                 coeff *= arg
@@ -5949,6 +5947,9 @@ def _symbolic_factor_list(expr, opt, method):
                         other.append((f, k))
 
                 factors.append((_factors_product(other), exp))
+    if method == 'sqf':
+        factors = [(reduce(mul, (f for f, _ in factors if _ == k)), k)
+                   for k in set(i for _, i in factors)]
 
     return coeff, factors
 


```

## Test Patch

```diff
diff --git a/sympy/polys/tests/test_polytools.py b/sympy/polys/tests/test_polytools.py
--- a/sympy/polys/tests/test_polytools.py
+++ b/sympy/polys/tests/test_polytools.py
@@ -3273,7 +3273,7 @@ def test_to_rational_coeffs():
 def test_factor_terms():
     # issue 7067
     assert factor_list(x*(x + y)) == (1, [(x, 1), (x + y, 1)])
-    assert sqf_list(x*(x + y)) == (1, [(x, 1), (x + y, 1)])
+    assert sqf_list(x*(x + y)) == (1, [(x**2 + x*y, 1)])
 
 
 def test_as_list():
@@ -3333,3 +3333,8 @@ def test_issue_17988():
 def test_issue_18205():
     assert cancel((2 + I)*(3 - I)) == 7 + I
     assert cancel((2 + I)*(2 - I)) == 5
+
+def test_issue_8695():
+    p = (x**2 + 1) * (x - 1)**2 * (x - 2)**3 * (x - 3)**3
+    result = (1, [(x**2 + 1, 1), (x - 1, 2), (x**2 - 5*x + 6, 3)])
+    assert sqf_list(p) == result

```

## Test Information

**Tests that should FAIL→PASS**: ["test_factor_terms"]

**Tests that should PASS→PASS**: ["test_Poly_mixed_operations", "test_Poly_from_dict", "test_Poly_from_list", "test_Poly_from_poly", "test_Poly_from_expr", "test_Poly__new__", "test_Poly__args", "test_Poly__gens", "test_Poly_zero", "test_Poly_one", "test_Poly__unify", "test_Poly_free_symbols", "test_PurePoly_free_symbols", "test_Poly__eq__", "test_PurePoly__eq__", "test_PurePoly_Poly", "test_Poly_get_domain", "test_Poly_set_domain", "test_Poly_get_modulus", "test_Poly_set_modulus", "test_Poly_add_ground", "test_Poly_sub_ground", "test_Poly_mul_ground", "test_Poly_quo_ground", "test_Poly_exquo_ground", "test_Poly_abs", "test_Poly_neg", "test_Poly_add", "test_Poly_sub", "test_Poly_mul", "test_issue_13079", "test_Poly_sqr", "test_Poly_pow", "test_Poly_divmod", "test_Poly_eq_ne", "test_Poly_nonzero", "test_Poly_properties", "test_Poly_is_irreducible", "test_Poly_subs", "test_Poly_replace", "test_Poly_reorder", "test_Poly_ltrim", "test_Poly_has_only_gens", "test_Poly_to_ring", "test_Poly_to_field", "test_Poly_to_exact", "test_Poly_retract", "test_Poly_slice", "test_Poly_coeffs", "test_Poly_monoms", "test_Poly_terms", "test_Poly_all_coeffs", "test_Poly_all_monoms", "test_Poly_all_terms", "test_Poly_termwise", "test_Poly_length", "test_Poly_as_dict", "test_Poly_as_expr", "test_Poly_lift", "test_Poly_deflate", "test_Poly_inject", "test_Poly_eject", "test_Poly_exclude", "test_Poly__gen_to_level", "test_Poly_degree", "test_Poly_degree_list", "test_Poly_total_degree", "test_Poly_homogenize", "test_Poly_homogeneous_order", "test_Poly_LC", "test_Poly_TC", "test_Poly_EC", "test_Poly_coeff", "test_Poly_nth", "test_Poly_LM", "test_Poly_LM_custom_order", "test_Poly_EM", "test_Poly_LT", "test_Poly_ET", "test_Poly_max_norm", "test_Poly_l1_norm", "test_Poly_clear_denoms", "test_Poly_rat_clear_denoms", "test_Poly_integrate", "test_Poly_diff", "test_issue_9585", "test_Poly_eval", "test_Poly___call__", "test_parallel_poly_from_expr", "test_pdiv", "test_div", "test_issue_7864", "test_gcdex", "test_revert", "test_subresultants", "test_resultant", "test_discriminant", "test_dispersion", "test_gcd_list", "test_lcm_list", "test_gcd", "test_gcd_numbers_vs_polys", "test_terms_gcd", "test_trunc", "test_monic", "test_content", "test_primitive", "test_compose", "test_shift", "test_transform", "test_sturm", "test_gff", "test_norm", "test_sqf_norm", "test_sqf", "test_factor", "test_factor_large", "test_factor_noeval", "test_intervals", "test_refine_root", "test_count_roots", "test_Poly_root", "test_real_roots", "test_all_roots", "test_nroots", "test_ground_roots", "test_nth_power_roots_poly", "test_torational_factor_list", "test_cancel", "test_reduced", "test_groebner", "test_fglm", "test_is_zero_dimensional", "test_GroebnerBasis", "test_poly", "test_keep_coeff", "test_poly_matching_consistency", "test_noncommutative", "test_to_rational_coeffs", "test_as_list", "test_issue_11198", "test_Poly_precision", "test_issue_12400", "test_issue_14364", "test_issue_15669", "test_issue_17988", "test_issue_18205"]

**Base Commit**: 3dff1b98a78f28c953ae2140b69356b8391e399c
**Environment Setup Commit**: 28b41c73c12b70d6ad9f6e45109a80649c4456da
