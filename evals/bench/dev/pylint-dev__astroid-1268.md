# pylint-dev__astroid-1268

**Repository**: pylint-dev/astroid
**Created**: 2021-11-21T16:15:23Z
**Version**: 2.9

## Problem Statement

'AsStringVisitor' object has no attribute 'visit_unknown'
```python
>>> import astroid
>>> astroid.nodes.Unknown().as_string()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/Users/tusharsadhwani/code/marvin-python/venv/lib/python3.9/site-packages/astroid/nodes/node_ng.py", line 609, in as_string
    return AsStringVisitor()(self)
  File "/Users/tusharsadhwani/code/marvin-python/venv/lib/python3.9/site-packages/astroid/nodes/as_string.py", line 56, in __call__
    return node.accept(self).replace(DOC_NEWLINE, "\n")
  File "/Users/tusharsadhwani/code/marvin-python/venv/lib/python3.9/site-packages/astroid/nodes/node_ng.py", line 220, in accept
    func = getattr(visitor, "visit_" + self.__class__.__name__.lower())
AttributeError: 'AsStringVisitor' object has no attribute 'visit_unknown'
>>> 
```
### `python -c "from astroid import __pkginfo__; print(__pkginfo__.version)"` output

2.8.6-dev0


## Hints

Thank you for opening the issue.
I don't believe `Unknown().as_string()` is ever called regularly. AFAIK it's only used during inference. What should the string representation of an `Unknown` node be? So not sure this needs to be addressed.
Probably just `'Unknown'`.
It's mostly only a problem when we do something like this:

```python
inferred = infer(node)
if inferred is not Uninferable:
    if inferred.as_string().contains(some_value):
        ...
```
So for the most part, as long as it doesn't crash we're good.

## Patch

```diff

diff --git a/astroid/nodes/as_string.py b/astroid/nodes/as_string.py
--- a/astroid/nodes/as_string.py
+++ b/astroid/nodes/as_string.py
@@ -36,6 +36,7 @@
         MatchSingleton,
         MatchStar,
         MatchValue,
+        Unknown,
     )
 
 # pylint: disable=unused-argument
@@ -643,6 +644,9 @@ def visit_property(self, node):
     def visit_evaluatedobject(self, node):
         return node.original.accept(self)
 
+    def visit_unknown(self, node: "Unknown") -> str:
+        return str(node)
+
 
 def _import_string(names):
     """return a list of (name, asname) formatted as a string"""


```

## Test Patch

```diff
diff --git a/tests/unittest_nodes.py b/tests/unittest_nodes.py
--- a/tests/unittest_nodes.py
+++ b/tests/unittest_nodes.py
@@ -306,6 +306,11 @@ def test_f_strings(self):
         ast = abuilder.string_build(code)
         self.assertEqual(ast.as_string().strip(), code.strip())
 
+    @staticmethod
+    def test_as_string_unknown() -> None:
+        assert nodes.Unknown().as_string() == "Unknown.Unknown()"
+        assert nodes.Unknown(lineno=1, col_offset=0).as_string() == "Unknown.Unknown()"
+
 
 class _NodeTest(unittest.TestCase):
     """test transformation of If Node"""

```

## Test Information

**Tests that should FAIL→PASS**: ["tests/unittest_nodes.py::AsStringTest::test_as_string_unknown"]

**Tests that should PASS→PASS**: ["tests/unittest_nodes.py::AsStringTest::test_3k_annotations_and_metaclass", "tests/unittest_nodes.py::AsStringTest::test_3k_as_string", "tests/unittest_nodes.py::AsStringTest::test_as_string", "tests/unittest_nodes.py::AsStringTest::test_as_string_for_list_containing_uninferable", "tests/unittest_nodes.py::AsStringTest::test_class_def", "tests/unittest_nodes.py::AsStringTest::test_ellipsis", "tests/unittest_nodes.py::AsStringTest::test_f_strings", "tests/unittest_nodes.py::AsStringTest::test_frozenset_as_string", "tests/unittest_nodes.py::AsStringTest::test_func_signature_issue_185", "tests/unittest_nodes.py::AsStringTest::test_int_attribute", "tests/unittest_nodes.py::AsStringTest::test_module2_as_string", "tests/unittest_nodes.py::AsStringTest::test_module_as_string", "tests/unittest_nodes.py::AsStringTest::test_operator_precedence", "tests/unittest_nodes.py::AsStringTest::test_slice_and_subscripts", "tests/unittest_nodes.py::AsStringTest::test_slices", "tests/unittest_nodes.py::AsStringTest::test_tuple_as_string", "tests/unittest_nodes.py::AsStringTest::test_varargs_kwargs_as_string", "tests/unittest_nodes.py::IfNodeTest::test_block_range", "tests/unittest_nodes.py::IfNodeTest::test_if_elif_else_node", "tests/unittest_nodes.py::IfNodeTest::test_if_sys_guard", "tests/unittest_nodes.py::IfNodeTest::test_if_typing_guard", "tests/unittest_nodes.py::TryExceptNodeTest::test_block_range", "tests/unittest_nodes.py::TryFinallyNodeTest::test_block_range", "tests/unittest_nodes.py::TryExceptFinallyNodeTest::test_block_range", "tests/unittest_nodes.py::ImportNodeTest::test_absolute_import", "tests/unittest_nodes.py::ImportNodeTest::test_as_string", "tests/unittest_nodes.py::ImportNodeTest::test_bad_import_inference", "tests/unittest_nodes.py::ImportNodeTest::test_conditional", "tests/unittest_nodes.py::ImportNodeTest::test_conditional_import", "tests/unittest_nodes.py::ImportNodeTest::test_from_self_resolve", "tests/unittest_nodes.py::ImportNodeTest::test_import_self_resolve", "tests/unittest_nodes.py::ImportNodeTest::test_more_absolute_import", "tests/unittest_nodes.py::ImportNodeTest::test_real_name", "tests/unittest_nodes.py::CmpNodeTest::test_as_string", "tests/unittest_nodes.py::ConstNodeTest::test_bool", "tests/unittest_nodes.py::ConstNodeTest::test_complex", "tests/unittest_nodes.py::ConstNodeTest::test_copy", "tests/unittest_nodes.py::ConstNodeTest::test_float", "tests/unittest_nodes.py::ConstNodeTest::test_int", "tests/unittest_nodes.py::ConstNodeTest::test_none", "tests/unittest_nodes.py::ConstNodeTest::test_str", "tests/unittest_nodes.py::ConstNodeTest::test_str_kind", "tests/unittest_nodes.py::ConstNodeTest::test_unicode", "tests/unittest_nodes.py::NameNodeTest::test_assign_to_true", "tests/unittest_nodes.py::TestNamedExprNode::test_frame", "tests/unittest_nodes.py::TestNamedExprNode::test_scope", "tests/unittest_nodes.py::AnnAssignNodeTest::test_as_string", "tests/unittest_nodes.py::AnnAssignNodeTest::test_complex", "tests/unittest_nodes.py::AnnAssignNodeTest::test_primitive", "tests/unittest_nodes.py::AnnAssignNodeTest::test_primitive_without_initial_value", "tests/unittest_nodes.py::ArgumentsNodeTC::test_kwoargs", "tests/unittest_nodes.py::ArgumentsNodeTC::test_positional_only", "tests/unittest_nodes.py::UnboundMethodNodeTest::test_no_super_getattr", "tests/unittest_nodes.py::BoundMethodNodeTest::test_is_property", "tests/unittest_nodes.py::AliasesTest::test_aliases", "tests/unittest_nodes.py::Python35AsyncTest::test_async_await_keywords", "tests/unittest_nodes.py::Python35AsyncTest::test_asyncfor_as_string", "tests/unittest_nodes.py::Python35AsyncTest::test_asyncwith_as_string", "tests/unittest_nodes.py::Python35AsyncTest::test_await_as_string", "tests/unittest_nodes.py::Python35AsyncTest::test_decorated_async_def_as_string", "tests/unittest_nodes.py::ContextTest::test_list_del", "tests/unittest_nodes.py::ContextTest::test_list_load", "tests/unittest_nodes.py::ContextTest::test_list_store", "tests/unittest_nodes.py::ContextTest::test_starred_load", "tests/unittest_nodes.py::ContextTest::test_starred_store", "tests/unittest_nodes.py::ContextTest::test_subscript_del", "tests/unittest_nodes.py::ContextTest::test_subscript_load", "tests/unittest_nodes.py::ContextTest::test_subscript_store", "tests/unittest_nodes.py::ContextTest::test_tuple_load", "tests/unittest_nodes.py::ContextTest::test_tuple_store", "tests/unittest_nodes.py::test_unknown", "tests/unittest_nodes.py::test_type_comments_with", "tests/unittest_nodes.py::test_type_comments_for", "tests/unittest_nodes.py::test_type_coments_assign", "tests/unittest_nodes.py::test_type_comments_invalid_expression", "tests/unittest_nodes.py::test_type_comments_invalid_function_comments", "tests/unittest_nodes.py::test_type_comments_function", "tests/unittest_nodes.py::test_type_comments_arguments", "tests/unittest_nodes.py::test_type_comments_posonly_arguments", "tests/unittest_nodes.py::test_correct_function_type_comment_parent", "tests/unittest_nodes.py::test_is_generator_for_yield_assignments", "tests/unittest_nodes.py::test_f_string_correct_line_numbering", "tests/unittest_nodes.py::test_assignment_expression", "tests/unittest_nodes.py::test_assignment_expression_in_functiondef", "tests/unittest_nodes.py::test_get_doc", "tests/unittest_nodes.py::test_parse_fstring_debug_mode", "tests/unittest_nodes.py::test_parse_type_comments_with_proper_parent", "tests/unittest_nodes.py::test_const_itered", "tests/unittest_nodes.py::test_is_generator_for_yield_in_while", "tests/unittest_nodes.py::test_is_generator_for_yield_in_if", "tests/unittest_nodes.py::test_is_generator_for_yield_in_aug_assign"]

**Base Commit**: ce5cbce5ba11cdc2f8139ade66feea1e181a7944
**Environment Setup Commit**: 0d1211558670cfefd95b39984b8d5f7f34837f32
