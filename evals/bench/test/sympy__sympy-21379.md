# sympy__sympy-21379

**Repository**: sympy/sympy
**Created**: 2021-04-24T19:49:52Z
**Version**: 1.9

## Problem Statement

Unexpected `PolynomialError` when using simple `subs()` for particular expressions
I am seeing weird behavior with `subs` for particular expressions with hyperbolic sinusoids with piecewise arguments. When applying `subs`, I obtain an unexpected `PolynomialError`. For context, I was umbrella-applying a casting from int to float of all int atoms for a bunch of random expressions before using a tensorflow lambdify to avoid potential tensorflow type errors. You can pretend the expression below has a `+ 1` at the end, but below is the MWE that I could produce.

See the expression below, and the conditions in which the exception arises.

Sympy version: 1.8.dev

```python
from sympy import *
from sympy.core.cache import clear_cache

x, y, z = symbols('x y z')

clear_cache()
expr = exp(sinh(Piecewise((x, y > x), (y, True)) / z))
# This works fine
expr.subs({1: 1.0})

clear_cache()
x, y, z = symbols('x y z', real=True)
expr = exp(sinh(Piecewise((x, y > x), (y, True)) / z))
# This fails with "PolynomialError: Piecewise generators do not make sense"
expr.subs({1: 1.0})  # error
# Now run it again (isympy...) w/o clearing cache and everything works as expected without error
expr.subs({1: 1.0})
```

I am not really sure where the issue is, but I think it has something to do with the order of assumptions in this specific type of expression. Here is what I found-

- The error only (AFAIK) happens with `cosh` or `tanh` in place of `sinh`, otherwise it succeeds
- The error goes away if removing the division by `z`
- The error goes away if removing `exp` (but stays for most unary functions, `sin`, `log`, etc.)
- The error only happens with real symbols for `x` and `y` (`z` does not have to be real)

Not too sure how to debug this one.


## Hints

Some functions call `Mod` when evaluated. That does not work well with arguments involving `Piecewise` expressions. In particular, calling `gcd` will lead to `PolynomialError`. That error should be caught by something like this:
```
--- a/sympy/core/mod.py
+++ b/sympy/core/mod.py
@@ -40,6 +40,7 @@ def eval(cls, p, q):
         from sympy.core.mul import Mul
         from sympy.core.singleton import S
         from sympy.core.exprtools import gcd_terms
+        from sympy.polys.polyerrors import PolynomialError
         from sympy.polys.polytools import gcd
 
         def doit(p, q):
@@ -166,10 +167,13 @@ def doit(p, q):
         # XXX other possibilities?
 
         # extract gcd; any further simplification should be done by the user
-        G = gcd(p, q)
-        if G != 1:
-            p, q = [
-                gcd_terms(i/G, clear=False, fraction=False) for i in (p, q)]
+        try:
+            G = gcd(p, q)
+            if G != 1:
+                p, q = [gcd_terms(i/G, clear=False, fraction=False)
+                        for i in (p, q)]
+        except PolynomialError:
+            G = S.One
         pwas, qwas = p, q
 
         # simplify terms
```
I can't seem to reproduce the OP problem. One suggestion for debugging is to disable the cache e.g. `SYMPY_USE_CACHE=no` but if that makes the problem go away then I guess it's to do with caching somehow and I'm not sure how to debug...

I can see what @jksuom is referring to:
```python
In [2]: (Piecewise((x, y > x), (y, True)) / z) % 1
---------------------------------------------------------------------------
PolynomialError
```
That should be fixed.

As an aside you might prefer to use `nfloat` rather than `expr.subs({1:1.0})`:
https://docs.sympy.org/latest/modules/core.html#sympy.core.function.nfloat
@oscarbenjamin My apologies - I missed a line in the post recreating the expression with real x/y/z. Here is the minimum code to reproduce (may require running w/o cache):
```python
from sympy import *

x, y, z = symbols('x y z', real=True)
expr = exp(sinh(Piecewise((x, y > x), (y, True)) / z))
expr.subs({1: 1.0})
```

Your code minimally identifies the real problem, however. Thanks for pointing out `nfloat`, but this also induces the exact same error.


@jksuom I can confirm that your patch fixes the issue on my end! I can put in a PR, and add the minimal test given by @oscarbenjamin, if you would like
Okay I can reproduce it now.

The PR would be good thanks.

I think that we also need to figure out what the caching issue is though. The error should be deterministic.

I was suggesting `nfloat` not to fix this issue but because it's possibly a better way of doing what you suggested. I expect that tensorflow is more efficient with integer exponents than float exponents.
This is the full traceback:
```python
Traceback (most recent call last):
  File "/Users/enojb/current/sympy/sympy/sympy/core/assumptions.py", line 454, in getit
    return self._assumptions[fact]
KeyError: 'zero'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "y.py", line 5, in <module>
    expr.subs({1: 1.0})
  File "/Users/enojb/current/sympy/sympy/sympy/core/basic.py", line 949, in subs
    rv = rv._subs(old, new, **kwargs)
  File "/Users/enojb/current/sympy/sympy/sympy/core/cache.py", line 72, in wrapper
    retval = cfunc(*args, **kwargs)
  File "/Users/enojb/current/sympy/sympy/sympy/core/basic.py", line 1063, in _subs
    rv = fallback(self, old, new)
  File "/Users/enojb/current/sympy/sympy/sympy/core/basic.py", line 1040, in fallback
    rv = self.func(*args)
  File "/Users/enojb/current/sympy/sympy/sympy/core/cache.py", line 72, in wrapper
    retval = cfunc(*args, **kwargs)
  File "/Users/enojb/current/sympy/sympy/sympy/core/function.py", line 473, in __new__
    result = super().__new__(cls, *args, **options)
  File "/Users/enojb/current/sympy/sympy/sympy/core/cache.py", line 72, in wrapper
    retval = cfunc(*args, **kwargs)
  File "/Users/enojb/current/sympy/sympy/sympy/core/function.py", line 285, in __new__
    evaluated = cls.eval(*args)
  File "/Users/enojb/current/sympy/sympy/sympy/functions/elementary/exponential.py", line 369, in eval
    if arg.is_zero:
  File "/Users/enojb/current/sympy/sympy/sympy/core/assumptions.py", line 458, in getit
    return _ask(fact, self)
  File "/Users/enojb/current/sympy/sympy/sympy/core/assumptions.py", line 513, in _ask
    _ask(pk, obj)
  File "/Users/enojb/current/sympy/sympy/sympy/core/assumptions.py", line 513, in _ask
    _ask(pk, obj)
  File "/Users/enojb/current/sympy/sympy/sympy/core/assumptions.py", line 513, in _ask
    _ask(pk, obj)
  [Previous line repeated 2 more times]
  File "/Users/enojb/current/sympy/sympy/sympy/core/assumptions.py", line 501, in _ask
    a = evaluate(obj)
  File "/Users/enojb/current/sympy/sympy/sympy/functions/elementary/hyperbolic.py", line 251, in _eval_is_real
    return (im%pi).is_zero
  File "/Users/enojb/current/sympy/sympy/sympy/core/decorators.py", line 266, in _func
    return func(self, other)
  File "/Users/enojb/current/sympy/sympy/sympy/core/decorators.py", line 136, in binary_op_wrapper
    return func(self, other)
  File "/Users/enojb/current/sympy/sympy/sympy/core/expr.py", line 280, in __mod__
    return Mod(self, other)
  File "/Users/enojb/current/sympy/sympy/sympy/core/cache.py", line 72, in wrapper
    retval = cfunc(*args, **kwargs)
  File "/Users/enojb/current/sympy/sympy/sympy/core/function.py", line 473, in __new__
    result = super().__new__(cls, *args, **options)
  File "/Users/enojb/current/sympy/sympy/sympy/core/cache.py", line 72, in wrapper
    retval = cfunc(*args, **kwargs)
  File "/Users/enojb/current/sympy/sympy/sympy/core/function.py", line 285, in __new__
    evaluated = cls.eval(*args)
  File "/Users/enojb/current/sympy/sympy/sympy/core/mod.py", line 169, in eval
    G = gcd(p, q)
  File "/Users/enojb/current/sympy/sympy/sympy/polys/polytools.py", line 5306, in gcd
    (F, G), opt = parallel_poly_from_expr((f, g), *gens, **args)
  File "/Users/enojb/current/sympy/sympy/sympy/polys/polytools.py", line 4340, in parallel_poly_from_expr
    return _parallel_poly_from_expr(exprs, opt)
  File "/Users/enojb/current/sympy/sympy/sympy/polys/polytools.py", line 4399, in _parallel_poly_from_expr
    raise PolynomialError("Piecewise generators do not make sense")
sympy.polys.polyerrors.PolynomialError: Piecewise generators do not make sense
```
The issue arises during a query in the old assumptions. The exponential function checks if its argument is zero here:
https://github.com/sympy/sympy/blob/624217179aaf8d094e6ff75b7493ad1ee47599b0/sympy/functions/elementary/exponential.py#L369
That gives:
```python
In [1]: x, y, z = symbols('x y z', real=True)

In [2]: sinh(Piecewise((x, y > x), (y, True)) * z**-1.0).is_zero
---------------------------------------------------------------------------
KeyError
```
Before processing the assumptions query the value of the queried assumption is stored as `None` here:
https://github.com/sympy/sympy/blob/624217179aaf8d094e6ff75b7493ad1ee47599b0/sympy/core/assumptions.py#L491-L493
That `None` remains there if an exception is raised during the query:
```python
In [1]: x, y, z = symbols('x y z', real=True)

In [2]: S = sinh(Piecewise((x, y > x), (y, True)) * z**-1.0)

In [3]: S._assumptions
Out[3]: {}

In [4]: try:
   ...:     S.is_zero
   ...: except Exception as e:
   ...:     print(e)
   ...: 
Piecewise generators do not make sense

In [5]: S._assumptions
Out[5]: 
{'zero': None,
 'extended_positive': None,
 'extended_real': None,
 'negative': None,
 'commutative': True,
 'extended_negative': None,
 'positive': None,
 'real': None}
```
A subsequent call to create the same expression returns the same object due to the cache and the object still has `None` is its assumptions dict:
```python
In [6]: S2 = sinh(Piecewise((x, y > x), (y, True)) * z**-1.0)

In [7]: S2 is S
Out[7]: True

In [8]: S2._assumptions
Out[8]: 
{'zero': None,
 'extended_positive': None,
 'extended_real': None,
 'negative': None,
 'commutative': True,
 'extended_negative': None,
 'positive': None,
 'real': None}

In [9]: S2.is_zero

In [10]: exp(sinh(Piecewise((x, y > x), (y, True)) * z**-1.0))
Out[10]: 
     ⎛ -1.0 ⎛⎧x  for x < y⎞⎞
 sinh⎜z    ⋅⎜⎨            ⎟⎟
     ⎝      ⎝⎩y  otherwise⎠⎠
ℯ  
```
Subsequent `is_zero` checks just return `None` from the assumptions dict without calling the handlers so they pass without raising.

The reason the `is_zero` handler raises first time around is due to the `sinh.is_real` handler which does this:
https://github.com/sympy/sympy/blob/624217179aaf8d094e6ff75b7493ad1ee47599b0/sympy/functions/elementary/hyperbolic.py#L250-L251
The `%` leads to `Mod` with the Piecewise which calls `gcd` as @jksuom showed above.

There are a few separate issues here:

1. The old assumptions system stores `None` when running a query but doesn't remove that `None` when an exception is raised.
2. `Mod` calls `gcd` on the argument when it is a Piecewise and `gcd` without catching the possible exception..
3. The `gcd` function raises an exception when given a `Piecewise`.

The fix suggested by @jksuom is for 2. which seems reasonable and I think we can merge a PR for that to fix using `Piecewise` with `Mod`.

I wonder about 3. as well though. Should `gcd` with a `Piecewise` raise an exception? If so then maybe `Mod` shouldn't be calling `gcd` at all. Perhaps just something like `gcd_terms` or `factor_terms` should be used there.

For point 1. I think that really the best solution is not putting `None` into the assumptions dict at all as there are other ways that it can lead to non-deterministic behaviour. Removing that line leads to a lot of different examples of RecursionError though (personally I consider each of those to be a bug in the old assumptions system).
I'll put a PR together. And, ah I see, yes you are right - good point (regarding TF float exponents).

I cannot comment on 1 as I'm not really familiar with the assumptions systems. But, regarding 3, would this exception make more sense as a `NotImplementedError` in `gcd`? Consider the potential behavior where `gcd` is applied to each condition of a `Piecewise` expression:

```python
In [1]: expr = Piecewise((x, x > 2), (2, True))

In [2]: expr
Out[2]: 
⎧x  for x > 2
⎨            
⎩2  otherwise

In [3]: gcd(x, x)
Out[3]: x

In [4]: gcd(2, x)
Out[4]: 1

In [5]: gcd(expr, x)  # current behavior
PolynomialError: Piecewise generators do not make sense

In [6]: gcd(expr, x)  # potential new behavior?
Out[6]: 
⎧x  for x > 2
⎨            
⎩1  otherwise
```

That would be what I expect from `gcd` here. For the `gcd` of two `Piecewise` expressions, this gets messier and I think would involve intersecting sets of conditions.

## Patch

```diff

diff --git a/sympy/core/mod.py b/sympy/core/mod.py
--- a/sympy/core/mod.py
+++ b/sympy/core/mod.py
@@ -40,6 +40,7 @@ def eval(cls, p, q):
         from sympy.core.mul import Mul
         from sympy.core.singleton import S
         from sympy.core.exprtools import gcd_terms
+        from sympy.polys.polyerrors import PolynomialError
         from sympy.polys.polytools import gcd
 
         def doit(p, q):
@@ -166,10 +167,13 @@ def doit(p, q):
         # XXX other possibilities?
 
         # extract gcd; any further simplification should be done by the user
-        G = gcd(p, q)
-        if G != 1:
-            p, q = [
-                gcd_terms(i/G, clear=False, fraction=False) for i in (p, q)]
+        try:
+            G = gcd(p, q)
+            if G != 1:
+                p, q = [gcd_terms(i/G, clear=False, fraction=False)
+                        for i in (p, q)]
+        except PolynomialError:  # issue 21373
+            G = S.One
         pwas, qwas = p, q
 
         # simplify terms


```

## Test Patch

```diff
diff --git a/sympy/core/tests/test_arit.py b/sympy/core/tests/test_arit.py
--- a/sympy/core/tests/test_arit.py
+++ b/sympy/core/tests/test_arit.py
@@ -1913,6 +1913,16 @@ def test_Mod():
     assert Mod(x, y).rewrite(floor) == x - y*floor(x/y)
     assert ((x - Mod(x, y))/y).rewrite(floor) == floor(x/y)
 
+    # issue 21373
+    from sympy.functions.elementary.trigonometric import sinh
+    from sympy.functions.elementary.piecewise import Piecewise
+
+    x_r, y_r = symbols('x_r y_r', real=True)
+    (Piecewise((x_r, y_r > x_r), (y_r, True)) / z) % 1
+    expr = exp(sinh(Piecewise((x_r, y_r > x_r), (y_r, True)) / z))
+    expr.subs({1: 1.0})
+    sinh(Piecewise((x_r, y_r > x_r), (y_r, True)) * z ** -1.0).is_zero
+
 
 def test_Mod_Pow():
     # modular exponentiation

```

## Test Information

**Tests that should FAIL→PASS**: ["test_Mod"]

**Tests that should PASS→PASS**: ["test_bug1", "test_Symbol", "test_arit0", "test_div", "test_pow", "test_pow2", "test_pow3", "test_mod_pow", "test_pow_E", "test_pow_issue_3516", "test_pow_im", "test_real_mul", "test_ncmul", "test_mul_add_identity", "test_ncpow", "test_powerbug", "test_Mul_doesnt_expand_exp", "test_Mul_is_integer", "test_Add_Mul_is_integer", "test_Add_Mul_is_finite", "test_Mul_is_even_odd", "test_evenness_in_ternary_integer_product_with_even", "test_oddness_in_ternary_integer_product_with_even", "test_Mul_is_rational", "test_Add_is_rational", "test_Add_is_even_odd", "test_Mul_is_negative_positive", "test_Mul_is_negative_positive_2", "test_Mul_is_nonpositive_nonnegative", "test_Add_is_negative_positive", "test_Add_is_nonpositive_nonnegative", "test_Pow_is_integer", "test_Pow_is_real", "test_real_Pow", "test_Pow_is_finite", "test_Pow_is_even_odd", "test_Pow_is_negative_positive", "test_Pow_is_zero", "test_Pow_is_nonpositive_nonnegative", "test_Mul_is_imaginary_real", "test_Mul_hermitian_antihermitian", "test_Add_is_comparable", "test_Mul_is_comparable", "test_Pow_is_comparable", "test_Add_is_positive_2", "test_Add_is_irrational", "test_Mul_is_irrational", "test_issue_3531", "test_issue_3531b", "test_bug3", "test_suppressed_evaluation", "test_AssocOp_doit", "test_Add_Mul_Expr_args", "test_Add_as_coeff_mul", "test_Pow_as_coeff_mul_doesnt_expand", "test_issue_3514_18626", "test_make_args", "test_issue_5126", "test_Rational_as_content_primitive", "test_Add_as_content_primitive", "test_Mul_as_content_primitive", "test_Pow_as_content_primitive", "test_issue_5460", "test_product_irrational", "test_issue_5919", "test_Mod_Pow", "test_Mod_is_integer", "test_Mod_is_nonposneg", "test_issue_6001", "test_polar", "test_issue_6040", "test_issue_6082", "test_issue_6077", "test_mul_flatten_oo", "test_add_flatten", "test_issue_5160_6087_6089_6090", "test_float_int_round", "test_issue_6611a", "test_denest_add_mul", "test_mul_coeff", "test_mul_zero_detection", "test_Mul_with_zero_infinite", "test_Mul_does_not_cancel_infinities", "test_Mul_does_not_distribute_infinity", "test_issue_8247_8354", "test_Add_is_zero", "test_issue_14392", "test_divmod", "test__neg__", "test_issue_18507", "test_issue_17130"]

**Base Commit**: 624217179aaf8d094e6ff75b7493ad1ee47599b0
**Environment Setup Commit**: f9a6f50ec0c74d935c50a6e9c9b2cb0469570d91
