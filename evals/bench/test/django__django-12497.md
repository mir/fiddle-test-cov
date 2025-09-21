# django__django-12497

**Repository**: django/django
**Created**: 2020-02-26T18:12:31Z
**Version**: 3.1

## Problem Statement

Wrong hint about recursive relationship.
Description
	 
		(last modified by Matheus Cunha Motta)
	 
When there's more than 2 ForeignKeys in an intermediary model of a m2m field and no through_fields have been set, Django will show an error with the following hint:
hint=(
	'If you want to create a recursive relationship, '
	'use ForeignKey("%s", symmetrical=False, through="%s").'
But 'symmetrical' and 'through' are m2m keyword arguments, not ForeignKey.
This was probably a small mistake where the developer thought ManyToManyField but typed ForeignKey instead. And the symmetrical=False is an outdated requirement to recursive relationships with intermediary model to self, not required since 3.0. I'll provide a PR with a proposed correction shortly after.
Edit: fixed description.


## Hints

Here's a PR: ​https://github.com/django/django/pull/12497 Edit: forgot to run tests and there was an error detected in the PR. I'll try to fix and run tests before submitting again.

## Patch

```diff

diff --git a/django/db/models/fields/related.py b/django/db/models/fields/related.py
--- a/django/db/models/fields/related.py
+++ b/django/db/models/fields/related.py
@@ -1309,7 +1309,7 @@ def _check_relationship_model(self, from_model=None, **kwargs):
                              "through_fields keyword argument.") % (self, from_model_name),
                             hint=(
                                 'If you want to create a recursive relationship, '
-                                'use ForeignKey("%s", symmetrical=False, through="%s").'
+                                'use ManyToManyField("%s", through="%s").'
                             ) % (
                                 RECURSIVE_RELATIONSHIP_CONSTANT,
                                 relationship_model_name,
@@ -1329,7 +1329,7 @@ def _check_relationship_model(self, from_model=None, **kwargs):
                             "through_fields keyword argument." % (self, to_model_name),
                             hint=(
                                 'If you want to create a recursive relationship, '
-                                'use ForeignKey("%s", symmetrical=False, through="%s").'
+                                'use ManyToManyField("%s", through="%s").'
                             ) % (
                                 RECURSIVE_RELATIONSHIP_CONSTANT,
                                 relationship_model_name,


```

## Test Patch

```diff
diff --git a/tests/invalid_models_tests/test_relative_fields.py b/tests/invalid_models_tests/test_relative_fields.py
--- a/tests/invalid_models_tests/test_relative_fields.py
+++ b/tests/invalid_models_tests/test_relative_fields.py
@@ -128,7 +128,36 @@ class ThroughModel(models.Model):
             ),
         ])
 
-    def test_ambiguous_relationship_model(self):
+    def test_ambiguous_relationship_model_from(self):
+        class Person(models.Model):
+            pass
+
+        class Group(models.Model):
+            field = models.ManyToManyField('Person', through='AmbiguousRelationship')
+
+        class AmbiguousRelationship(models.Model):
+            person = models.ForeignKey(Person, models.CASCADE)
+            first_group = models.ForeignKey(Group, models.CASCADE, related_name='first')
+            second_group = models.ForeignKey(Group, models.CASCADE, related_name='second')
+
+        field = Group._meta.get_field('field')
+        self.assertEqual(field.check(from_model=Group), [
+            Error(
+                "The model is used as an intermediate model by "
+                "'invalid_models_tests.Group.field', but it has more than one "
+                "foreign key from 'Group', which is ambiguous. You must "
+                "specify which foreign key Django should use via the "
+                "through_fields keyword argument.",
+                hint=(
+                    'If you want to create a recursive relationship, use '
+                    'ManyToManyField("self", through="AmbiguousRelationship").'
+                ),
+                obj=field,
+                id='fields.E334',
+            ),
+        ])
+
+    def test_ambiguous_relationship_model_to(self):
 
         class Person(models.Model):
             pass
@@ -152,7 +181,7 @@ class AmbiguousRelationship(models.Model):
                 "keyword argument.",
                 hint=(
                     'If you want to create a recursive relationship, use '
-                    'ForeignKey("self", symmetrical=False, through="AmbiguousRelationship").'
+                    'ManyToManyField("self", through="AmbiguousRelationship").'
                 ),
                 obj=field,
                 id='fields.E335',

```

## Test Information

**Tests that should FAIL→PASS**: ["test_ambiguous_relationship_model_from (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_ambiguous_relationship_model_to (invalid_models_tests.test_relative_fields.RelativeFieldTests)"]

**Tests that should PASS→PASS**: ["test_accessor_clash (invalid_models_tests.test_relative_fields.SelfReferentialFKClashTests)", "test_clash_under_explicit_related_name (invalid_models_tests.test_relative_fields.SelfReferentialFKClashTests)", "test_reverse_query_name_clash (invalid_models_tests.test_relative_fields.SelfReferentialFKClashTests)", "test_explicit_field_names (invalid_models_tests.test_relative_fields.M2mThroughFieldsTests)", "test_intersection_foreign_object (invalid_models_tests.test_relative_fields.M2mThroughFieldsTests)", "test_invalid_field (invalid_models_tests.test_relative_fields.M2mThroughFieldsTests)", "test_invalid_order (invalid_models_tests.test_relative_fields.M2mThroughFieldsTests)", "test_m2m_field_argument_validation (invalid_models_tests.test_relative_fields.M2mThroughFieldsTests)", "test_superset_foreign_object (invalid_models_tests.test_relative_fields.M2mThroughFieldsTests)", "test_clash_parent_link (invalid_models_tests.test_relative_fields.ComplexClashTests)", "test_complex_clash (invalid_models_tests.test_relative_fields.ComplexClashTests)", "test_accessor_clash (invalid_models_tests.test_relative_fields.SelfReferentialM2MClashTests)", "test_clash_between_accessors (invalid_models_tests.test_relative_fields.SelfReferentialM2MClashTests)", "test_clash_under_explicit_related_name (invalid_models_tests.test_relative_fields.SelfReferentialM2MClashTests)", "test_reverse_query_name_clash (invalid_models_tests.test_relative_fields.SelfReferentialM2MClashTests)", "test_valid_model (invalid_models_tests.test_relative_fields.SelfReferentialM2MClashTests)", "test_fk_to_fk (invalid_models_tests.test_relative_fields.ExplicitRelatedNameClashTests)", "test_fk_to_integer (invalid_models_tests.test_relative_fields.ExplicitRelatedNameClashTests)", "test_fk_to_m2m (invalid_models_tests.test_relative_fields.ExplicitRelatedNameClashTests)", "test_m2m_to_fk (invalid_models_tests.test_relative_fields.ExplicitRelatedNameClashTests)", "test_m2m_to_integer (invalid_models_tests.test_relative_fields.ExplicitRelatedNameClashTests)", "test_m2m_to_m2m (invalid_models_tests.test_relative_fields.ExplicitRelatedNameClashTests)", "test_clash_between_accessors (invalid_models_tests.test_relative_fields.AccessorClashTests)", "test_fk_to_fk (invalid_models_tests.test_relative_fields.AccessorClashTests)", "test_fk_to_integer (invalid_models_tests.test_relative_fields.AccessorClashTests)", "test_fk_to_m2m (invalid_models_tests.test_relative_fields.AccessorClashTests)", "test_m2m_to_fk (invalid_models_tests.test_relative_fields.AccessorClashTests)", "test_m2m_to_integer (invalid_models_tests.test_relative_fields.AccessorClashTests)", "test_m2m_to_m2m (invalid_models_tests.test_relative_fields.AccessorClashTests)", "Ref #22047.", "test_no_clash_for_hidden_related_name (invalid_models_tests.test_relative_fields.AccessorClashTests)", "test_fk_to_fk (invalid_models_tests.test_relative_fields.ReverseQueryNameClashTests)", "test_fk_to_integer (invalid_models_tests.test_relative_fields.ReverseQueryNameClashTests)", "test_fk_to_m2m (invalid_models_tests.test_relative_fields.ReverseQueryNameClashTests)", "test_m2m_to_fk (invalid_models_tests.test_relative_fields.ReverseQueryNameClashTests)", "test_m2m_to_integer (invalid_models_tests.test_relative_fields.ReverseQueryNameClashTests)", "test_m2m_to_m2m (invalid_models_tests.test_relative_fields.ReverseQueryNameClashTests)", "test_fk_to_fk (invalid_models_tests.test_relative_fields.ExplicitRelatedQueryNameClashTests)", "test_fk_to_integer (invalid_models_tests.test_relative_fields.ExplicitRelatedQueryNameClashTests)", "test_fk_to_m2m (invalid_models_tests.test_relative_fields.ExplicitRelatedQueryNameClashTests)", "test_hidden_fk_to_fk (invalid_models_tests.test_relative_fields.ExplicitRelatedQueryNameClashTests)", "test_hidden_fk_to_integer (invalid_models_tests.test_relative_fields.ExplicitRelatedQueryNameClashTests)", "test_hidden_fk_to_m2m (invalid_models_tests.test_relative_fields.ExplicitRelatedQueryNameClashTests)", "test_hidden_m2m_to_fk (invalid_models_tests.test_relative_fields.ExplicitRelatedQueryNameClashTests)", "test_hidden_m2m_to_integer (invalid_models_tests.test_relative_fields.ExplicitRelatedQueryNameClashTests)", "test_hidden_m2m_to_m2m (invalid_models_tests.test_relative_fields.ExplicitRelatedQueryNameClashTests)", "test_m2m_to_fk (invalid_models_tests.test_relative_fields.ExplicitRelatedQueryNameClashTests)", "test_m2m_to_integer (invalid_models_tests.test_relative_fields.ExplicitRelatedQueryNameClashTests)", "test_m2m_to_m2m (invalid_models_tests.test_relative_fields.ExplicitRelatedQueryNameClashTests)", "test_foreign_key_to_abstract_model (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_foreign_key_to_isolate_apps_model (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_foreign_key_to_missing_model (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_foreign_key_to_non_unique_field (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_foreign_key_to_non_unique_field_under_explicit_model (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_foreign_key_to_partially_unique_field (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_foreign_key_to_unique_field_with_meta_constraint (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_foreign_object_to_non_unique_fields (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_foreign_object_to_partially_unique_field (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_foreign_object_to_unique_field_with_meta_constraint (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_invalid_related_query_name (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_m2m_to_abstract_model (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_many_to_many_through_isolate_apps_model (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_many_to_many_to_isolate_apps_model (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_many_to_many_to_missing_model (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_many_to_many_with_limit_choices_auto_created_no_warning (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_many_to_many_with_useless_options (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_missing_relationship_model (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_missing_relationship_model_on_model_check (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_not_swapped_model (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_nullable_primary_key (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_on_delete_set_default_without_default_value (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_on_delete_set_null_on_non_nullable_field (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_referencing_to_swapped_model (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_related_field_has_invalid_related_name (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_related_field_has_valid_related_name (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_relationship_model_missing_foreign_key (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_relationship_model_with_foreign_key_to_wrong_model (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_to_fields_exist (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_to_fields_not_checked_if_related_model_doesnt_exist (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_too_many_foreign_keys_in_self_referential_model (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_unique_m2m (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_valid_foreign_key_without_accessor (invalid_models_tests.test_relative_fields.RelativeFieldTests)"]

**Base Commit**: a4881f5e5d7ee38b7e83301331a0b4962845ef8a
**Environment Setup Commit**: 0668164b4ac93a5be79f5b87fae83c657124d9ab
