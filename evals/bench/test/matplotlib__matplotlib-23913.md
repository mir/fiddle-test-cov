# matplotlib__matplotlib-23913

**Repository**: matplotlib/matplotlib
**Created**: 2022-09-16T21:51:24Z
**Version**: 3.6

## Problem Statement

legend draggable as keyword
<!--To help us understand and resolve your issue, please fill out the form to the best of your ability.-->
<!--You can feel free to delete the sections that do not apply.-->

### Feature request

**There is not keyword to make legend draggable at creation**

<!--A short 1-2 sentences that succinctly describes the bug-->

Is there a code reason why one can not add a "draggable=True" keyword to the __init__ function for Legend?  This would be more handy than having to call it after legend creation.  And, naively, it would seem simple to do.  But maybe there is a reason why it would not work?


## Hints

This seems like a reasonable request, you're welcome to submit a PR :-)  Note that the same comment applies to annotations.
I would also deprecate `draggable()` in favor of the more classic `set_draggable()`, `get_draggable()` (and thus, in the long-term future, `.draggable` could become a property).

## Patch

```diff

diff --git a/lib/matplotlib/legend.py b/lib/matplotlib/legend.py
--- a/lib/matplotlib/legend.py
+++ b/lib/matplotlib/legend.py
@@ -286,6 +286,9 @@ def _update_bbox_to_anchor(self, loc_in_canvas):
     The custom dictionary mapping instances or types to a legend
     handler. This *handler_map* updates the default handler map
     found at `matplotlib.legend.Legend.get_legend_handler_map`.
+
+draggable : bool, default: False
+    Whether the legend can be dragged with the mouse.
 """)
 
 
@@ -342,7 +345,8 @@ def __init__(
         title_fontproperties=None,  # properties for the legend title
         alignment="center",       # control the alignment within the legend box
         *,
-        ncol=1  # synonym for ncols (backward compatibility)
+        ncol=1,  # synonym for ncols (backward compatibility)
+        draggable=False  # whether the legend can be dragged with the mouse
     ):
         """
         Parameters
@@ -537,7 +541,9 @@ def val_or_rc(val, rc_name):
             title_prop_fp.set_size(title_fontsize)
 
         self.set_title(title, prop=title_prop_fp)
+
         self._draggable = None
+        self.set_draggable(state=draggable)
 
         # set the text color
 


```

## Test Patch

```diff
diff --git a/lib/matplotlib/tests/test_legend.py b/lib/matplotlib/tests/test_legend.py
--- a/lib/matplotlib/tests/test_legend.py
+++ b/lib/matplotlib/tests/test_legend.py
@@ -783,6 +783,14 @@ def test_get_set_draggable():
     assert not legend.get_draggable()
 
 
+@pytest.mark.parametrize('draggable', (True, False))
+def test_legend_draggable(draggable):
+    fig, ax = plt.subplots()
+    ax.plot(range(10), label='shabnams')
+    leg = ax.legend(draggable=draggable)
+    assert leg.get_draggable() is draggable
+
+
 def test_alpha_handles():
     x, n, hh = plt.hist([1, 2, 3], alpha=0.25, label='data', color='red')
     legend = plt.legend()

```

## Test Information

**Tests that should FAIL→PASS**: ["lib/matplotlib/tests/test_legend.py::test_legend_draggable[True]", "lib/matplotlib/tests/test_legend.py::test_legend_draggable[False]"]

**Tests that should PASS→PASS**: ["lib/matplotlib/tests/test_legend.py::test_legend_ordereddict", "lib/matplotlib/tests/test_legend.py::test_legend_auto1[png]", "lib/matplotlib/tests/test_legend.py::test_legend_auto1[pdf]", "lib/matplotlib/tests/test_legend.py::test_legend_auto2[png]", "lib/matplotlib/tests/test_legend.py::test_legend_auto2[pdf]", "lib/matplotlib/tests/test_legend.py::test_legend_auto3[png]", "lib/matplotlib/tests/test_legend.py::test_legend_auto3[pdf]", "lib/matplotlib/tests/test_legend.py::test_various_labels[png]", "lib/matplotlib/tests/test_legend.py::test_various_labels[pdf]", "lib/matplotlib/tests/test_legend.py::test_legend_label_with_leading_underscore", "lib/matplotlib/tests/test_legend.py::test_labels_first[png]", "lib/matplotlib/tests/test_legend.py::test_multiple_keys[png]", "lib/matplotlib/tests/test_legend.py::test_alpha_rgba[png]", "lib/matplotlib/tests/test_legend.py::test_alpha_rcparam[png]", "lib/matplotlib/tests/test_legend.py::test_fancy[png]", "lib/matplotlib/tests/test_legend.py::test_fancy[pdf]", "lib/matplotlib/tests/test_legend.py::test_framealpha[png]", "lib/matplotlib/tests/test_legend.py::test_framealpha[pdf]", "lib/matplotlib/tests/test_legend.py::test_rc[png]", "lib/matplotlib/tests/test_legend.py::test_rc[pdf]", "lib/matplotlib/tests/test_legend.py::test_legend_expand[png]", "lib/matplotlib/tests/test_legend.py::test_legend_expand[pdf]", "lib/matplotlib/tests/test_legend.py::test_hatching[png]", "lib/matplotlib/tests/test_legend.py::test_hatching[pdf]", "lib/matplotlib/tests/test_legend.py::test_legend_remove", "lib/matplotlib/tests/test_legend.py::TestLegendFunction::test_legend_no_args", "lib/matplotlib/tests/test_legend.py::TestLegendFunction::test_legend_positional_handles_labels", "lib/matplotlib/tests/test_legend.py::TestLegendFunction::test_legend_positional_handles_only", "lib/matplotlib/tests/test_legend.py::TestLegendFunction::test_legend_positional_labels_only", "lib/matplotlib/tests/test_legend.py::TestLegendFunction::test_legend_three_args", "lib/matplotlib/tests/test_legend.py::TestLegendFunction::test_legend_handler_map", "lib/matplotlib/tests/test_legend.py::TestLegendFunction::test_legend_kwargs_handles_only", "lib/matplotlib/tests/test_legend.py::TestLegendFunction::test_legend_kwargs_labels_only", "lib/matplotlib/tests/test_legend.py::TestLegendFunction::test_legend_kwargs_handles_labels", "lib/matplotlib/tests/test_legend.py::TestLegendFunction::test_warn_mixed_args_and_kwargs", "lib/matplotlib/tests/test_legend.py::TestLegendFunction::test_parasite", "lib/matplotlib/tests/test_legend.py::TestLegendFigureFunction::test_legend_handle_label", "lib/matplotlib/tests/test_legend.py::TestLegendFigureFunction::test_legend_no_args", "lib/matplotlib/tests/test_legend.py::TestLegendFigureFunction::test_legend_label_arg", "lib/matplotlib/tests/test_legend.py::TestLegendFigureFunction::test_legend_label_three_args", "lib/matplotlib/tests/test_legend.py::TestLegendFigureFunction::test_legend_label_three_args_pluskw", "lib/matplotlib/tests/test_legend.py::TestLegendFigureFunction::test_legend_kw_args", "lib/matplotlib/tests/test_legend.py::TestLegendFigureFunction::test_warn_args_kwargs", "lib/matplotlib/tests/test_legend.py::test_legend_stackplot[png]", "lib/matplotlib/tests/test_legend.py::test_cross_figure_patch_legend", "lib/matplotlib/tests/test_legend.py::test_nanscatter", "lib/matplotlib/tests/test_legend.py::test_legend_repeatcheckok", "lib/matplotlib/tests/test_legend.py::test_not_covering_scatter[png]", "lib/matplotlib/tests/test_legend.py::test_not_covering_scatter_transform[png]", "lib/matplotlib/tests/test_legend.py::test_linecollection_scaled_dashes", "lib/matplotlib/tests/test_legend.py::test_handler_numpoints", "lib/matplotlib/tests/test_legend.py::test_text_nohandler_warning", "lib/matplotlib/tests/test_legend.py::test_empty_bar_chart_with_legend", "lib/matplotlib/tests/test_legend.py::test_shadow_framealpha", "lib/matplotlib/tests/test_legend.py::test_legend_title_empty", "lib/matplotlib/tests/test_legend.py::test_legend_proper_window_extent", "lib/matplotlib/tests/test_legend.py::test_window_extent_cached_renderer", "lib/matplotlib/tests/test_legend.py::test_legend_title_fontprop_fontsize", "lib/matplotlib/tests/test_legend.py::test_legend_alignment[center]", "lib/matplotlib/tests/test_legend.py::test_legend_alignment[left]", "lib/matplotlib/tests/test_legend.py::test_legend_alignment[right]", "lib/matplotlib/tests/test_legend.py::test_legend_set_alignment[center]", "lib/matplotlib/tests/test_legend.py::test_legend_set_alignment[left]", "lib/matplotlib/tests/test_legend.py::test_legend_set_alignment[right]", "lib/matplotlib/tests/test_legend.py::test_legend_labelcolor_single[red]", "lib/matplotlib/tests/test_legend.py::test_legend_labelcolor_single[none]", "lib/matplotlib/tests/test_legend.py::test_legend_labelcolor_single[color2]", "lib/matplotlib/tests/test_legend.py::test_legend_labelcolor_list", "lib/matplotlib/tests/test_legend.py::test_legend_labelcolor_linecolor", "lib/matplotlib/tests/test_legend.py::test_legend_labelcolor_markeredgecolor", "lib/matplotlib/tests/test_legend.py::test_legend_labelcolor_markerfacecolor", "lib/matplotlib/tests/test_legend.py::test_legend_labelcolor_rcparam_single[red]", "lib/matplotlib/tests/test_legend.py::test_legend_labelcolor_rcparam_single[none]", "lib/matplotlib/tests/test_legend.py::test_legend_labelcolor_rcparam_single[color2]", "lib/matplotlib/tests/test_legend.py::test_legend_labelcolor_rcparam_linecolor", "lib/matplotlib/tests/test_legend.py::test_legend_labelcolor_rcparam_markeredgecolor", "lib/matplotlib/tests/test_legend.py::test_legend_labelcolor_rcparam_markeredgecolor_short", "lib/matplotlib/tests/test_legend.py::test_legend_labelcolor_rcparam_markerfacecolor", "lib/matplotlib/tests/test_legend.py::test_legend_labelcolor_rcparam_markerfacecolor_short", "lib/matplotlib/tests/test_legend.py::test_get_set_draggable", "lib/matplotlib/tests/test_legend.py::test_alpha_handles", "lib/matplotlib/tests/test_legend.py::test_warn_big_data_best_loc", "lib/matplotlib/tests/test_legend.py::test_no_warn_big_data_when_loc_specified", "lib/matplotlib/tests/test_legend.py::test_plot_multiple_input_multiple_label[label_array0]", "lib/matplotlib/tests/test_legend.py::test_plot_multiple_input_multiple_label[label_array1]", "lib/matplotlib/tests/test_legend.py::test_plot_multiple_input_multiple_label[label_array2]", "lib/matplotlib/tests/test_legend.py::test_plot_multiple_input_single_label[one]", "lib/matplotlib/tests/test_legend.py::test_plot_multiple_input_single_label[1]", "lib/matplotlib/tests/test_legend.py::test_plot_multiple_input_single_label[int]", "lib/matplotlib/tests/test_legend.py::test_plot_single_input_multiple_label[label_array0]", "lib/matplotlib/tests/test_legend.py::test_plot_single_input_multiple_label[label_array1]", "lib/matplotlib/tests/test_legend.py::test_plot_single_input_multiple_label[label_array2]", "lib/matplotlib/tests/test_legend.py::test_plot_multiple_label_incorrect_length_exception", "lib/matplotlib/tests/test_legend.py::test_legend_face_edgecolor", "lib/matplotlib/tests/test_legend.py::test_legend_text_axes", "lib/matplotlib/tests/test_legend.py::test_handlerline2d", "lib/matplotlib/tests/test_legend.py::test_subfigure_legend", "lib/matplotlib/tests/test_legend.py::test_setting_alpha_keeps_polycollection_color", "lib/matplotlib/tests/test_legend.py::test_legend_markers_from_line2d", "lib/matplotlib/tests/test_legend.py::test_ncol_ncols[png]", "lib/matplotlib/tests/test_legend.py::test_ncol_ncols[pdf]"]

**Base Commit**: 5c4595267ccd3daf78f5fd05693b7ecbcd575c1e
**Environment Setup Commit**: 73909bcb408886a22e2b84581d6b9e6d9907c813
