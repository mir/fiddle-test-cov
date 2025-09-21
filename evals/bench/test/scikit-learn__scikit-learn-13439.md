# scikit-learn__scikit-learn-13439

**Repository**: scikit-learn/scikit-learn
**Created**: 2019-03-12T20:32:50Z
**Version**: 0.21

## Problem Statement

Pipeline should implement __len__
#### Description

With the new indexing support `pipe[:len(pipe)]` raises an error.

#### Steps/Code to Reproduce

```python
from sklearn import svm
from sklearn.datasets import samples_generator
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_regression
from sklearn.pipeline import Pipeline

# generate some data to play with
X, y = samples_generator.make_classification(
    n_informative=5, n_redundant=0, random_state=42)

anova_filter = SelectKBest(f_regression, k=5)
clf = svm.SVC(kernel='linear')
pipe = Pipeline([('anova', anova_filter), ('svc', clf)])

len(pipe)
```

#### Versions

```
System:
    python: 3.6.7 | packaged by conda-forge | (default, Feb 19 2019, 18:37:23)  [GCC 4.2.1 Compatible Clang 4.0.1 (tags/RELEASE_401/final)]
executable: /Users/krisz/.conda/envs/arrow36/bin/python
   machine: Darwin-18.2.0-x86_64-i386-64bit

BLAS:
    macros: HAVE_CBLAS=None
  lib_dirs: /Users/krisz/.conda/envs/arrow36/lib
cblas_libs: openblas, openblas

Python deps:
       pip: 19.0.3
setuptools: 40.8.0
   sklearn: 0.21.dev0
     numpy: 1.16.2
     scipy: 1.2.1
    Cython: 0.29.6
    pandas: 0.24.1
```


## Hints

None should work just as well, but perhaps you're right that len should be
implemented. I don't think we should implement other things from sequences
such as iter, however.

I think len would be good to have but I would also try to add as little as possible.
+1

>

I am looking at it.

## Patch

```diff

diff --git a/sklearn/pipeline.py b/sklearn/pipeline.py
--- a/sklearn/pipeline.py
+++ b/sklearn/pipeline.py
@@ -199,6 +199,12 @@ def _iter(self, with_final=True):
             if trans is not None and trans != 'passthrough':
                 yield idx, name, trans
 
+    def __len__(self):
+        """
+        Returns the length of the Pipeline
+        """
+        return len(self.steps)
+
     def __getitem__(self, ind):
         """Returns a sub-pipeline or a single esimtator in the pipeline
 


```

## Test Patch

```diff
diff --git a/sklearn/tests/test_pipeline.py b/sklearn/tests/test_pipeline.py
--- a/sklearn/tests/test_pipeline.py
+++ b/sklearn/tests/test_pipeline.py
@@ -1069,5 +1069,6 @@ def test_make_pipeline_memory():
     assert pipeline.memory is memory
     pipeline = make_pipeline(DummyTransf(), SVC())
     assert pipeline.memory is None
+    assert len(pipeline) == 2
 
     shutil.rmtree(cachedir)

```

## Test Information

**Tests that should FAIL→PASS**: ["sklearn/tests/test_pipeline.py::test_make_pipeline_memory"]

**Tests that should PASS→PASS**: ["sklearn/tests/test_pipeline.py::test_pipeline_init", "sklearn/tests/test_pipeline.py::test_pipeline_init_tuple", "sklearn/tests/test_pipeline.py::test_pipeline_methods_anova", "sklearn/tests/test_pipeline.py::test_pipeline_fit_params", "sklearn/tests/test_pipeline.py::test_pipeline_sample_weight_supported", "sklearn/tests/test_pipeline.py::test_pipeline_sample_weight_unsupported", "sklearn/tests/test_pipeline.py::test_pipeline_raise_set_params_error", "sklearn/tests/test_pipeline.py::test_pipeline_methods_pca_svm", "sklearn/tests/test_pipeline.py::test_pipeline_methods_preprocessing_svm", "sklearn/tests/test_pipeline.py::test_fit_predict_on_pipeline", "sklearn/tests/test_pipeline.py::test_fit_predict_on_pipeline_without_fit_predict", "sklearn/tests/test_pipeline.py::test_fit_predict_with_intermediate_fit_params", "sklearn/tests/test_pipeline.py::test_predict_with_predict_params", "sklearn/tests/test_pipeline.py::test_feature_union", "sklearn/tests/test_pipeline.py::test_make_union", "sklearn/tests/test_pipeline.py::test_make_union_kwargs", "sklearn/tests/test_pipeline.py::test_pipeline_transform", "sklearn/tests/test_pipeline.py::test_pipeline_fit_transform", "sklearn/tests/test_pipeline.py::test_pipeline_slice", "sklearn/tests/test_pipeline.py::test_pipeline_index", "sklearn/tests/test_pipeline.py::test_set_pipeline_steps", "sklearn/tests/test_pipeline.py::test_pipeline_named_steps", "sklearn/tests/test_pipeline.py::test_pipeline_correctly_adjusts_steps[None]", "sklearn/tests/test_pipeline.py::test_pipeline_correctly_adjusts_steps[passthrough]", "sklearn/tests/test_pipeline.py::test_set_pipeline_step_passthrough[None]", "sklearn/tests/test_pipeline.py::test_set_pipeline_step_passthrough[passthrough]", "sklearn/tests/test_pipeline.py::test_pipeline_ducktyping", "sklearn/tests/test_pipeline.py::test_make_pipeline", "sklearn/tests/test_pipeline.py::test_feature_union_weights", "sklearn/tests/test_pipeline.py::test_feature_union_parallel", "sklearn/tests/test_pipeline.py::test_feature_union_feature_names", "sklearn/tests/test_pipeline.py::test_classes_property", "sklearn/tests/test_pipeline.py::test_set_feature_union_steps", "sklearn/tests/test_pipeline.py::test_set_feature_union_step_drop[drop]", "sklearn/tests/test_pipeline.py::test_set_feature_union_step_drop[None]", "sklearn/tests/test_pipeline.py::test_step_name_validation", "sklearn/tests/test_pipeline.py::test_set_params_nested_pipeline", "sklearn/tests/test_pipeline.py::test_pipeline_wrong_memory", "sklearn/tests/test_pipeline.py::test_pipeline_with_cache_attribute", "sklearn/tests/test_pipeline.py::test_pipeline_memory"]

**Base Commit**: a62775e99f2a5ea3d51db7160fad783f6cd8a4c5
**Environment Setup Commit**: 7813f7efb5b2012412888b69e73d76f2df2b50b6
