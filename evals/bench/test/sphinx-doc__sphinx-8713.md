# sphinx-doc__sphinx-8713

**Repository**: sphinx-doc/sphinx
**Created**: 2021-01-20T14:24:12Z
**Version**: 4.0

## Problem Statement

napoleon_use_param should also affect "other parameters" section
Subject: napoleon_use_param should also affect "other parameters" section

### Problem
Currently, napoleon always renders the Other parameters section as if napoleon_use_param was False, see source
```
    def _parse_other_parameters_section(self, section):
        # type: (unicode) -> List[unicode]
        return self._format_fields(_('Other Parameters'), self._consume_fields())

    def _parse_parameters_section(self, section):
        # type: (unicode) -> List[unicode]
        fields = self._consume_fields()
        if self._config.napoleon_use_param:
            return self._format_docutils_params(fields)
        else:
            return self._format_fields(_('Parameters'), fields)
```
whereas it would make sense that this section should follow the same formatting rules as the Parameters section.

#### Procedure to reproduce the problem
```
In [5]: print(str(sphinx.ext.napoleon.NumpyDocstring("""\ 
   ...: Parameters 
   ...: ---------- 
   ...: x : int 
   ...:  
   ...: Other parameters 
   ...: ---------------- 
   ...: y: float 
   ...: """)))                                                                                                                                                                                      
:param x:
:type x: int

:Other Parameters: **y** (*float*)
```

Note the difference in rendering.

#### Error logs / results
See above.

#### Expected results
```
:param x:
:type x: int

:Other Parameters:  // Or some other kind of heading.
:param: y
:type y: float
```

Alternatively another separate config value could be introduced, but that seems a bit overkill.

### Reproducible project / your project
N/A

### Environment info
- OS: Linux
- Python version: 3.7
- Sphinx version: 1.8.1



## Patch

```diff

diff --git a/sphinx/ext/napoleon/docstring.py b/sphinx/ext/napoleon/docstring.py
--- a/sphinx/ext/napoleon/docstring.py
+++ b/sphinx/ext/napoleon/docstring.py
@@ -682,7 +682,13 @@ def _parse_notes_section(self, section: str) -> List[str]:
         return self._parse_generic_section(_('Notes'), use_admonition)
 
     def _parse_other_parameters_section(self, section: str) -> List[str]:
-        return self._format_fields(_('Other Parameters'), self._consume_fields())
+        if self._config.napoleon_use_param:
+            # Allow to declare multiple parameters at once (ex: x, y: int)
+            fields = self._consume_fields(multiple=True)
+            return self._format_docutils_params(fields)
+        else:
+            fields = self._consume_fields()
+            return self._format_fields(_('Other Parameters'), fields)
 
     def _parse_parameters_section(self, section: str) -> List[str]:
         if self._config.napoleon_use_param:


```

## Test Patch

```diff
diff --git a/tests/test_ext_napoleon_docstring.py b/tests/test_ext_napoleon_docstring.py
--- a/tests/test_ext_napoleon_docstring.py
+++ b/tests/test_ext_napoleon_docstring.py
@@ -1441,12 +1441,18 @@ def test_parameters_with_class_reference(self):
 ----------
 param1 : :class:`MyClass <name.space.MyClass>` instance
 
+Other Parameters
+----------------
+param2 : :class:`MyClass <name.space.MyClass>` instance
+
 """
 
         config = Config(napoleon_use_param=False)
         actual = str(NumpyDocstring(docstring, config))
         expected = """\
 :Parameters: **param1** (:class:`MyClass <name.space.MyClass>` instance)
+
+:Other Parameters: **param2** (:class:`MyClass <name.space.MyClass>` instance)
 """
         self.assertEqual(expected, actual)
 
@@ -1455,6 +1461,9 @@ def test_parameters_with_class_reference(self):
         expected = """\
 :param param1:
 :type param1: :class:`MyClass <name.space.MyClass>` instance
+
+:param param2:
+:type param2: :class:`MyClass <name.space.MyClass>` instance
 """
         self.assertEqual(expected, actual)
 

```

## Test Information

**Tests that should FAIL→PASS**: ["tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_parameters_with_class_reference"]

**Tests that should PASS→PASS**: ["tests/test_ext_napoleon_docstring.py::NamedtupleSubclassTest::test_attributes_docstring", "tests/test_ext_napoleon_docstring.py::InlineAttributeTest::test_class_data_member", "tests/test_ext_napoleon_docstring.py::InlineAttributeTest::test_class_data_member_inline", "tests/test_ext_napoleon_docstring.py::InlineAttributeTest::test_class_data_member_inline_no_type", "tests/test_ext_napoleon_docstring.py::InlineAttributeTest::test_class_data_member_inline_ref_in_type", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_attributes_with_class_reference", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_code_block_in_returns_section", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_colon_in_return_type", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_custom_generic_sections", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_docstrings", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_keywords_with_types", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_kwargs_in_arguments", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_list_in_parameter_description", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_noindex", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_parameters_with_class_reference", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_pep526_annotations", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_raises_types", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_section_header_formatting", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_sphinx_admonitions", "tests/test_ext_napoleon_docstring.py::GoogleDocstringTest::test_xrefs_in_return_type", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_colon_in_return_type", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_convert_numpy_type_spec", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_docstrings", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_list_in_parameter_description", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_multiple_parameters", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_parameter_types", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_parameters_without_class_reference", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_raises_types", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_recombine_set_tokens", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_recombine_set_tokens_invalid", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_return_types", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_section_header_underline_length", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_see_also_refs", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_sphinx_admonitions", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_token_type", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_tokenize_type_spec", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_type_preprocessor", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_underscore_in_attribute", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_underscore_in_attribute_strip_signature_backslash", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_xrefs_in_return_type", "tests/test_ext_napoleon_docstring.py::NumpyDocstringTest::test_yield_types", "tests/test_ext_napoleon_docstring.py::TestNumpyDocstring::test_escape_args_and_kwargs[x,", "tests/test_ext_napoleon_docstring.py::TestNumpyDocstring::test_escape_args_and_kwargs[*args,", "tests/test_ext_napoleon_docstring.py::TestNumpyDocstring::test_escape_args_and_kwargs[*x,", "tests/test_ext_napoleon_docstring.py::TestNumpyDocstring::test_pep526_annotations"]

**Base Commit**: 3ed7590ed411bd93b26098faab4f23619cdb2267
**Environment Setup Commit**: 8939a75efaa911a12dbe6edccedf261e88bf7eef
