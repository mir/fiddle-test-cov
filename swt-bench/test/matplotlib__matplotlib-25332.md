# matplotlib__matplotlib-25332

**Repository**: matplotlib/matplotlib
**Created**: 2023-02-26T11:18:40Z
**Version**: 3.7

## Problem Statement

[Bug]: Unable to pickle figure with aligned labels
### Bug summary

 Unable to pickle figure after calling `align_labels()`

### Code for reproduction

```python
import matplotlib.pyplot as plt
import pickle

fig = plt.figure()
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)
time=[0,1,2,3,4]
speed=[40000,4300,4500,4700,4800]
acc=[10,11,12,13,14]
ax1.plot(time,speed)
ax1.set_ylabel('speed')
ax2.plot(time,acc)
ax2.set_ylabel('acc')

fig.align_labels() ##pickling works after removing this line 

pickle.dumps(fig)
plt.show()
```


### Actual outcome
```
align.py", line 16
pickle.dumps(fig)
TypeError: cannot pickle 'weakref.ReferenceType' object
```
### Expected outcome

Pickling successful

### Additional information

_No response_

### Operating system

Windows

### Matplotlib Version

3.7.0

### Matplotlib Backend

_No response_

### Python version

_No response_

### Jupyter version

_No response_

### Installation

None


## Hints

As you've noted, pickling is pretty fragile.  Do you _need_ to pickle?  

## Patch

```diff

diff --git a/lib/matplotlib/cbook.py b/lib/matplotlib/cbook.py
--- a/lib/matplotlib/cbook.py
+++ b/lib/matplotlib/cbook.py
@@ -788,6 +788,19 @@ class Grouper:
     def __init__(self, init=()):
         self._mapping = {weakref.ref(x): [weakref.ref(x)] for x in init}
 
+    def __getstate__(self):
+        return {
+            **vars(self),
+            # Convert weak refs to strong ones.
+            "_mapping": {k(): [v() for v in vs] for k, vs in self._mapping.items()},
+        }
+
+    def __setstate__(self, state):
+        vars(self).update(state)
+        # Convert strong refs to weak ones.
+        self._mapping = {weakref.ref(k): [*map(weakref.ref, vs)]
+                         for k, vs in self._mapping.items()}
+
     def __contains__(self, item):
         return weakref.ref(item) in self._mapping
 


```

## Test Patch

```diff
diff --git a/lib/matplotlib/tests/test_pickle.py b/lib/matplotlib/tests/test_pickle.py
--- a/lib/matplotlib/tests/test_pickle.py
+++ b/lib/matplotlib/tests/test_pickle.py
@@ -58,6 +58,7 @@ def _generate_complete_test_figure(fig_ref):
     # Ensure lists also pickle correctly.
     plt.subplot(3, 3, 1)
     plt.plot(list(range(10)))
+    plt.ylabel("hello")
 
     plt.subplot(3, 3, 2)
     plt.contourf(data, hatches=['//', 'ooo'])
@@ -68,6 +69,7 @@ def _generate_complete_test_figure(fig_ref):
 
     plt.subplot(3, 3, 4)
     plt.imshow(data)
+    plt.ylabel("hello\nworld!")
 
     plt.subplot(3, 3, 5)
     plt.pcolor(data)
@@ -89,6 +91,8 @@ def _generate_complete_test_figure(fig_ref):
     plt.subplot(3, 3, 9)
     plt.errorbar(x, x * -0.5, xerr=0.2, yerr=0.4)
 
+    fig_ref.align_ylabels()  # Test handling of _align_label_groups Groupers.
+
 
 @mpl.style.context("default")
 @check_figures_equal(extensions=["png"])

```

## Test Information

**Tests that should FAIL→PASS**: ["lib/matplotlib/tests/test_pickle.py::test_complete[png]"]

**Tests that should PASS→PASS**: ["lib/matplotlib/tests/test_pickle.py::test_simple", "lib/matplotlib/tests/test_pickle.py::test_gcf", "lib/matplotlib/tests/test_pickle.py::test_no_pyplot", "lib/matplotlib/tests/test_pickle.py::test_renderer", "lib/matplotlib/tests/test_pickle.py::test_image", "lib/matplotlib/tests/test_pickle.py::test_polar", "lib/matplotlib/tests/test_pickle.py::test_transform", "lib/matplotlib/tests/test_pickle.py::test_rrulewrapper", "lib/matplotlib/tests/test_pickle.py::test_shared", "lib/matplotlib/tests/test_pickle.py::test_inset_and_secondary", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap0]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap1]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap2]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap3]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap4]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap5]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap6]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap7]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap8]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap9]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap10]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap11]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap12]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap13]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap14]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap15]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap16]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap17]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap18]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap19]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap20]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap21]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap22]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap23]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap24]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap25]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap26]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap27]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap28]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap29]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap30]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap31]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap32]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap33]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap34]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap35]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap36]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap37]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap38]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap39]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap40]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap41]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap42]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap43]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap44]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap45]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap46]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap47]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap48]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap49]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap50]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap51]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap52]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap53]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap54]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap55]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap56]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap57]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap58]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap59]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap60]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap61]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap62]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap63]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap64]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap65]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap66]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap67]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap68]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap69]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap70]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap71]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap72]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap73]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap74]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap75]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap76]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap77]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap78]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap79]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap80]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap81]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap82]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap83]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap84]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap85]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap86]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap87]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap88]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap89]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap90]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap91]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap92]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap93]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap94]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap95]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap96]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap97]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap98]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap99]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap100]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap101]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap102]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap103]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap104]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap105]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap106]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap107]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap108]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap109]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap110]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap111]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap112]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap113]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap114]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap115]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap116]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap117]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap118]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap119]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap120]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap121]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap122]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap123]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap124]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap125]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap126]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap127]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap128]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap129]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap130]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap131]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap132]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap133]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap134]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap135]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap136]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap137]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap138]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap139]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap140]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap141]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap142]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap143]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap144]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap145]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap146]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap147]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap148]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap149]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap150]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap151]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap152]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap153]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap154]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap155]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap156]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap157]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap158]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap159]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap160]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap161]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap162]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap163]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap164]", "lib/matplotlib/tests/test_pickle.py::test_cmap[cmap165]", "lib/matplotlib/tests/test_pickle.py::test_unpickle_canvas", "lib/matplotlib/tests/test_pickle.py::test_mpl_toolkits", "lib/matplotlib/tests/test_pickle.py::test_standard_norm", "lib/matplotlib/tests/test_pickle.py::test_dynamic_norm", "lib/matplotlib/tests/test_pickle.py::test_vertexselector"]

**Base Commit**: 66ba515e671638971bd11a34cff12c107a437e0b
**Environment Setup Commit**: 0849036fd992a2dd133a0cffc3f84f58ccf1840f
