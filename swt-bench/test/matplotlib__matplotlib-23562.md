# matplotlib__matplotlib-23562

**Repository**: matplotlib/matplotlib
**Created**: 2022-08-05T13:44:06Z
**Version**: 3.5

## Problem Statement

'Poly3DCollection' object has no attribute '_facecolors2d'
The following minimal example demonstrates the issue:

```
import numpy as np
import matplotlib.tri as mtri
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

y,x = np.ogrid[1:10:100j, 1:10:100j]
z2 = np.cos(x)**3 - np.sin(y)**2
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
r = ax.plot_surface(x,y,z2, cmap='hot')
r.get_facecolors()
```

It fails on the last line with the following traceback:

```
AttributeError                            Traceback (most recent call last)
<ipython-input-13-de0f41d662cd> in <module>()
----> 1 r.get_facecolors()

/home/oliver/.virtualenvs/mpl/local/lib/python2.7/site-packages/mpl_toolkits/mplot3d/art3d.pyc in get_facecolors(self)
    634
    635     def get_facecolors(self):
--> 636         return self._facecolors2d
    637     get_facecolor = get_facecolors
    638

AttributeError: 'Poly3DCollection' object has no attribute '_facecolors2d'
```

Tested with mpl versions 1.3.1 and 1.4.2.

Sent here by Benjamin, from the mpl users mailing list (mail with the same title). Sorry for dumping this without more assistance, I'm not yet at a python level where I can help in debugging, I think (well, it seems daunting).



## Hints

Ok, I have a "fix", in the sense that that attribute will be defined upon initialization. However, for your example, the facecolors returned is completely useless ([[0, 0, 1, 1]] -- all blue, which is default). I suspect that there is a deeper problem with ScalarMappables in general in that they don't set their facecolors until draw time?

The solution is to probably force the evaluation of the norm + cmap in `get_facecolors`.

The bigger question I have is if regular PolyCollections that are
ScalarMappables suffer from the same problem?

On Sat, Feb 7, 2015 at 6:42 PM, Thomas A Caswell notifications@github.com
wrote:

> The solution is to probably force the evaluation of the norm + cmap in
> get_facecolors.
> 
> —
> Reply to this email directly or view it on GitHub
> https://github.com/matplotlib/matplotlib/issues/4067#issuecomment-73389124
> .

PR #4090 addresses this.  Although, it still doesn't return any useful
value... it just does the same thing that regular PolyCollections do.

On Mon, Feb 9, 2015 at 3:47 PM, Thomas A Caswell notifications@github.com
wrote:

> Assigned #4067 https://github.com/matplotlib/matplotlib/issues/4067 to
> @WeatherGod https://github.com/WeatherGod.
> 
> —
> Reply to this email directly or view it on GitHub
> https://github.com/matplotlib/matplotlib/issues/4067#event-232758504.

I believe I'm still running into this issue today. Below is the error message I receive when attempting to convert hb_made (a hexbin PolyCollection) into a Poly3DCollection. Are there any other ways to convert 2D PolyCollections into 3D PolyCollections?

```
ax.add_collection3d(hb_made, zs=shotNumber.get_array(), zdir='y')
```

  File "/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/mpl_toolkits/mplot3d/axes3d.py", line 2201, in add_collection3d
    art3d.poly_collection_2d_to_3d(col, zs=zs, zdir=zdir)
  File "/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/mpl_toolkits/mplot3d/art3d.py", line 716, in poly_collection_2d_to_3d
    col.set_3d_properties()
  File "/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/mpl_toolkits/mplot3d/art3d.py", line 595, in set_3d_properties
    self._edgecolors3d = PolyCollection.get_edgecolors(self)
  File "/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/matplotlib/collections.py", line 626, in get_edgecolor
    return self.get_facecolors()
  File "/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/mpl_toolkits/mplot3d/art3d.py", line 699, in get_facecolors
    return self._facecolors2d
AttributeError: 'Poly3DCollection' object has no attribute '_facecolors2d'

I don't know if this is the appropriate place to post this, but here is a temporary fix for anyone who is waiting on the permanent fix.

I encounter this same error when trying to add a legend to my 3D surface plot.

```
surf = axarr[0].plot_surface(XSrc, YAmb, XCorrMeanDepthErrs[CodingScheme], label=CodingScheme, 
						alpha=.5, facecolor=color, edgecolor='black', linewidth=2)
axarr[0].legend()
```

While a permanent fix is find, I found that a simple temporary fix is to explicitly set the `_facecolors2d` and `_edgecolors2d` parameters after creating the surface plot.

```
surf = axarr[0].plot_surface(XSrc, YAmb, XCorrMeanDepthErrs[CodingScheme], label=CodingScheme, 
						alpha=.5, facecolor=color, edgecolor='black', linewidth=2)
surf._facecolors2d=surf._facecolors3d
surf._edgecolors2d=surf._edgecolors3d
axarr[0].legend()
```

I also could not get the legend to show in my 3d plot of planes with the error:"AttributeError: 'Poly3DCollection' object has no attribute '_edgecolors2d'". 

Although the fix from @felipegb94 worked: 
surf._facecolors2d=surf._facecolors3d
surf._edgecolors2d=surf._edgecolors3d


I'm remilestoning this to keep it on the radar. 
I run into this today, but now even the workaround (https://github.com/matplotlib/matplotlib/issues/4067#issuecomment-357794003) is not working any more.
I ran into this today, with version 3.3.1.post1012+g5584ba764, the workaround did the trick.
I ran in to this as well, and the fix works in version 3.3.1 but not in 3.3.3
@bootje2000 Apparently some attributes have been renamed or moved around (prima facie). Try this slight modification to @felipegb94's workaround:
```
surf._facecolors2d = surf._facecolor3d
surf._edgecolors2d = surf._edgecolor3d
```
Note the lack of "s" on the RHS. `_facecolors3d` and `_edgecolors3d` do not seem to exist anymore.

This works in `matplotlib 3.3.3` as of January 04, 2021.
None of the workarounds work in matplotlib 3.5.1
It works after modifying for the available attributes `_facecolors `and `_edgecolors`:
`surf._facecolors2d = surf._facecolors`
`surf._edgecolors2d = surf._edgecolors`

Hint: if there are multiple surfaces on the same axes, the workaround must be applied to each surface individually.
@nina-wwc I just checked the minimal working example in this thread using `matplotlib-3.5.1` and `3.5.2` (latest) and my workaround works as it did before, as does yours. Could you test the example code in a virtual environment perhaps, if you haven't already done so?
The problem still is that we update some state during the draw process.  Internally we do the updating and the access in just the right order so that in most cases we do not notice that we also add the attributes on the fly. 

The best workaround for the current case (assuming 3.5):

```python
import numpy as np
import matplotlib.tri as mtri
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

y,x = np.ogrid[1:10:100j, 1:10:100j]
z2 = np.cos(x)**3 - np.sin(y)**2
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
r = ax.plot_surface(x,y,z2, cmap='hot')
fig.draw_without_rendering()   # <--- This is the key line
r.get_facecolors()
```

However, I still think the best solution is https://github.com/matplotlib/matplotlib/issues/4067#issuecomment-73389124 which will require looking in `get_facecolors` to detect when these attributes are missing (and if stale?) and then force what ever needs to be done to update them.

Labeling this as a good first issue because it clearly has affected a lot of people for a long time, there is a very clear reproduction example (that will make a perfect test), and there are no API design choices to be made, but medium difficulty because it will require understanding some slightly tricking inheritance and how our 3D artists draw them selves. 

## Patch

```diff

diff --git a/lib/mpl_toolkits/mplot3d/art3d.py b/lib/mpl_toolkits/mplot3d/art3d.py
--- a/lib/mpl_toolkits/mplot3d/art3d.py
+++ b/lib/mpl_toolkits/mplot3d/art3d.py
@@ -867,9 +867,19 @@ def set_alpha(self, alpha):
         self.stale = True
 
     def get_facecolor(self):
+        # docstring inherited
+        # self._facecolors2d is not initialized until do_3d_projection
+        if not hasattr(self, '_facecolors2d'):
+            self.axes.M = self.axes.get_proj()
+            self.do_3d_projection()
         return self._facecolors2d
 
     def get_edgecolor(self):
+        # docstring inherited
+        # self._edgecolors2d is not initialized until do_3d_projection
+        if not hasattr(self, '_edgecolors2d'):
+            self.axes.M = self.axes.get_proj()
+            self.do_3d_projection()
         return self._edgecolors2d
 
 


```

## Test Patch

```diff
diff --git a/lib/mpl_toolkits/tests/test_mplot3d.py b/lib/mpl_toolkits/tests/test_mplot3d.py
--- a/lib/mpl_toolkits/tests/test_mplot3d.py
+++ b/lib/mpl_toolkits/tests/test_mplot3d.py
@@ -1812,6 +1812,28 @@ def test_scatter_spiral():
     fig.canvas.draw()
 
 
+def test_Poly3DCollection_get_facecolor():
+    # Smoke test to see that get_facecolor does not raise
+    # See GH#4067
+    y, x = np.ogrid[1:10:100j, 1:10:100j]
+    z2 = np.cos(x) ** 3 - np.sin(y) ** 2
+    fig = plt.figure()
+    ax = fig.add_subplot(111, projection='3d')
+    r = ax.plot_surface(x, y, z2, cmap='hot')
+    r.get_facecolor()
+
+
+def test_Poly3DCollection_get_edgecolor():
+    # Smoke test to see that get_edgecolor does not raise
+    # See GH#4067
+    y, x = np.ogrid[1:10:100j, 1:10:100j]
+    z2 = np.cos(x) ** 3 - np.sin(y) ** 2
+    fig = plt.figure()
+    ax = fig.add_subplot(111, projection='3d')
+    r = ax.plot_surface(x, y, z2, cmap='hot')
+    r.get_edgecolor()
+
+
 @pytest.mark.parametrize(
     "vertical_axis, proj_expected, axis_lines_expected, tickdirs_expected",
     [

```

## Test Information

**Tests that should FAIL→PASS**: ["lib/mpl_toolkits/tests/test_mplot3d.py::test_Poly3DCollection_get_facecolor", "lib/mpl_toolkits/tests/test_mplot3d.py::test_Poly3DCollection_get_edgecolor"]

**Tests that should PASS→PASS**: ["lib/mpl_toolkits/tests/test_mplot3d.py::test_invisible_axes[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_aspects[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_axes3d_repr", "lib/mpl_toolkits/tests/test_mplot3d.py::test_bar3d[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_bar3d_colors", "lib/mpl_toolkits/tests/test_mplot3d.py::test_bar3d_shaded[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_bar3d_notshaded[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_bar3d_lightsource", "lib/mpl_toolkits/tests/test_mplot3d.py::test_contour3d[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_contour3d_extend3d[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_contourf3d[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_contourf3d_fill[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_contourf3d_extend[png-both-levels0]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_contourf3d_extend[png-min-levels1]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_contourf3d_extend[png-max-levels2]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_tricontour[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_contour3d_1d_input", "lib/mpl_toolkits/tests/test_mplot3d.py::test_lines3d[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_plot_scalar[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_mixedsubplots[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_tight_layout_text[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_scatter3d[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_scatter3d_color[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_scatter3d_linewidth[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_scatter3d_linewidth_modification[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_scatter3d_modification[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_scatter3d_sorting[png-True]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_scatter3d_sorting[png-False]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_marker_draw_order_data_reversed[png--50]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_marker_draw_order_data_reversed[png-130]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_marker_draw_order_view_rotated[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_plot_3d_from_2d[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_surface3d[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_surface3d_shaded[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_surface3d_masked[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_surface3d_masked_strides[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_text3d[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_text3d_modification[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_trisurf3d[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_trisurf3d_shaded[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_wireframe3d[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_wireframe3dzerocstride[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_wireframe3dzerorstride[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_wireframe3dzerostrideraises", "lib/mpl_toolkits/tests/test_mplot3d.py::test_mixedsamplesraises", "lib/mpl_toolkits/tests/test_mplot3d.py::test_quiver3d[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_quiver3d_empty[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_quiver3d_masked[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_patch_modification", "lib/mpl_toolkits/tests/test_mplot3d.py::test_patch_collection_modification[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_poly3dcollection_verts_validation", "lib/mpl_toolkits/tests/test_mplot3d.py::test_poly3dcollection_closed[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_poly_collection_2d_to_3d_empty", "lib/mpl_toolkits/tests/test_mplot3d.py::test_poly3dcollection_alpha[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_add_collection3d_zs_array[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_add_collection3d_zs_scalar[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_axes3d_labelpad[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_axes3d_cla[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_axes3d_rotated[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_plotsurface_1d_raises", "lib/mpl_toolkits/tests/test_mplot3d.py::test_proj_transform", "lib/mpl_toolkits/tests/test_mplot3d.py::test_proj_axes_cube[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_proj_axes_cube_ortho[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_rot", "lib/mpl_toolkits/tests/test_mplot3d.py::test_world", "lib/mpl_toolkits/tests/test_mplot3d.py::test_lines_dists[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_lines_dists_nowarning", "lib/mpl_toolkits/tests/test_mplot3d.py::test_autoscale", "lib/mpl_toolkits/tests/test_mplot3d.py::test_unautoscale[True-x]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_unautoscale[True-y]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_unautoscale[True-z]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_unautoscale[False-x]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_unautoscale[False-y]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_unautoscale[False-z]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_unautoscale[None-x]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_unautoscale[None-y]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_unautoscale[None-z]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_axes3d_focal_length_checks", "lib/mpl_toolkits/tests/test_mplot3d.py::test_axes3d_focal_length[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_axes3d_ortho[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_axes3d_isometric[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_invalid_axes_limits[set_xlim3d-left-inf]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_invalid_axes_limits[set_xlim3d-left-nan]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_invalid_axes_limits[set_xlim3d-right-inf]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_invalid_axes_limits[set_xlim3d-right-nan]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_invalid_axes_limits[set_ylim3d-bottom-inf]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_invalid_axes_limits[set_ylim3d-bottom-nan]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_invalid_axes_limits[set_ylim3d-top-inf]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_invalid_axes_limits[set_ylim3d-top-nan]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_invalid_axes_limits[set_zlim3d-bottom-inf]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_invalid_axes_limits[set_zlim3d-bottom-nan]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_invalid_axes_limits[set_zlim3d-top-inf]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_invalid_axes_limits[set_zlim3d-top-nan]", "lib/mpl_toolkits/tests/test_mplot3d.py::TestVoxels::test_simple[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::TestVoxels::test_edge_style[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::TestVoxels::test_named_colors[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::TestVoxels::test_rgb_data[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::TestVoxels::test_alpha[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::TestVoxels::test_xyz[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::TestVoxels::test_calling_conventions", "lib/mpl_toolkits/tests/test_mplot3d.py::test_line3d_set_get_data_3d", "lib/mpl_toolkits/tests/test_mplot3d.py::test_inverted[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_inverted_cla", "lib/mpl_toolkits/tests/test_mplot3d.py::test_ax3d_tickcolour", "lib/mpl_toolkits/tests/test_mplot3d.py::test_ticklabel_format[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_quiver3D_smoke[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_minor_ticks[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_errorbar3d_errorevery[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_errorbar3d[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_stem3d[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_equal_box_aspect[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_colorbar_pos", "lib/mpl_toolkits/tests/test_mplot3d.py::test_shared_axes_retick", "lib/mpl_toolkits/tests/test_mplot3d.py::test_pan", "lib/mpl_toolkits/tests/test_mplot3d.py::test_scalarmap_update[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_subfigure_simple", "lib/mpl_toolkits/tests/test_mplot3d.py::test_computed_zorder[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_format_coord", "lib/mpl_toolkits/tests/test_mplot3d.py::test_get_axis_position", "lib/mpl_toolkits/tests/test_mplot3d.py::test_margins", "lib/mpl_toolkits/tests/test_mplot3d.py::test_margins_errors[ValueError-args0-kwargs0-margin", "lib/mpl_toolkits/tests/test_mplot3d.py::test_margins_errors[ValueError-args1-kwargs1-margin", "lib/mpl_toolkits/tests/test_mplot3d.py::test_margins_errors[ValueError-args2-kwargs2-margin", "lib/mpl_toolkits/tests/test_mplot3d.py::test_margins_errors[ValueError-args3-kwargs3-margin", "lib/mpl_toolkits/tests/test_mplot3d.py::test_margins_errors[ValueError-args4-kwargs4-margin", "lib/mpl_toolkits/tests/test_mplot3d.py::test_margins_errors[ValueError-args5-kwargs5-margin", "lib/mpl_toolkits/tests/test_mplot3d.py::test_margins_errors[TypeError-args6-kwargs6-Cannot", "lib/mpl_toolkits/tests/test_mplot3d.py::test_margins_errors[TypeError-args7-kwargs7-Cannot", "lib/mpl_toolkits/tests/test_mplot3d.py::test_margins_errors[TypeError-args8-kwargs8-Cannot", "lib/mpl_toolkits/tests/test_mplot3d.py::test_margins_errors[TypeError-args9-kwargs9-Must", "lib/mpl_toolkits/tests/test_mplot3d.py::test_text_3d[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_pathpatch_3d[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_scatter_spiral[png]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_view_init_vertical_axis[z-proj_expected0-axis_lines_expected0-tickdirs_expected0]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_view_init_vertical_axis[y-proj_expected1-axis_lines_expected1-tickdirs_expected1]", "lib/mpl_toolkits/tests/test_mplot3d.py::test_view_init_vertical_axis[x-proj_expected2-axis_lines_expected2-tickdirs_expected2]"]

**Base Commit**: 29a86636a9c45ab5ac4d80ac76eaee497f460dce
**Environment Setup Commit**: de98877e3dc45de8dd441d008f23d88738dc015d
