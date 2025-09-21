# sympy__sympy-14024

**Repository**: sympy/sympy
**Created**: 2018-01-27T05:55:11Z
**Version**: 1.1

## Problem Statement

Inconsistency when simplifying (-a)**x * a**(-x), a a positive integer
Compare:

```
>>> a = Symbol('a', integer=True, positive=True)
>>> e = (-a)**x * a**(-x)
>>> f = simplify(e)
>>> print(e)
a**(-x)*(-a)**x
>>> print(f)
(-1)**x
>>> t = -S(10)/3
>>> n1 = e.subs(x,t)
>>> n2 = f.subs(x,t)
>>> print(N(n1))
-0.5 + 0.866025403784439*I
>>> print(N(n2))
-0.5 + 0.866025403784439*I
```

vs

```
>>> a = S(2)
>>> e = (-a)**x * a**(-x)
>>> f = simplify(e)
>>> print(e)
(-2)**x*2**(-x)
>>> print(f)
(-1)**x
>>> t = -S(10)/3
>>> n1 = e.subs(x,t)
>>> n2 = f.subs(x,t)
>>> print(N(n1))
0.5 - 0.866025403784439*I
>>> print(N(n2))
-0.5 + 0.866025403784439*I
```


## Hints

More succinctly, the problem is
```
>>> (-2)**(-S(10)/3)
-(-2)**(2/3)/16
```
Pow is supposed to use the principal branch, which means (-2) has complex argument pi, which under exponentiation becomes `-10*pi/3` or equivalently `2*pi/3`. But the result of automatic simplification is different: its argument is -pi/3. 

The base (-1) is handled correctly, though.
```
>>> (-1)**(-S(10)/3)
(-1)**(2/3)
```
Hence the inconsistency, because the simplified form of the product has (-1) in its base.

## Patch

```diff

diff --git a/sympy/core/numbers.py b/sympy/core/numbers.py
--- a/sympy/core/numbers.py
+++ b/sympy/core/numbers.py
@@ -1678,11 +1678,7 @@ def _eval_power(self, expt):
                 if (ne is S.One):
                     return Rational(self.q, self.p)
                 if self.is_negative:
-                    if expt.q != 1:
-                        return -(S.NegativeOne)**((expt.p % expt.q) /
-                               S(expt.q))*Rational(self.q, -self.p)**ne
-                    else:
-                        return S.NegativeOne**ne*Rational(self.q, -self.p)**ne
+                    return S.NegativeOne**expt*Rational(self.q, -self.p)**ne
                 else:
                     return Rational(self.q, self.p)**ne
             if expt is S.Infinity:  # -oo already caught by test for negative
@@ -2223,11 +2219,7 @@ def _eval_power(self, expt):
             # invert base and change sign on exponent
             ne = -expt
             if self.is_negative:
-                if expt.q != 1:
-                    return -(S.NegativeOne)**((expt.p % expt.q) /
-                            S(expt.q))*Rational(1, -self)**ne
-                else:
-                    return (S.NegativeOne)**ne*Rational(1, -self)**ne
+                    return S.NegativeOne**expt*Rational(1, -self)**ne
             else:
                 return Rational(1, self.p)**ne
         # see if base is a perfect root, sqrt(4) --> 2


```

## Test Patch

```diff
diff --git a/sympy/core/tests/test_numbers.py b/sympy/core/tests/test_numbers.py
--- a/sympy/core/tests/test_numbers.py
+++ b/sympy/core/tests/test_numbers.py
@@ -1041,6 +1041,10 @@ def test_powers_Integer():
         -(-1)**Rational(2, 3)*3**Rational(2, 3)/27
     assert (-3) ** Rational(-2, 3) == \
         -(-1)**Rational(1, 3)*3**Rational(1, 3)/3
+    assert (-2) ** Rational(-10, 3) == \
+        (-1)**Rational(2, 3)*2**Rational(2, 3)/16
+    assert abs(Pow(-2, Rational(-10, 3)).n() -
+        Pow(-2, Rational(-10, 3), evaluate=False).n()) < 1e-16
 
     # negative base and rational power with some simplification
     assert (-8) ** Rational(2, 5) == \
@@ -1121,6 +1125,10 @@ def test_powers_Rational():
         -4*(-1)**Rational(2, 3)*2**Rational(1, 3)*3**Rational(2, 3)/27
     assert Rational(-3, 2)**Rational(-2, 3) == \
         -(-1)**Rational(1, 3)*2**Rational(2, 3)*3**Rational(1, 3)/3
+    assert Rational(-3, 2)**Rational(-10, 3) == \
+        8*(-1)**Rational(2, 3)*2**Rational(1, 3)*3**Rational(2, 3)/81
+    assert abs(Pow(Rational(-2, 3), Rational(-7, 4)).n() -
+        Pow(Rational(-2, 3), Rational(-7, 4), evaluate=False).n()) < 1e-16
 
     # negative integer power and negative rational base
     assert Rational(-2, 3) ** Rational(-2, 1) == Rational(9, 4)

```

## Test Information

**Tests that should FAIL→PASS**: ["test_powers_Integer", "test_powers_Rational"]

**Tests that should PASS→PASS**: ["test_integers_cache", "test_seterr", "test_mod", "test_divmod", "test_igcd", "test_igcd_lehmer", "test_igcd2", "test_ilcm", "test_igcdex", "test_Integer_new", "test_Rational_new", "test_Number_new", "test_Rational_cmp", "test_Float", "test_float_mpf", "test_Float_RealElement", "test_Float_default_to_highprec_from_str", "test_Float_eval", "test_Float_issue_2107", "test_Float_from_tuple", "test_Infinity", "test_Infinity_2", "test_Mul_Infinity_Zero", "test_Div_By_Zero", "test_Infinity_inequations", "test_NaN", "test_special_numbers", "test_powers", "test_integer_nthroot_overflow", "test_integer_log", "test_isqrt", "test_powers_Float", "test_abs1", "test_accept_int", "test_dont_accept_str", "test_int", "test_long", "test_real_bug", "test_bug_sqrt", "test_pi_Pi", "test_no_len", "test_issue_3321", "test_issue_3692", "test_issue_3423", "test_issue_3449", "test_issue_13890", "test_Integer_factors", "test_Rational_factors", "test_issue_4107", "test_IntegerInteger", "test_Rational_gcd_lcm_cofactors", "test_Float_gcd_lcm_cofactors", "test_issue_4611", "test_conversion_to_mpmath", "test_relational", "test_Integer_as_index", "test_Rational_int", "test_zoo", "test_issue_4122", "test_GoldenRatio_expand", "test_as_content_primitive", "test_hashing_sympy_integers", "test_issue_4172", "test_Catalan_EulerGamma_prec", "test_Float_eq", "test_int_NumberSymbols", "test_issue_6640", "test_issue_6349", "test_mpf_norm", "test_latex", "test_issue_7742", "test_simplify_AlgebraicNumber", "test_Float_idempotence", "test_comp", "test_issue_9491", "test_issue_10063", "test_issue_10020", "test_invert_numbers", "test_mod_inverse", "test_golden_ratio_rewrite_as_sqrt", "test_comparisons_with_unknown_type", "test_NumberSymbol_comparison", "test_Integer_precision"]

**Base Commit**: b17abcb09cbcee80a90f6750e0f9b53f0247656c
**Environment Setup Commit**: ec9e3c0436fbff934fa84e22bf07f1b3ef5bfac3
