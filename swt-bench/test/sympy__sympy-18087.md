# sympy__sympy-18087

**Repository**: sympy/sympy
**Created**: 2019-12-20T12:38:00Z
**Version**: 1.6

## Problem Statement

Simplify of simple trig expression fails
trigsimp in various versions, including 1.5, incorrectly simplifies cos(x)+sqrt(sin(x)**2) as though it were cos(x)+sin(x) for general complex x. (Oddly it gets this right if x is real.)

Embarrassingly I found this by accident while writing sympy-based teaching material...



## Hints

I guess you mean this:
```julia
In [16]: cos(x) + sqrt(sin(x)**2)                                                                                                 
Out[16]: 
   _________         
  ╱    2             
╲╱  sin (x)  + cos(x)

In [17]: simplify(cos(x) + sqrt(sin(x)**2))                                                                                       
Out[17]: 
      ⎛    π⎞
√2⋅sin⎜x + ─⎟
      ⎝    4⎠
```
Which is incorrect if `sin(x)` is negative:
```julia
In [27]: (cos(x) + sqrt(sin(x)**2)).evalf(subs={x:-1})                                                                            
Out[27]: 1.38177329067604

In [28]: simplify(cos(x) + sqrt(sin(x)**2)).evalf(subs={x:-1})                                                                    
Out[28]: -0.301168678939757
```
For real x this works because the sqrt auto simplifies to abs before simplify is called:
```julia
In [18]: x = Symbol('x', real=True)                                                                                               

In [19]: simplify(cos(x) + sqrt(sin(x)**2))                                                                                       
Out[19]: cos(x) + │sin(x)│

In [20]: cos(x) + sqrt(sin(x)**2)                                                                                                 
Out[20]: cos(x) + │sin(x)│
```
Yes, that's the issue I mean.
`fu` and `trigsimp` return the same erroneous simplification. All three simplification functions end up in Fu's `TR10i()` and this is what it returns:
```
In [5]: from sympy.simplify.fu import *

In [6]: e = cos(x) + sqrt(sin(x)**2)

In [7]: TR10i(sqrt(sin(x)**2))
Out[7]: 
   _________
  ╱    2    
╲╱  sin (x) 

In [8]: TR10i(e)
Out[8]: 
      ⎛    π⎞
√2⋅sin⎜x + ─⎟
      ⎝    4⎠
```
The other `TR*` functions keep the `sqrt` around, it's only `TR10i` that mishandles it. (Or it's called with an expression outside its scope of application...)
I tracked down where the invalid simplification of `sqrt(x**2)` takes place or at least I think so:
`TR10i` calls `trig_split` (also in fu.py) where the line
https://github.com/sympy/sympy/blob/0d99c52566820e9a5bb72eaec575fce7c0df4782/sympy/simplify/fu.py#L1901
in essence applies `._as_expr()` to `Factors({sin(x)**2: S.Half})` which then returns `sin(x)`.

If I understand `Factors` (sympy.core.exprtools) correctly, its intent is to have an efficient internal representation of products and `.as_expr()` is supposed to reconstruct a standard expression from such a representation. But here's what it does to a general complex variable `x`:
```
In [21]: Factors(sqrt(x**2))
Out[21]: Factors({x**2: 1/2})
In [22]: _.as_expr()
Out[22]: x
```
It seems line 455 below
https://github.com/sympy/sympy/blob/0d99c52566820e9a5bb72eaec575fce7c0df4782/sympy/core/exprtools.py#L449-L458
unconditionally multiplies exponents if a power of a power is encountered. However this is not generally valid for non-integer exponents...

And line 457 does the same for other non-integer exponents:
```
In [23]: Factors((x**y)**z)
Out[23]: Factors({x**y: z})

In [24]: _.as_expr()
Out[24]:
 y⋅z
x
```

## Patch

```diff

diff --git a/sympy/core/exprtools.py b/sympy/core/exprtools.py
--- a/sympy/core/exprtools.py
+++ b/sympy/core/exprtools.py
@@ -358,8 +358,8 @@ def __init__(self, factors=None):  # Factors
             for f in list(factors.keys()):
                 if isinstance(f, Rational) and not isinstance(f, Integer):
                     p, q = Integer(f.p), Integer(f.q)
-                    factors[p] = (factors[p] if p in factors else 0) + factors[f]
-                    factors[q] = (factors[q] if q in factors else 0) - factors[f]
+                    factors[p] = (factors[p] if p in factors else S.Zero) + factors[f]
+                    factors[q] = (factors[q] if q in factors else S.Zero) - factors[f]
                     factors.pop(f)
             if i:
                 factors[I] = S.One*i
@@ -448,14 +448,12 @@ def as_expr(self):  # Factors
         args = []
         for factor, exp in self.factors.items():
             if exp != 1:
-                b, e = factor.as_base_exp()
-                if isinstance(exp, int):
-                    e = _keep_coeff(Integer(exp), e)
-                elif isinstance(exp, Rational):
+                if isinstance(exp, Integer):
+                    b, e = factor.as_base_exp()
                     e = _keep_coeff(exp, e)
+                    args.append(b**e)
                 else:
-                    e *= exp
-                args.append(b**e)
+                    args.append(factor**exp)
             else:
                 args.append(factor)
         return Mul(*args)


```

## Test Patch

```diff
diff --git a/sympy/core/tests/test_exprtools.py b/sympy/core/tests/test_exprtools.py
--- a/sympy/core/tests/test_exprtools.py
+++ b/sympy/core/tests/test_exprtools.py
@@ -27,6 +27,8 @@ def test_Factors():
     assert Factors({x: 2, y: 3, sin(x): 4}).as_expr() == x**2*y**3*sin(x)**4
     assert Factors(S.Infinity) == Factors({oo: 1})
     assert Factors(S.NegativeInfinity) == Factors({oo: 1, -1: 1})
+    # issue #18059:
+    assert Factors((x**2)**S.Half).as_expr() == (x**2)**S.Half
 
     a = Factors({x: 5, y: 3, z: 7})
     b = Factors({      y: 4, z: 3, t: 10})
diff --git a/sympy/simplify/tests/test_fu.py b/sympy/simplify/tests/test_fu.py
--- a/sympy/simplify/tests/test_fu.py
+++ b/sympy/simplify/tests/test_fu.py
@@ -276,6 +276,9 @@ def test_fu():
     expr = Mul(*[cos(2**i) for i in range(10)])
     assert fu(expr) == sin(1024)/(1024*sin(1))
 
+    # issue #18059:
+    assert fu(cos(x) + sqrt(sin(x)**2)) == cos(x) + sqrt(sin(x)**2)
+
 
 def test_objective():
     assert fu(sin(x)/cos(x), measure=lambda x: x.count_ops()) == \

```

## Test Information

**Tests that should FAIL→PASS**: ["test_Factors", "test_fu"]

**Tests that should PASS→PASS**: ["test_decompose_power", "test_Term", "test_gcd_terms", "test_factor_terms", "test_xreplace", "test_factor_nc", "test_issue_6360", "test_issue_7903", "test_issue_8263", "test_monotonic_sign", "test_TR1", "test_TR2", "test_TR2i", "test_TR3", "test__TR56", "test_TR5", "test_TR6", "test_TR7", "test_TR8", "test_TR9", "test_TR10", "test_TR10i", "test_TR11", "test_TR12", "test_TR13", "test_L", "test_objective", "test_process_common_addends", "test_trig_split", "test_TRmorrie", "test_TRpower", "test_hyper_as_trig", "test_TR12i", "test_TR14", "test_TR15_16_17"]

**Base Commit**: 9da013ad0ddc3cd96fe505f2e47c63e372040916
**Environment Setup Commit**: 28b41c73c12b70d6ad9f6e45109a80649c4456da
