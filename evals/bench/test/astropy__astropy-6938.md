# astropy__astropy-6938

**Repository**: astropy/astropy
**Created**: 2017-12-07T00:01:14Z
**Version**: 1.3

## Problem Statement

Possible bug in io.fits related to D exponents
I came across the following code in ``fitsrec.py``:

```python
        # Replace exponent separator in floating point numbers
        if 'D' in format:
            output_field.replace(encode_ascii('E'), encode_ascii('D'))
```

I think this may be incorrect because as far as I can tell ``replace`` is not an in-place operation for ``chararray`` (it returns a copy). Commenting out this code doesn't cause any tests to fail so I think this code isn't being tested anyway.


## Hints

It is tested with `astropy/io/fits/tests/test_checksum.py:test_ascii_table_data` but indeed the operation is not inplace and it does not fail. Using 'D' is probably better, but since #5362 (I had vague memory about something like this ^^, see also #5353) anyway 'D' and 'E' are read as double, so I think there is not difference on Astropy side.

## Patch

```diff

diff --git a/astropy/io/fits/fitsrec.py b/astropy/io/fits/fitsrec.py
--- a/astropy/io/fits/fitsrec.py
+++ b/astropy/io/fits/fitsrec.py
@@ -1261,7 +1261,7 @@ def _scale_back_ascii(self, col_idx, input_field, output_field):
 
         # Replace exponent separator in floating point numbers
         if 'D' in format:
-            output_field.replace(encode_ascii('E'), encode_ascii('D'))
+            output_field[:] = output_field.replace(b'E', b'D')
 
 
 def _get_recarray_field(array, key):


```

## Test Patch

```diff
diff --git a/astropy/io/fits/tests/test_checksum.py b/astropy/io/fits/tests/test_checksum.py
--- a/astropy/io/fits/tests/test_checksum.py
+++ b/astropy/io/fits/tests/test_checksum.py
@@ -205,9 +205,9 @@ def test_ascii_table_data(self):
                 # The checksum ends up being different on Windows, possibly due
                 # to slight floating point differences
                 assert 'CHECKSUM' in hdul[1].header
-                assert hdul[1].header['CHECKSUM'] == '51IDA1G981GCA1G9'
+                assert hdul[1].header['CHECKSUM'] == '3rKFAoI94oICAoI9'
                 assert 'DATASUM' in hdul[1].header
-                assert hdul[1].header['DATASUM'] == '1948208413'
+                assert hdul[1].header['DATASUM'] == '1914653725'
 
     def test_compressed_image_data(self):
         with fits.open(self.data('comp.fits')) as h1:
diff --git a/astropy/io/fits/tests/test_table.py b/astropy/io/fits/tests/test_table.py
--- a/astropy/io/fits/tests/test_table.py
+++ b/astropy/io/fits/tests/test_table.py
@@ -298,6 +298,19 @@ def test_ascii_table(self):
         hdul = fits.open(self.temp('toto.fits'))
         assert comparerecords(hdu.data, hdul[1].data)
         hdul.close()
+
+        # Test Scaling
+
+        r1 = np.array([11., 12.])
+        c2 = fits.Column(name='def', format='D', array=r1, bscale=2.3,
+                         bzero=0.6)
+        hdu = fits.TableHDU.from_columns([c2])
+        hdu.writeto(self.temp('toto.fits'), overwrite=True)
+        with open(self.temp('toto.fits')) as f:
+            assert '4.95652173913043548D+00' in f.read()
+        with fits.open(self.temp('toto.fits')) as hdul:
+            assert comparerecords(hdu.data, hdul[1].data)
+
         a.close()
 
     def test_endianness(self):

```

## Test Information

**Tests that should FAIL→PASS**: ["astropy/io/fits/tests/test_checksum.py::TestChecksumFunctions::test_ascii_table_data", "astropy/io/fits/tests/test_table.py::TestTableFunctions::test_ascii_table"]

**Tests that should PASS→PASS**: ["astropy/io/fits/tests/test_checksum.py::TestChecksumFunctions::test_sample_file", "astropy/io/fits/tests/test_checksum.py::TestChecksumFunctions::test_image_create", "astropy/io/fits/tests/test_checksum.py::TestChecksumFunctions::test_scaled_data", "astropy/io/fits/tests/test_checksum.py::TestChecksumFunctions::test_scaled_data_auto_rescale", "astropy/io/fits/tests/test_checksum.py::TestChecksumFunctions::test_uint16_data", "astropy/io/fits/tests/test_checksum.py::TestChecksumFunctions::test_groups_hdu_data", "astropy/io/fits/tests/test_checksum.py::TestChecksumFunctions::test_open_with_no_keywords", "astropy/io/fits/tests/test_checksum.py::TestChecksumFunctions::test_writeto_convenience", "astropy/io/fits/tests/test_checksum.py::TestChecksumFunctions::test_hdu_writeto", "astropy/io/fits/tests/test_checksum.py::TestChecksumFunctions::test_datasum_only", "astropy/io/fits/tests/test_table.py::test_regression_scalar_indexing"]

**Base Commit**: c76af9ed6bb89bfba45b9f5bc1e635188278e2fa
**Environment Setup Commit**: 848c8fa21332abd66b44efe3cb48b72377fb32cc
