# Drift Algorithm Catalog Sources

## Authoritative Method List

The authoritative method list is `../drift_methods_catalog.md`.

Current policy:

```text
catalog methods: 56
pure detectors: 55
operational methods: 1
```

`DM-056 DriftRetrainingClassifier` is intentionally included in the method
catalog but should be tagged as operational rather than pure detector.

## Variant Source

`../drift_method_variant_links.csv` maps method ids to variant ids. It currently
aligns with the catalog method list and should be used to enumerate supported
variants for each method design.

## Measurement Source

Use these files together:

- `../drift_measurements_catalog.csv`
- `../drift_method_variant_measurement_links.csv`
- `../drift_method_variant_measurement_summary.csv`

Shared canonical measurements such as `P_VALUE`, `TEST_STATISTIC`, and
`DRIFT_ALARM_STATE` are not semantically interchangeable across methods. The
method and variant context must always be preserved in `DriftResult`.

## Parameter Source

Use:

- `../drift_method_variant_parameters.csv`
- `../drift_method_parameter_guide.md`

Parameters from the CSV provide structure; the Markdown guide provides tuning
and interpretation details.

## Known Mismatch Risks

- `algorithm_variants/` has an extra fallback/support document that is not a
  catalog method.
- Some source paths are bare filenames while others include
  `algorithm_variants/`; implementation docs should normalize paths.
- Do not infer method count from Markdown file count.
- Do not infer detector count from method count because `DM-056` is operational.

## Validation Checks

The package should eventually include a validation command that checks:

- 56 unique method ids from `drift_methods_catalog.md`
- every catalog method has at least one variant mapping
- every variant has measurement mapping where applicable
- every referenced variant document exists
- fallback/support documents are excluded from method count

