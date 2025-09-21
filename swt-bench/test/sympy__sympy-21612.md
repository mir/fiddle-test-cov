# sympy__sympy-21612

**Repository**: sympy/sympy
**Created**: 2021-06-14T04:31:24Z
**Version**: 1.9

## Problem Statement

Latex parsing of fractions yields wrong expression due to missing brackets
Problematic latex expression: `"\\frac{\\frac{a^3+b}{c}}{\\frac{1}{c^2}}"`

is parsed to: `((a**3 + b)/c)/1/(c**2)`.

Expected is: `((a**3 + b)/c)/(1/(c**2))`. 

The missing brackets in the denominator result in a wrong expression.

## Tested on

- 1.8
- 1.6.2

## Reproduce:

```
root@d31ef1c26093:/# python3
Python 3.6.9 (default, Jan 26 2021, 15:33:00)
[GCC 8.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from sympy.parsing.latex import parse_latex
>>> parse_latex("\\frac{\\frac{a^3+b}{c}}{\\frac{1}{c^2}}")
((a**3 + b)/c)/1/(c**2)




## Hints

This can be further simplified and fails with 

````python
>>> parse_latex("\\frac{a}{\\frac{1}{b}}")
a/1/b
````
but works with a slighty different expression correctly (although the double brackets are not necessary):

````python
>>> parse_latex("\\frac{a}{\\frac{b}{c}}")
a/((b/c))
````
> This can be further simplified and fails with

This is a printing, not a parsing error. If you look at the args of the result they are `(a, 1/(1/b))`
This can be fixed with 
```diff
diff --git a/sympy/printing/str.py b/sympy/printing/str.py
index c3fdcdd435..3e4b7d1b19 100644
--- a/sympy/printing/str.py
+++ b/sympy/printing/str.py
@@ -333,7 +333,7 @@ def apow(i):
                     b.append(apow(item))
                 else:
                     if (len(item.args[0].args) != 1 and
-                            isinstance(item.base, Mul)):
+                            isinstance(item.base, (Mul, Pow))):
                         # To avoid situations like #14160
                         pow_paren.append(item)
                     b.append(item.base)
diff --git a/sympy/printing/tests/test_str.py b/sympy/printing/tests/test_str.py
index 690b1a8bbf..68c7d63769 100644
--- a/sympy/printing/tests/test_str.py
+++ b/sympy/printing/tests/test_str.py
@@ -252,6 +252,8 @@ def test_Mul():
     # For issue 14160
     assert str(Mul(-2, x, Pow(Mul(y,y,evaluate=False), -1, evaluate=False),
                                                 evaluate=False)) == '-2*x/(y*y)'
+    # issue 21537
+    assert str(Mul(x, Pow(1/y, -1, evaluate=False), evaluate=False)) == 'x/(1/y)'
 
 
     class CustomClass1(Expr):
```
@smichr That's great, thank you for the quick fix! This works fine here now with all the test cases.

I did not even consider that this is connected to printing and took the expression at face value. 

## Patch

```diff

diff --git a/sympy/printing/str.py b/sympy/printing/str.py
--- a/sympy/printing/str.py
+++ b/sympy/printing/str.py
@@ -333,7 +333,7 @@ def apow(i):
                     b.append(apow(item))
                 else:
                     if (len(item.args[0].args) != 1 and
-                            isinstance(item.base, Mul)):
+                            isinstance(item.base, (Mul, Pow))):
                         # To avoid situations like #14160
                         pow_paren.append(item)
                     b.append(item.base)


```

## Test Patch

```diff
diff --git a/sympy/printing/tests/test_str.py b/sympy/printing/tests/test_str.py
--- a/sympy/printing/tests/test_str.py
+++ b/sympy/printing/tests/test_str.py
@@ -252,6 +252,8 @@ def test_Mul():
     # For issue 14160
     assert str(Mul(-2, x, Pow(Mul(y,y,evaluate=False), -1, evaluate=False),
                                                 evaluate=False)) == '-2*x/(y*y)'
+    # issue 21537
+    assert str(Mul(x, Pow(1/y, -1, evaluate=False), evaluate=False)) == 'x/(1/y)'
 
 
     class CustomClass1(Expr):

```

## Test Information

**Tests that should FAIL→PASS**: ["test_Mul"]

**Tests that should PASS→PASS**: ["test_printmethod", "test_Abs", "test_Add", "test_Catalan", "test_ComplexInfinity", "test_Derivative", "test_dict", "test_Dict", "test_Dummy", "test_EulerGamma", "test_Exp", "test_factorial", "test_Function", "test_Geometry", "test_GoldenRatio", "test_TribonacciConstant", "test_ImaginaryUnit", "test_Infinity", "test_Integer", "test_Integral", "test_Interval", "test_AccumBounds", "test_Lambda", "test_Limit", "test_list", "test_Matrix_str", "test_NaN", "test_NegativeInfinity", "test_Order", "test_Permutation_Cycle", "test_Pi", "test_Poly", "test_PolyRing", "test_FracField", "test_PolyElement", "test_FracElement", "test_GaussianInteger", "test_GaussianRational", "test_Pow", "test_sqrt", "test_Rational", "test_Float", "test_Relational", "test_AppliedBinaryRelation", "test_CRootOf", "test_RootSum", "test_GroebnerBasis", "test_set", "test_SparseMatrix", "test_Sum", "test_Symbol", "test_tuple", "test_Series_str", "test_TransferFunction_str", "test_Parallel_str", "test_Feedback_str", "test_Quaternion_str_printer", "test_Quantity_str", "test_wild_str", "test_wild_matchpy", "test_zeta", "test_issue_3101", "test_issue_3103", "test_issue_4021", "test_sstrrepr", "test_infinity", "test_full_prec", "test_noncommutative", "test_empty_printer", "test_settings", "test_RandomDomain", "test_FiniteSet", "test_UniversalSet", "test_PrettyPoly", "test_categories", "test_Tr", "test_issue_6387", "test_MatMul_MatAdd", "test_MatrixSlice", "test_true_false", "test_Equivalent", "test_Xor", "test_Complement", "test_SymmetricDifference", "test_UnevaluatedExpr", "test_MatrixElement_printing", "test_MatrixSymbol_printing", "test_MatrixExpressions", "test_Subs_printing", "test_issue_15716", "test_str_special_matrices", "test_issue_14567", "test_issue_21119_21460", "test_Str", "test_diffgeom", "test_NDimArray", "test_Predicate", "test_AppliedPredicate"]

**Base Commit**: b4777fdcef467b7132c055f8ac2c9a5059e6a145
**Environment Setup Commit**: f9a6f50ec0c74d935c50a6e9c9b2cb0469570d91
