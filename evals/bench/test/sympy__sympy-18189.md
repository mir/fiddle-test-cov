# sympy__sympy-18189

**Repository**: sympy/sympy
**Created**: 2019-12-31T15:45:24Z
**Version**: 1.6

## Problem Statement

diophantine: incomplete results depending on syms order with permute=True
```
In [10]: diophantine(n**4 + m**4 - 2**4 - 3**4, syms=(m,n), permute=True)
Out[10]: {(-3, -2), (-3, 2), (-2, -3), (-2, 3), (2, -3), (2, 3), (3, -2), (3, 2)}

In [11]: diophantine(n**4 + m**4 - 2**4 - 3**4, syms=(n,m), permute=True)
Out[11]: {(3, 2)}
```

diophantine: incomplete results depending on syms order with permute=True
```
In [10]: diophantine(n**4 + m**4 - 2**4 - 3**4, syms=(m,n), permute=True)
Out[10]: {(-3, -2), (-3, 2), (-2, -3), (-2, 3), (2, -3), (2, 3), (3, -2), (3, 2)}

In [11]: diophantine(n**4 + m**4 - 2**4 - 3**4, syms=(n,m), permute=True)
Out[11]: {(3, 2)}
```



## Hints

```diff
diff --git a/sympy/solvers/diophantine.py b/sympy/solvers/diophantine.py
index 6092e35..b43f5c1 100644
--- a/sympy/solvers/diophantine.py
+++ b/sympy/solvers/diophantine.py
@@ -182,7 +182,7 @@ def diophantine(eq, param=symbols("t", integer=True), syms=None,
             if syms != var:
                 dict_sym_index = dict(zip(syms, range(len(syms))))
                 return {tuple([t[dict_sym_index[i]] for i in var])
-                            for t in diophantine(eq, param)}
+                            for t in diophantine(eq, param, permute=permute)}
         n, d = eq.as_numer_denom()
         if n.is_number:
             return set()
```
Based on a cursory glance at the code it seems that `permute=True` is lost when `diophantine` calls itself:
https://github.com/sympy/sympy/blob/d98abf000b189d4807c6f67307ebda47abb997f8/sympy/solvers/diophantine.py#L182-L185.
That should be easy to solve; I'll include a fix in my next PR (which is related).
Ah, ninja'd by @smichr :-)
```diff
diff --git a/sympy/solvers/diophantine.py b/sympy/solvers/diophantine.py
index 6092e35..b43f5c1 100644
--- a/sympy/solvers/diophantine.py
+++ b/sympy/solvers/diophantine.py
@@ -182,7 +182,7 @@ def diophantine(eq, param=symbols("t", integer=True), syms=None,
             if syms != var:
                 dict_sym_index = dict(zip(syms, range(len(syms))))
                 return {tuple([t[dict_sym_index[i]] for i in var])
-                            for t in diophantine(eq, param)}
+                            for t in diophantine(eq, param, permute=permute)}
         n, d = eq.as_numer_denom()
         if n.is_number:
             return set()
```
Based on a cursory glance at the code it seems that `permute=True` is lost when `diophantine` calls itself:
https://github.com/sympy/sympy/blob/d98abf000b189d4807c6f67307ebda47abb997f8/sympy/solvers/diophantine.py#L182-L185.
That should be easy to solve; I'll include a fix in my next PR (which is related).
Ah, ninja'd by @smichr :-)

## Patch

```diff

diff --git a/sympy/solvers/diophantine.py b/sympy/solvers/diophantine.py
--- a/sympy/solvers/diophantine.py
+++ b/sympy/solvers/diophantine.py
@@ -182,7 +182,7 @@ def diophantine(eq, param=symbols("t", integer=True), syms=None,
             if syms != var:
                 dict_sym_index = dict(zip(syms, range(len(syms))))
                 return {tuple([t[dict_sym_index[i]] for i in var])
-                            for t in diophantine(eq, param)}
+                            for t in diophantine(eq, param, permute=permute)}
         n, d = eq.as_numer_denom()
         if n.is_number:
             return set()


```

## Test Patch

```diff
diff --git a/sympy/solvers/tests/test_diophantine.py b/sympy/solvers/tests/test_diophantine.py
--- a/sympy/solvers/tests/test_diophantine.py
+++ b/sympy/solvers/tests/test_diophantine.py
@@ -547,6 +547,13 @@ def test_diophantine():
     assert diophantine(x**2 + y**2 +3*x- 5, permute=True) == \
         set([(-1, 1), (-4, -1), (1, -1), (1, 1), (-4, 1), (-1, -1), (4, 1), (4, -1)])
 
+
+    #test issue 18186
+    assert diophantine(y**4 + x**4 - 2**4 - 3**4, syms=(x, y), permute=True) == \
+        set([(-3, -2), (-3, 2), (-2, -3), (-2, 3), (2, -3), (2, 3), (3, -2), (3, 2)])
+    assert diophantine(y**4 + x**4 - 2**4 - 3**4, syms=(y, x), permute=True) == \
+        set([(-3, -2), (-3, 2), (-2, -3), (-2, 3), (2, -3), (2, 3), (3, -2), (3, 2)])
+
     # issue 18122
     assert check_solutions(x**2-y)
     assert check_solutions(y**2-x)
@@ -554,6 +561,7 @@ def test_diophantine():
     assert diophantine((y**2-x), t) == set([(t**2, -t)])
 
 
+
 def test_general_pythagorean():
     from sympy.abc import a, b, c, d, e
 

```

## Test Information

**Tests that should FAIL→PASS**: ["test_diophantine"]

**Tests that should PASS→PASS**: ["test_input_format", "test_univariate", "test_classify_diop", "test_linear", "test_quadratic_simple_hyperbolic_case", "test_quadratic_elliptical_case", "test_quadratic_parabolic_case", "test_quadratic_perfect_square", "test_quadratic_non_perfect_square", "test_issue_9106", "test_issue_18138", "test_DN", "test_bf_pell", "test_length", "test_transformation_to_pell", "test_find_DN", "test_ldescent", "test_diop_ternary_quadratic_normal", "test_transformation_to_normal", "test_diop_ternary_quadratic", "test_square_factor", "test_parametrize_ternary_quadratic", "test_no_square_ternary_quadratic", "test_descent", "test_general_pythagorean", "test_diop_general_sum_of_squares_quick", "test_diop_partition", "test_prime_as_sum_of_two_squares", "test_sum_of_three_squares", "test_sum_of_four_squares", "test_power_representation", "test_assumptions", "test_diopcoverage", "test_holzer", "test_issue_9539", "test_issue_8943", "test_diop_sum_of_even_powers", "test_sum_of_squares_powers", "test__can_do_sum_of_squares", "test_diophantine_permute_sign", "test_issue_9538"]

**Base Commit**: 1923822ddf8265199dbd9ef9ce09641d3fd042b9
**Environment Setup Commit**: 28b41c73c12b70d6ad9f6e45109a80649c4456da
