# django__django-14672

**Repository**: django/django
**Created**: 2021-07-20T10:47:34Z
**Version**: 4.0

## Problem Statement

Missing call `make_hashable` on `through_fields` in `ManyToManyRel`
Description
	
In 3.2 identity property has been added to all ForeignObjectRel to make it possible to compare them. A hash is derived from said identity and it's possible because identity is a tuple. To make limit_choices_to hashable (one of this tuple elements), ​there's a call to make_hashable.
It happens that through_fields can be a list. In such case, this make_hashable call is missing in ​ManyToManyRel.
For some reason it only fails on checking proxy model. I think proxy models have 29 checks and normal ones 24, hence the issue, but that's just a guess.
Minimal repro:
class Parent(models.Model):
	name = models.CharField(max_length=256)
class ProxyParent(Parent):
	class Meta:
		proxy = True
class Child(models.Model):
	parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
	many_to_many_field = models.ManyToManyField(
		to=Parent,
		through="ManyToManyModel",
		through_fields=['child', 'parent'],
		related_name="something"
	)
class ManyToManyModel(models.Model):
	parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='+')
	child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='+')
	second_child = models.ForeignKey(Child, on_delete=models.CASCADE, null=True, default=None)
Which will result in 
 File "manage.py", line 23, in <module>
	main()
 File "manage.py", line 19, in main
	execute_from_command_line(sys.argv)
 File "/home/tom/PycharmProjects/broken_m2m_project/venv/lib/python3.8/site-packages/django/core/management/__init__.py", line 419, in execute_from_command_line
	utility.execute()
 File "/home/tom/PycharmProjects/broken_m2m_project/venv/lib/python3.8/site-packages/django/core/management/__init__.py", line 413, in execute
	self.fetch_command(subcommand).run_from_argv(self.argv)
 File "/home/tom/PycharmProjects/broken_m2m_project/venv/lib/python3.8/site-packages/django/core/management/base.py", line 354, in run_from_argv
	self.execute(*args, **cmd_options)
 File "/home/tom/PycharmProjects/broken_m2m_project/venv/lib/python3.8/site-packages/django/core/management/base.py", line 393, in execute
	self.check()
 File "/home/tom/PycharmProjects/broken_m2m_project/venv/lib/python3.8/site-packages/django/core/management/base.py", line 419, in check
	all_issues = checks.run_checks(
 File "/home/tom/PycharmProjects/broken_m2m_project/venv/lib/python3.8/site-packages/django/core/checks/registry.py", line 76, in run_checks
	new_errors = check(app_configs=app_configs, databases=databases)
 File "/home/tom/PycharmProjects/broken_m2m_project/venv/lib/python3.8/site-packages/django/core/checks/model_checks.py", line 34, in check_all_models
	errors.extend(model.check(**kwargs))
 File "/home/tom/PycharmProjects/broken_m2m_project/venv/lib/python3.8/site-packages/django/db/models/base.py", line 1277, in check
	*cls._check_field_name_clashes(),
 File "/home/tom/PycharmProjects/djangbroken_m2m_projectProject/venv/lib/python3.8/site-packages/django/db/models/base.py", line 1465, in _check_field_name_clashes
	if f not in used_fields:
 File "/home/tom/PycharmProjects/broken_m2m_project/venv/lib/python3.8/site-packages/django/db/models/fields/reverse_related.py", line 140, in __hash__
	return hash(self.identity)
TypeError: unhashable type: 'list'
Solution: Add missing make_hashable call on self.through_fields in ManyToManyRel.
Missing call `make_hashable` on `through_fields` in `ManyToManyRel`
Description
	
In 3.2 identity property has been added to all ForeignObjectRel to make it possible to compare them. A hash is derived from said identity and it's possible because identity is a tuple. To make limit_choices_to hashable (one of this tuple elements), ​there's a call to make_hashable.
It happens that through_fields can be a list. In such case, this make_hashable call is missing in ​ManyToManyRel.
For some reason it only fails on checking proxy model. I think proxy models have 29 checks and normal ones 24, hence the issue, but that's just a guess.
Minimal repro:
class Parent(models.Model):
	name = models.CharField(max_length=256)
class ProxyParent(Parent):
	class Meta:
		proxy = True
class Child(models.Model):
	parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
	many_to_many_field = models.ManyToManyField(
		to=Parent,
		through="ManyToManyModel",
		through_fields=['child', 'parent'],
		related_name="something"
	)
class ManyToManyModel(models.Model):
	parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='+')
	child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='+')
	second_child = models.ForeignKey(Child, on_delete=models.CASCADE, null=True, default=None)
Which will result in 
 File "manage.py", line 23, in <module>
	main()
 File "manage.py", line 19, in main
	execute_from_command_line(sys.argv)
 File "/home/tom/PycharmProjects/broken_m2m_project/venv/lib/python3.8/site-packages/django/core/management/__init__.py", line 419, in execute_from_command_line
	utility.execute()
 File "/home/tom/PycharmProjects/broken_m2m_project/venv/lib/python3.8/site-packages/django/core/management/__init__.py", line 413, in execute
	self.fetch_command(subcommand).run_from_argv(self.argv)
 File "/home/tom/PycharmProjects/broken_m2m_project/venv/lib/python3.8/site-packages/django/core/management/base.py", line 354, in run_from_argv
	self.execute(*args, **cmd_options)
 File "/home/tom/PycharmProjects/broken_m2m_project/venv/lib/python3.8/site-packages/django/core/management/base.py", line 393, in execute
	self.check()
 File "/home/tom/PycharmProjects/broken_m2m_project/venv/lib/python3.8/site-packages/django/core/management/base.py", line 419, in check
	all_issues = checks.run_checks(
 File "/home/tom/PycharmProjects/broken_m2m_project/venv/lib/python3.8/site-packages/django/core/checks/registry.py", line 76, in run_checks
	new_errors = check(app_configs=app_configs, databases=databases)
 File "/home/tom/PycharmProjects/broken_m2m_project/venv/lib/python3.8/site-packages/django/core/checks/model_checks.py", line 34, in check_all_models
	errors.extend(model.check(**kwargs))
 File "/home/tom/PycharmProjects/broken_m2m_project/venv/lib/python3.8/site-packages/django/db/models/base.py", line 1277, in check
	*cls._check_field_name_clashes(),
 File "/home/tom/PycharmProjects/djangbroken_m2m_projectProject/venv/lib/python3.8/site-packages/django/db/models/base.py", line 1465, in _check_field_name_clashes
	if f not in used_fields:
 File "/home/tom/PycharmProjects/broken_m2m_project/venv/lib/python3.8/site-packages/django/db/models/fields/reverse_related.py", line 140, in __hash__
	return hash(self.identity)
TypeError: unhashable type: 'list'
Solution: Add missing make_hashable call on self.through_fields in ManyToManyRel.


## Patch

```diff

diff --git a/django/db/models/fields/reverse_related.py b/django/db/models/fields/reverse_related.py
--- a/django/db/models/fields/reverse_related.py
+++ b/django/db/models/fields/reverse_related.py
@@ -310,7 +310,7 @@ def __init__(self, field, to, related_name=None, related_query_name=None,
     def identity(self):
         return super().identity + (
             self.through,
-            self.through_fields,
+            make_hashable(self.through_fields),
             self.db_constraint,
         )
 


```

## Test Patch

```diff
diff --git a/tests/invalid_models_tests/test_models.py b/tests/invalid_models_tests/test_models.py
--- a/tests/invalid_models_tests/test_models.py
+++ b/tests/invalid_models_tests/test_models.py
@@ -821,6 +821,33 @@ class Child(Parent):
             )
         ])
 
+    def test_field_name_clash_with_m2m_through(self):
+        class Parent(models.Model):
+            clash_id = models.IntegerField()
+
+        class Child(Parent):
+            clash = models.ForeignKey('Child', models.CASCADE)
+
+        class Model(models.Model):
+            parents = models.ManyToManyField(
+                to=Parent,
+                through='Through',
+                through_fields=['parent', 'model'],
+            )
+
+        class Through(models.Model):
+            parent = models.ForeignKey(Parent, models.CASCADE)
+            model = models.ForeignKey(Model, models.CASCADE)
+
+        self.assertEqual(Child.check(), [
+            Error(
+                "The field 'clash' clashes with the field 'clash_id' from "
+                "model 'invalid_models_tests.parent'.",
+                obj=Child._meta.get_field('clash'),
+                id='models.E006',
+            )
+        ])
+
     def test_multiinheritance_clash(self):
         class Mother(models.Model):
             clash = models.IntegerField()
diff --git a/tests/m2m_through/models.py b/tests/m2m_through/models.py
--- a/tests/m2m_through/models.py
+++ b/tests/m2m_through/models.py
@@ -11,6 +11,10 @@ class Meta:
         ordering = ('name',)
 
 
+class PersonChild(Person):
+    pass
+
+
 class Group(models.Model):
     name = models.CharField(max_length=128)
     members = models.ManyToManyField(Person, through='Membership')
@@ -85,8 +89,9 @@ class SymmetricalFriendship(models.Model):
 class Event(models.Model):
     title = models.CharField(max_length=50)
     invitees = models.ManyToManyField(
-        Person, through='Invitation',
-        through_fields=('event', 'invitee'),
+        to=Person,
+        through='Invitation',
+        through_fields=['event', 'invitee'],
         related_name='events_invited',
     )
 
diff --git a/tests/m2m_through/tests.py b/tests/m2m_through/tests.py
--- a/tests/m2m_through/tests.py
+++ b/tests/m2m_through/tests.py
@@ -6,8 +6,8 @@
 
 from .models import (
     CustomMembership, Employee, Event, Friendship, Group, Ingredient,
-    Invitation, Membership, Person, PersonSelfRefM2M, Recipe, RecipeIngredient,
-    Relationship, SymmetricalFriendship,
+    Invitation, Membership, Person, PersonChild, PersonSelfRefM2M, Recipe,
+    RecipeIngredient, Relationship, SymmetricalFriendship,
 )
 
 
@@ -20,6 +20,13 @@ def setUpTestData(cls):
         cls.rock = Group.objects.create(name='Rock')
         cls.roll = Group.objects.create(name='Roll')
 
+    def test_reverse_inherited_m2m_with_through_fields_list_hashable(self):
+        reverse_m2m = Person._meta.get_field('events_invited')
+        self.assertEqual(reverse_m2m.through_fields, ['event', 'invitee'])
+        inherited_reverse_m2m = PersonChild._meta.get_field('events_invited')
+        self.assertEqual(inherited_reverse_m2m.through_fields, ['event', 'invitee'])
+        self.assertEqual(hash(reverse_m2m), hash(inherited_reverse_m2m))
+
     def test_retrieve_intermediate_items(self):
         Membership.objects.create(person=self.jim, group=self.rock)
         Membership.objects.create(person=self.jane, group=self.rock)

```

## Test Information

**Tests that should FAIL→PASS**: ["test_multiple_autofields (invalid_models_tests.test_models.MultipleAutoFieldsTests)", "test_db_column_clash (invalid_models_tests.test_models.FieldNamesTests)", "test_ending_with_underscore (invalid_models_tests.test_models.FieldNamesTests)", "test_including_separator (invalid_models_tests.test_models.FieldNamesTests)", "test_pk (invalid_models_tests.test_models.FieldNamesTests)", "test_check_jsonfield (invalid_models_tests.test_models.JSONFieldTests)", "test_check_jsonfield_required_db_features (invalid_models_tests.test_models.JSONFieldTests)", "test_ordering_pointing_to_json_field_value (invalid_models_tests.test_models.JSONFieldTests)", "test_choices (m2m_through.tests.M2mThroughToFieldsTests)", "test_retrieval (m2m_through.tests.M2mThroughToFieldsTests)", "test_list_containing_non_iterable (invalid_models_tests.test_models.UniqueTogetherTests)", "test_non_iterable (invalid_models_tests.test_models.UniqueTogetherTests)", "test_non_list (invalid_models_tests.test_models.UniqueTogetherTests)", "test_pointing_to_fk (invalid_models_tests.test_models.UniqueTogetherTests)", "test_pointing_to_m2m (invalid_models_tests.test_models.UniqueTogetherTests)", "test_pointing_to_missing_field (invalid_models_tests.test_models.UniqueTogetherTests)", "test_valid_model (invalid_models_tests.test_models.UniqueTogetherTests)", "test_list_containing_non_iterable (invalid_models_tests.test_models.IndexTogetherTests)", "test_non_iterable (invalid_models_tests.test_models.IndexTogetherTests)", "test_non_list (invalid_models_tests.test_models.IndexTogetherTests)", "test_pointing_to_fk (invalid_models_tests.test_models.IndexTogetherTests)", "test_pointing_to_m2m_field (invalid_models_tests.test_models.IndexTogetherTests)", "test_pointing_to_missing_field (invalid_models_tests.test_models.IndexTogetherTests)", "test_pointing_to_non_local_field (invalid_models_tests.test_models.IndexTogetherTests)", "test_field_name_clash_with_child_accessor (invalid_models_tests.test_models.ShadowingFieldsTests)", "test_field_name_clash_with_m2m_through (invalid_models_tests.test_models.ShadowingFieldsTests)", "test_id_clash (invalid_models_tests.test_models.ShadowingFieldsTests)", "test_inheritance_clash (invalid_models_tests.test_models.ShadowingFieldsTests)", "test_multigeneration_inheritance (invalid_models_tests.test_models.ShadowingFieldsTests)", "test_multiinheritance_clash (invalid_models_tests.test_models.ShadowingFieldsTests)", "test_func_index (invalid_models_tests.test_models.IndexesTests)", "test_func_index_complex_expression_custom_lookup (invalid_models_tests.test_models.IndexesTests)", "test_func_index_pointing_to_fk (invalid_models_tests.test_models.IndexesTests)", "test_func_index_pointing_to_m2m_field (invalid_models_tests.test_models.IndexesTests)", "test_func_index_pointing_to_missing_field (invalid_models_tests.test_models.IndexesTests)", "test_func_index_pointing_to_missing_field_nested (invalid_models_tests.test_models.IndexesTests)", "test_func_index_pointing_to_non_local_field (invalid_models_tests.test_models.IndexesTests)", "test_func_index_required_db_features (invalid_models_tests.test_models.IndexesTests)", "test_index_with_condition (invalid_models_tests.test_models.IndexesTests)", "test_index_with_condition_required_db_features (invalid_models_tests.test_models.IndexesTests)", "test_index_with_include (invalid_models_tests.test_models.IndexesTests)", "test_index_with_include_required_db_features (invalid_models_tests.test_models.IndexesTests)", "test_max_name_length (invalid_models_tests.test_models.IndexesTests)", "test_name_constraints (invalid_models_tests.test_models.IndexesTests)", "test_pointing_to_fk (invalid_models_tests.test_models.IndexesTests)", "test_pointing_to_m2m_field (invalid_models_tests.test_models.IndexesTests)", "test_pointing_to_missing_field (invalid_models_tests.test_models.IndexesTests)", "test_pointing_to_non_local_field (invalid_models_tests.test_models.IndexesTests)", "test_add_on_symmetrical_m2m_with_intermediate_model (m2m_through.tests.M2mThroughReferentialTests)", "test_self_referential_empty_qs (m2m_through.tests.M2mThroughReferentialTests)", "test_self_referential_non_symmetrical_both (m2m_through.tests.M2mThroughReferentialTests)", "test_self_referential_non_symmetrical_clear_first_side (m2m_through.tests.M2mThroughReferentialTests)", "test_self_referential_non_symmetrical_first_side (m2m_through.tests.M2mThroughReferentialTests)", "test_self_referential_non_symmetrical_second_side (m2m_through.tests.M2mThroughReferentialTests)", "test_self_referential_symmetrical (m2m_through.tests.M2mThroughReferentialTests)", "test_set_on_symmetrical_m2m_with_intermediate_model (m2m_through.tests.M2mThroughReferentialTests)", "test_through_fields_self_referential (m2m_through.tests.M2mThroughReferentialTests)", "test_just_order_with_respect_to_no_errors (invalid_models_tests.test_models.OtherModelTests)", "test_just_ordering_no_errors (invalid_models_tests.test_models.OtherModelTests)", "test_lazy_reference_checks (invalid_models_tests.test_models.OtherModelTests)", "test_m2m_autogenerated_table_name_clash (invalid_models_tests.test_models.OtherModelTests)", "test_m2m_autogenerated_table_name_clash_database_routers_installed (invalid_models_tests.test_models.OtherModelTests)", "test_m2m_field_table_name_clash (invalid_models_tests.test_models.OtherModelTests)", "test_m2m_field_table_name_clash_database_routers_installed (invalid_models_tests.test_models.OtherModelTests)", "test_m2m_table_name_clash (invalid_models_tests.test_models.OtherModelTests)", "test_m2m_table_name_clash_database_routers_installed (invalid_models_tests.test_models.OtherModelTests)", "test_m2m_to_concrete_and_proxy_allowed (invalid_models_tests.test_models.OtherModelTests)", "test_m2m_unmanaged_shadow_models_not_checked (invalid_models_tests.test_models.OtherModelTests)", "test_name_beginning_with_underscore (invalid_models_tests.test_models.OtherModelTests)", "test_name_contains_double_underscores (invalid_models_tests.test_models.OtherModelTests)", "test_name_ending_with_underscore (invalid_models_tests.test_models.OtherModelTests)", "test_non_valid (invalid_models_tests.test_models.OtherModelTests)", "test_onetoone_with_explicit_parent_link_parent_model (invalid_models_tests.test_models.OtherModelTests)", "test_onetoone_with_parent_model (invalid_models_tests.test_models.OtherModelTests)", "test_ordering_allows_registered_lookups (invalid_models_tests.test_models.OtherModelTests)", "test_ordering_non_iterable (invalid_models_tests.test_models.OtherModelTests)", "test_ordering_pointing_multiple_times_to_model_fields (invalid_models_tests.test_models.OtherModelTests)", "test_ordering_pointing_to_foreignkey_field (invalid_models_tests.test_models.OtherModelTests)", "test_ordering_pointing_to_lookup_not_transform (invalid_models_tests.test_models.OtherModelTests)", "test_ordering_pointing_to_missing_field (invalid_models_tests.test_models.OtherModelTests)", "test_ordering_pointing_to_missing_foreignkey_field (invalid_models_tests.test_models.OtherModelTests)", "test_ordering_pointing_to_missing_related_field (invalid_models_tests.test_models.OtherModelTests)", "test_ordering_pointing_to_missing_related_model_field (invalid_models_tests.test_models.OtherModelTests)", "test_ordering_pointing_to_non_related_field (invalid_models_tests.test_models.OtherModelTests)", "test_ordering_pointing_to_related_model_pk (invalid_models_tests.test_models.OtherModelTests)", "test_ordering_pointing_to_two_related_model_field (invalid_models_tests.test_models.OtherModelTests)", "test_ordering_with_order_with_respect_to (invalid_models_tests.test_models.OtherModelTests)", "test_property_and_related_field_accessor_clash (invalid_models_tests.test_models.OtherModelTests)", "test_single_primary_key (invalid_models_tests.test_models.OtherModelTests)", "test_swappable_missing_app (invalid_models_tests.test_models.OtherModelTests)", "test_swappable_missing_app_name (invalid_models_tests.test_models.OtherModelTests)", "test_two_m2m_through_same_model_with_different_through_fields (invalid_models_tests.test_models.OtherModelTests)", "test_two_m2m_through_same_relationship (invalid_models_tests.test_models.OtherModelTests)", "test_unique_primary_key (invalid_models_tests.test_models.OtherModelTests)", "test_check_constraint_pointing_to_fk (invalid_models_tests.test_models.ConstraintsTests)", "test_check_constraint_pointing_to_joined_fields (invalid_models_tests.test_models.ConstraintsTests)", "test_check_constraint_pointing_to_joined_fields_complex_check (invalid_models_tests.test_models.ConstraintsTests)", "test_check_constraint_pointing_to_m2m_field (invalid_models_tests.test_models.ConstraintsTests)", "test_check_constraint_pointing_to_missing_field (invalid_models_tests.test_models.ConstraintsTests)", "test_check_constraint_pointing_to_non_local_field (invalid_models_tests.test_models.ConstraintsTests)", "test_check_constraint_pointing_to_pk (invalid_models_tests.test_models.ConstraintsTests)", "test_check_constraint_pointing_to_reverse_fk (invalid_models_tests.test_models.ConstraintsTests)", "test_check_constraint_pointing_to_reverse_o2o (invalid_models_tests.test_models.ConstraintsTests)", "test_check_constraints (invalid_models_tests.test_models.ConstraintsTests)", "test_check_constraints_required_db_features (invalid_models_tests.test_models.ConstraintsTests)", "test_deferrable_unique_constraint (invalid_models_tests.test_models.ConstraintsTests)", "test_deferrable_unique_constraint_required_db_features (invalid_models_tests.test_models.ConstraintsTests)", "test_func_unique_constraint (invalid_models_tests.test_models.ConstraintsTests)", "test_func_unique_constraint_expression_custom_lookup (invalid_models_tests.test_models.ConstraintsTests)", "test_func_unique_constraint_pointing_to_fk (invalid_models_tests.test_models.ConstraintsTests)", "test_func_unique_constraint_pointing_to_m2m_field (invalid_models_tests.test_models.ConstraintsTests)", "test_func_unique_constraint_pointing_to_missing_field (invalid_models_tests.test_models.ConstraintsTests)", "test_func_unique_constraint_pointing_to_missing_field_nested (invalid_models_tests.test_models.ConstraintsTests)", "test_func_unique_constraint_pointing_to_non_local_field (invalid_models_tests.test_models.ConstraintsTests)", "test_func_unique_constraint_required_db_features (invalid_models_tests.test_models.ConstraintsTests)", "test_unique_constraint_condition_pointing_to_joined_fields (invalid_models_tests.test_models.ConstraintsTests)", "test_unique_constraint_condition_pointing_to_missing_field (invalid_models_tests.test_models.ConstraintsTests)", "test_unique_constraint_pointing_to_fk (invalid_models_tests.test_models.ConstraintsTests)", "test_unique_constraint_pointing_to_m2m_field (invalid_models_tests.test_models.ConstraintsTests)", "test_unique_constraint_pointing_to_missing_field (invalid_models_tests.test_models.ConstraintsTests)", "test_unique_constraint_pointing_to_non_local_field (invalid_models_tests.test_models.ConstraintsTests)", "test_unique_constraint_pointing_to_reverse_o2o (invalid_models_tests.test_models.ConstraintsTests)", "test_unique_constraint_with_condition (invalid_models_tests.test_models.ConstraintsTests)", "test_unique_constraint_with_condition_required_db_features (invalid_models_tests.test_models.ConstraintsTests)", "test_unique_constraint_with_include (invalid_models_tests.test_models.ConstraintsTests)", "test_unique_constraint_with_include_required_db_features (invalid_models_tests.test_models.ConstraintsTests)", "test_add_on_m2m_with_intermediate_model (m2m_through.tests.M2mThroughTests)", "test_add_on_m2m_with_intermediate_model_callable_through_default (m2m_through.tests.M2mThroughTests)", "test_add_on_m2m_with_intermediate_model_value_required (m2m_through.tests.M2mThroughTests)", "test_add_on_m2m_with_intermediate_model_value_required_fails (m2m_through.tests.M2mThroughTests)", "test_add_on_reverse_m2m_with_intermediate_model (m2m_through.tests.M2mThroughTests)", "test_clear_on_reverse_removes_all_the_m2m_relationships (m2m_through.tests.M2mThroughTests)", "test_clear_removes_all_the_m2m_relationships (m2m_through.tests.M2mThroughTests)", "test_create_on_m2m_with_intermediate_model (m2m_through.tests.M2mThroughTests)", "test_create_on_m2m_with_intermediate_model_callable_through_default (m2m_through.tests.M2mThroughTests)", "test_create_on_m2m_with_intermediate_model_value_required (m2m_through.tests.M2mThroughTests)", "test_create_on_m2m_with_intermediate_model_value_required_fails (m2m_through.tests.M2mThroughTests)", "test_create_on_reverse_m2m_with_intermediate_model (m2m_through.tests.M2mThroughTests)", "test_custom_related_name_doesnt_conflict_with_fky_related_name (m2m_through.tests.M2mThroughTests)", "test_custom_related_name_forward_empty_qs (m2m_through.tests.M2mThroughTests)", "test_custom_related_name_forward_non_empty_qs (m2m_through.tests.M2mThroughTests)", "test_custom_related_name_reverse_empty_qs (m2m_through.tests.M2mThroughTests)", "test_custom_related_name_reverse_non_empty_qs (m2m_through.tests.M2mThroughTests)", "test_filter_on_intermediate_model (m2m_through.tests.M2mThroughTests)", "test_get_on_intermediate_model (m2m_through.tests.M2mThroughTests)", "test_get_or_create_on_m2m_with_intermediate_model_value_required (m2m_through.tests.M2mThroughTests)", "test_get_or_create_on_m2m_with_intermediate_model_value_required_fails (m2m_through.tests.M2mThroughTests)", "test_order_by_relational_field_through_model (m2m_through.tests.M2mThroughTests)", "test_query_first_model_by_intermediate_model_attribute (m2m_through.tests.M2mThroughTests)", "test_query_model_by_attribute_name_of_related_model (m2m_through.tests.M2mThroughTests)", "test_query_model_by_custom_related_name (m2m_through.tests.M2mThroughTests)", "test_query_model_by_intermediate_can_return_non_unique_queryset (m2m_through.tests.M2mThroughTests)", "test_query_model_by_related_model_name (m2m_through.tests.M2mThroughTests)", "test_query_second_model_by_intermediate_model_attribute (m2m_through.tests.M2mThroughTests)", "test_remove_on_m2m_with_intermediate_model (m2m_through.tests.M2mThroughTests)", "test_remove_on_m2m_with_intermediate_model_multiple (m2m_through.tests.M2mThroughTests)", "test_remove_on_reverse_m2m_with_intermediate_model (m2m_through.tests.M2mThroughTests)", "test_retrieve_intermediate_items (m2m_through.tests.M2mThroughTests)", "test_retrieve_reverse_intermediate_items (m2m_through.tests.M2mThroughTests)", "test_reverse_inherited_m2m_with_through_fields_list_hashable (m2m_through.tests.M2mThroughTests)", "test_set_on_m2m_with_intermediate_model (m2m_through.tests.M2mThroughTests)", "test_set_on_m2m_with_intermediate_model_callable_through_default (m2m_through.tests.M2mThroughTests)", "test_set_on_m2m_with_intermediate_model_value_required (m2m_through.tests.M2mThroughTests)", "test_set_on_m2m_with_intermediate_model_value_required_fails (m2m_through.tests.M2mThroughTests)", "test_set_on_reverse_m2m_with_intermediate_model (m2m_through.tests.M2mThroughTests)", "Relations with intermediary tables with multiple FKs", "test_update_or_create_on_m2m_with_intermediate_model_value_required (m2m_through.tests.M2mThroughTests)", "test_update_or_create_on_m2m_with_intermediate_model_value_required_fails (m2m_through.tests.M2mThroughTests)"]

**Tests that should PASS→PASS**: []

**Base Commit**: 00ea883ef56fb5e092cbe4a6f7ff2e7470886ac4
**Environment Setup Commit**: 475cffd1d64c690cdad16ede4d5e81985738ceb4
