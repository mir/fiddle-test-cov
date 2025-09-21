# sympy__sympy-12419

**Repository**: sympy/sympy
**Created**: 2017-03-25T15:02:26Z
**Version**: 1.0

## Problem Statement

Sum of the elements of an identity matrix is zero
I think this is a bug.

I created a matrix by M.T * M under an assumption that M is orthogonal.  SymPy successfully recognized that the result is an identity matrix.  I tested its identity-ness by element-wise, queries, and sum of the diagonal elements and received expected results.

However, when I attempt to evaluate the total sum of the elements the result was 0 while 'n' is expected.

```
from sympy import *
from sympy import Q as Query

n = Symbol('n', integer=True, positive=True)
i, j = symbols('i j', integer=True)
M = MatrixSymbol('M', n, n)

e = None
with assuming(Query.orthogonal(M)):
    e = refine((M.T * M).doit())

# Correct: M.T * M is an identity matrix.
print(e, e[0, 0], e[0, 1], e[1, 0], e[1, 1])

# Correct: The output is True True
print(ask(Query.diagonal(e)), ask(Query.integer_elements(e)))

# Correct: The sum of the diagonal elements is n
print(Sum(e[i, i], (i, 0, n-1)).doit())

# So far so good
# Total sum of the elements is expected to be 'n' but the answer is 0!
print(Sum(Sum(e[i, j], (i, 0, n-1)), (j, 0, n-1)).doit())
```


## Hints

@wakita
shouldn't these be 1
I would like to work on this issue
```
>>> Sum(e[0,i],(i,0,n-1)).doit()
0
>>> Sum(e[i,0],(i,0,n-1)).doit()
0
```
Hey,
I would like to try to solve this issue. Where should I look first?
Interesting observation if I replace j with i in e[i, j] the answer comes as n**2 which is correct.. 
@Vedarth would you give your code here
@SatyaPrakashDwibedi `print(Sum(Sum(e[i, i], (i, 0, n-1)), (j, 0, n-1)).doit())`
Here is something more... 
if i write `print Sum(e[i,i] ,(i ,0 ,n-1) ,(j ,0 ,n-1)).doit()` it gives the same output.
I am not sure where to look to fix the issue ,though, please tell me if you get any leads.
@SatyaPrakashDwibedi Yes, both of the two math expressions that you gave should be 1s.

@Vedarth n**2 is incorrect.  'e' is an identity matrix.  The total sum should be the same as the number of diagonal elements, which is 'n'.
The problem appears to be that while `e[0,0] == e[j,j] == 1`, `e[I,j] == 0` -- it assumes that if the indices are different then you are off-diagonal rather than not evaluating them at all because it is not known if `i == j`. I would start by looking in an `eval` method for this object. Inequality of indices *only for Numbers* should give 0 (while equality of numbers or expressions should give 1).
@smichr I see.  Thank you for your enlightenment.

I wonder if this situation be similar to `KroneckerDelta(i, j)`.

```
i, j = symbols('i j', integer=True)
n = Symbol('n', integer=True, positive=True)
Sum(Sum(KroneckerDelta(i, j), (i, 0, n-1)), (j, 0, n-1)).doit()
```
gives the following answer:

`Sum(Piecewise((1, And(0 <= j, j <= n - 1)), (0, True)), (j, 0, n - 1))`

If SymPy can reduce this formula to `n`, I suppose reduction of `e[i, j]` to a KroneckerDelta is a candidate solution.
@smichr I would like to work on this issue.
Where should I start looking
and have a look 
```
>>> Sum(e[k, 0], (i, 0, n-1))
Sum(0, (i, 0, n - 1))
```
why??
@smichr You are right. It is ignoring i==j case. What do you mean by eval method? Please elaborate a little bit on how do you want it done. I am trying to solve it.
@wakita I think you already know it by now but I am just clarifying anyways, e[i,i] in my code will be evaluated as sum of diagonals n times which gives `n*n` or `n**2.` So it is evaluating it correctly.
@SatyaPrakashDwibedi I have already started working on this issue. If you find anything useful please do inform me. It would be a great help. More the merrier :)
@SatyaPrakashDwibedi The thing is it is somehow omitting the case where (in e[firstelement, secondelement]) the first element == second element. That is why even though when we write [k,0] it is giving 0. I have tried several other combinations and this result is consistent.
How ever if we write `print(Sum(Sum(e[0, 0], (i, 0, n-1)), (j, 0, n-1)).doit())` output is `n**2` as it is evaluating adding e[0,0] `n*n` times.

> I wonder if this situation be similar to KroneckerDelta(i, j)

Exactly. Notice how the KD is evaluated as a `Piecewise` since we don't know whether `i==j` until actual values are substituted.

BTW, you don't have to write two `Sum`s; you can have a nested range:

```
>>> Sum(i*j,(i,1,3),(j,1,3)).doit()  # instead of Sum(Sum(i*j, (i,1,3)), (j,1,3)).doit()
36
>>> sum([i*j for i in range(1,4) for j in range(1,4)])
36
```
OK, it's the `_entry` method of the `Identity` that is the culprit:

```
    def _entry(self, i, j):
        if i == j:
            return S.One
        else:
            return S.Zero
```

This should just return `KroneckerDelta(i, j)`. When it does then

```
>>> print(Sum(Sum(e[i, j], (i, 0, n-1)), (j, 0, n-1)).doit())
Sum(Piecewise((1, (0 <= j) & (j <= n - 1)), (0, True)), (j, 0, n - 1))
>>> t=_
>>> t.subs(n,3)
3
>>> t.subs(n,30)
30
```

breadcrumb: tracing is a great way to find where such problems are located. I started a trace with the expression `e[1,2]` and followed the trace until I saw where the 0 was being returned: in the `_entry` method.
@smichr I guess,it is fixed then.Nothing else to be done?
```
>>> Sum(KroneckerDelta(i, j), (i, 0, n-1), (j, 0, n-1)).doit()
Sum(Piecewise((1, j <= n - 1), (0, True)), (j, 0, n - 1))
```

I think, given that (j, 0, n-1), we can safely say that `j <= n - 1` always holds.  Under this condition, the Piecewise form can be reduced to `1` and we can have `n` for the symbolic result.  Or am I demanding too much?
@smichr so we need to return KroneckerDelta(i,j) instead of S.one and S.zero? Is that what you mean?
> so we need to return KroneckerDelta(i,j) instead of S.one and S.zero

Although that would work, it's probably overkill. How about returning:

```
eq = Eq(i, j)
if eq == True:
    return S.One
elif eq == False:
    return S.Zero
return Piecewise((1, eq), (0, True)) # this line alone is sufficient; maybe it's better to avoid Piecewise
```
@smichr I made one PR [here](https://github.com/sympy/sympy/pull/12316),I added Kronecker delta,it passes the tests, could you please review it.
@smichr  First of all I am so sorry for extremely late response. Secondly, I don't think def _entry is the culprit. _entry's job is to tell if e[i,j] is 0 or 1 depending on the values and i think it is doing it's job just fine. But the problem is that when we write e[i,j] it automatically assumes i and j are different and ignores the cases where they are ,in fact, same. I tried 

> '''eq = Eq(i, j)
if eq == True:
    return S.One
elif eq == False:
    return S.Zero
return Piecewise((1, eq), (0, True)) # this line alone is sufficient; maybe it's better to avoid Piecewise'''

But it did not work. Answer is still coming as 0.
Also i fiddled around a bit and noticed some thing interesting
```
for i in range(0,5):
    for j in range(0,5):
        print e[i,j] # e is identity matrix.
```
this gives the correct output. All the ones and zeroes are there. Also,
```
x=0
for i in range(0,5):
    for j in range(0,5):
        x=x+e[i,j]
print x
```
And again it is giving a correct answer. So i think it is a problem somewhere else may be an eval error.
I don't know how to solve it please explain how to do it. Please correct me if I am mistaken.
> fiddled around a bit and noticed some thing interesting

That's because you are using literal values for `i` and `j`: `Eq(i,j)` when `i=1`, `j=2` gives `S.false`.

The modifications that I suggested work only if you don't nest the Sums; I'm not sure why the Sums don't denest when Piecewise is involved but (as @wakita demonstrated) it *is* smart enough when using KroneckerDelta to denest, but it doesn't evaluate until a concrete value is substituted.

```
>>> from sympy import Q as Query
>>>
>>> n = Symbol('n', integer=True, positive=True)
>>> i, j = symbols('i j', integer=True)
>>> M = MatrixSymbol('M', n, n)
>>>
>>> e = None
>>> with assuming(Query.orthogonal(M)):
...     e = refine((M.T * M).doit())
...
>>> g = Sum(e[i, j], (i, 0, n-1), (j, 0, n-1))
>>> g.subs(n,3)
Sum(Piecewise((1, Eq(i, j)), (0, True)), (i, 0, 2), (j, 0, 2))
>>> _.doit()
3

# the double sum form doesn't work

>>> Sum(Sum(e[i, j], (i, 0, n-1)), (j, 0, n-1))
Sum(Piecewise((Sum(1, (i, 0, n - 1)), Eq(i, j)), (Sum(0, (i, 0, n - 1)), True)), (j, 0, n - 1))
>>> _.subs(n,3)
Sum(Piecewise((Sum(1, (i, 0, 2)), Eq(i, j)), (Sum(0, (i, 0, 2)), True)), (j, 0, 2))
>>> _.doit()
Piecewise((3, Eq(i, 0)), (0, True)) + Piecewise((3, Eq(i, 1)), (0, True)) + Piecewise((3, Eq(i, 2)), (0, True))

# the KroneckerDelta form denests but doesn't evaluate until you substitute a concrete value

>>> Sum(Sum(KroneckerDelta(i,j), (i, 0, n-1)), (j, 0, n-1))
Sum(KroneckerDelta(i, j), (i, 0, n - 1), (j, 0, n - 1))
>>> _.doit()
Sum(Piecewise((1, (0 <= j) & (j <= n - 1)), (0, True)), (j, 0, n - 1))
>>> _.subs(n,3)
Sum(Piecewise((1, (0 <= j) & (j <= 2)), (0, True)), (j, 0, 2))
>>> _.doit()
3
```

Because of the better behavior of KroneckerDelta, perhaps the `_entry` should be written in terms of that instead of Piecewise.

## Patch

```diff

diff --git a/sympy/matrices/expressions/matexpr.py b/sympy/matrices/expressions/matexpr.py
--- a/sympy/matrices/expressions/matexpr.py
+++ b/sympy/matrices/expressions/matexpr.py
@@ -2,11 +2,12 @@
 
 from functools import wraps
 
-from sympy.core import S, Symbol, Tuple, Integer, Basic, Expr
+from sympy.core import S, Symbol, Tuple, Integer, Basic, Expr, Eq
 from sympy.core.decorators import call_highest_priority
 from sympy.core.compatibility import range
 from sympy.core.sympify import SympifyError, sympify
 from sympy.functions import conjugate, adjoint
+from sympy.functions.special.tensor_functions import KroneckerDelta
 from sympy.matrices import ShapeError
 from sympy.simplify import simplify
 
@@ -375,7 +376,6 @@ def _eval_derivative(self, v):
         if self.args[0] != v.args[0]:
             return S.Zero
 
-        from sympy import KroneckerDelta
         return KroneckerDelta(self.args[1], v.args[1])*KroneckerDelta(self.args[2], v.args[2])
 
 
@@ -476,10 +476,12 @@ def conjugate(self):
         return self
 
     def _entry(self, i, j):
-        if i == j:
+        eq = Eq(i, j)
+        if eq is S.true:
             return S.One
-        else:
+        elif eq is S.false:
             return S.Zero
+        return KroneckerDelta(i, j)
 
     def _eval_determinant(self):
         return S.One


```

## Test Patch

```diff
diff --git a/sympy/matrices/expressions/tests/test_matexpr.py b/sympy/matrices/expressions/tests/test_matexpr.py
--- a/sympy/matrices/expressions/tests/test_matexpr.py
+++ b/sympy/matrices/expressions/tests/test_matexpr.py
@@ -65,6 +65,7 @@ def test_ZeroMatrix():
     with raises(ShapeError):
         Z**2
 
+
 def test_ZeroMatrix_doit():
     Znn = ZeroMatrix(Add(n, n, evaluate=False), n)
     assert isinstance(Znn.rows, Add)
@@ -74,6 +75,8 @@ def test_ZeroMatrix_doit():
 
 def test_Identity():
     A = MatrixSymbol('A', n, m)
+    i, j = symbols('i j')
+
     In = Identity(n)
     Im = Identity(m)
 
@@ -84,6 +87,11 @@ def test_Identity():
     assert In.inverse() == In
     assert In.conjugate() == In
 
+    assert In[i, j] != 0
+    assert Sum(In[i, j], (i, 0, n-1), (j, 0, n-1)).subs(n,3).doit() == 3
+    assert Sum(Sum(In[i, j], (i, 0, n-1)), (j, 0, n-1)).subs(n,3).doit() == 3
+
+
 def test_Identity_doit():
     Inn = Identity(Add(n, n, evaluate=False))
     assert isinstance(Inn.rows, Add)

```

## Test Information

**Tests that should FAIL→PASS**: ["test_Identity"]

**Tests that should PASS→PASS**: ["test_shape", "test_matexpr", "test_subs", "test_ZeroMatrix", "test_ZeroMatrix_doit", "test_Identity_doit", "test_addition", "test_multiplication", "test_MatPow", "test_MatrixSymbol", "test_dense_conversion", "test_free_symbols", "test_zero_matmul", "test_matadd_simplify", "test_matmul_simplify", "test_invariants", "test_indexing", "test_single_indexing", "test_MatrixElement_commutative", "test_MatrixSymbol_determinant", "test_MatrixElement_diff", "test_MatrixElement_doit", "test_identity_powers", "test_Zero_power", "test_matrixelement_diff"]

**Base Commit**: 479939f8c65c8c2908bbedc959549a257a7c0b0b
**Environment Setup Commit**: 50b81f9f6be151014501ffac44e5dc6b2416938f
