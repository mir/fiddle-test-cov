# django__django-12125

**Repository**: django/django
**Created**: 2019-11-22T12:55:45Z
**Version**: 3.1

## Problem Statement

makemigrations produces incorrect path for inner classes
Description
	
When you define a subclass from django.db.models.Field as an inner class of some other class, and use this field inside a django.db.models.Model class, then when you run manage.py makemigrations, a migrations file is created which refers to the inner class as if it were a top-level class of the module it is in.
To reproduce, create the following as your model:
class Outer(object):
	class Inner(models.CharField):
		pass
class A(models.Model):
	field = Outer.Inner(max_length=20)
After running manage.py makemigrations, the generated migrations file contains the following:
migrations.CreateModel(
	name='A',
	fields=[
		('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
		('field', test1.models.Inner(max_length=20)),
	],
),
Note the test1.models.Inner, which should have been test1.models.Outer.Inner.
The real life case involved an EnumField from django-enumfields, defined as an inner class of a Django Model class, similar to this:
import enum
from enumfields import Enum, EnumField
class Thing(models.Model):
	@enum.unique
	class State(Enum):
		on = 'on'
		off = 'off'
	state = EnumField(enum=State)
This results in the following migrations code:
migrations.CreateModel(
	name='Thing',
	fields=[
		('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
		('state', enumfields.fields.EnumField(enum=test1.models.State, max_length=10)),
	],
),
This refers to test1.models.State, instead of to test1.models.Thing.State.


## Hints

This should be possible to do by relying on __qualname__ (instead of __name__) now that master is Python 3 only.
​PR
I think we should focus on using __qualname__ during migration serialization as well instead of simply solving the field subclasses case.
In fb0f987: Fixed #27914 -- Added support for nested classes in Field.deconstruct()/repr().
In 451b585: Refs #27914 -- Used qualname in model operations' deconstruct().
I am still encountering this issue when running makemigrations on models that include a django-enumfields EnumField. From tracing through the code, I believe the Enum is getting serialized using the django.db.migrations.serializer.TypeSerializer, which still uses the __name__ rather than __qualname__. As a result, the Enum's path gets resolved to app_name.models.enum_name and the generated migration file throws an error "app_name.models has no 'enum_name' member". The correct path for the inner class should be app_name.models.model_name.enum_name. ​https://github.com/django/django/blob/master/django/db/migrations/serializer.py#L266
Reopening it. Will recheck with nested enum field.
​PR for fixing enum class as an inner class of model.
In d3030dea: Refs #27914 -- Moved test enum.Enum subclasses outside of WriterTests.test_serialize_enums().
In 6452112: Refs #27914 -- Fixed serialization of nested enum.Enum classes in migrations.
In 1a4db2c: [3.0.x] Refs #27914 -- Moved test enum.Enum subclasses outside of WriterTests.test_serialize_enums(). Backport of d3030deaaa50b7814e34ef1e71f2afaf97c6bec6 from master
In 30271a47: [3.0.x] Refs #27914 -- Fixed serialization of nested enum.Enum classes in migrations. Backport of 6452112640081ac8838147a8ba192c45879203d8 from master
commit 6452112640081ac8838147a8ba192c45879203d8 does not resolve this ticket. The commit patched the EnumSerializer with __qualname__, which works for Enum members. However, the serializer_factory is returning TypeSerializer for the Enum subclass, which is still using __name__ With v3.0.x introducing models.Choices, models.IntegerChoices, using nested enums will become a common pattern; serializing them properly with __qualname__ seems prudent. Here's a patch for the 3.0rc1 build ​https://github.com/django/django/files/3879265/django_db_migrations_serializer_TypeSerializer.patch.txt
Agreed, we should fix this.
I will create a patch a soon as possible.
Submitted PR: ​https://github.com/django/django/pull/12125
PR: ​https://github.com/django/django/pull/12125

## Patch

```diff

diff --git a/django/db/migrations/serializer.py b/django/db/migrations/serializer.py
--- a/django/db/migrations/serializer.py
+++ b/django/db/migrations/serializer.py
@@ -269,7 +269,7 @@ def serialize(self):
             if module == builtins.__name__:
                 return self.value.__name__, set()
             else:
-                return "%s.%s" % (module, self.value.__name__), {"import %s" % module}
+                return "%s.%s" % (module, self.value.__qualname__), {"import %s" % module}
 
 
 class UUIDSerializer(BaseSerializer):


```

## Test Patch

```diff
diff --git a/tests/migrations/test_writer.py b/tests/migrations/test_writer.py
--- a/tests/migrations/test_writer.py
+++ b/tests/migrations/test_writer.py
@@ -26,6 +26,11 @@
 from .models import FoodManager, FoodQuerySet
 
 
+class DeconstructibleInstances:
+    def deconstruct(self):
+        return ('DeconstructibleInstances', [], {})
+
+
 class Money(decimal.Decimal):
     def deconstruct(self):
         return (
@@ -188,6 +193,10 @@ class NestedEnum(enum.IntEnum):
         A = 1
         B = 2
 
+    class NestedChoices(models.TextChoices):
+        X = 'X', 'X value'
+        Y = 'Y', 'Y value'
+
     def safe_exec(self, string, value=None):
         d = {}
         try:
@@ -383,6 +392,18 @@ class DateChoices(datetime.date, models.Choices):
             "default=datetime.date(1969, 11, 19))"
         )
 
+    def test_serialize_nested_class(self):
+        for nested_cls in [self.NestedEnum, self.NestedChoices]:
+            cls_name = nested_cls.__name__
+            with self.subTest(cls_name):
+                self.assertSerializedResultEqual(
+                    nested_cls,
+                    (
+                        "migrations.test_writer.WriterTests.%s" % cls_name,
+                        {'import migrations.test_writer'},
+                    ),
+                )
+
     def test_serialize_uuid(self):
         self.assertSerializedEqual(uuid.uuid1())
         self.assertSerializedEqual(uuid.uuid4())
@@ -726,10 +747,6 @@ def test_deconstruct_class_arguments(self):
         # Yes, it doesn't make sense to use a class as a default for a
         # CharField. It does make sense for custom fields though, for example
         # an enumfield that takes the enum class as an argument.
-        class DeconstructibleInstances:
-            def deconstruct(self):
-                return ('DeconstructibleInstances', [], {})
-
         string = MigrationWriter.serialize(models.CharField(default=DeconstructibleInstances))[0]
         self.assertEqual(string, "models.CharField(default=migrations.test_writer.DeconstructibleInstances)")
 

```

## Test Information

**Tests that should FAIL→PASS**: ["test_serialize_nested_class (migrations.test_writer.WriterTests)", "test_serialize_numbers (migrations.test_writer.WriterTests)"]

**Tests that should PASS→PASS**: ["test_args_kwargs_signature (migrations.test_writer.OperationWriterTests)", "test_args_signature (migrations.test_writer.OperationWriterTests)", "test_empty_signature (migrations.test_writer.OperationWriterTests)", "test_expand_args_signature (migrations.test_writer.OperationWriterTests)", "test_kwargs_signature (migrations.test_writer.OperationWriterTests)", "test_multiline_args_signature (migrations.test_writer.OperationWriterTests)", "test_nested_args_signature (migrations.test_writer.OperationWriterTests)", "test_nested_operation_expand_args_signature (migrations.test_writer.OperationWriterTests)", "test_custom_operation (migrations.test_writer.WriterTests)", "test_deconstruct_class_arguments (migrations.test_writer.WriterTests)", "test_migration_file_header_comments (migrations.test_writer.WriterTests)", "test_migration_path (migrations.test_writer.WriterTests)", "test_models_import_omitted (migrations.test_writer.WriterTests)", "test_register_non_serializer (migrations.test_writer.WriterTests)", "test_register_serializer (migrations.test_writer.WriterTests)", "test_serialize_builtin_types (migrations.test_writer.WriterTests)", "test_serialize_builtins (migrations.test_writer.WriterTests)", "test_serialize_choices (migrations.test_writer.WriterTests)", "test_serialize_class_based_validators (migrations.test_writer.WriterTests)", "test_serialize_collections (migrations.test_writer.WriterTests)", "test_serialize_compiled_regex (migrations.test_writer.WriterTests)", "test_serialize_constants (migrations.test_writer.WriterTests)", "test_serialize_datetime (migrations.test_writer.WriterTests)", "test_serialize_empty_nonempty_tuple (migrations.test_writer.WriterTests)", "test_serialize_enums (migrations.test_writer.WriterTests)", "test_serialize_fields (migrations.test_writer.WriterTests)", "test_serialize_frozensets (migrations.test_writer.WriterTests)", "test_serialize_functions (migrations.test_writer.WriterTests)", "test_serialize_functools_partial (migrations.test_writer.WriterTests)", "test_serialize_functools_partialmethod (migrations.test_writer.WriterTests)", "test_serialize_iterators (migrations.test_writer.WriterTests)", "test_serialize_lazy_objects (migrations.test_writer.WriterTests)", "A reference in a local scope can't be serialized.", "test_serialize_managers (migrations.test_writer.WriterTests)", "test_serialize_multiline_strings (migrations.test_writer.WriterTests)", "test_serialize_range (migrations.test_writer.WriterTests)", "test_serialize_set (migrations.test_writer.WriterTests)", "test_serialize_settings (migrations.test_writer.WriterTests)", "test_serialize_strings (migrations.test_writer.WriterTests)", "test_serialize_timedelta (migrations.test_writer.WriterTests)", "test_serialize_type_none (migrations.test_writer.WriterTests)", "An unbound method used within a class body can be serialized.", "test_serialize_uuid (migrations.test_writer.WriterTests)", "test_simple_migration (migrations.test_writer.WriterTests)", "test_sorted_imports (migrations.test_writer.WriterTests)"]

**Base Commit**: 89d41cba392b759732ba9f1db4ff29ed47da6a56
**Environment Setup Commit**: 0668164b4ac93a5be79f5b87fae83c657124d9ab
