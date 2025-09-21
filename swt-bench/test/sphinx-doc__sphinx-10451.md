# sphinx-doc__sphinx-10451

**Repository**: sphinx-doc/sphinx
**Created**: 2022-05-15T11:49:39Z
**Version**: 5.1

## Problem Statement

Fix duplicated *args and **kwargs with autodoc_typehints
Fix duplicated *args and **kwargs with autodoc_typehints

### Bugfix
- Bugfix

### Detail
Consider this
```python
class _ClassWithDocumentedInitAndStarArgs:
    """Class docstring."""

    def __init__(self, x: int, *args: int, **kwargs: int) -> None:
        """Init docstring.

        :param x: Some integer
        :param *args: Some integer
        :param **kwargs: Some integer
        """
```
when using the autodoc extension and the setting `autodoc_typehints = "description"`.

WIth sphinx 4.2.0, the current output is
```
Class docstring.

   Parameters:
      * **x** (*int*) --

      * **args** (*int*) --

      * **kwargs** (*int*) --

   Return type:
      None

   __init__(x, *args, **kwargs)

      Init docstring.

      Parameters:
         * **x** (*int*) -- Some integer

         * ***args** --

           Some integer

         * ****kwargs** --

           Some integer

         * **args** (*int*) --

         * **kwargs** (*int*) --

      Return type:
         None
```
where the *args and **kwargs are duplicated and incomplete.

The expected output is
```
  Class docstring.

   Parameters:
      * **x** (*int*) --

      * ***args** (*int*) --

      * ****kwargs** (*int*) --

   Return type:
      None

   __init__(x, *args, **kwargs)

      Init docstring.

      Parameters:
         * **x** (*int*) -- Some integer

         * ***args** (*int*) --

           Some integer

         * ****kwargs** (*int*) --

           Some integer

      Return type:
         None

```


## Hints

I noticed this docstring causes warnings because `*` and `**` are considered as mark-up symbols:

```
    def __init__(self, x: int, *args: int, **kwargs: int) -> None:
        """Init docstring.

        :param x: Some integer
        :param *args: Some integer
        :param **kwargs: Some integer
        """
```

Here are warnings:
```
/Users/tkomiya/work/tmp/doc/example.py:docstring of example.ClassWithDocumentedInitAndStarArgs:6: WARNING: Inline emphasis start-string without end-string.
/Users/tkomiya/work/tmp/doc/example.py:docstring of example.ClassWithDocumentedInitAndStarArgs:7: WARNING: Inline strong start-string without end-string.
```

It will work fine if we escape `*` character like the following. But it's not officially recommended way, I believe.

```
    def __init__(self, x: int, *args: int, **kwargs: int) -> None:
        """Init docstring.

        :param x: Some integer
        :param \*args: Some integer
        :param \*\*kwargs: Some integer
        """
```

I'm not sure this feature is really needed?
> I noticed this docstring causes warnings because `*` and `**` are considered as mark-up symbols:
> 
> ```
>     def __init__(self, x: int, *args: int, **kwargs: int) -> None:
>         """Init docstring.
> 
>         :param x: Some integer
>         :param *args: Some integer
>         :param **kwargs: Some integer
>         """
> ```
> 
> Here are warnings:
> 
> ```
> /Users/tkomiya/work/tmp/doc/example.py:docstring of example.ClassWithDocumentedInitAndStarArgs:6: WARNING: Inline emphasis start-string without end-string.
> /Users/tkomiya/work/tmp/doc/example.py:docstring of example.ClassWithDocumentedInitAndStarArgs:7: WARNING: Inline strong start-string without end-string.
> ```
> 
> It will work fine if we escape `*` character like the following. But it's not officially recommended way, I believe.
> 
> ```
>     def __init__(self, x: int, *args: int, **kwargs: int) -> None:
>         """Init docstring.
> 
>         :param x: Some integer
>         :param \*args: Some integer
>         :param \*\*kwargs: Some integer
>         """
> ```
> 
> I'm not sure this feature is really needed?

This is needed for the Numpy and Google docstring formats, which napoleon converts to `:param:`s.

Oh, I missed numpydoc format. Indeed, it recommends prepending stars.
https://numpydoc.readthedocs.io/en/latest/format.html#parameters

## Patch

```diff

diff --git a/sphinx/ext/autodoc/typehints.py b/sphinx/ext/autodoc/typehints.py
--- a/sphinx/ext/autodoc/typehints.py
+++ b/sphinx/ext/autodoc/typehints.py
@@ -115,7 +115,15 @@ def modify_field_list(node: nodes.field_list, annotations: Dict[str, str],
         if name == 'return':
             continue
 
-        arg = arguments.get(name, {})
+        if '*' + name in arguments:
+            name = '*' + name
+            arguments.get(name)
+        elif '**' + name in arguments:
+            name = '**' + name
+            arguments.get(name)
+        else:
+            arg = arguments.get(name, {})
+
         if not arg.get('type'):
             field = nodes.field()
             field += nodes.field_name('', 'type ' + name)
@@ -167,13 +175,19 @@ def augment_descriptions_with_types(
             has_type.add('return')
 
     # Add 'type' for parameters with a description but no declared type.
-    for name in annotations:
+    for name, annotation in annotations.items():
         if name in ('return', 'returns'):
             continue
+
+        if '*' + name in has_description:
+            name = '*' + name
+        elif '**' + name in has_description:
+            name = '**' + name
+
         if name in has_description and name not in has_type:
             field = nodes.field()
             field += nodes.field_name('', 'type ' + name)
-            field += nodes.field_body('', nodes.paragraph('', annotations[name]))
+            field += nodes.field_body('', nodes.paragraph('', annotation))
             node += field
 
     # Add 'rtype' if 'return' is present and 'rtype' isn't.


```

## Test Patch

```diff
diff --git a/tests/roots/test-ext-autodoc/target/typehints.py b/tests/roots/test-ext-autodoc/target/typehints.py
--- a/tests/roots/test-ext-autodoc/target/typehints.py
+++ b/tests/roots/test-ext-autodoc/target/typehints.py
@@ -94,8 +94,10 @@ def missing_attr(c,
 class _ClassWithDocumentedInit:
     """Class docstring."""
 
-    def __init__(self, x: int) -> None:
+    def __init__(self, x: int, *args: int, **kwargs: int) -> None:
         """Init docstring.
 
         :param x: Some integer
+        :param args: Some integer
+        :param kwargs: Some integer
         """
diff --git a/tests/roots/test-ext-napoleon/conf.py b/tests/roots/test-ext-napoleon/conf.py
new file mode 100644
--- /dev/null
+++ b/tests/roots/test-ext-napoleon/conf.py
@@ -0,0 +1,5 @@
+import os
+import sys
+
+sys.path.insert(0, os.path.abspath('.'))
+extensions = ['sphinx.ext.napoleon']
diff --git a/tests/roots/test-ext-napoleon/index.rst b/tests/roots/test-ext-napoleon/index.rst
new file mode 100644
--- /dev/null
+++ b/tests/roots/test-ext-napoleon/index.rst
@@ -0,0 +1,6 @@
+test-ext-napoleon
+=================
+
+.. toctree::
+
+   typehints
diff --git a/tests/roots/test-ext-napoleon/mypackage/__init__.py b/tests/roots/test-ext-napoleon/mypackage/__init__.py
new file mode 100644
diff --git a/tests/roots/test-ext-napoleon/mypackage/typehints.py b/tests/roots/test-ext-napoleon/mypackage/typehints.py
new file mode 100644
--- /dev/null
+++ b/tests/roots/test-ext-napoleon/mypackage/typehints.py
@@ -0,0 +1,11 @@
+def hello(x: int, *args: int, **kwargs: int) -> None:
+    """
+    Parameters
+    ----------
+    x
+        X
+    *args
+        Additional arguments.
+    **kwargs
+        Extra arguments.
+    """
diff --git a/tests/roots/test-ext-napoleon/typehints.rst b/tests/roots/test-ext-napoleon/typehints.rst
new file mode 100644
--- /dev/null
+++ b/tests/roots/test-ext-napoleon/typehints.rst
@@ -0,0 +1,5 @@
+typehints
+=========
+
+.. automodule:: mypackage.typehints
+   :members:
diff --git a/tests/test_ext_autodoc_configs.py b/tests/test_ext_autodoc_configs.py
--- a/tests/test_ext_autodoc_configs.py
+++ b/tests/test_ext_autodoc_configs.py
@@ -1034,19 +1034,27 @@ def test_autodoc_typehints_description_with_documented_init(app):
     )
     app.build()
     context = (app.outdir / 'index.txt').read_text(encoding='utf8')
-    assert ('class target.typehints._ClassWithDocumentedInit(x)\n'
+    assert ('class target.typehints._ClassWithDocumentedInit(x, *args, **kwargs)\n'
             '\n'
             '   Class docstring.\n'
             '\n'
             '   Parameters:\n'
-            '      **x** (*int*) --\n'
+            '      * **x** (*int*) --\n'
             '\n'
-            '   __init__(x)\n'
+            '      * **args** (*int*) --\n'
+            '\n'
+            '      * **kwargs** (*int*) --\n'
+            '\n'
+            '   __init__(x, *args, **kwargs)\n'
             '\n'
             '      Init docstring.\n'
             '\n'
             '      Parameters:\n'
-            '         **x** (*int*) -- Some integer\n'
+            '         * **x** (*int*) -- Some integer\n'
+            '\n'
+            '         * **args** (*int*) -- Some integer\n'
+            '\n'
+            '         * **kwargs** (*int*) -- Some integer\n'
             '\n'
             '      Return type:\n'
             '         None\n' == context)
@@ -1063,16 +1071,20 @@ def test_autodoc_typehints_description_with_documented_init_no_undoc(app):
     )
     app.build()
     context = (app.outdir / 'index.txt').read_text(encoding='utf8')
-    assert ('class target.typehints._ClassWithDocumentedInit(x)\n'
+    assert ('class target.typehints._ClassWithDocumentedInit(x, *args, **kwargs)\n'
             '\n'
             '   Class docstring.\n'
             '\n'
-            '   __init__(x)\n'
+            '   __init__(x, *args, **kwargs)\n'
             '\n'
             '      Init docstring.\n'
             '\n'
             '      Parameters:\n'
-            '         **x** (*int*) -- Some integer\n' == context)
+            '         * **x** (*int*) -- Some integer\n'
+            '\n'
+            '         * **args** (*int*) -- Some integer\n'
+            '\n'
+            '         * **kwargs** (*int*) -- Some integer\n' == context)
 
 
 @pytest.mark.sphinx('text', testroot='ext-autodoc',
@@ -1089,16 +1101,20 @@ def test_autodoc_typehints_description_with_documented_init_no_undoc_doc_rtype(a
     )
     app.build()
     context = (app.outdir / 'index.txt').read_text(encoding='utf8')
-    assert ('class target.typehints._ClassWithDocumentedInit(x)\n'
+    assert ('class target.typehints._ClassWithDocumentedInit(x, *args, **kwargs)\n'
             '\n'
             '   Class docstring.\n'
             '\n'
-            '   __init__(x)\n'
+            '   __init__(x, *args, **kwargs)\n'
             '\n'
             '      Init docstring.\n'
             '\n'
             '      Parameters:\n'
-            '         **x** (*int*) -- Some integer\n' == context)
+            '         * **x** (*int*) -- Some integer\n'
+            '\n'
+            '         * **args** (*int*) -- Some integer\n'
+            '\n'
+            '         * **kwargs** (*int*) -- Some integer\n' == context)
 
 
 @pytest.mark.sphinx('text', testroot='ext-autodoc',
diff --git a/tests/test_ext_napoleon_docstring.py b/tests/test_ext_napoleon_docstring.py
--- a/tests/test_ext_napoleon_docstring.py
+++ b/tests/test_ext_napoleon_docstring.py
@@ -2593,3 +2593,48 @@ def test_pep526_annotations(self):
 """
         print(actual)
         assert expected == actual
+
+
+@pytest.mark.sphinx('text', testroot='ext-napoleon',
+                    confoverrides={'autodoc_typehints': 'description',
+                                   'autodoc_typehints_description_target': 'all'})
+def test_napoleon_and_autodoc_typehints_description_all(app, status, warning):
+    app.build()
+    content = (app.outdir / 'typehints.txt').read_text(encoding='utf-8')
+    assert content == (
+        'typehints\n'
+        '*********\n'
+        '\n'
+        'mypackage.typehints.hello(x, *args, **kwargs)\n'
+        '\n'
+        '   Parameters:\n'
+        '      * **x** (*int*) -- X\n'
+        '\n'
+        '      * ***args** (*int*) -- Additional arguments.\n'
+        '\n'
+        '      * ****kwargs** (*int*) -- Extra arguments.\n'
+        '\n'
+        '   Return type:\n'
+        '      None\n'
+    )
+
+
+@pytest.mark.sphinx('text', testroot='ext-napoleon',
+                    confoverrides={'autodoc_typehints': 'description',
+                                   'autodoc_typehints_description_target': 'documented_params'})
+def test_napoleon_and_autodoc_typehints_description_documented_params(app, status, warning):
+    app.build()
+    content = (app.outdir / 'typehints.txt').read_text(encoding='utf-8')
+    assert content == (
+        'typehints\n'
+        '*********\n'
+        '\n'
+        'mypackage.typehints.hello(x, *args, **kwargs)\n'
+        '\n'
+        '   Parameters:\n'
+        '      * **x** (*int*) -- X\n'
+        '\n'
+        '      * ***args** (*int*) -- Additional arguments.\n'
+        '\n'
+        '      * ****kwargs** (*int*) -- Extra arguments.\n'
+    )

```

## Test Information

**Tests that should FAIL→PASS**: ["tests/test_ext_napoleon_docstring.py::test_napoleon_and_autodoc_typehints_description_all", "tests/test_ext_napoleon_docstring.py::test_napoleon_and_autodoc_typehints_description_documented_params"]

**Tests that should PASS→PASS**: ["tests/test_ext_autodoc_configs.py::test_autoclass_content_class", "tests/test_ext_autodoc_configs.py::test_autoclass_content_init", "tests/test_ext_autodoc_configs.py::test_autodoc_class_signature_mixed", "tests/test_ext_autodoc_configs.py::test_autodoc_class_signature_separated_init", "tests/test_ext_autodoc_configs.py::test_autodoc_class_signature_separated_new", "tests/test_ext_autodoc_configs.py::test_autoclass_content_both", "tests/test_ext_autodoc_configs.py::test_autodoc_inherit_docstrings", "tests/test_ext_autodoc_configs.py::test_autodoc_docstring_signature", "tests/test_ext_autodoc_configs.py::test_autoclass_content_and_docstring_signature_class", "tests/test_ext_autodoc_configs.py::test_autoclass_content_and_docstring_signature_init", "tests/test_ext_autodoc_configs.py::test_autoclass_content_and_docstring_signature_both", "tests/test_ext_autodoc_configs.py::test_mocked_module_imports", "tests/test_ext_autodoc_configs.py::test_autodoc_typehints_signature", "tests/test_ext_autodoc_configs.py::test_autodoc_typehints_none", "tests/test_ext_autodoc_configs.py::test_autodoc_typehints_none_for_overload", "tests/test_ext_autodoc_configs.py::test_autodoc_typehints_description", "tests/test_ext_autodoc_configs.py::test_autodoc_typehints_description_no_undoc", "tests/test_ext_autodoc_configs.py::test_autodoc_typehints_description_no_undoc_doc_rtype", "tests/test_ext_autodoc_configs.py::test_autodoc_typehints_description_with_documented_init", "tests/test_ext_autodoc_configs.py::test_autodoc_typehints_description_with_documented_init_no_undoc", "tests/test_ext_autodoc_configs.py::test_autodoc_typehints_description_with_documented_init_no_undoc_doc_rtype", "tests/test_ext_autodoc_configs.py::test_autodoc_typehints_description_for_invalid_node", "tests/test_ext_autodoc_configs.py::test_autodoc_typehints_both", "tests/test_ext_autodoc_configs.py::test_autodoc_type_aliases", "tests/test_ext_autodoc_configs.py::test_autodoc_typehints_description_and_type_aliases", "tests/test_ext_autodoc_configs.py::test_autodoc_typehints_format_fully_qualified", "tests/test_ext_autodoc_configs.py::test_autodoc_typehints_format_fully_qualified_for_class_alias", "tests/test_ext_autodoc_configs.py::test_autodoc_typehints_format_fully_qualified_for_generic_alias", "tests/test_ext_autodoc_configs.py::test_autodoc_typehints_format_fully_qualified_for_newtype_alias", "tests/test_ext_autodoc_configs.py::test_autodoc_default_options", "tests/test_ext_autodoc_configs.py::test_autodoc_default_options_with_values", "tests/test_ext_napoleon_docstring.py::NamedtupleSubclassTest::test_attributes_docstring", "tests/test_ext_napoleon_docstring.py::InlineAttributeTest::test_class_data_member", "tests/test_ext_napoleon_docstring.py::InlineAttributeTest::test_class_data_member_inline", "tests/test_ext_napoleon_docstring.py::InlineAttributeTest::test_class_data_member_inline_no_type", "tests/test_ext_napoleon_docstring.py::InlineAttributeTest::test_class_data_member_inline_ref_in_type", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_attributes_with_class_reference", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_attributes_with_use_ivar", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_code_block_in_returns_section", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_colon_in_return_type", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_custom_generic_sections", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_docstrings", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_keywords_with_types", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_kwargs_in_arguments", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_list_in_parameter_description", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_noindex", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_parameters_with_class_reference", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_pep526_annotations", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_preprocess_types", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_raises_types", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_section_header_formatting", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_sphinx_admonitions", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_xrefs_in_return_type", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_colon_in_return_type", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_convert_numpy_type_spec", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_docstrings", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_list_in_parameter_description", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_multiple_parameters", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_parameter_types", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_parameters_with_class_reference", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_parameters_without_class_reference", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_raises_types", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_recombine_set_tokens", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_recombine_set_tokens_invalid", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_return_types", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_section_header_underline_length", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_see_also_refs", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_sphinx_admonitions", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_token_type", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_tokenize_type_spec", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_type_preprocessor", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_underscore_in_attribute", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_underscore_in_attribute_strip_signature_backslash", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_xrefs_in_return_type", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_yield_types", "tests/test_ext_napoleon_docstring.py::TestNumpyDocstring::test_token_type_invalid", "tests/test_ext_napoleon_docstring.py::TestNumpyDocstring::test_escape_args_and_kwargs[x,", "tests/test_ext_napoleon_docstring.py::TestNumpyDocstring::test_escape_args_and_kwargs[*args,", "tests/test_ext_napoleon_docstring.py::TestNumpyDocstring::test_escape_args_and_kwargs[*x,", "tests/test_ext_napoleon_docstring.py::TestNumpyDocstring::test_pep526_annotations"]

**Base Commit**: 195e911f1dab04b8ddeacbe04b7d214aaf81bb0b
**Environment Setup Commit**: 571b55328d401a6e1d50e37407df56586065a7be
