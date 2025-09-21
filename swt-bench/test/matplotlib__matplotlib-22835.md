# matplotlib__matplotlib-22835

**Repository**: matplotlib/matplotlib
**Created**: 2022-04-12T23:13:58Z
**Version**: 3.5

## Problem Statement

[Bug]: scalar mappable format_cursor_data crashes on BoundarNorm
### Bug summary

In 3.5.0 if you do:

```python
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl

fig, ax = plt.subplots()
norm = mpl.colors.BoundaryNorm(np.linspace(-4, 4, 5), 256)
X = np.random.randn(10, 10)
pc = ax.imshow(X, cmap='RdBu_r', norm=norm)
```

and mouse over the image, it crashes with

```
File "/Users/jklymak/matplotlib/lib/matplotlib/artist.py", line 1282, in format_cursor_data
    neighbors = self.norm.inverse(
  File "/Users/jklymak/matplotlib/lib/matplotlib/colors.py", line 1829, in inverse
    raise ValueError("BoundaryNorm is not invertible")
ValueError: BoundaryNorm is not invertible
```

and interaction stops.  

Not sure if we should have a special check here, a try-except, or actually just make BoundaryNorm approximately invertible.  


### Matplotlib Version

main 3.5.0


[Bug]: scalar mappable format_cursor_data crashes on BoundarNorm
### Bug summary

In 3.5.0 if you do:

```python
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl

fig, ax = plt.subplots()
norm = mpl.colors.BoundaryNorm(np.linspace(-4, 4, 5), 256)
X = np.random.randn(10, 10)
pc = ax.imshow(X, cmap='RdBu_r', norm=norm)
```

and mouse over the image, it crashes with

```
File "/Users/jklymak/matplotlib/lib/matplotlib/artist.py", line 1282, in format_cursor_data
    neighbors = self.norm.inverse(
  File "/Users/jklymak/matplotlib/lib/matplotlib/colors.py", line 1829, in inverse
    raise ValueError("BoundaryNorm is not invertible")
ValueError: BoundaryNorm is not invertible
```

and interaction stops.  

Not sure if we should have a special check here, a try-except, or actually just make BoundaryNorm approximately invertible.  


### Matplotlib Version

main 3.5.0




## Hints

I think the correct fix is to specifically check for BoundaryNorm there and implement special logic to determine the positions of the neighboring intervals (on the BoundaryNorm) for that case.
I tried returning the passed in `value` instead of the exception at https://github.com/matplotlib/matplotlib/blob/b2bb7be4ba343fcec6b1dbbffd7106e6af240221/lib/matplotlib/colors.py#L1829

```python
return value
```
and it seems to work. At least the error is gone and the values displayed in the plot (bottom right) when hovering with the mouse seem also right. But the numbers are rounded to only 1 digit in sci notation. So 19, 20 or 21 become 2.e+01.
Hope this helps.

Maybe a more constructive suggestion for a change in https://github.com/matplotlib/matplotlib/blob/b2bb7be4ba343fcec6b1dbbffd7106e6af240221/lib/matplotlib/artist.py#L1280 that tries to fix the error:
```python
ends = self.norm(np.array([self.norm.vmin, self.norm.vmax]))
if np.isfinite(normed) and np.allclose(ends, 0.5, rtol=0.0, atol=0.5):
```
This way, because `BoundaryNorm` doesn't map to 0...1 range but to the indices of the colors, the call to `BoundaryNorm.inverse()` is skipped and the default value for `g_sig_digits=3` is used.
But I'm not sure if there can be a case where `BoundaryNorm` actually maps its endpoints to 0...1, in which case all breaks down.
hey, I just ran into this while plotting data... (interactivity doesn't stop but it plots a lot of issues)  any updates?
@raphaelquast no, this still needs someone to work on it.

Labeled as a good first issue as there in no API design here (just returning an empty string is better than the current state).
I can give a PR, that is based on my [last comment](https://github.com/matplotlib/matplotlib/issues/21915#issuecomment-992454625) a try. But my concerns/questions from then are still valid.
As this is all internal code, I think we should just do an `isinstance(norm, BoundaryNorm)` check and then act accordingly.  There is already a bunch of instances of this in the colorbar code as precedence. 
After thinking about my suggestion again, I now understand why you prefer an `isinstace` check.
(In my initial suggestion one would have to check if `ends` maps to (0,1) and if `normed` is in [0, 1] for the correct way to implement my idea. But these conditions are taylored to catch `BoundaryNorm` anyway, so why not do it directly.)

However, I suggest using a try block after https://github.com/matplotlib/matplotlib/blob/c33557d120eefe3148ebfcf2e758ff2357966000/lib/matplotlib/artist.py#L1305
```python
# Midpoints of neighboring color intervals.
try:
    neighbors = self.norm.inverse(
        (int(normed * n) + np.array([0, 1])) / n)
except ValueError:
    # non-invertible ScalarMappable
```
because `BoundaryNorm` raises a `ValueError` anyway and I assume this to be the case for all non-invertible `ScalarMappables`.
(And the issue is the exception raised from `inverse`).

The question is:
What to put in the `except`? So what is "acting accordingly" in this case?
If `BoundaryNorm` isn't invertible, how can we reliably get the data values of the midpoints of neighboring colors?

I think it should be enough to get the boundaries themselves, instead of the midpoints (though both is possible) with something like:
```python
cur_idx = np.argmin(np.abs(self.norm.boundaries - data))
cur_bound = self.norm.boundaries[cur_idx]
neigh_idx = cur_idx + 1 if data > cur_bound else cur_idx - 1
neighbors = self.norm.boundaries[
    np.array([cur_idx, neigh_idx])
]
```
Problems with this code are:
- `boundaries` property is specific to `BoundaryNorm`, isn't it? So we gained nothing by using `try .. except`
- more checks are needed to cover all cases for `clip` and `extend` options of `BoundaryNorm` such that `neigh_idx` is always in bounds
- for very coarse boundaries compared to data (ie: `boundaries = [0,1,2,3,4,5]; data = random(n)*5) the displayed values are always rounded to one significant digit. While in principle, this is expected (I believe), it results in inconsistency. In my example 0.111111 would be given as 0.1 and 0.001 as 0.001 and 1.234 would be just 1.
> boundaries property is specific to BoundaryNorm, isn't it? So we gained nothing by using try .. except

This is one argument in favor of doing the `isinstance` check because then you can assert we _have_ a BoundaryNorm and can trust that you can access its state etc.   One on hand, duck typeing is in general a Good Thing in Python and we should err on the side of being forgiving on input, but sometimes the complexity of it is more trouble than it is worth if you really only have 1 case that you are trying catch!  

>  I assume this to be the case for all non-invertible ScalarMappables.

However we only (at this point) are talking about a way to recover in the case of BoundaryNorm.  Let everything else continue to fail and we will deal with those issues if/when they get reported.
I think the correct fix is to specifically check for BoundaryNorm there and implement special logic to determine the positions of the neighboring intervals (on the BoundaryNorm) for that case.
I tried returning the passed in `value` instead of the exception at https://github.com/matplotlib/matplotlib/blob/b2bb7be4ba343fcec6b1dbbffd7106e6af240221/lib/matplotlib/colors.py#L1829

```python
return value
```
and it seems to work. At least the error is gone and the values displayed in the plot (bottom right) when hovering with the mouse seem also right. But the numbers are rounded to only 1 digit in sci notation. So 19, 20 or 21 become 2.e+01.
Hope this helps.

Maybe a more constructive suggestion for a change in https://github.com/matplotlib/matplotlib/blob/b2bb7be4ba343fcec6b1dbbffd7106e6af240221/lib/matplotlib/artist.py#L1280 that tries to fix the error:
```python
ends = self.norm(np.array([self.norm.vmin, self.norm.vmax]))
if np.isfinite(normed) and np.allclose(ends, 0.5, rtol=0.0, atol=0.5):
```
This way, because `BoundaryNorm` doesn't map to 0...1 range but to the indices of the colors, the call to `BoundaryNorm.inverse()` is skipped and the default value for `g_sig_digits=3` is used.
But I'm not sure if there can be a case where `BoundaryNorm` actually maps its endpoints to 0...1, in which case all breaks down.
hey, I just ran into this while plotting data... (interactivity doesn't stop but it plots a lot of issues)  any updates?
@raphaelquast no, this still needs someone to work on it.

Labeled as a good first issue as there in no API design here (just returning an empty string is better than the current state).
I can give a PR, that is based on my [last comment](https://github.com/matplotlib/matplotlib/issues/21915#issuecomment-992454625) a try. But my concerns/questions from then are still valid.
As this is all internal code, I think we should just do an `isinstance(norm, BoundaryNorm)` check and then act accordingly.  There is already a bunch of instances of this in the colorbar code as precedence. 
After thinking about my suggestion again, I now understand why you prefer an `isinstace` check.
(In my initial suggestion one would have to check if `ends` maps to (0,1) and if `normed` is in [0, 1] for the correct way to implement my idea. But these conditions are taylored to catch `BoundaryNorm` anyway, so why not do it directly.)

However, I suggest using a try block after https://github.com/matplotlib/matplotlib/blob/c33557d120eefe3148ebfcf2e758ff2357966000/lib/matplotlib/artist.py#L1305
```python
# Midpoints of neighboring color intervals.
try:
    neighbors = self.norm.inverse(
        (int(normed * n) + np.array([0, 1])) / n)
except ValueError:
    # non-invertible ScalarMappable
```
because `BoundaryNorm` raises a `ValueError` anyway and I assume this to be the case for all non-invertible `ScalarMappables`.
(And the issue is the exception raised from `inverse`).

The question is:
What to put in the `except`? So what is "acting accordingly" in this case?
If `BoundaryNorm` isn't invertible, how can we reliably get the data values of the midpoints of neighboring colors?

I think it should be enough to get the boundaries themselves, instead of the midpoints (though both is possible) with something like:
```python
cur_idx = np.argmin(np.abs(self.norm.boundaries - data))
cur_bound = self.norm.boundaries[cur_idx]
neigh_idx = cur_idx + 1 if data > cur_bound else cur_idx - 1
neighbors = self.norm.boundaries[
    np.array([cur_idx, neigh_idx])
]
```
Problems with this code are:
- `boundaries` property is specific to `BoundaryNorm`, isn't it? So we gained nothing by using `try .. except`
- more checks are needed to cover all cases for `clip` and `extend` options of `BoundaryNorm` such that `neigh_idx` is always in bounds
- for very coarse boundaries compared to data (ie: `boundaries = [0,1,2,3,4,5]; data = random(n)*5) the displayed values are always rounded to one significant digit. While in principle, this is expected (I believe), it results in inconsistency. In my example 0.111111 would be given as 0.1 and 0.001 as 0.001 and 1.234 would be just 1.
> boundaries property is specific to BoundaryNorm, isn't it? So we gained nothing by using try .. except

This is one argument in favor of doing the `isinstance` check because then you can assert we _have_ a BoundaryNorm and can trust that you can access its state etc.   One on hand, duck typeing is in general a Good Thing in Python and we should err on the side of being forgiving on input, but sometimes the complexity of it is more trouble than it is worth if you really only have 1 case that you are trying catch!  

>  I assume this to be the case for all non-invertible ScalarMappables.

However we only (at this point) are talking about a way to recover in the case of BoundaryNorm.  Let everything else continue to fail and we will deal with those issues if/when they get reported.

## Patch

```diff

diff --git a/lib/matplotlib/artist.py b/lib/matplotlib/artist.py
--- a/lib/matplotlib/artist.py
+++ b/lib/matplotlib/artist.py
@@ -12,6 +12,7 @@
 
 import matplotlib as mpl
 from . import _api, cbook
+from .colors import BoundaryNorm
 from .cm import ScalarMappable
 from .path import Path
 from .transforms import (Bbox, IdentityTransform, Transform, TransformedBbox,
@@ -1303,10 +1304,20 @@ def format_cursor_data(self, data):
                 return "[]"
             normed = self.norm(data)
             if np.isfinite(normed):
-                # Midpoints of neighboring color intervals.
-                neighbors = self.norm.inverse(
-                    (int(self.norm(data) * n) + np.array([0, 1])) / n)
-                delta = abs(neighbors - data).max()
+                if isinstance(self.norm, BoundaryNorm):
+                    # not an invertible normalization mapping
+                    cur_idx = np.argmin(np.abs(self.norm.boundaries - data))
+                    neigh_idx = max(0, cur_idx - 1)
+                    # use max diff to prevent delta == 0
+                    delta = np.diff(
+                        self.norm.boundaries[neigh_idx:cur_idx + 2]
+                    ).max()
+
+                else:
+                    # Midpoints of neighboring color intervals.
+                    neighbors = self.norm.inverse(
+                        (int(normed * n) + np.array([0, 1])) / n)
+                    delta = abs(neighbors - data).max()
                 g_sig_digits = cbook._g_sig_digits(data, delta)
             else:
                 g_sig_digits = 3  # Consistent with default below.


```

## Test Patch

```diff
diff --git a/lib/matplotlib/tests/test_artist.py b/lib/matplotlib/tests/test_artist.py
--- a/lib/matplotlib/tests/test_artist.py
+++ b/lib/matplotlib/tests/test_artist.py
@@ -5,6 +5,8 @@
 
 import pytest
 
+from matplotlib import cm
+import matplotlib.colors as mcolors
 import matplotlib.pyplot as plt
 import matplotlib.patches as mpatches
 import matplotlib.lines as mlines
@@ -372,3 +374,164 @@ class MyArtist4(MyArtist3):
         pass
 
     assert MyArtist4.set is MyArtist3.set
+
+
+def test_format_cursor_data_BoundaryNorm():
+    """Test if cursor data is correct when using BoundaryNorm."""
+    X = np.empty((3, 3))
+    X[0, 0] = 0.9
+    X[0, 1] = 0.99
+    X[0, 2] = 0.999
+    X[1, 0] = -1
+    X[1, 1] = 0
+    X[1, 2] = 1
+    X[2, 0] = 0.09
+    X[2, 1] = 0.009
+    X[2, 2] = 0.0009
+
+    # map range -1..1 to 0..256 in 0.1 steps
+    fig, ax = plt.subplots()
+    fig.suptitle("-1..1 to 0..256 in 0.1")
+    norm = mcolors.BoundaryNorm(np.linspace(-1, 1, 20), 256)
+    img = ax.imshow(X, cmap='RdBu_r', norm=norm)
+
+    labels_list = [
+        "[0.9]",
+        "[1.]",
+        "[1.]",
+        "[-1.0]",
+        "[0.0]",
+        "[1.0]",
+        "[0.09]",
+        "[0.009]",
+        "[0.0009]",
+    ]
+    for v, label in zip(X.flat, labels_list):
+        # label = "[{:-#.{}g}]".format(v, cbook._g_sig_digits(v, 0.1))
+        assert img.format_cursor_data(v) == label
+
+    plt.close()
+
+    # map range -1..1 to 0..256 in 0.01 steps
+    fig, ax = plt.subplots()
+    fig.suptitle("-1..1 to 0..256 in 0.01")
+    cmap = cm.get_cmap('RdBu_r', 200)
+    norm = mcolors.BoundaryNorm(np.linspace(-1, 1, 200), 200)
+    img = ax.imshow(X, cmap=cmap, norm=norm)
+
+    labels_list = [
+        "[0.90]",
+        "[0.99]",
+        "[1.0]",
+        "[-1.00]",
+        "[0.00]",
+        "[1.00]",
+        "[0.09]",
+        "[0.009]",
+        "[0.0009]",
+    ]
+    for v, label in zip(X.flat, labels_list):
+        # label = "[{:-#.{}g}]".format(v, cbook._g_sig_digits(v, 0.01))
+        assert img.format_cursor_data(v) == label
+
+    plt.close()
+
+    # map range -1..1 to 0..256 in 0.01 steps
+    fig, ax = plt.subplots()
+    fig.suptitle("-1..1 to 0..256 in 0.001")
+    cmap = cm.get_cmap('RdBu_r', 2000)
+    norm = mcolors.BoundaryNorm(np.linspace(-1, 1, 2000), 2000)
+    img = ax.imshow(X, cmap=cmap, norm=norm)
+
+    labels_list = [
+        "[0.900]",
+        "[0.990]",
+        "[0.999]",
+        "[-1.000]",
+        "[0.000]",
+        "[1.000]",
+        "[0.090]",
+        "[0.009]",
+        "[0.0009]",
+    ]
+    for v, label in zip(X.flat, labels_list):
+        # label = "[{:-#.{}g}]".format(v, cbook._g_sig_digits(v, 0.001))
+        assert img.format_cursor_data(v) == label
+
+    plt.close()
+
+    # different testing data set with
+    # out of bounds values for 0..1 range
+    X = np.empty((7, 1))
+    X[0] = -1.0
+    X[1] = 0.0
+    X[2] = 0.1
+    X[3] = 0.5
+    X[4] = 0.9
+    X[5] = 1.0
+    X[6] = 2.0
+
+    labels_list = [
+        "[-1.0]",
+        "[0.0]",
+        "[0.1]",
+        "[0.5]",
+        "[0.9]",
+        "[1.0]",
+        "[2.0]",
+    ]
+
+    fig, ax = plt.subplots()
+    fig.suptitle("noclip, neither")
+    norm = mcolors.BoundaryNorm(
+        np.linspace(0, 1, 4, endpoint=True), 256, clip=False, extend='neither')
+    img = ax.imshow(X, cmap='RdBu_r', norm=norm)
+    for v, label in zip(X.flat, labels_list):
+        # label = "[{:-#.{}g}]".format(v, cbook._g_sig_digits(v, 0.33))
+        assert img.format_cursor_data(v) == label
+
+    plt.close()
+
+    fig, ax = plt.subplots()
+    fig.suptitle("noclip, min")
+    norm = mcolors.BoundaryNorm(
+        np.linspace(0, 1, 4, endpoint=True), 256, clip=False, extend='min')
+    img = ax.imshow(X, cmap='RdBu_r', norm=norm)
+    for v, label in zip(X.flat, labels_list):
+        # label = "[{:-#.{}g}]".format(v, cbook._g_sig_digits(v, 0.33))
+        assert img.format_cursor_data(v) == label
+
+    plt.close()
+
+    fig, ax = plt.subplots()
+    fig.suptitle("noclip, max")
+    norm = mcolors.BoundaryNorm(
+        np.linspace(0, 1, 4, endpoint=True), 256, clip=False, extend='max')
+    img = ax.imshow(X, cmap='RdBu_r', norm=norm)
+    for v, label in zip(X.flat, labels_list):
+        # label = "[{:-#.{}g}]".format(v, cbook._g_sig_digits(v, 0.33))
+        assert img.format_cursor_data(v) == label
+
+    plt.close()
+
+    fig, ax = plt.subplots()
+    fig.suptitle("noclip, both")
+    norm = mcolors.BoundaryNorm(
+        np.linspace(0, 1, 4, endpoint=True), 256, clip=False, extend='both')
+    img = ax.imshow(X, cmap='RdBu_r', norm=norm)
+    for v, label in zip(X.flat, labels_list):
+        # label = "[{:-#.{}g}]".format(v, cbook._g_sig_digits(v, 0.33))
+        assert img.format_cursor_data(v) == label
+
+    plt.close()
+
+    fig, ax = plt.subplots()
+    fig.suptitle("clip, neither")
+    norm = mcolors.BoundaryNorm(
+        np.linspace(0, 1, 4, endpoint=True), 256, clip=True, extend='neither')
+    img = ax.imshow(X, cmap='RdBu_r', norm=norm)
+    for v, label in zip(X.flat, labels_list):
+        # label = "[{:-#.{}g}]".format(v, cbook._g_sig_digits(v, 0.33))
+        assert img.format_cursor_data(v) == label
+
+    plt.close()

```

## Test Information

**Tests that should FAIL→PASS**: ["lib/matplotlib/tests/test_artist.py::test_format_cursor_data_BoundaryNorm"]

**Tests that should PASS→PASS**: ["lib/matplotlib/tests/test_artist.py::test_patch_transform_of_none", "lib/matplotlib/tests/test_artist.py::test_collection_transform_of_none", "lib/matplotlib/tests/test_artist.py::test_clipping[png]", "lib/matplotlib/tests/test_artist.py::test_clipping[pdf]", "lib/matplotlib/tests/test_artist.py::test_clipping_zoom[png]", "lib/matplotlib/tests/test_artist.py::test_cull_markers", "lib/matplotlib/tests/test_artist.py::test_hatching[png]", "lib/matplotlib/tests/test_artist.py::test_hatching[pdf]", "lib/matplotlib/tests/test_artist.py::test_remove", "lib/matplotlib/tests/test_artist.py::test_default_edges[png]", "lib/matplotlib/tests/test_artist.py::test_properties", "lib/matplotlib/tests/test_artist.py::test_setp", "lib/matplotlib/tests/test_artist.py::test_None_zorder", "lib/matplotlib/tests/test_artist.py::test_artist_inspector_get_valid_values[-unknown]", "lib/matplotlib/tests/test_artist.py::test_artist_inspector_get_valid_values[ACCEPTS:", "lib/matplotlib/tests/test_artist.py::test_artist_inspector_get_valid_values[..", "lib/matplotlib/tests/test_artist.py::test_artist_inspector_get_valid_values[arg", "lib/matplotlib/tests/test_artist.py::test_artist_inspector_get_valid_values[*arg", "lib/matplotlib/tests/test_artist.py::test_artist_inspector_get_aliases", "lib/matplotlib/tests/test_artist.py::test_set_alpha", "lib/matplotlib/tests/test_artist.py::test_set_alpha_for_array", "lib/matplotlib/tests/test_artist.py::test_callbacks", "lib/matplotlib/tests/test_artist.py::test_set_signature", "lib/matplotlib/tests/test_artist.py::test_set_is_overwritten"]

**Base Commit**: c33557d120eefe3148ebfcf2e758ff2357966000
**Environment Setup Commit**: de98877e3dc45de8dd441d008f23d88738dc015d
