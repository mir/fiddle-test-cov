# django__django-13230

**Repository**: django/django
**Created**: 2020-07-23T14:59:50Z
**Version**: 3.2

## Problem Statement

Add support for item_comments to syndication framework
Description
	
Add comments argument to feed.add_item() in syndication.views so that item_comments can be defined directly without having to take the detour via item_extra_kwargs .
Additionally, comments is already explicitly mentioned in the feedparser, but not implemented in the view.


## Patch

```diff

diff --git a/django/contrib/syndication/views.py b/django/contrib/syndication/views.py
--- a/django/contrib/syndication/views.py
+++ b/django/contrib/syndication/views.py
@@ -212,6 +212,7 @@ def get_feed(self, obj, request):
                 author_name=author_name,
                 author_email=author_email,
                 author_link=author_link,
+                comments=self._get_dynamic_attr('item_comments', item),
                 categories=self._get_dynamic_attr('item_categories', item),
                 item_copyright=self._get_dynamic_attr('item_copyright', item),
                 **self.item_extra_kwargs(item)


```

## Test Patch

```diff
diff --git a/tests/syndication_tests/feeds.py b/tests/syndication_tests/feeds.py
--- a/tests/syndication_tests/feeds.py
+++ b/tests/syndication_tests/feeds.py
@@ -29,6 +29,9 @@ def item_pubdate(self, item):
     def item_updateddate(self, item):
         return item.updated
 
+    def item_comments(self, item):
+        return "%scomments" % item.get_absolute_url()
+
     item_author_name = 'Sally Smith'
     item_author_email = 'test@example.com'
     item_author_link = 'http://www.example.com/'
diff --git a/tests/syndication_tests/tests.py b/tests/syndication_tests/tests.py
--- a/tests/syndication_tests/tests.py
+++ b/tests/syndication_tests/tests.py
@@ -136,10 +136,20 @@ def test_rss2_feed(self):
             'guid': 'http://example.com/blog/1/',
             'pubDate': pub_date,
             'author': 'test@example.com (Sally Smith)',
+            'comments': '/blog/1/comments',
         })
         self.assertCategories(items[0], ['python', 'testing'])
         for item in items:
-            self.assertChildNodes(item, ['title', 'link', 'description', 'guid', 'category', 'pubDate', 'author'])
+            self.assertChildNodes(item, [
+                'title',
+                'link',
+                'description',
+                'guid',
+                'category',
+                'pubDate',
+                'author',
+                'comments',
+            ])
             # Assert that <guid> does not have any 'isPermaLink' attribute
             self.assertIsNone(item.getElementsByTagName(
                 'guid')[0].attributes.get('isPermaLink'))

```

## Test Information

**Tests that should FAIL→PASS**: ["test_rss2_feed (syndication_tests.tests.SyndicationFeedTest)"]

**Tests that should PASS→PASS**: ["test_add_domain (syndication_tests.tests.SyndicationFeedTest)", "test_atom_feed (syndication_tests.tests.SyndicationFeedTest)", "test_atom_feed_published_and_updated_elements (syndication_tests.tests.SyndicationFeedTest)", "test_atom_multiple_enclosures (syndication_tests.tests.SyndicationFeedTest)", "test_atom_single_enclosure (syndication_tests.tests.SyndicationFeedTest)", "test_aware_datetime_conversion (syndication_tests.tests.SyndicationFeedTest)", "test_custom_feed_generator (syndication_tests.tests.SyndicationFeedTest)", "test_feed_generator_language_attribute (syndication_tests.tests.SyndicationFeedTest)", "test_feed_last_modified_time (syndication_tests.tests.SyndicationFeedTest)", "test_feed_last_modified_time_naive_date (syndication_tests.tests.SyndicationFeedTest)", "test_feed_url (syndication_tests.tests.SyndicationFeedTest)", "test_item_link_error (syndication_tests.tests.SyndicationFeedTest)", "test_latest_post_date (syndication_tests.tests.SyndicationFeedTest)", "test_naive_datetime_conversion (syndication_tests.tests.SyndicationFeedTest)", "test_rss091_feed (syndication_tests.tests.SyndicationFeedTest)", "test_rss2_feed_guid_permalink_false (syndication_tests.tests.SyndicationFeedTest)", "test_rss2_feed_guid_permalink_true (syndication_tests.tests.SyndicationFeedTest)", "test_rss2_multiple_enclosures (syndication_tests.tests.SyndicationFeedTest)", "test_rss2_single_enclosure (syndication_tests.tests.SyndicationFeedTest)", "test_secure_urls (syndication_tests.tests.SyndicationFeedTest)", "test_template_context_feed (syndication_tests.tests.SyndicationFeedTest)", "test_template_feed (syndication_tests.tests.SyndicationFeedTest)", "test_title_escaping (syndication_tests.tests.SyndicationFeedTest)"]

**Base Commit**: 184a6eebb0ef56d5f1b1315a8e666830e37f3f81
**Environment Setup Commit**: 65dfb06a1ab56c238cc80f5e1c31f61210c4577d
