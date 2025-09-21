# sympy__sympy-21847

**Repository**: sympy/sympy
**Created**: 2021-08-10T17:41:59Z
**Version**: 1.9

## Problem Statement

itermonomials returns incorrect monomials when using min_degrees argument
`itermonomials` returns incorrect monomials when using optional `min_degrees` argument

For example, the following code introduces three symbolic variables and generates monomials with max and min degree of 3:


```
import sympy as sp
from sympy.polys.orderings import monomial_key

x1, x2, x3 = sp.symbols('x1, x2, x3')
states = [x1, x2, x3]
max_degrees = 3
min_degrees = 3
monomials = sorted(sp.itermonomials(states, max_degrees, min_degrees=min_degrees), 
                   key=monomial_key('grlex', states))
print(monomials)
```
The code returns `[x3**3, x2**3, x1**3]`, when it _should_ also return monomials such as `x1*x2**2, x2*x3**2, etc...` that also have total degree of 3. This behaviour is inconsistent with the documentation that states that 

> A generator of all monomials `monom` is returned, such that either `min_degree <= total_degree(monom) <= max_degree`...

The monomials are also missing when `max_degrees` is increased above `min_degrees`.


## Hints

Doesn't look like the `min_degrees` argument is actually used anywhere in the codebase. Also there don't seem to be any nontrivial tests for passing `min_degrees` as an integer.

The issue would be fixed with this diff and some tests in `test_monomials.py`:
```diff
diff --git a/sympy/polys/monomials.py b/sympy/polys/monomials.py
index 0e84403307..d2cd3451e5 100644
--- a/sympy/polys/monomials.py
+++ b/sympy/polys/monomials.py
@@ -127,7 +127,7 @@ def itermonomials(variables, max_degrees, min_degrees=None):
                 for variable in item:
                     if variable != 1:
                         powers[variable] += 1
-                if max(powers.values()) >= min_degree:
+                if sum(powers.values()) >= min_degree:
                     monomials_list_comm.append(Mul(*item))
             yield from set(monomials_list_comm)
         else:
@@ -139,7 +139,7 @@ def itermonomials(variables, max_degrees, min_degrees=None):
                 for variable in item:
                     if variable != 1:
                         powers[variable] += 1
-                if max(powers.values()) >= min_degree:
+                if sum(powers.values()) >= min_degree:
                     monomials_list_non_comm.append(Mul(*item))
             yield from set(monomials_list_non_comm)
     else:
```


## Patch

```diff

diff --git a/sympy/polys/monomials.py b/sympy/polys/monomials.py
--- a/sympy/polys/monomials.py
+++ b/sympy/polys/monomials.py
@@ -127,7 +127,7 @@ def itermonomials(variables, max_degrees, min_degrees=None):
                 for variable in item:
                     if variable != 1:
                         powers[variable] += 1
-                if max(powers.values()) >= min_degree:
+                if sum(powers.values()) >= min_degree:
                     monomials_list_comm.append(Mul(*item))
             yield from set(monomials_list_comm)
         else:
@@ -139,7 +139,7 @@ def itermonomials(variables, max_degrees, min_degrees=None):
                 for variable in item:
                     if variable != 1:
                         powers[variable] += 1
-                if max(powers.values()) >= min_degree:
+                if sum(powers.values()) >= min_degree:
                     monomials_list_non_comm.append(Mul(*item))
             yield from set(monomials_list_non_comm)
     else:


```

## Test Patch

```diff
diff --git a/sympy/polys/tests/test_monomials.py b/sympy/polys/tests/test_monomials.py
--- a/sympy/polys/tests/test_monomials.py
+++ b/sympy/polys/tests/test_monomials.py
@@ -15,7 +15,6 @@
 from sympy.core import S, symbols
 from sympy.testing.pytest import raises
 
-
 def test_monomials():
 
     # total_degree tests
@@ -114,6 +113,9 @@ def test_monomials():
     assert set(itermonomials([x], [3], [1])) == {x, x**3, x**2}
     assert set(itermonomials([x], [3], [2])) == {x**3, x**2}
 
+    assert set(itermonomials([x, y], 3, 3)) == {x**3, x**2*y, x*y**2, y**3}
+    assert set(itermonomials([x, y], 3, 2)) == {x**2, x*y, y**2, x**3, x**2*y, x*y**2, y**3}
+
     assert set(itermonomials([x, y], [0, 0])) == {S.One}
     assert set(itermonomials([x, y], [0, 1])) == {S.One, y}
     assert set(itermonomials([x, y], [0, 2])) == {S.One, y, y**2}
@@ -132,6 +134,15 @@ def test_monomials():
             {S.One, y**2, x*y**2, x, x*y, x**2, x**2*y**2, y, x**2*y}
 
     i, j, k = symbols('i j k', commutative=False)
+    assert set(itermonomials([i, j, k], 2, 2)) == \
+            {k*i, i**2, i*j, j*k, j*i, k**2, j**2, k*j, i*k}
+    assert set(itermonomials([i, j, k], 3, 2)) == \
+            {j*k**2, i*k**2, k*i*j, k*i**2, k**2, j*k*j, k*j**2, i*k*i, i*j,
+                    j**2*k, i**2*j, j*i*k, j**3, i**3, k*j*i, j*k*i, j*i,
+                    k**2*j, j*i**2, k*j, k*j*k, i*j*i, j*i*j, i*j**2, j**2,
+                    k*i*k, i**2, j*k, i*k, i*k*j, k**3, i**2*k, j**2*i, k**2*i,
+                    i*j*k, k*i
+            }
     assert set(itermonomials([i, j, k], [0, 0, 0])) == {S.One}
     assert set(itermonomials([i, j, k], [0, 0, 1])) == {1, k}
     assert set(itermonomials([i, j, k], [0, 1, 0])) == {1, j}

```

## Test Information

**Tests that should FAIL→PASS**: ["test_monomials"]

**Tests that should PASS→PASS**: ["test_monomial_count", "test_monomial_mul", "test_monomial_div", "test_monomial_gcd", "test_monomial_lcm", "test_monomial_max", "test_monomial_pow", "test_monomial_min", "test_monomial_divides"]

**Base Commit**: d9b18c518d64d0ebe8e35a98c2fb519938b9b151
**Environment Setup Commit**: f9a6f50ec0c74d935c50a6e9c9b2cb0469570d91
