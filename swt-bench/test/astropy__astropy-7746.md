# astropy__astropy-7746

**Repository**: astropy/astropy
**Created**: 2018-08-20T14:07:20Z
**Version**: 1.3

## Problem Statement

Issue when passing empty lists/arrays to WCS transformations
The following should not fail but instead should return empty lists/arrays:

```
In [1]: from astropy.wcs import WCS

In [2]: wcs = WCS('2MASS_h.fits')

In [3]: wcs.wcs_pix2world([], [], 0)
---------------------------------------------------------------------------
InconsistentAxisTypesError                Traceback (most recent call last)
<ipython-input-3-e2cc0e97941a> in <module>()
----> 1 wcs.wcs_pix2world([], [], 0)

~/Dropbox/Code/Astropy/astropy/astropy/wcs/wcs.py in wcs_pix2world(self, *args, **kwargs)
   1352         return self._array_converter(
   1353             lambda xy, o: self.wcs.p2s(xy, o)['world'],
-> 1354             'output', *args, **kwargs)
   1355     wcs_pix2world.__doc__ = """
   1356         Transforms pixel coordinates to world coordinates by doing

~/Dropbox/Code/Astropy/astropy/astropy/wcs/wcs.py in _array_converter(self, func, sky, ra_dec_order, *args)
   1267                     "a 1-D array for each axis, followed by an origin.")
   1268 
-> 1269             return _return_list_of_arrays(axes, origin)
   1270 
   1271         raise TypeError(

~/Dropbox/Code/Astropy/astropy/astropy/wcs/wcs.py in _return_list_of_arrays(axes, origin)
   1223             if ra_dec_order and sky == 'input':
   1224                 xy = self._denormalize_sky(xy)
-> 1225             output = func(xy, origin)
   1226             if ra_dec_order and sky == 'output':
   1227                 output = self._normalize_sky(output)

~/Dropbox/Code/Astropy/astropy/astropy/wcs/wcs.py in <lambda>(xy, o)
   1351             raise ValueError("No basic WCS settings were created.")
   1352         return self._array_converter(
-> 1353             lambda xy, o: self.wcs.p2s(xy, o)['world'],
   1354             'output', *args, **kwargs)
   1355     wcs_pix2world.__doc__ = """

InconsistentAxisTypesError: ERROR 4 in wcsp2s() at line 2646 of file cextern/wcslib/C/wcs.c:
ncoord and/or nelem inconsistent with the wcsprm.
```


## Patch

```diff

diff --git a/astropy/wcs/wcs.py b/astropy/wcs/wcs.py
--- a/astropy/wcs/wcs.py
+++ b/astropy/wcs/wcs.py
@@ -1212,6 +1212,9 @@ def _array_converter(self, func, sky, *args, ra_dec_order=False):
         """
 
         def _return_list_of_arrays(axes, origin):
+            if any([x.size == 0 for x in axes]):
+                return axes
+
             try:
                 axes = np.broadcast_arrays(*axes)
             except ValueError:
@@ -1235,6 +1238,8 @@ def _return_single_array(xy, origin):
                 raise ValueError(
                     "When providing two arguments, the array must be "
                     "of shape (N, {0})".format(self.naxis))
+            if 0 in xy.shape:
+                return xy
             if ra_dec_order and sky == 'input':
                 xy = self._denormalize_sky(xy)
             result = func(xy, origin)


```

## Test Patch

```diff
diff --git a/astropy/wcs/tests/test_wcs.py b/astropy/wcs/tests/test_wcs.py
--- a/astropy/wcs/tests/test_wcs.py
+++ b/astropy/wcs/tests/test_wcs.py
@@ -1093,3 +1093,21 @@ def test_keyedsip():
     assert isinstance( w.sip, wcs.Sip )
     assert w.sip.crpix[0] == 2048
     assert w.sip.crpix[1] == 1026
+
+
+def test_zero_size_input():
+    with fits.open(get_pkg_data_filename('data/sip.fits')) as f:
+        w = wcs.WCS(f[0].header)
+
+    inp = np.zeros((0, 2))
+    assert_array_equal(inp, w.all_pix2world(inp, 0))
+    assert_array_equal(inp, w.all_world2pix(inp, 0))
+
+    inp = [], [1]
+    result = w.all_pix2world([], [1], 0)
+    assert_array_equal(inp[0], result[0])
+    assert_array_equal(inp[1], result[1])
+
+    result = w.all_world2pix([], [1], 0)
+    assert_array_equal(inp[0], result[0])
+    assert_array_equal(inp[1], result[1])

```

## Test Information

**Tests that should FAIL→PASS**: ["astropy/wcs/tests/test_wcs.py::test_zero_size_input"]

**Tests that should PASS→PASS**: ["astropy/wcs/tests/test_wcs.py::TestMaps::test_consistency", "astropy/wcs/tests/test_wcs.py::TestMaps::test_maps", "astropy/wcs/tests/test_wcs.py::TestSpectra::test_consistency", "astropy/wcs/tests/test_wcs.py::TestSpectra::test_spectra", "astropy/wcs/tests/test_wcs.py::test_fixes", "astropy/wcs/tests/test_wcs.py::test_outside_sky", "astropy/wcs/tests/test_wcs.py::test_pix2world", "astropy/wcs/tests/test_wcs.py::test_load_fits_path", "astropy/wcs/tests/test_wcs.py::test_dict_init", "astropy/wcs/tests/test_wcs.py::test_extra_kwarg", "astropy/wcs/tests/test_wcs.py::test_3d_shapes", "astropy/wcs/tests/test_wcs.py::test_preserve_shape", "astropy/wcs/tests/test_wcs.py::test_broadcasting", "astropy/wcs/tests/test_wcs.py::test_shape_mismatch", "astropy/wcs/tests/test_wcs.py::test_invalid_shape", "astropy/wcs/tests/test_wcs.py::test_warning_about_defunct_keywords", "astropy/wcs/tests/test_wcs.py::test_warning_about_defunct_keywords_exception", "astropy/wcs/tests/test_wcs.py::test_to_header_string", "astropy/wcs/tests/test_wcs.py::test_to_fits", "astropy/wcs/tests/test_wcs.py::test_to_header_warning", "astropy/wcs/tests/test_wcs.py::test_no_comments_in_header", "astropy/wcs/tests/test_wcs.py::test_find_all_wcs_crash", "astropy/wcs/tests/test_wcs.py::test_validate", "astropy/wcs/tests/test_wcs.py::test_validate_with_2_wcses", "astropy/wcs/tests/test_wcs.py::test_crpix_maps_to_crval", "astropy/wcs/tests/test_wcs.py::test_all_world2pix", "astropy/wcs/tests/test_wcs.py::test_scamp_sip_distortion_parameters", "astropy/wcs/tests/test_wcs.py::test_fixes2", "astropy/wcs/tests/test_wcs.py::test_unit_normalization", "astropy/wcs/tests/test_wcs.py::test_footprint_to_file", "astropy/wcs/tests/test_wcs.py::test_validate_faulty_wcs", "astropy/wcs/tests/test_wcs.py::test_error_message", "astropy/wcs/tests/test_wcs.py::test_out_of_bounds", "astropy/wcs/tests/test_wcs.py::test_calc_footprint_1", "astropy/wcs/tests/test_wcs.py::test_calc_footprint_2", "astropy/wcs/tests/test_wcs.py::test_calc_footprint_3", "astropy/wcs/tests/test_wcs.py::test_sip", "astropy/wcs/tests/test_wcs.py::test_printwcs", "astropy/wcs/tests/test_wcs.py::test_invalid_spherical", "astropy/wcs/tests/test_wcs.py::test_no_iteration", "astropy/wcs/tests/test_wcs.py::test_sip_tpv_agreement", "astropy/wcs/tests/test_wcs.py::test_tpv_copy", "astropy/wcs/tests/test_wcs.py::test_hst_wcs", "astropy/wcs/tests/test_wcs.py::test_list_naxis", "astropy/wcs/tests/test_wcs.py::test_sip_broken", "astropy/wcs/tests/test_wcs.py::test_no_truncate_crval", "astropy/wcs/tests/test_wcs.py::test_no_truncate_crval_try2", "astropy/wcs/tests/test_wcs.py::test_no_truncate_crval_p17", "astropy/wcs/tests/test_wcs.py::test_no_truncate_using_compare", "astropy/wcs/tests/test_wcs.py::test_passing_ImageHDU", "astropy/wcs/tests/test_wcs.py::test_inconsistent_sip", "astropy/wcs/tests/test_wcs.py::test_bounds_check", "astropy/wcs/tests/test_wcs.py::test_naxis", "astropy/wcs/tests/test_wcs.py::test_sip_with_altkey", "astropy/wcs/tests/test_wcs.py::test_to_fits_1", "astropy/wcs/tests/test_wcs.py::test_keyedsip"]

**Base Commit**: d5bd3f68bb6d5ce3a61bdce9883ee750d1afade5
**Environment Setup Commit**: 848c8fa21332abd66b44efe3cb48b72377fb32cc
