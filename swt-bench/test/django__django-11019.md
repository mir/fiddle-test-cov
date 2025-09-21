# django__django-11019

**Repository**: django/django
**Created**: 2019-02-23T15:51:14Z
**Version**: 3.0

## Problem Statement

Merging 3 or more media objects can throw unnecessary MediaOrderConflictWarnings
Description
	
Consider the following form definition, where text-editor-extras.js depends on text-editor.js but all other JS files are independent:
from django import forms
class ColorPicker(forms.Widget):
	class Media:
		js = ['color-picker.js']
class SimpleTextWidget(forms.Widget):
	class Media:
		js = ['text-editor.js']
class FancyTextWidget(forms.Widget):
	class Media:
		js = ['text-editor.js', 'text-editor-extras.js', 'color-picker.js']
class MyForm(forms.Form):
	background_color = forms.CharField(widget=ColorPicker())
	intro = forms.CharField(widget=SimpleTextWidget())
	body = forms.CharField(widget=FancyTextWidget())
Django should be able to resolve the JS files for the final form into the order text-editor.js, text-editor-extras.js, color-picker.js. However, accessing MyForm().media results in:
/projects/django/django/forms/widgets.py:145: MediaOrderConflictWarning: Detected duplicate Media files in an opposite order:
text-editor-extras.js
text-editor.js
 MediaOrderConflictWarning,
Media(css={}, js=['text-editor-extras.js', 'color-picker.js', 'text-editor.js'])
The MediaOrderConflictWarning is a result of the order that the additions happen in: ColorPicker().media + SimpleTextWidget().media produces Media(css={}, js=['color-picker.js', 'text-editor.js']), which (wrongly) imposes the constraint that color-picker.js must appear before text-editor.js.
The final result is particularly unintuitive here, as it's worse than the "naïve" result produced by Django 1.11 before order-checking was added (color-picker.js, text-editor.js, text-editor-extras.js), and the pair of files reported in the warning message seems wrong too (aren't color-picker.js and text-editor.js the wrong-ordered ones?)


## Hints

As a tentative fix, I propose that media objects should explicitly distinguish between cases where we do / don't care about ordering, notionally something like: class FancyTextWidget(forms.Widget): class Media: js = { ('text-editor.js', 'text-editor-extras.js'), # tuple = order is important 'color-picker.js' # set = order is unimportant } (although using a set for this is problematic due to the need for contents to be hashable), and the result of adding two media objects should be a "don't care" so that we aren't introducing dependencies where the original objects didn't have them. We would then defer assembling them into a flat list until the final render call. I haven't worked out the rest of the algorithm yet, but I'm willing to dig further if this sounds like a sensible plan of attack...
Are you testing with the fix from #30153?
Yes, testing against current master (b39bd0aa6d5667d6bbcf7d349a1035c676e3f972).
So ​https://github.com/django/django/commit/959d0c078a1c903cd1e4850932be77c4f0d2294d (the fix for #30153) didn't make this case worse, it just didn't improve on it. The problem is actually the same I encountered, with the same unintuitive error message too. There is still a way to produce a conflicting order but it's harder to trigger in the administration interface now but unfortunately still easy. Also, going back to the state of things pre 2.0 was already discussed previously and rejected. Here's a failing test and and an idea to make this particular test pass: Merge the JS sublists starting from the longest list and continuing with shorter lists. The CSS case is missing yet. The right thing to do would be (against ​worse is better) to add some sort of dependency resolution solver with backtracking but that's surely a bad idea for many other reasons. The change makes some old tests fail (I only took a closer look at test_merge_js_three_way and in this case the failure is fine -- custom_widget.js is allowed to appear before jquery.js.) diff --git a/django/forms/widgets.py b/django/forms/widgets.py index 02aa32b207..d85c409152 100644 --- a/django/forms/widgets.py +++ b/django/forms/widgets.py @@ -70,9 +70,15 @@ class Media: @property def _js(self): - js = self._js_lists[0] + sorted_by_length = list(sorted( + filter(None, self._js_lists), + key=lambda lst: -len(lst), + )) + if not sorted_by_length: + return [] + js = sorted_by_length[0] # filter(None, ...) avoids calling merge() with empty lists. - for obj in filter(None, self._js_lists[1:]): + for obj in filter(None, sorted_by_length[1:]): js = self.merge(js, obj) return js diff --git a/tests/forms_tests/tests/test_media.py b/tests/forms_tests/tests/test_media.py index 8cb484a15e..9d17ad403b 100644 --- a/tests/forms_tests/tests/test_media.py +++ b/tests/forms_tests/tests/test_media.py @@ -571,3 +571,12 @@ class FormsMediaTestCase(SimpleTestCase): # was never specified. merged = widget3 + form1 + form2 self.assertEqual(merged._css, {'screen': ['a.css', 'b.css'], 'all': ['c.css']}) + + def test_merge_js_some_more(self): + widget1 = Media(js=['color-picker.js']) + widget2 = Media(js=['text-editor.js']) + widget3 = Media(js=['text-editor.js', 'text-editor-extras.js', 'color-picker.js']) + + merged = widget1 + widget2 + widget3 + + self.assertEqual(merged._js, ['text-editor.js', 'text-editor-extras.js', 'color-picker.js'])
Thinking some more: sorted() is more likely to break existing code because people probably haven't listed all dependencies in their js attributes now. Yes, that's not what they should have done, but breaking peoples' projects sucks and I don't really want to do that (even if introducing sorted() might be the least disruptive and at the same time most correct change) wanting to handle the jquery, widget1, noConflict and jquery, widget2, noConflict case has introduced an unexpected amount of complexity introducing a complex solving framework will have a really bad impact on runtime and will introduce even more complexity and is out of the question to me I'm happy to help fixing this but right now I only see bad and worse choices.
I don't think sorting by length is the way to go - it would be trivial to make the test fail again by extending the first list with unrelated items. It might be a good real-world heuristic for finding a solution more often, but that's just trading a reproducible bug for an unpredictable one. (I'm not sure I'd trust it as a heuristic either: we've encountered this issue on Wagtail CMS, where we're making extensive use of form media on hierarchical form structures, and so those media definitions will tend to bubble up several layers to reach the top level. At that point, there's no way of knowing whether the longer list is the one with more complex dependencies, or just one that collected more unrelated files on the way up the tree...) I'll do some more thinking on this. My hunch is that even if it does end up being a travelling-salesman-type problem, it's unlikely to be run on a large enough data set for performance to be an issue.
I don't think sorting by length is the way to go - it would be trivial to make the test fail again by extending the first list with unrelated items. It might be a good real-world heuristic for finding a solution more often, but that's just trading a reproducible bug for an unpredictable one. Well yes, if the ColorPicker itself would have a longer list of JS files it depends on then it would fail too. If, on the other hand, it wasn't a ColorPicker widget but a ColorPicker formset or form the initially declared lists would still be preserved and sorting the lists by length would give the correct result. Since #30153 the initially declared lists (or tuples) are preserved so maybe you have many JS and CSS declarations but as long as they are unrelated there will not be many long sublists. I'm obviously happy though if you're willing to spend the time finding a robust solution to this problem. (For the record: Personally I was happy with the state of things pre-2.0 too... and For the record 2: I'm also using custom widgets and inlines in feincms3/django-content-editor. It's really surprising to me that we didn't stumble on this earlier since we're always working on the latest Django version or even on pre-release versions if at all possible)
Hi there, I'm the dude who implemented the warning. I am not so sure this is a bug. Let's try tackle this step by step. The new merging algorithm that was introduced in version 2 is an improvement. It is the most accurate way to merge two sorted lists. It's not the simplest way, but has been reviewed plenty times. The warning is another story. It is independent from the algorithm. It merely tells you that the a certain order could not be maintained. We figured back than, that this would be a good idea. It warns a developer about a potential issue, but does not raise an exception. With that in mind, the correct way to deal with the issue described right now, is to ignore the warning. BUT, that doesn't mean that you don't have a valid point. There are implicit and explicit orders. Not all assets require ordering and (random) orders that only exist because of Media merging don't matter at all. This brings me back to a point that I have [previously made](https://code.djangoproject.com/ticket/30153#comment:6). It would make sense to store the original lists, which is now the case on master, and only raise if the order violates the original list. The current implementation on master could also be improved by removing duplicates. Anyways, I would considers those changes improvements, but not bug fixes. I didn't have time yet to look into this. But I do have some time this weekend. If you want I can take another look into this and propose a solution that solves this issue. Best -Joe
"Ignore the warning" doesn't work here - the order-fixing has broken the dependency between text-editor.js and text-editor-extras.js. I can (reluctantly) accept an implementation that produces false warnings, and I can accept that a genuine dependency loop might produce undefined behaviour, but the combination of the two - breaking the ordering as a result of seeing a loop that isn't there - is definitely a bug. (To be clear, I'm not suggesting that the 2.x implementation is a step backwards from not doing order checking at all - but it does introduce a new failure case, and that's what I'm keen to fix.)
To summarise: Even with the new strategy in #30153 of holding on to the un-merged lists as long as possible, the final merging is still done by adding one list at a time. The intermediate results are lists, which are assumed to be order-critical; this means the intermediate results have additional constraints that are not present in the original lists, causing it to see conflicts where there aren't any. Additionally, we should try to preserve the original sequence of files as much as possible, to avoid unnecessarily breaking user code that hasn't fully specified its dependencies and is relying on the 1.x behaviour. I think we need to approach this as a graph problem (which I realise might sound like overkill, but I'd rather start with something formally correct and optimise later as necessary): a conflict occurs whenever the dependency graph is cyclic. #30153 is a useful step towards this, as it ensures we have the accurate dependency graph up until the point where we need to assemble the final list. I suggest we replace Media.merge with a new method that accepts any number of lists (using *args if we want to preserve the existing method signature for backwards compatibility). This would work as follows: Iterate over all items in all sub-lists, building a dependency graph (where a dependency is any item that immediately precedes it within a sub-list) and a de-duplicated list containing all items indexed in the order they are first encountered Starting from the first item in the de-duplicated list, backtrack through the dependency graph, following the lowest-indexed dependency each time until we reach an item with no dependencies. While backtracking, maintain a stack of visited items. If we encounter an item already on the stack, this is a dependency loop; throw a MediaOrderConflictWarning and break out of the backtracking loop Output the resulting item, then remove it from the dependency graph and the de-duplicated list If the 'visited items' stack is non-empty, pop the last item off it and repeat the backtracking step from there. Otherwise, repeat the backtracking step starting from the next item in the de-duplicated list Repeat until no items remain
This sounds correct. I'm not sure it's right though. It does sound awfully complex for what there is to gain. Maintaining this down the road will not get easier. Finding, explaining and understanding the fix for #30153 did already cost a lot of time which could also have been invested elsewhere. If I manually assign widget3's JS lists (see https://code.djangoproject.com/ticket/30179#comment:5) then everything just works and the final result is correct: # widget3 = Media(js=['text-editor.js', 'text-editor-extras.js', 'color-picker.js']) widget3 = Media() widget3._js_lists = [['text-editor.js', 'text-editor-extras.js'], ['color-picker.js']] So what you proposed first (https://code.djangoproject.com/ticket/30179#comment:1) might just work fine and would be good enough (tm). Something like ​https://github.com/django/django/blob/543fc97407a932613d283c1e0bb47616cf8782e3/django/forms/widgets.py#L52 # Instead of self._js_lists = [js]: self._js_lists = list(js) if isinstance(js, set) else [js]
@Matthias: I think that solution will work, but only if: 1) we're going to insist that users always use this notation wherever a "non-dependency" exists - i.e. it is considered user error for the user to forget to put color-picker.js in its own sub-list 2) we have a very tight definition of what a dependency is - e.g. color-picker.js can't legally be a dependency of text-editor.js / text-editor-extras.js, because it exists on its own in ColorPicker's media - which also invalidates the [jquery, widget1, noconflict] + [jquery, widget2, noconflict] case (does noconflict depend on widget1 or not?) I suspect you only have to go slightly before the complexity of [jquery, widget1, noconflict] + [jquery, widget2, noconflict] before you start running into counter-examples again.
PR: ​https://github.com/django/django/pull/11010 I encountered another subtle bug along the way (which I suspect has existed since 1.x): #12879 calls for us to strip duplicates from the input lists, but in the current implementation the only de-duplication happens during Media.merge, so this never happens in the case of a single list. I've now extended the tests to cover this: ​https://github.com/django/django/pull/11010/files#diff-7fc04ae9019782c1884a0e97e96eda1eR154 . As a minor side effect of this extra de-duplication step, tuples get converted to lists more often, so I've had to fix up some existing tests accordingly - hopefully that's acceptable fall-out :-)
Matt, great work. I believe it is best to merge all lists at once and not sequentially as I did. Based on your work, I would suggest to simply use the algorithms implemented in Python. Therefore the whole merge function can be replaced with a simple one liner: import heapq from collections import OrderedDict def merge(*sublists): return list(OrderedDict.fromkeys(heapq.merge(*sublists))) # >>> merge([3],[1],[1,2],[2,3]) # [1, 2, 3]
It actually behaves different. I will continue to review your pull-request. As stated there, it would be helpful if there is some kind of resource to understand what strategy you implemented. For now I will try to review it without it.

## Patch

```diff

diff --git a/django/forms/widgets.py b/django/forms/widgets.py
--- a/django/forms/widgets.py
+++ b/django/forms/widgets.py
@@ -6,16 +6,21 @@
 import datetime
 import re
 import warnings
+from collections import defaultdict
 from itertools import chain
 
 from django.conf import settings
 from django.forms.utils import to_current_timezone
 from django.templatetags.static import static
 from django.utils import datetime_safe, formats
+from django.utils.datastructures import OrderedSet
 from django.utils.dates import MONTHS
 from django.utils.formats import get_format
 from django.utils.html import format_html, html_safe
 from django.utils.safestring import mark_safe
+from django.utils.topological_sort import (
+    CyclicDependencyError, stable_topological_sort,
+)
 from django.utils.translation import gettext_lazy as _
 
 from .renderers import get_default_renderer
@@ -59,22 +64,15 @@ def __str__(self):
 
     @property
     def _css(self):
-        css = self._css_lists[0]
-        # filter(None, ...) avoids calling merge with empty dicts.
-        for obj in filter(None, self._css_lists[1:]):
-            css = {
-                medium: self.merge(css.get(medium, []), obj.get(medium, []))
-                for medium in css.keys() | obj.keys()
-            }
-        return css
+        css = defaultdict(list)
+        for css_list in self._css_lists:
+            for medium, sublist in css_list.items():
+                css[medium].append(sublist)
+        return {medium: self.merge(*lists) for medium, lists in css.items()}
 
     @property
     def _js(self):
-        js = self._js_lists[0]
-        # filter(None, ...) avoids calling merge() with empty lists.
-        for obj in filter(None, self._js_lists[1:]):
-            js = self.merge(js, obj)
-        return js
+        return self.merge(*self._js_lists)
 
     def render(self):
         return mark_safe('\n'.join(chain.from_iterable(getattr(self, 'render_' + name)() for name in MEDIA_TYPES)))
@@ -115,39 +113,37 @@ def __getitem__(self, name):
         raise KeyError('Unknown media type "%s"' % name)
 
     @staticmethod
-    def merge(list_1, list_2):
+    def merge(*lists):
         """
-        Merge two lists while trying to keep the relative order of the elements.
-        Warn if the lists have the same two elements in a different relative
-        order.
+        Merge lists while trying to keep the relative order of the elements.
+        Warn if the lists have the same elements in a different relative order.
 
         For static assets it can be important to have them included in the DOM
         in a certain order. In JavaScript you may not be able to reference a
         global or in CSS you might want to override a style.
         """
-        # Start with a copy of list_1.
-        combined_list = list(list_1)
-        last_insert_index = len(list_1)
-        # Walk list_2 in reverse, inserting each element into combined_list if
-        # it doesn't already exist.
-        for path in reversed(list_2):
-            try:
-                # Does path already exist in the list?
-                index = combined_list.index(path)
-            except ValueError:
-                # Add path to combined_list since it doesn't exist.
-                combined_list.insert(last_insert_index, path)
-            else:
-                if index > last_insert_index:
-                    warnings.warn(
-                        'Detected duplicate Media files in an opposite order:\n'
-                        '%s\n%s' % (combined_list[last_insert_index], combined_list[index]),
-                        MediaOrderConflictWarning,
-                    )
-                # path already exists in the list. Update last_insert_index so
-                # that the following elements are inserted in front of this one.
-                last_insert_index = index
-        return combined_list
+        dependency_graph = defaultdict(set)
+        all_items = OrderedSet()
+        for list_ in filter(None, lists):
+            head = list_[0]
+            # The first items depend on nothing but have to be part of the
+            # dependency graph to be included in the result.
+            dependency_graph.setdefault(head, set())
+            for item in list_:
+                all_items.add(item)
+                # No self dependencies
+                if head != item:
+                    dependency_graph[item].add(head)
+                head = item
+        try:
+            return stable_topological_sort(all_items, dependency_graph)
+        except CyclicDependencyError:
+            warnings.warn(
+                'Detected duplicate Media files in an opposite order: {}'.format(
+                    ', '.join(repr(l) for l in lists)
+                ), MediaOrderConflictWarning,
+            )
+            return list(all_items)
 
     def __add__(self, other):
         combined = Media()


```

## Test Patch

```diff
diff --git a/tests/admin_inlines/tests.py b/tests/admin_inlines/tests.py
--- a/tests/admin_inlines/tests.py
+++ b/tests/admin_inlines/tests.py
@@ -497,10 +497,10 @@ def test_inline_media_only_inline(self):
             response.context['inline_admin_formsets'][0].media._js,
             [
                 'admin/js/vendor/jquery/jquery.min.js',
-                'admin/js/jquery.init.js',
-                'admin/js/inlines.min.js',
                 'my_awesome_inline_scripts.js',
                 'custom_number.js',
+                'admin/js/jquery.init.js',
+                'admin/js/inlines.min.js',
             ]
         )
         self.assertContains(response, 'my_awesome_inline_scripts.js')
diff --git a/tests/admin_widgets/test_autocomplete_widget.py b/tests/admin_widgets/test_autocomplete_widget.py
--- a/tests/admin_widgets/test_autocomplete_widget.py
+++ b/tests/admin_widgets/test_autocomplete_widget.py
@@ -139,4 +139,4 @@ def test_media(self):
                 else:
                     expected_files = base_files
                 with translation.override(lang):
-                    self.assertEqual(AutocompleteSelect(rel, admin.site).media._js, expected_files)
+                    self.assertEqual(AutocompleteSelect(rel, admin.site).media._js, list(expected_files))
diff --git a/tests/forms_tests/tests/test_media.py b/tests/forms_tests/tests/test_media.py
--- a/tests/forms_tests/tests/test_media.py
+++ b/tests/forms_tests/tests/test_media.py
@@ -25,8 +25,8 @@ def test_construction(self):
         )
         self.assertEqual(
             repr(m),
-            "Media(css={'all': ('path/to/css1', '/path/to/css2')}, "
-            "js=('/path/to/js1', 'http://media.other.com/path/to/js2', 'https://secure.other.com/path/to/js3'))"
+            "Media(css={'all': ['path/to/css1', '/path/to/css2']}, "
+            "js=['/path/to/js1', 'http://media.other.com/path/to/js2', 'https://secure.other.com/path/to/js3'])"
         )
 
         class Foo:
@@ -125,8 +125,8 @@ class Media:
 <link href="/path/to/css3" type="text/css" media="all" rel="stylesheet">
 <script type="text/javascript" src="/path/to/js1"></script>
 <script type="text/javascript" src="http://media.other.com/path/to/js2"></script>
-<script type="text/javascript" src="https://secure.other.com/path/to/js3"></script>
-<script type="text/javascript" src="/path/to/js4"></script>"""
+<script type="text/javascript" src="/path/to/js4"></script>
+<script type="text/javascript" src="https://secure.other.com/path/to/js3"></script>"""
         )
 
         # media addition hasn't affected the original objects
@@ -151,6 +151,17 @@ class Media:
         self.assertEqual(str(w4.media), """<link href="/path/to/css1" type="text/css" media="all" rel="stylesheet">
 <script type="text/javascript" src="/path/to/js1"></script>""")
 
+    def test_media_deduplication(self):
+        # A deduplication test applied directly to a Media object, to confirm
+        # that the deduplication doesn't only happen at the point of merging
+        # two or more media objects.
+        media = Media(
+            css={'all': ('/path/to/css1', '/path/to/css1')},
+            js=('/path/to/js1', '/path/to/js1'),
+        )
+        self.assertEqual(str(media), """<link href="/path/to/css1" type="text/css" media="all" rel="stylesheet">
+<script type="text/javascript" src="/path/to/js1"></script>""")
+
     def test_media_property(self):
         ###############################################################
         # Property-based media definitions
@@ -197,12 +208,12 @@ def _media(self):
         self.assertEqual(
             str(w6.media),
             """<link href="http://media.example.com/static/path/to/css1" type="text/css" media="all" rel="stylesheet">
-<link href="/path/to/css2" type="text/css" media="all" rel="stylesheet">
 <link href="/other/path" type="text/css" media="all" rel="stylesheet">
+<link href="/path/to/css2" type="text/css" media="all" rel="stylesheet">
 <script type="text/javascript" src="/path/to/js1"></script>
+<script type="text/javascript" src="/other/js"></script>
 <script type="text/javascript" src="http://media.other.com/path/to/js2"></script>
-<script type="text/javascript" src="https://secure.other.com/path/to/js3"></script>
-<script type="text/javascript" src="/other/js"></script>"""
+<script type="text/javascript" src="https://secure.other.com/path/to/js3"></script>"""
         )
 
     def test_media_inheritance(self):
@@ -247,8 +258,8 @@ class Media:
 <link href="/path/to/css2" type="text/css" media="all" rel="stylesheet">
 <script type="text/javascript" src="/path/to/js1"></script>
 <script type="text/javascript" src="http://media.other.com/path/to/js2"></script>
-<script type="text/javascript" src="https://secure.other.com/path/to/js3"></script>
-<script type="text/javascript" src="/path/to/js4"></script>"""
+<script type="text/javascript" src="/path/to/js4"></script>
+<script type="text/javascript" src="https://secure.other.com/path/to/js3"></script>"""
         )
 
     def test_media_inheritance_from_property(self):
@@ -322,8 +333,8 @@ class Media:
 <link href="/path/to/css2" type="text/css" media="all" rel="stylesheet">
 <script type="text/javascript" src="/path/to/js1"></script>
 <script type="text/javascript" src="http://media.other.com/path/to/js2"></script>
-<script type="text/javascript" src="https://secure.other.com/path/to/js3"></script>
-<script type="text/javascript" src="/path/to/js4"></script>"""
+<script type="text/javascript" src="/path/to/js4"></script>
+<script type="text/javascript" src="https://secure.other.com/path/to/js3"></script>"""
         )
 
     def test_media_inheritance_single_type(self):
@@ -420,8 +431,8 @@ def __init__(self, attrs=None):
 <link href="/path/to/css3" type="text/css" media="all" rel="stylesheet">
 <script type="text/javascript" src="/path/to/js1"></script>
 <script type="text/javascript" src="http://media.other.com/path/to/js2"></script>
-<script type="text/javascript" src="https://secure.other.com/path/to/js3"></script>
-<script type="text/javascript" src="/path/to/js4"></script>"""
+<script type="text/javascript" src="/path/to/js4"></script>
+<script type="text/javascript" src="https://secure.other.com/path/to/js3"></script>"""
         )
 
     def test_form_media(self):
@@ -462,8 +473,8 @@ class MyForm(Form):
 <link href="/path/to/css3" type="text/css" media="all" rel="stylesheet">
 <script type="text/javascript" src="/path/to/js1"></script>
 <script type="text/javascript" src="http://media.other.com/path/to/js2"></script>
-<script type="text/javascript" src="https://secure.other.com/path/to/js3"></script>
-<script type="text/javascript" src="/path/to/js4"></script>"""
+<script type="text/javascript" src="/path/to/js4"></script>
+<script type="text/javascript" src="https://secure.other.com/path/to/js3"></script>"""
         )
 
         # Form media can be combined to produce a single media definition.
@@ -477,8 +488,8 @@ class AnotherForm(Form):
 <link href="/path/to/css3" type="text/css" media="all" rel="stylesheet">
 <script type="text/javascript" src="/path/to/js1"></script>
 <script type="text/javascript" src="http://media.other.com/path/to/js2"></script>
-<script type="text/javascript" src="https://secure.other.com/path/to/js3"></script>
-<script type="text/javascript" src="/path/to/js4"></script>"""
+<script type="text/javascript" src="/path/to/js4"></script>
+<script type="text/javascript" src="https://secure.other.com/path/to/js3"></script>"""
         )
 
         # Forms can also define media, following the same rules as widgets.
@@ -495,28 +506,28 @@ class Media:
         self.assertEqual(
             str(f3.media),
             """<link href="http://media.example.com/static/path/to/css1" type="text/css" media="all" rel="stylesheet">
+<link href="/some/form/css" type="text/css" media="all" rel="stylesheet">
 <link href="/path/to/css2" type="text/css" media="all" rel="stylesheet">
 <link href="/path/to/css3" type="text/css" media="all" rel="stylesheet">
-<link href="/some/form/css" type="text/css" media="all" rel="stylesheet">
 <script type="text/javascript" src="/path/to/js1"></script>
+<script type="text/javascript" src="/some/form/javascript"></script>
 <script type="text/javascript" src="http://media.other.com/path/to/js2"></script>
-<script type="text/javascript" src="https://secure.other.com/path/to/js3"></script>
 <script type="text/javascript" src="/path/to/js4"></script>
-<script type="text/javascript" src="/some/form/javascript"></script>"""
+<script type="text/javascript" src="https://secure.other.com/path/to/js3"></script>"""
         )
 
         # Media works in templates
         self.assertEqual(
             Template("{{ form.media.js }}{{ form.media.css }}").render(Context({'form': f3})),
             """<script type="text/javascript" src="/path/to/js1"></script>
+<script type="text/javascript" src="/some/form/javascript"></script>
 <script type="text/javascript" src="http://media.other.com/path/to/js2"></script>
-<script type="text/javascript" src="https://secure.other.com/path/to/js3"></script>
 <script type="text/javascript" src="/path/to/js4"></script>
-<script type="text/javascript" src="/some/form/javascript"></script>"""
+<script type="text/javascript" src="https://secure.other.com/path/to/js3"></script>"""
             """<link href="http://media.example.com/static/path/to/css1" type="text/css" media="all" rel="stylesheet">
+<link href="/some/form/css" type="text/css" media="all" rel="stylesheet">
 <link href="/path/to/css2" type="text/css" media="all" rel="stylesheet">
-<link href="/path/to/css3" type="text/css" media="all" rel="stylesheet">
-<link href="/some/form/css" type="text/css" media="all" rel="stylesheet">"""
+<link href="/path/to/css3" type="text/css" media="all" rel="stylesheet">"""
         )
 
     def test_html_safe(self):
@@ -526,19 +537,23 @@ def test_html_safe(self):
 
     def test_merge(self):
         test_values = (
-            (([1, 2], [3, 4]), [1, 2, 3, 4]),
+            (([1, 2], [3, 4]), [1, 3, 2, 4]),
             (([1, 2], [2, 3]), [1, 2, 3]),
             (([2, 3], [1, 2]), [1, 2, 3]),
             (([1, 3], [2, 3]), [1, 2, 3]),
             (([1, 2], [1, 3]), [1, 2, 3]),
             (([1, 2], [3, 2]), [1, 3, 2]),
+            (([1, 2], [1, 2]), [1, 2]),
+            ([[1, 2], [1, 3], [2, 3], [5, 7], [5, 6], [6, 7, 9], [8, 9]], [1, 5, 8, 2, 6, 3, 7, 9]),
+            ((), []),
+            (([1, 2],), [1, 2]),
         )
-        for (list1, list2), expected in test_values:
-            with self.subTest(list1=list1, list2=list2):
-                self.assertEqual(Media.merge(list1, list2), expected)
+        for lists, expected in test_values:
+            with self.subTest(lists=lists):
+                self.assertEqual(Media.merge(*lists), expected)
 
     def test_merge_warning(self):
-        msg = 'Detected duplicate Media files in an opposite order:\n1\n2'
+        msg = 'Detected duplicate Media files in an opposite order: [1, 2], [2, 1]'
         with self.assertWarnsMessage(RuntimeWarning, msg):
             self.assertEqual(Media.merge([1, 2], [2, 1]), [1, 2])
 
@@ -546,28 +561,30 @@ def test_merge_js_three_way(self):
         """
         The relative order of scripts is preserved in a three-way merge.
         """
-        # custom_widget.js doesn't depend on jquery.js.
-        widget1 = Media(js=['custom_widget.js'])
-        widget2 = Media(js=['jquery.js', 'uses_jquery.js'])
-        form_media = widget1 + widget2
-        # The relative ordering of custom_widget.js and jquery.js has been
-        # established (but without a real need to).
-        self.assertEqual(form_media._js, ['custom_widget.js', 'jquery.js', 'uses_jquery.js'])
-        # The inline also uses custom_widget.js. This time, it's at the end.
-        inline_media = Media(js=['jquery.js', 'also_jquery.js']) + Media(js=['custom_widget.js'])
-        merged = form_media + inline_media
-        self.assertEqual(merged._js, ['custom_widget.js', 'jquery.js', 'uses_jquery.js', 'also_jquery.js'])
+        widget1 = Media(js=['color-picker.js'])
+        widget2 = Media(js=['text-editor.js'])
+        widget3 = Media(js=['text-editor.js', 'text-editor-extras.js', 'color-picker.js'])
+        merged = widget1 + widget2 + widget3
+        self.assertEqual(merged._js, ['text-editor.js', 'text-editor-extras.js', 'color-picker.js'])
+
+    def test_merge_js_three_way2(self):
+        # The merge prefers to place 'c' before 'b' and 'g' before 'h' to
+        # preserve the original order. The preference 'c'->'b' is overridden by
+        # widget3's media, but 'g'->'h' survives in the final ordering.
+        widget1 = Media(js=['a', 'c', 'f', 'g', 'k'])
+        widget2 = Media(js=['a', 'b', 'f', 'h', 'k'])
+        widget3 = Media(js=['b', 'c', 'f', 'k'])
+        merged = widget1 + widget2 + widget3
+        self.assertEqual(merged._js, ['a', 'b', 'c', 'f', 'g', 'h', 'k'])
 
     def test_merge_css_three_way(self):
-        widget1 = Media(css={'screen': ['a.css']})
-        widget2 = Media(css={'screen': ['b.css']})
-        widget3 = Media(css={'all': ['c.css']})
-        form1 = widget1 + widget2
-        form2 = widget2 + widget1
-        # form1 and form2 have a.css and b.css in different order...
-        self.assertEqual(form1._css, {'screen': ['a.css', 'b.css']})
-        self.assertEqual(form2._css, {'screen': ['b.css', 'a.css']})
-        # ...but merging succeeds as the relative ordering of a.css and b.css
-        # was never specified.
-        merged = widget3 + form1 + form2
-        self.assertEqual(merged._css, {'screen': ['a.css', 'b.css'], 'all': ['c.css']})
+        widget1 = Media(css={'screen': ['c.css'], 'all': ['d.css', 'e.css']})
+        widget2 = Media(css={'screen': ['a.css']})
+        widget3 = Media(css={'screen': ['a.css', 'b.css', 'c.css'], 'all': ['e.css']})
+        merged = widget1 + widget2
+        # c.css comes before a.css because widget1 + widget2 establishes this
+        # order.
+        self.assertEqual(merged._css, {'screen': ['c.css', 'a.css'], 'all': ['d.css', 'e.css']})
+        merged = merged + widget3
+        # widget3 contains an explicit ordering of c.css and a.css.
+        self.assertEqual(merged._css, {'screen': ['a.css', 'b.css', 'c.css'], 'all': ['d.css', 'e.css']})

```

## Test Information

**Tests that should FAIL→PASS**: ["test_combine_media (forms_tests.tests.test_media.FormsMediaTestCase)", "test_construction (forms_tests.tests.test_media.FormsMediaTestCase)", "test_form_media (forms_tests.tests.test_media.FormsMediaTestCase)", "test_media_deduplication (forms_tests.tests.test_media.FormsMediaTestCase)", "test_media_inheritance (forms_tests.tests.test_media.FormsMediaTestCase)", "test_media_inheritance_extends (forms_tests.tests.test_media.FormsMediaTestCase)", "test_media_property_parent_references (forms_tests.tests.test_media.FormsMediaTestCase)", "test_merge (forms_tests.tests.test_media.FormsMediaTestCase)", "test_merge_css_three_way (forms_tests.tests.test_media.FormsMediaTestCase)", "test_merge_js_three_way (forms_tests.tests.test_media.FormsMediaTestCase)", "test_merge_js_three_way2 (forms_tests.tests.test_media.FormsMediaTestCase)", "test_merge_warning (forms_tests.tests.test_media.FormsMediaTestCase)", "test_multi_widget (forms_tests.tests.test_media.FormsMediaTestCase)", "test_media (admin_widgets.test_autocomplete_widget.AutocompleteMixinTests)", "test_render_options (admin_widgets.test_autocomplete_widget.AutocompleteMixinTests)", "test_inline_media_only_inline (admin_inlines.tests.TestInlineMedia)"]

**Tests that should PASS→PASS**: ["Regression for #9362", "test_html_safe (forms_tests.tests.test_media.FormsMediaTestCase)", "test_media_dsl (forms_tests.tests.test_media.FormsMediaTestCase)", "test_media_inheritance_from_property (forms_tests.tests.test_media.FormsMediaTestCase)", "test_media_inheritance_single_type (forms_tests.tests.test_media.FormsMediaTestCase)", "test_media_property (forms_tests.tests.test_media.FormsMediaTestCase)", "test_multi_media (forms_tests.tests.test_media.FormsMediaTestCase)", "test_build_attrs (admin_widgets.test_autocomplete_widget.AutocompleteMixinTests)", "test_build_attrs_no_custom_class (admin_widgets.test_autocomplete_widget.AutocompleteMixinTests)", "test_build_attrs_not_required_field (admin_widgets.test_autocomplete_widget.AutocompleteMixinTests)", "test_build_attrs_required_field (admin_widgets.test_autocomplete_widget.AutocompleteMixinTests)", "test_get_url (admin_widgets.test_autocomplete_widget.AutocompleteMixinTests)", "Empty option isn't present if the field isn't required.", "Empty option is present if the field isn't required.", "test_deleting_inline_with_protected_delete_does_not_validate (admin_inlines.tests.TestInlineProtectedOnDelete)", "test_all_inline_media (admin_inlines.tests.TestInlineMedia)", "test_inline_media_only_base (admin_inlines.tests.TestInlineMedia)", "test_inline_add_fk_add_perm (admin_inlines.tests.TestInlinePermissions)", "test_inline_add_fk_noperm (admin_inlines.tests.TestInlinePermissions)", "test_inline_add_m2m_add_perm (admin_inlines.tests.TestInlinePermissions)", "test_inline_add_m2m_noperm (admin_inlines.tests.TestInlinePermissions)", "test_inline_change_fk_add_change_perm (admin_inlines.tests.TestInlinePermissions)", "test_inline_change_fk_add_perm (admin_inlines.tests.TestInlinePermissions)", "test_inline_change_fk_all_perms (admin_inlines.tests.TestInlinePermissions)", "test_inline_change_fk_change_del_perm (admin_inlines.tests.TestInlinePermissions)", "test_inline_change_fk_change_perm (admin_inlines.tests.TestInlinePermissions)", "test_inline_change_fk_noperm (admin_inlines.tests.TestInlinePermissions)", "test_inline_change_m2m_add_perm (admin_inlines.tests.TestInlinePermissions)", "test_inline_change_m2m_change_perm (admin_inlines.tests.TestInlinePermissions)", "test_inline_change_m2m_noperm (admin_inlines.tests.TestInlinePermissions)", "Admin inline should invoke local callable when its name is listed in readonly_fields", "test_can_delete (admin_inlines.tests.TestInline)", "test_create_inlines_on_inherited_model (admin_inlines.tests.TestInline)", "test_custom_form_tabular_inline_label (admin_inlines.tests.TestInline)", "test_custom_form_tabular_inline_overridden_label (admin_inlines.tests.TestInline)", "test_custom_get_extra_form (admin_inlines.tests.TestInline)", "test_custom_min_num (admin_inlines.tests.TestInline)", "test_custom_pk_shortcut (admin_inlines.tests.TestInline)", "test_help_text (admin_inlines.tests.TestInline)", "test_inline_editable_pk (admin_inlines.tests.TestInline)", "#18263 -- Make sure hidden fields don't get a column in tabular inlines", "test_inline_nonauto_noneditable_inherited_pk (admin_inlines.tests.TestInline)", "test_inline_nonauto_noneditable_pk (admin_inlines.tests.TestInline)", "test_inline_primary (admin_inlines.tests.TestInline)", "Inlines `show_change_link` for registered models when enabled.", "Inlines `show_change_link` disabled for unregistered models.", "test_localize_pk_shortcut (admin_inlines.tests.TestInline)", "Autogenerated many-to-many inlines are displayed correctly (#13407)", "test_min_num (admin_inlines.tests.TestInline)", "Admin inline `readonly_field` shouldn't invoke parent ModelAdmin callable", "test_non_related_name_inline (admin_inlines.tests.TestInline)", "Inlines without change permission shows field inputs on add form.", "Bug #13174.", "test_stacked_inline_edit_form_contains_has_original_class (admin_inlines.tests.TestInline)", "test_tabular_inline_column_css_class (admin_inlines.tests.TestInline)", "Inlines `show_change_link` disabled by default.", "test_tabular_model_form_meta_readonly_field (admin_inlines.tests.TestInline)", "test_tabular_non_field_errors (admin_inlines.tests.TestInline)"]

**Base Commit**: 93e892bb645b16ebaf287beb5fe7f3ffe8d10408
**Environment Setup Commit**: 419a78300f7cd27611196e1e464d50fd0385ff27
