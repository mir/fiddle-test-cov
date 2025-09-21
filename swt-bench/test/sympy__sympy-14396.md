# sympy__sympy-14396

**Repository**: sympy/sympy
**Created**: 2018-03-05T19:18:01Z
**Version**: 1.1

## Problem Statement

Poly(domain='RR[y,z]') doesn't work
``` py
In [14]: Poly(1.2*x*y*z, x)
Out[14]: Poly(1.2*y*z*x, x, domain='RR[y,z]')

In [15]: Poly(1.2*x*y*z, x, domain='RR[y,z]')
---------------------------------------------------------------------------
OptionError                               Traceback (most recent call last)
<ipython-input-15-d83389519ae1> in <module>()
----> 1 Poly(1.2*x*y*z, x, domain='RR[y,z]')

/Users/aaronmeurer/Documents/Python/sympy/sympy-scratch/sympy/polys/polytools.py in __new__(cls, rep, *gens, **args)
     69     def __new__(cls, rep, *gens, **args):
     70         """Create a new polynomial instance out of something useful. """
---> 71         opt = options.build_options(gens, args)
     72
     73         if 'order' in opt:

/Users/aaronmeurer/Documents/Python/sympy/sympy-scratch/sympy/polys/polyoptions.py in build_options(gens, args)
    718
    719     if len(args) != 1 or 'opt' not in args or gens:
--> 720         return Options(gens, args)
    721     else:
    722         return args['opt']

/Users/aaronmeurer/Documents/Python/sympy/sympy-scratch/sympy/polys/polyoptions.py in __init__(self, gens, args, flags, strict)
    151                     self[option] = cls.preprocess(value)
    152
--> 153         preprocess_options(args)
    154
    155         for key, value in dict(defaults).items():

/Users/aaronmeurer/Documents/Python/sympy/sympy-scratch/sympy/polys/polyoptions.py in preprocess_options(args)
    149
    150                 if value is not None:
--> 151                     self[option] = cls.preprocess(value)
    152
    153         preprocess_options(args)

/Users/aaronmeurer/Documents/Python/sympy/sympy-scratch/sympy/polys/polyoptions.py in preprocess(cls, domain)
    480                 return sympy.polys.domains.QQ.algebraic_field(*gens)
    481
--> 482         raise OptionError('expected a valid domain specification, got %s' % domain)
    483
    484     @classmethod

OptionError: expected a valid domain specification, got RR[y,z]
```

Also, the wording of error message could be improved



## Hints

```
In [14]: Poly(1.2*x*y*z, x)
Out[14]: Poly(1.2*y*z*x, x, domain='RR[y,z]')
```
I guess this is quite good

I mean why would we wanna do this
`In [15]: Poly(1.2*x*y*z, x, domain='RR[y,z]')`

BTW, Is this issue still on?
It is still a valid issue. The preprocessing of options should be extended to accept polynomial rings with real coefficients.
Hello, 
I would like to have this issue assigned to me. I want to start contributing, and reading the code I think I can fix this as my first issue.

Thanks
@3nr1c You don't need to have this issue assigned to you; if you have a solution, just send it a PR. Be sure to read [Development workflow](https://github.com/sympy/sympy/wiki/Development-workflow).

## Patch

```diff

diff --git a/sympy/polys/polyoptions.py b/sympy/polys/polyoptions.py
--- a/sympy/polys/polyoptions.py
+++ b/sympy/polys/polyoptions.py
@@ -405,7 +405,7 @@ class Domain(with_metaclass(OptionType, Option)):
     _re_realfield = re.compile(r"^(R|RR)(_(\d+))?$")
     _re_complexfield = re.compile(r"^(C|CC)(_(\d+))?$")
     _re_finitefield = re.compile(r"^(FF|GF)\((\d+)\)$")
-    _re_polynomial = re.compile(r"^(Z|ZZ|Q|QQ)\[(.+)\]$")
+    _re_polynomial = re.compile(r"^(Z|ZZ|Q|QQ|R|RR|C|CC)\[(.+)\]$")
     _re_fraction = re.compile(r"^(Z|ZZ|Q|QQ)\((.+)\)$")
     _re_algebraic = re.compile(r"^(Q|QQ)\<(.+)\>$")
 
@@ -459,8 +459,12 @@ def preprocess(cls, domain):
 
                 if ground in ['Z', 'ZZ']:
                     return sympy.polys.domains.ZZ.poly_ring(*gens)
-                else:
+                elif ground in ['Q', 'QQ']:
                     return sympy.polys.domains.QQ.poly_ring(*gens)
+                elif ground in ['R', 'RR']:
+                    return sympy.polys.domains.RR.poly_ring(*gens)
+                else:
+                    return sympy.polys.domains.CC.poly_ring(*gens)
 
             r = cls._re_fraction.match(domain)
 


```

## Test Patch

```diff
diff --git a/sympy/polys/tests/test_polyoptions.py b/sympy/polys/tests/test_polyoptions.py
--- a/sympy/polys/tests/test_polyoptions.py
+++ b/sympy/polys/tests/test_polyoptions.py
@@ -6,7 +6,7 @@
     Frac, Formal, Polys, Include, All, Gen, Symbols, Method)
 
 from sympy.polys.orderings import lex
-from sympy.polys.domains import FF, GF, ZZ, QQ, EX
+from sympy.polys.domains import FF, GF, ZZ, QQ, RR, CC, EX
 
 from sympy.polys.polyerrors import OptionError, GeneratorsError
 
@@ -176,15 +176,23 @@ def test_Domain_preprocess():
 
     assert Domain.preprocess('Z[x]') == ZZ[x]
     assert Domain.preprocess('Q[x]') == QQ[x]
+    assert Domain.preprocess('R[x]') == RR[x]
+    assert Domain.preprocess('C[x]') == CC[x]
 
     assert Domain.preprocess('ZZ[x]') == ZZ[x]
     assert Domain.preprocess('QQ[x]') == QQ[x]
+    assert Domain.preprocess('RR[x]') == RR[x]
+    assert Domain.preprocess('CC[x]') == CC[x]
 
     assert Domain.preprocess('Z[x,y]') == ZZ[x, y]
     assert Domain.preprocess('Q[x,y]') == QQ[x, y]
+    assert Domain.preprocess('R[x,y]') == RR[x, y]
+    assert Domain.preprocess('C[x,y]') == CC[x, y]
 
     assert Domain.preprocess('ZZ[x,y]') == ZZ[x, y]
     assert Domain.preprocess('QQ[x,y]') == QQ[x, y]
+    assert Domain.preprocess('RR[x,y]') == RR[x, y]
+    assert Domain.preprocess('CC[x,y]') == CC[x, y]
 
     raises(OptionError, lambda: Domain.preprocess('Z()'))
 

```

## Test Information

**Tests that should FAIL→PASS**: ["test_Domain_preprocess"]

**Tests that should PASS→PASS**: ["test_Options_clone", "test_Expand_preprocess", "test_Expand_postprocess", "test_Gens_preprocess", "test_Gens_postprocess", "test_Wrt_preprocess", "test_Wrt_postprocess", "test_Sort_preprocess", "test_Sort_postprocess", "test_Order_preprocess", "test_Order_postprocess", "test_Field_preprocess", "test_Field_postprocess", "test_Greedy_preprocess", "test_Greedy_postprocess", "test_Domain_postprocess", "test_Split_preprocess", "test_Split_postprocess", "test_Gaussian_preprocess", "test_Gaussian_postprocess", "test_Extension_preprocess", "test_Extension_postprocess", "test_Modulus_preprocess", "test_Modulus_postprocess", "test_Symmetric_preprocess", "test_Symmetric_postprocess", "test_Strict_preprocess", "test_Strict_postprocess", "test_Auto_preprocess", "test_Auto_postprocess", "test_Frac_preprocess", "test_Frac_postprocess", "test_Formal_preprocess", "test_Formal_postprocess", "test_Polys_preprocess", "test_Polys_postprocess", "test_Include_preprocess", "test_Include_postprocess", "test_All_preprocess", "test_All_postprocess", "test_Gen_postprocess", "test_Symbols_preprocess", "test_Symbols_postprocess", "test_Method_preprocess"]

**Base Commit**: f35ad6411f86a15dd78db39c29d1e5291f66f9b5
**Environment Setup Commit**: ec9e3c0436fbff934fa84e22bf07f1b3ef5bfac3
