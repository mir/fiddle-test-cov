# django__django-12856

**Repository**: django/django
**Created**: 2020-05-04T21:29:23Z
**Version**: 3.2

## Problem Statement

Add check for fields of UniqueConstraints.
Description
	 
		(last modified by Marnanel Thurman)
	 
When a model gains a UniqueConstraint, makemigrations doesn't check that the fields named therein actually exist.
This is in contrast to the older unique_together syntax, which raises models.E012 if the fields don't exist.
In the attached demonstration, you'll need to uncomment "with_unique_together" in settings.py in order to show that unique_together raises E012.


## Hints

Demonstration
Agreed. We can simply call cls._check_local_fields() for UniqueConstraint's fields. I attached tests.
Tests.
Hello Django Team, My name is Jannah Mandwee, and I am working on my final project for my undergraduate software engineering class (here is the link to the assignment: ​https://web.eecs.umich.edu/~weimerw/481/hw6.html). I have to contribute to an open-source project and was advised to look through easy ticket pickings. I am wondering if it is possible to contribute to this ticket or if there is another ticket you believe would be a better fit for me. Thank you for your help.
Replying to Jannah Mandwee: Hello Django Team, My name is Jannah Mandwee, and I am working on my final project for my undergraduate software engineering class (here is the link to the assignment: ​https://web.eecs.umich.edu/~weimerw/481/hw6.html). I have to contribute to an open-source project and was advised to look through easy ticket pickings. I am wondering if it is possible to contribute to this ticket or if there is another ticket you believe would be a better fit for me. Thank you for your help. Hi Jannah, I'm working in this ticket. You can consult this report: https://code.djangoproject.com/query?status=!closed&easy=1&stage=Accepted&order=priority there are all the tickets marked as easy.
CheckConstraint might have the same bug.

## Patch

```diff

diff --git a/django/db/models/base.py b/django/db/models/base.py
--- a/django/db/models/base.py
+++ b/django/db/models/base.py
@@ -1926,6 +1926,12 @@ def _check_constraints(cls, databases):
                         id='models.W038',
                     )
                 )
+            fields = (
+                field
+                for constraint in cls._meta.constraints if isinstance(constraint, UniqueConstraint)
+                for field in constraint.fields
+            )
+            errors.extend(cls._check_local_fields(fields, 'constraints'))
         return errors
 
 


```

## Test Patch

```diff
diff --git a/tests/invalid_models_tests/test_models.py b/tests/invalid_models_tests/test_models.py
--- a/tests/invalid_models_tests/test_models.py
+++ b/tests/invalid_models_tests/test_models.py
@@ -1501,3 +1501,70 @@ class Meta:
                 ]
 
         self.assertEqual(Model.check(databases=self.databases), [])
+
+    def test_unique_constraint_pointing_to_missing_field(self):
+        class Model(models.Model):
+            class Meta:
+                constraints = [models.UniqueConstraint(fields=['missing_field'], name='name')]
+
+        self.assertEqual(Model.check(databases=self.databases), [
+            Error(
+                "'constraints' refers to the nonexistent field "
+                "'missing_field'.",
+                obj=Model,
+                id='models.E012',
+            ),
+        ])
+
+    def test_unique_constraint_pointing_to_m2m_field(self):
+        class Model(models.Model):
+            m2m = models.ManyToManyField('self')
+
+            class Meta:
+                constraints = [models.UniqueConstraint(fields=['m2m'], name='name')]
+
+        self.assertEqual(Model.check(databases=self.databases), [
+            Error(
+                "'constraints' refers to a ManyToManyField 'm2m', but "
+                "ManyToManyFields are not permitted in 'constraints'.",
+                obj=Model,
+                id='models.E013',
+            ),
+        ])
+
+    def test_unique_constraint_pointing_to_non_local_field(self):
+        class Parent(models.Model):
+            field1 = models.IntegerField()
+
+        class Child(Parent):
+            field2 = models.IntegerField()
+
+            class Meta:
+                constraints = [
+                    models.UniqueConstraint(fields=['field2', 'field1'], name='name'),
+                ]
+
+        self.assertEqual(Child.check(databases=self.databases), [
+            Error(
+                "'constraints' refers to field 'field1' which is not local to "
+                "model 'Child'.",
+                hint='This issue may be caused by multi-table inheritance.',
+                obj=Child,
+                id='models.E016',
+            ),
+        ])
+
+    def test_unique_constraint_pointing_to_fk(self):
+        class Target(models.Model):
+            pass
+
+        class Model(models.Model):
+            fk_1 = models.ForeignKey(Target, models.CASCADE, related_name='target_1')
+            fk_2 = models.ForeignKey(Target, models.CASCADE, related_name='target_2')
+
+            class Meta:
+                constraints = [
+                    models.UniqueConstraint(fields=['fk_1_id', 'fk_2'], name='name'),
+                ]
+
+        self.assertEqual(Model.check(databases=self.databases), [])

```

## Test Information

**Tests that should FAIL→PASS**: ["test_unique_constraint_pointing_to_m2m_field (invalid_models_tests.test_models.ConstraintsTests)", "test_unique_constraint_pointing_to_missing_field (invalid_models_tests.test_models.ConstraintsTests)", "test_unique_constraint_pointing_to_non_local_field (invalid_models_tests.test_models.ConstraintsTests)"]

**Tests that should PASS→PASS**: ["test_check_jsonfield (invalid_models_tests.test_models.JSONFieldTests)", "test_check_jsonfield_required_db_features (invalid_models_tests.test_models.JSONFieldTests)", "test_ordering_pointing_to_json_field_value (invalid_models_tests.test_models.JSONFieldTests)", "test_db_column_clash (invalid_models_tests.test_models.FieldNamesTests)", "test_ending_with_underscore (invalid_models_tests.test_models.FieldNamesTests)", "test_including_separator (invalid_models_tests.test_models.FieldNamesTests)", "test_pk (invalid_models_tests.test_models.FieldNamesTests)", "test_list_containing_non_iterable (invalid_models_tests.test_models.UniqueTogetherTests)", "test_non_iterable (invalid_models_tests.test_models.UniqueTogetherTests)", "test_non_list (invalid_models_tests.test_models.UniqueTogetherTests)", "test_pointing_to_fk (invalid_models_tests.test_models.UniqueTogetherTests)", "test_pointing_to_m2m (invalid_models_tests.test_models.UniqueTogetherTests)", "test_pointing_to_missing_field (invalid_models_tests.test_models.UniqueTogetherTests)", "test_valid_model (invalid_models_tests.test_models.UniqueTogetherTests)", "test_list_containing_non_iterable (invalid_models_tests.test_models.IndexTogetherTests)", "test_non_iterable (invalid_models_tests.test_models.IndexTogetherTests)", "test_non_list (invalid_models_tests.test_models.IndexTogetherTests)", "test_pointing_to_fk (invalid_models_tests.test_models.IndexTogetherTests)", "test_pointing_to_m2m_field (invalid_models_tests.test_models.IndexTogetherTests)", "test_pointing_to_missing_field (invalid_models_tests.test_models.IndexTogetherTests)", "test_pointing_to_non_local_field (invalid_models_tests.test_models.IndexTogetherTests)", "test_field_name_clash_with_child_accessor (invalid_models_tests.test_models.ShadowingFieldsTests)", "test_id_clash (invalid_models_tests.test_models.ShadowingFieldsTests)", "test_inheritance_clash (invalid_models_tests.test_models.ShadowingFieldsTests)", "test_multigeneration_inheritance (invalid_models_tests.test_models.ShadowingFieldsTests)", "test_multiinheritance_clash (invalid_models_tests.test_models.ShadowingFieldsTests)", "test_index_with_condition (invalid_models_tests.test_models.IndexesTests)", "test_index_with_condition_required_db_features (invalid_models_tests.test_models.IndexesTests)", "test_max_name_length (invalid_models_tests.test_models.IndexesTests)", "test_name_constraints (invalid_models_tests.test_models.IndexesTests)", "test_pointing_to_fk (invalid_models_tests.test_models.IndexesTests)", "test_pointing_to_m2m_field (invalid_models_tests.test_models.IndexesTests)", "test_pointing_to_missing_field (invalid_models_tests.test_models.IndexesTests)", "test_pointing_to_non_local_field (invalid_models_tests.test_models.IndexesTests)", "test_check_constraints (invalid_models_tests.test_models.ConstraintsTests)", "test_check_constraints_required_db_features (invalid_models_tests.test_models.ConstraintsTests)", "test_deferrable_unique_constraint (invalid_models_tests.test_models.ConstraintsTests)", "test_deferrable_unique_constraint_required_db_features (invalid_models_tests.test_models.ConstraintsTests)", "test_unique_constraint_pointing_to_fk (invalid_models_tests.test_models.ConstraintsTests)", "test_unique_constraint_with_condition (invalid_models_tests.test_models.ConstraintsTests)", "test_unique_constraint_with_condition_required_db_features (invalid_models_tests.test_models.ConstraintsTests)", "test_just_order_with_respect_to_no_errors (invalid_models_tests.test_models.OtherModelTests)", "test_just_ordering_no_errors (invalid_models_tests.test_models.OtherModelTests)", "test_lazy_reference_checks (invalid_models_tests.test_models.OtherModelTests)", "test_m2m_autogenerated_table_name_clash (invalid_models_tests.test_models.OtherModelTests)", "test_m2m_autogenerated_table_name_clash_database_routers_installed (invalid_models_tests.test_models.OtherModelTests)", "test_m2m_field_table_name_clash (invalid_models_tests.test_models.OtherModelTests)", "test_m2m_field_table_name_clash_database_routers_installed (invalid_models_tests.test_models.OtherModelTests)", "test_m2m_table_name_clash (invalid_models_tests.test_models.OtherModelTests)", "test_m2m_table_name_clash_database_routers_installed (invalid_models_tests.test_models.OtherModelTests)", "test_m2m_to_concrete_and_proxy_allowed (invalid_models_tests.test_models.OtherModelTests)", "test_m2m_unmanaged_shadow_models_not_checked (invalid_models_tests.test_models.OtherModelTests)", "test_name_beginning_with_underscore (invalid_models_tests.test_models.OtherModelTests)", "test_name_contains_double_underscores (invalid_models_tests.test_models.OtherModelTests)", "test_name_ending_with_underscore (invalid_models_tests.test_models.OtherModelTests)", "test_non_valid (invalid_models_tests.test_models.OtherModelTests)", "test_onetoone_with_explicit_parent_link_parent_model (invalid_models_tests.test_models.OtherModelTests)", "test_onetoone_with_parent_model (invalid_models_tests.test_models.OtherModelTests)", "test_ordering_allows_registered_lookups (invalid_models_tests.test_models.OtherModelTests)", "test_ordering_non_iterable (invalid_models_tests.test_models.OtherModelTests)", "test_ordering_pointing_multiple_times_to_model_fields (invalid_models_tests.test_models.OtherModelTests)", "test_ordering_pointing_to_foreignkey_field (invalid_models_tests.test_models.OtherModelTests)", "test_ordering_pointing_to_lookup_not_transform (invalid_models_tests.test_models.OtherModelTests)", "test_ordering_pointing_to_missing_field (invalid_models_tests.test_models.OtherModelTests)", "test_ordering_pointing_to_missing_foreignkey_field (invalid_models_tests.test_models.OtherModelTests)", "test_ordering_pointing_to_missing_related_field (invalid_models_tests.test_models.OtherModelTests)", "test_ordering_pointing_to_missing_related_model_field (invalid_models_tests.test_models.OtherModelTests)", "test_ordering_pointing_to_non_related_field (invalid_models_tests.test_models.OtherModelTests)", "test_ordering_pointing_to_related_model_pk (invalid_models_tests.test_models.OtherModelTests)", "test_ordering_pointing_to_two_related_model_field (invalid_models_tests.test_models.OtherModelTests)", "test_ordering_with_order_with_respect_to (invalid_models_tests.test_models.OtherModelTests)", "test_property_and_related_field_accessor_clash (invalid_models_tests.test_models.OtherModelTests)", "test_single_primary_key (invalid_models_tests.test_models.OtherModelTests)", "test_swappable_missing_app (invalid_models_tests.test_models.OtherModelTests)", "test_swappable_missing_app_name (invalid_models_tests.test_models.OtherModelTests)", "test_two_m2m_through_same_model_with_different_through_fields (invalid_models_tests.test_models.OtherModelTests)", "test_two_m2m_through_same_relationship (invalid_models_tests.test_models.OtherModelTests)", "test_unique_primary_key (invalid_models_tests.test_models.OtherModelTests)"]

**Base Commit**: 8328811f048fed0dd22573224def8c65410c9f2e
**Environment Setup Commit**: 65dfb06a1ab56c238cc80f5e1c31f61210c4577d
