# Initial source import validation

Date: 2026-11-19 (Asia/Seoul). Scope: selected current application source, not a database backup or container image export. The upload was prepared in an isolated checkout; the running services and their PostgreSQL volume were not changed.

## Included and excluded

Included: current application code, unit/browser tests, catalog CSV/Markdown, synthetic frontend demo assets, chart definitions, schema/generator tools, and managed-contract metadata. Required CSVs and the synthetic time-series JavaScript assets are intentionally versioned.

Excluded: actual CASE-019 extracted datasets, operational SQLite/PostgreSQL records and backups, LLM request/response logs, generated download archives, original Word reports, tool caches, validation captures and local secrets. Synthetic CASE datasets are generated locally using the supplied generator. Historical harness status files are snapshots, not claims that the full harness was rerun during import.

Existing P0/P1 managed source files were compared byte-for-byte with the current source and retained. Changes for publication are deployment configuration, README/ignore files, the unregistered LLM default endpoint and the guide-registration tool's DB environment handling. The existing LLM table shapes are documented as manual schema-only deployment examples, without adding a migration or changing the P0 managed-contract CSV. No detector output, chart payload or public request/response shape was changed.

## Results

| Check | Result |
| --- | --- |
| Algorithm unit suite | 308 passed, 1 failed; failure also reproduced against the original source |
| Payload coverage/binding and LLM timing/newline regression tests | 22 passed |
| Model uncertainty, CUSUM and Wasserstein Runtime tests | 10 passed |
| Builder placement | 1600px and 1280px passed: click/drag/overlay/sample adaptation/labels/preview |
| Builder component browser suite | 32 components and 4 overlays at both widths; preview/zoom/data evidence/saved-report checks passed; no JS errors |
| Chart payload registry | 53 payloads; 262 component instances; 37 registry/spec types; errors=0, warnings=37 |
| JS / shell syntax | Builder/Runtime node --check and entrypoint bash -n passed |
| Compose | Standard and Linux Compose config validation passed |
| Catalog SQL generation | 56 catalog methods, 176 variants, 53 charts, 32 components; generated locally |
| Fresh PostgreSQL initialization | Separate network-disabled ephemeral DB: main schema, generated catalog SQL, documented existing LLM context DDL and guide registration succeeded |
| Fresh DB contents | 57 method rows including Generic/Fallback, 53 charts, 32 components; LLM component contexts=32, chart/analysis contexts=56 |
| Public source scan | No GitHub/OpenAI token, private-key header or private LAN address pattern found in selected source |

Legacy source retains its original CRLF and whitespace to preserve managed source bytes. With CRLF-aware checking, 83 pre-existing whitespace/blank-EOF findings remain in imported files. Newly written deployment/configuration documents pass whitespace checks.

## Known limitations

The test `test_gma_schema_window_warning_and_deferred_requests` still expects `GMA_WITH_EMPIRICAL_LIMIT` to return `not_applicable`, while the current implementation returns `drift_detected`. The same failure exists in the original checkout. Neither the test nor the managed algorithm implementation was changed to mask this discrepancy.

The 37 payload-validator warnings concern inferred field-contract candidates in existing payloads, including category and matrix configurations. They do not make the validator exit nonzero, but zero errors must not be read as every chart being visually or semantically certified. Only the specified Builder browser tests were rerun.

Validation used an isolated Python 3.12 test environment and an existing PostgreSQL 16 application image for the empty-DB check. The new Docker image was not rebuilt end to end. No live LLM request, real dataset upload, production restart or full chart-method harness run was performed.
