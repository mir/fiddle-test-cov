# matplotlib__matplotlib-23987

**Repository**: matplotlib/matplotlib
**Created**: 2022-09-22T21:39:02Z
**Version**: 3.6

## Problem Statement

[Bug]: Constrained layout UserWarning even when False
### Bug summary

When using layout settings such as `plt.subplots_adjust` or `bbox_inches='tight`, a UserWarning is produced due to incompatibility with constrained_layout, even if constrained_layout = False. This was not the case in previous versions.

### Code for reproduction

```python
import matplotlib.pyplot as plt
import numpy as np
a = np.linspace(0,2*np.pi,100)
b = np.sin(a)
c = np.cos(a)
fig,ax = plt.subplots(1,2,figsize=(8,2),constrained_layout=False)
ax[0].plot(a,b)
ax[1].plot(a,c)
plt.subplots_adjust(wspace=0)
```


### Actual outcome

The plot works fine but the warning is generated

`/var/folders/ss/pfgdfm2x7_s4cyw2v0b_t7q80000gn/T/ipykernel_76923/4170965423.py:7: UserWarning: This figure was using a layout engine that is incompatible with subplots_adjust and/or tight_layout; not calling subplots_adjust.
  plt.subplots_adjust(wspace=0)`

### Expected outcome

no warning

### Additional information

Warning disappears when constrained_layout=False is removed

### Operating system

OS/X

### Matplotlib Version

3.6.0

### Matplotlib Backend

_No response_

### Python version

_No response_

### Jupyter version

_No response_

### Installation

conda


## Hints

Yup, that is indeed a bug https://github.com/matplotlib/matplotlib/blob/e98d8d085e8f53ec0467422b326f7738a2dd695e/lib/matplotlib/figure.py#L2428-L2431 

PR on the way.
@VanWieren Did you mean to close this?  We normally keep bugs open until the PR to fix it is actually merged.
> @VanWieren Did you mean to close this? We normally keep bugs open until the PR to fix it is actually merged.

oh oops, I did not know that. Will reopen

## Patch

```diff

diff --git a/lib/matplotlib/figure.py b/lib/matplotlib/figure.py
--- a/lib/matplotlib/figure.py
+++ b/lib/matplotlib/figure.py
@@ -2426,9 +2426,12 @@ def __init__(self,
             if isinstance(tight_layout, dict):
                 self.get_layout_engine().set(**tight_layout)
         elif constrained_layout is not None:
-            self.set_layout_engine(layout='constrained')
             if isinstance(constrained_layout, dict):
+                self.set_layout_engine(layout='constrained')
                 self.get_layout_engine().set(**constrained_layout)
+            elif constrained_layout:
+                self.set_layout_engine(layout='constrained')
+
         else:
             # everything is None, so use default:
             self.set_layout_engine(layout=layout)


```

## Test Patch

```diff
diff --git a/lib/matplotlib/tests/test_constrainedlayout.py b/lib/matplotlib/tests/test_constrainedlayout.py
--- a/lib/matplotlib/tests/test_constrainedlayout.py
+++ b/lib/matplotlib/tests/test_constrainedlayout.py
@@ -656,3 +656,14 @@ def test_compressed1():
     pos = axs[1, 2].get_position()
     np.testing.assert_allclose(pos.x1, 0.8618, atol=1e-3)
     np.testing.assert_allclose(pos.y0, 0.1934, atol=1e-3)
+
+
+@pytest.mark.parametrize('arg, state', [
+    (True, True),
+    (False, False),
+    ({}, True),
+    ({'rect': None}, True)
+])
+def test_set_constrained_layout(arg, state):
+    fig, ax = plt.subplots(constrained_layout=arg)
+    assert fig.get_constrained_layout() is state

```

## Test Information

**Tests that should FAIL→PASS**: ["lib/matplotlib/tests/test_constrainedlayout.py::test_set_constrained_layout[False-False]"]

**Tests that should PASS→PASS**: ["lib/matplotlib/tests/test_constrainedlayout.py::test_constrained_layout1[png]", "lib/matplotlib/tests/test_constrainedlayout.py::test_constrained_layout2[png]", "lib/matplotlib/tests/test_constrainedlayout.py::test_constrained_layout3[png]", "lib/matplotlib/tests/test_constrainedlayout.py::test_constrained_layout4[png]", "lib/matplotlib/tests/test_constrainedlayout.py::test_constrained_layout5[png]", "lib/matplotlib/tests/test_constrainedlayout.py::test_constrained_layout6[png]", "lib/matplotlib/tests/test_constrainedlayout.py::test_identical_subgridspec", "lib/matplotlib/tests/test_constrainedlayout.py::test_constrained_layout7", "lib/matplotlib/tests/test_constrainedlayout.py::test_constrained_layout8[png]", "lib/matplotlib/tests/test_constrainedlayout.py::test_constrained_layout9[png]", "lib/matplotlib/tests/test_constrainedlayout.py::test_constrained_layout10[png]", "lib/matplotlib/tests/test_constrainedlayout.py::test_constrained_layout11[png]", "lib/matplotlib/tests/test_constrainedlayout.py::test_constrained_layout11rat[png]", "lib/matplotlib/tests/test_constrainedlayout.py::test_constrained_layout12[png]", "lib/matplotlib/tests/test_constrainedlayout.py::test_constrained_layout13[png]", "lib/matplotlib/tests/test_constrainedlayout.py::test_constrained_layout14[png]", "lib/matplotlib/tests/test_constrainedlayout.py::test_constrained_layout15[png]", "lib/matplotlib/tests/test_constrainedlayout.py::test_constrained_layout16[png]", "lib/matplotlib/tests/test_constrainedlayout.py::test_constrained_layout17[png]", "lib/matplotlib/tests/test_constrainedlayout.py::test_constrained_layout18", "lib/matplotlib/tests/test_constrainedlayout.py::test_constrained_layout19", "lib/matplotlib/tests/test_constrainedlayout.py::test_constrained_layout20", "lib/matplotlib/tests/test_constrainedlayout.py::test_constrained_layout21", "lib/matplotlib/tests/test_constrainedlayout.py::test_constrained_layout22", "lib/matplotlib/tests/test_constrainedlayout.py::test_constrained_layout23", "lib/matplotlib/tests/test_constrainedlayout.py::test_colorbar_location[png]", "lib/matplotlib/tests/test_constrainedlayout.py::test_hidden_axes", "lib/matplotlib/tests/test_constrainedlayout.py::test_colorbar_align", "lib/matplotlib/tests/test_constrainedlayout.py::test_colorbars_no_overlapV[png]", "lib/matplotlib/tests/test_constrainedlayout.py::test_colorbars_no_overlapH[png]", "lib/matplotlib/tests/test_constrainedlayout.py::test_manually_set_position", "lib/matplotlib/tests/test_constrainedlayout.py::test_bboxtight[png]", "lib/matplotlib/tests/test_constrainedlayout.py::test_bbox[png]", "lib/matplotlib/tests/test_constrainedlayout.py::test_align_labels", "lib/matplotlib/tests/test_constrainedlayout.py::test_suplabels", "lib/matplotlib/tests/test_constrainedlayout.py::test_gridspec_addressing", "lib/matplotlib/tests/test_constrainedlayout.py::test_discouraged_api", "lib/matplotlib/tests/test_constrainedlayout.py::test_kwargs", "lib/matplotlib/tests/test_constrainedlayout.py::test_rect", "lib/matplotlib/tests/test_constrainedlayout.py::test_compressed1", "lib/matplotlib/tests/test_constrainedlayout.py::test_set_constrained_layout[True-True]", "lib/matplotlib/tests/test_constrainedlayout.py::test_set_constrained_layout[arg2-True]", "lib/matplotlib/tests/test_constrainedlayout.py::test_set_constrained_layout[arg3-True]"]

**Base Commit**: e98d8d085e8f53ec0467422b326f7738a2dd695e
**Environment Setup Commit**: 73909bcb408886a22e2b84581d6b9e6d9907c813
