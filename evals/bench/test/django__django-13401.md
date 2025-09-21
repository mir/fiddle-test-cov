# django__django-13401

**Repository**: django/django
**Created**: 2020-09-09T11:19:00Z
**Version**: 3.2

## Problem Statement

Abstract model field should not be equal across models
Description
	
Consider the following models:
class A(models.Model):
	class Meta:
		abstract = True
	myfield = IntegerField()
class B(A):
	pass
class C(A):
	pass
If I pull the fields of B and C into a shared set, one will be de-duplicated away, because they compare as equal. I found this surprising, though in practice using a list was sufficient for my need. The root of the issue is that they compare equal, as fields only consider self.creation_counter when comparing for equality.
len({B._meta.get_field('myfield'), C._meta.get_field('myfield')}) == 1
B._meta.get_field('myfield') == C._meta.get_field('myfield')
We should adjust __eq__ so that if the field.model is different, they will compare unequal. Similarly, it is probably wise to adjust __hash__ and __lt__ to match.
When adjusting __lt__, it may be wise to order first by self.creation_counter so that cases not affected by this equality collision won't be re-ordered. In my experimental branch, there was one test that broke if I ordered them by model first.
I brought this up on IRC django-dev to check my intuitions, and those conversing with me there seemed to agree that the current behavior is not intuitive.


## Patch

```diff

diff --git a/django/db/models/fields/__init__.py b/django/db/models/fields/__init__.py
--- a/django/db/models/fields/__init__.py
+++ b/django/db/models/fields/__init__.py
@@ -516,17 +516,37 @@ def clone(self):
     def __eq__(self, other):
         # Needed for @total_ordering
         if isinstance(other, Field):
-            return self.creation_counter == other.creation_counter
+            return (
+                self.creation_counter == other.creation_counter and
+                getattr(self, 'model', None) == getattr(other, 'model', None)
+            )
         return NotImplemented
 
     def __lt__(self, other):
         # This is needed because bisect does not take a comparison function.
+        # Order by creation_counter first for backward compatibility.
         if isinstance(other, Field):
-            return self.creation_counter < other.creation_counter
+            if (
+                self.creation_counter != other.creation_counter or
+                not hasattr(self, 'model') and not hasattr(other, 'model')
+            ):
+                return self.creation_counter < other.creation_counter
+            elif hasattr(self, 'model') != hasattr(other, 'model'):
+                return not hasattr(self, 'model')  # Order no-model fields first
+            else:
+                # creation_counter's are equal, compare only models.
+                return (
+                    (self.model._meta.app_label, self.model._meta.model_name) <
+                    (other.model._meta.app_label, other.model._meta.model_name)
+                )
         return NotImplemented
 
     def __hash__(self):
-        return hash(self.creation_counter)
+        return hash((
+            self.creation_counter,
+            self.model._meta.app_label if hasattr(self, 'model') else None,
+            self.model._meta.model_name if hasattr(self, 'model') else None,
+        ))
 
     def __deepcopy__(self, memodict):
         # We don't have to deepcopy very much here, since most things are not


```

## Test Patch

```diff
diff --git a/tests/model_fields/tests.py b/tests/model_fields/tests.py
--- a/tests/model_fields/tests.py
+++ b/tests/model_fields/tests.py
@@ -102,6 +102,36 @@ def test_deconstruct_nested_field(self):
         name, path, args, kwargs = Nested.Field().deconstruct()
         self.assertEqual(path, 'model_fields.tests.Nested.Field')
 
+    def test_abstract_inherited_fields(self):
+        """Field instances from abstract models are not equal."""
+        class AbstractModel(models.Model):
+            field = models.IntegerField()
+
+            class Meta:
+                abstract = True
+
+        class InheritAbstractModel1(AbstractModel):
+            pass
+
+        class InheritAbstractModel2(AbstractModel):
+            pass
+
+        abstract_model_field = AbstractModel._meta.get_field('field')
+        inherit1_model_field = InheritAbstractModel1._meta.get_field('field')
+        inherit2_model_field = InheritAbstractModel2._meta.get_field('field')
+
+        self.assertNotEqual(abstract_model_field, inherit1_model_field)
+        self.assertNotEqual(abstract_model_field, inherit2_model_field)
+        self.assertNotEqual(inherit1_model_field, inherit2_model_field)
+
+        self.assertLess(abstract_model_field, inherit1_model_field)
+        self.assertLess(abstract_model_field, inherit2_model_field)
+        self.assertLess(inherit1_model_field, inherit2_model_field)
+
+        self.assertNotEqual(hash(abstract_model_field), hash(inherit1_model_field))
+        self.assertNotEqual(hash(abstract_model_field), hash(inherit2_model_field))
+        self.assertNotEqual(hash(inherit1_model_field), hash(inherit2_model_field))
+
 
 class ChoicesTests(SimpleTestCase):
 

```

## Test Information

**Tests that should FAIL→PASS**: ["Field instances from abstract models are not equal."]

**Tests that should PASS→PASS**: ["test_blank_in_choices (model_fields.tests.GetChoicesTests)", "test_blank_in_grouped_choices (model_fields.tests.GetChoicesTests)", "test_empty_choices (model_fields.tests.GetChoicesTests)", "test_lazy_strings_not_evaluated (model_fields.tests.GetChoicesTests)", "test_get_choices (model_fields.tests.GetChoicesLimitChoicesToTests)", "test_get_choices_reverse_related_field (model_fields.tests.GetChoicesLimitChoicesToTests)", "test_choices_and_field_display (model_fields.tests.GetFieldDisplayTests)", "test_empty_iterator_choices (model_fields.tests.GetFieldDisplayTests)", "A translated display value is coerced to str.", "test_iterator_choices (model_fields.tests.GetFieldDisplayTests)", "test_overriding_FIELD_display (model_fields.tests.GetFieldDisplayTests)", "test_overriding_inherited_FIELD_display (model_fields.tests.GetFieldDisplayTests)", "Can supply a custom choices form class to Field.formfield()", "deconstruct() uses __qualname__ for nested class support.", "Field instances can be pickled.", "test_field_name (model_fields.tests.BasicFieldTests)", "Fields are ordered based on their creation.", "test_field_repr (model_fields.tests.BasicFieldTests)", "__repr__() uses __qualname__ for nested class support.", "test_field_str (model_fields.tests.BasicFieldTests)", "test_field_verbose_name (model_fields.tests.BasicFieldTests)", "Field.formfield() sets disabled for fields with choices.", "test_show_hidden_initial (model_fields.tests.BasicFieldTests)", "test_get_choices (model_fields.tests.GetChoicesOrderingTests)", "test_get_choices_default_ordering (model_fields.tests.GetChoicesOrderingTests)", "test_get_choices_reverse_related_field (model_fields.tests.GetChoicesOrderingTests)", "test_get_choices_reverse_related_field_default_ordering (model_fields.tests.GetChoicesOrderingTests)", "test_check (model_fields.tests.ChoicesTests)", "test_choices (model_fields.tests.ChoicesTests)", "test_flatchoices (model_fields.tests.ChoicesTests)", "test_formfield (model_fields.tests.ChoicesTests)", "test_invalid_choice (model_fields.tests.ChoicesTests)"]

**Base Commit**: 453967477e3ddae704cd739eac2449c0e13d464c
**Environment Setup Commit**: 65dfb06a1ab56c238cc80f5e1c31f61210c4577d
