# django__django-17087

**Repository**: django/django
**Created**: 2023-07-17T20:28:41Z
**Version**: 5.0

## Problem Statement

Class methods from nested classes cannot be used as Field.default.
Description
	 
		(last modified by Mariusz Felisiak)
	 
Given the following model:
 
class Profile(models.Model):
	class Capability(models.TextChoices):
		BASIC = ("BASIC", "Basic")
		PROFESSIONAL = ("PROFESSIONAL", "Professional")
		
		@classmethod
		def default(cls) -> list[str]:
			return [cls.BASIC]
	capabilities = ArrayField(
		models.CharField(choices=Capability.choices, max_length=30, blank=True),
		null=True,
		default=Capability.default
	)
The resulting migration contained the following:
 # ...
	 migrations.AddField(
		 model_name='profile',
		 name='capabilities',
		 field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, choices=[('BASIC', 'Basic'), ('PROFESSIONAL', 'Professional')], max_length=30), default=appname.models.Capability.default, null=True, size=None),
	 ),
 # ...
As you can see, migrations.AddField is passed as argument "default" a wrong value "appname.models.Capability.default", which leads to an error when trying to migrate. The right value should be "appname.models.Profile.Capability.default".


## Hints

Thanks for the report. It seems that FunctionTypeSerializer should use __qualname__ instead of __name__: django/db/migrations/serializer.py diff --git a/django/db/migrations/serializer.py b/django/db/migrations/serializer.py index d88cda6e20..06657ebaab 100644 a b class FunctionTypeSerializer(BaseSerializer): 168168 ): 169169 klass = self.value.__self__ 170170 module = klass.__module__ 171 return "%s.%s.%s" % (module, klass.__name__, self.value.__name__), { 171 return "%s.%s.%s" % (module, klass.__qualname__, self.value.__name__), { 172172 "import %s" % module 173173 } 174174 # Further error checking Would you like to prepare a patch? (regression test is required)
Also to nitpick the terminology: Capability is a nested class, not a subclass. (fyi for anyone preparing tests/commit message)
Replying to David Sanders: Also to nitpick the terminology: Capability is a nested class, not a subclass. (fyi for anyone preparing tests/commit message) You're right, that was inaccurate. Thanks for having fixed the title
Replying to Mariusz Felisiak: Thanks for the report. It seems that FunctionTypeSerializer should use __qualname__ instead of __name__: django/db/migrations/serializer.py diff --git a/django/db/migrations/serializer.py b/django/db/migrations/serializer.py index d88cda6e20..06657ebaab 100644 a b class FunctionTypeSerializer(BaseSerializer): 168168 ): 169169 klass = self.value.__self__ 170170 module = klass.__module__ 171 return "%s.%s.%s" % (module, klass.__name__, self.value.__name__), { 171 return "%s.%s.%s" % (module, klass.__qualname__, self.value.__name__), { 172172 "import %s" % module 173173 } 174174 # Further error checking Would you like to prepare a patch? (regression test is required) I would be very happy to prepare a patch, i will do my best to write a test that's coherent with the current suite
I would be very happy to prepare a patch, i will do my best to write a test that's coherent with the current suite You can check tests in tests.migrations.test_writer.WriterTests, e.g. test_serialize_nested_class().

## Patch

```diff

diff --git a/django/db/migrations/serializer.py b/django/db/migrations/serializer.py
--- a/django/db/migrations/serializer.py
+++ b/django/db/migrations/serializer.py
@@ -168,7 +168,7 @@ def serialize(self):
         ):
             klass = self.value.__self__
             module = klass.__module__
-            return "%s.%s.%s" % (module, klass.__name__, self.value.__name__), {
+            return "%s.%s.%s" % (module, klass.__qualname__, self.value.__name__), {
                 "import %s" % module
             }
         # Further error checking


```

## Test Patch

```diff
diff --git a/tests/migrations/test_writer.py b/tests/migrations/test_writer.py
--- a/tests/migrations/test_writer.py
+++ b/tests/migrations/test_writer.py
@@ -211,6 +211,10 @@ class NestedChoices(models.TextChoices):
         X = "X", "X value"
         Y = "Y", "Y value"
 
+        @classmethod
+        def method(cls):
+            return cls.X
+
     def safe_exec(self, string, value=None):
         d = {}
         try:
@@ -468,6 +472,15 @@ def test_serialize_nested_class(self):
                     ),
                 )
 
+    def test_serialize_nested_class_method(self):
+        self.assertSerializedResultEqual(
+            self.NestedChoices.method,
+            (
+                "migrations.test_writer.WriterTests.NestedChoices.method",
+                {"import migrations.test_writer"},
+            ),
+        )
+
     def test_serialize_uuid(self):
         self.assertSerializedEqual(uuid.uuid1())
         self.assertSerializedEqual(uuid.uuid4())

```

## Test Information

**Tests that should FAIL→PASS**: ["test_serialize_nested_class_method (migrations.test_writer.WriterTests.test_serialize_nested_class_method)"]

**Tests that should PASS→PASS**: ["test_args_kwargs_signature (migrations.test_writer.OperationWriterTests.test_args_kwargs_signature)", "test_args_signature (migrations.test_writer.OperationWriterTests.test_args_signature)", "test_empty_signature (migrations.test_writer.OperationWriterTests.test_empty_signature)", "test_expand_args_signature (migrations.test_writer.OperationWriterTests.test_expand_args_signature)", "test_kwargs_signature (migrations.test_writer.OperationWriterTests.test_kwargs_signature)", "test_multiline_args_signature (migrations.test_writer.OperationWriterTests.test_multiline_args_signature)", "test_nested_args_signature (migrations.test_writer.OperationWriterTests.test_nested_args_signature)", "test_nested_operation_expand_args_signature (migrations.test_writer.OperationWriterTests.test_nested_operation_expand_args_signature)", "test_custom_operation (migrations.test_writer.WriterTests.test_custom_operation)", "test_deconstruct_class_arguments (migrations.test_writer.WriterTests.test_deconstruct_class_arguments)", "Test comments at top of file.", "test_migration_path (migrations.test_writer.WriterTests.test_migration_path)", "django.db.models shouldn't be imported if unused.", "test_register_non_serializer (migrations.test_writer.WriterTests.test_register_non_serializer)", "test_register_serializer (migrations.test_writer.WriterTests.test_register_serializer)", "test_serialize_builtin_types (migrations.test_writer.WriterTests.test_serialize_builtin_types)", "test_serialize_builtins (migrations.test_writer.WriterTests.test_serialize_builtins)", "test_serialize_choices (migrations.test_writer.WriterTests.test_serialize_choices)", "Ticket #22943: Test serialization of class-based validators, including", "test_serialize_collections (migrations.test_writer.WriterTests.test_serialize_collections)", "Make sure compiled regex can be serialized.", "test_serialize_complex_func_index (migrations.test_writer.WriterTests.test_serialize_complex_func_index)", "test_serialize_constants (migrations.test_writer.WriterTests.test_serialize_constants)", "test_serialize_datetime (migrations.test_writer.WriterTests.test_serialize_datetime)", "Ticket #22679: makemigrations generates invalid code for (an empty", "test_serialize_enum_flags (migrations.test_writer.WriterTests.test_serialize_enum_flags)", "test_serialize_enums (migrations.test_writer.WriterTests.test_serialize_enums)", "test_serialize_fields (migrations.test_writer.WriterTests.test_serialize_fields)", "test_serialize_frozensets (migrations.test_writer.WriterTests.test_serialize_frozensets)", "test_serialize_functions (migrations.test_writer.WriterTests.test_serialize_functions)", "test_serialize_functools_partial (migrations.test_writer.WriterTests.test_serialize_functools_partial)", "test_serialize_functools_partialmethod (migrations.test_writer.WriterTests.test_serialize_functools_partialmethod)", "test_serialize_iterators (migrations.test_writer.WriterTests.test_serialize_iterators)", "test_serialize_lazy_objects (migrations.test_writer.WriterTests.test_serialize_lazy_objects)", "A reference in a local scope can't be serialized.", "test_serialize_managers (migrations.test_writer.WriterTests.test_serialize_managers)", "test_serialize_multiline_strings (migrations.test_writer.WriterTests.test_serialize_multiline_strings)", "test_serialize_nested_class (migrations.test_writer.WriterTests.test_serialize_nested_class)", "test_serialize_numbers (migrations.test_writer.WriterTests.test_serialize_numbers)", "test_serialize_path_like (migrations.test_writer.WriterTests.test_serialize_path_like)", "test_serialize_pathlib (migrations.test_writer.WriterTests.test_serialize_pathlib)", "test_serialize_range (migrations.test_writer.WriterTests.test_serialize_range)", "test_serialize_set (migrations.test_writer.WriterTests.test_serialize_set)", "test_serialize_settings (migrations.test_writer.WriterTests.test_serialize_settings)", "test_serialize_strings (migrations.test_writer.WriterTests.test_serialize_strings)", "test_serialize_timedelta (migrations.test_writer.WriterTests.test_serialize_timedelta)", "test_serialize_type_model (migrations.test_writer.WriterTests.test_serialize_type_model)", "test_serialize_type_none (migrations.test_writer.WriterTests.test_serialize_type_none)", "An unbound method used within a class body can be serialized.", "test_serialize_uuid (migrations.test_writer.WriterTests.test_serialize_uuid)", "Tests serializing a simple migration.", "test_sorted_dependencies (migrations.test_writer.WriterTests.test_sorted_dependencies)", "#24155 - Tests ordering of imports."]

**Base Commit**: 4a72da71001f154ea60906a2f74898d32b7322a7
**Environment Setup Commit**: 4a72da71001f154ea60906a2f74898d32b7322a7
