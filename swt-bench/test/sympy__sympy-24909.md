# sympy__sympy-24909

**Repository**: sympy/sympy
**Created**: 2023-03-13T14:24:25Z
**Version**: 1.13

## Problem Statement

Bug with milli prefix
What happened:
```
In [1]: from sympy.physics.units import milli, W
In [2]: milli*W == 1
Out[2]: True
In [3]: W*milli
Out[3]: watt*Prefix(milli, m, -3, 10)
```
What I expected to happen: milli*W should evaluate to milli watts / mW

`milli*W` or more generally `milli` times some unit evaluates to the number 1. I have tried this with Watts and Volts, I'm not sure what other cases this happens. I'm using sympy version 1.11.1-1 on Arch Linux with Python 3.10.9. If you cannot reproduce I would be happy to be of any assitance.


## Hints

I get a 1 for all of the following (and some are redundant like "V" and "volt"):
```python
W, joule, ohm, newton, volt, V, v, volts, henrys, pa, kilogram, ohms, kilograms, Pa, weber, tesla, Wb, H, wb, newtons, kilometers, webers, pascals, kilometer, watt, T, km, kg, joules, pascal, watts, J, henry, kilo, teslas
```
Plus it's only milli.
```
In [65]: for p in PREFIXES:
    ...:     print(p, PREFIXES[p]*W)
    ...:
Y 1000000000000000000000000*watt
Z 1000000000000000000000*watt
E 1000000000000000000*watt
P 1000000000000000*watt
T 1000000000000*watt
G 1000000000*watt
M 1000000*watt
k 1000*watt
h 100*watt
da 10*watt
d watt/10
c watt/100
m 1
mu watt/1000000
n watt/1000000000
p watt/1000000000000
f watt/1000000000000000
a watt/1000000000000000000
z watt/1000000000000000000000
y watt/1000000000000000000000000
```
Dear team,

I am excited to contribute to this project and offer my skills. Please let me support the team's efforts and collaborate effectively. Looking forward to working with you all.
@Sourabh5768  Thanks for showing interest, you don't need to ask for a contribution If you know how to fix an issue, you can just make a pull request to fix it.

## Patch

```diff

diff --git a/sympy/physics/units/prefixes.py b/sympy/physics/units/prefixes.py
--- a/sympy/physics/units/prefixes.py
+++ b/sympy/physics/units/prefixes.py
@@ -6,7 +6,7 @@
 """
 from sympy.core.expr import Expr
 from sympy.core.sympify import sympify
-
+from sympy.core.singleton import S
 
 class Prefix(Expr):
     """
@@ -85,9 +85,9 @@ def __mul__(self, other):
 
         fact = self.scale_factor * other.scale_factor
 
-        if fact == 1:
-            return 1
-        elif isinstance(other, Prefix):
+        if isinstance(other, Prefix):
+            if fact == 1:
+                return S.One
             # simplify prefix
             for p in PREFIXES:
                 if PREFIXES[p].scale_factor == fact:
@@ -103,7 +103,7 @@ def __truediv__(self, other):
         fact = self.scale_factor / other.scale_factor
 
         if fact == 1:
-            return 1
+            return S.One
         elif isinstance(other, Prefix):
             for p in PREFIXES:
                 if PREFIXES[p].scale_factor == fact:


```

## Test Patch

```diff
diff --git a/sympy/physics/units/tests/test_prefixes.py b/sympy/physics/units/tests/test_prefixes.py
--- a/sympy/physics/units/tests/test_prefixes.py
+++ b/sympy/physics/units/tests/test_prefixes.py
@@ -2,7 +2,7 @@
 from sympy.core.numbers import Rational
 from sympy.core.singleton import S
 from sympy.core.symbol import (Symbol, symbols)
-from sympy.physics.units import Quantity, length, meter
+from sympy.physics.units import Quantity, length, meter, W
 from sympy.physics.units.prefixes import PREFIXES, Prefix, prefix_unit, kilo, \
     kibi
 from sympy.physics.units.systems import SI
@@ -17,7 +17,8 @@ def test_prefix_operations():
 
     dodeca = Prefix('dodeca', 'dd', 1, base=12)
 
-    assert m * k == 1
+    assert m * k is S.One
+    assert m * W == W / 1000
     assert k * k == M
     assert 1 / m == k
     assert k / m == M
@@ -25,7 +26,7 @@ def test_prefix_operations():
     assert dodeca * dodeca == 144
     assert 1 / dodeca == S.One / 12
     assert k / dodeca == S(1000) / 12
-    assert dodeca / dodeca == 1
+    assert dodeca / dodeca is S.One
 
     m = Quantity("fake_meter")
     SI.set_quantity_dimension(m, S.One)

```

## Test Information

**Tests that should FAIL→PASS**: ["test_prefix_operations"]

**Tests that should PASS→PASS**: ["test_prefix_unit", "test_bases"]

**Base Commit**: d3b4158dea271485e3daa11bf82e69b8dab348ce
**Environment Setup Commit**: be161798ecc7278ccf3ffa47259e3b5fde280b7d
