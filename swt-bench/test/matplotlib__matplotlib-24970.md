# matplotlib__matplotlib-24970

**Repository**: matplotlib/matplotlib
**Created**: 2023-01-13T14:23:39Z
**Version**: 3.6

## Problem Statement

[Bug]: NumPy 1.24 deprecation warnings
### Bug summary

Starting NumPy 1.24 I observe several deprecation warnings.


### Code for reproduction

```python
import matplotlib.pyplot as plt
import numpy as np

plt.get_cmap()(np.empty((0, ), dtype=np.uint8))
```


### Actual outcome

```
/usr/lib/python3.10/site-packages/matplotlib/colors.py:730: DeprecationWarning: NumPy will stop allowing conversion of out-of-bound Python integers to integer arrays.  The conversion of 257 to uint8 will fail in the future.
For the old behavior, usually:
    np.array(value).astype(dtype)`
will give the desired result (the cast overflows).
  xa[xa > self.N - 1] = self._i_over
/usr/lib/python3.10/site-packages/matplotlib/colors.py:731: DeprecationWarning: NumPy will stop allowing conversion of out-of-bound Python integers to integer arrays.  The conversion of 256 to uint8 will fail in the future.
For the old behavior, usually:
    np.array(value).astype(dtype)`
will give the desired result (the cast overflows).
  xa[xa < 0] = self._i_under
/usr/lib/python3.10/site-packages/matplotlib/colors.py:732: DeprecationWarning: NumPy will stop allowing conversion of out-of-bound Python integers to integer arrays.  The conversion of 258 to uint8 will fail in the future.
For the old behavior, usually:
    np.array(value).astype(dtype)`
will give the desired result (the cast overflows).
  xa[mask_bad] = self._i_bad
```

### Expected outcome

No warnings.

### Additional information

_No response_

### Operating system

ArchLinux

### Matplotlib Version

3.6.2

### Matplotlib Backend

QtAgg

### Python version

Python 3.10.9

### Jupyter version

_No response_

### Installation

Linux package manager


## Hints

Thanks for the report! Unfortunately I can't reproduce this. What version of numpy are you using when the warning appears?
Sorry, forgot to mention that you need to enable the warnings during normal execution, e.g., `python -W always <file>.py`. In my case, the warnings are issued during `pytest` run which seems to activate these warnings by default.

As for the NumPy version, I'm running
```console
$ python -c 'import numpy; print(numpy.__version__)'
1.24.0
```
Thanks, I can now reproduce 😄 
The problem is that there are three more values, that are by default out of range in this case, to note specific cases:
https://github.com/matplotlib/matplotlib/blob/8d2329ad89120410d7ef04faddba2c51db743b06/lib/matplotlib/colors.py#L673-L675
(N = 256 by default)

These are then assigned to out-of-range and masked/bad values here:
https://github.com/matplotlib/matplotlib/blob/8d2329ad89120410d7ef04faddba2c51db743b06/lib/matplotlib/colors.py#L730-L732
which now raises a deprecation warning.

I think that one way forward would be to check the type of `xa` for int/uint and in that case take modulo the maximum value for `self._i_over` etc. This is basically what happens now anyway, but we need to do it explicitly rather than relying on numpy doing it. (I cannot really see how this makes sense from a color perspective, but we will at least keep the current behavior.)
I think this is exposing a real bug that we need to promote the input data to be bigger than uint8.  What we are doing here is buildin a lookup up table, the first N entries are for for values into the actually color map and then the next 3 entries are the special cases for over/under/bad so `xa` needs to be big enough to hold `self.N + 2` as values.
I don't know if this is a bigger bug or not, but I would like us to have fixed any deprecation warnings from dependencies before 3.7 is out (or if necessary a quick 3.7.1.)

## Patch

```diff

diff --git a/lib/matplotlib/colors.py b/lib/matplotlib/colors.py
--- a/lib/matplotlib/colors.py
+++ b/lib/matplotlib/colors.py
@@ -715,16 +715,17 @@ def __call__(self, X, alpha=None, bytes=False):
         if not xa.dtype.isnative:
             xa = xa.byteswap().newbyteorder()  # Native byteorder is faster.
         if xa.dtype.kind == "f":
-            with np.errstate(invalid="ignore"):
-                xa *= self.N
-                # Negative values are out of range, but astype(int) would
-                # truncate them towards zero.
-                xa[xa < 0] = -1
-                # xa == 1 (== N after multiplication) is not out of range.
-                xa[xa == self.N] = self.N - 1
-                # Avoid converting large positive values to negative integers.
-                np.clip(xa, -1, self.N, out=xa)
-                xa = xa.astype(int)
+            xa *= self.N
+            # Negative values are out of range, but astype(int) would
+            # truncate them towards zero.
+            xa[xa < 0] = -1
+            # xa == 1 (== N after multiplication) is not out of range.
+            xa[xa == self.N] = self.N - 1
+            # Avoid converting large positive values to negative integers.
+            np.clip(xa, -1, self.N, out=xa)
+        with np.errstate(invalid="ignore"):
+            # We need this cast for unsigned ints as well as floats
+            xa = xa.astype(int)
         # Set the over-range indices before the under-range;
         # otherwise the under-range values get converted to over-range.
         xa[xa > self.N - 1] = self._i_over


```

## Test Patch

```diff
diff --git a/lib/matplotlib/tests/test_colors.py b/lib/matplotlib/tests/test_colors.py
--- a/lib/matplotlib/tests/test_colors.py
+++ b/lib/matplotlib/tests/test_colors.py
@@ -30,6 +30,13 @@ def test_create_lookup_table(N, result):
     assert_array_almost_equal(mcolors._create_lookup_table(N, data), result)
 
 
+@pytest.mark.parametrize("dtype", [np.uint8, int, np.float16, float])
+def test_index_dtype(dtype):
+    # We use subtraction in the indexing, so need to verify that uint8 works
+    cm = mpl.colormaps["viridis"]
+    assert_array_equal(cm(dtype(0)), cm(0))
+
+
 def test_resampled():
     """
     GitHub issue #6025 pointed to incorrect ListedColormap.resampled;

```

## Test Information

**Tests that should FAIL→PASS**: ["lib/matplotlib/tests/test_colors.py::test_index_dtype[uint8]"]

**Tests that should PASS→PASS**: ["lib/matplotlib/tests/test_colors.py::test_create_lookup_table[5-result0]", "lib/matplotlib/tests/test_colors.py::test_create_lookup_table[2-result1]", "lib/matplotlib/tests/test_colors.py::test_create_lookup_table[1-result2]", "lib/matplotlib/tests/test_colors.py::test_index_dtype[int]", "lib/matplotlib/tests/test_colors.py::test_index_dtype[float16]", "lib/matplotlib/tests/test_colors.py::test_index_dtype[float]", "lib/matplotlib/tests/test_colors.py::test_resampled", "lib/matplotlib/tests/test_colors.py::test_register_cmap", "lib/matplotlib/tests/test_colors.py::test_colormaps_get_cmap", "lib/matplotlib/tests/test_colors.py::test_unregister_builtin_cmap", "lib/matplotlib/tests/test_colors.py::test_colormap_copy", "lib/matplotlib/tests/test_colors.py::test_colormap_equals", "lib/matplotlib/tests/test_colors.py::test_colormap_endian", "lib/matplotlib/tests/test_colors.py::test_colormap_invalid", "lib/matplotlib/tests/test_colors.py::test_colormap_return_types", "lib/matplotlib/tests/test_colors.py::test_BoundaryNorm", "lib/matplotlib/tests/test_colors.py::test_CenteredNorm", "lib/matplotlib/tests/test_colors.py::test_lognorm_invalid[-1-2]", "lib/matplotlib/tests/test_colors.py::test_lognorm_invalid[3-1]", "lib/matplotlib/tests/test_colors.py::test_LogNorm", "lib/matplotlib/tests/test_colors.py::test_LogNorm_inverse", "lib/matplotlib/tests/test_colors.py::test_PowerNorm", "lib/matplotlib/tests/test_colors.py::test_PowerNorm_translation_invariance", "lib/matplotlib/tests/test_colors.py::test_Normalize", "lib/matplotlib/tests/test_colors.py::test_FuncNorm", "lib/matplotlib/tests/test_colors.py::test_TwoSlopeNorm_autoscale", "lib/matplotlib/tests/test_colors.py::test_TwoSlopeNorm_autoscale_None_vmin", "lib/matplotlib/tests/test_colors.py::test_TwoSlopeNorm_autoscale_None_vmax", "lib/matplotlib/tests/test_colors.py::test_TwoSlopeNorm_scale", "lib/matplotlib/tests/test_colors.py::test_TwoSlopeNorm_scaleout_center", "lib/matplotlib/tests/test_colors.py::test_TwoSlopeNorm_scaleout_center_max", "lib/matplotlib/tests/test_colors.py::test_TwoSlopeNorm_Even", "lib/matplotlib/tests/test_colors.py::test_TwoSlopeNorm_Odd", "lib/matplotlib/tests/test_colors.py::test_TwoSlopeNorm_VminEqualsVcenter", "lib/matplotlib/tests/test_colors.py::test_TwoSlopeNorm_VmaxEqualsVcenter", "lib/matplotlib/tests/test_colors.py::test_TwoSlopeNorm_VminGTVcenter", "lib/matplotlib/tests/test_colors.py::test_TwoSlopeNorm_TwoSlopeNorm_VminGTVmax", "lib/matplotlib/tests/test_colors.py::test_TwoSlopeNorm_VcenterGTVmax", "lib/matplotlib/tests/test_colors.py::test_TwoSlopeNorm_premature_scaling", "lib/matplotlib/tests/test_colors.py::test_SymLogNorm", "lib/matplotlib/tests/test_colors.py::test_SymLogNorm_colorbar", "lib/matplotlib/tests/test_colors.py::test_SymLogNorm_single_zero", "lib/matplotlib/tests/test_colors.py::TestAsinhNorm::test_init", "lib/matplotlib/tests/test_colors.py::TestAsinhNorm::test_norm", "lib/matplotlib/tests/test_colors.py::test_cmap_and_norm_from_levels_and_colors[png]", "lib/matplotlib/tests/test_colors.py::test_boundarynorm_and_colorbarbase[png]", "lib/matplotlib/tests/test_colors.py::test_cmap_and_norm_from_levels_and_colors2", "lib/matplotlib/tests/test_colors.py::test_rgb_hsv_round_trip", "lib/matplotlib/tests/test_colors.py::test_autoscale_masked", "lib/matplotlib/tests/test_colors.py::test_light_source_topo_surface[png]", "lib/matplotlib/tests/test_colors.py::test_light_source_shading_default", "lib/matplotlib/tests/test_colors.py::test_light_source_shading_empty_mask", "lib/matplotlib/tests/test_colors.py::test_light_source_masked_shading", "lib/matplotlib/tests/test_colors.py::test_light_source_hillshading", "lib/matplotlib/tests/test_colors.py::test_light_source_planar_hillshading", "lib/matplotlib/tests/test_colors.py::test_color_names", "lib/matplotlib/tests/test_colors.py::test_pandas_iterable", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Accent]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Accent_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Blues]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Blues_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[BrBG]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[BrBG_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[BuGn]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[BuGn_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[BuPu]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[BuPu_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[CMRmap]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[CMRmap_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Dark2]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Dark2_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[GnBu]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[GnBu_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Greens]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Greens_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Greys]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Greys_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[OrRd]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[OrRd_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Oranges]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Oranges_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[PRGn]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[PRGn_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Paired]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Paired_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Pastel1]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Pastel1_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Pastel2]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Pastel2_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[PiYG]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[PiYG_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[PuBu]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[PuBuGn]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[PuBuGn_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[PuBu_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[PuOr]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[PuOr_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[PuRd]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[PuRd_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Purples]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Purples_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[RdBu]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[RdBu_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[RdGy]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[RdGy_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[RdPu]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[RdPu_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[RdYlBu]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[RdYlBu_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[RdYlGn]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[RdYlGn_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Reds]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Reds_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Set1]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Set1_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Set2]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Set2_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Set3]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Set3_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Spectral]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Spectral_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Wistia]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[Wistia_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[YlGn]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[YlGnBu]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[YlGnBu_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[YlGn_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[YlOrBr]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[YlOrBr_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[YlOrRd]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[YlOrRd_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[afmhot]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[afmhot_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[autumn]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[autumn_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[binary]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[binary_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[bone]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[bone_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[brg]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[brg_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[bwr]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[bwr_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[cividis]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[cividis_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[cool]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[cool_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[coolwarm]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[coolwarm_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[copper]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[copper_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[cubehelix]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[cubehelix_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[flag]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[flag_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[gist_earth]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[gist_earth_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[gist_gray]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[gist_gray_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[gist_heat]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[gist_heat_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[gist_ncar]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[gist_ncar_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[gist_rainbow]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[gist_rainbow_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[gist_stern]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[gist_stern_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[gist_yarg]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[gist_yarg_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[gnuplot]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[gnuplot2]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[gnuplot2_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[gnuplot_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[gray]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[gray_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[hot]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[hot_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[hsv]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[hsv_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[inferno]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[inferno_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[jet]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[jet_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[magma]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[magma_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[nipy_spectral]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[nipy_spectral_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[ocean]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[ocean_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[pink]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[pink_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[plasma]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[plasma_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[prism]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[prism_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[rainbow]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[rainbow_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[seismic]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[seismic_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[spring]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[spring_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[summer]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[summer_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[tab10]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[tab10_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[tab20]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[tab20_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[tab20b]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[tab20b_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[tab20c]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[tab20c_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[terrain]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[terrain_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[turbo]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[turbo_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[twilight]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[twilight_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[twilight_shifted]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[twilight_shifted_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[viridis]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[viridis_r]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[winter]", "lib/matplotlib/tests/test_colors.py::test_colormap_reversing[winter_r]", "lib/matplotlib/tests/test_colors.py::test_has_alpha_channel", "lib/matplotlib/tests/test_colors.py::test_cn", "lib/matplotlib/tests/test_colors.py::test_conversions", "lib/matplotlib/tests/test_colors.py::test_conversions_masked", "lib/matplotlib/tests/test_colors.py::test_to_rgba_array_single_str", "lib/matplotlib/tests/test_colors.py::test_to_rgba_array_alpha_array", "lib/matplotlib/tests/test_colors.py::test_failed_conversions", "lib/matplotlib/tests/test_colors.py::test_grey_gray", "lib/matplotlib/tests/test_colors.py::test_tableau_order", "lib/matplotlib/tests/test_colors.py::test_ndarray_subclass_norm", "lib/matplotlib/tests/test_colors.py::test_same_color", "lib/matplotlib/tests/test_colors.py::test_hex_shorthand_notation", "lib/matplotlib/tests/test_colors.py::test_repr_png", "lib/matplotlib/tests/test_colors.py::test_repr_html", "lib/matplotlib/tests/test_colors.py::test_get_under_over_bad", "lib/matplotlib/tests/test_colors.py::test_non_mutable_get_values[over]", "lib/matplotlib/tests/test_colors.py::test_non_mutable_get_values[under]", "lib/matplotlib/tests/test_colors.py::test_non_mutable_get_values[bad]", "lib/matplotlib/tests/test_colors.py::test_colormap_alpha_array", "lib/matplotlib/tests/test_colors.py::test_colormap_bad_data_with_alpha", "lib/matplotlib/tests/test_colors.py::test_2d_to_rgba", "lib/matplotlib/tests/test_colors.py::test_set_dict_to_rgba", "lib/matplotlib/tests/test_colors.py::test_norm_deepcopy", "lib/matplotlib/tests/test_colors.py::test_norm_callback", "lib/matplotlib/tests/test_colors.py::test_scalarmappable_norm_update", "lib/matplotlib/tests/test_colors.py::test_norm_update_figs[png]", "lib/matplotlib/tests/test_colors.py::test_norm_update_figs[pdf]", "lib/matplotlib/tests/test_colors.py::test_make_norm_from_scale_name", "lib/matplotlib/tests/test_colors.py::test_color_sequences", "lib/matplotlib/tests/test_colors.py::test_cm_set_cmap_error"]

**Base Commit**: a3011dfd1aaa2487cce8aa7369475533133ef777
**Environment Setup Commit**: 73909bcb408886a22e2b84581d6b9e6d9907c813
