# pydicom__pydicom-1139

**Repository**: pydicom/pydicom
**Created**: 2020-06-26T11:47:17Z
**Version**: 2.0

## Problem Statement

Make PersonName3 iterable
```python
from pydicom import Dataset

ds = Dataset()
ds.PatientName = 'SomeName'

'S' in ds.PatientName
```
```
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: argument of type 'PersonName3' is not iterable
```

I'm not really sure if this is intentional or if PN elements should support `str` methods. And yes I know I can `str(ds.PatientName)` but it's a bit silly, especially when I keep having to write exceptions to my element iterators just for PN elements.


## Hints

I think it is reasonable to support at least some `str` methods (definitely `__contains__` for the example above), but there are many that don't make a lot of sense in this context though - e.g. `join`, `ljust`, `maketrans`, `splitlines` just to name a few, but I suppose each would either never be actually used or would have no effect.

I have a vague memory that one or more of the `PersonName` classes was at one time subclassed from `str`, or at least that it was discussed... does anyone remember?  Maybe it would be easier now with only Python 3 supported.
`PersonName` was derived from `str` or `unicode` in Python 2, but that caused a number of problems, which is why you switched to `PersonName3` in Python 3, I think. I agree though that it makes sense to implement `str` methods, either by implementing some of them, or generically by adding `__getattr__` that converts it to `str` and applies the attribute to that string. 

## Patch

```diff

diff --git a/pydicom/valuerep.py b/pydicom/valuerep.py
--- a/pydicom/valuerep.py
+++ b/pydicom/valuerep.py
@@ -1,6 +1,5 @@
 # Copyright 2008-2018 pydicom authors. See LICENSE file for details.
 """Special classes for DICOM value representations (VR)"""
-from copy import deepcopy
 from decimal import Decimal
 import re
 
@@ -750,6 +749,25 @@ def __ne__(self, other):
     def __str__(self):
         return '='.join(self.components).__str__()
 
+    def __next__(self):
+        # Get next character or stop iteration
+        if self._i < self._rep_len:
+            c = self._str_rep[self._i]
+            self._i += 1
+            return c
+        else:
+            raise StopIteration
+
+    def __iter__(self):
+        # Get string rep. and length, initialize index counter
+        self._str_rep = self.__str__()
+        self._rep_len = len(self._str_rep)
+        self._i = 0
+        return self
+
+    def __contains__(self, x):
+        return x in self.__str__()
+
     def __repr__(self):
         return '='.join(self.components).__repr__()
 


```

## Test Patch

```diff
diff --git a/pydicom/tests/test_valuerep.py b/pydicom/tests/test_valuerep.py
--- a/pydicom/tests/test_valuerep.py
+++ b/pydicom/tests/test_valuerep.py
@@ -427,6 +427,62 @@ def test_hash(self):
         )
         assert hash(pn1) == hash(pn2)
 
+    def test_next(self):
+        """Test that the next function works on it's own"""
+        # Test getting the first character
+        pn1 = PersonName("John^Doe^^Dr", encodings=default_encoding)
+        pn1_itr = iter(pn1)
+        assert next(pn1_itr) == "J"
+
+        # Test getting multiple characters
+        pn2 = PersonName(
+            "Yamada^Tarou=山田^太郎=やまだ^たろう", [default_encoding, "iso2022_jp"]
+        )
+        pn2_itr = iter(pn2)
+        assert next(pn2_itr) == "Y"
+        assert next(pn2_itr) == "a"
+
+        # Test getting all characters
+        pn3 = PersonName("SomeName")
+        pn3_itr = iter(pn3)
+        assert next(pn3_itr) == "S"
+        assert next(pn3_itr) == "o"
+        assert next(pn3_itr) == "m"
+        assert next(pn3_itr) == "e"
+        assert next(pn3_itr) == "N"
+        assert next(pn3_itr) == "a"
+        assert next(pn3_itr) == "m"
+        assert next(pn3_itr) == "e"
+
+        # Attempting to get next characeter should stop the iteration
+        # I.e. next can only start once
+        with pytest.raises(StopIteration):
+            next(pn3_itr)
+
+        # Test that next() doesn't work without instantiating an iterator
+        pn4 = PersonName("SomeName")
+        with pytest.raises(AttributeError):
+            next(pn4)
+
+    def test_iterator(self):
+        """Test that iterators can be corretly constructed"""
+        name_str = "John^Doe^^Dr"
+        pn1 = PersonName(name_str)
+        
+        for i, c in enumerate(pn1):
+            assert name_str[i] == c
+
+        # Ensure that multiple iterators can be created on the same variable
+        for i, c in enumerate(pn1):
+            assert name_str[i] == c
+
+    def test_contains(self):
+        """Test that characters can be check if they are within the name"""
+        pn1 = PersonName("John^Doe")
+        assert ("J" in pn1) == True
+        assert ("o" in pn1) == True
+        assert ("x" in pn1) == False
+
 
 class TestDateTime:
     """Unit tests for DA, DT, TM conversion to datetime objects"""

```

## Test Information

**Tests that should FAIL→PASS**: ["pydicom/tests/test_valuerep.py::TestPersonName::test_next", "pydicom/tests/test_valuerep.py::TestPersonName::test_iterator", "pydicom/tests/test_valuerep.py::TestPersonName::test_contains"]

**Tests that should PASS→PASS**: ["pydicom/tests/test_valuerep.py::TestTM::test_pickling", "pydicom/tests/test_valuerep.py::TestDT::test_pickling", "pydicom/tests/test_valuerep.py::TestDA::test_pickling", "pydicom/tests/test_valuerep.py::TestDS::test_empty_value", "pydicom/tests/test_valuerep.py::TestDS::test_float_values", "pydicom/tests/test_valuerep.py::TestDSfloat::test_pickling", "pydicom/tests/test_valuerep.py::TestDSfloat::test_str", "pydicom/tests/test_valuerep.py::TestDSfloat::test_repr", "pydicom/tests/test_valuerep.py::TestDSdecimal::test_pickling", "pydicom/tests/test_valuerep.py::TestDSdecimal::test_float_value", "pydicom/tests/test_valuerep.py::TestIS::test_empty_value", "pydicom/tests/test_valuerep.py::TestIS::test_valid_value", "pydicom/tests/test_valuerep.py::TestIS::test_invalid_value", "pydicom/tests/test_valuerep.py::TestIS::test_pickling", "pydicom/tests/test_valuerep.py::TestIS::test_longint", "pydicom/tests/test_valuerep.py::TestIS::test_overflow", "pydicom/tests/test_valuerep.py::TestIS::test_str", "pydicom/tests/test_valuerep.py::TestIS::test_repr", "pydicom/tests/test_valuerep.py::TestBadValueRead::test_read_bad_value_in_VR_default", "pydicom/tests/test_valuerep.py::TestBadValueRead::test_read_bad_value_in_VR_enforce_valid_value", "pydicom/tests/test_valuerep.py::TestDecimalString::test_DS_decimal_set", "pydicom/tests/test_valuerep.py::TestDecimalString::test_valid_decimal_strings", "pydicom/tests/test_valuerep.py::TestDecimalString::test_invalid_decimal_strings", "pydicom/tests/test_valuerep.py::TestPersonName::test_last_first", "pydicom/tests/test_valuerep.py::TestPersonName::test_copy", "pydicom/tests/test_valuerep.py::TestPersonName::test_three_component", "pydicom/tests/test_valuerep.py::TestPersonName::test_formatting", "pydicom/tests/test_valuerep.py::TestPersonName::test_unicode_kr", "pydicom/tests/test_valuerep.py::TestPersonName::test_unicode_jp_from_bytes", "pydicom/tests/test_valuerep.py::TestPersonName::test_unicode_jp_from_bytes_comp_delimiter", "pydicom/tests/test_valuerep.py::TestPersonName::test_unicode_jp_from_bytes_caret_delimiter", "pydicom/tests/test_valuerep.py::TestPersonName::test_unicode_jp_from_unicode", "pydicom/tests/test_valuerep.py::TestPersonName::test_not_equal", "pydicom/tests/test_valuerep.py::TestPersonName::test_encoding_carried", "pydicom/tests/test_valuerep.py::TestPersonName::test_hash", "pydicom/tests/test_valuerep.py::TestDateTime::test_date", "pydicom/tests/test_valuerep.py::TestDateTime::test_date_time", "pydicom/tests/test_valuerep.py::TestDateTime::test_time"]

**Base Commit**: b9fb05c177b685bf683f7f57b2d57374eb7d882d
**Environment Setup Commit**: 9d69811e539774f296c2f289839147e741251716
