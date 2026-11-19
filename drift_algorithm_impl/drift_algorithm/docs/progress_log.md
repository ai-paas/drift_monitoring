# Drift Algorithm Progress Log

## 2026-06-25

### Documentation Scaffold

Created the initial `drift_algorithm/` documentation scaffold.

Files added:

- `drift_algorithm/README.md`
- `drift_algorithm/docs/README.md`
- `drift_algorithm/docs/catalog_sources.md`
- `drift_algorithm/docs/input_output_contracts.md`
- `drift_algorithm/docs/implementation_guide.md`
- `drift_algorithm/docs/schema_overview.md`
- `drift_algorithm/docs/method_design_template.md`
- `drift_algorithm/docs/schemas/*.md`
- `drift_algorithm/docs/method_designs/DM-*.md`
- `drift_algorithm/tools/generate_method_design_docs.py`

Manager review:

- confirmed `drift_methods_catalog.md` is the authoritative method source
- confirmed 56 method design documents were generated
- confirmed `generic_fallback_algorithm_variants.md` is excluded from method count
- spot-checked KS, MMD, HAT, and DriftRetrainingClassifier schema classification
- verified generator syntax with `python -m py_compile`

Decision:

```text
accepted as documentation scaffold
```

### Workflow Documentation

Added implementation workflow and manager review rules.

Files added:

- `drift_algorithm/docs/implementation_workflow.md`
- `drift_algorithm/docs/progress_log.md`

Manager decision:

```text
workflow accepted for subsequent work
```

Next candidate:

```text
DM-001 KS Test design detail and first implementation loop
```

### DM-001 KS Test Design Detail

Worker updated:

- `drift_algorithm/docs/method_designs/DM-001_ks_test.md`

Manager review:

- confirmed method identity against `drift_methods_catalog.md`
- confirmed first implementation scope is numeric univariate `(time, value)`
- confirmed supported first-phase variants:
  - `TWO_SAMPLE_KS_TWO_SIDED`
  - `TWO_SAMPLE_KS_ONE_SIDED_GREATER`
  - `TWO_SAMPLE_KS_ONE_SIDED_LESS`
  - `TWO_SAMPLE_KS_EXACT_PVALUE`
  - `TWO_SAMPLE_KS_ASYMPTOTIC_PVALUE`
  - `KS_WITH_TIES_OR_DISCRETE_CAUTION`
- confirmed deferred variants return not applicable:
  - `ONE_SAMPLE_KS_KNOWN_CDF`
  - `LILLIEFORS_RELATED_ONE_SAMPLE`
  - `HIGHER_ORDER_KS`
  - `TWO_SAMPLE_KS_APPROX_QUANTILE`
- confirmed measurement mapping covers `KS_STATISTIC`, `P_VALUE`,
  `TEST_STATISTIC`, and `SAMPLE_SIZE`
- accepted concrete drift rule: `p_value < alpha`

Decision:

```text
accepted as implementation-ready
```

### DM-001 KS Test Implementation

Implemented the first code path for KS Test.

Files added:

- `drift_algorithm/__init__.py`
- `drift_algorithm/core/__init__.py`
- `drift_algorithm/core/result.py`
- `drift_algorithm/core/windows.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/batchdistributioncomparison.py`
- `tests/test_ks_test.py`

Implemented behavior:

- public `detect_ks_test` function with DataFrame input
- inclusive reference/current window slicing
- numeric value validation and invalid row filtering
- supported KS variants for two-sample tests
- deferred variant handling with `severity="not_applicable"`
- canonical measurements including `KS_STATISTIC`, `P_VALUE`,
  `TEST_STATISTIC`, and `SAMPLE_SIZE`
- tie/discrete caution path for `KS_WITH_TIES_OR_DISCRETE_CAUTION`

Checks run:

```powershell
python -m py_compile drift_algorithm\core\result.py drift_algorithm\core\windows.py drift_algorithm\methods\batchdistributioncomparison.py tests\test_ks_test.py
python -m pytest tests\test_ks_test.py -q
git diff --check
```

Check results:

```text
py_compile: passed
pytest: 6 passed
git diff --check: passed
```

Manager decision:

```text
accepted as first implementation loop
```

Next candidate:

```text
DM-002 Wasserstein Distance design detail and implementation
```

### DM-002 Wasserstein Distance Design Detail

Worker updated:

- `drift_algorithm/docs/method_designs/DM-002_wasserstein_distance.md`

Manager review:

- confirmed method identity against `drift_methods_catalog.md`
- confirmed first implementation scope is numeric univariate `(time, value)`
- accepted `WASSERSTEIN_1D_EXACT` as the first implementation target
- confirmed deferred variants:
  - `WASSERSTEIN_WINDOW_TREND`
  - `SLICED_WASSERSTEIN_EMBEDDING`
  - `WASSERSTEIN_APPROX_HISTOGRAM`
- confirmed measurement mapping covers `WASSERSTEIN_DISTANCE`,
  `DRIFT_ALARM_STATE`, `FEATURE_IMPORTANCE_OR_RANK`, and `SAMPLE_SIZE`
- accepted score-only behavior when no threshold is supplied:
  `severity="watch"` and `DRIFT_ALARM_STATE="undetermined"`

Decision:

```text
accepted as implementation-ready
```

Open design decision:

```text
No production default threshold is defined. A caller or calibration process must
provide `threshold` or `threshold_or_alpha` for binary alarm decisions.
```

### DM-002 Wasserstein Distance Implementation

Implemented the first code path for Wasserstein Distance.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/batchdistributioncomparison.py`
- `tests/test_wasserstein_distance.py`

Implemented behavior:

- public `detect_wasserstein_distance` function with DataFrame input
- `WASSERSTEIN_1D_EXACT` exact univariate calculation
- threshold-based alarm when `threshold` or `threshold_or_alpha` is supplied
- score-only watch result when threshold is absent
- optional nonnegative sample weights through SciPy
- explicit not-applicable handling for deferred variants and invalid policies
- canonical measurements including `WASSERSTEIN_DISTANCE`, `SAMPLE_SIZE`,
  `DRIFT_ALARM_STATE`, and `FEATURE_IMPORTANCE_OR_RANK`

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py tests\test_wasserstein_distance.py tests\test_ks_test.py
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py -q
git diff --check
```

Check results:

```text
py_compile: passed
pytest: 12 passed
git diff --check: passed
```

Manager decision:

```text
accepted as second implementation loop
```

Next candidate:

```text
DM-018 Mann-Whitney U / Wilcoxon Rank Sum Test design detail and implementation
```

### DM-018 Mann-Whitney U / Wilcoxon Rank Sum Test Design Detail

Worker updated:

- `drift_algorithm/docs/method_designs/DM-018_mann_whitney_u_wilcoxon_rank_sum_test.md`

Manager review:

- confirmed method identity against `drift_methods_catalog.md`
- confirmed numeric two-window `(time, value)` implementation scope
- accepted first implementation variants:
  - `MANN_WHITNEY_TWO_SIDED`
  - `MANN_WHITNEY_ONE_SIDED`
  - `MANN_WHITNEY_EXACT`
- confirmed canonical measurement mapping:
  - `TEST_STATISTIC`
  - `P_VALUE`
  - `DRIFT_ALARM_STATE`
- accepted p-value rule: `p_value < alpha`
- accepted one-sided orientation metadata because SciPy is called as
  `x=reference, y=current`

Decision:

```text
accepted as implementation-ready
```

Open design decision:

```text
`exact_max_sample_size=8` is the initial default for exact mode. Adjust later if
project calibration chooses a different cutoff.
```

### DM-018 Mann-Whitney U / Wilcoxon Rank Sum Test Implementation

Implemented Mann-Whitney U / Wilcoxon Rank Sum Test.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/batchdistributioncomparison.py`
- `tests/test_mann_whitney_u_wilcoxon_rank_sum_test.py`

Implemented behavior:

- public `detect_mann_whitney_u_wilcoxon_rank_sum_test` function
- two-sided, one-sided, and exact variants
- exact precondition handling for small tie-free samples
- p-value based drift decision
- one-sided direction aliases for current increase/decrease
- canonical measurements including `TEST_STATISTIC`, `P_VALUE`,
  `DRIFT_ALARM_STATE`, and `SAMPLE_SIZE`
- rank-biserial correlation as non-canonical effect-size helper

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_ks_test.py tests\test_wasserstein_distance.py
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py -q
git diff --check
```

Check results:

```text
py_compile: passed
pytest: 18 passed
git diff --check: passed
```

Manager decision:

```text
accepted as third implementation loop
```

Next candidate:

```text
DM-019 t-test 계열 design detail and implementation
```

### DM-019 t-test 계열 Design Detail

Worker updated:

- `drift_algorithm/docs/method_designs/DM-019_t_test.md`

Manager review:

- confirmed method identity against `drift_methods_catalog.md`
- confirmed numeric mean-shift `(time, value)` implementation scope
- accepted first implementation variants:
  - `ONE_SAMPLE_T_TEST`
  - `TWO_SAMPLE_STUDENT_T_TEST`
  - `WELCH_T_TEST`
  - `PAIRED_T_TEST`
- confirmed canonical measurement mapping:
  - `TEST_STATISTIC`
  - `P_VALUE`
  - `DRIFT_ALARM_STATE`
- accepted p-value rule: `p_value < alpha`
- accepted manager decisions:
  - one-sample may use reference-window mean as fallback baseline with warning
  - duplicate paired keys are rejected until an aggregation policy exists
  - confidence interval is optional/best-effort metadata in the first implementation

Decision:

```text
accepted as implementation-ready
```

### DM-019 t-test 계열 Implementation

Implemented t-test family.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/batchdistributioncomparison.py`
- `tests/test_t_test.py`

Implemented behavior:

- public `detect_t_test` function
- Welch default two-sample t-test
- Student equal-variance t-test
- one-sample t-test with explicit baseline or reference-mean fallback
- paired t-test with strict pair key alignment
- p-value based drift decision
- direction aliases for current increase/decrease
- canonical measurements including `TEST_STATISTIC`, `P_VALUE`,
  `DRIFT_ALARM_STATE`, and `SAMPLE_SIZE`

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py tests\test_t_test.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_ks_test.py tests\test_wasserstein_distance.py
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py -q
git diff --check
```

Check results:

```text
py_compile: passed
pytest: 25 passed
git diff --check: passed
```

Manager decision:

```text
accepted as fourth implementation loop
```

Next candidate:

```text
DM-021 Levene's Test design detail and implementation
```

### DM-021 Levene's Test Design Detail

Worker updated:

- `drift_algorithm/docs/method_designs/DM-021_levene_s_test.md`

Manager review:

- confirmed method identity against `drift_methods_catalog.md`
- confirmed numeric variance/scale `(time, value)` implementation scope
- accepted first implementation variants:
  - `LEVENE_MEAN_CENTER`
  - `BROWN_FORSYTHE_MEDIAN_CENTER`
  - `TRIMMED_MEAN_LEVENE`
- accepted default variant: `BROWN_FORSYTHE_MEDIAN_CENTER`
- confirmed canonical measurement mapping:
  - `TEST_STATISTIC`
  - `P_VALUE`
  - `DRIFT_ALARM_STATE`
- accepted p-value rule: `p_value < alpha`
- accepted first implementation limitation: only two-sided alternative

Decision:

```text
accepted as implementation-ready
```

### DM-021 Levene's Test Implementation

Implemented Levene's Test.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/batchdistributioncomparison.py`
- `tests/test_levene_s_test.py`

Implemented behavior:

- public `detect_levene_s_test` function
- mean-centered Levene, Brown-Forsythe median-centered, and trimmed-mean variants
- p-value based variance/scale drift decision
- canonical measurements including `TEST_STATISTIC`, `P_VALUE`,
  `DRIFT_ALARM_STATE`, and `SAMPLE_SIZE`
- helper measurements for reference/current variance, variance ratio, center
  policy, and centers
- explicit not-applicable handling for invalid center, one-sided alternative,
  degenerate constant windows, and invalid schema/window inputs

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py tests\test_levene_s_test.py tests\test_t_test.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_ks_test.py tests\test_wasserstein_distance.py
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py -q
git diff --check
```

Check results:

```text
py_compile: passed
pytest: 32 passed
git diff --check: passed
```

Manager decision:

```text
accepted as fifth implementation loop
```

Next candidate:

```text
DM-014 Anderson-Darling Test design detail and implementation
```

### DM-014 Anderson-Darling Test Design Detail

Worker updated:

- `drift_algorithm/docs/method_designs/DM-014_anderson_darling_test.md`

Manager review:

- confirmed method identity against `drift_methods_catalog.md`
- confirmed numeric empirical-distribution `(time, value)` implementation scope
- accepted first implementation variants:
  - `TWO_SAMPLE_ANDERSON_DARLING`
  - `TAIL_SENSITIVE_AD`
- accepted deferred variants:
  - `ONE_SAMPLE_ANDERSON_DARLING`
  - `K_SAMPLE_ANDERSON_DARLING`
- confirmed canonical measurement mapping:
  - `TEST_STATISTIC`
  - `P_VALUE`
  - `DRIFT_ALARM_STATE`
- accepted p-value rule: `p_value < alpha`
- accepted tail metadata as explanatory output only for the first
  implementation

Decision:

```text
accepted as implementation-ready
```

### DM-014 Anderson-Darling Test Implementation

Implemented Anderson-Darling Test.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/batchdistributioncomparison.py`
- `tests/test_anderson_darling_test.py`

Implemented behavior:

- public `detect_anderson_darling_test` function
- default two-sample Anderson-Darling detector using scipy `anderson_ksamp`
- tail-sensitive variant with reference-quantile tail thresholds, counts,
  rates, and deltas
- p-value based distribution drift decision
- alpha alias handling for `alpha`, `threshold_or_alpha`, and
  `significance_level`
- canonical measurements including `TEST_STATISTIC`, `P_VALUE`,
  `DRIFT_ALARM_STATE`, and `SAMPLE_SIZE`
- explicit not-applicable handling for deferred variants, invalid alpha aliases,
  invalid tail parameters, boolean value input, missing windows, and too-small
  effective samples

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py tests\test_anderson_darling_test.py
python -m pytest tests\test_anderson_darling_test.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py -q
```

Check results:

```text
py_compile: passed
DM-014 pytest: 6 passed
implemented numeric batch pytest: 38 passed
```

Manager decision:

```text
accepted as sixth implementation loop
```

Next candidate:

```text
DM-015 Cramer-von Mises Test design detail and implementation
```

### DM-015 Cramer-von Mises Test Design Detail

Worker updated:

- `drift_algorithm/docs/method_designs/DM-015_cramer_von_mises_test.md`

Manager review:

- confirmed method identity against `drift_methods_catalog.md`
- confirmed numeric empirical CDF `(time, value)` implementation scope
- accepted first implementation variant:
  - `TWO_SAMPLE_CVM`
- accepted deferred variants:
  - `ONE_SAMPLE_CVM`
  - `K_SAMPLE_CVM`
- confirmed canonical measurement mapping:
  - `TEST_STATISTIC`
  - `P_VALUE`
  - `DRIFT_ALARM_STATE`
- accepted p-value rule: `p_value < alpha`
- accepted descriptive mean/median/quartile summaries as explanatory
  measurements only

Decision:

```text
accepted as implementation-ready
```

### DM-015 Cramer-von Mises Test Implementation

Implemented Cramer-von Mises Test.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/batchdistributioncomparison.py`
- `tests/test_cramer_von_mises_test.py`

Implemented behavior:

- public `detect_cramer_von_mises_test` function
- default two-sample CvM detector using scipy `cramervonmises_2samp`
- p-value method support for `auto`, `asymptotic`, and `exact`
- p-value based numeric distribution drift decision
- alpha alias handling for `alpha`, `threshold_or_alpha`, and
  `significance_level`
- canonical measurements including `TEST_STATISTIC`, `P_VALUE`,
  `DRIFT_ALARM_STATE`, and `SAMPLE_SIZE`
- descriptive helper measurements for mean, median, quartiles, and median delta
- explicit not-applicable handling for deferred variants, one-sided
  alternatives, invalid p-value method, invalid nan/tie policies, boolean input,
  missing windows, and too-small effective samples

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py tests\test_cramer_von_mises_test.py
python -m pytest tests\test_cramer_von_mises_test.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py -q
```

Check results:

```text
py_compile: passed
DM-015 pytest: 6 passed
implemented numeric batch pytest: 44 passed
```

Manager decision:

```text
accepted as seventh implementation loop
```

Next candidate:

```text
DM-016 Kuiper's Test design detail and implementation
```

### DM-016 Kuiper's Test Design Detail

Worker updated:

- `drift_algorithm/docs/method_designs/DM-016_kuiper_s_test.md`

Manager review:

- confirmed method identity against `drift_methods_catalog.md`
- confirmed numeric empirical CDF `(time, value)` first implementation scope
- accepted first implementation variant:
  - `KUIPER_TWO_SAMPLE`
- accepted deferred variants:
  - `KUIPER_CIRCULAR_DATA`
  - `KUIPER_ONE_SAMPLE`
- confirmed canonical measurement mapping:
  - `TEST_STATISTIC`
  - `P_VALUE`
  - `DRIFT_ALARM_STATE`
- accepted local EDF statistic: `D_plus + D_minus`
- accepted default permutation p-value with plus-one correction
- accepted explicit threshold mode only when an externally calibrated statistic
  threshold is supplied

Decision:

```text
accepted as implementation-ready
```

### DM-016 Kuiper's Test Implementation

Implemented Kuiper's Test.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/batchdistributioncomparison.py`
- `tests/test_kuiper_s_test.py`

Implemented behavior:

- public `detect_kuiper_s_test` function
- default two-sample Kuiper detector using local empirical CDF gaps
- permutation p-value mode with plus-one correction, `permutation_count`, and
  `random_seed`
- threshold decision mode with explicit statistic threshold
- canonical measurements including `TEST_STATISTIC`, `P_VALUE`,
  `DRIFT_ALARM_STATE`, and `SAMPLE_SIZE`
- helper measurements for `KUIPER_D_PLUS`, `KUIPER_D_MINUS`, permutation count,
  mean, median, quartiles, and median delta
- explicit not-applicable handling for deferred variants, one-sided
  alternatives, invalid decision/p-value policies, invalid threshold, invalid
  nan/tie/circular policies, boolean input, missing windows, too-small samples,
  and permutation guardrails

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py tests\test_kuiper_s_test.py
python -m pytest tests\test_kuiper_s_test.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py -q
```

Check results:

```text
py_compile: passed
DM-016 pytest: 6 passed
implemented numeric batch pytest: 50 passed
```

Manager decision:

```text
accepted as eighth implementation loop
```

Next candidate:

```text
DM-017 Baumgartner-Weiss-Schindler Test design detail and implementation
```

### DM-017 Baumgartner-Weiss-Schindler Test Design Detail

Worker updated:

- `drift_algorithm/docs/method_designs/DM-017_baumgartner_weiss_schindler_test.md`

Manager review:

- confirmed method identity against `drift_methods_catalog.md`
- confirmed numeric rank-based `(time, value)` first implementation scope
- accepted first implementation variants:
  - `BWS_TWO_SAMPLE`
  - `BWS_RANK_BASED`
- accepted deferred variant:
  - `BWS_EXACT_OR_ASYMPTOTIC`
- confirmed canonical measurement mapping:
  - `TEST_STATISTIC`
  - `P_VALUE`
  - `DRIFT_ALARM_STATE`
- accepted local rank-based statistic and average-rank tie handling
- accepted default permutation p-value with plus-one correction
- accepted explicit threshold mode only when an externally calibrated statistic
  threshold is supplied

Decision:

```text
accepted as implementation-ready
```

### DM-017 Baumgartner-Weiss-Schindler Test Implementation

Implemented Baumgartner-Weiss-Schindler Test.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/batchdistributioncomparison.py`
- `tests/test_baumgartner_weiss_schindler_test.py`

Implemented behavior:

- public `detect_baumgartner_weiss_schindler_test` function
- default two-sample BWS detector using local rank-based statistic
- `BWS_RANK_BASED` alias-style supported variant using the same backend
- permutation p-value mode with plus-one correction, `permutation_count`, and
  `random_seed`
- threshold decision mode with explicit statistic threshold
- canonical measurements including `TEST_STATISTIC`, `P_VALUE`,
  `DRIFT_ALARM_STATE`, and `SAMPLE_SIZE`
- helper measurements for `BWS_REFERENCE_COMPONENT`,
  `BWS_CURRENT_COMPONENT`, permutation count, mean, median, quartiles, and
  median delta
- explicit not-applicable handling for exact/asymptotic variant and p-value
  methods, invalid decision/p-value policies, invalid threshold, invalid
  nan/tie policies, boolean input, missing windows, too-small samples, and
  permutation guardrails

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py tests\test_baumgartner_weiss_schindler_test.py
python -m pytest tests\test_baumgartner_weiss_schindler_test.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py -q
```

Check results:

```text
py_compile: passed
DM-017 pytest: 7 passed
implemented numeric batch pytest: 57 passed
```

Manager decision:

```text
accepted as ninth implementation loop
```

Next candidate:

```text
DM-020 F-test / Variance Test 계열 design detail and implementation
```

### DM-020 F-test / Variance Test 계열 Design Detail

Worker updated:

- `drift_algorithm/docs/method_designs/DM-020_f_test_variance_test.md`

Manager review:

- confirmed method identity against `drift_methods_catalog.md`
- confirmed numeric variance `(time, value)` first implementation scope
- accepted first implementation variant:
  - `F_TEST_EQUAL_VARIANCE`
- accepted deferred variants:
  - `ANOVA_F_TEST_GROUP_MEAN`
  - `MODEL_COMPARISON_F_TEST`
- confirmed canonical measurement mapping:
  - `TEST_STATISTIC`
  - `P_VALUE`
  - `DRIFT_ALARM_STATE`
- accepted `VARIANCE_RATIO = current_variance / reference_variance`
- accepted `scipy.stats.f` CDF/SF p-value backend
- accepted alternatives: two-sided, current variance greater, current variance
  less

Decision:

```text
accepted as implementation-ready
```

### DM-020 F-test / Variance Test 계열 Implementation

Implemented F-test / Variance Test 계열.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/batchdistributioncomparison.py`
- `tests/test_f_test_variance_test.py`

Implemented behavior:

- public `detect_f_test_variance_test` function
- default equal-variance F-test for reference/current numeric windows
- two-sided symmetric p-value and one-sided current-greater/current-less
  alternatives
- canonical measurements including `TEST_STATISTIC`, `P_VALUE`,
  `DRIFT_ALARM_STATE`, and `SAMPLE_SIZE`
- helper measurements for reference/current variance, variance ratios, degrees
  of freedom, means, and standard deviations
- explicit not-applicable handling for deferred ANOVA/model-comparison variants,
  invalid alternatives, invalid p-value method, invalid variance-ratio policy,
  boolean input, missing windows, and too-small samples
- explicit error result for degenerate zero-variance calculation failure

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py tests\test_f_test_variance_test.py
python -m pytest tests\test_f_test_variance_test.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py -q
```

Check results:

```text
py_compile: passed
DM-020 pytest: 7 passed
implemented numeric batch pytest: 64 passed
```

Manager decision:

```text
accepted as tenth implementation loop
```

Next candidate:

```text
DM-022 Energy Distance design detail and implementation
```

### DM-022 Energy Distance Design Detail

Worker updated:

- `drift_algorithm/docs/method_designs/DM-022_energy_distance.md`

Manager review:

- confirmed method identity against `drift_methods_catalog.md`
- confirmed univariate numeric distance `(time, value)` first implementation
  scope
- accepted first implementation variants:
  - `UNIVARIATE_ENERGY_DISTANCE`
  - `ENERGY_DISTANCE_PERMUTATION_TEST`
- accepted deferred variant:
  - `MULTIVARIATE_ENERGY_DISTANCE`
- confirmed canonical measurement mapping:
  - `TEST_STATISTIC`
  - `P_VALUE`
  - `DRIFT_ALARM_STATE`
- accepted `scipy.stats.energy_distance` backend
- accepted distance-only default with `watch`/`undetermined` when no threshold
  is supplied
- accepted threshold rule `energy_distance > threshold`
- accepted permutation p-value with add-one correction and strict
  `p_value < alpha`

Decision:

```text
accepted as implementation-ready
```

### DM-022 Energy Distance Implementation

Implemented Energy Distance.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/batchdistributioncomparison.py`
- `tests/test_energy_distance.py`

Implemented behavior:

- public `detect_energy_distance` function
- default univariate Energy distance using scipy `energy_distance`
- distance-only mode returning `severity="watch"` and
  `DRIFT_ALARM_STATE="undetermined"` when no threshold is supplied
- threshold mode with strict `distance > threshold`
- permutation p-value variant with add-one correction, `permutation_count`, and
  `random_seed`
- canonical measurements including `TEST_STATISTIC`, `P_VALUE`,
  `DRIFT_ALARM_STATE`, and `SAMPLE_SIZE`
- helper measurements for `ENERGY_DISTANCE`, permutation metadata, mean,
  median, quartiles, and median delta
- explicit not-applicable handling for multivariate variant, invalid distance
  metric, invalid p-value method, invalid threshold/alpha policies, boolean
  input, missing windows, and too-small samples

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py tests\test_energy_distance.py
python -m pytest tests\test_energy_distance.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py -q
```

Check results:

```text
py_compile: passed
DM-022 pytest: 6 passed
implemented numeric batch pytest: 70 passed
```

Manager decision:

```text
accepted as eleventh implementation loop
```

Next candidate:

```text
DM-023 Epps-Singleton Test design detail and implementation
```

### DM-023 Epps-Singleton Test Design Detail

Worker updated:

- `drift_algorithm/docs/method_designs/DM-023_epps_singleton_test.md`

Manager review:

- confirmed method identity against `drift_methods_catalog.md`
- confirmed univariate numeric two-sample `(time, value)` first implementation
  scope
- accepted first implementation variants:
  - `TWO_SAMPLE_EPPS_SINGLETON`
  - `DISCRETE_EPPS_SINGLETON`
- accepted deferred variant:
  - `ASYMPTOTIC_EPPS_SINGLETON`
- confirmed canonical measurement mapping:
  - `TEST_STATISTIC`
  - `P_VALUE`
  - `DRIFT_ALARM_STATE`
- accepted scipy `epps_singleton_2samp` backend
- accepted default `t_points=(0.4, 0.8)` and strict `p_value < alpha`
  decision rule

Decision:

```text
accepted as implementation-ready
```

### DM-023 Epps-Singleton Test Implementation

Implemented Epps-Singleton Test.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/batchdistributioncomparison.py`
- `tests/test_epps_singleton_test.py`

Implemented behavior:

- public `detect_epps_singleton_test` function
- default two-sample Epps-Singleton detector using scipy
  `epps_singleton_2samp`
- numeric `DISCRETE_EPPS_SINGLETON` variant with discrete/tie metadata
- deferred `ASYMPTOTIC_EPPS_SINGLETON` named screening variant
- canonical measurements including `TEST_STATISTIC`, `P_VALUE`,
  `DRIFT_ALARM_STATE`, and `SAMPLE_SIZE`
- helper measurements for `EPPS_SINGLETON_STATISTIC`, `T_POINTS`, unique
  ratios, mean/median/quartile summaries, mean delta, and discrete top-value
  frequencies
- explicit not-applicable handling for invalid t-points, unsupported p-value
  methods, deferred asymptotic variant, boolean input, missing windows, and
  too-small samples

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py tests\test_epps_singleton_test.py
python -m pytest tests\test_epps_singleton_test.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py -q
```

Check results:

```text
py_compile: passed
DM-023 pytest: 6 passed
implemented numeric batch pytest: 76 passed
```

Manager decision:

```text
accepted as twelfth implementation loop
```

Next candidate:

```text
DM-024 MMD design detail and implementation
```

### DM-024 MMD Design Detail

Worker updated:

- `drift_algorithm/docs/method_designs/DM-024_mmd.md`

Manager review:

- confirmed method identity against `drift_methods_catalog.md`
- accepted univariate numeric `(time, value)` first implementation scope even
  though the catalog also covers vector/embedding MMD
- accepted first implementation variants:
  - `KERNEL_MMD_BIASED`
  - `KERNEL_MMD_UNBIASED`
- accepted deferred variants:
  - `LINEAR_TIME_MMD`
  - `STREAMING_MMD`
- confirmed canonical measurement mapping:
  - `TEST_STATISTIC`
  - `P_VALUE`
  - `DRIFT_ALARM_STATE`
- accepted NumPy RBF kernel implementation
- accepted median-heuristic bandwidth default
- accepted score-only default with `watch`/`undetermined` when no threshold is
  supplied
- accepted permutation p-value with add-one correction and strict
  `p_value < alpha`

Decision:

```text
accepted as implementation-ready
```

### DM-024 MMD Implementation

Implemented MMD.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/batchdistributioncomparison.py`
- `tests/test_mmd.py`

Implemented behavior:

- public `detect_mmd` function
- default `KERNEL_MMD_BIASED` RBF squared MMD
- `KERNEL_MMD_UNBIASED` with signed finite-sample statistic preserved
- median heuristic, fixed bandwidth, and gamma bandwidth policies
- score-only mode returning `severity="watch"` and
  `DRIFT_ALARM_STATE="undetermined"` when no threshold is supplied
- threshold mode with strict `mmd_score > threshold`
- permutation p-value mode with add-one correction, fixed observed bandwidth,
  `permutation_count`, and `random_seed`
- canonical measurements including `TEST_STATISTIC`, `P_VALUE`,
  `DRIFT_ALARM_STATE`, and `SAMPLE_SIZE`
- helper measurements for `MMD_STATISTIC`, `MMD_SQUARED`, kernel metadata,
  permutation metadata, mean/median/quartile summaries, and deltas
- explicit not-applicable handling for deferred linear/streaming variants,
  multivariate/embedding requests, invalid kernel/bandwidth policies, invalid
  threshold/alpha policies, boolean input, missing windows, too-small samples,
  and unresolved median bandwidth

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py tests\test_mmd.py
python -m pytest tests\test_mmd.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py -q
```

Check results:

```text
py_compile: passed
DM-024 pytest: 6 passed
implemented numeric batch pytest: 82 passed
```

Manager decision:

```text
accepted as thirteenth implementation loop
```

Next candidate:

```text
DM-025 Least-Squares Density Difference design detail and implementation
```

## 2026-06-25 - DM-025 LSDD Implementation Loop

### Worker Output

Worker prepared detailed design for:

- `drift_algorithm/docs/method_designs/DM-025_lsdd.md`

Key design conclusions:

- first implementation scope is scalar numeric `(time, value)` windows
- default variant is `LEAST_SQUARES_DENSITY_DIFFERENCE`
- supported optional p-value policy is `PERMUTATION_LSDD`
- `LSDD_WITH_PREPROCESSING`, multivariate feature matrices, and embeddings are
  deferred
- default behavior is score-only with `drift_detected=None` and
  `DRIFT_ALARM_STATE="undetermined"` unless threshold or permutation mode is
  requested
- default kernel policy is RBF with median bandwidth, quantile centers,
  `n_centers=min(100, pooled_n)`, and `regularization_lambda=0.001`
- permutation p-value uses fixed observed centers/bandwidth, add-one
  correction, and strict `p_value < alpha`

### Manager Review

Manager reviewed the DM-025 design and accepted it with these constraints:

- implement direct RBF-center least-squares density difference, not a generic
  KDE/grid approximation
- keep the public API aligned with existing batch distribution methods
- reject preprocessing, feature matrix, embedding, and array-like scalar-column
  requests explicitly as `not_applicable`
- preserve score-only semantics by not fabricating p-values
- keep permutation mode deterministic with `random_seed`

Decision:

```text
accepted as implementation-ready
```

### DM-025 LSDD Implementation

Implemented LSDD.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/batchdistributioncomparison.py`
- `tests/test_lsdd.py`

Implemented behavior:

- public `detect_lsdd` function
- default `LEAST_SQUARES_DENSITY_DIFFERENCE` scalar numeric detector
- optional `PERMUTATION_LSDD` mode via variant selector or
  `p_value_method="permutation"`
- RBF basis score with median or fixed bandwidth policy
- quantile and random center selection
- ridge-regularized least-squares solve with nonnegative public score
- threshold mode with strict `lsdd_score > threshold`
- permutation mode with add-one p-value and strict `p_value < alpha`
- canonical measurements including `TEST_STATISTIC`, `P_VALUE`,
  `DRIFT_ALARM_STATE`, and `SAMPLE_SIZE`
- helper measurements for `LSDD_SCORE`, raw objective, kernel metadata,
  bandwidth/gamma, center policy, regularization, permutation metadata,
  mean/median/quartile summaries, and deltas
- explicit not-applicable handling for deferred preprocessing variant,
  multivariate/embedding requests, invalid kernel/bandwidth/center policies,
  invalid threshold/alpha policies, boolean input, missing windows,
  too-small samples, and unresolved median bandwidth

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py tests\test_lsdd.py
python -m pytest tests\test_lsdd.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py -q
```

Check results:

```text
py_compile: passed
DM-025 pytest: 6 passed
implemented numeric batch pytest: 88 passed
```

Manager decision:

```text
accepted as fourteenth implementation loop
```

Next candidate:

```text
DM-026 ADWIN design detail and implementation
```

## 2026-06-25 - DM-026 ADWIN Implementation Loop

### Worker Output

Worker prepared detailed design for:

- `drift_algorithm/docs/method_designs/DM-026_adwin.md`

Key design conclusions:

- first implementation scope is `ADWIN_MEAN_STREAM`
- the finite public DataFrame API replays reference/current windows as one
  chronological numeric stream
- `ADWIN_ERROR_RATE` is deferred until label/error stream contracts are defined
- `ADWIN_DISTANCE_STREAM` is deferred until precomputed distance stream
  contracts are defined
- top-level `p_value` remains `None`; top-level `threshold` records resolved
  ADWIN `delta`
- output focuses on `WINDOW_SIZE`, `DRIFT_ALARM_STATE`, final adaptive-window
  state, and compact alarm event summaries

### Manager Review

Manager reviewed the DM-026 design and accepted it with these constraints:

- implement without adding a network dependency
- use a NumPy/Pandas finite-replay implementation for the first pass
- keep `max_buckets` as a compatibility/audit parameter while recording that
  the first implementation uses an exact uncompressed finite window
- do not silently interpret supervised labels, error streams, or upstream
  distance streams as generic numeric ADWIN input
- do not fabricate p-values from ADWIN's internal alarm rule

Decision:

```text
accepted as implementation-ready
```

### DM-026 ADWIN Implementation

Implemented ADWIN.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/streamingchangedetector.py`
- `tests/test_adwin.py`

Implemented behavior:

- public `detect_adwin` function
- default `ADWIN_MEAN_STREAM` scalar numeric finite replay detector
- direct NumPy exact-window ADWIN mean-change logic with deterministic cut
  evaluation
- `delta`, `threshold_or_alpha`, `clock`, `max_buckets`,
  `min_window_length`, `grace_period`, event-recording, and sample-size
  validation
- canonical measurements including `WINDOW_SIZE` and `DRIFT_ALARM_STATE`
- helper measurements for `ADAPTIVE_WINDOW_WIDTH`, `ALARM_COUNT`,
  first/last alarm summaries, optional `ALARM_EVENTS`, final window
  statistics, sample sizes, and mean/median movement
- explicit not-applicable handling for deferred error-rate and distance-stream
  variants, multivariate/embedding/category requests, raw label/prediction
  requests, invalid parameters, boolean input, missing windows, too-small
  samples, and overlapping windows

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\streamingchangedetector.py tests\test_adwin.py
python -m pytest tests\test_adwin.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py -q
```

Check results:

```text
py_compile: passed
DM-026 pytest: 5 passed
implemented numeric and streaming pytest: 93 passed
```

Manager decision:

```text
accepted as fifteenth implementation loop
```

Next candidate:

```text
DM-027 KSWIN design detail and implementation
```

## 2026-06-25 - DM-027 KSWIN Implementation Loop

### Worker Output

Worker prepared detailed design for:

- `drift_algorithm/docs/method_designs/DM-027_kswin.md`

Key design conclusions:

- first implementation scope is scalar numeric `(time, value)` finite replay
- supported variants are `KSWIN_STANDARD` and `KSWIN_NUMERIC_STREAM`
- `KSWIN_WITH_SUBSAMPLING` is deferred until sampling and reproducibility
  policy is approved
- reference/current windows define replay scope; KSWIN itself compares older
  and recent parts inside each sliding window
- default parameters are `alpha=0.005`, `window_size=100`, `stat_size=30`, and
  `check_every=1`
- canonical outputs are `TEST_STATISTIC`, `P_VALUE`, and
  `DRIFT_ALARM_STATE`

### Manager Review

Manager reviewed the DM-027 design and accepted it with these constraints:

- use SciPy `ks_2samp` for the p-value path already available in the project
- do not reinterpret KSWIN as a full reference/current batch KS test
- keep subsampling variant explicit `not_applicable`
- use strict `p_value < alpha`
- warn on tied/discrete values, periodic checking, and uncorrected repeated
  window tests

Decision:

```text
accepted as implementation-ready
```

### DM-027 KSWIN Implementation

Implemented KSWIN.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/streamingchangedetector.py`
- `tests/test_kswin.py`

Implemented behavior:

- public `detect_kswin` function
- default `KSWIN_STANDARD` finite replay detector
- `KSWIN_NUMERIC_STREAM` alias-style supported variant
- `KSWIN_WITH_SUBSAMPLING` deferred as not applicable
- sliding-window KS comparisons using older subwindow versus latest
  `stat_size` rows
- `alpha`, `threshold_or_alpha`, `window_size`, `data_points`, `stat_size`,
  `check_every`, event-recording, tie policy, and sample-size validation
- canonical measurements including `TEST_STATISTIC`, `P_VALUE`, and
  `DRIFT_ALARM_STATE`
- helper measurements for `KS_STATISTIC`, last checked statistic/p-value,
  alarm summaries, optional `ALARM_EVENTS`, sample sizes, check counts, and
  descriptive mean/median movement
- explicit not-applicable handling for subsampling, multivariate/embedding/
  categorical requests, raw label/prediction requests, invalid parameters,
  boolean input, missing windows, too-small samples, stream shorter than
  `window_size`, and overlapping windows

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\streamingchangedetector.py tests\test_kswin.py
python -m pytest tests\test_kswin.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py -q
```

Check results:

```text
py_compile: passed
DM-027 pytest: 5 passed
implemented numeric and streaming pytest: 98 passed
```

Manager decision:

```text
accepted as sixteenth implementation loop
```

Next candidate:

```text
DM-028 Page-Hinkley Test design detail and implementation
```

## 2026-06-25 - DM-028 Page-Hinkley Test Implementation Loop

### Worker Output

Worker prepared detailed design for:

- `drift_algorithm/docs/method_designs/DM-028_page_hinkley_test.md`

Key design conclusions:

- first implementation scope is scalar numeric `(time, value)` finite replay
- default variant is `PAGE_HINKLEY_INCREASE`
- `PAGE_HINKLEY_DECREASE` is supported by direction normalization
- reference/current windows define chronological replay scope, not a batch
  two-sample comparison
- `threshold_or_alpha` is a compatibility alias for `threshold`
- no p-value is returned
- canonical outputs are `PAGE_HINKLEY_STATISTIC` and `DRIFT_ALARM_STATE`

### Manager Review

Manager reviewed the DM-028 design and accepted it with these constraints:

- implement without adding a streaming backend dependency
- use a deterministic NumPy Page-Hinkley state machine
- keep `alpha` metadata-only in the first implementation
- use strict `PAGE_HINKLEY_STATISTIC > threshold`
- keep supervised error-rate and retraining requests explicit
  `not_applicable`

Decision:

```text
accepted as implementation-ready
```

### DM-028 Page-Hinkley Test Implementation

Implemented Page-Hinkley Test.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/streamingchangedetector.py`
- `tests/test_page_hinkley_test.py`

Implemented behavior:

- public `detect_page_hinkley_test` function
- `PAGE_HINKLEY_INCREASE` and `PAGE_HINKLEY_DECREASE` variants
- finite chronological replay over scalar numeric reference/current windows
- threshold, `threshold_or_alpha`, `delta`, direction, reset policy,
  `min_instances`, `check_every`, event-recording, and sample-size validation
- canonical measurements including `PAGE_HINKLEY_STATISTIC` and
  `DRIFT_ALARM_STATE`
- helper measurements for `PH_STATISTIC`, max statistic, final running mean,
  cumulative deviation state, threshold/delta/direction, alarm summaries,
  optional `ALARM_EVENTS`, sample sizes, and descriptive mean/median movement
- explicit not-applicable handling for supervised error streams, retraining
  variants, multivariate/embedding/categorical requests, invalid parameters,
  boolean input, missing windows, too-small samples, and overlapping windows

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\streamingchangedetector.py tests\test_page_hinkley_test.py
python -m pytest tests\test_page_hinkley_test.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py -q
```

Check results:

```text
py_compile: passed
DM-028 pytest: 6 passed
implemented numeric and streaming pytest: 104 passed
```

Manager decision:

```text
accepted as seventeenth implementation loop
```

Next candidate:

```text
DM-029 CUSUM design detail and implementation
```

## 2026-06-25 - DM-029 CUSUM Implementation Loop

### Worker Output

Worker prepared detailed design for:

- `drift_algorithm/docs/method_designs/DM-029_cusum.md`

Key design conclusions:

- first implementation scope is scalar numeric `(time, value)` finite replay
- supported variants are `ONE_SIDED_UPPER_CUSUM`,
  `ONE_SIDED_LOWER_CUSUM`, and `TWO_SIDED_CUSUM`
- `CUSUM_ON_DISTANCE_STREAM` is deferred until an upstream distance-stream
  contract is approved
- omitted `target_mean` is inferred only from the effective reference window
- `decision_threshold_h`, `threshold`, and `threshold_or_alpha` are alarm
  threshold aliases, not p-value thresholds
- canonical outputs are `CUSUM_STATISTIC` and `DRIFT_ALARM_STATE`

### Manager Review

Manager reviewed the DM-029 design and accepted it with these constraints:

- implement a deterministic NumPy CUSUM state machine
- do not add external dependencies
- keep current data out of default calibration
- support real upper, lower, and two-sided recurrences
- use strict `CUSUM_STATISTIC > decision_threshold_h`
- keep distance-stream and supervised error-stream requests explicit
  `not_applicable`

Decision:

```text
accepted as implementation-ready
```

### DM-029 CUSUM Implementation

Implemented CUSUM.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/streamingchangedetector.py`
- `tests/test_cusum.py`

Implemented behavior:

- public `detect_cusum` function
- `ONE_SIDED_UPPER_CUSUM`, `ONE_SIDED_LOWER_CUSUM`, and
  `TWO_SIDED_CUSUM` variants
- finite chronological replay over scalar numeric reference/current windows
- reference-only default calibration for `target_mean`, `allowance_k`, and
  `decision_threshold_h`
- threshold alias validation for `decision_threshold_h`, `threshold`, and
  `threshold_or_alpha`
- direction alias validation, reset policy, `warmup_size`, `check_every`,
  event-recording, and sample-size validation
- canonical measurements including `CUSUM_STATISTIC` and
  `DRIFT_ALARM_STATE`
- helper measurements for positive/negative CUSUM states, max states,
  target/allowance/threshold, alarm direction summaries, optional
  `ALARM_EVENTS`, sample sizes, and descriptive mean/std/median movement
- explicit not-applicable handling for distance-stream, supervised,
  multivariate/embedding/categorical requests, invalid parameters, boolean
  input, missing windows, too-small samples, and overlapping windows

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\streamingchangedetector.py tests\test_cusum.py
python -m pytest tests\test_cusum.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py -q
```

Check results:

```text
py_compile: passed
DM-029 pytest: 6 passed
implemented numeric and streaming pytest: 110 passed
```

Manager decision:

```text
accepted as eighteenth implementation loop
```

Next candidate:

```text
DM-030 EWMA design detail and implementation
```

## 2026-06-25 - DM-030 EWMA Implementation Loop

### Worker Output

Worker prepared detailed design for:

- `drift_algorithm/docs/method_designs/DM-030_ewma.md`

Key design conclusions:

- first implementation scope is scalar numeric `(time, value)` finite replay
- supported variants are `EWMA_UNIVARIATE_CONTROL_CHART` and
  `EWMA_ONE_SIDED`
- `EWMA_BASELINE_REPLAY_THRESHOLD` is deferred until empirical baseline replay
  calibration is approved
- reference window supplies default `center_line` and `sigma`
- steady-state EWMA limits use `sigma * sqrt(lambda / (2 - lambda))`
- EWMA does not return a p-value; alarm uses strict control-limit crossing

### Manager Review

Manager reviewed the DM-030 design and accepted it with these constraints:

- implement deterministic NumPy/Pandas EWMA state
- do not add dependencies
- keep current data out of calibration defaults
- support two-sided and one-sided limit monitoring
- keep empirical replay threshold requests explicit `not_applicable`
- preserve `p_value=None`

Decision:

```text
accepted as implementation-ready
```

### DM-030 EWMA Implementation

Implemented EWMA.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/streamingchangedetector.py`
- `tests/test_ewma.py`

Implemented behavior:

- public `detect_ewma` function
- `EWMA_UNIVARIATE_CONTROL_CHART` and `EWMA_ONE_SIDED` variants
- finite chronological replay over scalar numeric reference/current windows
- reference-only default calibration for `center_line` and `sigma`
- steady-state EWMA control-limit calculation
- one-sided threshold mapping for upper/lower monitored limits
- `lambda`, control width, explicit limits, direction, reset policy,
  `warmup_size`, `check_every`, event-recording, and sample-size validation
- canonical measurements including `EWMA_VALUE`, `CONTROL_LIMIT`, and
  `DRIFT_ALARM_STATE`
- helper measurements for UCL/LCL, center line, sigma, lambda, max/min EWMA,
  limit excess, alarm direction summaries, optional `ALARM_EVENTS`, sample
  sizes, and descriptive mean/std/median movement
- explicit not-applicable handling for empirical replay thresholds,
  supervised, multivariate/embedding/categorical requests, invalid
  parameters, boolean input, missing windows, too-small samples, and
  overlapping windows

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\streamingchangedetector.py tests\test_ewma.py
python -m pytest tests\test_ewma.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py -q
```

Check results:

```text
py_compile: passed
DM-030 pytest: 6 passed
implemented numeric and streaming pytest: 116 passed
```

Manager decision:

```text
accepted as nineteenth implementation loop
```

Next candidate:

```text
DM-031 Geometric Moving Average design detail and implementation
```

## 2026-06-25 - DM-031 Geometric Moving Average Implementation Loop

### Worker Output

Worker prepared detailed design for:

- `drift_algorithm/docs/method_designs/DM-031_geometric_moving_average.md`

Key design conclusions:

- first implementation scope is scalar numeric `(time, value)` finite replay
- supported variants are `GMA_CONTROL_CHART` and `GMA_ONE_SIDED`
- `GMA_WITH_EMPIRICAL_LIMIT` is deferred until empirical baseline replay
  calibration is approved
- GMA uses geometric/exponentially weighted moving-average style recurrence
- `P_VALUE` is included as `None` because the catalog maps it but GMA is not a
  p-value test
- default parameters mirror the control-chart family:
  `lambda=0.2`, `control_width=3.0`, `warmup_size=20`,
  `check_every=1`, `reset_policy="none"`

### Manager Review

Manager reviewed the DM-031 design and accepted it with these constraints:

- keep DM-031 result identity and field names separate from EWMA
- reuse the geometric weighting recurrence semantics, not the public EWMA
  contract
- support two-sided and one-sided limit monitoring
- keep scalar `control_limit` valid only for one-sided GMA
- keep empirical-limit and supervised/multivariate requests explicit
  `not_applicable`
- preserve `p_value=None` and measurement `P_VALUE=None`

Decision:

```text
accepted as implementation-ready
```

### DM-031 Geometric Moving Average Implementation

Implemented Geometric Moving Average.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/streamingchangedetector.py`
- `tests/test_geometric_moving_average.py`

Implemented behavior:

- public `detect_geometric_moving_average` function
- `GMA_CONTROL_CHART` and `GMA_ONE_SIDED` variants
- finite chronological replay over scalar numeric reference/current windows
- reference-only default calibration for `center_line` and `sigma`
- steady-state geometric moving-average control-limit calculation
- one-sided threshold/scalar control-limit mapping and two-sided dict
  control-limit mapping
- canonical measurements including `TEST_STATISTIC`, `P_VALUE`, and
  `DRIFT_ALARM_STATE`
- helper measurements for `GMA_STATISTIC`, control limits, center line,
  sigma, lambda, max/min GMA statistic, limit excess, alarm direction
  summaries, optional `ALARM_EVENTS`, sample sizes, and descriptive
  mean/std/median movement
- explicit not-applicable handling for empirical limit, supervised,
  multivariate/embedding/categorical requests, invalid parameters, boolean
  input, missing windows, too-small samples, and overlapping windows

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\streamingchangedetector.py tests\test_geometric_moving_average.py
python -m pytest tests\test_geometric_moving_average.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py -q
```

Check results:

```text
py_compile: passed
DM-031 pytest: 6 passed
implemented numeric and streaming pytest: 122 passed
```

Manager decision:

```text
accepted as twentieth implementation loop
```

Next candidate:

```text
DM-032 BOCD design detail and implementation
```

## 2026-06-26 - DM-032 BOCD Implementation Loop

### Worker Output

Worker prepared detailed design for:

- `drift_algorithm/docs/method_designs/DM-032_bocd.md`

Key design conclusions:

- first implementation scope is scalar numeric `(time, value)` finite replay
- supported variants are `BAYESIAN_ONLINE_CHANGE_POINT_GAUSSIAN`,
  `BOCD_HAZARD_RATE_VARIANT`, and `BOCD_PREDICTIVE_PROBABILITY`
- Gaussian Normal-Inverse-Gamma prior is calibrated from the effective
  reference window unless explicit prior parameters are supplied
- constant-hazard `run_length=0` posterior alone is not used as the alarm
  score; the operational change probability is posterior mass assigned to
  short run lengths `0..short_run_length`
- BOCD does not return a frequentist p-value; `P_VALUE=None`

### Manager Review

Manager reviewed the DM-032 design and accepted it with these constraints:

- implement without adding a streaming backend dependency
- use deterministic NumPy log-space posterior updates
- keep multivariate, embedding, categorical, count, and supervised label/error
  requests explicit `not_applicable`
- preserve `p_value=None`
- expose hazard, prior, run-length truncation, and predictive probability
  settings in measurements/metadata

Decision:

```text
accepted as implementation-ready
```

### DM-032 BOCD Implementation

Implemented BOCD.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/streamingchangedetector.py`
- `drift_algorithm/docs/method_designs/DM-032_bocd.md`
- `tests/test_bocd.py`

Implemented behavior:

- public `detect_bocd` function
- finite chronological replay over scalar numeric reference/current windows
- Gaussian conjugate BOCD with Student-t predictive likelihood
- `BAYESIAN_ONLINE_CHANGE_POINT_GAUSSIAN`,
  `BOCD_HAZARD_RATE_VARIANT`, and `BOCD_PREDICTIVE_PROBABILITY` variants
- reference-window prior calibration and explicit prior override support
- hazard setting through `hazard_rate` or `expected_run_length`
- short-run posterior mass alarm using `change_probability_threshold`
- optional low predictive probability alarm
- canonical measurements including `TEST_STATISTIC`, `P_VALUE=None`, and
  `DRIFT_ALARM_STATE`
- helper measurements for change probability, predictive probability,
  run-length MAP/expected value, alarm summaries, optional `ALARM_EVENTS`,
  sample sizes, and numeric reference/current summaries
- explicit not-applicable handling for unsupported variants, non-scalar inputs,
  supervised label/error requests, unsupported likelihoods, invalid parameters,
  boolean input, missing windows, too-small samples, and overlapping windows

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\streamingchangedetector.py tests\test_bocd.py
python -m pytest tests\test_bocd.py -q
python -m pytest tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py -q
```

Check results:

```text
py_compile: passed
DM-032 pytest: 5 passed
streaming pytest: 39 passed
```

Manager decision:

```text
accepted as twenty-first implementation loop
```

Next candidate:

```text
DM-033 SeqDrift design detail and implementation
```

## 2026-06-26 - DM-033 SeqDrift Implementation Loop

### Worker Output

Worker prepared detailed design for:

- `drift_algorithm/docs/method_designs/DM-033_seqdrift.md`

Key design conclusions:

- first implementation scope is scalar numeric `(time, value)` finite replay
- supported variants are `SEQDRIFT1` and `SEQDRIFT2`
- raw `y_true`/`y_pred` conversion to an error stream is deferred until an
  explicit label/error stream contract is approved
- `SEQDRIFT1` uses the full effective reference window as the baseline
- `SEQDRIFT2` uses deterministic reservoir sampling for the reference baseline
- canonical outputs are `SEQUENTIAL_BOUND`, `DRIFT_ALARM_STATE`, and
  `METHOD_POLICY`
- SeqDrift does not return a frequentist p-value; `P_VALUE=None`

### Manager Review

Manager reviewed the DM-033 design and accepted it with these constraints:

- implement without adding a streaming backend dependency
- use a deterministic NumPy sequential-bound calculation
- keep multivariate, embedding, categorical, count, and raw label/prediction
  requests explicit `not_applicable`
- preserve `p_value=None`
- expose block size, delta, bound type, sampling policy, reservoir size, and
  seed in measurements/metadata

Decision:

```text
accepted as implementation-ready
```

### DM-033 SeqDrift Implementation

Implemented SeqDrift.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/streamingchangedetector.py`
- `drift_algorithm/docs/method_designs/DM-033_seqdrift.md`
- `tests/test_seqdrift.py`

Implemented behavior:

- public `detect_seqdrift` function
- finite chronological replay over scalar numeric reference/current windows
- `SEQDRIFT1` exact reference baseline
- `SEQDRIFT2` deterministic reservoir reference baseline
- Hoeffding-style sequential prefix bound
- `delta`, `threshold_or_alpha`, `block_size`, `reservoir_size`,
  `sampling_policy`, `bound_type`, `random_seed`, `value_min`, and `value_max`
  handling
- canonical measurements including `SEQUENTIAL_BOUND`, `DRIFT_ALARM_STATE`,
  and `METHOD_POLICY`
- helper measurements for maximum evidence, bound margin, last evidence/bound,
  alarm summaries, optional `ALARM_EVENTS`, sample sizes, and numeric
  reference/current summaries
- explicit not-applicable handling for unsupported variants, non-scalar inputs,
  raw label/prediction requests, invalid parameters, boolean input, missing
  windows, too-small samples, and overlapping windows

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\streamingchangedetector.py tests\test_seqdrift.py
python -m pytest tests\test_seqdrift.py -q
python -m pytest tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py -q
```

Check results:

```text
py_compile: passed
DM-033 pytest: 5 passed
streaming pytest: 44 passed
```

Manager decision:

```text
accepted as twenty-second implementation loop
```

Next candidate:

```text
DM-035 DDM design detail and implementation
```

## 2026-06-26 - DM-035 DDM Implementation Loop

### Worker Output

Worker prepared detailed design for:

- `drift_algorithm/docs/method_designs/DM-035_ddm.md`

Key design conclusions:

- first implementation belongs in
  `drift_algorithm.methods.supervisedconceptdriftdetector`
- supported variants are `DDM_STANDARD`, `DDM_WARNING_BUFFER`, and
  `DDM_CLASS_SPECIFIC`
- input is a binary error stream through `error_col`/`input_signal`, or derived
  from `y_true != y_pred`
- `DDM_CLASS_SPECIFIC` filters rows by the true label matching `class_label`
- DDM does not return a frequentist p-value; `P_VALUE=None`

### Manager Review

Manager reviewed the DM-035 design and accepted it with these constraints:

- implement a deterministic DDM state machine without adding dependencies
- use standard warning/drift thresholds:
  `p_i + s_i >= p_min + level * s_min`
- keep non-binary and unsupported input requests explicit `not_applicable`
- preserve `p_value=None`
- expose warning buffer, error rate, standard deviation, thresholds, and timing
  fields in measurements

Decision:

```text
accepted as implementation-ready
```

### DM-035 DDM Implementation

Implemented DDM.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/supervisedconceptdriftdetector.py`
- `drift_algorithm/docs/method_designs/DM-035_ddm.md`
- `tests/test_ddm.py`

Implemented behavior:

- public `detect_ddm` function
- `DDM_STANDARD`, `DDM_WARNING_BUFFER`, and `DDM_CLASS_SPECIFIC` variants
- precomputed binary error stream input
- `y_true`/`y_pred` derived error stream input
- class-specific filtering by `class_label`
- warning and drift state detection using DDM error-rate and standard deviation
  thresholds
- warning buffer retention for `DDM_WARNING_BUFFER`
- canonical measurements including `ERROR_RATE`, `STANDARD_DEVIATION`,
  `WARNING_STATE`, `DRIFT_ALARM_STATE`, and `BUFFERED_INSTANCE_COUNT`
- helper measurements for thresholds, minimum error state, warning/drift timing,
  optional `DDM_EVENTS`, optional `WARNING_BUFFER`, sample sizes, and
  reference/current error-rate summaries
- explicit not-applicable handling for unsupported variants, unsupported
  non-scalar requests, missing error/label columns, non-binary errors, missing
  class label, invalid parameters, missing windows, too-small samples, and
  overlapping windows

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\supervisedconceptdriftdetector.py tests\test_ddm.py
python -m pytest tests\test_ddm.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py -q
```

Check results:

```text
py_compile: passed
DM-035 pytest: 5 passed
implemented numeric, streaming, and DDM pytest: 137 passed
```

Manager decision:

```text
accepted as twenty-third implementation loop
```

Next candidate:

```text
DM-036 RDDM design detail and implementation
```

## 2026-06-26 - DM-036 RDDM Implementation Loop

### Worker Design Detail

Worker completed the first RDDM design detail pass in:

- `drift_algorithm/docs/method_designs/DM-036_rddm.md`

Design decisions:

- classify RDDM under `SupervisedConceptDriftDetector`
- support precomputed binary error streams and `y_true`/`y_pred` derived error
  streams
- support `RDDM_STANDARD` and `RDDM_REACTIVE_RESET`
- use a DDM-style RDDM statistic:
  `p_i + s_i >= p_min + level * s_min`
- bound the effective concept history with `max_concept_size`
- expose retained window size and reset/adaptation metadata
- RDDM does not return a frequentist p-value; `P_VALUE=None`

### Manager Review

Manager reviewed the DM-036 design and accepted it with these constraints:

- keep implementation deterministic and dependency-free beyond current NumPy /
  pandas usage
- reject unsupported feature, embedding, categorical, and unsupervised requests
  as `not_applicable`
- require binary error stream semantics when `error_col` / `input_signal` is
  used
- allow `RDDM_REACTIVE_RESET` only with reactive reset policy
- preserve `p_value=None`

Decision:

```text
accepted as implementation-ready
```

### DM-036 RDDM Implementation

Implemented RDDM.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/supervisedconceptdriftdetector.py`
- `drift_algorithm/docs/method_designs/DM-036_rddm.md`
- `tests/test_rddm.py`

Implemented behavior:

- public `detect_rddm` function
- `RDDM_STANDARD` and `RDDM_REACTIVE_RESET` variants
- precomputed binary error stream input
- `y_true`/`y_pred` derived error stream input
- RDDM warning and drift state detection with bounded concept history
- retained warning/recent window metadata
- reactive reset event summary for `RDDM_REACTIVE_RESET`
- canonical measurements including `WARNING_STATE`, `DRIFT_ALARM_STATE`,
  `WINDOW_SIZE`, `ADAPTATION_EVENT`, and `ERROR_RATE`
- helper measurements for retained size, thresholds, standard deviation,
  timing, reset event, post-reset error rate, optional `RDDM_EVENTS`, sample
  sizes, and reference/current error-rate summaries
- explicit not-applicable handling for unsupported variants, unsupported
  non-scalar requests, missing error/label columns, non-binary errors, invalid
  reset policy, invalid concept size parameters, missing windows, too-small
  samples, and overlapping windows

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\supervisedconceptdriftdetector.py tests\test_rddm.py
python -m pytest tests\test_rddm.py -q
python -m pytest tests\test_ddm.py tests\test_rddm.py -q
python -m pytest tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py -q
```

Check results:

```text
py_compile: passed
DM-036 pytest: 5 passed
DDM and RDDM pytest: 10 passed
streaming and supervised pytest subset: 54 passed
implemented numeric, streaming, and supervised pytest: 142 passed
```

Manager decision:

```text
accepted as twenty-fourth implementation loop
```

Next candidate:

```text
DM-037 EDDM design detail and implementation
```

## 2026-06-26 - DM-037 EDDM Implementation Loop

### Worker Design Detail

Worker completed the first EDDM design detail pass in:

- `drift_algorithm/docs/method_designs/DM-037_eddm.md`

Design decisions:

- classify EDDM under `SupervisedConceptDriftDetector`
- support precomputed binary error streams and `y_true`/`y_pred` derived error
  streams
- support `EDDM_DISTANCE_BETWEEN_ERRORS`, `EDDM_WARNING_DRIFT`, and
  `EDDM_GRADUAL_DRIFT`
- use index-gap distance between consecutive errors
- compute the EDDM score as `mean(distance) + 2 * std(distance)`
- compare the current score to the historical maximum score
- EDDM does not return a frequentist p-value; `P_VALUE=None`

### Manager Review

Manager reviewed the DM-037 design and accepted it with these constraints:

- keep implementation deterministic and dependency-free beyond current NumPy /
  pandas usage
- reject unsupported feature, embedding, categorical, and unsupervised requests
  as `not_applicable`
- require binary error stream semantics when `error_col` / `input_signal` is
  used
- expose score ratio and error-distance summary measurements
- preserve `p_value=None`

Decision:

```text
accepted as implementation-ready
```

### DM-037 EDDM Implementation

Implemented EDDM.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/supervisedconceptdriftdetector.py`
- `drift_algorithm/docs/method_designs/DM-037_eddm.md`
- `tests/test_eddm.py`

Implemented behavior:

- public `detect_eddm` function
- `EDDM_DISTANCE_BETWEEN_ERRORS`, `EDDM_WARNING_DRIFT`, and
  `EDDM_GRADUAL_DRIFT` variants
- precomputed binary error stream input
- `y_true`/`y_pred` derived error stream input
- error-distance score tracking with warning/drift ratio thresholds
- canonical measurements including `TEST_STATISTIC`, `P_VALUE`, and
  `DRIFT_ALARM_STATE`
- helper measurements for EDDM score, score ratio, error-distance mean/std,
  maximum score, warning/drift timing, gradual drift state, optional
  `EDDM_EVENTS`, sample sizes, and reference/current error-rate summaries
- explicit not-applicable handling for unsupported variants, unsupported
  non-scalar requests, missing error/label columns, non-binary errors,
  unsupported distance metric, missing windows, too-small samples, too few
  observed errors, and overlapping windows

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\supervisedconceptdriftdetector.py tests\test_eddm.py
python -m pytest tests\test_eddm.py -q
python -m pytest tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py -q
python -m pytest tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py -q
```

Check results:

```text
py_compile: passed
DM-037 pytest: 5 passed
DDM/RDDM/EDDM pytest: 15 passed
streaming and supervised pytest subset: 59 passed
implemented numeric, streaming, and supervised pytest: 147 passed
```

Manager decision:

```text
accepted as twenty-fifth implementation loop
```

Next candidate:

```text
DM-038 ECDD-WT design detail and implementation
```

## 2026-06-26 - DM-038 ECDD-WT Implementation Loop

### Worker Design Detail

Worker completed the first ECDD-WT design detail pass in:

- `drift_algorithm/docs/method_designs/DM-038_ecdd_wt.md`

Design decisions:

- classify ECDD-WT under `SupervisedConceptDriftDetector`
- support precomputed binary error streams and `y_true`/`y_pred` derived error
  streams
- support `ECDD_WT_STANDARD`, `ECDD_WT_WARNING_DRIFT`, and
  `ECDD_WT_ERROR_STREAM`
- estimate the baseline error rate from the reference window
- compute an EWMA error statistic using configurable `lambda`
- standardize the EWMA statistic against the reference baseline variance
- ECDD-WT does not return a frequentist p-value; `P_VALUE=None`

### Manager Review

Manager reviewed the DM-038 design and accepted it with these constraints:

- keep implementation deterministic and dependency-free beyond current NumPy /
  pandas usage
- reject unsupported feature, embedding, categorical, and unsupervised requests
  as `not_applicable`
- require binary error stream semantics when `error_col` / `input_signal` is
  used
- expose EWMA statistic, standardized statistic, baseline error rate, and
  warning/drift timing
- preserve `p_value=None`

Decision:

```text
accepted as implementation-ready
```

### DM-038 ECDD-WT Implementation

Implemented ECDD-WT.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/supervisedconceptdriftdetector.py`
- `drift_algorithm/docs/method_designs/DM-038_ecdd_wt.md`
- `tests/test_ecdd_wt.py`

Implemented behavior:

- public `detect_ecdd_wt` function
- `ECDD_WT_STANDARD`, `ECDD_WT_WARNING_DRIFT`, and
  `ECDD_WT_ERROR_STREAM` variants
- precomputed binary error stream input
- `y_true`/`y_pred` derived error stream input
- reference-window baseline error-rate estimation
- EWMA error statistic tracking with warning/drift thresholds
- canonical measurements including `TEST_STATISTIC`, `P_VALUE`, and
  `DRIFT_ALARM_STATE`
- helper measurements for EWMA statistic, standardized ECDD-WT statistic,
  baseline error rate, final error rate, lambda, warning/drift timing, optional
  `ECDD_WT_EVENTS`, sample sizes, and reference/current error-rate summaries
- explicit not-applicable handling for unsupported variants, unsupported
  non-scalar requests, missing error/label columns, non-binary errors, invalid
  lambda or threshold values, missing windows, too-small samples, and
  overlapping windows

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\supervisedconceptdriftdetector.py tests\test_ecdd_wt.py
python -m pytest tests\test_ecdd_wt.py -q
python -m pytest tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py -q
python -m pytest tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py -q
```

Check results:

```text
py_compile: passed
DM-038 pytest: 5 passed
DDM/RDDM/EDDM/ECDD-WT pytest: 20 passed
streaming and supervised pytest subset: 64 passed
implemented numeric, streaming, and supervised pytest: 152 passed
```

Manager decision:

```text
accepted as twenty-sixth implementation loop
```

Next candidate:

```text
DM-039 HDDM-A design detail and implementation
```

## 2026-06-26 - DM-039 HDDM-A Implementation Loop

### Worker Design Detail

Worker completed the first HDDM-A design detail pass in:

- `drift_algorithm/docs/method_designs/DM-039_hddm_a.md`

Design decisions:

- classify HDDM-A under `SupervisedConceptDriftDetector`
- support precomputed binary error streams and `y_true`/`y_pred` derived error
  streams
- support `HDDM_A_HOEFFDING_BOUND`, `HDDM_A_WARNING_DRIFT`, and
  `HDDM_A_TWO_SIDED`
- compare reference-window error mean against current-window prefix means
- use Hoeffding bounds computed from reference and current prefix sample sizes
- support two-sided monitoring only for `HDDM_A_TWO_SIDED`
- HDDM-A does not return a frequentist p-value; `P_VALUE=None`

### Manager Review

Manager reviewed the DM-039 design and accepted it with these constraints:

- keep implementation deterministic and dependency-free beyond current NumPy /
  pandas usage
- reject unsupported feature, embedding, categorical, and unsupervised requests
  as `not_applicable`
- require binary error stream semantics when `error_col` / `input_signal` is
  used
- expose mean difference, Hoeffding bounds, direction, and warning/drift timing
- preserve `p_value=None`

Decision:

```text
accepted as implementation-ready
```

### DM-039 HDDM-A Implementation

Implemented HDDM-A.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/supervisedconceptdriftdetector.py`
- `drift_algorithm/docs/method_designs/DM-039_hddm_a.md`
- `tests/test_hddm_a.py`

Implemented behavior:

- public `detect_hddm_a` function
- `HDDM_A_HOEFFDING_BOUND`, `HDDM_A_WARNING_DRIFT`, and
  `HDDM_A_TWO_SIDED` variants
- precomputed binary error stream input
- `y_true`/`y_pred` derived error stream input
- reference mean vs current prefix mean comparison
- Hoeffding warning/drift bound calculation
- one-sided increase detection and two-sided increase/decrease detection
- canonical measurements including `TEST_STATISTIC`, `P_VALUE`, and
  `DRIFT_ALARM_STATE`
- helper measurements for mean difference, reference/current prefix means,
  Hoeffding warning/drift bounds, change direction, warning/drift timing,
  optional `HDDM_A_EVENTS`, sample sizes, and reference/current error-rate
  summaries
- explicit not-applicable handling for unsupported variants, unsupported
  non-scalar requests, missing error/label columns, non-binary errors, invalid
  confidence or two-sided parameters, missing windows, too-small samples, and
  overlapping windows

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\supervisedconceptdriftdetector.py tests\test_hddm_a.py
python -m pytest tests\test_hddm_a.py -q
python -m pytest tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py -q
python -m pytest tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py -q
```

Check results:

```text
py_compile: passed
DM-039 pytest: 5 passed
supervised detector pytest: 25 passed
streaming and supervised pytest subset: 69 passed
implemented numeric, streaming, and supervised pytest: 157 passed
```

Manager decision:

```text
accepted as twenty-seventh implementation loop
```

Next candidate:

```text
DM-040 HDDM-W design detail and implementation
```

## 2026-06-26 - DM-040 HDDM-W Implementation Loop

### Worker Design Detail

Worker completed the first HDDM-W design detail pass in:

- `drift_algorithm/docs/method_designs/DM-040_hddm_w.md`

Design decisions:

- classify HDDM-W under `SupervisedConceptDriftDetector`
- support precomputed binary error streams and `y_true`/`y_pred` derived error
  streams
- support `HDDM_W_WEIGHTED_AVERAGE`, `HDDM_W_WARNING_DRIFT`, and
  `HDDM_W_RECENT_ERROR_WEIGHTING`
- compare reference-window error mean against current recent-weighted error mean
- compute current effective sample size from the exponential weights induced by
  `lambda`
- use weighted Hoeffding bounds for warning/drift decisions
- HDDM-W does not return a frequentist p-value; `P_VALUE=None`

### Manager Review

Manager reviewed the DM-040 design and accepted it with these constraints:

- keep implementation deterministic and dependency-free beyond current NumPy /
  pandas usage
- reject unsupported feature, embedding, categorical, and unsupervised requests
  as `not_applicable`
- require binary error stream semantics when `error_col` / `input_signal` is
  used
- expose weighted mean difference, effective sample size, Hoeffding bounds,
  direction, and warning/drift timing
- preserve `p_value=None`

Decision:

```text
accepted as implementation-ready
```

### DM-040 HDDM-W Implementation

Implemented HDDM-W.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/supervisedconceptdriftdetector.py`
- `drift_algorithm/docs/method_designs/DM-040_hddm_w.md`
- `tests/test_hddm_w.py`

Implemented behavior:

- public `detect_hddm_w` function
- `HDDM_W_WEIGHTED_AVERAGE`, `HDDM_W_WARNING_DRIFT`, and
  `HDDM_W_RECENT_ERROR_WEIGHTING` variants
- precomputed binary error stream input
- `y_true`/`y_pred` derived error stream input
- reference mean vs current recent-weighted mean comparison
- weighted effective sample size calculation
- weighted Hoeffding warning/drift bound calculation
- one-sided increase detection and optional two-sided increase/decrease
  detection
- canonical measurements including `TEST_STATISTIC`, `P_VALUE`, and
  `DRIFT_ALARM_STATE`
- helper measurements for weighted mean difference, reference/weighted current
  means, effective current sample size, Hoeffding warning/drift bounds, change
  direction, lambda, warning/drift timing, optional `HDDM_W_EVENTS`, sample
  sizes, and reference/current error-rate summaries
- explicit not-applicable handling for unsupported variants, unsupported
  non-scalar requests, missing error/label columns, non-binary errors, invalid
  confidence/lambda/two-sided parameters, missing windows, too-small samples,
  and overlapping windows

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\supervisedconceptdriftdetector.py tests\test_hddm_w.py
python -m pytest tests\test_hddm_w.py -q
python -m pytest tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py -q
python -m pytest tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py -q
```

Check results:

```text
py_compile: passed
DM-040 pytest: 5 passed
supervised detector pytest: 30 passed
streaming and supervised pytest subset: 74 passed
implemented numeric, streaming, and supervised pytest: 162 passed
```

Manager decision:

```text
accepted as twenty-eighth implementation loop
```

Next candidate:

```text
DM-041 STEPD design detail and implementation
```

## 2026-06-26 - DM-041 STEPD Implementation Loop

### Worker Design Detail

Worker completed the first STEPD design detail pass in:

- `drift_algorithm/docs/method_designs/DM-041_stepd.md`

Design decisions:

- classify STEPD under `SupervisedConceptDriftDetector`
- support precomputed binary error streams and `y_true`/`y_pred` derived error
  streams
- support `STEPD_ACCURACY_WINDOW`, `STEPD_WARNING_DRIFT`, and
  `STEPD_SUPERVISED_STREAM`
- compare reference-window accuracy against rolling current-window accuracy
- use a one-sided two-proportion normal approximation for accuracy degradation
- separate warning/drift states using `alpha_warning` and `alpha_drift`

### Manager Review

Manager reviewed the DM-041 design and accepted it with these constraints:

- keep implementation deterministic and dependency-free beyond current NumPy /
  pandas usage
- reject unsupported feature, embedding, categorical, and unsupervised requests
  as `not_applicable`
- require binary error stream semantics when `error_col` / `input_signal` is
  used
- expose z statistic, p-value, reference/current accuracy, window size, and
  warning/drift timing
- return a normal-approximation one-sided p-value for STEPD

Decision:

```text
accepted as implementation-ready
```

### DM-041 STEPD Implementation

Implemented STEPD.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/supervisedconceptdriftdetector.py`
- `drift_algorithm/docs/method_designs/DM-041_stepd.md`
- `tests/test_stepd.py`

Implemented behavior:

- public `detect_stepd` function
- `STEPD_ACCURACY_WINDOW`, `STEPD_WARNING_DRIFT`, and
  `STEPD_SUPERVISED_STREAM` variants
- precomputed binary error stream input
- `y_true`/`y_pred` derived error stream input
- reference-window accuracy estimation
- rolling current-window accuracy comparison
- one-sided two-proportion z statistic and p-value
- canonical measurements including `TEST_STATISTIC`, `P_VALUE`, and
  `DRIFT_ALARM_STATE`
- helper measurements for reference/current-window accuracy, accuracy delta,
  alpha thresholds, window size, warning/drift timing, optional `STEPD_EVENTS`,
  sample sizes, and reference/current error-rate summaries
- explicit not-applicable handling for unsupported variants, unsupported
  non-scalar requests, missing error/label columns, non-binary errors, invalid
  alpha/window parameters, missing windows, too-small samples, and overlapping
  windows

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\supervisedconceptdriftdetector.py tests\test_stepd.py
python -m pytest tests\test_stepd.py -q
python -m pytest tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py -q
python -m pytest tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py -q
```

Check results:

```text
py_compile: passed
DM-041 pytest: 5 passed
supervised detector pytest: 35 passed
streaming and supervised pytest subset: 79 passed
implemented numeric, streaming, and supervised pytest: 167 passed
```

Manager decision:

```text
accepted as twenty-ninth implementation loop
```

Next candidate:

```text
DM-042 Hotelling T2 design detail and implementation
```

## 2026-06-26 - DM-042 Hotelling T2 Implementation Loop

### Worker Design Detail

Worker completed the first Hotelling T2 design detail pass in:

- `drift_algorithm/docs/method_designs/DM-042_hotelling_t2.md`

Design decisions:

- classify Hotelling T2 under `MultivariateProcessControl`
- support multivariate numeric input via `feature_cols` or `embedding_cols`
- support `HOTELLING_T2_ONE_SAMPLE_PHASE_II`, `HOTELLING_T2_TWO_SAMPLE`, and
  `REGULARIZED_HOTELLING_T2`
- use pooled covariance for two-sample T2
- use reference covariance for Phase II current-window mean monitoring
- support diagonal loading and shrinkage for regularized covariance
- defer PCA preprocessing

### Manager Review

Manager reviewed the DM-042 design and accepted it with these constraints:

- keep implementation deterministic and use current NumPy / SciPy dependencies
- require at least two numeric feature columns
- reject PCA preprocessing as `not_applicable` in the first implementation
- expose T2 statistic, p-value where available, control limit, method policy,
  feature dimension, and mean difference vector
- warn on ill-conditioned or regularized covariance usage

Decision:

```text
accepted as implementation-ready
```

### DM-042 Hotelling T2 Implementation

Implemented Hotelling T2.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/multivariateprocesscontrol.py`
- `drift_algorithm/docs/method_designs/DM-042_hotelling_t2.md`
- `tests/test_hotelling_t2.py`

Implemented behavior:

- public `detect_hotelling_t2` function
- `HOTELLING_T2_ONE_SAMPLE_PHASE_II`, `HOTELLING_T2_TWO_SAMPLE`, and
  `REGULARIZED_HOTELLING_T2` variants
- multivariate numeric window preparation with invalid timestamp / non-finite
  feature row handling
- pooled-covariance two-sample T2 statistic and F-approximation p-value
- reference-covariance Phase II T2 statistic and control-limit comparison
- regularized T2 with diagonal loading or shrinkage covariance policy
- canonical measurements including `HOTELLING_T2_STATISTIC`, `CONTROL_LIMIT`,
  `DRIFT_ALARM_STATE`, `METHOD_POLICY`, and `P_VALUE`
- helper measurements for feature dimension, mean difference vector, feature
  columns, and sample sizes
- explicit not-applicable handling for unsupported variants, missing feature
  columns, univariate input, PCA request, missing windows, too-small samples,
  and unusable F-approximation sample sizes

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\multivariateprocesscontrol.py tests\test_hotelling_t2.py
python -m pytest tests\test_hotelling_t2.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py -q
```

Check results:

```text
py_compile: passed
DM-042 pytest: 5 passed
implemented numeric, streaming, supervised, and multivariate pytest: 172 passed
```

Manager decision:

```text
accepted as thirtieth implementation loop
```

Next candidate:

```text
DM-043 MEWMA design detail and implementation
```

## 2026-06-26 - DM-043 MEWMA Implementation Loop

### Worker Design Detail

Worker completed the first MEWMA design detail pass in:

- `drift_algorithm/docs/method_designs/DM-043_mewma.md`

Design decisions:

- classify MEWMA under `MultivariateProcessControl`
- support multivariate numeric input via `feature_cols` or `embedding_cols`
- support `MEWMA_STANDARD` and `MEWMA_WITH_MAHALANOBIS_D2`
- use reference-window mean and covariance as the baseline
- compute finite-time scaled MEWMA statistic from the EWMA vector
- use explicit `control_limit` when supplied, otherwise use chi-square
  approximation from `alpha`
- expose Mahalanobis D2 for the D2 variant

### Manager Review

Manager reviewed the DM-043 design and accepted it with these constraints:

- keep implementation deterministic and use current NumPy / SciPy dependencies
- require at least two numeric feature columns
- preserve finite DataFrame replay behavior for current rows
- expose MEWMA statistic, Mahalanobis D2, control limit, lambda, final EWMA
  vector, and baseline mean vector
- warn on ill-conditioned or regularized covariance usage

Decision:

```text
accepted as implementation-ready
```

### DM-043 MEWMA Implementation

Implemented MEWMA.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/multivariateprocesscontrol.py`
- `drift_algorithm/docs/method_designs/DM-043_mewma.md`
- `tests/test_mewma.py`

Implemented behavior:

- public `detect_mewma` function
- `MEWMA_STANDARD` and `MEWMA_WITH_MAHALANOBIS_D2` variants
- multivariate numeric window preparation with invalid timestamp / non-finite
  feature row handling
- reference-window baseline mean and covariance estimation
- optional diagonal-loading covariance regularization
- current-window chronological MEWMA replay
- finite-time scaled MEWMA statistic
- chi-square approximate control limit when explicit limit is absent
- canonical measurements including `MEWMA_STATISTIC`, `MAHALANOBIS_DISTANCE`,
  `CONTROL_LIMIT`, and `DRIFT_ALARM_STATE`
- helper measurements for feature dimension, feature columns, lambda, final
  EWMA vector, reference mean vector, alarm index/time, and sample sizes
- explicit not-applicable handling for unsupported variants, missing feature
  columns, univariate input, invalid lambda/control/covariance parameters,
  missing windows, and too-small samples

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\multivariateprocesscontrol.py tests\test_mewma.py
python -m pytest tests\test_mewma.py -q
python -m pytest tests\test_hotelling_t2.py tests\test_mewma.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py -q
```

Check results:

```text
py_compile: passed
DM-043 pytest: 4 passed
multivariate process control pytest: 9 passed
implemented numeric, streaming, supervised, and multivariate pytest: 176 passed
```

Manager decision:

```text
accepted as thirty-first implementation loop
```

Next candidate:

```text
DM-044 Mahalanobis Distance design detail and implementation
```

## 2026-06-26 - DM-044 Mahalanobis Distance Implementation Loop

### Worker Design Detail

Worker completed the first Mahalanobis Distance design detail pass in:

- `drift_algorithm/docs/method_designs/DM-044_mahalanobis_distance.md`

Design decisions:

- classify Mahalanobis Distance under `MultivariateProcessControl`
- support multivariate numeric input via `feature_cols` or `embedding_cols`
- support `SAMPLE_MAHALANOBIS_OUTLIER`, `WINDOW_MEAN_MAHALANOBIS`, and
  `ROBUST_MAHALANOBIS`
- use reference-window baseline center/covariance for classical variants
- use chi-square D2 limit from `alpha` unless explicit `threshold` /
  `control_limit` is supplied
- expose outlier count and outlier fraction for sample-level screening
- implement robust variant with deterministic median and MAD-based diagonal
  covariance rather than adding a new robust covariance dependency

### Manager Review

Manager reviewed the DM-044 design and accepted it with these constraints:

- keep the implementation inside the existing multivariate process-control
  module and reuse shared window validation
- require at least two numeric feature columns
- return `not_applicable` for unsupported variants, bad windows, missing
  features, invalid alpha/threshold parameters, or insufficient samples
- warn when covariance is ill-conditioned, regularized, or robust diagonal
  covariance changes the distance scale
- expose canonical measurements for distance, D2, method policy, outlier flag,
  threshold exceedance, outlier count/fraction, sample sizes, and feature
  dimension

Decision:

```text
accepted as implementation-ready
```

### DM-044 Mahalanobis Distance Implementation

Implemented Mahalanobis Distance.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/multivariateprocesscontrol.py`
- `drift_algorithm/docs/method_designs/DM-044_mahalanobis_distance.md`
- `tests/test_mahalanobis_distance.py`

Implemented behavior:

- public `detect_mahalanobis_distance` function
- `WINDOW_MEAN_MAHALANOBIS` variant for current-window mean shift scoring
- `SAMPLE_MAHALANOBIS_OUTLIER` variant for sample-level outlier screening
- `ROBUST_MAHALANOBIS` variant using median/MAD diagonal covariance
- explicit threshold/control-limit support
- chi-square D2 threshold approximation when explicit threshold is absent
- canonical measurements including `MAHALANOBIS_DISTANCE`, `MAHALANOBIS_D2`,
  `METHOD_POLICY`, `OUTLIER_FLAG`, and `THRESHOLD_EXCEEDANCE`
- helper measurements for p-value, control limit, sample sizes, feature
  dimension, feature columns, reference center, current center, outlier count,
  and outlier fraction
- explicit not-applicable handling for unsupported variants, missing feature
  columns, univariate input, invalid alpha/threshold parameters, missing
  windows, and too-small samples

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\multivariateprocesscontrol.py tests\test_mahalanobis_distance.py
python -m pytest tests\test_mahalanobis_distance.py -q
python -m pytest tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py -q
```

Check results:

```text
py_compile: passed
DM-044 pytest: 5 passed
multivariate process control pytest: 14 passed
implemented numeric, streaming, supervised, and multivariate pytest: 181 passed
```

Manager decision:

```text
accepted as thirty-second implementation loop
```

Next candidate:

```text
DM-045 OCDD design detail and implementation
```

## 2026-06-26 - DM-045 OCDD Implementation Loop

### Worker Design Detail

Worker completed the first OCDD design detail pass in:

- `drift_algorithm/docs/method_designs/DM-045_ocdd.md`

Design decisions:

- classify OCDD under `RepresentationDriftMethod`
- create `drift_algorithm.methods.representationdriftmethod`
- support multivariate numeric input via `feature_cols` or `embedding_cols`
- support `ONE_CLASS_SVM_DRIFT`, `ISOLATION_FOREST_DRIFT_SCORE`, and
  `AUTOENCODER_RECONSTRUCTION_DRIFT`
- avoid adding new dependencies; implement deterministic NumPy surrogates for
  the first pass
- use reference score quantile threshold from `alpha` unless explicit
  `threshold` / `score_threshold` is supplied
- use `anomaly_rate_threshold` as the final drift decision rule

### Manager Review

Manager reviewed the DM-045 design and accepted it with these constraints:

- do not require scikit-learn for this implementation pass
- clearly expose surrogate method policy in measurements and warnings
- require at least two numeric feature columns
- return `not_applicable` for unsupported variants, bad windows, missing
  features, invalid alpha/threshold/rate parameters, invalid latent dimension,
  or insufficient samples
- expose canonical measurements for anomaly score, anomaly rate, boundary
  violation rate, reconstruction error, threshold, method policy, anomaly
  count, sample sizes, and feature dimension

Decision:

```text
accepted as implementation-ready
```

### DM-045 OCDD Implementation

Implemented OCDD.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/representationdriftmethod.py`
- `drift_algorithm/docs/method_designs/DM-045_ocdd.md`
- `tests/test_ocdd.py`

Implemented behavior:

- public `detect_ocdd` function
- `ONE_CLASS_SVM_DRIFT` radial one-class boundary surrogate
- `ISOLATION_FOREST_DRIFT_SCORE` fixed-seed random projection anomaly-score
  surrogate
- `AUTOENCODER_RECONSTRUCTION_DRIFT` linear PCA reconstruction surrogate
- reference-window score threshold calibration from `alpha`
- explicit `threshold` / `score_threshold` support
- `anomaly_rate_threshold` final alarm rule
- canonical measurements including `ANOMALY_SCORE`,
  `OUTLIER_OR_ANOMALY_RATE`, and `RECONSTRUCTION_ERROR`
- helper measurements for max score, boundary violation rate, threshold,
  anomaly count, sample sizes, feature dimension, feature columns, and method
  policy
- explicit not-applicable handling for unsupported variants, missing feature
  columns, univariate input, invalid alpha/threshold/rate parameters, invalid
  latent dimension, missing windows, and too-small samples

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\representationdriftmethod.py tests\test_ocdd.py
python -m pytest tests\test_ocdd.py -q
python -m pytest tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py tests\test_ocdd.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py tests\test_ocdd.py -q
```

Check results:

```text
py_compile: passed
DM-045 pytest: 5 passed
representation/multivariate regression pytest: 19 passed
implemented numeric, streaming, supervised, multivariate, and representation pytest: 186 passed
```

Manager decision:

```text
accepted as thirty-third implementation loop
```

Next candidate:

```text
DM-046 Feature Map Drift design detail and implementation
```

## 2026-06-26 - DM-046 Feature Map Drift Implementation Loop

### Worker Design Detail

Worker completed the first Feature Map Drift design detail pass in:

- `drift_algorithm/docs/method_designs/DM-046_feature_map_drift.md`

Design decisions:

- classify Feature Map Drift under `RepresentationDriftMethod`
- continue using `drift_algorithm.methods.representationdriftmethod`
- support multivariate feature map input via `feature_cols`, `embedding_cols`,
  or `layer_feature_cols`
- support `MODEL_FEATURE_MAP_KS`, `MODEL_FEATURE_MAP_MMD`, and
  `LAYERWISE_FEATURE_MAP_DRIFT`
- use axis-wise KS tests for feature-level screening
- use RBF-kernel MMD for full-vector and multi-feature layer scoring
- support optional permutation p-value calibration for MMD
- expose layerwise statistics and alarm states for layer-level interpretation

### Manager Review

Manager reviewed the DM-046 design and accepted it with these constraints:

- reuse the existing representation window validation
- require at least two numeric feature-map columns
- make layer features unique across `layer_feature_cols`
- use p-value based drift decisions when a p-value is available
- expose a method policy so KS, MMD, and layerwise scoring are distinguishable
- return `not_applicable` for unsupported variants, bad windows, missing
  features, invalid alpha/threshold/bandwidth/permutation parameters, or
  insufficient samples

Decision:

```text
accepted as implementation-ready
```

### DM-046 Feature Map Drift Implementation

Implemented Feature Map Drift.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/representationdriftmethod.py`
- `drift_algorithm/docs/method_designs/DM-046_feature_map_drift.md`
- `tests/test_feature_map_drift.py`

Implemented behavior:

- public `detect_feature_map_drift` function
- `MODEL_FEATURE_MAP_KS` variant with axis-wise KS tests
- `MODEL_FEATURE_MAP_MMD` variant with RBF-kernel MMD and optional permutation
  p-value
- `LAYERWISE_FEATURE_MAP_DRIFT` variant with layer-level KS/MMD scoring
- median pairwise distance default bandwidth for MMD
- canonical measurements including `TEST_STATISTIC`, `P_VALUE`, and
  `DRIFT_ALARM_STATE`
- helper measurements for feature-map score, max feature statistic, significant
  feature count/fraction, layerwise scores, sample sizes, feature dimension,
  and feature columns
- explicit not-applicable handling for unsupported variants, missing feature
  columns, univariate input, duplicate layer columns, invalid alpha/threshold /
  bandwidth / permutation parameters, missing windows, and too-small samples

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\representationdriftmethod.py tests\test_feature_map_drift.py
python -m pytest tests\test_feature_map_drift.py -q
python -m pytest tests\test_ocdd.py tests\test_feature_map_drift.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py tests\test_ocdd.py tests\test_feature_map_drift.py -q
```

Check results:

```text
py_compile: passed
DM-046 pytest: 5 passed
representation regression pytest: 10 passed
implemented numeric, streaming, supervised, multivariate, and representation pytest: 191 passed
```

Manager decision:

```text
accepted as thirty-fourth implementation loop
```

Next candidate:

```text
DM-047 Autoencoder Representation Drift design detail and implementation
```

## 2026-06-26 - DM-047 Autoencoder Representation Drift Implementation Loop

### Worker Design Detail

Worker completed the first Autoencoder Representation Drift design detail pass in:

- `drift_algorithm/docs/method_designs/DM-047_autoencoder_representation_drift.md`

Design decisions:

- classify Autoencoder Representation Drift under `RepresentationDriftMethod`
- continue using `drift_algorithm.methods.representationdriftmethod`
- support `feature_cols`, `embedding_cols`, `latent_cols`, or
  `reconstruction_error_col`
- support `LATENT_SPACE_DRIFT`, `RECONSTRUCTION_ERROR_DRIFT`, and
  `AUTOENCODER_DOMAIN_CLASSIFIER`
- use RBF-kernel MMD for latent distribution comparison
- use supplied reconstruction error when available and a deterministic PCA
  reconstruction surrogate otherwise
- use a nearest-centroid domain separability surrogate instead of adding a
  classifier dependency

### Manager Review

Manager reviewed the DM-047 design and accepted it with these constraints:

- reuse the existing representation window validation
- require at least two latent/representation columns for latent and classifier
  variants
- allow a single supplied reconstruction-error column for reconstruction-error
  drift
- expose method policy and surrogate caveats through measurements/warnings
- return `not_applicable` for unsupported variants, bad windows, missing
  columns, invalid alpha/threshold/bandwidth/permutation parameters, invalid
  latent dimension, or insufficient samples

Decision:

```text
accepted as implementation-ready
```

### DM-047 Autoencoder Representation Drift Implementation

Implemented Autoencoder Representation Drift.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/representationdriftmethod.py`
- `drift_algorithm/docs/method_designs/DM-047_autoencoder_representation_drift.md`
- `tests/test_autoencoder_representation_drift.py`

Implemented behavior:

- public `detect_autoencoder_representation_drift` function
- `LATENT_SPACE_DRIFT` variant with standardized latent-vector RBF MMD
- `RECONSTRUCTION_ERROR_DRIFT` variant with supplied error-column or PCA
  reconstruction-error surrogate
- `AUTOENCODER_DOMAIN_CLASSIFIER` variant with nearest-centroid AUC surrogate
- optional permutation p-value calibration for latent MMD
- canonical measurements including `TEST_STATISTIC`, `P_VALUE`, and
  `DRIFT_ALARM_STATE`
- helper measurements for latent drift score, reconstruction error,
  reference reconstruction error, domain classifier AUC/accuracy, current-domain
  probability, sample sizes, feature dimension, and feature columns
- explicit not-applicable handling for unsupported variants, missing columns,
  invalid alpha/threshold/bandwidth/permutation parameters, invalid latent
  dimension, missing windows, and too-small samples

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\representationdriftmethod.py tests\test_autoencoder_representation_drift.py
python -m pytest tests\test_autoencoder_representation_drift.py -q
python -m pytest tests\test_ocdd.py tests\test_feature_map_drift.py tests\test_autoencoder_representation_drift.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py tests\test_ocdd.py tests\test_feature_map_drift.py tests\test_autoencoder_representation_drift.py -q
```

Check results:

```text
py_compile: passed
DM-047 pytest: 5 passed
representation regression pytest: 15 passed
implemented numeric, streaming, supervised, multivariate, and representation pytest: 196 passed
```

Manager decision:

```text
accepted as thirty-fifth implementation loop
```

Next candidate:

```text
DM-048 Graph Embedding Drift design detail and implementation
```

## 2026-06-26 - DM-048 Graph Embedding Drift Implementation Loop

### Worker Design Detail

Worker completed the first Graph Embedding Drift design detail pass in:

- `drift_algorithm/docs/method_designs/DM-048_graph_embedding_drift.md`

Design decisions:

- classify Graph Embedding Drift under `RepresentationDriftMethod`
- continue using `drift_algorithm.methods.representationdriftmethod`
- support graph/node embedding input through `feature_cols` or `embedding_cols`
- support optional node group input through `node_group_col` / `group_col`
- support `GRAPH_EMBEDDING_MMD`, `GRAPH_EMBEDDING_CENTROID_SHIFT`, and
  `NODE_REPRESENTATION_DRIFT`
- use standardized RBF MMD for graph-level distribution comparison
- use standardized centroid shift and cosine distance for centroid movement
- use groupwise centroid shift ranking for node representation drift

### Manager Review

Manager reviewed the DM-048 design and accepted it with these constraints:

- reuse existing representation window validation and MMD helpers
- require at least two numeric embedding columns
- make grouped node analysis optional, with row-level fallback when no group
  column is supplied
- expose graph embedding score, centroid shift, cosine distance, node group
  scores, and top node group
- return `not_applicable` for unsupported variants, bad windows, missing
  columns, invalid alpha/threshold/bandwidth/permutation parameters, or
  insufficient samples/groups

Decision:

```text
accepted as implementation-ready
```

### DM-048 Graph Embedding Drift Implementation

Implemented Graph Embedding Drift.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/representationdriftmethod.py`
- `drift_algorithm/docs/method_designs/DM-048_graph_embedding_drift.md`
- `tests/test_graph_embedding_drift.py`

Implemented behavior:

- public `detect_graph_embedding_drift` function
- `GRAPH_EMBEDDING_MMD` variant with standardized RBF MMD and optional
  permutation p-value
- `GRAPH_EMBEDDING_CENTROID_SHIFT` variant with centroid shift and cosine
  distance
- `NODE_REPRESENTATION_DRIFT` variant with groupwise centroid-shift scores
- optional `node_group_col` / `group_col` support
- canonical measurements including `TEST_STATISTIC`, `P_VALUE`, and
  `DRIFT_ALARM_STATE`
- helper measurements for graph embedding drift score, centroid shift, cosine
  distance, node group scores, top node group, sample sizes, feature dimension,
  and feature columns
- explicit not-applicable handling for unsupported variants, missing feature or
  group columns, invalid alpha/threshold/bandwidth/permutation parameters,
  missing windows, too-small samples, and too-small node groups

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\representationdriftmethod.py tests\test_graph_embedding_drift.py
python -m pytest tests\test_graph_embedding_drift.py -q
python -m pytest tests\test_ocdd.py tests\test_feature_map_drift.py tests\test_autoencoder_representation_drift.py tests\test_graph_embedding_drift.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py tests\test_ocdd.py tests\test_feature_map_drift.py tests\test_autoencoder_representation_drift.py tests\test_graph_embedding_drift.py -q
```

Check results:

```text
py_compile: passed
DM-048 pytest: 5 passed
representation regression pytest: 20 passed
implemented numeric, streaming, supervised, multivariate, and representation pytest: 201 passed
```

Manager decision:

```text
accepted as thirty-sixth implementation loop
```

Next candidate:

```text
DM-049 LLM Query / Semantic Distance design detail and implementation
```

## 2026-06-26 - DM-049 LLM Query / Semantic Distance Implementation Loop

### Worker Design Detail

Worker completed the first LLM Query / Semantic Distance design detail pass in:

- `drift_algorithm/docs/method_designs/DM-049_llm_query_semantic_distance.md`

Design decisions:

- classify LLM Query / Semantic Distance under `RepresentationDriftMethod`
- continue using `drift_algorithm.methods.representationdriftmethod`
- support embedding input through `feature_cols` or `embedding_cols`
- support topic distribution input through `topic_col` / `category_col`
- support `QUERY_CENTROID_COSINE_SHIFT`,
  `TEXT_DOMAIN_CLASSIFIER_DRIFT`, and `TOPIC_DISTRIBUTION_SHIFT`
- use raw centroid cosine distance for semantic center shift
- use nearest-centroid domain separability as a dependency-free classifier
  surrogate
- use Jensen-Shannon distance for topic distribution shift

### Manager Review

Manager reviewed the DM-049 design and accepted it with these constraints:

- do not call external LLM or embedding services
- require precomputed embedding columns for embedding-based variants
- require topic/category column for topic shift
- expose canonical semantic distance, classifier, and topic measurements
- return `not_applicable` for unsupported variants, bad windows, missing
  columns, invalid thresholds, or insufficient samples

Decision:

```text
accepted as implementation-ready
```

### DM-049 LLM Query / Semantic Distance Implementation

Implemented LLM Query / Semantic Distance.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/representationdriftmethod.py`
- `drift_algorithm/docs/method_designs/DM-049_llm_query_semantic_distance.md`
- `tests/test_llm_query_semantic_distance.py`

Implemented behavior:

- public `detect_llm_query_semantic_distance` function
- `QUERY_CENTROID_COSINE_SHIFT` variant with cosine distance and centroid shift
- `TEXT_DOMAIN_CLASSIFIER_DRIFT` variant with nearest-centroid ROC-AUC surrogate
- `TOPIC_DISTRIBUTION_SHIFT` variant with Jensen-Shannon distance and maximum
  topic proportion delta
- optional topic `count_col` support
- canonical measurements including `CENTROID_SHIFT`, `COSINE_DISTANCE`,
  `ROC_AUC`, `CLASSIFIER_CONFIDENCE`, `JENSEN_SHANNON_DISTANCE`, and
  `TOPIC_PROPORTION_DELTA`
- explicit not-applicable handling for unsupported variants, missing columns,
  invalid thresholds, invalid windows, and too-small samples

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\representationdriftmethod.py tests\test_llm_query_semantic_distance.py
python -m pytest tests\test_llm_query_semantic_distance.py -q
python -m pytest tests\test_ocdd.py tests\test_feature_map_drift.py tests\test_autoencoder_representation_drift.py tests\test_graph_embedding_drift.py tests\test_llm_query_semantic_distance.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py tests\test_ocdd.py tests\test_feature_map_drift.py tests\test_autoencoder_representation_drift.py tests\test_graph_embedding_drift.py tests\test_llm_query_semantic_distance.py -q
```

Check results:

```text
py_compile: passed
DM-049 pytest: 5 passed
representation regression pytest: 25 passed
implemented numeric, streaming, supervised, multivariate, and representation pytest: 206 passed
```

Manager decision:

```text
accepted as thirty-seventh implementation loop
```

Next candidate:

```text
DM-050 Model Uncertainty Drift design detail and implementation
```

## 2026-06-26 - DM-050 Model Uncertainty Drift Implementation Loop

### Worker Output

Worker detailed the DM-050 design in
`drift_algorithm/docs/method_designs/DM-050_model_uncertainty_drift.md`.

Implementation target:

```text
module: drift_algorithm.methods.representationdriftmethod
function: detect_model_uncertainty_drift
```

Supported variants:

- `SOFTMAX_CONFIDENCE_DRIFT`
- `ENTROPY_DRIFT`
- `PREDICTIVE_VARIANCE_DRIFT`

### Manager Review

Manager reviewed the DM-050 design and accepted it with these constraints:

- use supplied model uncertainty signals only; do not train or call an external
  model
- support confidence columns, probability columns, variance columns, prediction
  columns, or explicit value columns depending on variant
- use a dependency-free two-sample KS p-value decision rule
- expose canonical uncertainty, low-confidence, sample-size, and p-value
  measurements
- return `not_applicable` for unsupported variants, missing columns, invalid
  probability/confidence/variance values, bad windows, or insufficient samples

Decision:

```text
accepted as implementation-ready
```

### DM-050 Model Uncertainty Drift Implementation

Implemented Model Uncertainty Drift.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/representationdriftmethod.py`
- `drift_algorithm/docs/method_designs/DM-050_model_uncertainty_drift.md`
- `tests/test_model_uncertainty_drift.py`

Implemented behavior:

- public `detect_model_uncertainty_drift` function
- softmax confidence drift from confidence column, probability columns, or value
  column
- entropy drift from probability columns
- predictive variance drift from variance column, prediction columns, or value
  column
- two-sample KS statistic and p-value with `p_value < alpha` decision rule
- low-confidence rate metadata for confidence variants
- explicit not-applicable handling for unsupported variants, missing columns,
  invalid thresholds, invalid windows, invalid numeric inputs, and too-small
  samples

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\representationdriftmethod.py tests\test_model_uncertainty_drift.py
python -m pytest tests\test_model_uncertainty_drift.py -q
python -m pytest tests\test_ocdd.py tests\test_feature_map_drift.py tests\test_autoencoder_representation_drift.py tests\test_graph_embedding_drift.py tests\test_llm_query_semantic_distance.py tests\test_model_uncertainty_drift.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py tests\test_ocdd.py tests\test_feature_map_drift.py tests\test_autoencoder_representation_drift.py tests\test_graph_embedding_drift.py tests\test_llm_query_semantic_distance.py tests\test_model_uncertainty_drift.py -q
```

Check results:

```text
py_compile: passed
DM-050 pytest: 5 passed
representation regression pytest: 30 passed
implemented numeric, streaming, supervised, multivariate, and representation pytest: 211 passed
```

Manager decision:

```text
accepted as thirty-eighth implementation loop
```

Next candidate:

```text
DM-051 SHAP Drift design detail and implementation
```

## 2026-06-26 - DM-051 SHAP Drift Implementation Loop

### Worker Output

Worker detailed the DM-051 design in
`drift_algorithm/docs/method_designs/DM-051_shap_drift.md`.

Implementation target:

```text
module: drift_algorithm.methods.explanationdriftmethod
function: detect_shap_drift
```

Supported variants:

- `SHAP_VALUE_DISTRIBUTION_TEST`
- `GLOBAL_IMPORTANCE_RANK_SHIFT`
- `CLASS_CONDITIONAL_SHAP_DRIFT`

### Manager Review

Manager reviewed the DM-051 design and accepted it with these constraints:

- consume already-computed SHAP values; do not compute SHAP values or call a
  model explainer
- support wide SHAP matrix columns through `shap_cols` or `feature_cols`
- use feature-wise KS tests for SHAP distribution drift
- use normalized mean absolute rank movement for global importance rank shift
- require `class_col` or `label_col` for class-conditional drift
- return `not_applicable` for unsupported variants, missing columns, invalid
  windows, invalid SHAP values, or insufficient samples

Decision:

```text
accepted as implementation-ready
```

### DM-051 SHAP Drift Implementation

Implemented SHAP Drift.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/explanationdriftmethod.py`
- `drift_algorithm/docs/method_designs/DM-051_shap_drift.md`
- `tests/test_shap_drift.py`

Implemented behavior:

- public `detect_shap_drift` function
- `SHAP_VALUE_DISTRIBUTION_TEST` variant with feature-wise two-sample KS tests
- `GLOBAL_IMPORTANCE_RANK_SHIFT` variant with mean absolute SHAP importance rank
  movement
- `CLASS_CONDITIONAL_SHAP_DRIFT` variant with class-specific feature-wise KS
  tests
- canonical measurements including `SHAP_DRIFT_DISTANCE`,
  `FEATURE_IMPORTANCE_OR_RANK`, `CLASS_SHAP_DRIFT_DISTANCE`,
  `SIGNIFICANT_FEATURES`, `TEST_STATISTIC`, `P_VALUE`, and
  `DRIFT_ALARM_STATE`
- explicit not-applicable handling for unsupported variants, missing columns,
  invalid thresholds, invalid windows, invalid SHAP values, missing class column,
  and too-small samples

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\explanationdriftmethod.py tests\test_shap_drift.py
python -m pytest tests\test_shap_drift.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py tests\test_ocdd.py tests\test_feature_map_drift.py tests\test_autoencoder_representation_drift.py tests\test_graph_embedding_drift.py tests\test_llm_query_semantic_distance.py tests\test_model_uncertainty_drift.py tests\test_shap_drift.py -q
```

Check results:

```text
py_compile: passed
DM-051 pytest: 5 passed
implemented numeric, streaming, supervised, multivariate, representation, and explanation pytest: 216 passed
```

Manager decision:

```text
accepted as thirty-ninth implementation loop
```

Next candidate:

```text
DM-052 Tree Feature 기반 감지 design detail and implementation
```

## 2026-06-26 - DM-052 Tree Feature 기반 감지 Implementation Loop

### Worker Output

Worker detailed the DM-052 design in
`drift_algorithm/docs/method_designs/DM-052_tree_feature.md`.

Implementation target:

```text
module: drift_algorithm.methods.explanationdriftmethod
function: detect_tree_feature
```

Supported variants:

- `TIME_FEATURE_SPLIT_DETECTOR`
- `DOMAIN_CLASSIFIER_TREE`

### Manager Review

Manager reviewed the DM-052 design and accepted it with these constraints:

- use a deterministic decision-stump surrogate instead of adding a full tree
  learner dependency
- support numeric feature matrices through `feature_cols`
- require `time_feature_col` to be present in `feature_cols` for time-feature
  split detection
- report feature importance, split threshold, split direction, split accuracy,
  and ROC-AUC metadata
- return `not_applicable` for unsupported variants, missing columns, invalid
  windows, invalid thresholds, invalid feature values, or insufficient samples

Decision:

```text
accepted as implementation-ready
```

### DM-052 Tree Feature 기반 감지 Implementation

Implemented Tree Feature 기반 감지.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/explanationdriftmethod.py`
- `drift_algorithm/docs/method_designs/DM-052_tree_feature.md`
- `tests/test_tree_feature.py`

Implemented behavior:

- public `detect_tree_feature` function
- `TIME_FEATURE_SPLIT_DETECTOR` variant with time/period feature shallow-split
  detection
- `DOMAIN_CLASSIFIER_TREE` variant with best univariate domain-classifier stump
  ROC-AUC
- canonical measurements including `TREE_SPLIT_SIGNAL`, `ROC_AUC`,
  `FEATURE_IMPORTANCE_OR_RANK`, `TEST_STATISTIC`, and `DRIFT_ALARM_STATE`
- explicit not-applicable handling for unsupported variants, missing columns,
  invalid thresholds, invalid windows, invalid feature values, and too-small
  samples

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\explanationdriftmethod.py tests\test_tree_feature.py
python -m pytest tests\test_tree_feature.py -q
python -m pytest tests\test_shap_drift.py tests\test_tree_feature.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py tests\test_ocdd.py tests\test_feature_map_drift.py tests\test_autoencoder_representation_drift.py tests\test_graph_embedding_drift.py tests\test_llm_query_semantic_distance.py tests\test_model_uncertainty_drift.py tests\test_shap_drift.py tests\test_tree_feature.py -q
```

Check results:

```text
py_compile: passed
DM-052 pytest: 5 passed
explanation regression pytest: 10 passed
implemented numeric, streaming, supervised, multivariate, representation, and explanation pytest: 221 passed
```

Manager decision:

```text
accepted as fortieth implementation loop
```

Next candidate:

```text
DM-053 Classifier Embedding Drift Detection design detail and implementation
```

## 2026-06-26 - DM-053 Classifier Embedding Drift Detection Implementation Loop

### Worker Output

Worker detailed the DM-053 design in
`drift_algorithm/docs/method_designs/DM-053_classifier_embedding_drift_detection.md`.

Implementation target:

```text
module: drift_algorithm.methods.domainclassifiermethod
function: detect_classifier_embedding_drift_detection
```

Supported variants:

- `DOMAIN_CLASSIFIER_ROC_AUC`
- `DOMAIN_CLASSIFIER_PROBABILITY_DRIFT`
- `CROSS_VALIDATED_DOMAIN_CLASSIFIER`

### Manager Review

Manager reviewed the DM-053 design and accepted it with these constraints:

- use precomputed embedding columns only
- use a deterministic centroid-domain classifier surrogate instead of adding a
  trained classifier dependency
- report ROC-AUC, current-class probability movement, high-probability tail
  rate, and blocked fold scores where applicable
- return `not_applicable` for unsupported variants, missing columns, invalid
  windows, invalid embedding values, invalid thresholds, or insufficient samples

Decision:

```text
accepted as implementation-ready
```

### DM-053 Classifier Embedding Drift Detection Implementation

Implemented Classifier Embedding Drift Detection.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/domainclassifiermethod.py`
- `drift_algorithm/docs/method_designs/DM-053_classifier_embedding_drift_detection.md`
- `tests/test_classifier_embedding_drift.py`

Implemented behavior:

- public `detect_classifier_embedding_drift_detection` function
- `DOMAIN_CLASSIFIER_ROC_AUC` variant with centroid-domain ROC-AUC
- `DOMAIN_CLASSIFIER_PROBABILITY_DRIFT` variant with current-class probability
  KS test
- `CROSS_VALIDATED_DOMAIN_CLASSIFIER` variant with blocked-fold centroid AUC
- canonical measurements including `ROC_AUC`, `DOMAIN_CLASSIFIER_SCORE`,
  `PROBABILITY_MEAN_REFERENCE`, `PROBABILITY_MEAN_CURRENT`,
  `HIGH_CURRENT_PROBABILITY_RATE`, and `CROSS_VALIDATION_FOLD_SCORES`
- explicit not-applicable handling for unsupported variants, missing columns,
  invalid thresholds, invalid windows, invalid embedding values, and too-small
  samples

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\domainclassifiermethod.py tests\test_classifier_embedding_drift.py
python -m pytest tests\test_classifier_embedding_drift.py -q
python -m pytest tests\test_classifier_embedding_drift.py tests\test_shap_drift.py tests\test_tree_feature.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py tests\test_ocdd.py tests\test_feature_map_drift.py tests\test_autoencoder_representation_drift.py tests\test_graph_embedding_drift.py tests\test_llm_query_semantic_distance.py tests\test_model_uncertainty_drift.py tests\test_shap_drift.py tests\test_tree_feature.py tests\test_classifier_embedding_drift.py -q
```

Check results:

```text
py_compile: passed
DM-053 pytest: 5 passed
domain/explanation regression pytest: 15 passed
implemented numeric, streaming, supervised, multivariate, representation, explanation, and domain-classifier pytest: 226 passed
```

Manager decision:

```text
accepted as forty-first implementation loop
```

Next candidate:

```text
DM-054 Text Domain Classifier Drift design detail and implementation
```

## 2026-06-26 - DM-054 Text Domain Classifier Drift Implementation Loop

### Worker Output

Worker detailed the DM-054 design in
`drift_algorithm/docs/method_designs/DM-054_text_domain_classifier_drift.md`.

Implementation target:

```text
module: drift_algorithm.methods.domainclassifiermethod
function: detect_text_domain_classifier_drift
```

Supported variants:

- `TEXT_DOMAIN_CLASSIFIER_ROC_AUC`
- `TEXT_DOMAIN_CLASSIFIER_STAT_TEST`
- `TEXT_DESCRIPTOR_DRIFT`

### Manager Review

Manager reviewed the DM-054 design and accepted it with these constraints:

- avoid external NLP or classifier dependencies
- vectorize raw text with a deterministic bag-of-words representation
- allow supplied embedding/feature columns for classifier variants
- allow numeric descriptor columns for descriptor drift
- return `not_applicable` for unsupported variants, missing columns, invalid
  windows, empty token vocabulary, invalid numeric values, invalid thresholds,
  or insufficient samples

Decision:

```text
accepted as implementation-ready
```

### DM-054 Text Domain Classifier Drift Implementation

Implemented Text Domain Classifier Drift.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/domainclassifiermethod.py`
- `drift_algorithm/docs/method_designs/DM-054_text_domain_classifier_drift.md`
- `tests/test_text_domain_classifier_drift.py`

Implemented behavior:

- public `detect_text_domain_classifier_drift` function
- `TEXT_DOMAIN_CLASSIFIER_ROC_AUC` variant with bag-of-words or supplied vector
  centroid-domain ROC-AUC
- `TEXT_DOMAIN_CLASSIFIER_STAT_TEST` variant with classifier probability KS test
- `TEXT_DESCRIPTOR_DRIFT` variant with numeric descriptor KS tests
- canonical measurements including `ROC_AUC`, `DOMAIN_CLASSIFIER_SCORE`,
  `TEXT_DOMAIN_CLASSIFIER_STATISTIC`, `TEXT_DESCRIPTOR_DRIFT`,
  `SIGNIFICANT_DESCRIPTORS`, probability mean/tail metrics, and sample sizes
- explicit not-applicable handling for unsupported variants, missing columns,
  invalid thresholds, invalid windows, invalid text/vector/descriptor input, and
  too-small samples

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\domainclassifiermethod.py tests\test_text_domain_classifier_drift.py
python -m pytest tests\test_text_domain_classifier_drift.py -q
python -m pytest tests\test_classifier_embedding_drift.py tests\test_text_domain_classifier_drift.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py tests\test_ocdd.py tests\test_feature_map_drift.py tests\test_autoencoder_representation_drift.py tests\test_graph_embedding_drift.py tests\test_llm_query_semantic_distance.py tests\test_model_uncertainty_drift.py tests\test_shap_drift.py tests\test_tree_feature.py tests\test_classifier_embedding_drift.py tests\test_text_domain_classifier_drift.py -q
```

Check results:

```text
py_compile: passed
DM-054 pytest: 5 passed
domain-classifier regression pytest: 10 passed
implemented numeric, streaming, supervised, multivariate, representation, explanation, and domain-classifier pytest: 231 passed
```

Manager decision:

```text
accepted as forty-second implementation loop
```

Next candidate:

```text
DM-055 HAT design detail and implementation
```

## 2026-06-26 - DM-055 HAT Implementation Loop

### Worker Output

Worker detailed the DM-055 design in
`drift_algorithm/docs/method_designs/DM-055_hat.md`.

Implementation target:

```text
module: drift_algorithm.methods.operationaladaptationmethod
function: detect_hat
```

Supported variants:

- `HAT_ADWIN_NODE_MONITORING`
- `HAT_ALTERNATE_TREE_REPLACEMENT`

### Manager Review

Manager reviewed the DM-055 design and accepted it with these constraints:

- consume finite HAT-like operational logs rather than training a Hoeffding
  Adaptive Tree
- support 0/1 error streams or `y_true`/`y_pred` label streams
- support optional node, online accuracy, alternate-created, and replacement
  event columns
- report adaptation events, node drift states, online/pre-post performance, and
  drift alarm state
- return `not_applicable` for unsupported variants, missing columns, invalid
  windows, non-binary errors, invalid thresholds, or insufficient samples

Decision:

```text
accepted as implementation-ready
```

### DM-055 HAT Implementation

Implemented HAT operational replay.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/operationaladaptationmethod.py`
- `drift_algorithm/docs/method_designs/DM-055_hat.md`
- `tests/test_hat.py`

Implemented behavior:

- public `detect_hat` function
- `HAT_ADWIN_NODE_MONITORING` variant with global and node-level error-rate
  delta alarm states
- `HAT_ALTERNATE_TREE_REPLACEMENT` variant with alternate tree creation and
  replacement event replay
- canonical measurements including `ADAPTATION_EVENT`, `DRIFT_ALARM_STATE`,
  `ONLINE_OR_PRE_POST_PERFORMANCE`, `NODE_DRIFT_STATE`, `NODE_ALARM_COUNT`, and
  `HAT_STATISTIC`
- explicit not-applicable handling for unsupported variants, missing columns,
  invalid thresholds, invalid windows, non-binary errors, and too-small samples

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\operationaladaptationmethod.py tests\test_hat.py
python -m pytest tests\test_hat.py -q
python -m pytest tests\test_hat.py tests\test_classifier_embedding_drift.py tests\test_text_domain_classifier_drift.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py tests\test_ocdd.py tests\test_feature_map_drift.py tests\test_autoencoder_representation_drift.py tests\test_graph_embedding_drift.py tests\test_llm_query_semantic_distance.py tests\test_model_uncertainty_drift.py tests\test_shap_drift.py tests\test_tree_feature.py tests\test_classifier_embedding_drift.py tests\test_text_domain_classifier_drift.py tests\test_hat.py -q
```

Check results:

```text
py_compile: passed
DM-055 pytest: 5 passed
operational/domain regression pytest: 15 passed
implemented numeric, streaming, supervised, multivariate, representation, explanation, domain-classifier, and operational pytest: 236 passed
```

Manager decision:

```text
accepted as forty-third implementation loop
```

Next candidate:

```text
DM-056 DriftRetrainingClassifier design detail and implementation
```

## 2026-06-26 - DM-056 DriftRetrainingClassifier Implementation Loop

### Worker Output

Worker detailed the DM-056 design in
`drift_algorithm/docs/method_designs/DM-056_driftretrainingclassifier.md`.

Implementation target:

```text
module: drift_algorithm.methods.operationaladaptationmethod
function: detect_driftretrainingclassifier
```

Supported variants:

- `DRIFT_RETRAINING_WITH_ADWIN`
- `DRIFT_RETRAINING_WITH_PAGE_HINKLEY`
- `DRIFT_RETRAINING_CHAMPION_CHALLENGER`

### Manager Review

Manager reviewed the DM-056 design and accepted it with these constraints:

- consume operational logs rather than training, retraining, deploying, or
  promoting a model
- support numeric metric streams or label-derived 0/1 error streams
- support retraining trigger and model promotion event flags
- support champion/challenger metric comparison for promotion recommendation
- return `not_applicable` for unsupported variants, missing columns, invalid
  windows, invalid metric values, invalid thresholds, or insufficient samples

Decision:

```text
accepted as implementation-ready
```

### DM-056 DriftRetrainingClassifier Implementation

Implemented DriftRetrainingClassifier operational replay.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/operationaladaptationmethod.py`
- `drift_algorithm/docs/method_designs/DM-056_driftretrainingclassifier.md`
- `tests/test_drift_retraining_classifier.py`

Implemented behavior:

- public `detect_driftretrainingclassifier` function
- `DRIFT_RETRAINING_WITH_ADWIN` variant with metric mean movement retraining
  trigger surrogate
- `DRIFT_RETRAINING_WITH_PAGE_HINKLEY` variant with cumulative metric
  degradation trigger surrogate
- `DRIFT_RETRAINING_CHAMPION_CHALLENGER` variant with champion/challenger uplift
  and promotion decision metadata
- canonical measurements including `RETRAINING_EVENT`, `ADAPTATION_EVENT`,
  `ONLINE_OR_PRE_POST_PERFORMANCE`, `RETRAINING_CANDIDATE_WINDOW`,
  `PROMOTION_DECISION`, and `CHAMPION_CHALLENGER_UPLIFT`
- explicit not-applicable handling for unsupported variants, missing columns,
  invalid thresholds, invalid windows, invalid metric values, and too-small
  samples

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\operationaladaptationmethod.py tests\test_drift_retraining_classifier.py
python -m pytest tests\test_drift_retraining_classifier.py -q
python -m pytest tests\test_hat.py tests\test_drift_retraining_classifier.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py tests\test_ocdd.py tests\test_feature_map_drift.py tests\test_autoencoder_representation_drift.py tests\test_graph_embedding_drift.py tests\test_llm_query_semantic_distance.py tests\test_model_uncertainty_drift.py tests\test_shap_drift.py tests\test_tree_feature.py tests\test_classifier_embedding_drift.py tests\test_text_domain_classifier_drift.py tests\test_hat.py tests\test_drift_retraining_classifier.py -q
```

Check results:

```text
py_compile: passed
DM-056 pytest: 5 passed
operational regression pytest: 10 passed
implemented numeric, streaming, supervised, multivariate, representation, explanation, domain-classifier, and operational pytest: 241 passed
```

Manager decision:

```text
accepted as forty-fourth implementation loop
```

Sequential implementation status:

```text
DM-025 through DM-056 completed, excluding previously skipped DM-034 and held DM-003 through DM-013.
```

## 2026-06-26 - DM-003 Chi-square Test Implementation Loop

### DM-003 Chi-square Test Implementation

Implemented Chi-square Test.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/batchdistributioncomparison.py`
- `drift_algorithm/docs/method_designs/DM-003_chi_square_test.md`
- `tests/test_chi_square_test.py`

Implemented behavior:

- public `detect_chi_square_test` function
- `CHI_SQUARE_GOODNESS_OF_FIT` with reference-derived expected proportions
- `CHI_SQUARE_HOMOGENEITY` over reference/current category count tables
- `CHI_SQUARE_WITH_LOW_EXPECTED_COUNT_CAUTION` with expected-count diagnostics
- long categorical count input through `category_col` and optional `count_col`
- canonical measurements including `TEST_STATISTIC`, `P_VALUE`,
  `DEGREES_OF_FREEDOM`, category counts/proportion deltas, residuals, and low
  expected-count diagnostics
- explicit not-applicable handling for unsupported variants, missing columns,
  invalid windows, invalid counts, too few categories, zero expected counts, and
  insufficient samples

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py drift_algorithm\methods\__init__.py drift_algorithm\__init__.py tests\test_chi_square_test.py
python -m pytest tests\test_chi_square_test.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_chi_square_test.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_chi_square_test.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py tests\test_ocdd.py tests\test_feature_map_drift.py tests\test_autoencoder_representation_drift.py tests\test_graph_embedding_drift.py tests\test_llm_query_semantic_distance.py tests\test_model_uncertainty_drift.py tests\test_shap_drift.py tests\test_tree_feature.py tests\test_classifier_embedding_drift.py tests\test_text_domain_classifier_drift.py tests\test_hat.py tests\test_drift_retraining_classifier.py -q
```

Check results:

```text
py_compile: passed
DM-003 pytest: 5 passed
DM-001/002/003 batch regression pytest: 17 passed
implemented numeric, categorical, streaming, supervised, multivariate, representation, explanation, domain-classifier, and operational pytest: 246 passed
```

Next candidate:

```text
DM-004 Fisher's Exact Test design detail and implementation
```

## 2026-06-26 - DM-004 Fisher's Exact Test Implementation Loop

### DM-004 Fisher's Exact Test Implementation

Implemented Fisher's Exact Test.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/batchdistributioncomparison.py`
- `drift_algorithm/docs/method_designs/DM-004_fisher_s_exact_test.md`
- `tests/test_fisher_s_exact_test.py`

Implemented behavior:

- public `detect_fisher_s_exact_test` function
- `TWO_BY_TWO_FISHER_EXACT` using SciPy Fisher exact test
- `ONE_SIDED_FISHER_EXACT` using SciPy Fisher exact test with one-sided
  alternative
- `EXTENDED_CONTINGENCY_EXACT_TEST` using a deterministic permutation exact-test
  surrogate for 2xK contingency tables
- long categorical count input through `category_col` and optional `count_col`
- canonical measurements including `TEST_STATISTIC`, `P_VALUE`, `ODDS_RATIO`,
  category counts, and category proportion deltas
- explicit not-applicable handling for unsupported variants, missing columns,
  invalid windows, invalid alternatives, invalid counts, incompatible table
  shape, and insufficient samples

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py drift_algorithm\methods\__init__.py drift_algorithm\__init__.py tests\test_fisher_s_exact_test.py
python -m pytest tests\test_fisher_s_exact_test.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_chi_square_test.py tests\test_fisher_s_exact_test.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_chi_square_test.py tests\test_fisher_s_exact_test.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py tests\test_ocdd.py tests\test_feature_map_drift.py tests\test_autoencoder_representation_drift.py tests\test_graph_embedding_drift.py tests\test_llm_query_semantic_distance.py tests\test_model_uncertainty_drift.py tests\test_shap_drift.py tests\test_tree_feature.py tests\test_classifier_embedding_drift.py tests\test_text_domain_classifier_drift.py tests\test_hat.py tests\test_drift_retraining_classifier.py -q
```

Check results:

```text
py_compile: passed
DM-004 pytest: 5 passed
DM-001/002/003/004 batch regression pytest: 22 passed
implemented numeric, categorical, streaming, supervised, multivariate, representation, explanation, domain-classifier, and operational pytest: 251 passed
```

Next candidate:

```text
DM-005 G-test design detail and implementation
```

## 2026-06-26 - DM-005 G-test Implementation Loop

### DM-005 G-test Implementation

Implemented G-test.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/batchdistributioncomparison.py`
- `drift_algorithm/docs/method_designs/DM-005_g_test.md`
- `tests/test_g_test.py`

Implemented behavior:

- public `detect_g_test` function
- `LIKELIHOOD_RATIO_G_TEST_GOF` with reference-derived expected proportions
- `LIKELIHOOD_RATIO_G_TEST_INDEPENDENCE` over reference/current contingency
  tables
- `G_TEST_WITH_SMALL_COUNT_CAUTION` with expected-count diagnostics
- long categorical count input through `category_col` and optional `count_col`
- canonical measurements including `TEST_STATISTIC`, `G_STATISTIC`, `P_VALUE`,
  degrees of freedom, category counts/proportion deltas, and small expected
  count diagnostics
- explicit not-applicable handling for unsupported variants, missing columns,
  invalid windows, invalid counts, too few categories, zero expected counts, and
  insufficient samples

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py tests\test_g_test.py
python -m pytest tests\test_g_test.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_chi_square_test.py tests\test_fisher_s_exact_test.py tests\test_g_test.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_chi_square_test.py tests\test_fisher_s_exact_test.py tests\test_g_test.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py tests\test_ocdd.py tests\test_feature_map_drift.py tests\test_autoencoder_representation_drift.py tests\test_graph_embedding_drift.py tests\test_llm_query_semantic_distance.py tests\test_model_uncertainty_drift.py tests\test_shap_drift.py tests\test_tree_feature.py tests\test_classifier_embedding_drift.py tests\test_text_domain_classifier_drift.py tests\test_hat.py tests\test_drift_retraining_classifier.py -q
```

Check results:

```text
py_compile: passed
DM-005 pytest: 5 passed
DM-001 through DM-005 batch regression pytest: 27 passed
implemented numeric, categorical, streaming, supervised, multivariate, representation, explanation, domain-classifier, and operational pytest: 256 passed
```

Next candidate:

```text
DM-006 PSI design detail and implementation
```

## 2026-06-26 - DM-006 PSI Implementation Loop

### DM-006 PSI Implementation

Implemented PSI.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/batchdistributioncomparison.py`
- `drift_algorithm/docs/method_designs/DM-006_psi.md`
- `tests/test_psi.py`

Implemented behavior:

- public `detect_psi` function
- `NUMERIC_BINNED_PSI` with reference quantile bins
- `CATEGORICAL_PSI`, `SCORE_BAND_PSI`, and `POPULATION_WEIGHTED_PSI` over
  category/count tables
- threshold-based alarm without p-value
- canonical measurements including `PSI_SCORE`, `PSI_CONTRIBUTION`, category
  counts, sample sizes, and alarm state
- explicit not-applicable handling for unsupported variants, missing columns,
  invalid windows, constant numeric reference values, invalid counts, invalid
  thresholds, and too-small samples

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py tests\test_psi.py
python -m pytest tests\test_psi.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_chi_square_test.py tests\test_fisher_s_exact_test.py tests\test_g_test.py tests\test_psi.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_chi_square_test.py tests\test_fisher_s_exact_test.py tests\test_g_test.py tests\test_psi.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py tests\test_ocdd.py tests\test_feature_map_drift.py tests\test_autoencoder_representation_drift.py tests\test_graph_embedding_drift.py tests\test_llm_query_semantic_distance.py tests\test_model_uncertainty_drift.py tests\test_shap_drift.py tests\test_tree_feature.py tests\test_classifier_embedding_drift.py tests\test_text_domain_classifier_drift.py tests\test_hat.py tests\test_drift_retraining_classifier.py -q
```

Check results:

```text
py_compile: passed
DM-006 pytest: 5 passed
DM-001 through DM-006 batch regression pytest: 32 passed
implemented numeric, categorical, streaming, supervised, multivariate, representation, explanation, domain-classifier, and operational pytest: 261 passed
```

Next candidate:

```text
DM-007 KL Divergence design detail and implementation
```

## 2026-06-26 - DM-007 KL Divergence Implementation Loop

### DM-007 KL Divergence Implementation

Implemented KL Divergence.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/batchdistributioncomparison.py`
- `drift_algorithm/docs/method_designs/DM-007_kl_divergence.md`
- `tests/test_kl_divergence.py`

Implemented behavior:

- public `detect_kl_divergence` function
- `DISCRETE_KL_DIVERGENCE`, `HISTOGRAM_KL_DIVERGENCE`,
  `SMOOTHED_KL_DIVERGENCE`, and `SYMMETRIZED_KL`
- categorical/count-table KL and numeric histogram KL using reference quantile
  bins
- epsilon smoothing before probability normalization
- threshold-based alarm without p-value
- canonical measurements including directional KL values, contribution rows,
  category counts, sample sizes, and alarm state
- explicit not-applicable handling for unsupported variants, missing columns,
  invalid windows, invalid counts, constant numeric reference values, invalid
  thresholds, invalid smoothing epsilon, and too-small samples

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py tests\test_kl_divergence.py
python -m pytest tests\test_kl_divergence.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_chi_square_test.py tests\test_fisher_s_exact_test.py tests\test_g_test.py tests\test_psi.py tests\test_kl_divergence.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_chi_square_test.py tests\test_fisher_s_exact_test.py tests\test_g_test.py tests\test_psi.py tests\test_kl_divergence.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py tests\test_ocdd.py tests\test_feature_map_drift.py tests\test_autoencoder_representation_drift.py tests\test_graph_embedding_drift.py tests\test_llm_query_semantic_distance.py tests\test_model_uncertainty_drift.py tests\test_shap_drift.py tests\test_tree_feature.py tests\test_classifier_embedding_drift.py tests\test_text_domain_classifier_drift.py tests\test_hat.py tests\test_drift_retraining_classifier.py -q
```

Check results:

```text
py_compile: passed
DM-007 pytest: 5 passed
DM-001 through DM-007 batch regression pytest: 37 passed
implemented numeric, categorical, streaming, supervised, multivariate, representation, explanation, domain-classifier, and operational pytest: 266 passed
```

Next candidate:

```text
DM-008 Jensen-Shannon Distance design detail and implementation
```

## 2026-06-26 - DM-008 Jensen-Shannon Distance Implementation Loop

### DM-008 Jensen-Shannon Distance Implementation

Implemented Jensen-Shannon Distance.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/batchdistributioncomparison.py`
- `drift_algorithm/docs/method_designs/DM-008_jensen_shannon_distance.md`
- `tests/test_jensen_shannon_distance.py`

Implemented behavior:

- public `detect_jensen_shannon_distance` function
- `JENSEN_SHANNON_DIVERGENCE`
- `JENSEN_SHANNON_DISTANCE`
- `MULTICLASS_PROBABILITY_JS`
- `TEXT_TOPIC_JS`
- categorical/count-table probability distributions
- numeric histogram support for `JENSEN_SHANNON_DIVERGENCE` and
  `JENSEN_SHANNON_DISTANCE` with
  `input_mode="numeric_histogram"`
- base-2 JS divergence and square-root JS distance measurements
- threshold-based alarm without p-value
- canonical measurements including `JENSEN_SHANNON_DIVERGENCE`,
  `JENSEN_SHANNON_DISTANCE`, `TEST_STATISTIC`, `DRIFT_ALARM_STATE`,
  contribution rows, category proportion deltas, category counts, and sample
  sizes
- explicit not-applicable handling for unsupported variants, missing columns,
  invalid windows, invalid counts, constant numeric reference values, invalid
  thresholds, invalid smoothing epsilon, and too-small samples

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py drift_algorithm\methods\__init__.py drift_algorithm\__init__.py tests\test_jensen_shannon_distance.py
python -m pytest tests\test_jensen_shannon_distance.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_chi_square_test.py tests\test_fisher_s_exact_test.py tests\test_g_test.py tests\test_psi.py tests\test_kl_divergence.py tests\test_jensen_shannon_distance.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_chi_square_test.py tests\test_fisher_s_exact_test.py tests\test_g_test.py tests\test_psi.py tests\test_kl_divergence.py tests\test_jensen_shannon_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py tests\test_ocdd.py tests\test_feature_map_drift.py tests\test_autoencoder_representation_drift.py tests\test_graph_embedding_drift.py tests\test_llm_query_semantic_distance.py tests\test_model_uncertainty_drift.py tests\test_shap_drift.py tests\test_tree_feature.py tests\test_classifier_embedding_drift.py tests\test_text_domain_classifier_drift.py tests\test_hat.py tests\test_drift_retraining_classifier.py -q
```

Check results:

```text
py_compile: passed
DM-008 pytest: 6 passed
DM-001 through DM-008 batch regression pytest: 43 passed
implemented numeric, categorical, streaming, supervised, multivariate, representation, explanation, domain-classifier, and operational pytest: 272 passed
```

Next candidate:

```text
DM-009 Hellinger Distance design detail and implementation
```

## 2026-06-26 - DM-009 Hellinger Distance Implementation Loop

### DM-009 Hellinger Distance Implementation

Implemented Hellinger Distance.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/batchdistributioncomparison.py`
- `drift_algorithm/docs/method_designs/DM-009_hellinger_distance.md`
- `tests/test_hellinger_distance.py`

Implemented behavior:

- public `detect_hellinger_distance` function
- `DISCRETE_HELLINGER_DISTANCE`
- `HISTOGRAM_HELLINGER_DISTANCE`
- `CATEGORICAL_HELLINGER_DISTANCE`
- categorical/count-table probability distributions
- numeric histogram support for `HISTOGRAM_HELLINGER_DISTANCE`
- bounded Hellinger distance score
- threshold-based alarm without p-value
- canonical measurements including `HELLINGER_DISTANCE`, `TEST_STATISTIC`,
  `DRIFT_ALARM_STATE`, contribution rows, category proportion deltas, category
  counts, and sample sizes
- explicit not-applicable handling for unsupported variants, missing columns,
  invalid windows, invalid counts, constant numeric reference values, invalid
  thresholds, and too-small samples

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py drift_algorithm\methods\__init__.py drift_algorithm\__init__.py tests\test_hellinger_distance.py
python -m pytest tests\test_hellinger_distance.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_chi_square_test.py tests\test_fisher_s_exact_test.py tests\test_g_test.py tests\test_psi.py tests\test_kl_divergence.py tests\test_jensen_shannon_distance.py tests\test_hellinger_distance.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_chi_square_test.py tests\test_fisher_s_exact_test.py tests\test_g_test.py tests\test_psi.py tests\test_kl_divergence.py tests\test_jensen_shannon_distance.py tests\test_hellinger_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py tests\test_ocdd.py tests\test_feature_map_drift.py tests\test_autoencoder_representation_drift.py tests\test_graph_embedding_drift.py tests\test_llm_query_semantic_distance.py tests\test_model_uncertainty_drift.py tests\test_shap_drift.py tests\test_tree_feature.py tests\test_classifier_embedding_drift.py tests\test_text_domain_classifier_drift.py tests\test_hat.py tests\test_drift_retraining_classifier.py -q
```

Check results:

```text
py_compile: passed
DM-009 pytest: 5 passed
DM-001 through DM-009 batch regression pytest: 48 passed
implemented numeric, categorical, streaming, supervised, multivariate, representation, explanation, domain-classifier, and operational pytest: 277 passed
```

Next candidate:

```text
DM-010 Total Variation Distance design detail and implementation
```

## 2026-06-26 - DM-010 Total Variation Distance Implementation Loop

### DM-010 Total Variation Distance Implementation

Implemented Total Variation Distance.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/batchdistributioncomparison.py`
- `drift_algorithm/docs/method_designs/DM-010_total_variation_distance.md`
- `tests/test_total_variation_distance.py`

Implemented behavior:

- public `detect_total_variation_distance` function
- `CATEGORICAL_TOTAL_VARIATION`
- `HISTOGRAM_TOTAL_VARIATION`
- `PROBABILITY_VECTOR_TOTAL_VARIATION`
- categorical/count-table probability distributions
- numeric histogram support for `HISTOGRAM_TOTAL_VARIATION`
- probability-vector variant through the category/count probability-vector
  contract
- bounded total variation distance score
- threshold-based alarm without p-value
- canonical measurements including `TOTAL_VARIATION_DISTANCE`,
  `TEST_STATISTIC`, `DRIFT_ALARM_STATE`, contribution rows, category proportion
  deltas, category counts, and sample sizes
- explicit not-applicable handling for unsupported variants, missing columns,
  invalid windows, invalid counts, constant numeric reference values, invalid
  thresholds, and too-small samples

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py drift_algorithm\methods\__init__.py drift_algorithm\__init__.py tests\test_total_variation_distance.py
python -m pytest tests\test_total_variation_distance.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_chi_square_test.py tests\test_fisher_s_exact_test.py tests\test_g_test.py tests\test_psi.py tests\test_kl_divergence.py tests\test_jensen_shannon_distance.py tests\test_hellinger_distance.py tests\test_total_variation_distance.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_chi_square_test.py tests\test_fisher_s_exact_test.py tests\test_g_test.py tests\test_psi.py tests\test_kl_divergence.py tests\test_jensen_shannon_distance.py tests\test_hellinger_distance.py tests\test_total_variation_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py tests\test_ocdd.py tests\test_feature_map_drift.py tests\test_autoencoder_representation_drift.py tests\test_graph_embedding_drift.py tests\test_llm_query_semantic_distance.py tests\test_model_uncertainty_drift.py tests\test_shap_drift.py tests\test_tree_feature.py tests\test_classifier_embedding_drift.py tests\test_text_domain_classifier_drift.py tests\test_hat.py tests\test_drift_retraining_classifier.py -q
```

Check results:

```text
py_compile: passed
DM-010 pytest: 5 passed
DM-001 through DM-010 batch regression pytest: 53 passed
implemented numeric, categorical, streaming, supervised, multivariate, representation, explanation, domain-classifier, and operational pytest: 282 passed
```

Next candidate:

```text
DM-011 L-Infinity Distance design detail and implementation
```

## 2026-06-26 - DM-011 L-Infinity Distance Implementation Loop

### DM-011 L-Infinity Distance Implementation

Implemented L-Infinity Distance.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/batchdistributioncomparison.py`
- `drift_algorithm/docs/method_designs/DM-011_l_infinity_distance.md`
- `tests/test_l_infinity_distance.py`

Implemented behavior:

- public `detect_l_infinity_distance` function
- `CATEGORICAL_L_INFINITY`
- `PROBABILITY_VECTOR_L_INFINITY`
- `BINNED_NUMERIC_L_INFINITY`
- categorical/count-table probability distributions
- numeric histogram support for `BINNED_NUMERIC_L_INFINITY`
- probability-vector variant through the category/count probability-vector
  contract
- bounded max absolute proportion delta score
- threshold-based alarm without p-value
- canonical measurements including `L_INFINITY_DISTANCE`,
  `MAX_ABSOLUTE_PROPORTION_DELTA`, `MAX_COMPONENT`, `TEST_STATISTIC`,
  `DRIFT_ALARM_STATE`, contribution rows, category proportion deltas, category
  counts, and sample sizes
- explicit not-applicable handling for unsupported variants, missing columns,
  invalid windows, invalid counts, constant numeric reference values, invalid
  thresholds, and too-small samples

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py drift_algorithm\methods\__init__.py drift_algorithm\__init__.py tests\test_l_infinity_distance.py
python -m pytest tests\test_l_infinity_distance.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_chi_square_test.py tests\test_fisher_s_exact_test.py tests\test_g_test.py tests\test_psi.py tests\test_kl_divergence.py tests\test_jensen_shannon_distance.py tests\test_hellinger_distance.py tests\test_total_variation_distance.py tests\test_l_infinity_distance.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_chi_square_test.py tests\test_fisher_s_exact_test.py tests\test_g_test.py tests\test_psi.py tests\test_kl_divergence.py tests\test_jensen_shannon_distance.py tests\test_hellinger_distance.py tests\test_total_variation_distance.py tests\test_l_infinity_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py tests\test_ocdd.py tests\test_feature_map_drift.py tests\test_autoencoder_representation_drift.py tests\test_graph_embedding_drift.py tests\test_llm_query_semantic_distance.py tests\test_model_uncertainty_drift.py tests\test_shap_drift.py tests\test_tree_feature.py tests\test_classifier_embedding_drift.py tests\test_text_domain_classifier_drift.py tests\test_hat.py tests\test_drift_retraining_classifier.py -q
```

Check results:

```text
py_compile: passed
DM-011 pytest: 5 passed
DM-001 through DM-011 batch regression pytest: 58 passed
implemented numeric, categorical, streaming, supervised, multivariate, representation, explanation, domain-classifier, and operational pytest: 287 passed
```

Next candidate:

```text
DM-012 Bhattacharyya Distance design detail and implementation
```

## 2026-06-26 - DM-012 Bhattacharyya Distance Implementation Loop

### DM-012 Bhattacharyya Distance Implementation

Implemented Bhattacharyya Distance.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/batchdistributioncomparison.py`
- `drift_algorithm/docs/method_designs/DM-012_bhattacharyya_distance.md`
- `tests/test_bhattacharyya_distance.py`

Implemented behavior:

- public `detect_bhattacharyya_distance` function
- `DISCRETE_BHATTACHARYYA_DISTANCE`
- `GAUSSIAN_BHATTACHARYYA_DISTANCE`
- `HISTOGRAM_BHATTACHARYYA_DISTANCE`
- categorical/count-table probability distributions
- numeric histogram support for `HISTOGRAM_BHATTACHARYYA_DISTANCE`
- univariate numeric Gaussian summary support for
  `GAUSSIAN_BHATTACHARYYA_DISTANCE`
- Bhattacharyya coefficient and distance measurements
- threshold-based alarm without p-value
- canonical measurements including `BHATTACHARYYA_DISTANCE`,
  `BHATTACHARYYA_COEFFICIENT`, `TEST_STATISTIC`, `DRIFT_ALARM_STATE`,
  contribution rows or Gaussian summary, category proportion deltas, category
  counts, and sample sizes
- explicit not-applicable handling for unsupported variants, missing columns,
  invalid windows, invalid counts, constant numeric reference values, nonpositive
  Gaussian variance, invalid thresholds, and too-small samples

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py drift_algorithm\methods\__init__.py drift_algorithm\__init__.py tests\test_bhattacharyya_distance.py
python -m pytest tests\test_bhattacharyya_distance.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_chi_square_test.py tests\test_fisher_s_exact_test.py tests\test_g_test.py tests\test_psi.py tests\test_kl_divergence.py tests\test_jensen_shannon_distance.py tests\test_hellinger_distance.py tests\test_total_variation_distance.py tests\test_l_infinity_distance.py tests\test_bhattacharyya_distance.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_chi_square_test.py tests\test_fisher_s_exact_test.py tests\test_g_test.py tests\test_psi.py tests\test_kl_divergence.py tests\test_jensen_shannon_distance.py tests\test_hellinger_distance.py tests\test_total_variation_distance.py tests\test_l_infinity_distance.py tests\test_bhattacharyya_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py tests\test_ocdd.py tests\test_feature_map_drift.py tests\test_autoencoder_representation_drift.py tests\test_graph_embedding_drift.py tests\test_llm_query_semantic_distance.py tests\test_model_uncertainty_drift.py tests\test_shap_drift.py tests\test_tree_feature.py tests\test_classifier_embedding_drift.py tests\test_text_domain_classifier_drift.py tests\test_hat.py tests\test_drift_retraining_classifier.py -q
```

Check results:

```text
py_compile: passed
DM-012 pytest: 5 passed
DM-001 through DM-012 batch regression pytest: 63 passed
implemented numeric, categorical, streaming, supervised, multivariate, representation, explanation, domain-classifier, and operational pytest: 292 passed
```

Next candidate:

```text
DM-013 Histogram Intersection Normalized Complement design detail and implementation
```

## 2026-06-26 - DM-013 Histogram Intersection Normalized Complement Implementation Loop

### DM-013 Histogram Intersection Normalized Complement Implementation

Implemented Histogram Intersection Normalized Complement.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/batchdistributioncomparison.py`
- `drift_algorithm/docs/method_designs/DM-013_histogram_intersection_normalized_complement.md`
- `tests/test_histogram_intersection_normalized_complement.py`

Implemented behavior:

- public `detect_histogram_intersection_normalized_complement` function
- `HINC_CATEGORICAL`
- `HINC_HISTOGRAM_NUMERIC`
- `HINC_IMAGE_FEATURE`
- categorical/count-table probability distributions
- numeric histogram support for `HINC_HISTOGRAM_NUMERIC`
- image-feature variant through the category/count feature-bin histogram
  contract
- histogram intersection and normalized complement score
- threshold-based alarm without p-value
- canonical measurements including
  `HISTOGRAM_INTERSECTION_NORMALIZED_COMPLEMENT`,
  `HISTOGRAM_INTERSECTION`, `TEST_STATISTIC`, `DRIFT_ALARM_STATE`,
  contribution rows, category proportion deltas, category counts, and sample
  sizes
- explicit not-applicable handling for unsupported variants, missing columns,
  invalid windows, invalid counts, constant numeric reference values, invalid
  thresholds, and too-small samples

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py drift_algorithm\methods\__init__.py drift_algorithm\__init__.py tests\test_histogram_intersection_normalized_complement.py
python -m pytest tests\test_histogram_intersection_normalized_complement.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_chi_square_test.py tests\test_fisher_s_exact_test.py tests\test_g_test.py tests\test_psi.py tests\test_kl_divergence.py tests\test_jensen_shannon_distance.py tests\test_hellinger_distance.py tests\test_total_variation_distance.py tests\test_l_infinity_distance.py tests\test_bhattacharyya_distance.py tests\test_histogram_intersection_normalized_complement.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_chi_square_test.py tests\test_fisher_s_exact_test.py tests\test_g_test.py tests\test_psi.py tests\test_kl_divergence.py tests\test_jensen_shannon_distance.py tests\test_hellinger_distance.py tests\test_total_variation_distance.py tests\test_l_infinity_distance.py tests\test_bhattacharyya_distance.py tests\test_histogram_intersection_normalized_complement.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py tests\test_ocdd.py tests\test_feature_map_drift.py tests\test_autoencoder_representation_drift.py tests\test_graph_embedding_drift.py tests\test_llm_query_semantic_distance.py tests\test_model_uncertainty_drift.py tests\test_shap_drift.py tests\test_tree_feature.py tests\test_classifier_embedding_drift.py tests\test_text_domain_classifier_drift.py tests\test_hat.py tests\test_drift_retraining_classifier.py -q
```

Check results:

```text
py_compile: passed
DM-013 pytest: 5 passed
DM-001 through DM-013 batch regression pytest: 68 passed
implemented numeric, categorical, streaming, supervised, multivariate, representation, explanation, domain-classifier, and operational pytest: 297 passed
```

Next candidate:

```text
DM-001 through DM-056 completed, excluding separately held DM-034 SPRT.
```

## 2026-06-26 - DM-034 SPRT Implementation Loop

### DM-034 SPRT Implementation

Implemented SPRT.

Files changed:

- `drift_algorithm/__init__.py`
- `drift_algorithm/methods/__init__.py`
- `drift_algorithm/methods/streamingchangedetector.py`
- `drift_algorithm/docs/method_designs/DM-034_sprt.md`
- `tests/test_sprt.py`

Implemented behavior:

- public `detect_sprt` function
- `SPRT_BERNOULLI_ERROR_RATE`
- `SPRT_GAUSSIAN_MEAN_SHIFT`
- reference window used for validation and optional Gaussian sigma calibration
- current window replayed as the sequential likelihood-ratio stream
- Bernoulli 0/1 error stream contract through `error_col` or numeric
  `value_col`
- Gaussian numeric stream contract with `mu0`, `mu1` or `mean_shift`, and
  `sigma` or reference-window standard deviation
- default SPRT decision boundaries from `alpha` and `beta`
- H0/H1/continue decision state, LLR, control limits, sequential bounds, and
  decision events
- threshold-based boundary decision without p-value
- explicit not-applicable handling for unsupported variants, missing columns,
  invalid windows, raw label/prediction inputs, non-Bernoulli values, invalid
  hypothesis parameters, invalid boundaries, and nonpositive Gaussian sigma

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\streamingchangedetector.py drift_algorithm\methods\__init__.py drift_algorithm\__init__.py tests\test_sprt.py
python -m pytest tests\test_sprt.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_chi_square_test.py tests\test_fisher_s_exact_test.py tests\test_g_test.py tests\test_psi.py tests\test_kl_divergence.py tests\test_jensen_shannon_distance.py tests\test_hellinger_distance.py tests\test_total_variation_distance.py tests\test_l_infinity_distance.py tests\test_bhattacharyya_distance.py tests\test_histogram_intersection_normalized_complement.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_sprt.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py tests\test_ocdd.py tests\test_feature_map_drift.py tests\test_autoencoder_representation_drift.py tests\test_graph_embedding_drift.py tests\test_llm_query_semantic_distance.py tests\test_model_uncertainty_drift.py tests\test_shap_drift.py tests\test_tree_feature.py tests\test_classifier_embedding_drift.py tests\test_text_domain_classifier_drift.py tests\test_hat.py tests\test_drift_retraining_classifier.py -q
```

Check results:

```text
py_compile: passed
DM-034 pytest: 5 passed
implemented numeric, categorical, streaming, supervised, multivariate, representation, explanation, domain-classifier, and operational pytest: 302 passed
```

Next candidate:

```text
DM-001 through DM-056 completed.
```
