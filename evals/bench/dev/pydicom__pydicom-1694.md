# pydicom__pydicom-1694

**Repository**: pydicom/pydicom
**Created**: 2022-09-20T18:52:53Z
**Version**: 2.3

## Problem Statement

Dataset.to_json_dict can still generate exceptions when suppress_invalid_tags=True
**Describe the bug**
I'm using `Dataset.to_json_dict(suppress_invalid_tags=True)` and can live with losing invalid tags.  Unfortunately, I can still trigger an exception with something like  `2.0` in an `IS` field.

**Expected behavior**
to_json_dict shouldn't throw an error about an invalid tag when `suppress_invalid_tags` is enabled.

My thought was simply to move the `data_element = self[key]` into the try/catch block that's right after it.

**Steps To Reproduce**

Traceback:
```
  File "dicom.py", line 143, in create_dict
    json_ds = ds.to_json_dict(suppress_invalid_tags=True)
  File "/usr/lib/python3/dist-packages/pydicom/dataset.py", line 2495, in to_json_dict
    data_element = self[key]
  File "/usr/lib/python3/dist-packages/pydicom/dataset.py", line 939, in __getitem__
    self[tag] = DataElement_from_raw(elem, character_set, self)
  File "/usr/lib/python3/dist-packages/pydicom/dataelem.py", line 859, in DataElement_from_raw
    value = convert_value(vr, raw, encoding)
  File "/usr/lib/python3/dist-packages/pydicom/values.py", line 771, in convert_value
    return converter(byte_string, is_little_endian, num_format)
  File "/usr/lib/python3/dist-packages/pydicom/values.py", line 348, in convert_IS_string
    return MultiString(num_string, valtype=pydicom.valuerep.IS)
  File "/usr/lib/python3/dist-packages/pydicom/valuerep.py", line 1213, in MultiString
    return valtype(splitup[0])
  File "/usr/lib/python3/dist-packages/pydicom/valuerep.py", line 1131, in __new__
    raise TypeError("Could not convert value to integer without loss")
TypeError: Could not convert value to integer without loss
```

**Your environment**
python 3.7, pydicom 2.3




## Patch

```diff

diff --git a/pydicom/dataset.py b/pydicom/dataset.py
--- a/pydicom/dataset.py
+++ b/pydicom/dataset.py
@@ -2492,8 +2492,8 @@ def to_json_dict(
         json_dataset = {}
         for key in self.keys():
             json_key = '{:08X}'.format(key)
-            data_element = self[key]
             try:
+                data_element = self[key]
                 json_dataset[json_key] = data_element.to_json_dict(
                     bulk_data_element_handler=bulk_data_element_handler,
                     bulk_data_threshold=bulk_data_threshold


```

## Test Patch

```diff
diff --git a/pydicom/tests/test_json.py b/pydicom/tests/test_json.py
--- a/pydicom/tests/test_json.py
+++ b/pydicom/tests/test_json.py
@@ -7,7 +7,7 @@
 
 from pydicom import dcmread
 from pydicom.data import get_testdata_file
-from pydicom.dataelem import DataElement
+from pydicom.dataelem import DataElement, RawDataElement
 from pydicom.dataset import Dataset
 from pydicom.tag import Tag, BaseTag
 from pydicom.valuerep import PersonName
@@ -284,7 +284,23 @@ def test_suppress_invalid_tags(self, _):
 
         ds_json = ds.to_json_dict(suppress_invalid_tags=True)
 
-        assert ds_json.get("00100010") is None
+        assert "00100010" not in ds_json
+
+    def test_suppress_invalid_tags_with_failed_dataelement(self):
+        """Test tags that raise exceptions don't if suppress_invalid_tags True.
+        """
+        ds = Dataset()
+        # we have to add a RawDataElement as creating a DataElement would
+        # already raise an exception
+        ds[0x00082128] = RawDataElement(
+            Tag(0x00082128), 'IS', 4, b'5.25', 0, True, True)
+
+        with pytest.raises(TypeError):
+            ds.to_json_dict()
+
+        ds_json = ds.to_json_dict(suppress_invalid_tags=True)
+
+        assert "00082128" not in ds_json
 
 
 class TestSequence:

```

## Test Information

**Tests that should FAIL→PASS**: ["pydicom/tests/test_json.py::TestDataSetToJson::test_suppress_invalid_tags_with_failed_dataelement"]

**Tests that should PASS→PASS**: ["pydicom/tests/test_json.py::TestPersonName::test_json_pn_from_file", "pydicom/tests/test_json.py::TestPersonName::test_pn_components_to_json", "pydicom/tests/test_json.py::TestPersonName::test_pn_components_from_json", "pydicom/tests/test_json.py::TestPersonName::test_empty_value", "pydicom/tests/test_json.py::TestPersonName::test_multi_value_to_json", "pydicom/tests/test_json.py::TestPersonName::test_dataelem_from_json", "pydicom/tests/test_json.py::TestAT::test_to_json", "pydicom/tests/test_json.py::TestAT::test_from_json", "pydicom/tests/test_json.py::TestAT::test_invalid_value_in_json", "pydicom/tests/test_json.py::TestAT::test_invalid_tag_in_json", "pydicom/tests/test_json.py::TestDataSetToJson::test_json_from_dicom_file", "pydicom/tests/test_json.py::TestDataSetToJson::test_roundtrip", "pydicom/tests/test_json.py::TestDataSetToJson::test_dataset_dumphandler", "pydicom/tests/test_json.py::TestDataSetToJson::test_dataelement_dumphandler", "pydicom/tests/test_json.py::TestDataSetToJson::test_sort_order", "pydicom/tests/test_json.py::TestDataSetToJson::test_suppress_invalid_tags", "pydicom/tests/test_json.py::TestSequence::test_nested_sequences", "pydicom/tests/test_json.py::TestBinary::test_inline_binary", "pydicom/tests/test_json.py::TestBinary::test_invalid_inline_binary", "pydicom/tests/test_json.py::TestBinary::test_valid_bulkdata_uri", "pydicom/tests/test_json.py::TestBinary::test_invalid_bulkdata_uri", "pydicom/tests/test_json.py::TestBinary::test_bulk_data_reader_is_called", "pydicom/tests/test_json.py::TestBinary::test_bulk_data_reader_is_called_2", "pydicom/tests/test_json.py::TestBinary::test_bulk_data_reader_is_called_within_SQ", "pydicom/tests/test_json.py::TestNumeric::test_numeric_values", "pydicom/tests/test_json.py::TestNumeric::test_numeric_types"]

**Base Commit**: f8cf45b6c121e5a4bf4a43f71aba3bc64af3db9c
**Environment Setup Commit**: a8be738418dee0a2b93c241fbd5e0bc82f4b8680
