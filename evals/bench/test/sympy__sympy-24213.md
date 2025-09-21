# sympy__sympy-24213

**Repository**: sympy/sympy
**Created**: 2022-11-03T14:00:09Z
**Version**: 1.12

## Problem Statement

collect_factor_and_dimension does not detect equivalent dimensions in addition
Code to reproduce:
```python
from sympy.physics import units
from sympy.physics.units.systems.si import SI

v1 = units.Quantity('v1')
SI.set_quantity_dimension(v1, units.velocity)
SI.set_quantity_scale_factor(v1, 2 * units.meter / units.second)

a1 = units.Quantity('a1')
SI.set_quantity_dimension(a1, units.acceleration)
SI.set_quantity_scale_factor(a1, -9.8 * units.meter / units.second**2)

t1 = units.Quantity('t1')
SI.set_quantity_dimension(t1, units.time)
SI.set_quantity_scale_factor(t1, 5 * units.second)

expr1 = a1*t1 + v1
SI._collect_factor_and_dimension(expr1)
```
Results in:
```
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "C:\Python\Python310\lib\site-packages\sympy\physics\units\unitsystem.py", line 179, in _collect_factor_and_dimension
    raise ValueError(
ValueError: Dimension of "v1" is Dimension(velocity), but it should be Dimension(acceleration*time)
```


## Patch

```diff

diff --git a/sympy/physics/units/unitsystem.py b/sympy/physics/units/unitsystem.py
--- a/sympy/physics/units/unitsystem.py
+++ b/sympy/physics/units/unitsystem.py
@@ -175,7 +175,7 @@ def _collect_factor_and_dimension(self, expr):
             for addend in expr.args[1:]:
                 addend_factor, addend_dim = \
                     self._collect_factor_and_dimension(addend)
-                if dim != addend_dim:
+                if not self.get_dimension_system().equivalent_dims(dim, addend_dim):
                     raise ValueError(
                         'Dimension of "{}" is {}, '
                         'but it should be {}'.format(


```

## Test Patch

```diff
diff --git a/sympy/physics/units/tests/test_quantities.py b/sympy/physics/units/tests/test_quantities.py
--- a/sympy/physics/units/tests/test_quantities.py
+++ b/sympy/physics/units/tests/test_quantities.py
@@ -561,6 +561,22 @@ def test_issue_24062():
     exp_expr = 1 + exp(expr)
     assert SI._collect_factor_and_dimension(exp_expr) == (1 + E, Dimension(1))
 
+def test_issue_24211():
+    from sympy.physics.units import time, velocity, acceleration, second, meter
+    V1 = Quantity('V1')
+    SI.set_quantity_dimension(V1, velocity)
+    SI.set_quantity_scale_factor(V1, 1 * meter / second)
+    A1 = Quantity('A1')
+    SI.set_quantity_dimension(A1, acceleration)
+    SI.set_quantity_scale_factor(A1, 1 * meter / second**2)
+    T1 = Quantity('T1')
+    SI.set_quantity_dimension(T1, time)
+    SI.set_quantity_scale_factor(T1, 1 * second)
+
+    expr = A1*T1 + V1
+    # should not throw ValueError here
+    SI._collect_factor_and_dimension(expr)
+
 
 def test_prefixed_property():
     assert not meter.is_prefixed

```

## Test Information

**Tests that should FAIL→PASS**: ["test_issue_24211"]

**Tests that should PASS→PASS**: ["test_str_repr", "test_eq", "test_convert_to", "test_Quantity_definition", "test_abbrev", "test_print", "test_Quantity_eq", "test_add_sub", "test_quantity_abs", "test_check_unit_consistency", "test_mul_div", "test_units", "test_issue_quart", "test_issue_5565", "test_find_unit", "test_Quantity_derivative", "test_quantity_postprocessing", "test_factor_and_dimension", "test_dimensional_expr_of_derivative", "test_get_dimensional_expr_with_function", "test_binary_information", "test_conversion_with_2_nonstandard_dimensions", "test_eval_subs", "test_issue_14932", "test_issue_14547", "test_deprecated_quantity_methods", "test_issue_22164", "test_issue_22819", "test_issue_20288", "test_issue_24062", "test_prefixed_property"]

**Base Commit**: e8c22f6eac7314be8d92590bfff92ced79ee03e2
**Environment Setup Commit**: c6cb7c5602fa48034ab1bd43c2347a7e8488f12e
