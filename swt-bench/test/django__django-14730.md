# django__django-14730

**Repository**: django/django
**Created**: 2021-08-03T04:27:52Z
**Version**: 4.0

## Problem Statement

Prevent developers from defining a related_name on symmetrical ManyToManyFields
Description
	
In ManyToManyField, if the symmetrical argument is passed, or if it's a self-referential ManyToMany relationship, the related field on the target model is not created. However, if a developer passes in the related_name not understanding this fact, they may be confused until they find the information about symmetrical relationship. Thus, it is proposed to raise an error when the user defines a ManyToManyField in this condition.


## Hints

I have a PR that implements this incoming.
​https://github.com/django/django/pull/14730
OK, I guess we can do something here — it probably is a source of confusion. The same issue was raised in #18021 (but as an invalid bug report, rather than suggesting improving the messaging). Looking at the PR — I'm sceptical about just raising an error — this will likely break code in the wild. Can we investigate adding a system check here instead? There are several similar checks for related fields already: ​https://docs.djangoproject.com/en/3.2/ref/checks/#related-fields
Same issue also came up in #12641
Absolutely. A system check is a much better approach than my initial idea of the error. I have changed the patch to use a system check.
Unchecking patch needs improvement as instructed on the page, (pending reviewer acceptance of course).

## Patch

```diff

diff --git a/django/db/models/fields/related.py b/django/db/models/fields/related.py
--- a/django/db/models/fields/related.py
+++ b/django/db/models/fields/related.py
@@ -1258,6 +1258,16 @@ def _check_ignored_options(self, **kwargs):
                 )
             )
 
+        if self.remote_field.symmetrical and self._related_name:
+            warnings.append(
+                checks.Warning(
+                    'related_name has no effect on ManyToManyField '
+                    'with a symmetrical relationship, e.g. to "self".',
+                    obj=self,
+                    id='fields.W345',
+                )
+            )
+
         return warnings
 
     def _check_relationship_model(self, from_model=None, **kwargs):


```

## Test Patch

```diff
diff --git a/tests/field_deconstruction/tests.py b/tests/field_deconstruction/tests.py
--- a/tests/field_deconstruction/tests.py
+++ b/tests/field_deconstruction/tests.py
@@ -438,7 +438,6 @@ class MyModel(models.Model):
             m2m = models.ManyToManyField('self')
             m2m_related_name = models.ManyToManyField(
                 'self',
-                related_name='custom_name',
                 related_query_name='custom_query_name',
                 limit_choices_to={'flag': True},
             )
@@ -455,7 +454,6 @@ class MyModel(models.Model):
         self.assertEqual(args, [])
         self.assertEqual(kwargs, {
             'to': 'field_deconstruction.MyModel',
-            'related_name': 'custom_name',
             'related_query_name': 'custom_query_name',
             'limit_choices_to': {'flag': True},
         })
diff --git a/tests/invalid_models_tests/test_relative_fields.py b/tests/invalid_models_tests/test_relative_fields.py
--- a/tests/invalid_models_tests/test_relative_fields.py
+++ b/tests/invalid_models_tests/test_relative_fields.py
@@ -128,6 +128,20 @@ class ThroughModel(models.Model):
             ),
         ])
 
+    def test_many_to_many_with_useless_related_name(self):
+        class ModelM2M(models.Model):
+            m2m = models.ManyToManyField('self', related_name='children')
+
+        field = ModelM2M._meta.get_field('m2m')
+        self.assertEqual(ModelM2M.check(), [
+            DjangoWarning(
+                'related_name has no effect on ManyToManyField with '
+                'a symmetrical relationship, e.g. to "self".',
+                obj=field,
+                id='fields.W345',
+            ),
+        ])
+
     def test_ambiguous_relationship_model_from(self):
         class Person(models.Model):
             pass
diff --git a/tests/model_meta/models.py b/tests/model_meta/models.py
--- a/tests/model_meta/models.py
+++ b/tests/model_meta/models.py
@@ -23,7 +23,7 @@ class AbstractPerson(models.Model):
 
     # M2M fields
     m2m_abstract = models.ManyToManyField(Relation, related_name='m2m_abstract_rel')
-    friends_abstract = models.ManyToManyField('self', related_name='friends_abstract', symmetrical=True)
+    friends_abstract = models.ManyToManyField('self', symmetrical=True)
     following_abstract = models.ManyToManyField('self', related_name='followers_abstract', symmetrical=False)
 
     # VIRTUAL fields
@@ -60,7 +60,7 @@ class BasePerson(AbstractPerson):
 
     # M2M fields
     m2m_base = models.ManyToManyField(Relation, related_name='m2m_base_rel')
-    friends_base = models.ManyToManyField('self', related_name='friends_base', symmetrical=True)
+    friends_base = models.ManyToManyField('self', symmetrical=True)
     following_base = models.ManyToManyField('self', related_name='followers_base', symmetrical=False)
 
     # VIRTUAL fields
@@ -88,7 +88,7 @@ class Person(BasePerson):
 
     # M2M Fields
     m2m_inherited = models.ManyToManyField(Relation, related_name='m2m_concrete_rel')
-    friends_inherited = models.ManyToManyField('self', related_name='friends_concrete', symmetrical=True)
+    friends_inherited = models.ManyToManyField('self', symmetrical=True)
     following_inherited = models.ManyToManyField('self', related_name='followers_concrete', symmetrical=False)
 
     # VIRTUAL fields

```

## Test Information

**Tests that should FAIL→PASS**: ["test_many_to_many_with_useless_related_name (invalid_models_tests.test_relative_fields.RelativeFieldTests)"]

**Tests that should PASS→PASS**: ["test_accessor_clash (invalid_models_tests.test_relative_fields.SelfReferentialFKClashTests)", "test_clash_under_explicit_related_name (invalid_models_tests.test_relative_fields.SelfReferentialFKClashTests)", "test_reverse_query_name_clash (invalid_models_tests.test_relative_fields.SelfReferentialFKClashTests)", "test_clash_parent_link (invalid_models_tests.test_relative_fields.ComplexClashTests)", "test_complex_clash (invalid_models_tests.test_relative_fields.ComplexClashTests)", "If ``through_fields`` kwarg is given, it must specify both", "test_intersection_foreign_object (invalid_models_tests.test_relative_fields.M2mThroughFieldsTests)", "Providing invalid field names to ManyToManyField.through_fields", "Mixing up the order of link fields to ManyToManyField.through_fields", "ManyToManyField accepts the ``through_fields`` kwarg", "test_superset_foreign_object (invalid_models_tests.test_relative_fields.M2mThroughFieldsTests)", "test_accessor_clash (invalid_models_tests.test_relative_fields.SelfReferentialM2MClashTests)", "test_clash_between_accessors (invalid_models_tests.test_relative_fields.SelfReferentialM2MClashTests)", "test_clash_under_explicit_related_name (invalid_models_tests.test_relative_fields.SelfReferentialM2MClashTests)", "test_reverse_query_name_clash (invalid_models_tests.test_relative_fields.SelfReferentialM2MClashTests)", "test_valid_model (invalid_models_tests.test_relative_fields.SelfReferentialM2MClashTests)", "test_fk_to_fk (invalid_models_tests.test_relative_fields.ExplicitRelatedNameClashTests)", "test_fk_to_integer (invalid_models_tests.test_relative_fields.ExplicitRelatedNameClashTests)", "test_fk_to_m2m (invalid_models_tests.test_relative_fields.ExplicitRelatedNameClashTests)", "test_m2m_to_fk (invalid_models_tests.test_relative_fields.ExplicitRelatedNameClashTests)", "test_m2m_to_integer (invalid_models_tests.test_relative_fields.ExplicitRelatedNameClashTests)", "test_m2m_to_m2m (invalid_models_tests.test_relative_fields.ExplicitRelatedNameClashTests)", "test_fk_to_fk (invalid_models_tests.test_relative_fields.ExplicitRelatedQueryNameClashTests)", "test_fk_to_integer (invalid_models_tests.test_relative_fields.ExplicitRelatedQueryNameClashTests)", "test_fk_to_m2m (invalid_models_tests.test_relative_fields.ExplicitRelatedQueryNameClashTests)", "test_hidden_fk_to_fk (invalid_models_tests.test_relative_fields.ExplicitRelatedQueryNameClashTests)", "test_hidden_fk_to_integer (invalid_models_tests.test_relative_fields.ExplicitRelatedQueryNameClashTests)", "test_hidden_fk_to_m2m (invalid_models_tests.test_relative_fields.ExplicitRelatedQueryNameClashTests)", "test_hidden_m2m_to_fk (invalid_models_tests.test_relative_fields.ExplicitRelatedQueryNameClashTests)", "test_hidden_m2m_to_integer (invalid_models_tests.test_relative_fields.ExplicitRelatedQueryNameClashTests)", "test_hidden_m2m_to_m2m (invalid_models_tests.test_relative_fields.ExplicitRelatedQueryNameClashTests)", "test_m2m_to_fk (invalid_models_tests.test_relative_fields.ExplicitRelatedQueryNameClashTests)", "test_m2m_to_integer (invalid_models_tests.test_relative_fields.ExplicitRelatedQueryNameClashTests)", "test_m2m_to_m2m (invalid_models_tests.test_relative_fields.ExplicitRelatedQueryNameClashTests)", "test_clash_between_accessors (invalid_models_tests.test_relative_fields.AccessorClashTests)", "test_fk_to_fk (invalid_models_tests.test_relative_fields.AccessorClashTests)", "test_fk_to_integer (invalid_models_tests.test_relative_fields.AccessorClashTests)", "test_fk_to_m2m (invalid_models_tests.test_relative_fields.AccessorClashTests)", "test_m2m_to_fk (invalid_models_tests.test_relative_fields.AccessorClashTests)", "test_m2m_to_integer (invalid_models_tests.test_relative_fields.AccessorClashTests)", "test_m2m_to_m2m (invalid_models_tests.test_relative_fields.AccessorClashTests)", "Ref #22047.", "test_no_clash_for_hidden_related_name (invalid_models_tests.test_relative_fields.AccessorClashTests)", "test_fk_to_fk (invalid_models_tests.test_relative_fields.ReverseQueryNameClashTests)", "test_fk_to_integer (invalid_models_tests.test_relative_fields.ReverseQueryNameClashTests)", "test_fk_to_m2m (invalid_models_tests.test_relative_fields.ReverseQueryNameClashTests)", "test_m2m_to_fk (invalid_models_tests.test_relative_fields.ReverseQueryNameClashTests)", "test_m2m_to_integer (invalid_models_tests.test_relative_fields.ReverseQueryNameClashTests)", "test_m2m_to_m2m (invalid_models_tests.test_relative_fields.ReverseQueryNameClashTests)", "test_no_clash_across_apps_without_accessor (invalid_models_tests.test_relative_fields.ReverseQueryNameClashTests)", "test_ambiguous_relationship_model_from (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_ambiguous_relationship_model_to (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_foreign_key_to_abstract_model (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "#25723 - Referenced model registration lookup should be run against the", "test_foreign_key_to_missing_model (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_foreign_key_to_non_unique_field (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_foreign_key_to_non_unique_field_under_explicit_model (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_foreign_key_to_partially_unique_field (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_foreign_key_to_unique_field_with_meta_constraint (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_foreign_object_to_non_unique_fields (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_foreign_object_to_partially_unique_field (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_foreign_object_to_unique_field_with_meta_constraint (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_invalid_related_query_name (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_m2m_to_abstract_model (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "#25723 - Through model registration lookup should be run against the", "test_many_to_many_to_missing_model (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_many_to_many_with_limit_choices_auto_created_no_warning (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_many_to_many_with_useless_options (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_missing_relationship_model (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_missing_relationship_model_on_model_check (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_not_swapped_model (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_nullable_primary_key (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_on_delete_set_default_without_default_value (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_on_delete_set_null_on_non_nullable_field (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_referencing_to_swapped_model (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_related_field_has_invalid_related_name (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_related_field_has_valid_related_name (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_relationship_model_missing_foreign_key (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_relationship_model_with_foreign_key_to_wrong_model (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_to_fields_exist (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_to_fields_not_checked_if_related_model_doesnt_exist (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_too_many_foreign_keys_in_self_referential_model (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_unique_m2m (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_valid_foreign_key_without_accessor (invalid_models_tests.test_relative_fields.RelativeFieldTests)", "test_auto_field (field_deconstruction.tests.FieldDeconstructionTests)", "test_big_integer_field (field_deconstruction.tests.FieldDeconstructionTests)", "test_binary_field (field_deconstruction.tests.FieldDeconstructionTests)", "test_boolean_field (field_deconstruction.tests.FieldDeconstructionTests)", "test_char_field (field_deconstruction.tests.FieldDeconstructionTests)", "test_char_field_choices (field_deconstruction.tests.FieldDeconstructionTests)", "test_csi_field (field_deconstruction.tests.FieldDeconstructionTests)", "test_date_field (field_deconstruction.tests.FieldDeconstructionTests)", "test_datetime_field (field_deconstruction.tests.FieldDeconstructionTests)", "test_db_tablespace (field_deconstruction.tests.FieldDeconstructionTests)", "test_decimal_field (field_deconstruction.tests.FieldDeconstructionTests)", "A DecimalField with decimal_places=0 should work (#22272).", "test_email_field (field_deconstruction.tests.FieldDeconstructionTests)", "test_file_field (field_deconstruction.tests.FieldDeconstructionTests)", "test_file_path_field (field_deconstruction.tests.FieldDeconstructionTests)", "test_float_field (field_deconstruction.tests.FieldDeconstructionTests)", "test_foreign_key (field_deconstruction.tests.FieldDeconstructionTests)", "test_foreign_key_swapped (field_deconstruction.tests.FieldDeconstructionTests)", "test_generic_ip_address_field (field_deconstruction.tests.FieldDeconstructionTests)", "test_image_field (field_deconstruction.tests.FieldDeconstructionTests)", "test_integer_field (field_deconstruction.tests.FieldDeconstructionTests)", "test_ip_address_field (field_deconstruction.tests.FieldDeconstructionTests)", "test_many_to_many_field (field_deconstruction.tests.FieldDeconstructionTests)", "test_many_to_many_field_related_name (field_deconstruction.tests.FieldDeconstructionTests)", "test_many_to_many_field_swapped (field_deconstruction.tests.FieldDeconstructionTests)", "Tests the outputting of the correct name if assigned one.", "test_one_to_one (field_deconstruction.tests.FieldDeconstructionTests)", "test_positive_big_integer_field (field_deconstruction.tests.FieldDeconstructionTests)", "test_positive_integer_field (field_deconstruction.tests.FieldDeconstructionTests)", "test_positive_small_integer_field (field_deconstruction.tests.FieldDeconstructionTests)", "test_slug_field (field_deconstruction.tests.FieldDeconstructionTests)", "test_small_integer_field (field_deconstruction.tests.FieldDeconstructionTests)", "test_text_field (field_deconstruction.tests.FieldDeconstructionTests)", "test_time_field (field_deconstruction.tests.FieldDeconstructionTests)", "test_url_field (field_deconstruction.tests.FieldDeconstructionTests)"]

**Base Commit**: 4fe3774c729f3fd5105b3001fe69a70bdca95ac3
**Environment Setup Commit**: 475cffd1d64c690cdad16ede4d5e81985738ceb4
