# django__django-11999

**Repository**: django/django
**Created**: 2019-10-31T10:39:18Z
**Version**: 3.1

## Problem Statement

Cannot override get_FOO_display() in Django 2.2+.
Description
	
I cannot override the get_FIELD_display function on models since version 2.2. It works in version 2.1.
Example:
class FooBar(models.Model):
	foo_bar = models.CharField(_("foo"), choices=[(1, 'foo'), (2, 'bar')])
	def __str__(self):
		return self.get_foo_bar_display() # This returns 'foo' or 'bar' in 2.2, but 'something' in 2.1
	def get_foo_bar_display(self):
		return "something"
What I expect is that I should be able to override this function.


## Hints

Thanks for this report. Regression in a68ea231012434b522ce45c513d84add516afa60. Reproduced at 54a7b021125d23a248e70ba17bf8b10bc8619234.
OK, I have a lead on this. Not at all happy about how it looks at first pass, but I'll a proof of concept PR together for it tomorrow AM.
I don't think it should be marked as blocker since it looks like it was never supported, because it depends on the order of attrs passed in ModelBase.__new__(). So on Django 2.1 and Python 3.7: In [1]: import django ...: django.VERSION In [2]: from django.db import models ...: ...: class FooBar(models.Model): ...: def get_foo_bar_display(self): ...: return "something" ...: ...: foo_bar = models.CharField("foo", choices=[(1, 'foo'), (2, 'bar')]) ...: ...: def __str__(self): ...: return self.get_foo_bar_display() # This returns 'foo' or 'bar' in 2.2, but 'something' in 2.1 ...: ...: class Meta: ...: app_label = 'test' ...: ...: FooBar(foo_bar=1) Out[2]: <FooBar: foo> Before ​Python 3.6 the order of attrs wasn't defined at all.
Sergey, an example from the ticket description works for me with Django 2.1 and Python 3.6, 3.7 and 3.8.
In [2]: import django ...: django.VERSION Out[2]: (2, 1, 13, 'final', 0) In [3]: import sys ...: sys.version Out[3]: '3.5.7 (default, Oct 17 2019, 07:04:41) \n[GCC 8.3.0]' In [4]: from django.db import models ...: ...: class FooBar(models.Model): ...: foo_bar = models.CharField("foo", choices=[(1, 'foo'), (2, 'bar')]) ...: ...: def __str__(self): ...: return self.get_foo_bar_display() # This returns 'foo' or 'bar' in 2.2, but 'something' in 2.1 ...: ...: def get_foo_bar_display(self): ...: return "something" ...: ...: class Meta: ...: app_label = 'test' ...: ...: FooBar(foo_bar=1) Out[4]: <FooBar: foo>
OK, so there is a behaviour change here, but Sergey is correct that it does depend on attr order, so it's hard to say that this can be said to ever have been thought of as supported, with the exact example provided. This example produces the opposite result on 2.1 (even on >=PY36): def test_overriding_display_backwards(self): class FooBar2(models.Model): def get_foo_bar_display(self): return "something" foo_bar = models.CharField("foo", choices=[(1, 'foo'), (2, 'bar')]) f = FooBar2(foo_bar=1) # This returns 'foo' or 'bar' in both 2.2 and 2.1 self.assertEqual(f.get_foo_bar_display(), "foo") Because get_foo_bar_display() is defined before foo_bar is gets replaced in the the add_to_class() step. Semantically order shouldn't make a difference. Given that it does, I can't see that we're bound to maintain that behaviour. (There's a possible fix in Field.contribute_to_class() but implementing that just reverses the pass/fail behaviour depending on order...) Rather, the correct way to implement this on 2.2+ is: def test_overriding_display(self): class FooBar(models.Model): foo_bar = models.CharField("foo", choices=[(1, 'foo'), (2, 'bar')]) def _get_FIELD_display(self, field): if field.attname == 'foo_bar': return "something" return super()._get_FIELD_display(field) f = FooBar(foo_bar=1) self.assertEqual(f.get_foo_bar_display(), "something") This is stable for declaration order on version 2.2+. This approach requires overriding _get_FIELD_display() before declaring fields on 2.1, because otherwise Model._get_FIELD_display() is picked up during Field.contribute_to_class(). This ordering dependency is, ultimately, the same issue that was addressed in a68ea231012434b522ce45c513d84add516afa60, and the follow-up in #30254. The behaviour in 2.1 (and before) was incorrect. Yes, there's a behaviour change here but it's a bugfix, and all bugfixes are breaking changes if you're depending on the broken behaviour. I'm going to downgrade this from Release Blocker accordingly. I'll reclassify this as a Documentation issue and provide the working example, as overriding _get_FIELD_display() is a legitimate use-case I'd guess.
Replying to Carlton Gibson: (There's a possible fix in Field.contribute_to_class() but implementing that just reverses the pass/fail behaviour depending on order...) Doesn't this fix it? if not hasattr(cls, 'get_%s_display' % self.name): setattr(cls, 'get_%s_display' % self.name, partialmethod(cls._get_FIELD_display, field=self))

## Patch

```diff

diff --git a/django/db/models/fields/__init__.py b/django/db/models/fields/__init__.py
--- a/django/db/models/fields/__init__.py
+++ b/django/db/models/fields/__init__.py
@@ -763,8 +763,12 @@ def contribute_to_class(self, cls, name, private_only=False):
             if not getattr(cls, self.attname, None):
                 setattr(cls, self.attname, self.descriptor_class(self))
         if self.choices is not None:
-            setattr(cls, 'get_%s_display' % self.name,
-                    partialmethod(cls._get_FIELD_display, field=self))
+            if not hasattr(cls, 'get_%s_display' % self.name):
+                setattr(
+                    cls,
+                    'get_%s_display' % self.name,
+                    partialmethod(cls._get_FIELD_display, field=self),
+                )
 
     def get_filter_kwargs_for_object(self, obj):
         """


```

## Test Patch

```diff
diff --git a/tests/model_fields/tests.py b/tests/model_fields/tests.py
--- a/tests/model_fields/tests.py
+++ b/tests/model_fields/tests.py
@@ -168,6 +168,16 @@ def test_get_FIELD_display_translated(self):
         self.assertIsInstance(val, str)
         self.assertEqual(val, 'translated')
 
+    def test_overriding_FIELD_display(self):
+        class FooBar(models.Model):
+            foo_bar = models.IntegerField(choices=[(1, 'foo'), (2, 'bar')])
+
+            def get_foo_bar_display(self):
+                return 'something'
+
+        f = FooBar(foo_bar=1)
+        self.assertEqual(f.get_foo_bar_display(), 'something')
+
     def test_iterator_choices(self):
         """
         get_choices() works with Iterators.

```

## Test Information

**Tests that should FAIL→PASS**: ["test_overriding_FIELD_display (model_fields.tests.GetFieldDisplayTests)"]

**Tests that should PASS→PASS**: ["test_blank_in_choices (model_fields.tests.GetChoicesTests)", "test_blank_in_grouped_choices (model_fields.tests.GetChoicesTests)", "test_empty_choices (model_fields.tests.GetChoicesTests)", "test_lazy_strings_not_evaluated (model_fields.tests.GetChoicesTests)", "test_check (model_fields.tests.ChoicesTests)", "test_choices (model_fields.tests.ChoicesTests)", "test_flatchoices (model_fields.tests.ChoicesTests)", "test_formfield (model_fields.tests.ChoicesTests)", "test_invalid_choice (model_fields.tests.ChoicesTests)", "Can supply a custom choices form class to Field.formfield()", "deconstruct() uses __qualname__ for nested class support.", "Field instances can be pickled.", "test_field_name (model_fields.tests.BasicFieldTests)", "Fields are ordered based on their creation.", "test_field_repr (model_fields.tests.BasicFieldTests)", "__repr__() uses __qualname__ for nested class support.", "test_field_str (model_fields.tests.BasicFieldTests)", "test_field_verbose_name (model_fields.tests.BasicFieldTests)", "Field.formfield() sets disabled for fields with choices.", "test_show_hidden_initial (model_fields.tests.BasicFieldTests)", "test_choices_and_field_display (model_fields.tests.GetFieldDisplayTests)", "test_empty_iterator_choices (model_fields.tests.GetFieldDisplayTests)", "A translated display value is coerced to str.", "test_iterator_choices (model_fields.tests.GetFieldDisplayTests)", "test_get_choices (model_fields.tests.GetChoicesLimitChoicesToTests)", "test_get_choices_reverse_related_field (model_fields.tests.GetChoicesLimitChoicesToTests)", "test_get_choices (model_fields.tests.GetChoicesOrderingTests)", "test_get_choices_default_ordering (model_fields.tests.GetChoicesOrderingTests)", "test_get_choices_reverse_related_field (model_fields.tests.GetChoicesOrderingTests)", "test_get_choices_reverse_related_field_default_ordering (model_fields.tests.GetChoicesOrderingTests)"]

**Base Commit**: 84633905273fc916e3d17883810d9969c03f73c2
**Environment Setup Commit**: 0668164b4ac93a5be79f5b87fae83c657124d9ab
