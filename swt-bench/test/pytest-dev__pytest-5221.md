# pytest-dev__pytest-5221

**Repository**: pytest-dev/pytest
**Created**: 2019-05-06T22:36:44Z
**Version**: 4.4

## Problem Statement

Display fixture scope with `pytest --fixtures`
It would be useful to show fixture scopes with `pytest --fixtures`; currently the only way to learn the scope of a fixture is look at the docs (when that is documented) or at the source code.


## Patch

```diff

diff --git a/src/_pytest/python.py b/src/_pytest/python.py
--- a/src/_pytest/python.py
+++ b/src/_pytest/python.py
@@ -1342,17 +1342,19 @@ def _showfixtures_main(config, session):
                 currentmodule = module
         if verbose <= 0 and argname[0] == "_":
             continue
+        tw.write(argname, green=True)
+        if fixturedef.scope != "function":
+            tw.write(" [%s scope]" % fixturedef.scope, cyan=True)
         if verbose > 0:
-            funcargspec = "%s -- %s" % (argname, bestrel)
-        else:
-            funcargspec = argname
-        tw.line(funcargspec, green=True)
+            tw.write(" -- %s" % bestrel, yellow=True)
+        tw.write("\n")
         loc = getlocation(fixturedef.func, curdir)
         doc = fixturedef.func.__doc__ or ""
         if doc:
             write_docstring(tw, doc)
         else:
             tw.line("    %s: no docstring available" % (loc,), red=True)
+        tw.line()
 
 
 def write_docstring(tw, doc, indent="    "):


```

## Test Patch

```diff
diff --git a/testing/python/fixtures.py b/testing/python/fixtures.py
--- a/testing/python/fixtures.py
+++ b/testing/python/fixtures.py
@@ -3037,11 +3037,25 @@ def test_funcarg_compat(self, testdir):
 
     def test_show_fixtures(self, testdir):
         result = testdir.runpytest("--fixtures")
-        result.stdout.fnmatch_lines(["*tmpdir*", "*temporary directory*"])
+        result.stdout.fnmatch_lines(
+            [
+                "tmpdir_factory [[]session scope[]]",
+                "*for the test session*",
+                "tmpdir",
+                "*temporary directory*",
+            ]
+        )
 
     def test_show_fixtures_verbose(self, testdir):
         result = testdir.runpytest("--fixtures", "-v")
-        result.stdout.fnmatch_lines(["*tmpdir*--*tmpdir.py*", "*temporary directory*"])
+        result.stdout.fnmatch_lines(
+            [
+                "tmpdir_factory [[]session scope[]] -- *tmpdir.py*",
+                "*for the test session*",
+                "tmpdir -- *tmpdir.py*",
+                "*temporary directory*",
+            ]
+        )
 
     def test_show_fixtures_testmodule(self, testdir):
         p = testdir.makepyfile(

```

## Test Information

**Tests that should FAIL→PASS**: ["testing/python/fixtures.py::TestShowFixtures::test_show_fixtures", "testing/python/fixtures.py::TestShowFixtures::test_show_fixtures_verbose"]

**Tests that should PASS→PASS**: ["testing/python/fixtures.py::test_getfuncargnames", "testing/python/fixtures.py::TestFillFixtures::test_fillfuncargs_exposed", "testing/python/fixtures.py::TestShowFixtures::test_fixture_disallow_twice", "testing/python/fixtures.py::test_call_fixture_function_error", "testing/python/fixtures.py::TestFillFixtures::test_funcarg_lookupfails", "testing/python/fixtures.py::TestFillFixtures::test_detect_recursive_dependency_error", "testing/python/fixtures.py::TestFillFixtures::test_funcarg_basic", "testing/python/fixtures.py::TestFillFixtures::test_funcarg_lookup_modulelevel", "testing/python/fixtures.py::TestFillFixtures::test_funcarg_lookup_classlevel", "testing/python/fixtures.py::TestFillFixtures::test_conftest_funcargs_only_available_in_subdir", "testing/python/fixtures.py::TestFillFixtures::test_extend_fixture_module_class", "testing/python/fixtures.py::TestFillFixtures::test_extend_fixture_conftest_module", "testing/python/fixtures.py::TestFillFixtures::test_extend_fixture_conftest_conftest", "testing/python/fixtures.py::TestFillFixtures::test_extend_fixture_conftest_plugin", "testing/python/fixtures.py::TestFillFixtures::test_extend_fixture_plugin_plugin", "testing/python/fixtures.py::TestFillFixtures::test_override_parametrized_fixture_conftest_module", "testing/python/fixtures.py::TestFillFixtures::test_override_parametrized_fixture_conftest_conftest", "testing/python/fixtures.py::TestFillFixtures::test_override_non_parametrized_fixture_conftest_module", "testing/python/fixtures.py::TestFillFixtures::test_override_non_parametrized_fixture_conftest_conftest", "testing/python/fixtures.py::TestFillFixtures::test_override_autouse_fixture_with_parametrized_fixture_conftest_conftest", "testing/python/fixtures.py::TestFillFixtures::test_autouse_fixture_plugin", "testing/python/fixtures.py::TestFillFixtures::test_funcarg_lookup_error", "testing/python/fixtures.py::TestFillFixtures::test_fixture_excinfo_leak", "testing/python/fixtures.py::TestRequestBasic::test_request_attributes", "testing/python/fixtures.py::TestRequestBasic::test_request_attributes_method", "testing/python/fixtures.py::TestRequestBasic::test_request_contains_funcarg_arg2fixturedefs", "testing/python/fixtures.py::TestRequestBasic::test_request_garbage", "testing/python/fixtures.py::TestRequestBasic::test_getfixturevalue_recursive", "testing/python/fixtures.py::TestRequestBasic::test_getfixturevalue_teardown", "testing/python/fixtures.py::TestRequestBasic::test_getfixturevalue[getfixturevalue]", "testing/python/fixtures.py::TestRequestBasic::test_getfixturevalue[getfuncargvalue]", "testing/python/fixtures.py::TestRequestBasic::test_request_addfinalizer", "testing/python/fixtures.py::TestRequestBasic::test_request_addfinalizer_failing_setup", "testing/python/fixtures.py::TestRequestBasic::test_request_addfinalizer_failing_setup_module", "testing/python/fixtures.py::TestRequestBasic::test_request_addfinalizer_partial_setup_failure", "testing/python/fixtures.py::TestRequestBasic::test_request_subrequest_addfinalizer_exceptions", "testing/python/fixtures.py::TestRequestBasic::test_request_getmodulepath", "testing/python/fixtures.py::TestRequestBasic::test_request_fixturenames", "testing/python/fixtures.py::TestRequestBasic::test_request_fixturenames_dynamic_fixture", "testing/python/fixtures.py::TestRequestBasic::test_funcargnames_compatattr", "testing/python/fixtures.py::TestRequestBasic::test_setupdecorator_and_xunit", "testing/python/fixtures.py::TestRequestBasic::test_fixtures_sub_subdir_normalize_sep", "testing/python/fixtures.py::TestRequestBasic::test_show_fixtures_color_yes", "testing/python/fixtures.py::TestRequestBasic::test_newstyle_with_request", "testing/python/fixtures.py::TestRequestBasic::test_setupcontext_no_param", "testing/python/fixtures.py::TestRequestMarking::test_applymarker", "testing/python/fixtures.py::TestRequestMarking::test_accesskeywords", "testing/python/fixtures.py::TestRequestMarking::test_accessmarker_dynamic", "testing/python/fixtures.py::TestFixtureUsages::test_noargfixturedec", "testing/python/fixtures.py::TestFixtureUsages::test_receives_funcargs", "testing/python/fixtures.py::TestFixtureUsages::test_receives_funcargs_scope_mismatch", "testing/python/fixtures.py::TestFixtureUsages::test_receives_funcargs_scope_mismatch_issue660", "testing/python/fixtures.py::TestFixtureUsages::test_invalid_scope", "testing/python/fixtures.py::TestFixtureUsages::test_funcarg_parametrized_and_used_twice", "testing/python/fixtures.py::TestFixtureUsages::test_factory_uses_unknown_funcarg_as_dependency_error", "testing/python/fixtures.py::TestFixtureUsages::test_factory_setup_as_classes_fails", "testing/python/fixtures.py::TestFixtureUsages::test_request_can_be_overridden", "testing/python/fixtures.py::TestFixtureUsages::test_usefixtures_marker", "testing/python/fixtures.py::TestFixtureUsages::test_usefixtures_ini", "testing/python/fixtures.py::TestFixtureUsages::test_usefixtures_seen_in_showmarkers", "testing/python/fixtures.py::TestFixtureUsages::test_request_instance_issue203", "testing/python/fixtures.py::TestFixtureUsages::test_fixture_parametrized_with_iterator", "testing/python/fixtures.py::TestFixtureUsages::test_setup_functions_as_fixtures", "testing/python/fixtures.py::TestFixtureManagerParseFactories::test_parsefactories_evil_objects_issue214", "testing/python/fixtures.py::TestFixtureManagerParseFactories::test_parsefactories_conftest", "testing/python/fixtures.py::TestFixtureManagerParseFactories::test_parsefactories_conftest_and_module_and_class", "testing/python/fixtures.py::TestFixtureManagerParseFactories::test_parsefactories_relative_node_ids", "testing/python/fixtures.py::TestFixtureManagerParseFactories::test_package_xunit_fixture", "testing/python/fixtures.py::TestFixtureManagerParseFactories::test_package_fixture_complex", "testing/python/fixtures.py::TestFixtureManagerParseFactories::test_collect_custom_items", "testing/python/fixtures.py::TestAutouseDiscovery::test_parsefactories_conftest", "testing/python/fixtures.py::TestAutouseDiscovery::test_two_classes_separated_autouse", "testing/python/fixtures.py::TestAutouseDiscovery::test_setup_at_classlevel", "testing/python/fixtures.py::TestAutouseDiscovery::test_callables_nocode", "testing/python/fixtures.py::TestAutouseDiscovery::test_autouse_in_conftests", "testing/python/fixtures.py::TestAutouseDiscovery::test_autouse_in_module_and_two_classes", "testing/python/fixtures.py::TestAutouseManagement::test_autouse_conftest_mid_directory", "testing/python/fixtures.py::TestAutouseManagement::test_funcarg_and_setup", "testing/python/fixtures.py::TestAutouseManagement::test_uses_parametrized_resource", "testing/python/fixtures.py::TestAutouseManagement::test_session_parametrized_function", "testing/python/fixtures.py::TestAutouseManagement::test_class_function_parametrization_finalization", "testing/python/fixtures.py::TestAutouseManagement::test_scope_ordering", "testing/python/fixtures.py::TestAutouseManagement::test_parametrization_setup_teardown_ordering", "testing/python/fixtures.py::TestAutouseManagement::test_ordering_autouse_before_explicit", "testing/python/fixtures.py::TestAutouseManagement::test_ordering_dependencies_torndown_first[p10-p00]", "testing/python/fixtures.py::TestAutouseManagement::test_ordering_dependencies_torndown_first[p10-p01]", "testing/python/fixtures.py::TestAutouseManagement::test_ordering_dependencies_torndown_first[p11-p00]", "testing/python/fixtures.py::TestAutouseManagement::test_ordering_dependencies_torndown_first[p11-p01]", "testing/python/fixtures.py::TestFixtureMarker::test_parametrize", "testing/python/fixtures.py::TestFixtureMarker::test_multiple_parametrization_issue_736", "testing/python/fixtures.py::TestFixtureMarker::test_override_parametrized_fixture_issue_979['fixt,", "testing/python/fixtures.py::TestFixtureMarker::test_override_parametrized_fixture_issue_979['fixt,val']", "testing/python/fixtures.py::TestFixtureMarker::test_override_parametrized_fixture_issue_979[['fixt',", "testing/python/fixtures.py::TestFixtureMarker::test_override_parametrized_fixture_issue_979[('fixt',", "testing/python/fixtures.py::TestFixtureMarker::test_scope_session", "testing/python/fixtures.py::TestFixtureMarker::test_scope_session_exc", "testing/python/fixtures.py::TestFixtureMarker::test_scope_session_exc_two_fix", "testing/python/fixtures.py::TestFixtureMarker::test_scope_exc", "testing/python/fixtures.py::TestFixtureMarker::test_scope_module_uses_session", "testing/python/fixtures.py::TestFixtureMarker::test_scope_module_and_finalizer", "testing/python/fixtures.py::TestFixtureMarker::test_scope_mismatch_various", "testing/python/fixtures.py::TestFixtureMarker::test_register_only_with_mark", "testing/python/fixtures.py::TestFixtureMarker::test_parametrize_and_scope", "testing/python/fixtures.py::TestFixtureMarker::test_scope_mismatch", "testing/python/fixtures.py::TestFixtureMarker::test_parametrize_separated_order", "testing/python/fixtures.py::TestFixtureMarker::test_module_parametrized_ordering", "testing/python/fixtures.py::TestFixtureMarker::test_dynamic_parametrized_ordering", "testing/python/fixtures.py::TestFixtureMarker::test_class_ordering", "testing/python/fixtures.py::TestFixtureMarker::test_parametrize_separated_order_higher_scope_first", "testing/python/fixtures.py::TestFixtureMarker::test_parametrized_fixture_teardown_order", "testing/python/fixtures.py::TestFixtureMarker::test_fixture_finalizer", "testing/python/fixtures.py::TestFixtureMarker::test_class_scope_with_normal_tests", "testing/python/fixtures.py::TestFixtureMarker::test_request_is_clean", "testing/python/fixtures.py::TestFixtureMarker::test_parametrize_separated_lifecycle", "testing/python/fixtures.py::TestFixtureMarker::test_parametrize_function_scoped_finalizers_called", "testing/python/fixtures.py::TestFixtureMarker::test_finalizer_order_on_parametrization[session]", "testing/python/fixtures.py::TestFixtureMarker::test_finalizer_order_on_parametrization[function]", "testing/python/fixtures.py::TestFixtureMarker::test_finalizer_order_on_parametrization[module]", "testing/python/fixtures.py::TestFixtureMarker::test_class_scope_parametrization_ordering", "testing/python/fixtures.py::TestFixtureMarker::test_parametrize_setup_function", "testing/python/fixtures.py::TestFixtureMarker::test_fixture_marked_function_not_collected_as_test", "testing/python/fixtures.py::TestFixtureMarker::test_params_and_ids", "testing/python/fixtures.py::TestFixtureMarker::test_params_and_ids_yieldfixture", "testing/python/fixtures.py::TestFixtureMarker::test_deterministic_fixture_collection", "testing/python/fixtures.py::TestRequestScopeAccess::test_setup[session--fspath", "testing/python/fixtures.py::TestRequestScopeAccess::test_setup[module-module", "testing/python/fixtures.py::TestRequestScopeAccess::test_setup[class-module", "testing/python/fixtures.py::TestRequestScopeAccess::test_setup[function-module", "testing/python/fixtures.py::TestRequestScopeAccess::test_funcarg[session--fspath", "testing/python/fixtures.py::TestRequestScopeAccess::test_funcarg[module-module", "testing/python/fixtures.py::TestRequestScopeAccess::test_funcarg[class-module", "testing/python/fixtures.py::TestRequestScopeAccess::test_funcarg[function-module", "testing/python/fixtures.py::TestErrors::test_subfactory_missing_funcarg", "testing/python/fixtures.py::TestErrors::test_issue498_fixture_finalizer_failing", "testing/python/fixtures.py::TestErrors::test_setupfunc_missing_funcarg", "testing/python/fixtures.py::TestShowFixtures::test_funcarg_compat", "testing/python/fixtures.py::TestShowFixtures::test_show_fixtures_testmodule", "testing/python/fixtures.py::TestShowFixtures::test_show_fixtures_conftest[True]", "testing/python/fixtures.py::TestShowFixtures::test_show_fixtures_conftest[False]", "testing/python/fixtures.py::TestShowFixtures::test_show_fixtures_trimmed_doc", "testing/python/fixtures.py::TestShowFixtures::test_show_fixtures_indented_doc", "testing/python/fixtures.py::TestShowFixtures::test_show_fixtures_indented_doc_first_line_unindented", "testing/python/fixtures.py::TestShowFixtures::test_show_fixtures_indented_in_class", "testing/python/fixtures.py::TestShowFixtures::test_show_fixtures_different_files", "testing/python/fixtures.py::TestShowFixtures::test_show_fixtures_with_same_name", "testing/python/fixtures.py::TestContextManagerFixtureFuncs::test_simple[fixture]", "testing/python/fixtures.py::TestContextManagerFixtureFuncs::test_simple[yield_fixture]", "testing/python/fixtures.py::TestContextManagerFixtureFuncs::test_scoped[fixture]", "testing/python/fixtures.py::TestContextManagerFixtureFuncs::test_scoped[yield_fixture]", "testing/python/fixtures.py::TestContextManagerFixtureFuncs::test_setup_exception[fixture]", "testing/python/fixtures.py::TestContextManagerFixtureFuncs::test_setup_exception[yield_fixture]", "testing/python/fixtures.py::TestContextManagerFixtureFuncs::test_teardown_exception[fixture]", "testing/python/fixtures.py::TestContextManagerFixtureFuncs::test_teardown_exception[yield_fixture]", "testing/python/fixtures.py::TestContextManagerFixtureFuncs::test_yields_more_than_one[fixture]", "testing/python/fixtures.py::TestContextManagerFixtureFuncs::test_yields_more_than_one[yield_fixture]", "testing/python/fixtures.py::TestContextManagerFixtureFuncs::test_custom_name[fixture]", "testing/python/fixtures.py::TestContextManagerFixtureFuncs::test_custom_name[yield_fixture]", "testing/python/fixtures.py::TestParameterizedSubRequest::test_call_from_fixture", "testing/python/fixtures.py::TestParameterizedSubRequest::test_call_from_test", "testing/python/fixtures.py::TestParameterizedSubRequest::test_external_fixture", "testing/python/fixtures.py::TestParameterizedSubRequest::test_non_relative_path", "testing/python/fixtures.py::test_pytest_fixture_setup_and_post_finalizer_hook", "testing/python/fixtures.py::TestScopeOrdering::test_func_closure_module_auto[mark]", "testing/python/fixtures.py::TestScopeOrdering::test_func_closure_module_auto[autouse]", "testing/python/fixtures.py::TestScopeOrdering::test_func_closure_with_native_fixtures", "testing/python/fixtures.py::TestScopeOrdering::test_func_closure_module", "testing/python/fixtures.py::TestScopeOrdering::test_func_closure_scopes_reordered", "testing/python/fixtures.py::TestScopeOrdering::test_func_closure_same_scope_closer_root_first", "testing/python/fixtures.py::TestScopeOrdering::test_func_closure_all_scopes_complex", "testing/python/fixtures.py::TestScopeOrdering::test_multiple_packages"]

**Base Commit**: 4a2fdce62b73944030cff9b3e52862868ca9584d
**Environment Setup Commit**: 4ccaa987d47566e3907f2f74167c4ab7997f622f
