# sympy__sympy-24102

**Repository**: sympy/sympy
**Created**: 2022-10-01T18:41:32Z
**Version**: 1.12

## Problem Statement

Cannot parse Greek characters (and possibly others) in parse_mathematica
The old Mathematica parser `mathematica` in the package `sympy.parsing.mathematica` was able to parse e.g. Greek characters. Hence the following example works fine:
```
from sympy.parsing.mathematica import mathematica
mathematica('λ')
Out[]: 
λ
```

As of SymPy v. 1.11, the `mathematica` function is deprecated, and is replaced by `parse_mathematica`. This function, however, seems unable to handle the simple example above:
```
from sympy.parsing.mathematica import parse_mathematica
parse_mathematica('λ')
Traceback (most recent call last):
...
File "<string>", line unknown
SyntaxError: unable to create a single AST for the expression
```

This appears to be due to a bug in `parse_mathematica`, which is why I have opened this issue.

Thanks in advance!
Cannot parse Greek characters (and possibly others) in parse_mathematica
The old Mathematica parser `mathematica` in the package `sympy.parsing.mathematica` was able to parse e.g. Greek characters. Hence the following example works fine:
```
from sympy.parsing.mathematica import mathematica
mathematica('λ')
Out[]: 
λ
```

As of SymPy v. 1.11, the `mathematica` function is deprecated, and is replaced by `parse_mathematica`. This function, however, seems unable to handle the simple example above:
```
from sympy.parsing.mathematica import parse_mathematica
parse_mathematica('λ')
Traceback (most recent call last):
...
File "<string>", line unknown
SyntaxError: unable to create a single AST for the expression
```

This appears to be due to a bug in `parse_mathematica`, which is why I have opened this issue.

Thanks in advance!


## Patch

```diff

diff --git a/sympy/parsing/mathematica.py b/sympy/parsing/mathematica.py
--- a/sympy/parsing/mathematica.py
+++ b/sympy/parsing/mathematica.py
@@ -654,7 +654,7 @@ def _from_mathematica_to_tokens(self, code: str):
             code_splits[i] = code_split
 
         # Tokenize the input strings with a regular expression:
-        token_lists = [tokenizer.findall(i) if isinstance(i, str) else [i] for i in code_splits]
+        token_lists = [tokenizer.findall(i) if isinstance(i, str) and i.isascii() else [i] for i in code_splits]
         tokens = [j for i in token_lists for j in i]
 
         # Remove newlines at the beginning


```

## Test Patch

```diff
diff --git a/sympy/parsing/tests/test_mathematica.py b/sympy/parsing/tests/test_mathematica.py
--- a/sympy/parsing/tests/test_mathematica.py
+++ b/sympy/parsing/tests/test_mathematica.py
@@ -15,6 +15,7 @@ def test_mathematica():
         'x+y': 'x+y',
         '355/113': '355/113',
         '2.718281828': '2.718281828',
+        'Cos(1/2 * π)': 'Cos(π/2)',
         'Sin[12]': 'sin(12)',
         'Exp[Log[4]]': 'exp(log(4))',
         '(x+1)(x+3)': '(x+1)*(x+3)',
@@ -94,6 +95,7 @@ def test_parser_mathematica_tokenizer():
     assert chain("+x") == "x"
     assert chain("-1") == "-1"
     assert chain("- 3") == "-3"
+    assert chain("α") == "α"
     assert chain("+Sin[x]") == ["Sin", "x"]
     assert chain("-Sin[x]") == ["Times", "-1", ["Sin", "x"]]
     assert chain("x(a+1)") == ["Times", "x", ["Plus", "a", "1"]]
diff --git a/sympy/testing/quality_unicode.py b/sympy/testing/quality_unicode.py
--- a/sympy/testing/quality_unicode.py
+++ b/sympy/testing/quality_unicode.py
@@ -48,6 +48,8 @@
 
 unicode_strict_whitelist = [
     r'*/sympy/parsing/latex/_antlr/__init__.py',
+    # test_mathematica.py uses some unicode for testing Greek characters are working #24055
+    r'*/sympy/parsing/tests/test_mathematica.py',
 ]
 
 

```

## Test Information

**Tests that should FAIL→PASS**: ["test_mathematica", "test_parser_mathematica_tokenizer"]

**Tests that should PASS→PASS**: []

**Base Commit**: 58598660a3f6ab3d918781c4988c2e4b2bdd9297
**Environment Setup Commit**: c6cb7c5602fa48034ab1bd43c2347a7e8488f12e
