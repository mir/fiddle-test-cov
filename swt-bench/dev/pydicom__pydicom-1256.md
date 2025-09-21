# pydicom__pydicom-1256

**Repository**: pydicom/pydicom
**Created**: 2020-11-04T21:13:33Z
**Version**: 2.1

## Problem Statement

from_json does not correctly convert BulkDataURI's in SQ data elements
**Describe the bug**
When a DICOM object contains large data elements in SQ elements and is converted to JSON, those elements are correctly turned into BulkDataURI's. However, when the JSON is converted back to DICOM using from_json, the BulkDataURI's in SQ data elements are not converted back and warnings are thrown.

**Expected behavior**
The BulkDataURI's in SQ data elements get converted back correctly.

**Steps To Reproduce**
Take the `waveform_ecg.dcm` in the test data, convert it to JSON, and then convert the JSON to DICOM

**Your environment**
module       | version
------       | -------
platform     | macOS-10.15.7-x86_64-i386-64bit
Python       | 3.8.2 (v3.8.2:7b3ab5921f, Feb 24 2020, 17:52:18)  [Clang 6.0 (clang-600.0.57)]
pydicom      | 2.1.0
gdcm         | _module not found_
jpeg_ls      | _module not found_
numpy        | _module not found_
PIL          | _module not found_

The problem is in `jsonrep.py` at line 227. I plan on submitting a pull-request today for this.


## Patch

```diff

diff --git a/pydicom/jsonrep.py b/pydicom/jsonrep.py
--- a/pydicom/jsonrep.py
+++ b/pydicom/jsonrep.py
@@ -226,7 +226,8 @@ def get_sequence_item(self, value):
                     value_key = unique_value_keys[0]
                     elem = DataElement.from_json(
                         self.dataset_class, key, vr,
-                        val[value_key], value_key
+                        val[value_key], value_key,
+                        self.bulk_data_element_handler
                     )
                 ds.add(elem)
         return ds


```

## Test Patch

```diff
diff --git a/pydicom/tests/test_json.py b/pydicom/tests/test_json.py
--- a/pydicom/tests/test_json.py
+++ b/pydicom/tests/test_json.py
@@ -354,3 +354,25 @@ def bulk_data_reader(tag, vr, value):
         ds = Dataset().from_json(json.dumps(json_data), bulk_data_reader)
 
         assert b'xyzzy' == ds[0x00091002].value
+
+    def test_bulk_data_reader_is_called_within_SQ(self):
+        def bulk_data_reader(_):
+            return b'xyzzy'
+
+        json_data = {
+            "003a0200": {
+                "vr": "SQ", 
+                "Value": [
+                    {
+                        "54001010": {
+                            "vr": "OW",
+                            "BulkDataURI": "https://a.dummy.url"
+                        }
+                    }
+                ]
+            }
+        }
+
+        ds = Dataset().from_json(json.dumps(json_data), bulk_data_reader)
+
+        assert b'xyzzy' == ds[0x003a0200].value[0][0x54001010].value

```

## Test Information

**Tests that should FAIL→PASS**: ["pydicom/tests/test_json.py::TestBinary::test_bulk_data_reader_is_called_within_SQ"]

**Tests that should PASS→PASS**: ["pydicom/tests/test_json.py::TestPersonName::test_json_pn_from_file", "pydicom/tests/test_json.py::TestPersonName::test_pn_components_to_json", "pydicom/tests/test_json.py::TestPersonName::test_pn_components_from_json", "pydicom/tests/test_json.py::TestPersonName::test_empty_value", "pydicom/tests/test_json.py::TestPersonName::test_multi_value_to_json", "pydicom/tests/test_json.py::TestPersonName::test_dataelem_from_json", "pydicom/tests/test_json.py::TestAT::test_to_json", "pydicom/tests/test_json.py::TestAT::test_from_json", "pydicom/tests/test_json.py::TestAT::test_invalid_value_in_json", "pydicom/tests/test_json.py::TestAT::test_invalid_tag_in_json", "pydicom/tests/test_json.py::TestDataSetToJson::test_json_from_dicom_file", "pydicom/tests/test_json.py::TestDataSetToJson::test_roundtrip", "pydicom/tests/test_json.py::TestDataSetToJson::test_dataset_dumphandler", "pydicom/tests/test_json.py::TestDataSetToJson::test_dataelement_dumphandler", "pydicom/tests/test_json.py::TestDataSetToJson::test_sort_order", "pydicom/tests/test_json.py::TestSequence::test_nested_sequences", "pydicom/tests/test_json.py::TestBinary::test_inline_binary", "pydicom/tests/test_json.py::TestBinary::test_invalid_inline_binary", "pydicom/tests/test_json.py::TestBinary::test_valid_bulkdata_uri", "pydicom/tests/test_json.py::TestBinary::test_invalid_bulkdata_uri", "pydicom/tests/test_json.py::TestBinary::test_bulk_data_reader_is_called", "pydicom/tests/test_json.py::TestBinary::test_bulk_data_reader_is_called_2"]

**Base Commit**: 49a3da4a3d9c24d7e8427a25048a1c7d5c4f7724
**Environment Setup Commit**: 506ecea8f378dc687d5c504788fc78810a190b7a
