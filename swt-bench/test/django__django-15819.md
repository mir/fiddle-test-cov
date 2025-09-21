# django__django-15819

**Repository**: django/django
**Created**: 2022-07-04T18:29:53Z
**Version**: 4.2

## Problem Statement

inspectdb should generate related_name on same relation links.
Description
	
Hi!
After models generation with inspectdb command we have issue with relations to same enities
module.Model.field1: (fields.E304) Reverse accessor for 'module.Model.field1' clashes with reverse accessor for 'module.Model.field2'.
HINT: Add or change a related_name argument to the definition for 'module.Model.field1' or 'module.Model.field2'.
*
Maybe we can autogenerate
related_name='attribute_name'
to all fields in model if related Model was used for this table


## Hints

FIrst solution variant was - ​https://github.com/django/django/pull/15816 But now I see it is not correct. I'll be back with new pull request

## Patch

```diff

diff --git a/django/core/management/commands/inspectdb.py b/django/core/management/commands/inspectdb.py
--- a/django/core/management/commands/inspectdb.py
+++ b/django/core/management/commands/inspectdb.py
@@ -127,12 +127,14 @@ def table2model(table_name):
                     yield "# The error was: %s" % e
                     continue
 
+                model_name = table2model(table_name)
                 yield ""
                 yield ""
-                yield "class %s(models.Model):" % table2model(table_name)
-                known_models.append(table2model(table_name))
+                yield "class %s(models.Model):" % model_name
+                known_models.append(model_name)
                 used_column_names = []  # Holds column names used in the table so far
                 column_to_field_name = {}  # Maps column names to names of model fields
+                used_relations = set()  # Holds foreign relations used in the table.
                 for row in table_description:
                     comment_notes = (
                         []
@@ -186,6 +188,12 @@ def table2model(table_name):
                             field_type = "%s(%s" % (rel_type, rel_to)
                         else:
                             field_type = "%s('%s'" % (rel_type, rel_to)
+                        if rel_to in used_relations:
+                            extra_params["related_name"] = "%s_%s_set" % (
+                                model_name.lower(),
+                                att_name,
+                            )
+                        used_relations.add(rel_to)
                     else:
                         # Calling `get_field_type` to get the field type string and any
                         # additional parameters and notes.


```

## Test Patch

```diff
diff --git a/tests/inspectdb/models.py b/tests/inspectdb/models.py
--- a/tests/inspectdb/models.py
+++ b/tests/inspectdb/models.py
@@ -9,6 +9,7 @@ class People(models.Model):
 
 class Message(models.Model):
     from_field = models.ForeignKey(People, models.CASCADE, db_column="from_id")
+    author = models.ForeignKey(People, models.CASCADE, related_name="message_authors")
 
 
 class PeopleData(models.Model):
diff --git a/tests/inspectdb/tests.py b/tests/inspectdb/tests.py
--- a/tests/inspectdb/tests.py
+++ b/tests/inspectdb/tests.py
@@ -433,6 +433,15 @@ def test_introspection_errors(self):
         # The error message depends on the backend
         self.assertIn("# The error was:", output)
 
+    def test_same_relations(self):
+        out = StringIO()
+        call_command("inspectdb", "inspectdb_message", stdout=out)
+        self.assertIn(
+            "author = models.ForeignKey('InspectdbPeople', models.DO_NOTHING, "
+            "related_name='inspectdbmessage_author_set')",
+            out.getvalue(),
+        )
+
 
 class InspectDBTransactionalTests(TransactionTestCase):
     available_apps = ["inspectdb"]

```

## Test Information

**Tests that should FAIL→PASS**: ["test_same_relations (inspectdb.tests.InspectDBTestCase)"]

**Tests that should PASS→PASS**: ["test_composite_primary_key (inspectdb.tests.InspectDBTransactionalTests)", "inspectdb --include-views creates models for database views.", "test_attribute_name_not_python_keyword (inspectdb.tests.InspectDBTestCase)", "test_char_field_db_collation (inspectdb.tests.InspectDBTestCase)", "Introspection of columns with a custom field (#21090)", "Introspection of column names consist/start with digits (#16536/#17676)", "Test introspection of various Django field types", "test_foreign_key_to_field (inspectdb.tests.InspectDBTestCase)", "Introspection errors should not crash the command, and the error should", "test_json_field (inspectdb.tests.InspectDBTestCase)", "By default the command generates models with `Meta.managed = False`.", "Introspection of column names containing special characters,", "test_stealth_table_name_filter_option (inspectdb.tests.InspectDBTestCase)", "Introspection of table names containing special characters,", "inspectdb can inspect a subset of tables by passing the table names as", "test_table_with_func_unique_constraint (inspectdb.tests.InspectDBTestCase)", "test_text_field_db_collation (inspectdb.tests.InspectDBTestCase)", "test_unique_together_meta (inspectdb.tests.InspectDBTestCase)"]

**Base Commit**: 877c800f255ccaa7abde1fb944de45d1616f5cc9
**Environment Setup Commit**: 0fbdb9784da915fce5dcc1fe82bac9b4785749e5
