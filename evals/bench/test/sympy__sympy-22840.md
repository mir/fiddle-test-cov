# sympy__sympy-22840

**Repository**: sympy/sympy
**Created**: 2022-01-11T17:34:54Z
**Version**: 1.10

## Problem Statement

cse() has strange behaviour for MatrixSymbol indexing
Example: 
```python
import sympy as sp
from pprint import pprint


def sub_in_matrixsymbols(exp, matrices):
    for matrix in matrices:
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                name = "%s_%d_%d" % (matrix.name, i, j)
                sym = sp.symbols(name)
                exp = exp.subs(sym, matrix[i, j])
    return exp


def t44(name):
    return sp.Matrix(4, 4, lambda i, j: sp.symbols('%s_%d_%d' % (name, i, j)))


# Construct matrices of symbols that work with our
# expressions. (MatrixSymbols does not.)
a = t44("a")
b = t44("b")

# Set up expression. This is a just a simple example.
e = a * b

# Put in matrixsymbols. (Gives array-input in codegen.)
e2 = sub_in_matrixsymbols(e, [sp.MatrixSymbol("a", 4, 4), sp.MatrixSymbol("b", 4, 4)])
cse_subs, cse_reduced = sp.cse(e2)
pprint((cse_subs, cse_reduced))

# Codegen, etc..
print "\nccode:"
for sym, expr in cse_subs:
    constants, not_c, c_expr = sympy.printing.ccode(
        expr,
        human=False,
        assign_to=sympy.printing.ccode(sym),
    )
    assert not constants, constants
    assert not not_c, not_c
    print "%s\n" % c_expr

```

This gives the following output:

```
([(x0, a),
  (x1, x0[0, 0]),
  (x2, b),
  (x3, x2[0, 0]),
  (x4, x0[0, 1]),
  (x5, x2[1, 0]),
  (x6, x0[0, 2]),
  (x7, x2[2, 0]),
  (x8, x0[0, 3]),
  (x9, x2[3, 0]),
  (x10, x2[0, 1]),
  (x11, x2[1, 1]),
  (x12, x2[2, 1]),
  (x13, x2[3, 1]),
  (x14, x2[0, 2]),
  (x15, x2[1, 2]),
  (x16, x2[2, 2]),
  (x17, x2[3, 2]),
  (x18, x2[0, 3]),
  (x19, x2[1, 3]),
  (x20, x2[2, 3]),
  (x21, x2[3, 3]),
  (x22, x0[1, 0]),
  (x23, x0[1, 1]),
  (x24, x0[1, 2]),
  (x25, x0[1, 3]),
  (x26, x0[2, 0]),
  (x27, x0[2, 1]),
  (x28, x0[2, 2]),
  (x29, x0[2, 3]),
  (x30, x0[3, 0]),
  (x31, x0[3, 1]),
  (x32, x0[3, 2]),
  (x33, x0[3, 3])],
 [Matrix([
[    x1*x3 + x4*x5 + x6*x7 + x8*x9,     x1*x10 + x11*x4 + x12*x6 + x13*x8,     x1*x14 + x15*x4 + x16*x6 + x17*x8,     x1*x18 + x19*x4 + x20*x6 + x21*x8],
[x22*x3 + x23*x5 + x24*x7 + x25*x9, x10*x22 + x11*x23 + x12*x24 + x13*x25, x14*x22 + x15*x23 + x16*x24 + x17*x25, x18*x22 + x19*x23 + x20*x24 + x21*x25],
[x26*x3 + x27*x5 + x28*x7 + x29*x9, x10*x26 + x11*x27 + x12*x28 + x13*x29, x14*x26 + x15*x27 + x16*x28 + x17*x29, x18*x26 + x19*x27 + x20*x28 + x21*x29],
[x3*x30 + x31*x5 + x32*x7 + x33*x9, x10*x30 + x11*x31 + x12*x32 + x13*x33, x14*x30 + x15*x31 + x16*x32 + x17*x33, x18*x30 + x19*x31 + x20*x32 + x21*x33]])])

ccode:
x0[0] = a[0];
x0[1] = a[1];
x0[2] = a[2];
x0[3] = a[3];
x0[4] = a[4];
x0[5] = a[5];
x0[6] = a[6];
x0[7] = a[7];
x0[8] = a[8];
x0[9] = a[9];
x0[10] = a[10];
x0[11] = a[11];
x0[12] = a[12];
x0[13] = a[13];
x0[14] = a[14];
x0[15] = a[15];
x1 = x0[0];
x2[0] = b[0];
x2[1] = b[1];
x2[2] = b[2];
x2[3] = b[3];
x2[4] = b[4];
x2[5] = b[5];
x2[6] = b[6];
x2[7] = b[7];
x2[8] = b[8];
x2[9] = b[9];
x2[10] = b[10];
x2[11] = b[11];
x2[12] = b[12];
x2[13] = b[13];
x2[14] = b[14];
x2[15] = b[15];
x3 = x2[0];
x4 = x0[1];
x5 = x2[4];
x6 = x0[2];
x7 = x2[8];
x8 = x0[3];
x9 = x2[12];
x10 = x2[1];
x11 = x2[5];
x12 = x2[9];
x13 = x2[13];
x14 = x2[2];
x15 = x2[6];
x16 = x2[10];
x17 = x2[14];
x18 = x2[3];
x19 = x2[7];
x20 = x2[11];
x21 = x2[15];
x22 = x0[4];
x23 = x0[5];
x24 = x0[6];
x25 = x0[7];
x26 = x0[8];
x27 = x0[9];
x28 = x0[10];
x29 = x0[11];
x30 = x0[12];
x31 = x0[13];
x32 = x0[14];
x33 = x0[15];
```

`x0` and `x2` are just copies of the matrices `a` and `b`, respectively.


## Hints

Can you create a very simple example using MatrixSymbol and the expected output that you'd like to see?
I think one would expect the output to be similar to the following (except for the expression returned by CSE being a matrix where the individual elements are terms as defined by matrix multiplication, that is, unchanged by `cse()`).

```py
import sympy as sp
from pprint import pprint
import sympy.printing.ccode


def print_ccode(assign_to, expr):
    constants, not_c, c_expr = sympy.printing.ccode(
        expr,
        human=False,
        assign_to=assign_to,
    )
    assert not constants, constants
    assert not not_c, not_c
    print "%s" % c_expr


a = sp.MatrixSymbol("a", 4, 4)
b = sp.MatrixSymbol("b", 4, 4)

# Set up expression. This is a just a simple example.
e = a * b
print "\nexpr:"
print e

cse_subs, cse_reduced = sp.cse(e)
print "\ncse(expr):"
pprint((cse_subs, cse_reduced))

# Codegen.
print "\nccode:"
for sym, expr in cse_subs:
    print_ccode(sympy.printing.ccode(sym), expr)
assert len(cse_reduced) == 1
print_ccode(sympy.printing.ccode(sp.symbols("result")), cse_reduced[0])
```

Gives the output:

```
expr:
a*b

cse(expr):
([], [a*b])

ccode:
result[0] = a[0]*b[0] + a[1]*b[4] + a[2]*b[8] + a[3]*b[12];
result[1] = a[0]*b[1] + a[1]*b[5] + a[2]*b[9] + a[3]*b[13];
result[2] = a[0]*b[2] + a[1]*b[6] + a[2]*b[10] + a[3]*b[14];
result[3] = a[0]*b[3] + a[1]*b[7] + a[2]*b[11] + a[3]*b[15];
result[4] = a[4]*b[0] + a[5]*b[4] + a[6]*b[8] + a[7]*b[12];
result[5] = a[4]*b[1] + a[5]*b[5] + a[6]*b[9] + a[7]*b[13];
result[6] = a[4]*b[2] + a[5]*b[6] + a[6]*b[10] + a[7]*b[14];
result[7] = a[4]*b[3] + a[5]*b[7] + a[6]*b[11] + a[7]*b[15];
result[8] = a[8]*b[0] + a[9]*b[4] + a[10]*b[8] + a[11]*b[12];
result[9] = a[8]*b[1] + a[9]*b[5] + a[10]*b[9] + a[11]*b[13];
result[10] = a[8]*b[2] + a[9]*b[6] + a[10]*b[10] + a[11]*b[14];
result[11] = a[8]*b[3] + a[9]*b[7] + a[10]*b[11] + a[11]*b[15];
result[12] = a[12]*b[0] + a[13]*b[4] + a[14]*b[8] + a[15]*b[12];
result[13] = a[12]*b[1] + a[13]*b[5] + a[14]*b[9] + a[15]*b[13];
result[14] = a[12]*b[2] + a[13]*b[6] + a[14]*b[10] + a[15]*b[14];
result[15] = a[12]*b[3] + a[13]*b[7] + a[14]*b[11] + a[15]*b[15];
```
Thanks. Note that it doesn't look like cse is well tested (i.e. designed) for MatrixSymbols based on the unit tests: https://github.com/sympy/sympy/blob/master/sympy/simplify/tests/test_cse.py#L315. Those tests don't really prove that it works as desired. So this definitely needs to be fixed.
The first part works as expected:

```
In [1]: import sympy as sm

In [2]: M = sm.MatrixSymbol('M', 3, 3)

In [3]: B = sm.MatrixSymbol('B', 3, 3)

In [4]: M * B
Out[4]: M*B

In [5]: sm.cse(M * B)
Out[5]: ([], [M*B])
```
For the ccode of an expression of MatrixSymbols, I would not expect it to print the results as you have them. MatrixSymbols should map to a matrix algebra library like BLAS and LINPACK. But Matrix, on the other hand, should do what you expect. Note how this works:

```
In [8]: M = sm.Matrix(3, 3, lambda i, j: sm.Symbol('M_{}{}'.format(i, j)))

In [9]: M
Out[9]: 
Matrix([
[M_00, M_01, M_02],
[M_10, M_11, M_12],
[M_20, M_21, M_22]])

In [10]: B = sm.Matrix(3, 3, lambda i, j: sm.Symbol('B_{}{}'.format(i, j)))

In [11]: B
Out[11]: 
Matrix([
[B_00, B_01, B_02],
[B_10, B_11, B_12],
[B_20, B_21, B_22]])

In [12]: M * B
Out[12]: 
Matrix([
[B_00*M_00 + B_10*M_01 + B_20*M_02, B_01*M_00 + B_11*M_01 + B_21*M_02, B_02*M_00 + B_12*M_01 + B_22*M_02],
[B_00*M_10 + B_10*M_11 + B_20*M_12, B_01*M_10 + B_11*M_11 + B_21*M_12, B_02*M_10 + B_12*M_11 + B_22*M_12],
[B_00*M_20 + B_10*M_21 + B_20*M_22, B_01*M_20 + B_11*M_21 + B_21*M_22, B_02*M_20 + B_12*M_21 + B_22*M_22]])

In [13]: sm.cse(M * B)
Out[13]: 
([], [Matrix([
  [B_00*M_00 + B_10*M_01 + B_20*M_02, B_01*M_00 + B_11*M_01 + B_21*M_02, B_02*M_00 + B_12*M_01 + B_22*M_02],
  [B_00*M_10 + B_10*M_11 + B_20*M_12, B_01*M_10 + B_11*M_11 + B_21*M_12, B_02*M_10 + B_12*M_11 + B_22*M_12],
  [B_00*M_20 + B_10*M_21 + B_20*M_22, B_01*M_20 + B_11*M_21 + B_21*M_22, B_02*M_20 + B_12*M_21 + B_22*M_22]])])

In [17]: print(sm.ccode(M * B, assign_to=sm.MatrixSymbol('E', 3, 3)))
E[0] = B_00*M_00 + B_10*M_01 + B_20*M_02;
E[1] = B_01*M_00 + B_11*M_01 + B_21*M_02;
E[2] = B_02*M_00 + B_12*M_01 + B_22*M_02;
E[3] = B_00*M_10 + B_10*M_11 + B_20*M_12;
E[4] = B_01*M_10 + B_11*M_11 + B_21*M_12;
E[5] = B_02*M_10 + B_12*M_11 + B_22*M_12;
E[6] = B_00*M_20 + B_10*M_21 + B_20*M_22;
E[7] = B_01*M_20 + B_11*M_21 + B_21*M_22;
E[8] = B_02*M_20 + B_12*M_21 + B_22*M_22;
```
But in order to get a single input argument from codegen it cannot be different symbols, and if you replace each symbol with a `MatrixSymbol[i, j]` then `cse()` starts doing the above non-optiimizations for some reason.
As far as I know, `codegen` does not work with Matrix or MatrixSymbol's in any meaningful way. There are related issues:

#11456
#4367
#10522

In general, there needs to be work done in the code generators to properly support matrices.

As a work around, I suggest using `ccode` and a custom template to get the result you want.

## Patch

```diff

diff --git a/sympy/simplify/cse_main.py b/sympy/simplify/cse_main.py
--- a/sympy/simplify/cse_main.py
+++ b/sympy/simplify/cse_main.py
@@ -567,6 +567,7 @@ def tree_cse(exprs, symbols, opt_subs=None, order='canonical', ignore=()):
         Substitutions containing any Symbol from ``ignore`` will be ignored.
     """
     from sympy.matrices.expressions import MatrixExpr, MatrixSymbol, MatMul, MatAdd
+    from sympy.matrices.expressions.matexpr import MatrixElement
     from sympy.polys.rootoftools import RootOf
 
     if opt_subs is None:
@@ -586,7 +587,10 @@ def _find_repeated(expr):
         if isinstance(expr, RootOf):
             return
 
-        if isinstance(expr, Basic) and (expr.is_Atom or expr.is_Order):
+        if isinstance(expr, Basic) and (
+                expr.is_Atom or
+                expr.is_Order or
+                isinstance(expr, (MatrixSymbol, MatrixElement))):
             if expr.is_Symbol:
                 excluded_symbols.add(expr)
             return


```

## Test Patch

```diff
diff --git a/sympy/simplify/tests/test_cse.py b/sympy/simplify/tests/test_cse.py
--- a/sympy/simplify/tests/test_cse.py
+++ b/sympy/simplify/tests/test_cse.py
@@ -347,6 +347,10 @@ def test_cse_MatrixSymbol():
     B = MatrixSymbol("B", n, n)
     assert cse(B) == ([], [B])
 
+    assert cse(A[0] * A[0]) == ([], [A[0]*A[0]])
+
+    assert cse(A[0,0]*A[0,1] + A[0,0]*A[0,1]*A[0,2]) == ([(x0, A[0, 0]*A[0, 1])], [x0*A[0, 2] + x0])
+
 def test_cse_MatrixExpr():
     A = MatrixSymbol('A', 3, 3)
     y = MatrixSymbol('y', 3, 1)
diff --git a/sympy/utilities/tests/test_codegen.py b/sympy/utilities/tests/test_codegen.py
--- a/sympy/utilities/tests/test_codegen.py
+++ b/sympy/utilities/tests/test_codegen.py
@@ -531,26 +531,9 @@ def test_multidim_c_argument_cse():
         '#include "test.h"\n'
         "#include <math.h>\n"
         "void c(double *A, double *b, double *out) {\n"
-        "   double x0[9];\n"
-        "   x0[0] = A[0];\n"
-        "   x0[1] = A[1];\n"
-        "   x0[2] = A[2];\n"
-        "   x0[3] = A[3];\n"
-        "   x0[4] = A[4];\n"
-        "   x0[5] = A[5];\n"
-        "   x0[6] = A[6];\n"
-        "   x0[7] = A[7];\n"
-        "   x0[8] = A[8];\n"
-        "   double x1[3];\n"
-        "   x1[0] = b[0];\n"
-        "   x1[1] = b[1];\n"
-        "   x1[2] = b[2];\n"
-        "   const double x2 = x1[0];\n"
-        "   const double x3 = x1[1];\n"
-        "   const double x4 = x1[2];\n"
-        "   out[0] = x2*x0[0] + x3*x0[1] + x4*x0[2];\n"
-        "   out[1] = x2*x0[3] + x3*x0[4] + x4*x0[5];\n"
-        "   out[2] = x2*x0[6] + x3*x0[7] + x4*x0[8];\n"
+        "   out[0] = A[0]*b[0] + A[1]*b[1] + A[2]*b[2];\n"
+        "   out[1] = A[3]*b[0] + A[4]*b[1] + A[5]*b[2];\n"
+        "   out[2] = A[6]*b[0] + A[7]*b[1] + A[8]*b[2];\n"
         "}\n"
     )
     assert code == expected

```

## Test Information

**Tests that should FAIL→PASS**: ["test_cse_MatrixSymbol", "test_multidim_c_argument_cse"]

**Tests that should PASS→PASS**: ["test_numbered_symbols", "test_preprocess_for_cse", "test_postprocess_for_cse", "test_cse_single", "test_cse_single2", "test_cse_not_possible", "test_nested_substitution", "test_subtraction_opt", "test_multiple_expressions", "test_bypass_non_commutatives", "test_issue_4498", "test_issue_4020", "test_issue_4203", "test_issue_6263", "test_dont_cse_tuples", "test_pow_invpow", "test_postprocess", "test_issue_4499", "test_issue_6169", "test_cse_Indexed", "test_cse_MatrixExpr", "test_Piecewise", "test_ignore_order_terms", "test_name_conflict", "test_name_conflict_cust_symbols", "test_symbols_exhausted_error", "test_issue_7840", "test_issue_8891", "test_issue_11230", "test_hollow_rejection", "test_cse_ignore", "test_cse_ignore_issue_15002", "test_cse__performance", "test_issue_12070", "test_issue_13000", "test_issue_18203", "test_unevaluated_mul", "test_cse_release_variables", "test_cse_list", "test_issue_18991", "test_Routine_argument_order", "test_empty_c_code", "test_empty_c_code_with_comment", "test_empty_c_header", "test_simple_c_code", "test_c_code_reserved_words", "test_numbersymbol_c_code", "test_c_code_argument_order", "test_simple_c_header", "test_simple_c_codegen", "test_multiple_results_c", "test_no_results_c", "test_ansi_math1_codegen", "test_ansi_math2_codegen", "test_complicated_codegen", "test_loops_c", "test_dummy_loops_c", "test_partial_loops_c", "test_output_arg_c", "test_output_arg_c_reserved_words", "test_ccode_results_named_ordered", "test_ccode_matrixsymbol_slice", "test_ccode_cse", "test_ccode_unused_array_arg", "test_empty_f_code", "test_empty_f_code_with_header", "test_empty_f_header", "test_simple_f_code", "test_numbersymbol_f_code", "test_erf_f_code", "test_f_code_argument_order", "test_simple_f_header", "test_simple_f_codegen", "test_multiple_results_f", "test_no_results_f", "test_intrinsic_math_codegen", "test_intrinsic_math2_codegen", "test_complicated_codegen_f95", "test_loops", "test_dummy_loops_f95", "test_loops_InOut", "test_partial_loops_f", "test_output_arg_f", "test_inline_function", "test_f_code_call_signature_wrap", "test_check_case", "test_check_case_false_positive", "test_c_fortran_omit_routine_name", "test_fcode_matrix_output", "test_fcode_results_named_ordered", "test_fcode_matrixsymbol_slice", "test_fcode_matrixsymbol_slice_autoname", "test_global_vars", "test_custom_codegen", "test_c_with_printer"]

**Base Commit**: d822fcba181155b85ff2b29fe525adbafb22b448
**Environment Setup Commit**: fd40404e72921b9e52a5f9582246e4a6cd96c431
