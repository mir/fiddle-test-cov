# sympy__sympy-19487

**Repository**: sympy/sympy
**Created**: 2020-06-04T09:25:34Z
**Version**: 1.7

## Problem Statement

Rewrite sign as abs
In sympy the `sign` function is defined as
```
    sign(z)  :=  z / Abs(z)
```
for all complex non-zero `z`. There should be a way to rewrite the sign in terms of `Abs` e.g.:
```
>>> sign(x).rewrite(Abs)                                                                                                                   
 x 
───
│x│
```
I'm not sure how the possibility of `x` being zero should be handled currently we have
```
>>> sign(0)                                                                                                                               
0
>>> 0 / Abs(0)                                                                                                                            
nan
```
Maybe `sign(0)` should be `nan` as well. Otherwise maybe rewrite as Abs would have to be careful about the possibility of the arg being zero (that would make the rewrite fail in most cases).


## Hints

Getting nan for `sign(0)` would be pretty [non-intuitive](https://en.wikipedia.org/wiki/Sign_function) for any mathematical programmer given it's non-derivative definition.

If a rewrite request cannot be fulfilled under all conditions and the request was not for Piecewise, I think the rewrite should return None.
Actually I think it's fine if the rewrite doesn't always work. At least something like this could rewrite:
```julia
In [2]: sign(1+I).rewrite(Abs)                                                                                                                 
Out[2]: sign(1 + ⅈ)
```
You can use piecewise like
```
Piecewise(
    (0, Eq(x, 0)),
    (x / Abs(x), Ne(x, 0))
)
```
Originally this question comes from SO:
https://stackoverflow.com/questions/61676438/integrating-and-deriving-absolute-functions-sympy/61681347#61681347

The original question was about `diff(Abs(x))`:
```
In [2]: x = Symbol('x', real=True)                                                                                                             

In [3]: Abs(x).diff(x)                                                                                                                         
Out[3]: sign(x)
```
Maybe the result from `diff` should be a `Piecewise` or at least an `ExprCondPair` guarding against `x=0`.
The problem is that real-valued functions like abs, re, im, arg,... are not holomorphic and have no complex derivative. See also https://github.com/sympy/sympy/issues/8502.
@jksuom could we add conditions in the `Derivative` class of the functions module which would check if the expression is an instance of a non-holomorphic function, in such a case it could raise an error or in the case of `Abs` simply  check the domain. I believe all the classes in `sympy/functions/elementary/complexes.py` could be checked.
Would it be possible to add an `_eval_derivative` method raising an error to those functions?
When would it raise?
If the function is non-holomorphic, there is no derivative to be returned.
There is a reasonable derivative of `Abs` when defined over the reals though e.g.:
```julia
In [1]: x = Symbol('x', real=True)                                                                                                

In [2]: Abs(x).diff(x)                                                                                                            
Out[2]: sign(x)
```
Maybe there should be two functions, one defined on reals and the other on complexes.
> Would it be possible to add an `_eval_derivative` method raising an error to those functions?

In the `Derivative` class in `sympy.function`?



> When would it raise?

As suggested, if the function is non-holomorphic or in the case of `Abs()` it could be a check on the domain of the argument.


> Maybe there should be two functions, one defined on reals and the other on complexes.

I am not sure if there are any non-holomorphic functions on Real numbers. In my opinion only the `Abs()` function would fall in this case. Hence I think this could be done using one function only.
```
def _eval_derivative(self, expr):
    if isinstance(expr,[re, im, sign, arg, conjugate]):
	raise TypeError("Derivative not possible for Non-Holomorphic functions")
    if isinstance(expr,Abs):
	if Abs.arg[0].free_symbols.is_complex:
	    raises TypeError("There is a complex argument which makes Abs non-holomorphic")
```
This is something I was thinking but I am not sure about it as `Derivative` class already has a method with the same name. I also think that appropriate changes also need to be made in the `fdiff()` method of the `Abs` class.
@jksuom I wanted to know if there are more non-holomorphic functions in sympy/functions/elementary/complexes.py to which an error can be raised.
Those functions in complexes.py have a `_eval_derivative` method. Maybe that would be the proper place for raising an error if that is desired.
Are there any other examples of functions that raise when differentiated?

I just tried
```julia
In [83]: n = Symbol('n', integer=True, positive=True)                                                                             

In [84]: totient(n).diff(n)                                                                                                       
Out[84]: 
d             
──(totient(n))
dn 
```
@oscarbenjamin I am not sure if this is a situation when it should raise, for example: if `n` here is a prime number the derivative wrt `n` would hence be `1` . Although in sympy 
```
>>> x = Symbol('x', real=True, prime=True)
>>> totient(x).evalf()
ϕ(x)
```
is the output and not `x-1`.Maybe this kind of functionality can be added.
@jksuom I think your way is correct and wanted to ask if the error to be raised is appropriately `TypeError`?
I don't think that the totient function should be differentiable. I was just trying to think of functions where it might be an error to differentiate them.

I think it's better to leave the derivative of Abs unevaluated. You might have something like `Abs(f(x))` where `f` can be substituted for something reasonable later.
@dhruvmendiratta6 Yes, I think that `TypeError` would be the appropriate choice. Note, however, that raising errors would probably break some tests. It may be desirable to add some try-except blocks to handle those properly.
What about something like this:
```julia
In [21]: x = Symbol('x', real=True)                                                                                               

In [22]: f = Function('f')                                                                                                        

In [23]: e = Derivative(Abs(f(x)), x)                                                                                             

In [24]: e                                                                                                                        
Out[24]: 
d         
──(│f(x)│)
dx        

In [25]: e.subs(f, cosh)                                                                                                          
Out[25]: 
d          
──(cosh(x))
dx         

In [26]: e.subs(f, cosh).doit()                                                                                                   
Out[26]: sinh(x)
```
@jksuom @oscarbenjamin 
Any suggestion on how this can be done?
I think changes need to be made here
https://github.com/sympy/sympy/blob/7c11a00d4ace555e8be084d69c4da4e6f4975f64/sympy/functions/elementary/complexes.py#L605-L608
to leave the derivative of `Abs` unevaluated. I tried changing this to 
```
def _eval_derivative(self, x):
        if self.args[0].is_extended_real or self.args[0].is_imaginary:
            return Derivative(self.args[0], x, evaluate=True) \
                * Derivative(self, x, evaluate=False)
```
which gives
```
>>> x = Symbol('x', real = True)
>>> Abs(x**3).diff(x)
x**2*Derivative(Abs(x), x) + 2*x*Abs(x)
```
But then I can't figure out how to evaluate when the need arises.The above result,which I think is wrong, occurs even when no changes are made.
I think rewrite in general can't avoid having situations where things are only defined correctly in the limit, unless we return a Piecewise. For example, `sinc(x).rewrite(sin)`.
```py
>>> pprint(sinc(x).rewrite(sin))
⎧sin(x)
⎪──────  for x ≠ 0
⎨  x
⎪
⎩  1     otherwise
```
I made `_eval_rewrite_as_Abs()` for the `sign` class which gives the following:
```
>>> sign(x).rewrite(Abs)
Piecewise((0, Eq(x, 0)), (x/Abs(x), True))
```
Although as discussed earlier raising an error in `_eval_derivative()` causes some tests to break :
```
File "c:\users\mendiratta\sympy\sympy\functions\elementary\tests\test_complexes.py", line 414, in test_Abs
    assert Abs(x).diff(x) == -sign(x)
 File "c:\users\mendiratta\sympy\sympy\functions\elementary\tests\test_complexes.py", line 833, in test_derivatives_issue_4757
    assert Abs(f(x)).diff(x).subs(f(x), 1 + I*x).doit() == x/sqrt(1 + x**2)
 File "c:\users\mendiratta\sympy\sympy\functions\elementary\tests\test_complexes.py", line 969, in test_issue_15893
    assert eq.doit() == sign(f(x))
```
The first two are understood but in the third one both `f` and `x` are real and still are caught by the newly raised error which doesn't make sense as I raised a `TypeError` only if the argument is not real.

## Patch

```diff

diff --git a/sympy/functions/elementary/complexes.py b/sympy/functions/elementary/complexes.py
--- a/sympy/functions/elementary/complexes.py
+++ b/sympy/functions/elementary/complexes.py
@@ -394,6 +394,9 @@ def _eval_rewrite_as_Heaviside(self, arg, **kwargs):
         if arg.is_extended_real:
             return Heaviside(arg, H0=S(1)/2) * 2 - 1
 
+    def _eval_rewrite_as_Abs(self, arg, **kwargs):
+        return Piecewise((0, Eq(arg, 0)), (arg / Abs(arg), True))
+
     def _eval_simplify(self, **kwargs):
         return self.func(self.args[0].factor())  # XXX include doit?
 


```

## Test Patch

```diff
diff --git a/sympy/core/tests/test_subs.py b/sympy/core/tests/test_subs.py
--- a/sympy/core/tests/test_subs.py
+++ b/sympy/core/tests/test_subs.py
@@ -855,3 +855,10 @@ def test_issue_17823():
 def test_issue_19326():
     x, y = [i(t) for i in map(Function, 'xy')]
     assert (x*y).subs({x: 1 + x, y: x}) == (1 + x)*x
+
+def test_issue_19558():
+    e = (7*x*cos(x) - 12*log(x)**3)*(-log(x)**4 + 2*sin(x) + 1)**2/ \
+    (2*(x*cos(x) - 2*log(x)**3)*(3*log(x)**4 - 7*sin(x) + 3)**2)
+
+    assert e.subs(x, oo) == AccumBounds(-oo, oo)
+    assert (sin(x) + cos(x)).subs(x, oo) == AccumBounds(-2, 2)
diff --git a/sympy/functions/elementary/tests/test_complexes.py b/sympy/functions/elementary/tests/test_complexes.py
--- a/sympy/functions/elementary/tests/test_complexes.py
+++ b/sympy/functions/elementary/tests/test_complexes.py
@@ -4,7 +4,7 @@
     pi, Rational, re, S, sign, sin, sqrt, Symbol, symbols, transpose,
     zoo, exp_polar, Piecewise, Interval, comp, Integral, Matrix,
     ImmutableMatrix, SparseMatrix, ImmutableSparseMatrix, MatrixSymbol,
-    FunctionMatrix, Lambda, Derivative)
+    FunctionMatrix, Lambda, Derivative, Eq)
 from sympy.core.expr import unchanged
 from sympy.core.function import ArgumentIndexError
 from sympy.testing.pytest import XFAIL, raises
@@ -296,11 +296,14 @@ def test_sign():
     assert sign(Symbol('x', real=True, zero=False)).is_nonpositive is None
 
     x, y = Symbol('x', real=True), Symbol('y')
+    f = Function('f')
     assert sign(x).rewrite(Piecewise) == \
         Piecewise((1, x > 0), (-1, x < 0), (0, True))
     assert sign(y).rewrite(Piecewise) == sign(y)
     assert sign(x).rewrite(Heaviside) == 2*Heaviside(x, H0=S(1)/2) - 1
     assert sign(y).rewrite(Heaviside) == sign(y)
+    assert sign(y).rewrite(Abs) == Piecewise((0, Eq(y, 0)), (y/Abs(y), True))
+    assert sign(f(y)).rewrite(Abs) == Piecewise((0, Eq(f(y), 0)), (f(y)/Abs(f(y)), True))
 
     # evaluate what can be evaluated
     assert sign(exp_polar(I*pi)*pi) is S.NegativeOne

```

## Test Information

**Tests that should FAIL→PASS**: ["test_sign"]

**Tests that should PASS→PASS**: ["test_subs", "test_subs_Matrix", "test_subs_AccumBounds", "test_trigonometric", "test_powers", "test_logexppow", "test_bug", "test_subbug1", "test_subbug2", "test_dict_set", "test_dict_ambigous", "test_deriv_sub_bug3", "test_equality_subs1", "test_equality_subs2", "test_issue_3742", "test_subs_dict1", "test_mul", "test_subs_simple", "test_subs_constants", "test_subs_commutative", "test_subs_noncommutative", "test_subs_basic_funcs", "test_subs_wild", "test_subs_mixed", "test_division", "test_add", "test_subs_issue_4009", "test_functions_subs", "test_derivative_subs", "test_derivative_subs2", "test_derivative_subs3", "test_issue_5284", "test_subs_iter", "test_subs_dict", "test_no_arith_subs_on_floats", "test_issue_5651", "test_issue_6075", "test_issue_6079", "test_issue_4680", "test_issue_6158", "test_Function_subs", "test_simultaneous_subs", "test_issue_6419_6421", "test_issue_6559", "test_issue_5261", "test_issue_6923", "test_2arg_hack", "test_noncommutative_subs", "test_issue_2877", "test_issue_5910", "test_issue_5217", "test_issue_10829", "test_pow_eval_subs_no_cache", "test_RootOf_issue_10092", "test_issue_8886", "test_issue_12657", "test_recurse_Application_args", "test_Subs_subs", "test_issue_13333", "test_issue_15234", "test_issue_6976", "test_issue_11746", "test_issue_17823", "test_issue_19326", "test_re", "test_im", "test_as_real_imag", "test_Abs", "test_Abs_rewrite", "test_Abs_real", "test_Abs_properties", "test_abs", "test_arg", "test_arg_rewrite", "test_adjoint", "test_conjugate", "test_conjugate_transpose", "test_transpose", "test_polarify", "test_unpolarify", "test_issue_4035", "test_issue_3206", "test_issue_4754_derivative_conjugate", "test_derivatives_issue_4757", "test_issue_11413", "test_periodic_argument", "test_principal_branch", "test_issue_14216", "test_issue_14238", "test_zero_assumptions"]

**Base Commit**: 25fbcce5b1a4c7e3956e6062930f4a44ce95a632
**Environment Setup Commit**: cffd4e0f86fefd4802349a9f9b19ed70934ea354
