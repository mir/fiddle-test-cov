# sympy__sympy-23191

**Repository**: sympy/sympy
**Created**: 2022-03-01T17:22:06Z
**Version**: 1.11

## Problem Statement

display bug while using pretty_print with sympy.vector object in the terminal
The following code jumbles some of the outputs in the terminal, essentially by inserting the unit vector in the middle -
```python
from sympy import *
from sympy.vector import CoordSys3D, Del

init_printing()

delop = Del()
CC_ = CoordSys3D("C")
x,    y,    z    = CC_.x, CC_.y, CC_.z
xhat, yhat, zhat = CC_.i, CC_.j, CC_.k

t = symbols("t")
ten = symbols("10", positive=True)
eps, mu = 4*pi*ten**(-11), ten**(-5)

Bx = 2 * ten**(-4) * cos(ten**5 * t) * sin(ten**(-3) * y)
vecB = Bx * xhat
vecE = (1/eps) * Integral(delop.cross(vecB/mu).doit(), t)

pprint(vecB)
print()
pprint(vecE)
print()
pprint(vecE.doit())
```

Output:
```python
⎛     ⎛y_C⎞    ⎛  5  ⎞⎞    
⎜2⋅sin⎜───⎟ i_C⋅cos⎝10 ⋅t⎠⎟
⎜     ⎜  3⎟           ⎟    
⎜     ⎝10 ⎠           ⎟    
⎜─────────────────────⎟    
⎜           4         ⎟    
⎝         10          ⎠    

⎛     ⌠                           ⎞    
⎜     ⎮       ⎛y_C⎞    ⎛  5  ⎞    ⎟ k_C
⎜     ⎮ -2⋅cos⎜───⎟⋅cos⎝10 ⋅t⎠    ⎟    
⎜     ⎮       ⎜  3⎟               ⎟    
⎜  11 ⎮       ⎝10 ⎠               ⎟    
⎜10  ⋅⎮ ─────────────────────── dt⎟    
⎜     ⎮             2             ⎟    
⎜     ⎮           10              ⎟    
⎜     ⌡                           ⎟    
⎜─────────────────────────────────⎟    
⎝               4⋅π               ⎠    

⎛   4    ⎛  5  ⎞    ⎛y_C⎞ ⎞    
⎜-10 ⋅sin⎝10 ⋅t⎠⋅cos⎜───⎟ k_C ⎟
⎜                   ⎜  3⎟ ⎟    
⎜                   ⎝10 ⎠ ⎟    
⎜─────────────────────────⎟    
⎝           2⋅π           ⎠    ```


## Hints

You can control print order as described [here](https://stackoverflow.com/a/58541713/1089161).
The default order should not break the multiline bracket of pretty print. Please see the output in constant width mode or paste it in a text editor. The second output is fine while the right bracket is broken in the other two.
I can verify that this seems to be an issue specific to pretty print. The Latex renderer outputs what you want. This should be fixable. Here is an image of the output for your vectors from the latex rendered in Jupyter.
![image](https://user-images.githubusercontent.com/1231317/153658279-1cf4d387-2101-4cb3-b182-131ed3cbe1b8.png)

Admittedly the small outer parenthesis are not stylistically great, but the ordering is what you expect.
The LaTeX printer ought to be using \left and \right for parentheses. 

## Patch

```diff

diff --git a/sympy/printing/pretty/pretty.py b/sympy/printing/pretty/pretty.py
--- a/sympy/printing/pretty/pretty.py
+++ b/sympy/printing/pretty/pretty.py
@@ -1144,22 +1144,24 @@ def _print_BasisDependent(self, expr):
             if '\n' in partstr:
                 tempstr = partstr
                 tempstr = tempstr.replace(vectstrs[i], '')
-                if '\N{right parenthesis extension}' in tempstr:   # If scalar is a fraction
+                if '\N{RIGHT PARENTHESIS EXTENSION}' in tempstr:   # If scalar is a fraction
                     for paren in range(len(tempstr)):
                         flag[i] = 1
-                        if tempstr[paren] == '\N{right parenthesis extension}':
-                            tempstr = tempstr[:paren] + '\N{right parenthesis extension}'\
+                        if tempstr[paren] == '\N{RIGHT PARENTHESIS EXTENSION}' and tempstr[paren + 1] == '\n':
+                            # We want to place the vector string after all the right parentheses, because
+                            # otherwise, the vector will be in the middle of the string
+                            tempstr = tempstr[:paren] + '\N{RIGHT PARENTHESIS EXTENSION}'\
                                          + ' '  + vectstrs[i] + tempstr[paren + 1:]
                             break
                 elif '\N{RIGHT PARENTHESIS LOWER HOOK}' in tempstr:
-                    flag[i] = 1
-                    tempstr = tempstr.replace('\N{RIGHT PARENTHESIS LOWER HOOK}',
-                                        '\N{RIGHT PARENTHESIS LOWER HOOK}'
-                                        + ' ' + vectstrs[i])
-                else:
-                    tempstr = tempstr.replace('\N{RIGHT PARENTHESIS UPPER HOOK}',
-                                        '\N{RIGHT PARENTHESIS UPPER HOOK}'
-                                        + ' ' + vectstrs[i])
+                    # We want to place the vector string after all the right parentheses, because
+                    # otherwise, the vector will be in the middle of the string. For this reason,
+                    # we insert the vector string at the rightmost index.
+                    index = tempstr.rfind('\N{RIGHT PARENTHESIS LOWER HOOK}')
+                    if index != -1: # then this character was found in this string
+                        flag[i] = 1
+                        tempstr = tempstr[:index] + '\N{RIGHT PARENTHESIS LOWER HOOK}'\
+                                     + ' '  + vectstrs[i] + tempstr[index + 1:]
                 o1[i] = tempstr
 
         o1 = [x.split('\n') for x in o1]


```

## Test Patch

```diff
diff --git a/sympy/vector/tests/test_printing.py b/sympy/vector/tests/test_printing.py
--- a/sympy/vector/tests/test_printing.py
+++ b/sympy/vector/tests/test_printing.py
@@ -3,7 +3,7 @@
 from sympy.integrals.integrals import Integral
 from sympy.printing.latex import latex
 from sympy.printing.pretty import pretty as xpretty
-from sympy.vector import CoordSys3D, Vector, express
+from sympy.vector import CoordSys3D, Del, Vector, express
 from sympy.abc import a, b, c
 from sympy.testing.pytest import XFAIL
 
@@ -160,6 +160,55 @@ def test_latex_printing():
                             '\\mathbf{\\hat{k}_{N}}{\\middle|}\\mathbf{' +
                             '\\hat{k}_{N}}\\right)')
 
+def test_issue_23058():
+    from sympy import symbols, sin, cos, pi, UnevaluatedExpr
+
+    delop = Del()
+    CC_   = CoordSys3D("C")
+    y     = CC_.y
+    xhat  = CC_.i
+
+    t = symbols("t")
+    ten = symbols("10", positive=True)
+    eps, mu = 4*pi*ten**(-11), ten**(-5)
+
+    Bx = 2 * ten**(-4) * cos(ten**5 * t) * sin(ten**(-3) * y)
+    vecB = Bx * xhat
+    vecE = (1/eps) * Integral(delop.cross(vecB/mu).doit(), t)
+    vecE = vecE.doit()
+
+    vecB_str = """\
+⎛     ⎛y_C⎞    ⎛  5  ⎞⎞    \n\
+⎜2⋅sin⎜───⎟⋅cos⎝10 ⋅t⎠⎟ i_C\n\
+⎜     ⎜  3⎟           ⎟    \n\
+⎜     ⎝10 ⎠           ⎟    \n\
+⎜─────────────────────⎟    \n\
+⎜           4         ⎟    \n\
+⎝         10          ⎠    \
+"""
+    vecE_str = """\
+⎛   4    ⎛  5  ⎞    ⎛y_C⎞ ⎞    \n\
+⎜-10 ⋅sin⎝10 ⋅t⎠⋅cos⎜───⎟ ⎟ k_C\n\
+⎜                   ⎜  3⎟ ⎟    \n\
+⎜                   ⎝10 ⎠ ⎟    \n\
+⎜─────────────────────────⎟    \n\
+⎝           2⋅π           ⎠    \
+"""
+
+    assert upretty(vecB) == vecB_str
+    assert upretty(vecE) == vecE_str
+
+    ten = UnevaluatedExpr(10)
+    eps, mu = 4*pi*ten**(-11), ten**(-5)
+
+    Bx = 2 * ten**(-4) * cos(ten**5 * t) * sin(ten**(-3) * y)
+    vecB = Bx * xhat
+
+    vecB_str = """\
+⎛    -4    ⎛    5⎞    ⎛      -3⎞⎞     \n\
+⎝2⋅10  ⋅cos⎝t⋅10 ⎠⋅sin⎝y_C⋅10  ⎠⎠ i_C \
+"""
+    assert upretty(vecB) == vecB_str
 
 def test_custom_names():
     A = CoordSys3D('A', vector_names=['x', 'y', 'z'],

```

## Test Information

**Tests that should FAIL→PASS**: ["test_issue_23058"]

**Tests that should PASS→PASS**: ["test_str_printing", "test_pretty_print_unicode_v", "test_latex_printing"]

**Base Commit**: fa9b4b140ec0eaf75a62c1111131626ef0f6f524
**Environment Setup Commit**: 9a6104eab0ea7ac191a09c24f3e2d79dcd66bda5
