# SWT-Bench: Testing and Validating Real-World Bug-Fixes with Code Agents

Niels Mündler1 , Mark Niklas Müller1,2 , Jingxuan He1 , Martin Vechev1

arXiv:2406.12952v3 [cs.SE] 7 Feb 2025

1

Department of Computer Science, ETH Zurich

2

LogicStar.ai

{niels.muendler, mark.mueller, jingxuan.he, martin.vechev}@inf.ethz.ch 1 mark@logicstar.ai 2

## Abstract
Rigorous software testing is crucial for developing and maintaining high-quality code, making automated test generation a promising avenue for both improving software quality and boosting the effectiveness of code generation methods. However, while code generation with Large Language Models (LLMs) is an extraordinarily active research area, test generation remains relatively unexplored. We address this gap and investigate the capability of LLM-based Code Agents to formalize user issues into test cases. To this end, we propose a novel benchmark based on popular GitHub repositories, containing real-world issues, ground-truth bug-fixes, and golden tests. We find that LLMs generally perform surprisingly well at generating relevant test cases, with Code Agents designed for code repair exceeding the performance of systems designed specifically for test generation. Further, as test generation is a similar but more structured task than code generation, it allows for a more fine-grained analysis using issue reproduction rate and coverage changes, providing a dual metric for analyzing systems designed for code repair. Finally, we find that generated tests are an effective filter for proposed code fixes, doubling the precision of SWE-AGENT. We release all data and code at github.com/logic-star-ai/SWT-Bench.

## Introduction

As the complexity of software systems increases, rigorous testing is becoming more important than ever to ensure their reliability and correctness. However, while a large portion of these tests aims to reproduce previously reported issues (Kang et al., 2023), such issue reproduction is often disliked by professional developers (Straubinger & Fraser, 2023). Therefore, automatic generation of tests reproducing such issues from informal natural language descriptions is a promising path toward improving both code quality and developer productivity. Finally, generated tests can be leveraged as formal specifications to boost the effectiveness of automatic code repair tools (Chen et al., 2023a). However, while automatic code generation, in particular using Code Agents, is an extremely active research area (i.e. Yang et al. (2024); Tao et al. (2024); Zhang et al. (2024); Bouzenia et al. (2024b); OpenDevin (2024); Bouzenia et al. (2024a); Schäfer et al. (2024); Alshahwan et al. (2024a)), there is comparatively little work investigating automatic test generation directly. Indeed, while prior work has proposed methods based on symbolic execution (Lukasczyk & Fraser, 2022), specialized transformers (Tufano et al., 2020), and general-purpose LLMs (Li et al., 2023; Alshahwan et al., 2024b; Kang et al., 2023, 2024; Chen et al., 2023b), Code Agents have not been considered in this context, and even less work is applicable to the issue reproduction setting. Finally, large-scale, diverse test-generation datasets are lacking for Python, which is one of the most popular programming languages at the time of writing (TIOBE, 2024; PYPL, 2024) and a focus of Code Agent research.

Task inputs

Generated Tests

Pre PR

Post PR

isValid currently allows trailing newlines but only alphanumeric characters should be accepted.

isValid("name\n") == False

Fail

Pass

isValid("name") == True

Pass

Pass

Codebase (Pre PR)

isValid("name") == False

Fail

Fail

**Figure 1: Evaluation of an SWT-B ENCH instance. Given an issue description in natural language**

and the corresponding codebase, the task is to generate tests that reproduce the issue. We considered a test to reproduce the issue if it fails on the codebase before the pull request (PR) is accepted, i.e., before the golden patch is applied, but passes after. We call this a fail-to-pass test (F → P ). A Benchmark for Test Generation In this work, we propose SWT-B ENCH, a novel and comprehensive dataset for test generation with the goal of issue reproduction in Python. SWT-B ENCH contains over 1 900 samples, each consisting of a GitHub issue, a golden code patch resolving the issue by adjusting the code, and a set of golden reference tests, obtained by transforming the popular SWE-B ENCH (Jimenez et al., 2023) from code repair to test generation. We leverage the fact that any code repair task can be transformed into a test generation task, even in the absence of golden tests, by utilizing the golden code patch for evaluation. Concretely, for every generated test, we determine whether it reproduces the described issue, by checking whether it fails on the original repository but passes after the golden patch is applied. The golden reference tests, used in SWEB ENCH for the evaluation of code repair performance, are solutions in this test generation setting. We illustrate this evaluation process of SWT-B ENCH in Fig. 1. Further, we report the coverage of the code modified by the golden patch as a more fine-grained evaluation metric for generated tests. Benchmarking Test Generation Methods We evaluate various existing test generation approaches on SWT-B ENCH, including directly prompting state-of-the-art LLMs to generate tests for the given issue, a state-of-the-art issue reproduction method LIBRO (Kang et al., 2023), and different Code Agents adapted to the task of test generation (Yang et al., 2024; Zhang et al., 2024; Aider, 2024). Interestingly, we find that despite being designed for code repair, the Code Agent SWE-AGENT outperforms non-agent methods at test generation, both reproducing more issues and achieving higher coverage, and generally find all agents to perform strongly in both areas. However, we still observe significant complementarity between the different approaches, with an ideal ensemble of the best four methods solving 71% more samples than the best single method. Further, while the performance on code repair and test generation is generally correlated, this does not hold on a per-sample basis. This indicates that reproducing an issue with a test and fixing this issue are distinct tasks of different difficulty. Finally, we find that generated tests can serve as a strong signal for the correctness of proposed code fixes, with SWE-AGENT achieving over twice the precision on fixes that pass self-generated tests that failed before the fix was applied. Key Contributions Our key contributions are:
- We introduce SWT-B ENCH, a new benchmark for test-based issue reproduction based on an extensive dataset of real-world software repositories, user issues, code patches, and test cases (§3).
- We propose to adapt Code Agents to the task of test generation for issue reproduction (§4).
- We provide an extensive evaluation of SWT-B ENCH, and demonstrate that, while issue reproduction is generally hard, Code Agents perform well, outperforming prior methods (§5).

## Related Work

Code Datasets Over recent years, a variety of code datasets such as HumanEval (Chen et al., 2021), APPS (Hendrycks et al., 2021), and MBPP (Austin et al., 2021) have been proposed to assess the capabilities of code synthesis and repair systems (Lin et al., 2017; Li et al., 2022). However, these largely focus on interview-style coding challenges or function-level code synthesis and do not capture the complexity of real-world codebases. Further, they have been shown to often include insufficient test cases to properly assess the correctness of the generated code (Liu et al., 2023a). Recently, a range of repository-level code-generation benchmarks (Liu et al., 2023b; Jain et al., 2024) including the popular SWE-B ENCH (Jimenez et al., 2023) have emerged, as modern LLMs 2

began to saturate the simpler function-level benchmarks. However, none of these benchmarks were designed to assess test generation. The only dataset for reproducing bugs based on real-world issues, Defects4J (Just et al., 2014), focuses on Java, is outdated, limited in size, and contains only short bug descriptions rather than detailed issue reports. In contrast, SWT-B ENCH is based on Python, which is better supported by modern Code Agents, contains more recent issue reports, and is significantly larger. Automated Unit Test Generation Many approaches have been suggested to automate (unit) test generation leveraging symbolic execution (Lukasczyk & Fraser, 2022), specialized transformers (Tufano et al., 2020), and general purpose LLMs (Li et al., 2023; Alshahwan et al., 2024b; Kang et al., 2023; Tufano et al., 2020; Kang et al., 2024; Schäfer et al., 2024; Alshahwan et al., 2024a; Chen et al., 2023b). Depending on their focus, they can be used to increase test coverage (Alshahwan et al., 2024b; Schäfer et al., 2024), find edge cases (Lukasczyk & Fraser, 2022), or reproduce reported issues (Kang et al., 2023). Issue-reproducing tests are especially interesting, as they can be used to validate automatically generated code repair candidates and thus improve the precision of code repair systems (Chen et al., 2023a). However, most test-generation approaches are not applicable to issue reproduction. We therefore evaluate the most recent applicable method, LIBRO (Kang et al., 2023), and a range of other LLM-based baselines on SWT-B ENCH. Code Agents Over the last year, LLMs have been equipped with tools to observe and interact with their environment over multiple turns and preserve a state across these turns (Wang et al., 2024). These so-called agents have proven successful on a range of complex tasks, including code repair and synthesis (Bouzenia et al., 2024b; OpenDevin, 2024; Zhang et al., 2024; Yang et al., 2024; Tao et al., 2024; Bouzenia et al., 2024a; Aider, 2024). Such Code Agents can typically search, read, and edit code using an agent computer interface (ACI) (Yang et al., 2024). In this work, we leverage such Code Agents for generating issue-reproducing tests by changing their instructions.

## Benchmarking Test Generation

In this section, we outline the structure of the proposed benchmark, SWT-B ENCH, and how we leverage it to measure the capabilities of LLMs and Code Agents for test generation.
### Notation and Definitions

We first introduce the notation to describe codebases, their test suites, and changes to these codebases in the form of patches. We denote a codebase R after applying patch X as R ◦ X. Several patches can be applied sequentially, i.e. R ◦ X ◦ Y is the codebase R after applying a first patch X and then a second one Y . When a code patch X is applied to R, a set of tests T can be used to check the correctness of the applied patch. A single test s can either pass (P) or fail (F) after we execute it within the context of codebase R. We consider a test to fail if an error is thrown during its execution, e.g., an AssertionError or ValueError. Such test errors frequently occur if R lacks or misimplements the functionality targeted by the test. They can also occur due to other reasons, such as incorrect syntax or formatting of the test s. Conversely, a test passes when running the test triggers no error. We define this process as an execution function: exec(s, R) ∈ {P, F }. We consider a test s to reproduce a described issue I of R, which is resolved by patch X if it fails on the original codebase (i.e. exec(s, R) = F ) but passes on the patched codebase (i.e. exec(s, R ◦ X) = P ). We denote these fail-to-pass tests with F → P and define F → F , P → P , and P → F tests similarly. If a test transitions from failing on R to any state on R◦X, we denote it as F → × and vice versa for × → F . Further, we consider a set of tests T to be successful at reproducing the issue I, if it contains at least one F → P test and no × → F test, or equivalently ∃s ∈ T, exec(s, R) = F ∧ ∀s ∈ T, exec(s, R ◦ X) = P .
### Benchmark Overview

To construct SWT-B ENCH, we leverage the same underlying data as SWE-B ENCH (Jimenez et al., 2023) and summarize its three-stage construction process here for completeness. 3

1. Scrape a total of ∼ 90 000 pull requests (PRs) from 12 popular open-source Python repositories from GitHub.
2. Filter PRs to only include those that were merged, resolved a GitHub issue, and made
changes to at least one test file.
3. Filter PRs to feature at least one F → P test, removing PRs that result in installation or
runtime errors. This results in 2 294 task instances, each consisting of a GitHub issue, a golden patch X ∗ fixing the issue, and a set of golden reference tests T ∗ .
**Table 1: Characterization of different attributes of**

However, we find that for 311 instances, the golden patch can not be evaluated without errors or does not fix the described issue reliably, i.e., some tests of T ∗ fail on R ◦ X ∗ . The main reasons are flaky test suites, e.g., django cases where HTTP requests sometimes return 500 Internal Server Error although the related code was not changed, erroneous test suite setup, e.g., the test suite tool tox not allowing external tools invoked in the sphinx setup, and time outs, e.g., when slow tests in the sympy library are run. We exclude these, leaving a total of 1 983 instances in SWT-B ENCH. To enable cheaper evaluation we create SWT-B ENCH L ITE, a subset of 276 issues, corresponding to SWE-B ENCH -L ITE.

SWT-B ENCH instance. Mean

Max

Issue Text

# Words

318.0

8756

Codebase

# Files # Lines

1563.0
337K

2757 772K

Existing Tests

# F →P # F →F # P →P # P →F # Total Coverage

0.0
5.0
116.7
1.5
123.2
70.1%

4 183 4837 607 4842 100%

Golden Tests

# F →P # P →P # Added # Removed # Files Ed. # Lines Ed.

2.0
0.9
2.9
0.3
1.5
31.8

958 339 958 104 15 581

We summarize key statistics of SWT-B ENCH in Table 1 and show pylint its repository composition in Fig. 2. While issue descriptions are on django sympy average only 318 words long, the longest one reaches 8 756 words. Generally, repository complexity is high with on average over 1 500 seaborn files and over 300 000 lines of code. Many repositories feature large flask test suites of > 120 and up to 4 800 tests, already covering 70% of matplotlib the lines in the to-be-patched code. Most of these existing tests are xarray sphinx unaffected by the golden patch with basically no F → P and only pytest requests astropy scikit
1.5 P → F tests on average. The golden tests remove on average
0.3 tests and add another 2.9 new test cases, of which roughly twothirds are F → P . The test patches edit on average 31.8 lines in Figure 2: Distribution of
1-2 files. Due to the filtering for unresolved issues during dataset SWT-B ENCH instances over GitHub repositories. curation, no golden tests are F → F or P → F .
### Metrics

We propose two main metrics to evaluate the test generation performance of any method; Success rate (S) and change coverage (C), described below. We further introduce the necessary but insufficient property of patch well-formedness (W). Success Rate The success rate S measures the portion of instances where the generated tests T reproduced the issue according to the definition in §3.1, i.e. at least one test in T transitions from failing to passing and none fail after applying the patch. This is the most important performance measure, as the presence of F → P and the absence of × → F tests are key for test-driven development and automatic code generation. We further report the portion of instances for which at least one Fail-to-Pass (F → P ), Fail-to-Any (F → ×), and Pass-to-Pass (P → P ) was generated. While F → × tests, i.e., all tests that fail on the original codebase, are not necessarily desirable, only F → × tests can result in the reproducing F → P test, whereas P → × tests can never reproduce an issue. As F → × can further be identified without knowledge of the golden code patch, generation methods can aim to always produce an F → × test. Finally, P → P tests indicate that the model generated well-formed and valid, but unrelated tests. 4

Change Coverage Coverage is an important metric to determine what portion of a codebase is tested. While path coverage measures this optimally, the exponential number of paths makes it infeasible in practice. We thus follow common practice, and instead measure line coverage. As we aim to specifically test the code described in the issue text, we consider only the coverage of the changes made by the golden code patch. Further, we observe that patches may include portions of non-executable lines, e.g. documentation or configuration files, and exclude them. Specifically, we consider all lines that are executed by the original test suite T R or the golden test suite T ∗ on both R and R ◦ X ∗ to be executable, and track coverage of such executable lines. Finally, we consider both the coverage of removed (including modified) lines of code in the original codebase and added (including modified) lines of code in the patched codebase, illustrated in Fig. 3. Formally, given the number of times CTRR (l) ∈ Z≥0 a specific line of code l was executed when running the test suite T R on codebase R, we define the executable lines of the patch X as

def isValid(name): """ check digit """ digitInFront = match( r"\d+.*", name ) if digitInFront: print("has digit") return False return True

def isValid(name): """ check d & n """ digitInFront = match( r"\d+.*", name ) trailNewl = newl(name) if trailNewl: print("trail newl") if digitInFront: print("has digit") return digitInFront return trailNewl

Xr∗ = {l ∈ Xr | CTRR (l) + CTR∗ (l) > 0}

+ +

R◦X Xa∗ = {l ∈ Xa | CTR◦X (l) > 0} R (l) + CT ∗

**Figure 3: Illustration of change coverage ∆C**

of the generated tests T , given the test suite where Xr and Xa are the lines added and removed T R of the original code base R, the golden by patch X, respectively, and T ∗ are the golden tests. patch X ∗ , and the golden tests T ∗ . Finally, we obtain the change coverage of the generated tests T as ∆CTX =

R◦X |{l ∈ Xr∗ | CTRR ∪T (l) > CTRR (l)}| + |{l ∈ Xa∗ | CTR◦X R ∪T (l) > CT R (l)}| . |Xr∗ | + |Xa∗ |

Where X and T are clear from context, we drop them for notational clarity. If none of the lines modified by the golden patch X are executed by any test, i.e., |Xr∗ | + |Xa∗ | = 0, we exclude this instance from our coverage analysis (1% of cases). Patch Well-Formedness Many LLMs struggle to generate well-formed code patch files (Jimenez et al., 2023) and the methods we investigate employ different approaches to mitigate this issue. To assess them, we additionally measure the patch applicability W as the portion of instances for which a well-formed patch was generated. We define W as the portion of instances for which the generated patch X can be applied to the original codebase R without errors. Since well-formedness is necessary for any test to be executed, it always exceeds S, F → P , and related rates.

## Automatic Test Generation

We first discuss how the test generation task differs from code repair, before introducing a novel code diff format based on these insights that is optimized for fault tolerance. Finally, we propose a range of test generation methods based on directly querying LLMs and leveraging Code Agents.
### Test Generation vs Code Repair

Automatic test generation is closely related to code repair: Instead of predicting a patch X that fixes the described issue and is then evaluated using a golden test T ∗ , we aim to predict reproducing tests T which are then evaluated on both the original state of the codebase R and the state after applying the golden code patch X ∗ . However, there are some key differences between the two tasks: First, adapting an existing test suite to reproduce an issue typically only requires adding new tests. Concretely, 71% of golden tests in SWT-B ENCH only add new test functions, with another 28% modifying existing functions, and only 1% removing functions. Second, testing permits and requires a more granular analysis. While fixed code is either correct and passes all test cases or incorrect when failing any of them, generated tests can be correct but irrelevant to the issue (P → P ), call relevant code but fail to expose the precise bug (increase in coverage), reproduce the issue with varying comprehensiveness on edge cases (F → P , with varying coverage), or fail in different ways. 5

1 -- demo/file.py

1

2 +++ demo/file.py

2

3 @@-4,5 +4,5 @@

3

4 def test_euclidean(a, b):

4

5 -

5

6 + 7

assert euclidean(1, 0) == 1 assert euclidean(100, 10) == 10 assert euclidean(1, 1) == 1

6 7

demo/file.py rewrite 1 def test_euclidean(a, b): assert euclidean(100, 10) == 10 assert euclidean(1, 1) == 1 end diff

**Figure 4: Comparison of the default unified diff format (left) and our fault-tolerant version (right).**

### A Code Diff Format for Automatic Test Generation

Code changes are typically represented in the unified diff format, i.e., in the git patch and diff format. While using this format to represent code changes is both precise and human-readable, it is very sensitive to misspecifications, requiring, e.g., the exact line numbers of code changes to be specified and specific code snippets (including all to-be-changed lines) to be repeated verbatim. As a result, many LLMs struggle to produce well-formed patch files (Jimenez et al., 2023). Even when loosening the strict diff requirements and fuzzy-matching the generated diff to a best-fit part of the code, GPT-4 only succeeded in 48% of cases, resulting in only 10 correctly reproduced issues. To alleviate this issue, we propose an adjusted patch format optimized for LLM generation that is easier to adhere to and more robust. Specifically, our custom diff format allows entire functions or classes to be inserted, replaced, or deleted, given the full function or class definition and (faulttolerant) location in the code. We show an example in Fig. 4, comparing it to the unified diff format. Based on whether the model wants to rewrite an existing function or insert a new function, the provided code is then substituted or inserted at the code location. This format is particularly well suited for test generation which usually only requires adding test functions. We provide a more formal description of this format in App. A and demonstrate its effectiveness in §5.
### Direct LLM Generation of Tests

We consider four baselines for test generation: Direct zero-shot prompting with the unified patch format (Z ERO S HOT), zero-shot prompting with our novel patch format (Z ERO S HOT P LUS), selecting the best out of 5 patches using an oracle (PASS @5), and the state-of-the-art test generation method, LIBRO (Kang et al., 2023), which uses a range of heuristics to pick the most promising among multiple generated tests. In all methods, the LLM is instructed to add tests to reproduce and cover the described issue in the codebase. We describe these methods below, deferring further details to App. E. Z ERO S HOT prompts the model with the issue description, a subset of the codebase retrieved using BM-25 (Robertson & Zaragoza, 2009), and instructions to generate a patch file in unified diff format. This method corresponds to the LLM-only baseline in SWE-B ENCH (Jimenez et al., 2023). Z ERO S HOT P LUS is similar to Z ERO S HOT but leverages our custom diff format, discussed in §4.2, which is optimized for LLMs and robustness to minor specification errors. PASS @5 uses our Z ERO S HOT P LUS prompting scheme to generate 5 proposal tests and then uses an oracle to pick the best one. While this is of course not practical in a real-world setting, it allows us to assess the potential of the LLM to generate good test cases given an effective selection mechanism. LIBRO (Kang et al., 2023), is the current state-of-the-art for LLM-based test generation. Similar to PASS @5 it generates multiple proposal tests using Z ERO S HOT P LUS prompting. However, instead

of using an oracle, it combines multiple heuristics to select the best test cases. In particular, it runs all generated tests and then selects the one inducing an error that is most similar to the problem description. This permits not only checking whether a generated diff is well-formed and the proposed test fails on the original codebase but also selecting the most relevant test case. As LIBRO was originally proposed for Java, we adapt it to our Python setting, as detailed in App. B.
### Code Agents for Test Generation

LLM-based agents are systems that take actions based on LLM-generated text, providing tools to observe and interact with their environment over multiple turns and preserve some state across these 6

turns. In the case of Code Agents, they can typically search, read, and edit code using an agent computer interface (ACI) (Yang et al., 2024). Recent work has shown that such Code Agents are particularly effective for complex repository-level code synthesis and repair tasks, outperforming unaided LLMs by a significant margin (Bouzenia et al., 2024b; OpenDevin, 2024; Zhang et al., 2024; Yang et al., 2024; Tao et al., 2024). In this work, we leverage Code Agents for automatic test generation by adjusting their instructions. Specifically, we adapt SWE-AGENT (Yang et al., 2024), AIDER (Aider, 2024), and AUTO C ODE ROVER (Zhang et al., 2024). SWE-AGENT (Yang et al., 2024) provides the LLM direct access to (augmented) command line tools and processes the output of these tools to be more easily parseable by an LLM. In particular, they provide special tools for searching, viewing, and editing files. Beyond initial instructions, they provide little guardrails or structure for the LLM and let it interact with a limited shell environment. AIDER (Aider, 2024) performs a repository indexing step to guide file selection and then includes all selected files in the next prompts. Further, model-generated summaries and reflections on previous actions are leveraged to augment the context. Before an edit is applied, it undergoes validation via static analysis and repository test cases using project-specific evaluation harnesses.

AUTO C ODE ROVER (Zhang et al., 2024) separates the code repair task into two distinct stages. In the first stage, the LLM is tasked with collecting all required context for the task at hand. To this end, it is equipped with a range of advanced code search and navigation tools, allowing it, e.g., to retrieve class signatures, function definitions, or surrounding code snippets. Once the LLM believes it has gathered sufficient context, it proceeds to the second stage. There, the LLM is tasked with generating the actual code patch in a single step, retrying only if the patch can not be applied. Adapting Code Agents for Test Generation As SWE-AGENT, AIDER, and AUTO C ODE ROVER were designed for program repair, we adapt their system and instruction prompts to focus on creating high-quality test cases. We find that the underlying LLMs are capable of following these changed instructions and successfully generate test cases for up to 87% of issues. Typically, the instruction changes were as simple as replacing phrases like "solve the issue" with "create unit tests that cover the issue". We provide a more detailed description of the used prompts in App. E. We experiment with instructing SWE-AGENT explicitly to execute the generated test cases before submitting them. We call this variant SWE-AGENT + and find that this increases the success rate S from 15.9% to 18.5% (see Table 2). Note we do not provide any information on how to run the tests. This contrasts the LIBRO setting, in which the test execution commands are assumed to be known.

## Experimental Evaluation

We leverage SWT-B ENCH to compare the performance of different test generation methods and underlying LLMs (§5.2), their relation with the code repair setting (§5.3), and the impact of instance characteristics (§5.4). We further explore hyperparameter ablations in App. C.
### Experimental Setup

We consider GPT-4 (gpt-4-1106-preview OpenAI 2023), GPT-4o mini (gpt-4o-mini-2024-07-18 OpenAI 2024), Claude 3.0 Haiku (Anthropic, 2023), Claude 3.5 Sonnet (Anthropic, 2024), Mistral Large 2 (Team, 2024b) (served via the Mistral AI API), and Mixtral 7x22b (Team 2024a served by Together AI TogetherAI 2023), as underlying LLMs, using GPT-4 unless indicated otherwise. We sample at temperature t = 0 for all zero-shot methods and agents and at t = 0.7 for LIBRO and PASS @5. For SWE-AGENT, AIDER, and AUTO C ODE ROVER, we use their default settings, restricting the number of API calls to 20, reflection steps to 3, and interaction rounds to 10, respectively. For LIBRO we sample 5 tests. Due to budget constraints, we focus our evaluation on SWT-B ENCH -L ITE. In App. C we explore and justify this choice of hyperparameters in detail.
### Automatic Test Generation

Comparing Test Generation Methods We compare test generation performance in Table 2 where all methods have access only to the issue description and the original codebase. We observe that using the original git code-diff format, Z ERO S HOT only generates well-formed patches 7

for 48.6% of issues. Using our novel test-specific code-diff format (Z ERO S HOT P LUS) boosts this rate to 89.5% yielding an almost 3x increase in success rate (S) to 9.4%. While picking the best among five generated tests (PASS @5) even yields an S of 20.3%, the heuristics employed by LIBRO can only convert about half of this gap into an S of 14.1%, still beating AUTO C ODE ROVER and AIDER which achieve an S of 9.1% and 12.7% respectively. SWE-AGENT, however, outperforms LI - Table 2: Rate of well-formed patches (W), successful BRO at an S of 15.9%, increased to tests (S), potentially reproducing initially failing tests
18.5%, when instructed to check its (F → ×), reproducing fail-to-pass tests (F → P ), and
generated tests (SWE-AGENT +). This correct but unhelpful pass-to-pass tests (P → P ), in %. stronger performance is significant at Method W S F →× F →P P →P p < 0.1%. Interestingly, SWE-AGENT produces fewer F → × tests than AIDER G OLDEN
100.0 100.0 100.0
100.0
11.2
PASS @5
93.1 20.3
62.7
22.1
7.2
and LIBRO despite having much higher applicability and yielding a higher S. Z ERO S HOT
48.6
3.6
38.8
5.8
3.6
We conclude that general-purpose Code Agents already perform as well as domain-specific test generation methods, with simple test-specific adjustments providing significant improvements.

LIBRO

89.5
92.0

9.4
14.1

55.4
60.1

10.1
15.2

7.2
7.2

AUTO C ODE ROVER AIDER SWE-AGENT SWE-AGENT +

47.1
66.7
87.3
85.5

9.1
12.7
15.9
18.5

43.8
57.6
48.2
46.4

9.1
17.0
16.7
19.2

7.6
8.7
9.8
10.1

Z ERO S HOT P LUS

Coverage of Generated Tests We analyze the Table 3: Change Coverage ∆C [%] as defined change coverage ∆C of the generated tests, i.e., in §3.3 aggregated over all instances, S inthe portion of executable golden patch code that is stances and non S instances (¬S). covered by the generated tests, in Table 3. Across Method ∆C all ∆C S ∆C ¬S all methods, we observe a significantly higher coverage on successful instances (∆C S ), indicatG OLDEN
72.0
72.0
ing that coverage is indeed correlated with test PASS @5
31.3
65.6
22.5
quality but more granular than S. Interestingly, Z ERO S HOT
7.6
34.9
6.6
SWE-AGENT + achieves notably higher coverage Z ERO S HOT P LUS
21.5
76.7
15.7
on successful instances than SWE-AGENT highLIBRO
23.8
64.2
17.0
lighting the impact of providing agents with more AUTO C ODE ROVER
17.9
61.3
13.6
test-generation-specific tools to identify promising AIDER
27.8
59.5
23.1
tests. Further, LIBRO achieves lower coverage than SWE-AGENT
26.5
64.7
19.1
most Code Agents, most likely as a consequence SWE-AGENT +
27.6
69.4
18.0
of preferring shorter tests. Model Effect We compare the effect Table 4: Comparison of different underlying LLMs for of different underlying LLMs for SWE- SWE-AGENT, all in %. AGENT in Table 4. We observe that Model W S F → × ∆C all not only S but even applicability (W) is highly sensitive to the underlying LLM’s Mistral L. 2
76.1 16.3
51.4
23.0
performance, with Haiku, GPT-4o mini, GPT-4
87.3 15.9
48.2
26.5
and Mixtral achieving significantly lower Cl.
3.5
Sonnet
67.8
12.3
59.1
30.3
performance than GPT-4. More capable GPT-4o mini
71.0
9.8
36.2
20.9
models like Claude 3.5 Sonnet and MisCl. 3.0 Haiku
20.3
2.5
6.9
3.0
tral Large 2 perform on par, with the latMixtral 8x22B
3.3
0.7
1.8
0.9
ter even outperforming GPT-4.
5.3

Code Repair and Test Generation Table 5: Performance of Z ERO S HOT P LUS, given the test file to change, none (-), the golden (✓) or an inTest Generation for a Given Code correct (✗) code patch, and the files retrieved via BM-25 Patch To assess the effectiveness of au(r), or modified by the golden (✓) or incorrect patch (✗). tomatic test generation at testing specific, provided fixes, we investigate the effect Test File Mod. Files Patch W S F → × ∆C all of providing a (possibly incorrect) code r
87.8
8.1
52.3
12.5
patch, the files it changed, and the test ✓ ✓
85.5 10.5
64.0
18.4
✗ ✗
75.0 10.5
50.0
13.2
file to be modified instead of the files re✓ r
76.7 15.1
59.3
17.6
trieved with BM25, reporting results in 8

**Table 5 in %. We use Z ERO S HOT P LUS to generate incorrect patches, resampling ≤5 times and**

excluding instances where we could not generate an incorrect but applicable patch, reducing the sample size to n = 172. Providing the test files to change almost doubles S from 8.1% to 15.1%, pulling even with SWE-AGENT. We observe that meanwhile providing a code patch and the files it changed has a much smaller impact, increasing S only to 10.5% for both the golden patch and an incorrect patch. This highlights the importance of retrieving the correct context for generating relevant tests. Meanwhile, GPT-4 is able to leverage the correct patch, and to improve the coverage increase of the relevant lines by almost 50%, from 12.5% to 18.4%. Filtering Code Fixes with Generated Tests State-of-the-art code generation methods only resolve around 20% of cases on SWE-B ENCH -L ITE (Jimenez et al., 2023). Without suitable tests to distinguish correct from incorrect fixes, the overhead from manual testing (Yang et al., 2008) would thus outweigh any benefits from automatic code generation. To address this issue, we use SWEAGENT to generate both bug fixes and tests, in a similar manner to Chen et al. (2023a). We then filter the generated bug fixes, retaining only those where all generated tests are F → P or P → P . While only achieving 20% recall, this more than doubles the precision of SWE-AGENT to 47.8%, making it significantly more practically useful, highlighting the importance of test generation, and opening an avenue to transferring the results from Chen et al. (2023a) towards more complex and realistic scenarios with more expensive inference and evaluation steps. Correlation of Test Generation and Code Repair Table 6: Overlap in solved instances of We analyze the overlap between solved instances of SWE-B ENCH and SWT-B ENCH. SWE-B ENCH and SWT-B ENCH, showing results in SWT SWE Overlap p-Value [%]
**Table 6. We observe that the overlap is small for both**

Z ERO S HOT P LUS 26 16 1
80.4%
methods, with no statistical evidence of correlation SWE-AGENT 44 50 7
72.8%
(p-values of 80.4% and 72.8% for Z ERO S HOT P LUS and SWE-AGENT, respectively, under the null hypothesis of independence and uniform hardness), indicating that generating tests and fixes are distinct tasks of different difficulties. We explore this relationship in more detail in App. D.
### Test Generation Success and Instace Characteristics

0

50

>

50

≤

0

20

≤

0

10

≤

0

% Success Rate (S) Effect of Issue Description Length
20.0
We investigate the relationship between
17.5
ZeroShotPlus issue description length and test gener15.0 LIBRO
12.5
AutoCodeRover ation performance in Fig. 5. We ob10.0 Aider
7.5
serve a general trend that issues with SWE-Agent+
5.0
longer descriptions are easier to gener2.5
0.0
ate tests for, with all methods achieving a higher S for longer descriptions, however tending to slightly decrease for Figure 5: Distribution of success rate (S) across issue devery long descriptions. This is likely scription lengths in # tokens due to the increased amount of information available in longer descriptions, while too-long descriptions may contain many distractors and make it difficult to extract relevant information for the LLM. SWE-AGENT +, which actively summarizes context, limiting file content and reducing history, is least sensitive to issue description length, achieving approximately the same S for all but the shortest lengths.

Effect of Data Contamination Table 7: Performance of Z ERO S HOT P LUS on PRs before/after As SWT-B ENCH is based on GPT-4 knowledge cutoff (KC = 30th April 2023) in %. historic GitHub issues, they may PR created n W S F → × F → P P → P ∆C all be contained in the pre-training data of the LLMs we use. To before KC 83 56.6 6.0
42.2
8.4
4.8
35.9
investigate this issue, we conafter KC 83 47.0 4.8
39.8
4.8
3.6
35.9
ducted an experiment comparing the performance of Z ERO S HOT P LUS on all issues created after the Knowledge Cutoff (KC) of GPT-4 (April 2023) to a random subset of the same size of instances created before, and report the results in Table 7. While we observe a small performance difference, we can not confirm its statistical significance (p ≈ 37%) due to the low number of samples created after the KC. Further, 9

all methods in Table 2 use the same underlying LLM and should thus benefit from any potential contamination to a similar degree, allowing for a fair comparison between different methods. Method Complimentarity We consider four diverse methods from §5.2 and analyze the overlap in the instances for which they are able to generate successful tests. We show the results in Fig. 6. While the best-performing approach, SWE-AGENT +, alone is able to solve 51 instances, the combination of all four approaches is able to solve 87 instances, highlighting the benefit of exploring a variety of approaches for test generation.

LIBRO AutoCodeRover

39

Aider SWE-Agent+

25

35

10

6 2

2 1

3

10

16 2 5

2 7

6

51 9

3 9

## Limitations and Future Work

**Figure 6: Overlap in instances solved by**

While our novel SWT-B ENCH covers a wide range of the four best performing methods. real-world issues, it has several limitations: It is limited to Python, which may limit the generalizability of our findings to other programming languages. Second, the dataset is based on popular GitHub repositories, which may not be representative of common software development practices and does preclude the generation of a private holdout test set. Finally, the dataset is limited to bug reproduction and issues that can be easily covered by adding test cases and does not measure edge case detection or global coverage increase. Further, as discussed in §5.4, most issues in SWT-B ENCH have been created before the knowledge cutoff of state-of-the-art models, posing a risk for data contamination. One approach to address this issue is to create a rolling version of SWT-B ENCH, based only on the most recently created GitHub issues. However, this comes at the cost of direct comparability of results and increased cost for reproducing results for all baselines on a changing evaluation set. Addressing these limitations would be an interesting direction for future work. As concrete starting points, we found several common errors even in the best performing method SWE-AGENT + that could be addressed through specialized monitoring: Adding passing tests that do not reproduce the given issue, getting stuck in loops after generating inapplicable edit commands, failing to execute the test environment correctly and adding tests with syntax errors or using invalid variables.

## Conclusion

We proposed SWT-B ENCH, a novel benchmark for generating reproducing tests from GitHub issue descriptions and the corresponding code bases. SWT-B ENCH leverages the dataset underlying the popular SWE-B ENCH which additionally contains a golden patch fixing the described issue. We judge whether a generated test reproduces the described issue by checking whether the test fails before applying this golden patch and succeeds afterward. We measure both the rate of such fail-topass tests and the coverage of the golden patch, providing a corresponding evaluation harness. We evaluated a variety of LLM-based test generation methods including Code Agents on SWT-B ENCH and found that Code Agents already outperform other approaches with only minor adaptations for the test-generation task. Finally, we demonstrated the great potential of generated tests to serve as a signal for the correctness of code fixes, i.e., we double the precision of Code Agents by filtering the generated patches to only those that cause a previously failing self-generated test to pass.

10

## References
Aider. Aider is SOTA for both SWE Bench and SWE Bench Lite, Jun 2024. Nadia Alshahwan, Jubin Chheda, Anastasia Finegenova, Beliz Gokkaya, Mark Harman, Inna Harper, Alexandru Marginean, Shubho Sengupta, and Eddy Wang. Automated unit test improvement using large language models at meta. CoRR, abs/2402.09171, 2024a. doi: 10.48550/ARXIV.
2402.09171.
Nadia Alshahwan, Jubin Chheda, Anastasia Finegenova, Beliz Gokkaya, Mark Harman, Inna Harper, Alexandru Marginean, Shubho Sengupta, and Eddy Wang. Automated unit test improvement using large language models at meta. CoRR, abs/2402.09171, 2024b. doi: 10.48550/ARXIV.
2402.09171.
Anthropic. Introducing Claude, Mar 2023. Anthropic. Introducing Claude 3.5 Sonnet, Jun 2024. Jacob Austin, Augustus Odena, Maxwell I. Nye, Maarten Bosma, Henryk Michalewski, David Dohan, Ellen Jiang, Carrie J. Cai, Michael Terry, Quoc V. Le, and Charles Sutton. Program synthesis with large language models. ArXiv preprint, abs/2108.07732, 2021. Islem Bouzenia, Premkumar T. Devanbu, and Michael Pradel. Repairagent: An autonomous, llmbased agent for program repair. CoRR, abs/2403.17134, 2024a. doi: 10.48550/ARXIV.2403.
17134.
Islem Bouzenia, Premkumar T. Devanbu, and Michael Pradel. Repairagent: An autonomous, llmbased agent for program repair. CoRR, 2024b. Bei Chen, Fengji Zhang, Anh Nguyen, Daoguang Zan, Zeqi Lin, Jian-Guang Lou, and Weizhu Chen. Codet: Code generation with generated tests. In Proc. of ICLR, 2023a. Mark Chen, Jerry Tworek, Heewoo Jun, Qiming Yuan, Henrique Pondé de Oliveira Pinto, Jared Kaplan, Harrison Edwards, Yuri Burda, Nicholas Joseph, Greg Brockman, Alex Ray, Raul Puri, Gretchen Krueger, Michael Petrov, Heidy Khlaaf, Girish Sastry, Pamela Mishkin, Brooke Chan, Scott Gray, Nick Ryder, Mikhail Pavlov, Alethea Power, Lukasz Kaiser, Mohammad Bavarian, Clemens Winter, Philippe Tillet, Felipe Petroski Such, Dave Cummings, Matthias Plappert, Fotios Chantzis, Elizabeth Barnes, Ariel Herbert-Voss, William Hebgen Guss, Alex Nichol, Alex Paino, Nikolas Tezak, Jie Tang, Igor Babuschkin, Suchir Balaji, Shantanu Jain, William Saunders, Christopher Hesse, Andrew N. Carr, Jan Leike, Joshua Achiam, Vedant Misra, Evan Morikawa, Alec Radford, Matthew Knight, Miles Brundage, Mira Murati, Katie Mayer, Peter Welinder, Bob McGrew, Dario Amodei, Sam McCandlish, Ilya Sutskever, and Wojciech Zaremba. Evaluating large language models trained on code. CoRR, 2021. Yinghao Chen, Zehao Hu, Chen Zhi, Junxiao Han, Shuiguang Deng, and Jianwei Yin. Chatunitest: A framework for llm-based test generation. arXiv e-prints, 2023b. Dan Hendrycks, Steven Basart, Saurav Kadavath, Mantas Mazeika, Akul Arora, Ethan Guo, Collin Burns, Samir Puranik, Horace He, Dawn Song, and Jacob Steinhardt. Measuring coding challenge competence with APPS. In NeurIPS Datasets and Benchmarks, 2021. Naman Jain, Manish Shetty, Tianjun Zhang, King Han, Koushik Sen, and Ion Stoica. R2e: Turning any github repository into a programming agent test environment. In ICLR 2024, 2024. Carlos E Jimenez, John Yang, Alexander Wettig, Shunyu Yao, Kexin Pei, Ofir Press, and Karthik Narasimhan. Swe-bench: Can language models resolve real-world github issues? ArXiv preprint, abs/2310.06770, 2023. René Just, Darioush Jalali, and Michael D. Ernst. Defects4j: a database of existing faults to enable controlled testing studies for java programs. In Proc. of ISSTA, 2014. doi: 10.1145/2610384.
2628055.
Sungmin Kang, Juyeon Yoon, and Shin Yoo. Large language models are few-shot testers: Exploring llm-based general bug reproduction. In Proc. of ICSE, 2023. doi: 10.1109/ICSE48619.2023.
00194.
11

Sungmin Kang, Juyeon Yoon, and Shin Yoo. LLM-powered test case generation for detecting tricky bugs. ArXiv preprint, abs/2404.10304, 2024. Tsz On Li, Wenxi Zong, Yibo Wang, Haoye Tian, Ying Wang, Shing-Chi Cheung, and Jeff Kramer. Nuances are the key: Unlocking chatgpt to find failure-inducing tests with differential prompting. In Proc. of ASE, 2023. doi: 10.1109/ASE56229.2023.00089. Yujia Li, David Choi, Junyoung Chung, Nate Kushman, Julian Schrittwieser, Rémi Leblond, Tom Eccles, James Keeling, Felix Gimeno, Agustin Dal Lago, Thomas Hubert, Peter Choy, Cyprien de Masson d’Autume, Igor Babuschkin, Xinyun Chen, Po-Sen Huang, Johannes Welbl, Sven Gowal, Alexey Cherepanov, James Molloy, Daniel J. Mankowitz, Esme Sutherland Robson, Pushmeet Kohli, Nando de Freitas, Koray Kavukcuoglu, and Oriol Vinyals. Competition-level code generation with alphacode. Science, 378(6624), 2022. doi: 10.1126/science.abq1158. Derrick Lin, James Koppel, Angela Chen, and Armando Solar-Lezama. Quixbugs: a multi-lingual program repair benchmark set based on the quixey challenge. In Proc. of SPLASH, 2017. doi:
10.1145/3135932.3135941.
Jiawei Liu, Chunqiu Steven Xia, Yuyao Wang, and Lingming Zhang. Is your code generated by chatgpt really correct? rigorous evaluation of large language models for code generation. In Proc. of NeurIPS, 2023a. Tianyang Liu, Canwen Xu, and Julian J. McAuley. Repobench: Benchmarking repository-level code auto-completion systems. CoRR, abs/2306.03091, 2023b. doi: 10.48550/ARXIV.2306.03091. Stephan Lukasczyk and Gordon Fraser. Pynguin: Automated unit test generation for python. In Proc. of ICSE, 2022. doi: 10.1145/3510454.3516829. OpenAI. GPT-4 technical report. ArXiv preprint, abs/2303.08774, 2023. OpenAI. GPT-4o mini: advancing cost-efficient intelligence, Jul 2024. OpenDevin. Opendevin: Code less, make more, 2024. PYPL. Pypl popularity of programming language index, Aug 2024. URL https://web.archive. org/web/20240806100838/https://pypl.github.io/PYPL.html. Stephen E. Robertson and Hugo Zaragoza. The probabilistic relevance framework: BM25 and beyond. Found. Trends Inf. Retr., 3(4), 2009. doi: 10.1561/1500000019. Max Schäfer, Sarah Nadi, Aryaz Eghbali, and Frank Tip. An empirical evaluation of using large language models for automated unit test generation. IEEE Trans. Software Eng., 50(1), 2024. doi: 10.1109/TSE.2023.3334955. Philipp Straubinger and Gordon Fraser. A survey on what developers think about testing. In 34th IEEE International Symposium on Software Reliability Engineering, ISSRE 2023, Florence, Italy, October 9-12, 2023, pp. 80–90. IEEE, 2023. doi: 10.1109/ISSRE59848.2023.00075. URL https://doi.org/10.1109/ISSRE59848.2023.00075. Wei Tao, Yucheng Zhou, Wenqiang Zhang, and Yu Cheng. MAGIS: llm-based multi-agent framework for github issue resolution. CoRR, abs/2403.17927, 2024. doi: 10.48550/ARXIV.2403.
17927.
MistralAI Team. Cheaper, Better, Faster, Stronger - Continuing to push the frontier of AI and making it accessible to all., Apr 2024a. MistralAI Team. Large enough, Jul 2024b. TIOBE.

Tiobe index for august 2024, Aug 2024.

URL https://web.archive.org/web/

20240807025036/https://www.tiobe.com/tiobe-index/.

TogetherAI. Together AI API, 2023. Michele Tufano, Dawn Drain, Alexey Svyatkovskiy, Shao Kun Deng, and Neel Sundaresan. Unit test case generation with transformers. ArXiv preprint, abs/2009.05617, 2020. 12

Lei Wang, Chen Ma, Xueyang Feng, Zeyu Zhang, Hao Yang, Jingsen Zhang, Zhiyuan Chen, Jiakai Tang, Xu Chen, Yankai Lin, Wayne Xin Zhao, Zhewei Wei, and Jirong Wen. A survey on large language model based autonomous agents. Frontiers Comput. Sci., 2024. John Yang, Carlos E. Jimenez, Alexander Wettig, Kilian Lieret, Shunyu Yao, Karthik Narasimhan, and Ofir Press. SWE-agent: Agent Computer Interfaces Enable Software Engineering Language Models, 2024. Ye Yang, Mei He, Mingshu Li, Qing Wang, and Barry W. Boehm. Phase distribution of software development effort. In Proc. of ESEM, 2008. doi: 10.1145/1414004.1414016. Yuntong Zhang, Haifeng Ruan, Zhiyu Fan, and Abhik Roychoudhury. Autocoderover: Autonomous program improvement. CoRR, abs/2404.05427, 2024. doi: 10.48550/ARXIV.2404.05427.

13

1 diff 2 < path or filename > 3 < "rewrite" or "insert" > 4 < line number / EOF / BOF > 5 < function to rewrite or insert > 6 end diff 7 < repeat as necessary >

**Figure 7: The Custom Diff format for Z ERO S HOT P LUS**

A

Formalization of Custom Prompt Format for Z ERO S HOT P LUS

We introduce a custom prompt format for language models to aid them with patch generation in the zero-shot setting. The format is visualized in Fig. 7 similar to how it is provided to the language model. A full example of applying the format on two files is part of the full prompt of Z ERO S HOTP LUS in Figs. 11 and 12. A diff block must start and end with diff and end diff respectively. The first line inside the block must specify an existing file for rewrites and may point to a new file in the case of insertion. Next, the language model specifies whether it intends to rewrite an existing function or insert a new function. If no exact match of the function name is found, we employ a fuzzy search using the line number or EOF/BOF as an indicator for where to look for the existing functions. EOF and BOF are particularly useful for inserting new functions. We note that diff blocks can be repeated an arbitrary number of times.

B

Adapting LIBRO to our Setting

Kang et al. (Kang et al., 2023) originally proposed LIBRO for an evaluation in a pass@k setting. There, it is useful to rank all generated tests to improve performance at k > 1. As we only consider pass@1, we drop ranking components irrelevant for the top-1 test in our reimplementation. Further, LIBRO includes heuristics for importing missing dependencies and inserting tests into the correct classes. While effective in Java, this is superfluous for Python, where tests can be added outside classes and dependency imports are (empirically) correctly generated by the LLM. We thus also drop these components. LIBRO clusters test cases based on whether the generated execution trace matches the issue description. As exact matching is often not applicable for the unstructured issue descriptions, we measure the similarity between the error message and the issue description by extracting the execution trace of the generated test cases and querying the same LLM used for test generation to judge whether they relate to the same issue. Depending on its answer, we obtain two clusters and choose the shortest result of the preferred cluster.

C

Hyperparameter Ablations

C.1

Ablation on number of LIBRO samples

We perform an ablation study by varying the number of samples used for the LIBRO baseline. The result is presented in Fig. 8a. LIBRO’s performance improves as more samples are considered, however the gains of additional samples are marginal from around the 5 samples we use by default. As shown in section App. G, to enable comparison at similar cost to Code Agents, we settle for 5 samples. C.2

Ablation on Interaction Rounds for Code Agents

We analyze the number of interactions required for each Agent to submit a solution and plot the results in Fig. 8b. We observe increasing interaction rounds improve performance until saturation at 5-10 iterations (we use 20 as a default) with the only exception being AutoCodeRover, which still gains performance up to the maximum of 20 iterations we consider. 14

**Table 8: Comparison of Z ERO S HOT P LUS for different T on GPT-4 (95% CI, n = 25).**

W

T
0.0
0.2
0.4
0.7

S

89.5
89.3 ± 0.3
89.9 ± 0.5
89.3 ± 0.4

9.4
8.8 ± 0.5
10.1 ± 0.6
8.8 ± 0.4
20

100

F →×

55.4
56.2 ± 0.5
56.8 ± 0.6
55.5 ± 0.8

F →P

10.1
9.6 ± 0.5
10.9 ± 0.6
9.7 ± 0.5

∆C all

P →P

7.2
6.0 ± 0.2
6.1 ± 0.5
6.1 ± 0.5

100

21.5
21.8 ± 0.3
22.3 ± 0.4
21.1 ± 0.6

25

SWE-AGENT SWE-AGENT + AUTO C ODE ROVER

W S

95

15

20

75

AIDER

10

85

5

25

0 10

0

S

W

90

S

W

15 50

10

80

1

2

3

4

5

6

7

8

9

5

0

5

Samples

(a) Ablation of W and S by number of LIBRO samples.

10

15

20

0

0

API Calls

5

10

15

API Calls

(b) Ablation of W and S by code agent over number of needed API calls until solution submission.

**Figure 8: Ablation on the number of samples and API calls for LIBRO and code agents resp.**

C.3

Ablation on Temperature

We run Z ERO S HOT P LUS using GPT-4 with 25 samples and analyze the performance variation for a temperature range from greedy decoding (T = 0), used for Z ERO S HOT, Z ERO S HOT P LUS and the agent settings, to T = 0.7, the setting used in LIBRO. The results are presented in Table 8. We observe a tendency of decreased performance and increasing variance in all metrics for increasing T . Moreover we observe a minimal variability among several runs of the test environment at T = 0, however much smaller than the variability due to temperature.

D

Distribution over Repositories

as

tr o dj py an go m fla at sk pl ot l py ib lin py t re test qu es t sc s se ikit ab o sp rn hi sy nx m xa py rr ay

% Success Rate (S) We compare the success rate of SWE50 AGENT for test and fix generation across repositories in Fig. 9. We observe that, 40 SWE-Bench while SWE-AGENT obtains similar suc30 SWT-Bench cess rates in both settings in three reposi20 tories, success rates vary strongly on most 10 other repositories. Indeed, there are five 0 repositories where test generation fails entirely while code repair fails on three and on only two of these both fail. Manually inspecting instances from the repositories Figure 9: Distribution of success rates across repositowhere test generation fails shows a variety ries for SWE-AGENT. of reasons, astropy usually features complex computations where unit test creation is difficult, requests features a highly complex code base, flask has extremely long golden test lengths indicating particularly challenging testing problems. For pylint generated tests are all P → P making them correct but unhelpful.

E

Full prompts

Z ERO S HOT, Z ERO S HOT P LUS and LIBRO The full prompt for Z ERO S HOT is displayed in Figs. 10 and 11. The full prompt for Z ERO S HOT P LUS and LIBRO is displayed in Figs. 12 and 13. Except for the way we include files, all lines are changed with respect to the setting in SWE-B ENCH. 15

20

**Table 9: Cost of different LLMs running SWE-AGENT on SWT-B ENCH Lite in USD**

Model

GPT-4

Haiku

Mixtral 8x22B

Mistral Large 2

Sonnet

GPT-4o mini

Cost

290.71

10.28

67.90

211.34

263.13

8.43

**Table 10: Cost of running different methods on SWT-B ENCH Lite using GPT-4 in USD**

Method Z ERO S HOT Z ERO S HOT P LUS PASS @5 LIBRO Cost

82.13

80.70

403.65

420.14

Method

AIDER

AUTO C ODE ROVER

SWE-AGENT

SWE-AGENT +

Cost

256.10

368.40

290.71

478.21

This includes in particular the demonstration of the unified diff format on an example. In the setting for Table 5 we add the lines highlighted in boldface. SWE-AGENT and SWE-AGENT + The prompt for SWE-AGENT and SWE-AGENT + is shown in Fig. 14. Changes with respect to the prompt of (Jimenez et al., 2023) are highlighted in boldface. The additional changes for SWE-AGENT + are highlighted in green. We only minimally adapt the provided evaluation harness for AIDER on SWE-B ENCH1 . In this harness, AIDER is provided with a single initial user prompt based on the user issue, while the entire agent workflow remains unchanged. We provide the entire prompt in Fig. 16 and highlight our change in boldface. AIDER

AUTO C ODE ROVER AUTO C ODE ROVER (Zhang et al., 2024) leverages a number of prompts that are provided to the model in different phases of the code/test generation process. We adapt the key prompts and display them in Fig. 15. Changes are highlighted in boldface. Further, we change every occurrence of "bug location" in the original prompts to "relevant location". We further add a function to the ACI that allows inserting code in new files and fetching the entire code (capped at the first 100 lines) of any file.

F

Licenses of used Code

We adapt code from the following projects in our work and include the respective licenses:
1. SWE-B ENCH (Jimenez et al., 2023): MIT License
2. SWE-AGENT (Yang et al., 2024): MIT License
3. AIDER (Aider, 2024): Apache License 2.0
4. AUTO C ODE ROVER (Zhang et al., 2024): GNU General Public License
For all licenses of the repositories used in SWT-B ENCH, we refer to Jiminez et al. (Jimenez et al., 2023), which contains a detailed list with licenses for each repository included.

G

Computational cost

There is cost to both running inference on Language Models and on evaluation their predictions on the test suites of the repositories. Since the evaluation can be performed on a consumer grade machine in reasonable time, we focus on the cost inferred from LLM inference. We report the cost for each setting in Tables 9 and 10, displaying the average cost of a full inference on SWT-B ENCH Lite for each model and method. The difference between cost of PASS @5 and LIBRO is just the additional filtering step incurred by LIBRO. 1

https://github.com/paul-gauthier/aider-swe-bench

16

**Table 11: Average execution time t per instance**

Method t

H

Z ERO S HOT P LUS
12.6s

LIBRO

2m52s

SWE-AGENT 3m42s

SWE-AGENT + 4m25s

AUTO C ODE ROVER 5m1s

Execution times

We run the different methods from Table 2 on 5 instances and compute the average execution time. For all LLMs we consider, part of the execution time is directly related to the number of tokens digested and generated (see Table 10). For methods that require interaction with an execution environment however, time is usually dominated by setting up such an environment in a clean and reproducible manner (i.e. dockerized). We list results on execution times in Table 11 and observe that all methods except zero-shot inference take between 3-5 minutes per instance, where we can observe a small trade off due to many-turn interactions in Code Agents versus single-shot execution in LIBRO. Given these small differences however, we believe execution time to be of limited practical relevance as issues can be processed in the background, similar to continuous integration, in response to raised user issues

17

1 The following text contains a user issue (in <issue/> brackets) posted at a repository.

Further, you are provided with file contents of several files in the repository that contain relevant code (in <code> brackets). It may be necessary to use code from third party dependencies or files not contained in the attached documents however. Your task is to identify the issue and implement a test case that verifies a proposed solution to this issue. More details at the end of this text. 2 3 <issue> 4 user issue comes here 5 </issue> 6 7 retrieval results or oracle files come here 8 9 Please generate test cases that check whether an implemented solution 10 resolves the issue of the user (at the top, within <issue/> brackets). 11 Present the test cases in unified diff formatting. 12 13 The general format of a diff is the unified output format, described as follows. 14 The unified output format starts with a two-line header, which looks like this: 15 16 --- from-file 17 +++ to-file 18 19 Next come one or more hunks of differences; each hunk shows one area where the files

differ. Unified format hunks look like this: 20 21 @@ from-file-line-numbers to-file-line-numbers @@ 22 23

line-from-either-file line-from-either-file

24 25 If a hunk contains just one line, only its start line number appears. Otherwise its line

numbers look like 'start,count'. An empty hunk is considered to start at the line that follows the hunk. 26 27 If a hunk and its context contain two or more lines, its line numbers look like 'start,

count'. Otherwise only its end line number appears. An empty hunk is considered to end at the line that precedes the hunk. 28 29 The lines common to both files begin with a space character. The lines that actually

differ between the two files have one of the following indicator characters in the left print column: 30 31 '+' A line was added here to the first file. 32 '-' A line was removed here from the first file. 33 34 Insertion can only be done at the end or beginning of the file, indicated by EOF or BOF

respectively. 35 36 As an example for a diff, consider the following two versions of the same file, once

before and once after a change. 37 The original version of the file was as follows. 38 [start of demo/test_file.py] 39 1 def test_euclidean(a, b): 40 2 41 3 42 4 43 5

assert euclidean(0, 0) == 0 assert euclidean(0, 1) == 1 assert euclidean(1, 0) == 1 assert euclidean(1, 1) == 1

44 6 45 7 @pytest.mark.parametrize("a, b, expected", [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1)

]) 46 8 def test_gcd(a, b): 47 9

assert gcd(a, b) == expected

48 10 49 [end of demo/file.py]

**Figure 10: Part 1 of the Prompt for Z ERO S HOT on SWT-B ENCH**

18

1 2 The diff for fix in function euclidean and adds the function gcd is as follows. 3 This diff changes the first file into the second file. 4

```diff

5 --- a/demo/file.py 6 +++ a/demo/file.py 7 @@ -4,4 +4,5 @@ 8 9 10 +

assert euclidean(1, 0) == 1 assert euclidean(1, 1) == 1 assert euclidean(100, 10) == 10

11

@pytest.mark.parametrize("a, b, expected", [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1) ]) 13 @@ -9,2 +10,6 @@ 14 assert gcd(a, b) == expected 12

15 16 +@pytest.mark.parametrize("a, b, expected", [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1),

(100, 10, 10)]) 17 +def test_lcm(a, b): 18 +

assert lcm(a, b) == expected

19 + 20

```

21 22 The new version of the file is as follows. 23 [start of demo/file.py] 24 1 def test_euclidean(a, b): 25 2 26 3 27 4 28 5 29 6

assert euclidean(0, 0) == 0 assert euclidean(0, 1) == 1 assert euclidean(1, 0) == 1 assert euclidean(1, 1) == 1 assert euclidean(100, 10) == 10

30 7 31 8 @pytest.mark.parametrize("a, b, expected", [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1)

]) 32 9 def test_gcd(a, b): 33 10

assert gcd(a, b) == expected

34 11 35 12 @pytest.mark.parametrize("a, b, expected", [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1,

1), (100, 10, 10)]) 36 13 def test_lcm(a, b): 37 14

assert lcm(a, b) == expected

38 15 39 [end of demo/file.py] 40 41 As you can see, you need to indicate the approximate line numbers, function name and the

path and file name you want to change, 42 but there can be as many independent blocks of changes as you need. You may also apply

changes to several files. 43 Apply as much reasoning as you please and see necessary. The format of the solution is

fixed and has to follow the custom diff format. 44 Make sure to implement only test cases and don't try to fix the issue itself.

**Figure 11: Part 2 of the Prompt for Z ERO S HOT on SWT-B ENCH**

19

1 The following text contains a user issue (in <issue/> brackets) posted at a repository.

Further, you are provided with file contents of several files in the repository that contain relevant code (in <code> brackets). It may be necessary to use code from third party dependencies or files not contained in the attached documents however. Your task is to identify the issue and implement a test case that verifies a proposed solution to this issue. More details at the end of this text. 2 3 <issue> 4 user issue comes here 5 </issue> 6 7 The following patch has been proposed to fix the issue described in the user issue (in

<issue/> brackets).The patch might give you a hint on how to write a covering test for the issue, but you should not assume that the patch is correct.It might be that the provided patch is not correct, so your test should check whether the patch resolves the issue.<patch>proposed patch</patch> 8 9 retrieval results or oracle files come here 10 11 Please generate test cases that check whether an implemented solution 12 resolves the issue of the user (at the top, within <issue/> brackets). 13 Present the test cases as a diff (custom format, explained below). 14 15 The general format of a diff is as follows. 16

```custom-diff

17 diff 18 <path/filename> 19 < "rewrite" or "insert" > 20 < rough line number / EOF / BOF > 21 < insert function that should be added or rewritten > 22 end diff 23 < repeat blocks of diff as necessary > 24

```

25 Insertion can only be done at the end or beginning of the file, indicated by EOF or BOF

respectively. 26 27 As an example for a diff, consider the following two versions of the same file, once

before and once after a change. 28 The original version of the file was as follows. 29 [start of demo/test_file.py] 30 1 def test_euclidean(a, b): 31 2 32 3 33 4 34 5

assert euclidean(0, 0) == 0 assert euclidean(0, 1) == 1 assert euclidean(1, 0) == 1 assert euclidean(1, 1) == 1

35 6 36 7 @pytest.mark.parametrize("a, b, expected", [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1)

]) 37 8 def test_gcd(a, b): 38 9

assert gcd(a, b) == expected

39 10 40 [end of demo/file.py] 41

```

**Figure 12: Part 1 of the Prompt for Z ERO S HOT P LUS on SWT-B ENCH**

20

1 The diff for fix in function euclidean and adds the function gcd is as follows. 2 This diff changes the first file into the second file. 3

```custom-diff

4 diff 5 demo/file.py 6 rewrite 7 1 8 def test_euclidean(a, b): 9 10 11 12 13 14 15 16 17 18 19 20 21 22

assert euclidean(0, 0) == 0 assert euclidean(0, 1) == 1 assert euclidean(1, 0) == 1 assert euclidean(1, 1) == 1 assert euclidean(100, 10) == 10 end diff diff demo/file.py insert EOF @ pytest.mark.parametrize("a, b, expected", [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1), (100, 10, 10)]) def test_lcm(a, b): assert lcm(a, b) == expected end diff

23 24 The new version of the file is as follows. 25 [start of demo/file.py] 26 1 def test_euclidean(a, b): 27 2 28 3 29 4 30 5 31 6

assert euclidean(0, 0) == 0 assert euclidean(0, 1) == 1 assert euclidean(1, 0) == 1 assert euclidean(1, 1) == 1 assert euclidean(100, 10) == 10

32 7 33 8 @pytest.mark.parametrize("a, b, expected", [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1)

]) 34 9 def test_gcd(a, b): 35 10

assert gcd(a, b) == expected

36 11 37 12 @pytest.mark.parametrize("a, b, expected", [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1,

1), (100, 10, 10)]) 38 13 def test_lcm(a, b): 39 14

assert lcm(a, b) == expected

40 15 41 [end of demo/file.py] 42 43 As you can see, you need to indicate the approximate line numbers, function name and the

path and file name you want to change, 44 but there can be as many independent blocks of changes as you need. You may also apply

changes to several files. 45 Apply as much reasoning as you please and see necessary. The format of the solution is

fixed and has to follow the custom diff format. 46 Make sure to implement only test cases and don't try to fix the issue itself.

**Figure 13: Part 2 of the Prompt for Z ERO S HOT P LUS on SWT-B ENCH**

21

1 We have received following issue within our repository. Here's the issue text: 2 ISSUE: 3 {issue} 4 5 INSTRUCTIONS: 6 Now, you’re going to create unit tests that cover the issue.

7

8 9 10

In other words, you should write unit tests that fail in the current state of the repositorybut will pass when the issue has been resolved. Essentially, you’ll want to write a unit test that reproduces the described issue. Your terminal session has started and you're in the repository's root directory. You can use any bash commands or the special interface to help you. Edit all the files you need to and run any checks or tests that you want. Remember, YOU CAN ONLY ENTER ONE COMMAND AT A TIME. You should always wait for feedback after every command. When you're satisfied with all of the changes you've made, you can submit your changes to the code base by simply running the submit command. Note however that you cannot use any interactive session commands (e.g. python, vim) in this environment, but you can write scripts and run them. E.g. you can write a python script and then run it with `python <script_name>.py`.

11 12 NOTE ABOUT THE EDIT COMMAND: Indentation really matters! When editing a file, make sure

to insert appropriate indentation before each line! 13 14 IMPORTANT TIPS: 15 1. Always start by trying to replicate the bug that the issues discusses. 16

17 18

If the issue includes code for reproducing the bug, we recommend that you reimplement that in your environment, and run it to make sure you can reproduce the bug. Then start trying to fix it. When you think you've fixed the bug, re-run the bug reproduction script to make sure that the bug has indeed been fixed.

19 20

21

If the bug reproduction script does not print anything when it successfully runs, we recommend adding a print("Script completed successfully, no errors.") command at the end of the file, so that you can be sure that the script indeed ran fine all the way through.

22 23 2. If you run a command and it doesn't work, try running a different command. A command

that did not work once will not work the second time unless you modify it! 24 25 3. If you open a file and need to get to an area around a specific line that is not in

the first 100 lines, say line 583, don't just use the scroll_down command multiple times. Instead, use the goto 583 command. It's much quicker. 26 27 4. If the bug reproduction script requires inputting/reading a specific file, such as

buggy-input.png, and you'd like to understand how to input that file, conduct a search in the existing repo code, to see whether someone else has already done that. Do this by running the command: find_file "buggy-input.png" If that doesn't work, use the linux 'find' command. 28 29 5. Always make sure to look at the currently open file and the current working directory

(which appears right after the currently open file). The currently open file might be in a different directory than the working directory! Note that some commands, such as 'create', open files, so they might change the current open file. 30 31 6. When editing files, it is easy to accidentally specify a wrong line number or to

write code with incorrect indentation. Always check the code after you issue an edit to make sure that it reflects what you wanted to accomplish. If it didn't, issue another command to fix it. 32 33 7.

After having applied your changes and before submitting, make sure to run pytest and check if the code *fails* as expected due to the issue description. If it doesn’t, revisit your code changes and adapt them accordingly.

**Figure 14: The Prompt for SWE-AGENT on SWT-B ENCH**

22

1 You are a software developer maintaining a large project. 2 You are working on an issue submitted to your project. 3 The issue contains a description marked between <issue> and </issue>. 4 Your task is to invoke a few search API calls to gather information about relevant code

lines, then write unit tests to capture the described behaviour in the issue.Ideally, the unit tests should fail before the bug is fixed or the requested feature is added, and pass after.Note you are not trying to solve the bug itself, but just capture the behaviour described in the issue by creating appropriate test cases. 1 You are a software developer maintaining a large project. 2 You are working on an issue submitted to your project. 3 The issue contains a description marked between <issue> and </issue>. 4 You ultimate goal is to write one or more unit tests that capture this issue.Ideally,

the unit tests should fail before the bug is fixed or the requested feature is added, and pass after.Note you are not trying to solve the bug itself, but just capture the behaviour described in the issue by creating appropriate test cases.

1 Write one or more unit tests for the issue, based on the retrieved context. 2 3 You can import necessary libraries. 4 5 6 Return the tests as patch in the format below. 7 8 Within `<file></file>`, replace `...` with actual file path. 9 10 Within `<original></original>`, replace `...` with the original code snippet from the

program. 11 12 Within `<patched></patched>`, replace `...` with the fixed version of the original code.

When adding orignal code and updated code, pay attention to indentation, as the code is in Python. 13 You can write multiple modifications if needed. 14 15

```

16 # modification 1 17 <file>...</file> 18 <original>...</original> 19 <patched>...</patched> 20 21 # modification 2 22 <file>...</file> 23 <original>...</original> 24 <patched>...</patched> 25 26 # modification 3 27 ... 28

```

**Figure 15: The Prompt for AUTO C ODE ROVER on SWT-B ENCH**

23

1 Below is a real GitHub issue from a popular GitHub repository. 2 The issue was filed some time ago. 3 The repo has been checked out at the commit that existed at the moment the issue was

filed. 4 If you are already familiar with this repo, be cautious! 5 You are working with an old version of the repo! 6 Filenames, directory names, file contents, etc may be different than what you're used to

. 7 8 Propose changes to update the repo to reproduce the problem below. 9 You’re going to create unit tests that cover the issue.

In other words, you should write unit tests that fail in the current state of the repository 10 but will pass when the issue has been resolved. Essentially, you’ll want to write a unit test that reproduces the described issue. 11 12 13 {issue}

**Figure 16: The Prompt for AIDER on SWT-B ENCH**

24

