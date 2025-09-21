# marshmallow-code__marshmallow-1359

**Repository**: marshmallow-code/marshmallow
**Created**: 2019-08-21T15:45:13Z
**Version**: 3.0

## Problem Statement

3.0: DateTime fields cannot be used as inner field for List or Tuple fields
Between releases 3.0.0rc8 and 3.0.0rc9, `DateTime` fields have started throwing an error when being instantiated as inner fields of container fields like `List` or `Tuple`. The snippet below works in <=3.0.0rc8 and throws the error below in >=3.0.0rc9 (and, worryingly, 3.0.0):

```python
from marshmallow import fields, Schema

class MySchema(Schema):
    times = fields.List(fields.DateTime())

s = MySchema()
```

Traceback:
```
Traceback (most recent call last):
  File "test-mm.py", line 8, in <module>
    s = MySchema()
  File "/Users/victor/.pyenv/versions/marshmallow/lib/python3.6/site-packages/marshmallow/schema.py", line 383, in __init__
    self.fields = self._init_fields()
  File "/Users/victor/.pyenv/versions/marshmallow/lib/python3.6/site-packages/marshmallow/schema.py", line 913, in _init_fields
    self._bind_field(field_name, field_obj)
  File "/Users/victor/.pyenv/versions/marshmallow/lib/python3.6/site-packages/marshmallow/schema.py", line 969, in _bind_field
    field_obj._bind_to_schema(field_name, self)
  File "/Users/victor/.pyenv/versions/marshmallow/lib/python3.6/site-packages/marshmallow/fields.py", line 636, in _bind_to_schema
    self.inner._bind_to_schema(field_name, self)
  File "/Users/victor/.pyenv/versions/marshmallow/lib/python3.6/site-packages/marshmallow/fields.py", line 1117, in _bind_to_schema
    or getattr(schema.opts, self.SCHEMA_OPTS_VAR_NAME)
AttributeError: 'List' object has no attribute 'opts'
```

It seems like it's treating the parent field as a Schema without checking that it is indeed a schema, so the `schema.opts` statement fails as fields don't have an `opts` attribute.


## Hints

Thanks for reporting. I don't think I'll have time to look into this until the weekend. Would you like to send a PR? 
I'm afraid I don't have any time either, and I don't really have enough context on the `_bind_to_schema` process to make sure I'm not breaking stuff.
OK, no problem. @lafrech Will you have a chance to look into this?
I've found the patch below to fix the minimal example above, but I'm not really sure what it's missing out on or how to test it properly:
```patch
diff --git a/src/marshmallow/fields.py b/src/marshmallow/fields.py
index 0b18e7d..700732e 100644
--- a/src/marshmallow/fields.py
+++ b/src/marshmallow/fields.py
@@ -1114,7 +1114,7 @@ class DateTime(Field):
         super()._bind_to_schema(field_name, schema)
         self.format = (
             self.format
-            or getattr(schema.opts, self.SCHEMA_OPTS_VAR_NAME)
+            or getattr(getattr(schema, "opts", None), self.SCHEMA_OPTS_VAR_NAME, None)
             or self.DEFAULT_FORMAT
         )
```
    git difftool 3.0.0rc8 3.0.0rc9 src/marshmallow/fields.py

When reworking container stuff, I changed

```py
        self.inner.parent = self
        self.inner.name = field_name
```
into

```py
        self.inner._bind_to_schema(field_name, self)
```

AFAIR, I did this merely to avoid duplication. On second thought, I think it was the right thing to do, not only for duplication but to actually bind inner fields to the `Schema`.

Reverting this avoids the error but the inner field's `_bind_to_schema` method is not called so I'm not sure it is desirable.

I think we really mean to call that method, not only in this case but also generally.

Changing

```py
            or getattr(schema.opts, self.SCHEMA_OPTS_VAR_NAME)
```

into

```py
            or getattr(self.root.opts, self.SCHEMA_OPTS_VAR_NAME)
```

might be a better fix. Can anyone confirm (@sloria, @deckar01)?

The fix in https://github.com/marshmallow-code/marshmallow/issues/1357#issuecomment-523465528 removes the error but also the feature: `DateTime` fields buried into container fields won't respect the format set in the `Schema`.

I didn't double-check that but AFAIU, the change I mentioned above (in container stuff rework) was the right thing to do. The feature was already broken (format set in `Schema` not respected if `DateTime` field in container field) and that's just one of the issues that may arise due to the inner field not being bound to the `Schema`. But I may be wrong.
On quick glance, your analysis and fix look correct @lafrech 
Let's do that, then.

Not much time either. The first who gets the time can do it.

For the non-reg tests :

1/ a test that checks the format set in the schema is respected if the `DateTime` field is in a container field

2/ a set of tests asserting the `_bind_to_schema` method of inner fields `List`, `Dict`, `Tuple` is called from container fields (we can use `DateTime` with the same test case for that)

Perhaps 1/ is useless if 2/ is done.

## Patch

```diff

diff --git a/src/marshmallow/fields.py b/src/marshmallow/fields.py
--- a/src/marshmallow/fields.py
+++ b/src/marshmallow/fields.py
@@ -1114,7 +1114,7 @@ def _bind_to_schema(self, field_name, schema):
         super()._bind_to_schema(field_name, schema)
         self.format = (
             self.format
-            or getattr(schema.opts, self.SCHEMA_OPTS_VAR_NAME)
+            or getattr(self.root.opts, self.SCHEMA_OPTS_VAR_NAME)
             or self.DEFAULT_FORMAT
         )
 


```

## Test Patch

```diff
diff --git a/tests/test_fields.py b/tests/test_fields.py
--- a/tests/test_fields.py
+++ b/tests/test_fields.py
@@ -169,6 +169,20 @@ class OtherSchema(MySchema):
         assert schema2.fields["foo"].key_field.root == schema2
         assert schema2.fields["foo"].value_field.root == schema2
 
+    # Regression test for https://github.com/marshmallow-code/marshmallow/issues/1357
+    def test_datetime_list_inner_format(self, schema):
+        class MySchema(Schema):
+            foo = fields.List(fields.DateTime())
+            bar = fields.Tuple((fields.DateTime(),))
+
+            class Meta:
+                datetimeformat = "iso8601"
+                dateformat = "iso8601"
+
+        schema = MySchema()
+        assert schema.fields["foo"].inner.format == "iso8601"
+        assert schema.fields["bar"].tuple_fields[0].format == "iso8601"
+
 
 class TestMetadata:
     @pytest.mark.parametrize("FieldClass", ALL_FIELDS)

```

## Test Information

**Tests that should FAIL→PASS**: ["tests/test_fields.py::TestParentAndName::test_datetime_list_inner_format"]

**Tests that should PASS→PASS**: ["tests/test_fields.py::test_field_aliases[Integer-Integer]", "tests/test_fields.py::test_field_aliases[String-String]", "tests/test_fields.py::test_field_aliases[Boolean-Boolean]", "tests/test_fields.py::test_field_aliases[Url-Url]", "tests/test_fields.py::TestField::test_repr", "tests/test_fields.py::TestField::test_error_raised_if_uncallable_validator_passed", "tests/test_fields.py::TestField::test_error_raised_if_missing_is_set_on_required_field", "tests/test_fields.py::TestField::test_custom_field_receives_attr_and_obj", "tests/test_fields.py::TestField::test_custom_field_receives_data_key_if_set", "tests/test_fields.py::TestField::test_custom_field_follows_data_key_if_set", "tests/test_fields.py::TestParentAndName::test_simple_field_parent_and_name", "tests/test_fields.py::TestParentAndName::test_unbound_field_root_returns_none", "tests/test_fields.py::TestParentAndName::test_list_field_inner_parent_and_name", "tests/test_fields.py::TestParentAndName::test_tuple_field_inner_parent_and_name", "tests/test_fields.py::TestParentAndName::test_mapping_field_inner_parent_and_name", "tests/test_fields.py::TestParentAndName::test_simple_field_root", "tests/test_fields.py::TestParentAndName::test_list_field_inner_root", "tests/test_fields.py::TestParentAndName::test_tuple_field_inner_root", "tests/test_fields.py::TestParentAndName::test_list_root_inheritance", "tests/test_fields.py::TestParentAndName::test_dict_root_inheritance", "tests/test_fields.py::TestMetadata::test_extra_metadata_may_be_added_to_field[String]", "tests/test_fields.py::TestMetadata::test_extra_metadata_may_be_added_to_field[Integer]", "tests/test_fields.py::TestMetadata::test_extra_metadata_may_be_added_to_field[Boolean]", "tests/test_fields.py::TestMetadata::test_extra_metadata_may_be_added_to_field[Float]", "tests/test_fields.py::TestMetadata::test_extra_metadata_may_be_added_to_field[Number]", "tests/test_fields.py::TestMetadata::test_extra_metadata_may_be_added_to_field[DateTime]", "tests/test_fields.py::TestMetadata::test_extra_metadata_may_be_added_to_field[Time]", "tests/test_fields.py::TestMetadata::test_extra_metadata_may_be_added_to_field[Date]", "tests/test_fields.py::TestMetadata::test_extra_metadata_may_be_added_to_field[TimeDelta]", "tests/test_fields.py::TestMetadata::test_extra_metadata_may_be_added_to_field[Dict]", "tests/test_fields.py::TestMetadata::test_extra_metadata_may_be_added_to_field[Url]", "tests/test_fields.py::TestMetadata::test_extra_metadata_may_be_added_to_field[Email]", "tests/test_fields.py::TestMetadata::test_extra_metadata_may_be_added_to_field[UUID]", "tests/test_fields.py::TestMetadata::test_extra_metadata_may_be_added_to_field[Decimal]", "tests/test_fields.py::TestErrorMessages::test_default_error_messages_get_merged_with_parent_error_messages_cstm_msg", "tests/test_fields.py::TestErrorMessages::test_default_error_messages_get_merged_with_parent_error_messages", "tests/test_fields.py::TestErrorMessages::test_make_error[required-Missing", "tests/test_fields.py::TestErrorMessages::test_make_error[null-Field", "tests/test_fields.py::TestErrorMessages::test_make_error[custom-Custom", "tests/test_fields.py::TestErrorMessages::test_make_error[validator_failed-Invalid", "tests/test_fields.py::TestErrorMessages::test_fail[required-Missing", "tests/test_fields.py::TestErrorMessages::test_fail[null-Field", "tests/test_fields.py::TestErrorMessages::test_fail[custom-Custom", "tests/test_fields.py::TestErrorMessages::test_fail[validator_failed-Invalid", "tests/test_fields.py::TestErrorMessages::test_make_error_key_doesnt_exist", "tests/test_fields.py::TestNestedField::test_nested_only_and_exclude_as_string[only]", "tests/test_fields.py::TestNestedField::test_nested_only_and_exclude_as_string[exclude]", "tests/test_fields.py::TestNestedField::test_nested_unknown_override[None-exclude]", "tests/test_fields.py::TestNestedField::test_nested_unknown_override[None-include]", "tests/test_fields.py::TestNestedField::test_nested_unknown_override[None-raise]", "tests/test_fields.py::TestNestedField::test_nested_unknown_override[exclude-exclude]", "tests/test_fields.py::TestNestedField::test_nested_unknown_override[exclude-include]", "tests/test_fields.py::TestNestedField::test_nested_unknown_override[exclude-raise]", "tests/test_fields.py::TestNestedField::test_nested_unknown_override[include-exclude]", "tests/test_fields.py::TestNestedField::test_nested_unknown_override[include-include]", "tests/test_fields.py::TestNestedField::test_nested_unknown_override[include-raise]", "tests/test_fields.py::TestNestedField::test_nested_unknown_override[raise-exclude]", "tests/test_fields.py::TestNestedField::test_nested_unknown_override[raise-include]", "tests/test_fields.py::TestNestedField::test_nested_unknown_override[raise-raise]", "tests/test_fields.py::TestListNested::test_list_nested_only_exclude_dump_only_load_only_propagated_to_nested[only]", "tests/test_fields.py::TestListNested::test_list_nested_only_exclude_dump_only_load_only_propagated_to_nested[exclude]", "tests/test_fields.py::TestListNested::test_list_nested_only_exclude_dump_only_load_only_propagated_to_nested[dump_only]", "tests/test_fields.py::TestListNested::test_list_nested_only_exclude_dump_only_load_only_propagated_to_nested[load_only]", "tests/test_fields.py::TestListNested::test_list_nested_only_and_exclude_merged_with_nested[only-expected0]", "tests/test_fields.py::TestListNested::test_list_nested_only_and_exclude_merged_with_nested[exclude-expected1]", "tests/test_fields.py::TestListNested::test_list_nested_partial_propagated_to_nested", "tests/test_fields.py::TestTupleNested::test_tuple_nested_only_exclude_dump_only_load_only_propagated_to_nested[dump_only]", "tests/test_fields.py::TestTupleNested::test_tuple_nested_only_exclude_dump_only_load_only_propagated_to_nested[load_only]", "tests/test_fields.py::TestTupleNested::test_tuple_nested_partial_propagated_to_nested", "tests/test_fields.py::TestDictNested::test_dict_nested_only_exclude_dump_only_load_only_propagated_to_nested[only]", "tests/test_fields.py::TestDictNested::test_dict_nested_only_exclude_dump_only_load_only_propagated_to_nested[exclude]", "tests/test_fields.py::TestDictNested::test_dict_nested_only_exclude_dump_only_load_only_propagated_to_nested[dump_only]", "tests/test_fields.py::TestDictNested::test_dict_nested_only_exclude_dump_only_load_only_propagated_to_nested[load_only]", "tests/test_fields.py::TestDictNested::test_dict_nested_only_and_exclude_merged_with_nested[only-expected0]", "tests/test_fields.py::TestDictNested::test_dict_nested_only_and_exclude_merged_with_nested[exclude-expected1]", "tests/test_fields.py::TestDictNested::test_dict_nested_partial_propagated_to_nested"]

**Base Commit**: b40a0f4e33823e6d0f341f7e8684e359a99060d1
**Environment Setup Commit**: 8b3a32614fd4a74e93e9a63a042e74c1fea34466
