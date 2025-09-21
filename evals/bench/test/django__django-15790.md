# django__django-15790

**Repository**: django/django
**Created**: 2022-06-23T11:02:06Z
**Version**: 4.2

## Problem Statement

check_for_template_tags_with_the_same_name with libraries in TEMPLATES
Description
	
I didn't explore this thoroughly, but I think there might be an issue with the check_for_template_tags_with_the_same_name when you add a template tag library into TEMPLATES['OPTIONS']['librairies'].
I'm getting an error like: 
(templates.E003) 'my_tags' is used for multiple template tag modules: 'someapp.templatetags.my_tags', 'someapp.templatetags.my_tags'


## Hints

Thanks for the report. It's a bug in the new system check (see 004b4620f6f4ad87261e149898940f2dcd5757ef and #32987).

## Patch

```diff

diff --git a/django/core/checks/templates.py b/django/core/checks/templates.py
--- a/django/core/checks/templates.py
+++ b/django/core/checks/templates.py
@@ -50,15 +50,15 @@ def check_string_if_invalid_is_string(app_configs, **kwargs):
 @register(Tags.templates)
 def check_for_template_tags_with_the_same_name(app_configs, **kwargs):
     errors = []
-    libraries = defaultdict(list)
+    libraries = defaultdict(set)
 
     for conf in settings.TEMPLATES:
         custom_libraries = conf.get("OPTIONS", {}).get("libraries", {})
         for module_name, module_path in custom_libraries.items():
-            libraries[module_name].append(module_path)
+            libraries[module_name].add(module_path)
 
     for module_name, module_path in get_template_tag_modules():
-        libraries[module_name].append(module_path)
+        libraries[module_name].add(module_path)
 
     for library_name, items in libraries.items():
         if len(items) > 1:
@@ -66,7 +66,7 @@ def check_for_template_tags_with_the_same_name(app_configs, **kwargs):
                 Error(
                     E003.msg.format(
                         repr(library_name),
-                        ", ".join(repr(item) for item in items),
+                        ", ".join(repr(item) for item in sorted(items)),
                     ),
                     id=E003.id,
                 )


```

## Test Patch

```diff
diff --git a/tests/check_framework/test_templates.py b/tests/check_framework/test_templates.py
--- a/tests/check_framework/test_templates.py
+++ b/tests/check_framework/test_templates.py
@@ -158,6 +158,19 @@ def test_template_tags_with_same_library_name(self):
                 [self.error_same_tags],
             )
 
+    @override_settings(
+        INSTALLED_APPS=["check_framework.template_test_apps.same_tags_app_1"]
+    )
+    def test_template_tags_same_library_in_installed_apps_libraries(self):
+        with self.settings(
+            TEMPLATES=[
+                self.get_settings(
+                    "same_tags", "same_tags_app_1.templatetags.same_tags"
+                ),
+            ]
+        ):
+            self.assertEqual(check_for_template_tags_with_the_same_name(None), [])
+
     @override_settings(
         INSTALLED_APPS=["check_framework.template_test_apps.same_tags_app_1"]
     )

```

## Test Information

**Tests that should FAIL→PASS**: ["test_template_tags_same_library_in_installed_apps_libraries (check_framework.test_templates.CheckTemplateTagLibrariesWithSameName)"]

**Tests that should PASS→PASS**: ["Error if template loaders are specified and APP_DIRS is True.", "test_app_dirs_removed (check_framework.test_templates.CheckTemplateSettingsAppDirsTest)", "test_loaders_removed (check_framework.test_templates.CheckTemplateSettingsAppDirsTest)", "test_string_if_invalid_both_are_strings (check_framework.test_templates.CheckTemplateStringIfInvalidTest)", "test_string_if_invalid_first_is_string (check_framework.test_templates.CheckTemplateStringIfInvalidTest)", "test_string_if_invalid_not_specified (check_framework.test_templates.CheckTemplateStringIfInvalidTest)", "test_string_if_invalid_not_string (check_framework.test_templates.CheckTemplateStringIfInvalidTest)", "test_template_tags_with_different_library_name (check_framework.test_templates.CheckTemplateTagLibrariesWithSameName)", "test_template_tags_with_different_name (check_framework.test_templates.CheckTemplateTagLibrariesWithSameName)", "test_template_tags_with_same_library_name (check_framework.test_templates.CheckTemplateTagLibrariesWithSameName)", "test_template_tags_with_same_library_name_and_module_name (check_framework.test_templates.CheckTemplateTagLibrariesWithSameName)", "test_template_tags_with_same_name (check_framework.test_templates.CheckTemplateTagLibrariesWithSameName)"]

**Base Commit**: c627226d05dd52aef59447dcfb29cec2c2b11b8a
**Environment Setup Commit**: 0fbdb9784da915fce5dcc1fe82bac9b4785749e5
