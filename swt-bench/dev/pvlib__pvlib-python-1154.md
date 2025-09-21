# pvlib__pvlib-python-1154

**Repository**: pvlib/pvlib-python
**Created**: 2021-01-29T20:53:24Z
**Version**: 0.8

## Problem Statement

pvlib.irradiance.reindl() model generates NaNs when GHI = 0
**Describe the bug**
The reindl function should give zero sky diffuse when GHI is zero. Instead it generates NaN or Inf values due to "term3" having a quotient that divides by GHI.  

**Expected behavior**
The reindl function should result in zero sky diffuse when GHI is zero.


pvlib.irradiance.reindl() model generates NaNs when GHI = 0
**Describe the bug**
The reindl function should give zero sky diffuse when GHI is zero. Instead it generates NaN or Inf values due to "term3" having a quotient that divides by GHI.  

**Expected behavior**
The reindl function should result in zero sky diffuse when GHI is zero.




## Hints

Verified. Looks like an easy fix.
Verified. Looks like an easy fix.

## Patch

```diff

diff --git a/pvlib/irradiance.py b/pvlib/irradiance.py
--- a/pvlib/irradiance.py
+++ b/pvlib/irradiance.py
@@ -886,8 +886,9 @@ def reindl(surface_tilt, surface_azimuth, dhi, dni, ghi, dni_extra,
     # these are the () and [] sub-terms of the second term of eqn 8
     term1 = 1 - AI
     term2 = 0.5 * (1 + tools.cosd(surface_tilt))
-    term3 = 1 + np.sqrt(HB / ghi) * (tools.sind(0.5 * surface_tilt) ** 3)
-
+    with np.errstate(invalid='ignore', divide='ignore'):
+        hb_to_ghi = np.where(ghi == 0, 0, np.divide(HB, ghi))
+    term3 = 1 + np.sqrt(hb_to_ghi) * (tools.sind(0.5 * surface_tilt)**3)
     sky_diffuse = dhi * (AI * Rb + term1 * term2 * term3)
     sky_diffuse = np.maximum(sky_diffuse, 0)
 


```

## Test Patch

```diff
diff --git a/pvlib/tests/test_irradiance.py b/pvlib/tests/test_irradiance.py
--- a/pvlib/tests/test_irradiance.py
+++ b/pvlib/tests/test_irradiance.py
@@ -203,7 +203,7 @@ def test_reindl(irrad_data, ephem_data, dni_et):
         40, 180, irrad_data['dhi'], irrad_data['dni'], irrad_data['ghi'],
         dni_et, ephem_data['apparent_zenith'], ephem_data['azimuth'])
     # values from matlab 1.4 code
-    assert_allclose(result, [np.nan, 27.9412, 104.1317, 34.1663], atol=1e-4)
+    assert_allclose(result, [0., 27.9412, 104.1317, 34.1663], atol=1e-4)
 
 
 def test_king(irrad_data, ephem_data):

```

## Test Information

**Tests that should FAIL→PASS**: ["pvlib/tests/test_irradiance.py::test_reindl"]

**Tests that should PASS→PASS**: ["pvlib/tests/test_irradiance.py::test_get_extra_radiation[asce-300-1383.636203]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[asce-300.0-1383.636203]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[asce-testval2-1383.636203]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[asce-testval3-1383.636203]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[asce-testval4-1383.636203]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[asce-testval5-expected5]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[asce-testval6-expected6]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[asce-testval7-expected7]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[asce-testval8-1383.636203]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[spencer-300-1383.636203]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[spencer-300.0-1383.636203]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[spencer-testval2-1383.636203]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[spencer-testval3-1383.636203]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[spencer-testval4-1383.636203]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[spencer-testval5-expected5]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[spencer-testval6-expected6]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[spencer-testval7-expected7]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[spencer-testval8-1383.636203]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[nrel-300-1383.636203]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[nrel-300.0-1383.636203]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[nrel-testval2-1383.636203]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[nrel-testval3-1383.636203]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[nrel-testval4-1383.636203]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[nrel-testval5-expected5]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[nrel-testval6-expected6]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[nrel-testval7-expected7]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[nrel-testval8-1383.636203]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[pyephem-300-1383.636203]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[pyephem-300.0-1383.636203]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[pyephem-testval2-1383.636203]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[pyephem-testval3-1383.636203]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[pyephem-testval4-1383.636203]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[pyephem-testval5-expected5]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[pyephem-testval6-expected6]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[pyephem-testval7-expected7]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation[pyephem-testval8-1383.636203]", "pvlib/tests/test_irradiance.py::test_get_extra_radiation_epoch_year", "pvlib/tests/test_irradiance.py::test_get_extra_radiation_nrel_numba", "pvlib/tests/test_irradiance.py::test_get_extra_radiation_invalid", "pvlib/tests/test_irradiance.py::test_grounddiffuse_simple_float", "pvlib/tests/test_irradiance.py::test_grounddiffuse_simple_series", "pvlib/tests/test_irradiance.py::test_grounddiffuse_albedo_0", "pvlib/tests/test_irradiance.py::test_grounddiffuse_albedo_invalid_surface", "pvlib/tests/test_irradiance.py::test_grounddiffuse_albedo_surface", "pvlib/tests/test_irradiance.py::test_isotropic_float", "pvlib/tests/test_irradiance.py::test_isotropic_series", "pvlib/tests/test_irradiance.py::test_klucher_series_float", "pvlib/tests/test_irradiance.py::test_klucher_series", "pvlib/tests/test_irradiance.py::test_haydavies", "pvlib/tests/test_irradiance.py::test_king", "pvlib/tests/test_irradiance.py::test_perez", "pvlib/tests/test_irradiance.py::test_perez_components", "pvlib/tests/test_irradiance.py::test_perez_arrays", "pvlib/tests/test_irradiance.py::test_perez_scalar", "pvlib/tests/test_irradiance.py::test_sky_diffuse_zenith_close_to_90[isotropic]", "pvlib/tests/test_irradiance.py::test_sky_diffuse_zenith_close_to_90[klucher]", "pvlib/tests/test_irradiance.py::test_sky_diffuse_zenith_close_to_90[haydavies]", "pvlib/tests/test_irradiance.py::test_sky_diffuse_zenith_close_to_90[reindl]", "pvlib/tests/test_irradiance.py::test_sky_diffuse_zenith_close_to_90[king]", "pvlib/tests/test_irradiance.py::test_sky_diffuse_zenith_close_to_90[perez]", "pvlib/tests/test_irradiance.py::test_get_sky_diffuse_invalid", "pvlib/tests/test_irradiance.py::test_campbell_norman", "pvlib/tests/test_irradiance.py::test_get_total_irradiance", "pvlib/tests/test_irradiance.py::test_get_total_irradiance_scalars[isotropic]", "pvlib/tests/test_irradiance.py::test_get_total_irradiance_scalars[klucher]", "pvlib/tests/test_irradiance.py::test_get_total_irradiance_scalars[haydavies]", "pvlib/tests/test_irradiance.py::test_get_total_irradiance_scalars[reindl]", "pvlib/tests/test_irradiance.py::test_get_total_irradiance_scalars[king]", "pvlib/tests/test_irradiance.py::test_get_total_irradiance_scalars[perez]", "pvlib/tests/test_irradiance.py::test_poa_components", "pvlib/tests/test_irradiance.py::test_disc_value[93193-expected0]", "pvlib/tests/test_irradiance.py::test_disc_value[None-expected1]", "pvlib/tests/test_irradiance.py::test_disc_value[101325-expected2]", "pvlib/tests/test_irradiance.py::test_disc_overirradiance", "pvlib/tests/test_irradiance.py::test_disc_min_cos_zenith_max_zenith", "pvlib/tests/test_irradiance.py::test_dirint_value", "pvlib/tests/test_irradiance.py::test_dirint_nans", "pvlib/tests/test_irradiance.py::test_dirint_tdew", "pvlib/tests/test_irradiance.py::test_dirint_no_delta_kt", "pvlib/tests/test_irradiance.py::test_dirint_coeffs", "pvlib/tests/test_irradiance.py::test_dirint_min_cos_zenith_max_zenith", "pvlib/tests/test_irradiance.py::test_gti_dirint", "pvlib/tests/test_irradiance.py::test_erbs", "pvlib/tests/test_irradiance.py::test_erbs_min_cos_zenith_max_zenith", "pvlib/tests/test_irradiance.py::test_erbs_all_scalar", "pvlib/tests/test_irradiance.py::test_dirindex", "pvlib/tests/test_irradiance.py::test_dirindex_min_cos_zenith_max_zenith", "pvlib/tests/test_irradiance.py::test_dni", "pvlib/tests/test_irradiance.py::test_aoi_and_aoi_projection[0-0-0-0-0-1]", "pvlib/tests/test_irradiance.py::test_aoi_and_aoi_projection[30-180-30-180-0-1]", "pvlib/tests/test_irradiance.py::test_aoi_and_aoi_projection[30-180-150-0-180--1]", "pvlib/tests/test_irradiance.py::test_aoi_and_aoi_projection[90-0-30-60-75.5224878-0.25]", "pvlib/tests/test_irradiance.py::test_aoi_and_aoi_projection[90-0-30-170-119.4987042--0.4924038]", "pvlib/tests/test_irradiance.py::test_kt_kt_prime_factor", "pvlib/tests/test_irradiance.py::test_clearsky_index", "pvlib/tests/test_irradiance.py::test_clearness_index", "pvlib/tests/test_irradiance.py::test_clearness_index_zenith_independent"]

**Base Commit**: 0b8f24c265d76320067a5ee908a57d475cd1bb24
**Environment Setup Commit**: ef8ad2fee9840a77d14b0dfd17fc489dd85c9b91
