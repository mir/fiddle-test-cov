# django__django-13933

**Repository**: django/django
**Created**: 2021-01-26T03:58:23Z
**Version**: 4.0

## Problem Statement

ModelChoiceField does not provide value of invalid choice when raising ValidationError
Description
	 
		(last modified by Aaron Wiegel)
	 
Compared with ChoiceField and others, ModelChoiceField does not show the value of the invalid choice when raising a validation error. Passing in parameters with the invalid value and modifying the default error message for the code invalid_choice should fix this.
From source code:
class ModelMultipleChoiceField(ModelChoiceField):
	"""A MultipleChoiceField whose choices are a model QuerySet."""
	widget = SelectMultiple
	hidden_widget = MultipleHiddenInput
	default_error_messages = {
		'invalid_list': _('Enter a list of values.'),
		'invalid_choice': _('Select a valid choice. %(value)s is not one of the'
							' available choices.'),
		'invalid_pk_value': _('“%(pk)s” is not a valid value.')
	}
	...
class ModelChoiceField(ChoiceField):
	"""A ChoiceField whose choices are a model QuerySet."""
	# This class is a subclass of ChoiceField for purity, but it doesn't
	# actually use any of ChoiceField's implementation.
	default_error_messages = {
		'invalid_choice': _('Select a valid choice. That choice is not one of'
							' the available choices.'),
	}
	...


## Hints

This message has been the same literally forever b2b6fc8e3c78671c8b6af2709358c3213c84d119. ​Given that ChoiceField passes the value when raising the error, if you set ​error_messages you should be able to get the result you want.
Replying to Carlton Gibson: This message has been the same literally forever b2b6fc8e3c78671c8b6af2709358c3213c84d119. ​Given that ChoiceField passes the value when raising the error, if you set ​error_messages you should be able to get the result you want. That is ChoiceField. ModelChoiceField ​does not pass the value to the validation error. So, when the invalid value error is raised, you can't display the offending value even if you override the defaults.
OK, if you want to look at submitting a PR we can see if any objections come up in review. Thanks.
PR: ​https://github.com/django/django/pull/13933

## Patch

```diff

diff --git a/django/forms/models.py b/django/forms/models.py
--- a/django/forms/models.py
+++ b/django/forms/models.py
@@ -1284,7 +1284,11 @@ def to_python(self, value):
                 value = getattr(value, key)
             value = self.queryset.get(**{key: value})
         except (ValueError, TypeError, self.queryset.model.DoesNotExist):
-            raise ValidationError(self.error_messages['invalid_choice'], code='invalid_choice')
+            raise ValidationError(
+                self.error_messages['invalid_choice'],
+                code='invalid_choice',
+                params={'value': value},
+            )
         return value
 
     def validate(self, value):


```

## Test Patch

```diff
diff --git a/tests/forms_tests/tests/test_error_messages.py b/tests/forms_tests/tests/test_error_messages.py
--- a/tests/forms_tests/tests/test_error_messages.py
+++ b/tests/forms_tests/tests/test_error_messages.py
@@ -308,3 +308,16 @@ def test_modelchoicefield(self):
         self.assertFormErrors(['REQUIRED'], f.clean, '')
         self.assertFormErrors(['NOT A LIST OF VALUES'], f.clean, '3')
         self.assertFormErrors(['4 IS INVALID CHOICE'], f.clean, ['4'])
+
+    def test_modelchoicefield_value_placeholder(self):
+        f = ModelChoiceField(
+            queryset=ChoiceModel.objects.all(),
+            error_messages={
+                'invalid_choice': '"%(value)s" is not one of the available choices.',
+            },
+        )
+        self.assertFormErrors(
+            ['"invalid" is not one of the available choices.'],
+            f.clean,
+            'invalid',
+        )

```

## Test Information

**Tests that should FAIL→PASS**: ["test_modelchoicefield_value_placeholder (forms_tests.tests.test_error_messages.ModelChoiceFieldErrorMessagesTestCase)"]

**Tests that should PASS→PASS**: ["test_modelchoicefield (forms_tests.tests.test_error_messages.ModelChoiceFieldErrorMessagesTestCase)", "test_booleanfield (forms_tests.tests.test_error_messages.FormsErrorMessagesTestCase)", "test_charfield (forms_tests.tests.test_error_messages.FormsErrorMessagesTestCase)", "test_choicefield (forms_tests.tests.test_error_messages.FormsErrorMessagesTestCase)", "test_datefield (forms_tests.tests.test_error_messages.FormsErrorMessagesTestCase)", "test_datetimefield (forms_tests.tests.test_error_messages.FormsErrorMessagesTestCase)", "test_decimalfield (forms_tests.tests.test_error_messages.FormsErrorMessagesTestCase)", "test_emailfield (forms_tests.tests.test_error_messages.FormsErrorMessagesTestCase)", "test_error_messages_escaping (forms_tests.tests.test_error_messages.FormsErrorMessagesTestCase)", "test_filefield (forms_tests.tests.test_error_messages.FormsErrorMessagesTestCase)", "test_floatfield (forms_tests.tests.test_error_messages.FormsErrorMessagesTestCase)", "test_generic_ipaddressfield (forms_tests.tests.test_error_messages.FormsErrorMessagesTestCase)", "test_integerfield (forms_tests.tests.test_error_messages.FormsErrorMessagesTestCase)", "test_multiplechoicefield (forms_tests.tests.test_error_messages.FormsErrorMessagesTestCase)", "test_regexfield (forms_tests.tests.test_error_messages.FormsErrorMessagesTestCase)", "test_splitdatetimefield (forms_tests.tests.test_error_messages.FormsErrorMessagesTestCase)", "test_subclassing_errorlist (forms_tests.tests.test_error_messages.FormsErrorMessagesTestCase)", "test_timefield (forms_tests.tests.test_error_messages.FormsErrorMessagesTestCase)", "test_urlfield (forms_tests.tests.test_error_messages.FormsErrorMessagesTestCase)"]

**Base Commit**: 42e8cf47c7ee2db238bf91197ea398126c546741
**Environment Setup Commit**: 475cffd1d64c690cdad16ede4d5e81985738ceb4
