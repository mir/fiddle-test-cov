# sympy__sympy-16792

**Repository**: sympy/sympy
**Created**: 2019-05-09T03:40:54Z
**Version**: 1.5

## Problem Statement

autowrap with cython backend fails when array arguments do not appear in wrapped expr
When using the cython backend for autowrap, it appears that the code is not correctly generated when the function in question has array arguments that do not appear in the final expression. A minimal counterexample is:

```python
from sympy.utilities.autowrap import autowrap
from sympy import MatrixSymbol
import numpy as np

x = MatrixSymbol('x', 2, 1)
expr = 1.0
f = autowrap(expr, args=(x,), backend='cython')

f(np.array([[1.0, 2.0]]))
```

This should of course return `1.0` but instead fails with:
```python
TypeError: only size-1 arrays can be converted to Python scalars
```

A little inspection reveals that this is because the corresponding C function is generated with an incorrect signature:

```C
double autofunc(double x) {

   double autofunc_result;
   autofunc_result = 1.0;
   return autofunc_result;

}
```

(`x` should be `double *`, not `double` in this case)

I've found that this error won't occur so long as `expr` depends at least in part on each argument. For example this slight modification of the above counterexample works perfectly:

```python
from sympy.utilities.autowrap import autowrap
from sympy import MatrixSymbol
import numpy as np

x = MatrixSymbol('x', 2, 1)
# now output depends on x
expr = x[0,0]
f = autowrap(expr, args=(x,), backend='cython')

# returns 1.0 as expected, without failure
f(np.array([[1.0, 2.0]]))
```

This may seem like a silly issue ("why even have `x` as an argument if it doesn't appear in the expression you're trying to evaluate?"). But of course in interfacing with external libraries (e.g. for numerical integration), one often needs functions to have a pre-defined signature regardless of whether a given argument contributes to the output.

I think I've identified the problem in `codegen` and will suggest a PR shortly.


## Patch

```diff

diff --git a/sympy/utilities/codegen.py b/sympy/utilities/codegen.py
--- a/sympy/utilities/codegen.py
+++ b/sympy/utilities/codegen.py
@@ -695,6 +695,11 @@ def routine(self, name, expr, argument_sequence=None, global_vars=None):
         arg_list = []
 
         # setup input argument list
+
+        # helper to get dimensions for data for array-like args
+        def dimensions(s):
+            return [(S.Zero, dim - 1) for dim in s.shape]
+
         array_symbols = {}
         for array in expressions.atoms(Indexed) | local_expressions.atoms(Indexed):
             array_symbols[array.base.label] = array
@@ -703,11 +708,8 @@ def routine(self, name, expr, argument_sequence=None, global_vars=None):
 
         for symbol in sorted(symbols, key=str):
             if symbol in array_symbols:
-                dims = []
                 array = array_symbols[symbol]
-                for dim in array.shape:
-                    dims.append((S.Zero, dim - 1))
-                metadata = {'dimensions': dims}
+                metadata = {'dimensions': dimensions(array)}
             else:
                 metadata = {}
 
@@ -739,7 +741,11 @@ def routine(self, name, expr, argument_sequence=None, global_vars=None):
                 try:
                     new_args.append(name_arg_dict[symbol])
                 except KeyError:
-                    new_args.append(InputArgument(symbol))
+                    if isinstance(symbol, (IndexedBase, MatrixSymbol)):
+                        metadata = {'dimensions': dimensions(symbol)}
+                    else:
+                        metadata = {}
+                    new_args.append(InputArgument(symbol, **metadata))
             arg_list = new_args
 
         return Routine(name, arg_list, return_val, local_vars, global_vars)


```

## Test Patch

```diff
diff --git a/sympy/utilities/tests/test_codegen.py b/sympy/utilities/tests/test_codegen.py
--- a/sympy/utilities/tests/test_codegen.py
+++ b/sympy/utilities/tests/test_codegen.py
@@ -582,6 +582,25 @@ def test_ccode_cse():
     )
     assert source == expected
 
+def test_ccode_unused_array_arg():
+    x = MatrixSymbol('x', 2, 1)
+    # x does not appear in output
+    name_expr = ("test", 1.0)
+    generator = CCodeGen()
+    result = codegen(name_expr, code_gen=generator, header=False, empty=False, argument_sequence=(x,))
+    source = result[0][1]
+    # note: x should appear as (double *)
+    expected = (
+        '#include "test.h"\n'
+        '#include <math.h>\n'
+        'double test(double *x) {\n'
+        '   double test_result;\n'
+        '   test_result = 1.0;\n'
+        '   return test_result;\n'
+        '}\n'
+    )
+    assert source == expected
+
 def test_empty_f_code():
     code_gen = FCodeGen()
     source = get_string(code_gen.dump_f95, [])

```

## Test Information

**Tests that should FAIL→PASS**: ["test_ccode_unused_array_arg"]

**Tests that should PASS→PASS**: ["test_Routine_argument_order", "test_empty_c_code", "test_empty_c_code_with_comment", "test_empty_c_header", "test_simple_c_code", "test_c_code_reserved_words", "test_numbersymbol_c_code", "test_c_code_argument_order", "test_simple_c_header", "test_simple_c_codegen", "test_multiple_results_c", "test_no_results_c", "test_ansi_math1_codegen", "test_ansi_math2_codegen", "test_complicated_codegen", "test_loops_c", "test_dummy_loops_c", "test_partial_loops_c", "test_output_arg_c", "test_output_arg_c_reserved_words", "test_ccode_results_named_ordered", "test_ccode_matrixsymbol_slice", "test_ccode_cse", "test_empty_f_code", "test_empty_f_code_with_header", "test_empty_f_header", "test_simple_f_code", "test_numbersymbol_f_code", "test_erf_f_code", "test_f_code_argument_order", "test_simple_f_header", "test_simple_f_codegen", "test_multiple_results_f", "test_no_results_f", "test_intrinsic_math_codegen", "test_intrinsic_math2_codegen", "test_complicated_codegen_f95", "test_loops", "test_dummy_loops_f95", "test_loops_InOut", "test_partial_loops_f", "test_output_arg_f", "test_inline_function", "test_f_code_call_signature_wrap", "test_check_case", "test_check_case_false_positive", "test_c_fortran_omit_routine_name", "test_fcode_matrix_output", "test_fcode_results_named_ordered", "test_fcode_matrixsymbol_slice", "test_fcode_matrixsymbol_slice_autoname", "test_global_vars", "test_custom_codegen", "test_c_with_printer"]

**Base Commit**: 09786a173e7a0a488f46dd6000177c23e5d24eed
**Environment Setup Commit**: 70381f282f2d9d039da860e391fe51649df2779d
