# scikit-learn__scikit-learn-25570

**Repository**: scikit-learn/scikit-learn
**Created**: 2023-02-08T18:28:21Z
**Version**: 1.3

## Problem Statement

ColumnTransformer with pandas output can't handle transformers with no features
### Describe the bug

Hi,

ColumnTransformer doesn't deal well with transformers that apply to 0 features (categorical_features in the example below) when using "pandas" as output. It seems steps with 0 features are not fitted, hence don't appear in `self._iter(fitted=True)` (_column_transformer.py l.856) and hence break the input to the `_add_prefix_for_feature_names_out` function (l.859).


### Steps/Code to Reproduce

Here is some code to reproduce the error. If you remove .set_output(transform="pandas") on the line before last, all works fine. If you remove the ("categorical", ...) step, it works fine too.

```python
import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

X = pd.DataFrame(data=[[1.0, 2.0, 3.0, 4.0], [4, 2, 2, 5]],
                 columns=["a", "b", "c", "d"])
y = np.array([0, 1])
categorical_features = []
numerical_features = ["a", "b", "c"]
model_preprocessing = ("preprocessing",
                       ColumnTransformer([
                           ('categorical', 'passthrough', categorical_features),
                           ('numerical', Pipeline([("scaler", RobustScaler()),
                                                   ("imputer", SimpleImputer(strategy="median"))
                                                   ]), numerical_features),
                       ], remainder='drop'))
pipeline = Pipeline([model_preprocessing, ("classifier", LGBMClassifier())]).set_output(transform="pandas")
pipeline.fit(X, y)
```

### Expected Results

The step with no features should be ignored.

### Actual Results

Here is the error message:
```pytb
Traceback (most recent call last):
  File "/home/philippe/workspace/script.py", line 22, in <module>
    pipeline.fit(X, y)
  File "/home/philippe/.anaconda3/envs/deleteme/lib/python3.9/site-packages/sklearn/pipeline.py", line 402, in fit
    Xt = self._fit(X, y, **fit_params_steps)
  File "/home/philippe/.anaconda3/envs/deleteme/lib/python3.9/site-packages/sklearn/pipeline.py", line 360, in _fit
    X, fitted_transformer = fit_transform_one_cached(
  File "/home/philippe/.anaconda3/envs/deleteme/lib/python3.9/site-packages/joblib/memory.py", line 349, in __call__
    return self.func(*args, **kwargs)
  File "/home/philippe/.anaconda3/envs/deleteme/lib/python3.9/site-packages/sklearn/pipeline.py", line 894, in _fit_transform_one
    res = transformer.fit_transform(X, y, **fit_params)
  File "/home/philippe/.anaconda3/envs/deleteme/lib/python3.9/site-packages/sklearn/utils/_set_output.py", line 142, in wrapped
    data_to_wrap = f(self, X, *args, **kwargs)
  File "/home/philippe/.anaconda3/envs/deleteme/lib/python3.9/site-packages/sklearn/compose/_column_transformer.py", line 750, in fit_transform
    return self._hstack(list(Xs))
  File "/home/philippe/.anaconda3/envs/deleteme/lib/python3.9/site-packages/sklearn/compose/_column_transformer.py", line 862, in _hstack
    output.columns = names_out
  File "/home/philippe/.anaconda3/envs/deleteme/lib/python3.9/site-packages/pandas/core/generic.py", line 5596, in __setattr__
    return object.__setattr__(self, name, value)
  File "pandas/_libs/properties.pyx", line 70, in pandas._libs.properties.AxisProperty.__set__
  File "/home/philippe/.anaconda3/envs/deleteme/lib/python3.9/site-packages/pandas/core/generic.py", line 769, in _set_axis
    self._mgr.set_axis(axis, labels)
  File "/home/philippe/.anaconda3/envs/deleteme/lib/python3.9/site-packages/pandas/core/internals/managers.py", line 214, in set_axis
    self._validate_set_axis(axis, new_labels)
  File "/home/philippe/.anaconda3/envs/deleteme/lib/python3.9/site-packages/pandas/core/internals/base.py", line 69, in _validate_set_axis
    raise ValueError(
ValueError: Length mismatch: Expected axis has 3 elements, new values have 0 elements

Process finished with exit code 1
```

### Versions

```shell
System:
    python: 3.9.15 (main, Nov 24 2022, 14:31:59)  [GCC 11.2.0]
executable: /home/philippe/.anaconda3/envs/strategy-training/bin/python
   machine: Linux-5.15.0-57-generic-x86_64-with-glibc2.31

Python dependencies:
      sklearn: 1.2.0
          pip: 22.2.2
   setuptools: 62.3.2
        numpy: 1.23.5
        scipy: 1.9.3
       Cython: None
       pandas: 1.4.1
   matplotlib: 3.6.3
       joblib: 1.2.0
threadpoolctl: 3.1.0

Built with OpenMP: True

threadpoolctl info:
       user_api: openmp
   internal_api: openmp
         prefix: libgomp
       filepath: /home/philippe/.anaconda3/envs/strategy-training/lib/python3.9/site-packages/scikit_learn.libs/libgomp-a34b3233.so.1.0.0
        version: None
    num_threads: 12

       user_api: blas
   internal_api: openblas
         prefix: libopenblas
       filepath: /home/philippe/.anaconda3/envs/strategy-training/lib/python3.9/site-packages/numpy.libs/libopenblas64_p-r0-742d56dc.3.20.so
        version: 0.3.20
threading_layer: pthreads
   architecture: Haswell
    num_threads: 12

       user_api: blas
   internal_api: openblas
         prefix: libopenblas
       filepath: /home/philippe/.anaconda3/envs/strategy-training/lib/python3.9/site-packages/scipy.libs/libopenblasp-r0-41284840.3.18.so
        version: 0.3.18
threading_layer: pthreads
   architecture: Haswell
    num_threads: 12
```



## Patch

```diff

diff --git a/sklearn/compose/_column_transformer.py b/sklearn/compose/_column_transformer.py
--- a/sklearn/compose/_column_transformer.py
+++ b/sklearn/compose/_column_transformer.py
@@ -865,7 +865,9 @@ def _hstack(self, Xs):
                 transformer_names = [
                     t[0] for t in self._iter(fitted=True, replace_strings=True)
                 ]
-                feature_names_outs = [X.columns for X in Xs]
+                # Selection of columns might be empty.
+                # Hence feature names are filtered for non-emptiness.
+                feature_names_outs = [X.columns for X in Xs if X.shape[1] != 0]
                 names_out = self._add_prefix_for_feature_names_out(
                     list(zip(transformer_names, feature_names_outs))
                 )


```

## Test Patch

```diff
diff --git a/sklearn/compose/tests/test_column_transformer.py b/sklearn/compose/tests/test_column_transformer.py
--- a/sklearn/compose/tests/test_column_transformer.py
+++ b/sklearn/compose/tests/test_column_transformer.py
@@ -2129,3 +2129,32 @@ def test_transformers_with_pandas_out_but_not_feature_names_out(
     ct.set_params(verbose_feature_names_out=False)
     X_trans_df1 = ct.fit_transform(X_df)
     assert_array_equal(X_trans_df1.columns, expected_non_verbose_names)
+
+
+@pytest.mark.parametrize(
+    "empty_selection",
+    [[], np.array([False, False]), [False, False]],
+    ids=["list", "bool", "bool_int"],
+)
+def test_empty_selection_pandas_output(empty_selection):
+    """Check that pandas output works when there is an empty selection.
+
+    Non-regression test for gh-25487
+    """
+    pd = pytest.importorskip("pandas")
+
+    X = pd.DataFrame([[1.0, 2.2], [3.0, 1.0]], columns=["a", "b"])
+    ct = ColumnTransformer(
+        [
+            ("categorical", "passthrough", empty_selection),
+            ("numerical", StandardScaler(), ["a", "b"]),
+        ],
+        verbose_feature_names_out=True,
+    )
+    ct.set_output(transform="pandas")
+    X_out = ct.fit_transform(X)
+    assert_array_equal(X_out.columns, ["numerical__a", "numerical__b"])
+
+    ct.set_params(verbose_feature_names_out=False)
+    X_out = ct.fit_transform(X)
+    assert_array_equal(X_out.columns, ["a", "b"])

```

## Test Information

**Tests that should FAIL→PASS**: ["sklearn/compose/tests/test_column_transformer.py::test_empty_selection_pandas_output[list]", "sklearn/compose/tests/test_column_transformer.py::test_empty_selection_pandas_output[bool]", "sklearn/compose/tests/test_column_transformer.py::test_empty_selection_pandas_output[bool_int]"]

**Tests that should PASS→PASS**: ["sklearn/compose/tests/test_column_transformer.py::test_column_transformer", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_tuple_transformers_parameter", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_dataframe", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_empty_columns[False-list-pandas]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_empty_columns[False-list-numpy]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_empty_columns[False-bool-pandas]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_empty_columns[False-bool-numpy]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_empty_columns[False-bool_int-pandas]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_empty_columns[False-bool_int-numpy]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_empty_columns[True-list-pandas]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_empty_columns[True-list-numpy]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_empty_columns[True-bool-pandas]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_empty_columns[True-bool-numpy]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_empty_columns[True-bool_int-pandas]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_empty_columns[True-bool_int-numpy]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_output_indices", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_output_indices_df", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_sparse_array", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_list", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_sparse_stacking", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_mixed_cols_sparse", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_sparse_threshold", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_error_msg_1D", "sklearn/compose/tests/test_column_transformer.py::test_2D_transformer_output", "sklearn/compose/tests/test_column_transformer.py::test_2D_transformer_output_pandas", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_invalid_columns[drop]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_invalid_columns[passthrough]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_invalid_transformer", "sklearn/compose/tests/test_column_transformer.py::test_make_column_transformer", "sklearn/compose/tests/test_column_transformer.py::test_make_column_transformer_pandas", "sklearn/compose/tests/test_column_transformer.py::test_make_column_transformer_kwargs", "sklearn/compose/tests/test_column_transformer.py::test_make_column_transformer_remainder_transformer", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_get_set_params", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_named_estimators", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_cloning", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_get_feature_names", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_special_strings", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_remainder", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_remainder_numpy[key0]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_remainder_numpy[key1]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_remainder_numpy[key2]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_remainder_numpy[key3]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_remainder_pandas[key0]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_remainder_pandas[key1]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_remainder_pandas[key2]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_remainder_pandas[key3]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_remainder_pandas[pd-index]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_remainder_pandas[key5]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_remainder_pandas[key6]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_remainder_pandas[key7]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_remainder_pandas[key8]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_remainder_transformer[key0]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_remainder_transformer[key1]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_remainder_transformer[key2]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_remainder_transformer[key3]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_no_remaining_remainder_transformer", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_drops_all_remainder_transformer", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_sparse_remainder_transformer", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_drop_all_sparse_remainder_transformer", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_get_set_params_with_remainder", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_no_estimators", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_verbose[fit-est0-\\\\[ColumnTransformer\\\\].*\\\\(1", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_verbose[fit-est1-\\\\[ColumnTransformer\\\\].*\\\\(1", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_verbose[fit-est2-\\\\[ColumnTransformer\\\\].*\\\\(1", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_verbose[fit-est3-\\\\[ColumnTransformer\\\\].*\\\\(1", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_verbose[fit-est4-\\\\[ColumnTransformer\\\\].*\\\\(1", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_verbose[fit-est5-\\\\[ColumnTransformer\\\\].*\\\\(1", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_verbose[fit-est6-\\\\[ColumnTransformer\\\\].*\\\\(1", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_verbose[fit_transform-est0-\\\\[ColumnTransformer\\\\].*\\\\(1", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_verbose[fit_transform-est1-\\\\[ColumnTransformer\\\\].*\\\\(1", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_verbose[fit_transform-est2-\\\\[ColumnTransformer\\\\].*\\\\(1", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_verbose[fit_transform-est3-\\\\[ColumnTransformer\\\\].*\\\\(1", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_verbose[fit_transform-est4-\\\\[ColumnTransformer\\\\].*\\\\(1", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_verbose[fit_transform-est5-\\\\[ColumnTransformer\\\\].*\\\\(1", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_verbose[fit_transform-est6-\\\\[ColumnTransformer\\\\].*\\\\(1", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_no_estimators_set_params", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_callable_specifier", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_callable_specifier_dataframe", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_negative_column_indexes", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_mask_indexing[asarray]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_mask_indexing[csr_matrix]", "sklearn/compose/tests/test_column_transformer.py::test_n_features_in", "sklearn/compose/tests/test_column_transformer.py::test_make_column_selector_with_select_dtypes[cols0-None-number-None]", "sklearn/compose/tests/test_column_transformer.py::test_make_column_selector_with_select_dtypes[cols1-None-None-object]", "sklearn/compose/tests/test_column_transformer.py::test_make_column_selector_with_select_dtypes[cols2-None-include2-None]", "sklearn/compose/tests/test_column_transformer.py::test_make_column_selector_with_select_dtypes[cols3-None-include3-None]", "sklearn/compose/tests/test_column_transformer.py::test_make_column_selector_with_select_dtypes[cols4-None-object-None]", "sklearn/compose/tests/test_column_transformer.py::test_make_column_selector_with_select_dtypes[cols5-None-float-None]", "sklearn/compose/tests/test_column_transformer.py::test_make_column_selector_with_select_dtypes[cols6-at$-include6-None]", "sklearn/compose/tests/test_column_transformer.py::test_make_column_selector_with_select_dtypes[cols7-None-include7-None]", "sklearn/compose/tests/test_column_transformer.py::test_make_column_selector_with_select_dtypes[cols8-^col_int-include8-None]", "sklearn/compose/tests/test_column_transformer.py::test_make_column_selector_with_select_dtypes[cols9-float|str-None-None]", "sklearn/compose/tests/test_column_transformer.py::test_make_column_selector_with_select_dtypes[cols10-^col_s-None-exclude10]", "sklearn/compose/tests/test_column_transformer.py::test_make_column_selector_with_select_dtypes[cols11-str$-float-None]", "sklearn/compose/tests/test_column_transformer.py::test_make_column_selector_with_select_dtypes[cols12-None-include12-None]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_with_make_column_selector", "sklearn/compose/tests/test_column_transformer.py::test_make_column_selector_error", "sklearn/compose/tests/test_column_transformer.py::test_make_column_selector_pickle", "sklearn/compose/tests/test_column_transformer.py::test_feature_names_empty_columns[list]", "sklearn/compose/tests/test_column_transformer.py::test_feature_names_empty_columns[array]", "sklearn/compose/tests/test_column_transformer.py::test_feature_names_empty_columns[callable]", "sklearn/compose/tests/test_column_transformer.py::test_feature_names_out_pandas[selector0]", "sklearn/compose/tests/test_column_transformer.py::test_feature_names_out_pandas[<lambda>0]", "sklearn/compose/tests/test_column_transformer.py::test_feature_names_out_pandas[selector2]", "sklearn/compose/tests/test_column_transformer.py::test_feature_names_out_pandas[<lambda>1]", "sklearn/compose/tests/test_column_transformer.py::test_feature_names_out_pandas[selector4]", "sklearn/compose/tests/test_column_transformer.py::test_feature_names_out_pandas[<lambda>2]", "sklearn/compose/tests/test_column_transformer.py::test_feature_names_out_non_pandas[selector0]", "sklearn/compose/tests/test_column_transformer.py::test_feature_names_out_non_pandas[<lambda>0]", "sklearn/compose/tests/test_column_transformer.py::test_feature_names_out_non_pandas[selector2]", "sklearn/compose/tests/test_column_transformer.py::test_feature_names_out_non_pandas[<lambda>1]", "sklearn/compose/tests/test_column_transformer.py::test_sk_visual_block_remainder[passthrough]", "sklearn/compose/tests/test_column_transformer.py::test_sk_visual_block_remainder[remainder1]", "sklearn/compose/tests/test_column_transformer.py::test_sk_visual_block_remainder_drop", "sklearn/compose/tests/test_column_transformer.py::test_sk_visual_block_remainder_fitted_pandas[passthrough]", "sklearn/compose/tests/test_column_transformer.py::test_sk_visual_block_remainder_fitted_pandas[remainder1]", "sklearn/compose/tests/test_column_transformer.py::test_sk_visual_block_remainder_fitted_numpy[passthrough]", "sklearn/compose/tests/test_column_transformer.py::test_sk_visual_block_remainder_fitted_numpy[remainder1]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_reordered_column_names_remainder[remainder0-first]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_reordered_column_names_remainder[remainder0-second]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_reordered_column_names_remainder[remainder0-0]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_reordered_column_names_remainder[remainder0-1]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_reordered_column_names_remainder[passthrough-first]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_reordered_column_names_remainder[passthrough-second]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_reordered_column_names_remainder[passthrough-0]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_reordered_column_names_remainder[passthrough-1]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_reordered_column_names_remainder[drop-first]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_reordered_column_names_remainder[drop-second]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_reordered_column_names_remainder[drop-0]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_reordered_column_names_remainder[drop-1]", "sklearn/compose/tests/test_column_transformer.py::test_feature_name_validation_missing_columns_drop_passthough", "sklearn/compose/tests/test_column_transformer.py::test_feature_names_in_", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_true[transformers0-passthrough-expected_names0]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_true[transformers1-drop-expected_names1]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_true[transformers2-passthrough-expected_names2]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_true[transformers3-passthrough-expected_names3]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_true[transformers4-drop-expected_names4]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_true[transformers5-passthrough-expected_names5]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_true[transformers6-drop-expected_names6]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_true[transformers7-drop-expected_names7]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_true[transformers8-passthrough-expected_names8]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_true[transformers9-passthrough-expected_names9]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_true[transformers10-drop-expected_names10]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_true[transformers11-passthrough-expected_names11]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_true[transformers12-passthrough-expected_names12]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_false[transformers0-passthrough-expected_names0]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_false[transformers1-drop-expected_names1]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_false[transformers2-passthrough-expected_names2]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_false[transformers3-passthrough-expected_names3]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_false[transformers4-drop-expected_names4]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_false[transformers5-passthrough-expected_names5]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_false[transformers6-drop-expected_names6]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_false[transformers7-passthrough-expected_names7]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_false[transformers8-passthrough-expected_names8]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_false[transformers9-drop-expected_names9]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_false[transformers10-passthrough-expected_names10]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_false[transformers11-passthrough-expected_names11]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_false[transformers12-drop-expected_names12]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_false[transformers13-drop-expected_names13]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_false_errors[transformers0-drop-['b']]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_false_errors[transformers1-drop-['c']]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_false_errors[transformers2-passthrough-['a']]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_false_errors[transformers3-passthrough-['a']]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_false_errors[transformers4-drop-['b',", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_false_errors[transformers5-passthrough-['a']]", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_false_errors[transformers6-passthrough-['a',", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_false_errors[transformers7-passthrough-['pca0',", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_false_errors[transformers8-passthrough-['a',", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_false_errors[transformers9-passthrough-['a',", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_false_errors[transformers10-passthrough-['a',", "sklearn/compose/tests/test_column_transformer.py::test_verbose_feature_names_out_false_errors[transformers11-passthrough-['a',", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_set_output[drop-True]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_set_output[drop-False]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_set_output[passthrough-True]", "sklearn/compose/tests/test_column_transformer.py::test_column_transformer_set_output[passthrough-False]", "sklearn/compose/tests/test_column_transformer.py::test_column_transform_set_output_mixed[True-drop]", "sklearn/compose/tests/test_column_transformer.py::test_column_transform_set_output_mixed[True-passthrough]", "sklearn/compose/tests/test_column_transformer.py::test_column_transform_set_output_mixed[False-drop]", "sklearn/compose/tests/test_column_transformer.py::test_column_transform_set_output_mixed[False-passthrough]", "sklearn/compose/tests/test_column_transformer.py::test_column_transform_set_output_after_fitting[drop]", "sklearn/compose/tests/test_column_transformer.py::test_column_transform_set_output_after_fitting[passthrough]", "sklearn/compose/tests/test_column_transformer.py::test_transformers_with_pandas_out_but_not_feature_names_out[trans_10-expected_verbose_names0-expected_non_verbose_names0]", "sklearn/compose/tests/test_column_transformer.py::test_transformers_with_pandas_out_but_not_feature_names_out[drop-expected_verbose_names1-expected_non_verbose_names1]", "sklearn/compose/tests/test_column_transformer.py::test_transformers_with_pandas_out_but_not_feature_names_out[passthrough-expected_verbose_names2-expected_non_verbose_names2]"]

**Base Commit**: cd25abee0ad0ac95225d4a9be8948eff69f49690
**Environment Setup Commit**: 1e8a5b833d1b58f3ab84099c4582239af854b23a
