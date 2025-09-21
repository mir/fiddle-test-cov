# sympy__sympy-16106

**Repository**: sympy/sympy
**Created**: 2019-02-28T17:21:46Z
**Version**: 1.4

## Problem Statement

mathml printer for IndexedBase required
Writing an `Indexed` object to MathML fails with a `TypeError` exception: `TypeError: 'Indexed' object is not iterable`:

```
In [340]: sympy.__version__
Out[340]: '1.0.1.dev'

In [341]: from sympy.abc import (a, b)

In [342]: sympy.printing.mathml(sympy.IndexedBase(a)[b])
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
<ipython-input-342-b32e493b70d3> in <module>()
----> 1 sympy.printing.mathml(sympy.IndexedBase(a)[b])

/dev/shm/gerrit/venv/stable-3.5/lib/python3.5/site-packages/sympy/printing/mathml.py in mathml(expr, **settings)
    442 def mathml(expr, **settings):
    443     """Returns the MathML representation of expr"""
--> 444     return MathMLPrinter(settings).doprint(expr)
    445 
    446 

/dev/shm/gerrit/venv/stable-3.5/lib/python3.5/site-packages/sympy/printing/mathml.py in doprint(self, expr)
     36         Prints the expression as MathML.
     37         """
---> 38         mathML = Printer._print(self, expr)
     39         unistr = mathML.toxml()
     40         xmlbstr = unistr.encode('ascii', 'xmlcharrefreplace')

/dev/shm/gerrit/venv/stable-3.5/lib/python3.5/site-packages/sympy/printing/printer.py in _print(self, expr, *args, **kwargs)
    255                 printmethod = '_print_' + cls.__name__
    256                 if hasattr(self, printmethod):
--> 257                     return getattr(self, printmethod)(expr, *args, **kwargs)
    258             # Unknown object, fall back to the emptyPrinter.
    259             return self.emptyPrinter(expr)

/dev/shm/gerrit/venv/stable-3.5/lib/python3.5/site-packages/sympy/printing/mathml.py in _print_Basic(self, e)
    356     def _print_Basic(self, e):
    357         x = self.dom.createElement(self.mathml_tag(e))
--> 358         for arg in e:
    359             x.appendChild(self._print(arg))
    360         return x

TypeError: 'Indexed' object is not iterable
```

It also fails for more complex expressions where at least one element is Indexed.


## Hints

Now it returns
```
'<indexed><indexedbase><ci>a</ci></indexedbase><ci>b</ci></indexed>'
```
for content printer and 
```
'<mrow><mi>indexed</mi><mfenced><mrow><mi>indexedbase</mi><mfenced><mi>a</mi></mfenced></mrow><mi>b</mi></mfenced></mrow>'
```
for presentation printer.

Probably not correct as it seems like it falls back to the printer for `Basic`.

Hence, a method `_print_IndexedBase` is required. Could be good to look at the LaTeX version to see how subscripts etc are handled.
Hi, can I take up this issue if it still needs fixing?
@pragyanmehrotra It is still needed so please go ahead!
@oscargus Sure I'll start working on it right ahead! However, Idk what exactly needs to be done so if you could point out how the output should look like and do I have to implement a new function or edit a current function it'd be a great help, Thanks.
```
from sympy import IndexedBase
a, b = symbols('a b')
IndexedBase(a)[b]
```
which renders as
![image](https://user-images.githubusercontent.com/8114497/53299790-abec5c80-383f-11e9-82c4-6dd3424f37a7.png)

Meaning that the presentation MathML output should be something like
`<msub><mi>a<mi><mi>b<mi></msub>`

Have a look at #16036 for some good resources.

Basically you need to do something like:
```
m = self.dom.createElement('msub')
m.appendChild(self._print(Whatever holds a))
m.appendChild(self._print(Whatever holds b))
```
in a function called `_print_IndexedBase`.

## Patch

```diff

diff --git a/sympy/printing/mathml.py b/sympy/printing/mathml.py
--- a/sympy/printing/mathml.py
+++ b/sympy/printing/mathml.py
@@ -1271,6 +1271,26 @@ def _print_Lambda(self, e):
         return x
 
 
+    def _print_tuple(self, e):
+        x = self.dom.createElement('mfenced')
+        for i in e:
+            x.appendChild(self._print(i))
+        return x
+
+
+    def _print_IndexedBase(self, e):
+        return self._print(e.label)
+
+    def _print_Indexed(self, e):
+        x = self.dom.createElement('msub')
+        x.appendChild(self._print(e.base))
+        if len(e.indices) == 1:
+            x.appendChild(self._print(e.indices[0]))
+            return x
+        x.appendChild(self._print(e.indices))
+        return x
+
+
 def mathml(expr, printer='content', **settings):
     """Returns the MathML representation of expr. If printer is presentation then
      prints Presentation MathML else prints content MathML.


```

## Test Patch

```diff
diff --git a/sympy/printing/tests/test_mathml.py b/sympy/printing/tests/test_mathml.py
--- a/sympy/printing/tests/test_mathml.py
+++ b/sympy/printing/tests/test_mathml.py
@@ -1,7 +1,7 @@
 from sympy import diff, Integral, Limit, sin, Symbol, Integer, Rational, cos, \
     tan, asin, acos, atan, sinh, cosh, tanh, asinh, acosh, atanh, E, I, oo, \
     pi, GoldenRatio, EulerGamma, Sum, Eq, Ne, Ge, Lt, Float, Matrix, Basic, S, \
-    MatrixSymbol, Function, Derivative, log, Lambda
+    MatrixSymbol, Function, Derivative, log, Lambda, IndexedBase, symbols
 from sympy.core.containers import Tuple
 from sympy.functions.elementary.complexes import re, im, Abs, conjugate
 from sympy.functions.elementary.integers import floor, ceiling
@@ -1139,3 +1139,17 @@ def test_print_random_symbol():
     R = RandomSymbol(Symbol('R'))
     assert mpp.doprint(R) == '<mi>R</mi>'
     assert mp.doprint(R) == '<ci>R</ci>'
+
+
+def test_print_IndexedBase():
+    a,b,c,d,e = symbols('a b c d e')
+    assert mathml(IndexedBase(a)[b],printer='presentation') == '<msub><mi>a</mi><mi>b</mi></msub>'
+    assert mathml(IndexedBase(a)[b,c,d],printer = 'presentation') == '<msub><mi>a</mi><mfenced><mi>b</mi><mi>c</mi><mi>d</mi></mfenced></msub>'
+    assert mathml(IndexedBase(a)[b]*IndexedBase(c)[d]*IndexedBase(e),printer = 'presentation') == '<mrow><msub><mi>a</mi><mi>b</mi></msub><mo>&InvisibleTimes;</mo><msub><mi>c</mi><mi>d</mi></msub><mo>&InvisibleTimes;</mo><mi>e</mi></mrow>'
+
+
+def test_print_Indexed():
+    a,b,c = symbols('a b c')
+    assert mathml(IndexedBase(a),printer = 'presentation') == '<mi>a</mi>'
+    assert mathml(IndexedBase(a/b),printer = 'presentation') == '<mrow><mfrac><mi>a</mi><mi>b</mi></mfrac></mrow>'
+    assert mathml(IndexedBase((a,b)),printer = 'presentation') == '<mrow><mfenced><mi>a</mi><mi>b</mi></mfenced></mrow>'

```

## Test Information

**Tests that should FAIL→PASS**: ["test_print_IndexedBase"]

**Tests that should PASS→PASS**: ["test_mathml_printer", "test_content_printmethod", "test_content_mathml_core", "test_content_mathml_functions", "test_content_mathml_limits", "test_content_mathml_integrals", "test_content_mathml_matrices", "test_content_mathml_sums", "test_content_mathml_tuples", "test_content_mathml_add", "test_content_mathml_Rational", "test_content_mathml_constants", "test_content_mathml_trig", "test_content_mathml_relational", "test_content_symbol", "test_content_mathml_greek", "test_content_mathml_order", "test_content_settings", "test_presentation_printmethod", "test_presentation_mathml_core", "test_presentation_mathml_functions", "test_print_derivative", "test_presentation_mathml_limits", "test_presentation_mathml_integrals", "test_presentation_mathml_matrices", "test_presentation_mathml_sums", "test_presentation_mathml_add", "test_presentation_mathml_Rational", "test_presentation_mathml_constants", "test_presentation_mathml_trig", "test_presentation_mathml_relational", "test_presentation_symbol", "test_presentation_mathml_greek", "test_presentation_mathml_order", "test_print_tuples", "test_print_re_im", "test_presentation_settings", "test_toprettyxml_hooking", "test_print_domains", "test_print_expression_with_minus", "test_print_AssocOp", "test_print_basic", "test_ln_notation_print", "test_mul_symbol_print", "test_print_lerchphi", "test_print_polylog", "test_print_logic", "test_root_notation_print", "test_fold_frac_powers_print", "test_fold_short_frac_print", "test_print_factorials", "test_print_Lambda", "test_print_conjugate", "test_print_matrix_symbol", "test_print_random_symbol"]

**Base Commit**: 0e987498b00167fdd4a08a41c852a97cb70ce8f2
**Environment Setup Commit**: 73b3f90093754c5ed1561bd885242330e3583004
