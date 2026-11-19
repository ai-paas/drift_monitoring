# Deployment and initialization

The integrated image runs PostgreSQL, Gallery, LLM Interpretation, Drift, Test Feeder, Builder and Admin under Supervisor. The standard Compose file stores PostgreSQL in a new project-scoped named volume. The Linux development variant also bind-mounts the checkout. Ports bind to localhost unless BIND_ADDRESS is changed in .env.

Use the commands in the root README to initialize the catalog on a fresh database. The source CSV/Markdown documents generate db/load_data.sql; that generated SQL and operational DB data are not versioned. The interpretation context tables were maintained separately in the original development database. Their existing schema-only definitions are documented below for fresh installations. No operational rows or prompt/response history are supplied. Existing managed-contract CSV and application/schema source files are unchanged.

Never restore the development database backup from a public repository. Populate your own datasets and configure a reachable OpenAI-compatible endpoint through .env. An LLM request sends supplied chart context to the configured endpoint. The initial source import does not include a real model endpoint or credentials.

The original local deployment may use an external PostgreSQL volume. This repository intentionally creates a project-scoped volume; it does not attach to the original volume automatically. Existing ports can conflict with another installation: stop only the intended project or override host port mappings before starting a second stack.

This is a development/demo stack; Admin provides management actions and is not an authenticated production gateway. Keep localhost binding or add appropriate access controls before exposing it. No live LLM calls or production data transfers were part of import validation.


## Existing interpretation tables

After applying the catalog schema and generated catalog data, create these existing tables and register the supplied guides. These are manual deployment examples of the current table shapes, not a newly versioned application migration.

```bash
docker compose exec -T drift-llm-postgres psql -U postgres -d drift_monitoring -v ON_ERROR_STOP=1 <<'SQL'
CREATE TABLE IF NOT EXISTS llm_chart_interpretation_context (
    context_key text PRIMARY KEY,
    applies_to text NOT NULL DEFAULT 'chart_family',
    context_markdown text NOT NULL,
    example_good text,
    example_bad text,
    version integer NOT NULL DEFAULT 1,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS llm_component_interpretation_context (
    component_code text PRIMARY KEY,
    context_markdown text NOT NULL,
    example_good text,
    example_bad text,
    version integer NOT NULL DEFAULT 1,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS llm_prompt_template (
    prompt_key text PRIMARY KEY,
    prompt_text text NOT NULL,
    description text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
SQL
docker compose exec drift-llm-postgres python3 '/opt/drift_llm_intepretation/drift 보고서/tools/register_llm_guides.py'
```
