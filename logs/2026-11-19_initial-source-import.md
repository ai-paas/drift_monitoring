# Initial public source import

- Date: 2026-11-19 (Asia/Seoul).
- Purpose: publish the current container-backed framework source to ai-paas/drift_monitoring with the user's explicit authorization.
- Added: selected source/catalog/test/document files; .env.example; docs/DEPLOYMENT.md; docs/IMPORT_VALIDATION.md; this log.
- Modified in publication checkout: README.md, Dockerfile, docker-compose*.yml, docker/supervisord.conf, .gitignore, .dockerignore, llm_interpretation_server/interpretation_server.py and README (local endpoint default only), drift 보고서/tools/register_llm_guides.py (environment-driven connection).
- Deleted: no original source files. The publication checkout intentionally omits runtime data, actual extracted datasets, LLM execution logs, backups, exports and private configuration. Existing target LICENSE is retained.
- Functions/classes/endpoints/public API: existing signatures and shapes unchanged. upsert_guides reads connection values from environment; no new endpoint.
- Managed contracts: existing registered P0/P1 source retained byte-for-byte; existing LLM table DDL is documented as a manual deployment example; no new migration or managed entry is introduced. No production schema/data migration performed.
- Validation: detailed results in docs/IMPORT_VALIDATION.md. Known original GMA failure and existing 37 field-candidate warnings remain visible. Targeted tests and Builder browser checks passed, and fresh isolated PostgreSQL catalog/guide initialization succeeded.
- Remaining: review original GMA test/implementation discrepancy and existing validator warnings in a separate change. Full image build and production rollout were outside this source import.
