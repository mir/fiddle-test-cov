# django__django-13220

**Repository**: django/django
**Created**: 2020-07-21T19:54:16Z
**Version**: 3.2

## Problem Statement

Allow ValidationErrors to equal each other when created identically
Description
	 
		(last modified by kamni)
	 
Currently ValidationErrors (django.core.exceptions.ValidationError) that have identical messages don't equal each other, which is counter-intuitive, and can make certain kinds of testing more complicated. Please add an __eq__ method that allows two ValidationErrors to be compared. 
Ideally, this would be more than just a simple self.messages == other.messages. It would be most helpful if the comparison were independent of the order in which errors were raised in a field or in non_field_errors.


## Hints

I probably wouldn't want to limit the comparison to an error's message but rather to its full set of attributes (message, code, params). While params is always pushed into message when iterating over the errors in an ValidationError, I believe it can be beneficial to know if the params that were put inside are the same.
​PR

## Patch

```diff

diff --git a/django/core/exceptions.py b/django/core/exceptions.py
--- a/django/core/exceptions.py
+++ b/django/core/exceptions.py
@@ -1,6 +1,9 @@
 """
 Global Django exception and warning classes.
 """
+import operator
+
+from django.utils.hashable import make_hashable
 
 
 class FieldDoesNotExist(Exception):
@@ -182,6 +185,23 @@ def __str__(self):
     def __repr__(self):
         return 'ValidationError(%s)' % self
 
+    def __eq__(self, other):
+        if not isinstance(other, ValidationError):
+            return NotImplemented
+        return hash(self) == hash(other)
+
+    def __hash__(self):
+        # Ignore params and messages ordering.
+        if hasattr(self, 'message'):
+            return hash((
+                self.message,
+                self.code,
+                tuple(sorted(make_hashable(self.params))) if self.params else None,
+            ))
+        if hasattr(self, 'error_dict'):
+            return hash(tuple(sorted(make_hashable(self.error_dict))))
+        return hash(tuple(sorted(self.error_list, key=operator.attrgetter('message'))))
+
 
 class EmptyResultSet(Exception):
     """A database query predicate is impossible."""


```

## Test Patch

```diff
diff --git a/tests/test_exceptions/test_validation_error.py b/tests/test_exceptions/test_validation_error.py
--- a/tests/test_exceptions/test_validation_error.py
+++ b/tests/test_exceptions/test_validation_error.py
@@ -1,4 +1,5 @@
 import unittest
+from unittest import mock
 
 from django.core.exceptions import ValidationError
 
@@ -14,3 +15,271 @@ def test_messages_concatenates_error_dict_values(self):
         message_dict['field2'] = ['E3', 'E4']
         exception = ValidationError(message_dict)
         self.assertEqual(sorted(exception.messages), ['E1', 'E2', 'E3', 'E4'])
+
+    def test_eq(self):
+        error1 = ValidationError('message')
+        error2 = ValidationError('message', code='my_code1')
+        error3 = ValidationError('message', code='my_code2')
+        error4 = ValidationError(
+            'error %(parm1)s %(parm2)s',
+            code='my_code1',
+            params={'parm1': 'val1', 'parm2': 'val2'},
+        )
+        error5 = ValidationError({'field1': 'message', 'field2': 'other'})
+        error6 = ValidationError({'field1': 'message'})
+        error7 = ValidationError([
+            ValidationError({'field1': 'field error', 'field2': 'other'}),
+            'message',
+        ])
+
+        self.assertEqual(error1, ValidationError('message'))
+        self.assertNotEqual(error1, ValidationError('message2'))
+        self.assertNotEqual(error1, error2)
+        self.assertNotEqual(error1, error4)
+        self.assertNotEqual(error1, error5)
+        self.assertNotEqual(error1, error6)
+        self.assertNotEqual(error1, error7)
+        self.assertEqual(error1, mock.ANY)
+        self.assertEqual(error2, ValidationError('message', code='my_code1'))
+        self.assertNotEqual(error2, ValidationError('other', code='my_code1'))
+        self.assertNotEqual(error2, error3)
+        self.assertNotEqual(error2, error4)
+        self.assertNotEqual(error2, error5)
+        self.assertNotEqual(error2, error6)
+        self.assertNotEqual(error2, error7)
+
+        self.assertEqual(error4, ValidationError(
+            'error %(parm1)s %(parm2)s',
+            code='my_code1',
+            params={'parm1': 'val1', 'parm2': 'val2'},
+        ))
+        self.assertNotEqual(error4, ValidationError(
+            'error %(parm1)s %(parm2)s',
+            code='my_code2',
+            params={'parm1': 'val1', 'parm2': 'val2'},
+        ))
+        self.assertNotEqual(error4, ValidationError(
+            'error %(parm1)s %(parm2)s',
+            code='my_code1',
+            params={'parm2': 'val2'},
+        ))
+        self.assertNotEqual(error4, ValidationError(
+            'error %(parm1)s %(parm2)s',
+            code='my_code1',
+            params={'parm2': 'val1', 'parm1': 'val2'},
+        ))
+        self.assertNotEqual(error4, ValidationError(
+            'error val1 val2',
+            code='my_code1',
+        ))
+        # params ordering is ignored.
+        self.assertEqual(error4, ValidationError(
+            'error %(parm1)s %(parm2)s',
+            code='my_code1',
+            params={'parm2': 'val2', 'parm1': 'val1'},
+        ))
+
+        self.assertEqual(
+            error5,
+            ValidationError({'field1': 'message', 'field2': 'other'}),
+        )
+        self.assertNotEqual(
+            error5,
+            ValidationError({'field1': 'message', 'field2': 'other2'}),
+        )
+        self.assertNotEqual(
+            error5,
+            ValidationError({'field1': 'message', 'field3': 'other'}),
+        )
+        self.assertNotEqual(error5, error6)
+        # fields ordering is ignored.
+        self.assertEqual(
+            error5,
+            ValidationError({'field2': 'other', 'field1': 'message'}),
+        )
+
+        self.assertNotEqual(error7, ValidationError(error7.error_list[1:]))
+        self.assertNotEqual(
+            ValidationError(['message']),
+            ValidationError([ValidationError('message', code='my_code')]),
+        )
+        # messages ordering is ignored.
+        self.assertEqual(
+            error7,
+            ValidationError(list(reversed(error7.error_list))),
+        )
+
+        self.assertNotEqual(error4, ValidationError([error4]))
+        self.assertNotEqual(ValidationError([error4]), error4)
+        self.assertNotEqual(error4, ValidationError({'field1': error4}))
+        self.assertNotEqual(ValidationError({'field1': error4}), error4)
+
+    def test_eq_nested(self):
+        error_dict = {
+            'field1': ValidationError(
+                'error %(parm1)s %(parm2)s',
+                code='my_code',
+                params={'parm1': 'val1', 'parm2': 'val2'},
+            ),
+            'field2': 'other',
+        }
+        error = ValidationError(error_dict)
+        self.assertEqual(error, ValidationError(dict(error_dict)))
+        self.assertEqual(error, ValidationError({
+            'field1': ValidationError(
+                'error %(parm1)s %(parm2)s',
+                code='my_code',
+                params={'parm2': 'val2', 'parm1': 'val1'},
+            ),
+            'field2': 'other',
+        }))
+        self.assertNotEqual(error, ValidationError(
+            {**error_dict, 'field2': 'message'},
+        ))
+        self.assertNotEqual(error, ValidationError({
+            'field1': ValidationError(
+                'error %(parm1)s val2',
+                code='my_code',
+                params={'parm1': 'val1'},
+            ),
+            'field2': 'other',
+        }))
+
+    def test_hash(self):
+        error1 = ValidationError('message')
+        error2 = ValidationError('message', code='my_code1')
+        error3 = ValidationError('message', code='my_code2')
+        error4 = ValidationError(
+            'error %(parm1)s %(parm2)s',
+            code='my_code1',
+            params={'parm1': 'val1', 'parm2': 'val2'},
+        )
+        error5 = ValidationError({'field1': 'message', 'field2': 'other'})
+        error6 = ValidationError({'field1': 'message'})
+        error7 = ValidationError([
+            ValidationError({'field1': 'field error', 'field2': 'other'}),
+            'message',
+        ])
+
+        self.assertEqual(hash(error1), hash(ValidationError('message')))
+        self.assertNotEqual(hash(error1), hash(ValidationError('message2')))
+        self.assertNotEqual(hash(error1), hash(error2))
+        self.assertNotEqual(hash(error1), hash(error4))
+        self.assertNotEqual(hash(error1), hash(error5))
+        self.assertNotEqual(hash(error1), hash(error6))
+        self.assertNotEqual(hash(error1), hash(error7))
+        self.assertEqual(
+            hash(error2),
+            hash(ValidationError('message', code='my_code1')),
+        )
+        self.assertNotEqual(
+            hash(error2),
+            hash(ValidationError('other', code='my_code1')),
+        )
+        self.assertNotEqual(hash(error2), hash(error3))
+        self.assertNotEqual(hash(error2), hash(error4))
+        self.assertNotEqual(hash(error2), hash(error5))
+        self.assertNotEqual(hash(error2), hash(error6))
+        self.assertNotEqual(hash(error2), hash(error7))
+
+        self.assertEqual(hash(error4), hash(ValidationError(
+            'error %(parm1)s %(parm2)s',
+            code='my_code1',
+            params={'parm1': 'val1', 'parm2': 'val2'},
+        )))
+        self.assertNotEqual(hash(error4), hash(ValidationError(
+            'error %(parm1)s %(parm2)s',
+            code='my_code2',
+            params={'parm1': 'val1', 'parm2': 'val2'},
+        )))
+        self.assertNotEqual(hash(error4), hash(ValidationError(
+            'error %(parm1)s %(parm2)s',
+            code='my_code1',
+            params={'parm2': 'val2'},
+        )))
+        self.assertNotEqual(hash(error4), hash(ValidationError(
+            'error %(parm1)s %(parm2)s',
+            code='my_code1',
+            params={'parm2': 'val1', 'parm1': 'val2'},
+        )))
+        self.assertNotEqual(hash(error4), hash(ValidationError(
+            'error val1 val2',
+            code='my_code1',
+        )))
+        # params ordering is ignored.
+        self.assertEqual(hash(error4), hash(ValidationError(
+            'error %(parm1)s %(parm2)s',
+            code='my_code1',
+            params={'parm2': 'val2', 'parm1': 'val1'},
+        )))
+
+        self.assertEqual(
+            hash(error5),
+            hash(ValidationError({'field1': 'message', 'field2': 'other'})),
+        )
+        self.assertNotEqual(
+            hash(error5),
+            hash(ValidationError({'field1': 'message', 'field2': 'other2'})),
+        )
+        self.assertNotEqual(
+            hash(error5),
+            hash(ValidationError({'field1': 'message', 'field3': 'other'})),
+        )
+        self.assertNotEqual(error5, error6)
+        # fields ordering is ignored.
+        self.assertEqual(
+            hash(error5),
+            hash(ValidationError({'field2': 'other', 'field1': 'message'})),
+        )
+
+        self.assertNotEqual(
+            hash(error7),
+            hash(ValidationError(error7.error_list[1:])),
+        )
+        self.assertNotEqual(
+            hash(ValidationError(['message'])),
+            hash(ValidationError([ValidationError('message', code='my_code')])),
+        )
+        # messages ordering is ignored.
+        self.assertEqual(
+            hash(error7),
+            hash(ValidationError(list(reversed(error7.error_list)))),
+        )
+
+        self.assertNotEqual(hash(error4), hash(ValidationError([error4])))
+        self.assertNotEqual(hash(ValidationError([error4])), hash(error4))
+        self.assertNotEqual(
+            hash(error4),
+            hash(ValidationError({'field1': error4})),
+        )
+
+    def test_hash_nested(self):
+        error_dict = {
+            'field1': ValidationError(
+                'error %(parm1)s %(parm2)s',
+                code='my_code',
+                params={'parm2': 'val2', 'parm1': 'val1'},
+            ),
+            'field2': 'other',
+        }
+        error = ValidationError(error_dict)
+        self.assertEqual(hash(error), hash(ValidationError(dict(error_dict))))
+        self.assertEqual(hash(error), hash(ValidationError({
+            'field1': ValidationError(
+                'error %(parm1)s %(parm2)s',
+                code='my_code',
+                params={'parm1': 'val1', 'parm2': 'val2'},
+            ),
+            'field2': 'other',
+        })))
+        self.assertNotEqual(hash(error), hash(ValidationError(
+            {**error_dict, 'field2': 'message'},
+        )))
+        self.assertNotEqual(hash(error), hash(ValidationError({
+            'field1': ValidationError(
+                'error %(parm1)s val2',
+                code='my_code',
+                params={'parm1': 'val1'},
+            ),
+            'field2': 'other',
+        })))

```

## Test Information

**Tests that should FAIL→PASS**: ["test_eq (test_exceptions.test_validation_error.TestValidationError)", "test_eq_nested (test_exceptions.test_validation_error.TestValidationError)", "test_hash (test_exceptions.test_validation_error.TestValidationError)", "test_hash_nested (test_exceptions.test_validation_error.TestValidationError)"]

**Tests that should PASS→PASS**: ["test_messages_concatenates_error_dict_values (test_exceptions.test_validation_error.TestValidationError)"]

**Base Commit**: 16218c20606d8cd89c5393970c83da04598a3e04
**Environment Setup Commit**: 65dfb06a1ab56c238cc80f5e1c31f61210c4577d
