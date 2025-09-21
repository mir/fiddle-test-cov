# sympy__sympy-21627

**Repository**: sympy/sympy
**Created**: 2021-06-16T17:29:41Z
**Version**: 1.9

## Problem Statement

Bug: maximum recusion depth error when checking is_zero of cosh expression
The following code causes a `RecursionError: maximum recursion depth exceeded while calling a Python object` error when checked if it is zero:
```
expr =sympify("cosh(acos(-i + acosh(-g + i)))")
expr.is_zero
```


## Hints

The problem is with `Abs`:
```python
In [7]: e = S("im(acos(-i + acosh(-g + i)))")                                                        

In [8]: abs(e)
```
That leads to this:
https://github.com/sympy/sympy/blob/126f80578140e752ad5135aac77b8ff887eede3e/sympy/functions/elementary/complexes.py#L616-L621
and then `sqrt` leads here:
https://github.com/sympy/sympy/blob/126f80578140e752ad5135aac77b8ff887eede3e/sympy/core/power.py#L336
which goes to here:
https://github.com/sympy/sympy/blob/126f80578140e752ad5135aac77b8ff887eede3e/sympy/core/power.py#L418
And then that's trying to compute the same abs again.

I'm not sure where the cycle should be broken but the code in `Abs.eval` seems excessively complicated.

> That leads to this:

The test should be changed to:
```python
_arg = signsimp(arg, evaluate=False)
if _arg != conj or _arg != -conj:
```
 We should probably never come to this test when the argument is real. There should be something like `if arg.is_extended_real` before `conj` is computed.
There are tests for nonnegative, nonpositive and imaginary. So an additional test before coming to this part would be
```python
if arg.is_extended_real:
    return
...
_arg = signsimp(arg, evaluate=False)
if _arg not in (conj, -conj):
...
```

## Patch

```diff

diff --git a/sympy/functions/elementary/complexes.py b/sympy/functions/elementary/complexes.py
--- a/sympy/functions/elementary/complexes.py
+++ b/sympy/functions/elementary/complexes.py
@@ -607,6 +607,8 @@ def eval(cls, arg):
             arg2 = -S.ImaginaryUnit * arg
             if arg2.is_extended_nonnegative:
                 return arg2
+        if arg.is_extended_real:
+            return
         # reject result if all new conjugates are just wrappers around
         # an expression that was already in the arg
         conj = signsimp(arg.conjugate(), evaluate=False)


```

## Test Patch

```diff
diff --git a/sympy/functions/elementary/tests/test_complexes.py b/sympy/functions/elementary/tests/test_complexes.py
--- a/sympy/functions/elementary/tests/test_complexes.py
+++ b/sympy/functions/elementary/tests/test_complexes.py
@@ -464,6 +464,8 @@ def test_Abs():
     # issue 19627
     f = Function('f', positive=True)
     assert sqrt(f(x)**2) == f(x)
+    # issue 21625
+    assert unchanged(Abs, S("im(acos(-i + acosh(-g + i)))"))
 
 
 def test_Abs_rewrite():

```

## Test Information

**Tests that should FAIL→PASS**: ["test_Abs"]

**Tests that should PASS→PASS**: ["test_re", "test_im", "test_sign", "test_as_real_imag", "test_Abs_rewrite", "test_Abs_real", "test_Abs_properties", "test_abs", "test_arg", "test_arg_rewrite", "test_adjoint", "test_conjugate", "test_conjugate_transpose", "test_transpose", "test_polarify", "test_unpolarify", "test_issue_4035", "test_issue_3206", "test_issue_4754_derivative_conjugate", "test_derivatives_issue_4757", "test_issue_11413", "test_periodic_argument", "test_principal_branch", "test_issue_14216", "test_issue_14238", "test_zero_assumptions"]

**Base Commit**: 126f80578140e752ad5135aac77b8ff887eede3e
**Environment Setup Commit**: f9a6f50ec0c74d935c50a6e9c9b2cb0469570d91
