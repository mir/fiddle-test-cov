# matplotlib__matplotlib-25498

**Repository**: matplotlib/matplotlib
**Created**: 2023-03-18T17:01:11Z
**Version**: 3.7

## Problem Statement

Update colorbar after changing mappable.norm
How can I update a colorbar, after I changed the norm instance of the colorbar?

`colorbar.update_normal(mappable)` has now effect and `colorbar.update_bruteforce(mappable)` throws a `ZeroDivsionError`-Exception.

Consider this example:

``` python
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np

img = 10**np.random.normal(1, 1, size=(50, 50))

fig, ax = plt.subplots(1, 1)
plot = ax.imshow(img, cmap='gray')
cb = fig.colorbar(plot, ax=ax)
plot.norm = LogNorm()
cb.update_normal(plot)  # no effect
cb.update_bruteforce(plot)  # throws ZeroDivisionError
plt.show()
```

Output for `cb.update_bruteforce(plot)`:

```
Traceback (most recent call last):
  File "test_norm.py", line 12, in <module>
    cb.update_bruteforce(plot)
  File "/home/maxnoe/.local/anaconda3/lib/python3.4/site-packages/matplotlib/colorbar.py", line 967, in update_bruteforce
    self.draw_all()
  File "/home/maxnoe/.local/anaconda3/lib/python3.4/site-packages/matplotlib/colorbar.py", line 342, in draw_all
    self._process_values()
  File "/home/maxnoe/.local/anaconda3/lib/python3.4/site-packages/matplotlib/colorbar.py", line 664, in _process_values
    b = self.norm.inverse(self._uniform_y(self.cmap.N + 1))
  File "/home/maxnoe/.local/anaconda3/lib/python3.4/site-packages/matplotlib/colors.py", line 1011, in inverse
    return vmin * ma.power((vmax / vmin), val)
ZeroDivisionError: division by zero
```



## Hints

You have run into a big bug in imshow, not colorbar.  As a workaround, after setting `plot.norm`, call `plot.autoscale()`.  Then the `update_bruteforce` will work.
When the norm is changed, it should pick up the vmax, vmin values from the autoscaling; but this is not happening.  Actually, it's worse than that; it fails even if the norm is set as a kwarg in the call to imshow. I haven't looked beyond that to see why.  I've confirmed the problem with master.

In ipython using `%matplotlib` setting the norm the first time works, changing it back later to
`Normalize()` or something other blows up:

```
--> 199         self.pixels.autoscale()
    200         self.update(force=True)
    201 

/home/maxnoe/.local/anaconda3/envs/ctapipe/lib/python3.5/site-packages/matplotlib/cm.py in autoscale(self)
    323             raise TypeError('You must first set_array for mappable')
    324         self.norm.autoscale(self._A)
--> 325         self.changed()
    326 
    327     def autoscale_None(self):

/home/maxnoe/.local/anaconda3/envs/ctapipe/lib/python3.5/site-packages/matplotlib/cm.py in changed(self)
    357         callbackSM listeners to the 'changed' signal
    358         """
--> 359         self.callbacksSM.process('changed', self)
    360 
    361         for key in self.update_dict:

/home/maxnoe/.local/anaconda3/envs/ctapipe/lib/python3.5/site-packages/matplotlib/cbook.py in process(self, s, *args, **kwargs)
    560             for cid, proxy in list(six.iteritems(self.callbacks[s])):
    561                 try:
--> 562                     proxy(*args, **kwargs)
    563                 except ReferenceError:
    564                     self._remove_proxy(proxy)

/home/maxnoe/.local/anaconda3/envs/ctapipe/lib/python3.5/site-packages/matplotlib/cbook.py in __call__(self, *args, **kwargs)
    427             mtd = self.func
    428         # invoke the callable and return the result
--> 429         return mtd(*args, **kwargs)
    430 
    431     def __eq__(self, other):

/home/maxnoe/.local/anaconda3/envs/ctapipe/lib/python3.5/site-packages/matplotlib/colorbar.py in on_mappable_changed(self, mappable)
    915         self.set_cmap(mappable.get_cmap())
    916         self.set_clim(mappable.get_clim())
--> 917         self.update_normal(mappable)
    918 
    919     def add_lines(self, CS, erase=True):

/home/maxnoe/.local/anaconda3/envs/ctapipe/lib/python3.5/site-packages/matplotlib/colorbar.py in update_normal(self, mappable)
    946         or contour plot to which this colorbar belongs is changed.
    947         '''
--> 948         self.draw_all()
    949         if isinstance(self.mappable, contour.ContourSet):
    950             CS = self.mappable

/home/maxnoe/.local/anaconda3/envs/ctapipe/lib/python3.5/site-packages/matplotlib/colorbar.py in draw_all(self)
    346         X, Y = self._mesh()
    347         C = self._values[:, np.newaxis]
--> 348         self._config_axes(X, Y)
    349         if self.filled:
    350             self._add_solids(X, Y, C)

/home/maxnoe/.local/anaconda3/envs/ctapipe/lib/python3.5/site-packages/matplotlib/colorbar.py in _config_axes(self, X, Y)
    442         ax.add_artist(self.patch)
    443 
--> 444         self.update_ticks()
    445 
    446     def _set_label(self):

/home/maxnoe/.local/anaconda3/envs/ctapipe/lib/python3.5/site-packages/matplotlib/colorbar.py in update_ticks(self)
    371         """
    372         ax = self.ax
--> 373         ticks, ticklabels, offset_string = self._ticker()
    374         if self.orientation == 'vertical':
    375             ax.yaxis.set_ticks(ticks)

/home/maxnoe/.local/anaconda3/envs/ctapipe/lib/python3.5/site-packages/matplotlib/colorbar.py in _ticker(self)
    592         formatter.set_data_interval(*intv)
    593 
--> 594         b = np.array(locator())
    595         if isinstance(locator, ticker.LogLocator):
    596             eps = 1e-10

/home/maxnoe/.local/anaconda3/envs/ctapipe/lib/python3.5/site-packages/matplotlib/ticker.py in __call__(self)
   1533         'Return the locations of the ticks'
   1534         vmin, vmax = self.axis.get_view_interval()
-> 1535         return self.tick_values(vmin, vmax)
   1536 
   1537     def tick_values(self, vmin, vmax):

/home/maxnoe/.local/anaconda3/envs/ctapipe/lib/python3.5/site-packages/matplotlib/ticker.py in tick_values(self, vmin, vmax)
   1551             if vmin <= 0.0 or not np.isfinite(vmin):
   1552                 raise ValueError(
-> 1553                     "Data has no positive values, and therefore can not be "
   1554                     "log-scaled.")
   1555 

ValueError: Data has no positive values, and therefore can not be log-scaled.
```

Any news on this? Why does setting the norm back to a linear norm blow up if there are negative values?

``` python
In [2]: %matplotlib
Using matplotlib backend: Qt4Agg

In [3]: # %load minimal_norm.py
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import Normalize, LogNorm


x, y = np.meshgrid(np.linspace(0, 1, 10), np.linspace(0, 1, 10))
z = np.random.normal(0, 5, size=x.shape)

fig = plt.figure()
img = plt.pcolor(x, y, z, cmap='viridis')
cbar = plt.colorbar(img)
   ...: 

In [4]: img.norm = LogNorm()

In [5]: img.autoscale()

In [7]: cbar.update_bruteforce(img)

In [8]: img.norm = Normalize()

In [9]: img.autoscale()
---------------------------------------------------------------------------
ValueError                                Traceback (most recent call last)
<ipython-input-9-e26279d12b00> in <module>()
----> 1 img.autoscale()

/home/maxnoe/.local/anaconda3/envs/ctapipe/lib/python3.5/site-packages/matplotlib/cm.py in autoscale(self)
    323             raise TypeError('You must first set_array for mappable')
    324         self.norm.autoscale(self._A)
--> 325         self.changed()
    326 
    327     def autoscale_None(self):

/home/maxnoe/.local/anaconda3/envs/ctapipe/lib/python3.5/site-packages/matplotlib/cm.py in changed(self)
    357         callbackSM listeners to the 'changed' signal
    358         """
--> 359         self.callbacksSM.process('changed', self)
    360 
    361         for key in self.update_dict:

/home/maxnoe/.local/anaconda3/envs/ctapipe/lib/python3.5/site-packages/matplotlib/cbook.py in process(self, s, *args, **kwargs)
    561             for cid, proxy in list(six.iteritems(self.callbacks[s])):
    562                 try:
--> 563                     proxy(*args, **kwargs)
    564                 except ReferenceError:
    565                     self._remove_proxy(proxy)

/home/maxnoe/.local/anaconda3/envs/ctapipe/lib/python3.5/site-packages/matplotlib/cbook.py in __call__(self, *args, **kwargs)
    428             mtd = self.func
    429         # invoke the callable and return the result
--> 430         return mtd(*args, **kwargs)
    431 
    432     def __eq__(self, other):

/home/maxnoe/.local/anaconda3/envs/ctapipe/lib/python3.5/site-packages/matplotlib/colorbar.py in on_mappable_changed(self, mappable)
    915         self.set_cmap(mappable.get_cmap())
    916         self.set_clim(mappable.get_clim())
--> 917         self.update_normal(mappable)
    918 
    919     def add_lines(self, CS, erase=True):

/home/maxnoe/.local/anaconda3/envs/ctapipe/lib/python3.5/site-packages/matplotlib/colorbar.py in update_normal(self, mappable)
    946         or contour plot to which this colorbar belongs is changed.
    947         '''
--> 948         self.draw_all()
    949         if isinstance(self.mappable, contour.ContourSet):
    950             CS = self.mappable

/home/maxnoe/.local/anaconda3/envs/ctapipe/lib/python3.5/site-packages/matplotlib/colorbar.py in draw_all(self)
    346         X, Y = self._mesh()
    347         C = self._values[:, np.newaxis]
--> 348         self._config_axes(X, Y)
    349         if self.filled:
    350             self._add_solids(X, Y, C)

/home/maxnoe/.local/anaconda3/envs/ctapipe/lib/python3.5/site-packages/matplotlib/colorbar.py in _config_axes(self, X, Y)
    442         ax.add_artist(self.patch)
    443 
--> 444         self.update_ticks()
    445 
    446     def _set_label(self):

/home/maxnoe/.local/anaconda3/envs/ctapipe/lib/python3.5/site-packages/matplotlib/colorbar.py in update_ticks(self)
    371         """
    372         ax = self.ax
--> 373         ticks, ticklabels, offset_string = self._ticker()
    374         if self.orientation == 'vertical':
    375             ax.yaxis.set_ticks(ticks)

/home/maxnoe/.local/anaconda3/envs/ctapipe/lib/python3.5/site-packages/matplotlib/colorbar.py in _ticker(self)
    592         formatter.set_data_interval(*intv)
    593 
--> 594         b = np.array(locator())
    595         if isinstance(locator, ticker.LogLocator):
    596             eps = 1e-10

/home/maxnoe/.local/anaconda3/envs/ctapipe/lib/python3.5/site-packages/matplotlib/ticker.py in __call__(self)
   1536         'Return the locations of the ticks'
   1537         vmin, vmax = self.axis.get_view_interval()
-> 1538         return self.tick_values(vmin, vmax)
   1539 
   1540     def tick_values(self, vmin, vmax):

/home/maxnoe/.local/anaconda3/envs/ctapipe/lib/python3.5/site-packages/matplotlib/ticker.py in tick_values(self, vmin, vmax)
   1554             if vmin <= 0.0 or not np.isfinite(vmin):
   1555                 raise ValueError(
-> 1556                     "Data has no positive values, and therefore can not be "
   1557                     "log-scaled.")
   1558 

ValueError: Data has no positive values, and therefore can not be log-scaled
```

This issue has been marked "inactive" because it has been 365 days since the last comment. If this issue is still present in recent Matplotlib releases, or the feature request is still wanted, please leave a comment and this label will be removed. If there are no updates in another 30 days, this issue will be automatically closed, but you are free to re-open or create a new issue if needed. We value issue reports, and this procedure is meant to help us resurface and prioritize issues that have not been addressed yet, not make them disappear.  Thanks for your help!

## Patch

```diff

diff --git a/lib/matplotlib/colorbar.py b/lib/matplotlib/colorbar.py
--- a/lib/matplotlib/colorbar.py
+++ b/lib/matplotlib/colorbar.py
@@ -301,11 +301,6 @@ def __init__(self, ax, mappable=None, *, cmap=None,
         if mappable is None:
             mappable = cm.ScalarMappable(norm=norm, cmap=cmap)
 
-        # Ensure the given mappable's norm has appropriate vmin and vmax
-        # set even if mappable.draw has not yet been called.
-        if mappable.get_array() is not None:
-            mappable.autoscale_None()
-
         self.mappable = mappable
         cmap = mappable.cmap
         norm = mappable.norm
@@ -1101,7 +1096,10 @@ def _process_values(self):
             b = np.hstack((b, b[-1] + 1))
 
         # transform from 0-1 to vmin-vmax:
+        if self.mappable.get_array() is not None:
+            self.mappable.autoscale_None()
         if not self.norm.scaled():
+            # If we still aren't scaled after autoscaling, use 0, 1 as default
             self.norm.vmin = 0
             self.norm.vmax = 1
         self.norm.vmin, self.norm.vmax = mtransforms.nonsingular(


```

## Test Patch

```diff
diff --git a/lib/matplotlib/tests/test_colorbar.py b/lib/matplotlib/tests/test_colorbar.py
--- a/lib/matplotlib/tests/test_colorbar.py
+++ b/lib/matplotlib/tests/test_colorbar.py
@@ -657,6 +657,12 @@ def test_colorbar_scale_reset():
 
     assert cbar.outline.get_edgecolor() == mcolors.to_rgba('red')
 
+    # log scale with no vmin/vmax set should scale to the data if there
+    # is a mappable already associated with the colorbar, not (0, 1)
+    pcm.norm = LogNorm()
+    assert pcm.norm.vmin == z.min()
+    assert pcm.norm.vmax == z.max()
+
 
 def test_colorbar_get_ticks_2():
     plt.rcParams['_internal.classic_mode'] = False

```

## Test Information

**Tests that should FAIL→PASS**: ["lib/matplotlib/tests/test_colorbar.py::test_colorbar_scale_reset"]

**Tests that should PASS→PASS**: ["lib/matplotlib/tests/test_colorbar.py::test_colorbar_extension_shape[png]", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_extension_length[png]", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_extension_inverted_axis[min-expected0-horizontal]", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_extension_inverted_axis[min-expected0-vertical]", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_extension_inverted_axis[max-expected1-horizontal]", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_extension_inverted_axis[max-expected1-vertical]", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_extension_inverted_axis[both-expected2-horizontal]", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_extension_inverted_axis[both-expected2-vertical]", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_positioning[png-True]", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_positioning[png-False]", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_single_ax_panchor_false", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_single_ax_panchor_east[standard]", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_single_ax_panchor_east[constrained]", "lib/matplotlib/tests/test_colorbar.py::test_contour_colorbar[png]", "lib/matplotlib/tests/test_colorbar.py::test_gridspec_make_colorbar[png]", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_single_scatter[png]", "lib/matplotlib/tests/test_colorbar.py::test_remove_from_figure[no", "lib/matplotlib/tests/test_colorbar.py::test_remove_from_figure[with", "lib/matplotlib/tests/test_colorbar.py::test_remove_from_figure_cl", "lib/matplotlib/tests/test_colorbar.py::test_colorbarbase", "lib/matplotlib/tests/test_colorbar.py::test_parentless_mappable", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_closed_patch[png]", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_ticks", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_minorticks_on_off", "lib/matplotlib/tests/test_colorbar.py::test_cbar_minorticks_for_rc_xyminortickvisible", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_autoticks", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_autotickslog", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_get_ticks", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_lognorm_extension[both]", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_lognorm_extension[min]", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_lognorm_extension[max]", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_powernorm_extension", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_axes_kw", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_log_minortick_labels", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_renorm", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_format[%4.2e]", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_format[{x:.2e}]", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_get_ticks_2", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_inverted_ticks", "lib/matplotlib/tests/test_colorbar.py::test_mappable_no_alpha", "lib/matplotlib/tests/test_colorbar.py::test_mappable_2d_alpha", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_label", "lib/matplotlib/tests/test_colorbar.py::test_keeping_xlabel[png]", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_int[clim0]", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_int[clim1]", "lib/matplotlib/tests/test_colorbar.py::test_anchored_cbar_position_using_specgrid", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_change_lim_scale[png]", "lib/matplotlib/tests/test_colorbar.py::test_axes_handles_same_functions[png]", "lib/matplotlib/tests/test_colorbar.py::test_inset_colorbar_layout", "lib/matplotlib/tests/test_colorbar.py::test_twoslope_colorbar[png]", "lib/matplotlib/tests/test_colorbar.py::test_remove_cb_whose_mappable_has_no_figure[png]", "lib/matplotlib/tests/test_colorbar.py::test_aspects", "lib/matplotlib/tests/test_colorbar.py::test_proportional_colorbars[png]", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_extend_drawedges[png]", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_contourf_extend_patches[png]", "lib/matplotlib/tests/test_colorbar.py::test_negative_boundarynorm", "lib/matplotlib/tests/test_colorbar.py::test_centerednorm", "lib/matplotlib/tests/test_colorbar.py::test_boundaries[png]", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_no_warning_rcparams_grid_true", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_set_formatter_locator", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_extend_alpha[png]", "lib/matplotlib/tests/test_colorbar.py::test_offset_text_loc", "lib/matplotlib/tests/test_colorbar.py::test_title_text_loc", "lib/matplotlib/tests/test_colorbar.py::test_passing_location[png]", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_errors[kwargs0-TypeError-location", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_errors[kwargs1-TypeError-location", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_errors[kwargs2-ValueError-'top'", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_errors[kwargs3-ValueError-invalid", "lib/matplotlib/tests/test_colorbar.py::test_colorbar_axes_parmeters"]

**Base Commit**: 78bf53caacbb5ce0dc7aa73f07a74c99f1ed919b
**Environment Setup Commit**: 0849036fd992a2dd133a0cffc3f84f58ccf1840f
