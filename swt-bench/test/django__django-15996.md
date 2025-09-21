# django__django-15996

**Repository**: django/django
**Created**: 2022-08-25T04:49:14Z
**Version**: 4.2

## Problem Statement

Support for serialization of combination of Enum flags.
Description
	 
		(last modified by Willem Van Onsem)
	 
If we work with a field:
regex_flags = models.IntegerField(default=re.UNICODE | re.IGNORECASE)
This is turned into a migration with:
default=re.RegexFlag[None]
This is due to the fact that the EnumSerializer aims to work with the .name of the item, but if there is no single item for the given value, then there is no such name.
In that case, we can use enum._decompose to obtain a list of names, and create an expression to create the enum value by "ORing" the items together.


## Hints

patch of the EnumSerializer

## Patch

```diff

diff --git a/django/db/migrations/serializer.py b/django/db/migrations/serializer.py
--- a/django/db/migrations/serializer.py
+++ b/django/db/migrations/serializer.py
@@ -16,7 +16,7 @@
 from django.db.migrations.operations.base import Operation
 from django.db.migrations.utils import COMPILED_REGEX_TYPE, RegexObject
 from django.utils.functional import LazyObject, Promise
-from django.utils.version import get_docs_version
+from django.utils.version import PY311, get_docs_version
 
 
 class BaseSerializer:
@@ -125,8 +125,21 @@ class EnumSerializer(BaseSerializer):
     def serialize(self):
         enum_class = self.value.__class__
         module = enum_class.__module__
+        if issubclass(enum_class, enum.Flag):
+            if PY311:
+                members = list(self.value)
+            else:
+                members, _ = enum._decompose(enum_class, self.value)
+                members = reversed(members)
+        else:
+            members = (self.value,)
         return (
-            "%s.%s[%r]" % (module, enum_class.__qualname__, self.value.name),
+            " | ".join(
+                [
+                    f"{module}.{enum_class.__qualname__}[{item.name!r}]"
+                    for item in members
+                ]
+            ),
             {"import %s" % module},
         )
 


```

## Test Patch

```diff
diff --git a/tests/migrations/test_writer.py b/tests/migrations/test_writer.py
--- a/tests/migrations/test_writer.py
+++ b/tests/migrations/test_writer.py
@@ -413,6 +413,14 @@ def test_serialize_enum_flags(self):
             "(2, migrations.test_writer.IntFlagEnum['B'])], "
             "default=migrations.test_writer.IntFlagEnum['A'])",
         )
+        self.assertSerializedResultEqual(
+            IntFlagEnum.A | IntFlagEnum.B,
+            (
+                "migrations.test_writer.IntFlagEnum['A'] | "
+                "migrations.test_writer.IntFlagEnum['B']",
+                {"import migrations.test_writer"},
+            ),
+        )
 
     def test_serialize_choices(self):
         class TextChoices(models.TextChoices):

```

## Test Information

**Tests that should FAIL→PASS**: ["test_serialize_enum_flags (migrations.test_writer.WriterTests)"]

**Tests that should PASS→PASS**: ["test_args_kwargs_signature (migrations.test_writer.OperationWriterTests)", "test_args_signature (migrations.test_writer.OperationWriterTests)", "test_empty_signature (migrations.test_writer.OperationWriterTests)", "test_expand_args_signature (migrations.test_writer.OperationWriterTests)", "test_kwargs_signature (migrations.test_writer.OperationWriterTests)", "test_multiline_args_signature (migrations.test_writer.OperationWriterTests)", "test_nested_args_signature (migrations.test_writer.OperationWriterTests)", "test_nested_operation_expand_args_signature (migrations.test_writer.OperationWriterTests)", "test_custom_operation (migrations.test_writer.WriterTests)", "test_deconstruct_class_arguments (migrations.test_writer.WriterTests)", "Test comments at top of file.", "test_migration_path (migrations.test_writer.WriterTests)", "django.db.models shouldn't be imported if unused.", "test_register_non_serializer (migrations.test_writer.WriterTests)", "test_register_serializer (migrations.test_writer.WriterTests)", "test_serialize_builtin_types (migrations.test_writer.WriterTests)", "test_serialize_builtins (migrations.test_writer.WriterTests)", "test_serialize_choices (migrations.test_writer.WriterTests)", "Ticket #22943: Test serialization of class-based validators, including", "test_serialize_collections (migrations.test_writer.WriterTests)", "Make sure compiled regex can be serialized.", "test_serialize_complex_func_index (migrations.test_writer.WriterTests)", "test_serialize_constants (migrations.test_writer.WriterTests)", "test_serialize_datetime (migrations.test_writer.WriterTests)", "Ticket #22679: makemigrations generates invalid code for (an empty", "test_serialize_enums (migrations.test_writer.WriterTests)", "test_serialize_fields (migrations.test_writer.WriterTests)", "test_serialize_frozensets (migrations.test_writer.WriterTests)", "test_serialize_functions (migrations.test_writer.WriterTests)", "test_serialize_functools_partial (migrations.test_writer.WriterTests)", "test_serialize_functools_partialmethod (migrations.test_writer.WriterTests)", "test_serialize_iterators (migrations.test_writer.WriterTests)", "test_serialize_lazy_objects (migrations.test_writer.WriterTests)", "A reference in a local scope can't be serialized.", "test_serialize_managers (migrations.test_writer.WriterTests)", "test_serialize_multiline_strings (migrations.test_writer.WriterTests)", "test_serialize_nested_class (migrations.test_writer.WriterTests)", "test_serialize_numbers (migrations.test_writer.WriterTests)", "test_serialize_path_like (migrations.test_writer.WriterTests)", "test_serialize_pathlib (migrations.test_writer.WriterTests)", "test_serialize_range (migrations.test_writer.WriterTests)", "test_serialize_set (migrations.test_writer.WriterTests)", "test_serialize_settings (migrations.test_writer.WriterTests)", "test_serialize_strings (migrations.test_writer.WriterTests)", "test_serialize_timedelta (migrations.test_writer.WriterTests)", "test_serialize_type_model (migrations.test_writer.WriterTests)", "test_serialize_type_none (migrations.test_writer.WriterTests)", "An unbound method used within a class body can be serialized.", "test_serialize_uuid (migrations.test_writer.WriterTests)", "Tests serializing a simple migration.", "#24155 - Tests ordering of imports."]

**Base Commit**: b30c0081d4d8a31ab7dc7f72a4c7099af606ef29
**Environment Setup Commit**: 0fbdb9784da915fce5dcc1fe82bac9b4785749e5
