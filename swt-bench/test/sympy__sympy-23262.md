# sympy__sympy-23262

**Repository**: sympy/sympy
**Created**: 2022-03-21T07:17:35Z
**Version**: 1.11

## Problem Statement

Python code printer not respecting tuple with one element
Hi,

Thanks for the recent updates in SymPy! I'm trying to update my code to use SymPy 1.10 but ran into an issue with the Python code printer. MWE:


```python
import inspect
from sympy import lambdify

inspect.getsource(lambdify([], tuple([1])))
```
SymPy 1.9 and under outputs:
```
'def _lambdifygenerated():\n    return (1,)\n'
```

But SymPy 1.10 gives

```
'def _lambdifygenerated():\n    return (1)\n'
```
Note the missing comma after `1` that causes an integer to be returned instead of a tuple. 

For tuples with two or more elements, the generated code is correct:
```python
inspect.getsource(lambdify([], tuple([1, 2])))
```
In SymPy  1.10 and under, outputs:

```
'def _lambdifygenerated():\n    return (1, 2)\n'
```
This result is expected.

Not sure if this is a regression. As this breaks my program which assumes the return type to always be a tuple, could you suggest a workaround from the code generation side? Thank you. 


## Hints

Bisected to 6ccd2b07ded5074941bb80b5967d60fa1593007a from #21993.

CC @bjodah 
As a work around for now, you can use the `Tuple` object from sympy. Note that it is constructed slightly differently from a python `tuple`, rather than giving a `list`, you give it multiple input arguments (or you can put a `*` in front of your list):
```python
>>> inspect.getsource(lambdify([], Tuple(*[1])))
def _lambdifygenerated():\n    return (1,)\n
>>> inspect.getsource(lambdify([], Tuple(1)))
def _lambdifygenerated():\n    return (1,)\n
```
Of course the problem should also be fixed. `lambdify` is in a bit of an awkward spot, it supports a lot of different input and output formats that make it practically impossible to keep any functionality that is not explicitly tested for whenever you make a change.



> As a work around for now, you can use the `Tuple` object from sympy. Note that it is constructed slightly differently from a python `tuple`, rather than giving a `list`, you give it multiple input arguments (or you can put a `*` in front of your list):

Thank you! This is tested to be working in SymPy 1.6-1.10. Consider this issue addressed for now. 

`lambdify` (or generally, the code generation) is an extremely useful tool. Are you aware of any roadmap or discussions on the refactoring of `lambdify` (or codegen)? I would like to contribute to it. 

I want to put out a 1.10.1 bugfix release. Should this be fixed?

## Patch

```diff

diff --git a/sympy/utilities/lambdify.py b/sympy/utilities/lambdify.py
--- a/sympy/utilities/lambdify.py
+++ b/sympy/utilities/lambdify.py
@@ -956,9 +956,9 @@ def _recursive_to_string(doprint, arg):
         return doprint(arg)
     elif iterable(arg):
         if isinstance(arg, list):
-            left, right = "[]"
+            left, right = "[", "]"
         elif isinstance(arg, tuple):
-            left, right = "()"
+            left, right = "(", ",)"
         else:
             raise NotImplementedError("unhandled type: %s, %s" % (type(arg), arg))
         return left +', '.join(_recursive_to_string(doprint, e) for e in arg) + right


```

## Test Patch

```diff
diff --git a/sympy/utilities/tests/test_lambdify.py b/sympy/utilities/tests/test_lambdify.py
--- a/sympy/utilities/tests/test_lambdify.py
+++ b/sympy/utilities/tests/test_lambdify.py
@@ -1192,6 +1192,8 @@ def test_issue_14941():
     # test tuple
     f2 = lambdify([x, y], (y, x), 'sympy')
     assert f2(2, 3) == (3, 2)
+    f2b = lambdify([], (1,))  # gh-23224
+    assert f2b() == (1,)
 
     # test list
     f3 = lambdify([x, y], [y, x], 'sympy')

```

## Test Information

**Tests that should FAIL→PASS**: ["test_issue_14941"]

**Tests that should PASS→PASS**: ["test_no_args", "test_single_arg", "test_list_args", "test_nested_args", "test_str_args", "test_own_namespace_1", "test_own_namespace_2", "test_own_module", "test_bad_args", "test_atoms", "test_sympy_lambda", "test_math_lambda", "test_mpmath_lambda", "test_number_precision", "test_mpmath_precision", "test_math_transl", "test_mpmath_transl", "test_empty_modules", "test_exponentiation", "test_sqrt", "test_trig", "test_integral", "test_double_integral", "test_vector_simple", "test_vector_discontinuous", "test_trig_symbolic", "test_trig_float", "test_docs", "test_math", "test_sin", "test_matrix", "test_issue9474", "test_sym_single_arg", "test_sym_list_args", "test_sym_integral", "test_namespace_order", "test_imps", "test_imps_errors", "test_imps_wrong_args", "test_lambdify_imps", "test_dummification", "test_curly_matrix_symbol", "test_python_keywords", "test_lambdify_docstring", "test_special_printers", "test_true_false", "test_issue_2790", "test_issue_12092", "test_issue_14911", "test_ITE", "test_Min_Max", "test_issue_12173", "test_sinc_mpmath", "test_lambdify_dummy_arg", "test_lambdify_mixed_symbol_dummy_args", "test_lambdify_inspect", "test_lambdify_Derivative_arg_issue_16468", "test_imag_real", "test_single_e", "test_beta_math", "test_lambdify_cse"]

**Base Commit**: fdc707f73a65a429935c01532cd3970d3355eab6
**Environment Setup Commit**: 9a6104eab0ea7ac191a09c24f3e2d79dcd66bda5
