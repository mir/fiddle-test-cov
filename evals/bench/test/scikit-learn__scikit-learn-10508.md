# scikit-learn__scikit-learn-10508

**Repository**: scikit-learn/scikit-learn
**Created**: 2018-01-19T18:00:29Z
**Version**: 0.20

## Problem Statement

LabelEncoder transform fails for empty lists (for certain inputs)
Python 3.6.3, scikit_learn 0.19.1

Depending on which datatypes were used to fit the LabelEncoder, transforming empty lists works or not. Expected behavior would be that empty arrays are returned in both cases.

```python
>>> from sklearn.preprocessing import LabelEncoder
>>> le = LabelEncoder()
>>> le.fit([1,2])
LabelEncoder()
>>> le.transform([])
array([], dtype=int64)
>>> le.fit(["a","b"])
LabelEncoder()
>>> le.transform([])
Traceback (most recent call last):
  File "[...]\Python36\lib\site-packages\numpy\core\fromnumeric.py", line 57, in _wrapfunc
    return getattr(obj, method)(*args, **kwds)
TypeError: Cannot cast array data from dtype('float64') to dtype('<U32') according to the rule 'safe'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "[...]\Python36\lib\site-packages\sklearn\preprocessing\label.py", line 134, in transform
    return np.searchsorted(self.classes_, y)
  File "[...]\Python36\lib\site-packages\numpy\core\fromnumeric.py", line 1075, in searchsorted
    return _wrapfunc(a, 'searchsorted', v, side=side, sorter=sorter)
  File "[...]\Python36\lib\site-packages\numpy\core\fromnumeric.py", line 67, in _wrapfunc
    return _wrapit(obj, method, *args, **kwds)
  File "[...]\Python36\lib\site-packages\numpy\core\fromnumeric.py", line 47, in _wrapit
    result = getattr(asarray(obj), method)(*args, **kwds)
TypeError: Cannot cast array data from dtype('float64') to dtype('<U32') according to the rule 'safe'
```


## Hints

`le.transform([])` will trigger an numpy array of `dtype=np.float64` and you fit something which was some string.

```python
from sklearn.preprocessing import LabelEncoder                                       
import numpy as np                                                                   
                                                                                     
le = LabelEncoder()                                                                  
X = np.array(["a", "b"])                                                             
le.fit(X)                                                                            
X_trans = le.transform(np.array([], dtype=X.dtype))
X_trans
array([], dtype=int64)
```
I would like to take it up. 
Hey @maykulkarni go ahead with PR. Sorry, please don't mind my referenced commit, I don't intend to send in a PR.

I would be happy to have a look over your PR once you send in (not that my review would matter much) :)

## Patch

```diff

diff --git a/sklearn/preprocessing/label.py b/sklearn/preprocessing/label.py
--- a/sklearn/preprocessing/label.py
+++ b/sklearn/preprocessing/label.py
@@ -126,6 +126,9 @@ def transform(self, y):
         """
         check_is_fitted(self, 'classes_')
         y = column_or_1d(y, warn=True)
+        # transform of empty array is empty array
+        if _num_samples(y) == 0:
+            return np.array([])
 
         classes = np.unique(y)
         if len(np.intersect1d(classes, self.classes_)) < len(classes):
@@ -147,6 +150,10 @@ def inverse_transform(self, y):
         y : numpy array of shape [n_samples]
         """
         check_is_fitted(self, 'classes_')
+        y = column_or_1d(y, warn=True)
+        # inverse transform of empty array is empty array
+        if _num_samples(y) == 0:
+            return np.array([])
 
         diff = np.setdiff1d(y, np.arange(len(self.classes_)))
         if len(diff):


```

## Test Patch

```diff
diff --git a/sklearn/preprocessing/tests/test_label.py b/sklearn/preprocessing/tests/test_label.py
--- a/sklearn/preprocessing/tests/test_label.py
+++ b/sklearn/preprocessing/tests/test_label.py
@@ -208,6 +208,21 @@ def test_label_encoder_errors():
     assert_raise_message(ValueError, msg, le.inverse_transform, [-2])
     assert_raise_message(ValueError, msg, le.inverse_transform, [-2, -3, -4])
 
+    # Fail on inverse_transform("")
+    msg = "bad input shape ()"
+    assert_raise_message(ValueError, msg, le.inverse_transform, "")
+
+
+def test_label_encoder_empty_array():
+    le = LabelEncoder()
+    le.fit(np.array(["1", "2", "1", "2", "2"]))
+    # test empty transform
+    transformed = le.transform([])
+    assert_array_equal(np.array([]), transformed)
+    # test empty inverse transform
+    inverse_transformed = le.inverse_transform([])
+    assert_array_equal(np.array([]), inverse_transformed)
+
 
 def test_sparse_output_multilabel_binarizer():
     # test input as iterable of iterables

```

## Test Information

**Tests that should FAIL→PASS**: ["sklearn/preprocessing/tests/test_label.py::test_label_encoder_errors", "sklearn/preprocessing/tests/test_label.py::test_label_encoder_empty_array"]

**Tests that should PASS→PASS**: ["sklearn/preprocessing/tests/test_label.py::test_label_binarizer", "sklearn/preprocessing/tests/test_label.py::test_label_binarizer_unseen_labels", "sklearn/preprocessing/tests/test_label.py::test_label_binarizer_set_label_encoding", "sklearn/preprocessing/tests/test_label.py::test_label_binarizer_errors", "sklearn/preprocessing/tests/test_label.py::test_label_encoder", "sklearn/preprocessing/tests/test_label.py::test_label_encoder_fit_transform", "sklearn/preprocessing/tests/test_label.py::test_sparse_output_multilabel_binarizer", "sklearn/preprocessing/tests/test_label.py::test_multilabel_binarizer", "sklearn/preprocessing/tests/test_label.py::test_multilabel_binarizer_empty_sample", "sklearn/preprocessing/tests/test_label.py::test_multilabel_binarizer_unknown_class", "sklearn/preprocessing/tests/test_label.py::test_multilabel_binarizer_given_classes", "sklearn/preprocessing/tests/test_label.py::test_multilabel_binarizer_same_length_sequence", "sklearn/preprocessing/tests/test_label.py::test_multilabel_binarizer_non_integer_labels", "sklearn/preprocessing/tests/test_label.py::test_multilabel_binarizer_non_unique", "sklearn/preprocessing/tests/test_label.py::test_multilabel_binarizer_inverse_validation", "sklearn/preprocessing/tests/test_label.py::test_label_binarize_with_class_order", "sklearn/preprocessing/tests/test_label.py::test_invalid_input_label_binarize", "sklearn/preprocessing/tests/test_label.py::test_inverse_binarize_multiclass"]

**Base Commit**: c753b77ac49e72ebc0fe5e3c2369fe628f975017
**Environment Setup Commit**: 55bf5d93e5674f13a1134d93a11fd0cd11aabcd1
