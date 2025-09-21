# marshmallow-code__marshmallow-1343

**Repository**: marshmallow-code/marshmallow
**Created**: 2019-08-13T04:36:01Z
**Version**: 2.20

## Problem Statement

[version 2.20.0] TypeError: 'NoneType' object is not subscriptable
After update from version 2.19.5 to 2.20.0 I got error for code like:

```python
from marshmallow import Schema, fields, validates


class Bar(Schema):
    value = fields.String()

    @validates('value')  # <- issue here
    def validate_value(self, value):
        pass


class Foo(Schema):
    bar = fields.Nested(Bar)


sch = Foo()

sch.validate({
    'bar': 'invalid',
})
```

```
Traceback (most recent call last):
  File "/_/bug_mschema.py", line 19, in <module>
    'bar': 'invalid',
  File "/_/env/lib/python3.7/site-packages/marshmallow/schema.py", line 628, in validate
    _, errors = self._do_load(data, many, partial=partial, postprocess=False)
  File "/_/env/lib/python3.7/site-packages/marshmallow/schema.py", line 670, in _do_load
    index_errors=self.opts.index_errors,
  File "/_/env/lib/python3.7/site-packages/marshmallow/marshalling.py", line 292, in deserialize
    index=(index if index_errors else None)
  File "/_/env/lib/python3.7/site-packages/marshmallow/marshalling.py", line 65, in call_and_store
    value = getter_func(data)
  File "/_/env/lib/python3.7/site-packages/marshmallow/marshalling.py", line 285, in <lambda>
    data
  File "/_/env/lib/python3.7/site-packages/marshmallow/fields.py", line 265, in deserialize
    output = self._deserialize(value, attr, data)
  File "/_/env/lib/python3.7/site-packages/marshmallow/fields.py", line 465, in _deserialize
    data, errors = self.schema.load(value)
  File "/_/env/lib/python3.7/site-packages/marshmallow/schema.py", line 588, in load
    result, errors = self._do_load(data, many, partial=partial, postprocess=True)
  File "/_/env/lib/python3.7/site-packages/marshmallow/schema.py", line 674, in _do_load
    self._invoke_field_validators(unmarshal, data=result, many=many)
  File "/_/env/lib/python3.7/site-packages/marshmallow/schema.py", line 894, in _invoke_field_validators
    value = data[field_obj.attribute or field_name]
TypeError: 'NoneType' object is not subscriptable
```


## Hints

Thanks for reporting. I was able to reproduce this on 2.20.0. This is likely a regression from https://github.com/marshmallow-code/marshmallow/pull/1323 . I don't have time to look into it now. Would appreciate a PR.

## Patch

```diff

diff --git a/src/marshmallow/schema.py b/src/marshmallow/schema.py
--- a/src/marshmallow/schema.py
+++ b/src/marshmallow/schema.py
@@ -877,7 +877,7 @@ def _invoke_field_validators(self, unmarshal, data, many):
                 for idx, item in enumerate(data):
                     try:
                         value = item[field_obj.attribute or field_name]
-                    except KeyError:
+                    except (KeyError, TypeError):
                         pass
                     else:
                         validated_value = unmarshal.call_and_store(
@@ -892,7 +892,7 @@ def _invoke_field_validators(self, unmarshal, data, many):
             else:
                 try:
                     value = data[field_obj.attribute or field_name]
-                except KeyError:
+                except (KeyError, TypeError):
                     pass
                 else:
                     validated_value = unmarshal.call_and_store(


```

## Test Patch

```diff
diff --git a/tests/test_marshalling.py b/tests/test_marshalling.py
--- a/tests/test_marshalling.py
+++ b/tests/test_marshalling.py
@@ -2,7 +2,7 @@
 
 import pytest
 
-from marshmallow import fields, Schema
+from marshmallow import fields, Schema, validates
 from marshmallow.marshalling import Marshaller, Unmarshaller, missing
 from marshmallow.exceptions import ValidationError
 
@@ -283,3 +283,24 @@ class TestSchema(Schema):
 
             assert result is None
             assert excinfo.value.messages == {'foo': {'_schema': ['Invalid input type.']}}
+
+    # Regression test for https://github.com/marshmallow-code/marshmallow/issues/1342
+    def test_deserialize_wrong_nested_type_with_validates_method(self, unmarshal):
+        class TestSchema(Schema):
+            value = fields.String()
+
+            @validates('value')
+            def validate_value(self, value):
+                pass
+
+        data = {
+            'foo': 'not what we need'
+        }
+        fields_dict = {
+            'foo': fields.Nested(TestSchema, required=True)
+        }
+        with pytest.raises(ValidationError) as excinfo:
+            result = unmarshal.deserialize(data, fields_dict)
+
+            assert result is None
+            assert excinfo.value.messages == {'foo': {'_schema': ['Invalid input type.']}}

```

## Test Information

**Tests that should FAIL→PASS**: ["tests/test_marshalling.py::TestUnmarshaller::test_deserialize_wrong_nested_type_with_validates_method"]

**Tests that should PASS→PASS**: ["tests/test_marshalling.py::test_missing_is_falsy", "tests/test_marshalling.py::TestMarshaller::test_prefix", "tests/test_marshalling.py::TestMarshaller::test_marshalling_generator", "tests/test_marshalling.py::TestMarshaller::test_default_to_missing", "tests/test_marshalling.py::TestMarshaller::test_serialize_fields_with_load_only_param", "tests/test_marshalling.py::TestMarshaller::test_missing_data_are_skipped", "tests/test_marshalling.py::TestMarshaller::test_serialize_with_load_only_doesnt_validate", "tests/test_marshalling.py::TestMarshaller::test_serialize_fields_with_dump_to_param", "tests/test_marshalling.py::TestMarshaller::test_serialize_fields_with_dump_to_and_prefix_params", "tests/test_marshalling.py::TestMarshaller::test_stores_indices_of_errors_when_many_equals_true", "tests/test_marshalling.py::TestMarshaller::test_doesnt_store_errors_when_index_errors_equals_false", "tests/test_marshalling.py::TestUnmarshaller::test_extra_data_is_ignored", "tests/test_marshalling.py::TestUnmarshaller::test_stores_errors", "tests/test_marshalling.py::TestUnmarshaller::test_stores_indices_of_errors_when_many_equals_true", "tests/test_marshalling.py::TestUnmarshaller::test_doesnt_store_errors_when_index_errors_equals_false", "tests/test_marshalling.py::TestUnmarshaller::test_deserialize", "tests/test_marshalling.py::TestUnmarshaller::test_extra_fields", "tests/test_marshalling.py::TestUnmarshaller::test_deserialize_many", "tests/test_marshalling.py::TestUnmarshaller::test_deserialize_stores_errors", "tests/test_marshalling.py::TestUnmarshaller::test_deserialize_fields_with_attribute_param", "tests/test_marshalling.py::TestUnmarshaller::test_deserialize_fields_with_load_from_param", "tests/test_marshalling.py::TestUnmarshaller::test_deserialize_fields_with_dump_only_param", "tests/test_marshalling.py::TestUnmarshaller::test_deserialize_wrong_type_root_data", "tests/test_marshalling.py::TestUnmarshaller::test_deserialize_wrong_type_nested_data"]

**Base Commit**: 2be2d83a1a9a6d3d9b85804f3ab545cecc409bb0
**Environment Setup Commit**: 7015fc4333a2f32cd58c3465296e834acd4496ff
