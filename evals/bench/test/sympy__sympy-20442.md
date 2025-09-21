# sympy__sympy-20442

**Repository**: sympy/sympy
**Created**: 2020-11-17T22:23:42Z
**Version**: 1.8

## Problem Statement

convert_to seems to combine orthogonal units
Tested in sympy 1.4, not presently in a position to install 1.5+.
Simple example. Consider `J = kg*m**2/s**2 => J*s = kg*m**2/s`. The convert_to behavior is odd:
```
>>>convert_to(joule*second,joule)
    joule**(7/9)
```
I would expect the unchanged original expression back, an expression in terms of base units, or an error. It appears that convert_to can only readily handle conversions where the full unit expression is valid.

Note that the following three related examples give sensible results:
```
>>>convert_to(joule*second,joule*second)
    joule*second
```
```
>>>convert_to(J*s, kg*m**2/s)
    kg*m**2/s
```
```
>>>convert_to(J*s,mins)
    J*mins/60
```


## Hints

Yes, this is a problem. When trying to convert into a unit that is not compatible, it should either do nothing (no conversion), or raise an exception. I personally don't see how the following makes sense:
```
>>> convert_to(meter, second) 
meter

```
I often do calculations with units as a failsafe check. When The operation checks out and delivers reasonable units, I take it as a sign that it went well. When it "silently" converts an expression into non-sensible units, this cannot be used as a failsafe check.
I am glad someone agrees this is a problem. I suggest that the physics.units package be disabled for now as it has serious flaws.

My solution is simply to use positive, real symbolic variables for units. I worry about the conversions myself. For example: `var('J m kg s Pa', positive=True, real=True)`. These behave as proper units and don't do anything mysterious. For unit conversions, I usually just use things like `.subs({J:kg*m**2/s**2})`. You could also use substitution using `.evalf()`.
> I suggest that the physics.units package be disabled for now

That seems a little drastic.

I don't use the units module but the docstring for `convert_to` says:
```
    Convert ``expr`` to the same expression with all of its units and quantities
    represented as factors of ``target_units``, whenever the dimension is compatible.
```
There are examples in the docstring showing that the `target_units` parameter can be a list and is intended to apply only to the relevant dimensions e.g.:
```
In [11]: convert_to(3*meter/second, hour)                                                                                                      
Out[11]: 
10800⋅meter
───────────
    hour
```
If you want a function to convert between strictly between one compound unit and another or otherwise raise an error then that seems reasonable but it probably needs to be a different function (maybe there already is one).
Hi @oscarbenjamin ! Thanks for your leads and additional information provided. I am relatively new to this and have to have a deeper look at the docstring. (Actually, I had a hard time finding the right information. I was mainly using google and did not get far enough.)
I stand by my suggestion. As my first example shows in the initial entry 
for this issue the result from a request that should return the original 
expression unchanged provides a wrong answer. This is exactly equivalent 
to the example you give, except that the particular case is wrong. As 
@schniepp shows there are other cases. This module needs repair and is 
not safely usable unless you know the answer you should get.

I think the convert_to function needs fixing. I would call this a bug. I 
presently do not have time to figure out how to fix it. If somebody does 
that would be great, but if not I think leaving it active makes SymPy's 
quality control look poor.

On 9/26/20 4:07 PM, Oscar Benjamin wrote:
> CAUTION: This email originated from outside of the organization. Do 
> not click links or open attachments unless you recognize the sender 
> and know the content is safe.
>
>     I suggest that the physics.units package be disabled for now
>
> That seems a little drastic.
>
> I don't use the units module but the docstring for |convert_to| says:
>
> |Convert ``expr`` to the same expression with all of its units and 
> quantities represented as factors of ``target_units``, whenever the 
> dimension is compatible. |
>
> There are examples in the docstring showing that the |target_units| 
> parameter can be a list and is intended to apply only to the relevant 
> dimensions e.g.:
>
> |In [11]: convert_to(3*meter/second, hour) Out[11]: 10800⋅meter 
> ─────────── hour |
>
> If you want a function to convert between strictly between one 
> compound unit and another or otherwise raise an error then that seems 
> reasonable but it probably needs to be a different function (maybe 
> there already is one).
>
> —
> You are receiving this because you authored the thread.
> Reply to this email directly, view it on GitHub 
> <https://github.com/sympy/sympy/issues/18368#issuecomment-699548030>, 
> or unsubscribe 
> <https://github.com/notifications/unsubscribe-auth/AAJMTVMMHFKELA3LZMDWCUDSHZJ25ANCNFSM4KILNGEQ>.
>
-- 
Dr. Jonathan H. Gutow
Chemistry Department                                 gutow@uwosh.edu
UW-Oshkosh                                           Office:920-424-1326
800 Algoma Boulevard                                 FAX:920-424-2042
Oshkosh, WI 54901
                 http://www.uwosh.edu/facstaff/gutow/


If the module is usable for anything then people will be using it so we can't just disable it.

In any case I'm sure it would be easier to fix the problem than it would be to disable the module.
Can we then please mark this as a bug, so it will receive some priority.
I've marked it as a bug but that doesn't imply any particular priority. Priority just comes down to what any contributor wants to work on.

I suspect that there are really multiple separate issues here but someone needs to take the time to investigate the causes to find out.
I agree that this is probably an indicator of multiple issues. My quick look at the code suggested there is something odd about the way the basis is handled and that I was not going to find a quick fix. Thus I went back to just treating units as symbols as I do in hand calculations. For teaching, I've concluded that is better anyway.
I also ran into this issue and wanted  to share my experience.  I ran this command and got the following result. 

```
>>> convert_to(5*ohm*2*A**2/cm, watt*m)
1000*10**(18/19)*meter**(13/19)*watt**(13/19)
```

The result is obviously meaningless.  I spent a lot of time trying to figure out what was going on.  I finally figured out the mistake was on my end.  I typed 'watt*m' for the target unit when what I wanted was 'watt/m.'  This is a problem mostly because if the user does not catch their mistake right away they are going to assume the program is not working.
> I suggest that the physics.units package be disabled for now as it has serious flaws.

If we disable the module in the master branch, it will only become available after a new SymPy version release. At that point, we will be bombarded by millions of people complaining about the missing module on Github and Stackoverflow.

Apparently, `physics.units` is one of the most used modules in SymPy. We keep getting lots of complaints even for small changes.
@Upabjojr I understand your reasoning. It still does not address the root problem of something wrong in how the basis set of units is handled. Could somebody at least update the instructions for `convert_to` to clearly warn about how it fails. 

I have other projects, so do not have time to contribute to the units package. Until this is fixed, I will continue to use plain vanilla positive real SymPy variables as units.

Regards
It's curious that this conversation has taken so long, when just 5 minutes of debugging have revealed this simple error:
https://github.com/sympy/sympy/blob/702bceaa0dde32193bfa9456df89eb63153a7538/sympy/physics/units/util.py#L33

`solve_least_squares` finds the solution to the matrix equation. In case no solution is found (like in `convert_to(joule*second, joule)`), it approximates to an inexact solution to the matrix system instead of raising an exception.

Simply changing it to `.solve_least_squares` to `.solve` should fix this issue.

## Patch

```diff

diff --git a/sympy/physics/units/util.py b/sympy/physics/units/util.py
--- a/sympy/physics/units/util.py
+++ b/sympy/physics/units/util.py
@@ -4,6 +4,7 @@
 
 from sympy import Add, Mul, Pow, Tuple, sympify
 from sympy.core.compatibility import reduce, Iterable, ordered
+from sympy.matrices.common import NonInvertibleMatrixError
 from sympy.physics.units.dimensions import Dimension
 from sympy.physics.units.prefixes import Prefix
 from sympy.physics.units.quantities import Quantity
@@ -30,7 +31,11 @@ def _get_conversion_matrix_for_expr(expr, target_units, unit_system):
     camat = Matrix([[dimension_system.get_dimensional_dependencies(i, mark_dimensionless=True).get(j, 0) for i in target_dims] for j in canon_dim_units])
     exprmat = Matrix([dim_dependencies.get(k, 0) for k in canon_dim_units])
 
-    res_exponents = camat.solve_least_squares(exprmat, method=None)
+    try:
+        res_exponents = camat.solve(exprmat)
+    except NonInvertibleMatrixError:
+        return None
+
     return res_exponents
 
 


```

## Test Patch

```diff
diff --git a/sympy/physics/units/tests/test_quantities.py b/sympy/physics/units/tests/test_quantities.py
--- a/sympy/physics/units/tests/test_quantities.py
+++ b/sympy/physics/units/tests/test_quantities.py
@@ -1,7 +1,7 @@
 from sympy import (Abs, Add, Function, Number, Rational, S, Symbol,
                    diff, exp, integrate, log, sin, sqrt, symbols)
 from sympy.physics.units import (amount_of_substance, convert_to, find_unit,
-                                 volume, kilometer)
+                                 volume, kilometer, joule)
 from sympy.physics.units.definitions import (amu, au, centimeter, coulomb,
     day, foot, grams, hour, inch, kg, km, m, meter, millimeter,
     minute, quart, s, second, speed_of_light, bit,
@@ -45,6 +45,10 @@ def test_convert_to():
     assert q.convert_to(s) == q
     assert speed_of_light.convert_to(m) == speed_of_light
 
+    expr = joule*second
+    conv = convert_to(expr, joule)
+    assert conv == joule*second
+
 
 def test_Quantity_definition():
     q = Quantity("s10", abbrev="sabbr")

```

## Test Information

**Tests that should FAIL→PASS**: ["test_convert_to"]

**Tests that should PASS→PASS**: ["test_str_repr", "test_eq", "test_Quantity_definition", "test_abbrev", "test_print", "test_Quantity_eq", "test_add_sub", "test_quantity_abs", "test_check_unit_consistency", "test_mul_div", "test_units", "test_issue_quart", "test_issue_5565", "test_find_unit", "test_Quantity_derivative", "test_quantity_postprocessing", "test_factor_and_dimension", "test_dimensional_expr_of_derivative", "test_get_dimensional_expr_with_function", "test_binary_information", "test_conversion_with_2_nonstandard_dimensions", "test_eval_subs", "test_issue_14932", "test_issue_14547"]

**Base Commit**: 1abbc0ac3e552cb184317194e5d5c5b9dd8fb640
**Environment Setup Commit**: 3ac1464b8840d5f8b618a654f9fbf09c452fe969
