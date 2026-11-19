# Drift Algorithm Documentation

This directory defines the implementation contract for the `drift_algorithm`
package.

## Source-of-Truth Order

Use source documents in this order:

1. `../drift_methods_catalog.md` for authoritative method identity and count.
2. `../drift_method_variant_links.csv` for method-variant mappings.
3. `../drift_method_variant_measurement_links.csv` and
   `../drift_method_variant_measurement_summary.csv` for output measurements.
4. `../drift_method_variant_parameters.csv` and
   `../drift_method_parameter_guide.md` for parameters.
5. `../algorithm_variants/*_algorithm_variants.md` for variant behavior,
   interpretation guidance, and cautions.

## Method Count Policy

The authoritative catalog contains 56 drift methods:

- 55 detector methods
- 1 operational adaptation method: `DM-056 DriftRetrainingClassifier`

`algorithm_variants/generic_fallback_algorithm_variants.md` is a support/fallback
document. It is not counted as `DM-057` unless the method catalog is explicitly
updated.

## Documentation Flow

1. Read `input_output_contracts.md`.
2. Read schema details under `schemas/`.
3. Read the method-specific file under `method_designs/`.
4. Implement the method against `implementation_guide.md`.
5. Add tests that verify canonical measurement outputs.

