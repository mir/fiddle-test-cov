# pvlib__pvlib-python-1707

**Repository**: pvlib/pvlib-python
**Created**: 2023-03-24T10:46:42Z
**Version**: 0.9

## Problem Statement

regression: iam.physical returns nan for aoi > 90° when n = 1
**Describe the bug**
For pvlib==0.9.5, when n = 1 (no reflection) and aoi > 90°, we get nan as result.

**To Reproduce**
```python
import pvlib
pvlib.iam.physical(aoi=100, n=1)
```
returns `nan`.

**Expected behavior**
The result should be `0`, as it was for pvlib <= 0.9.4.


**Versions:**
 - ``pvlib.__version__``: '0.9.5'
 - ``pandas.__version__``:  '1.5.3'
 - python: 3.10.4



## Patch

```diff

diff --git a/pvlib/iam.py b/pvlib/iam.py
--- a/pvlib/iam.py
+++ b/pvlib/iam.py
@@ -175,8 +175,12 @@ def physical(aoi, n=1.526, K=4.0, L=0.002, *, n_ar=None):
     n2costheta2 = n2 * costheta
 
     # reflectance of s-, p-polarized, and normal light by the first interface
-    rho12_s = ((n1costheta1 - n2costheta2) / (n1costheta1 + n2costheta2)) ** 2
-    rho12_p = ((n1costheta2 - n2costheta1) / (n1costheta2 + n2costheta1)) ** 2
+    with np.errstate(divide='ignore', invalid='ignore'):
+        rho12_s = \
+            ((n1costheta1 - n2costheta2) / (n1costheta1 + n2costheta2)) ** 2
+        rho12_p = \
+            ((n1costheta2 - n2costheta1) / (n1costheta2 + n2costheta1)) ** 2
+
     rho12_0 = ((n1 - n2) / (n1 + n2)) ** 2
 
     # transmittance through the first interface
@@ -208,13 +212,22 @@ def physical(aoi, n=1.526, K=4.0, L=0.002, *, n_ar=None):
         tau_0 *= (1 - rho23_0) / (1 - rho23_0 * rho12_0)
 
     # transmittance after absorption in the glass
-    tau_s *= np.exp(-K * L / costheta)
-    tau_p *= np.exp(-K * L / costheta)
+    with np.errstate(divide='ignore', invalid='ignore'):
+        tau_s *= np.exp(-K * L / costheta)
+        tau_p *= np.exp(-K * L / costheta)
+
     tau_0 *= np.exp(-K * L)
 
     # incidence angle modifier
     iam = (tau_s + tau_p) / 2 / tau_0
 
+    # for light coming from behind the plane, none can enter the module
+    # when n2 > 1, this is already the case
+    if np.isclose(n2, 1).any():
+        iam = np.where(aoi >= 90, 0, iam)
+        if isinstance(aoi, pd.Series):
+            iam = pd.Series(iam, index=aoi.index)
+
     return iam
 
 


```

## Test Patch

```diff
diff --git a/pvlib/tests/test_iam.py b/pvlib/tests/test_iam.py
--- a/pvlib/tests/test_iam.py
+++ b/pvlib/tests/test_iam.py
@@ -51,6 +51,18 @@ def test_physical():
     assert_series_equal(iam, expected)
 
 
+def test_physical_n1_L0():
+    aoi = np.array([0, 22.5, 45, 67.5, 90, 100, np.nan])
+    expected = np.array([1, 1, 1, 1, 0, 0, np.nan])
+    iam = _iam.physical(aoi, n=1, L=0)
+    assert_allclose(iam, expected, equal_nan=True)
+
+    aoi = pd.Series(aoi)
+    expected = pd.Series(expected)
+    iam = _iam.physical(aoi, n=1, L=0)
+    assert_series_equal(iam, expected)
+
+
 def test_physical_ar():
     aoi = np.array([0, 22.5, 45, 67.5, 90, 100, np.nan])
     expected = np.array([1, 0.99944171, 0.9917463, 0.91506158, 0, 0, np.nan])

```

## Test Information

**Tests that should FAIL→PASS**: ["pvlib/tests/test_iam.py::test_physical_n1_L0"]

**Tests that should PASS→PASS**: ["pvlib/tests/test_iam.py::test_ashrae", "pvlib/tests/test_iam.py::test_ashrae_scalar", "pvlib/tests/test_iam.py::test_physical", "pvlib/tests/test_iam.py::test_physical_ar", "pvlib/tests/test_iam.py::test_physical_noar", "pvlib/tests/test_iam.py::test_physical_scalar", "pvlib/tests/test_iam.py::test_martin_ruiz", "pvlib/tests/test_iam.py::test_martin_ruiz_exception", "pvlib/tests/test_iam.py::test_martin_ruiz_diffuse", "pvlib/tests/test_iam.py::test_iam_interp", "pvlib/tests/test_iam.py::test_sapm[45-0.9975036250000002]", "pvlib/tests/test_iam.py::test_sapm[aoi1-expected1]", "pvlib/tests/test_iam.py::test_sapm[aoi2-expected2]", "pvlib/tests/test_iam.py::test_sapm_limits", "pvlib/tests/test_iam.py::test_marion_diffuse_model", "pvlib/tests/test_iam.py::test_marion_diffuse_kwargs", "pvlib/tests/test_iam.py::test_marion_diffuse_invalid", "pvlib/tests/test_iam.py::test_marion_integrate_scalar[sky-180-0.9596085829811408]", "pvlib/tests/test_iam.py::test_marion_integrate_scalar[horizon-1800-0.8329070417832541]", "pvlib/tests/test_iam.py::test_marion_integrate_scalar[ground-180-0.719823559106309]", "pvlib/tests/test_iam.py::test_marion_integrate_list[sky-180-expected0]", "pvlib/tests/test_iam.py::test_marion_integrate_list[horizon-1800-expected1]", "pvlib/tests/test_iam.py::test_marion_integrate_list[ground-180-expected2]", "pvlib/tests/test_iam.py::test_marion_integrate_series[sky-180-expected0]", "pvlib/tests/test_iam.py::test_marion_integrate_series[horizon-1800-expected1]", "pvlib/tests/test_iam.py::test_marion_integrate_series[ground-180-expected2]", "pvlib/tests/test_iam.py::test_marion_integrate_ground_flat", "pvlib/tests/test_iam.py::test_marion_integrate_invalid", "pvlib/tests/test_iam.py::test_schlick", "pvlib/tests/test_iam.py::test_schlick_diffuse"]

**Base Commit**: 40e9e978c170bdde4eeee1547729417665dbc34c
**Environment Setup Commit**: 6072e0982c3c0236f532ddfa48fbf461180d834e
