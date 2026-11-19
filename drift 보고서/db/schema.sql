create table if not exists source_import_batch (
  import_batch_id bigserial primary key,
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  import_status varchar(20) not null default 'running',
  git_commit_sha char(40),
  source_root text,
  summary_json jsonb not null default '{}'::jsonb,
  error_message text,
  constraint ck_source_import_batch_status
    check (import_status in ('running', 'success', 'failed'))
);

create table if not exists source_document (
  source_document_id bigserial primary key,
  source_path text not null unique,
  source_type varchar(30) not null,
  domain varchar(50) not null,
  title text,
  checksum_sha256 char(64),
  file_size_bytes bigint,
  last_seen_at timestamptz not null default now(),
  is_active boolean not null default true,
  constraint ck_source_document_type
    check (source_type in ('markdown','csv','generated_js','html','image','code','other'))
);

create index if not exists idx_source_document_domain on source_document(domain);
create index if not exists idx_source_document_checksum on source_document(checksum_sha256);
create index if not exists idx_source_document_active on source_document(is_active);

create table if not exists drift_method (
  drift_method_id bigserial primary key,
  method_code varchar(80) not null unique,
  display_name text not null unique,
  method_category varchar(80),
  primary_input_type varchar(80),
  primary_output_type varchar(80),
  status varchar(20) not null default 'active',
  summary text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint ck_drift_method_status
    check (status in ('draft','active','deprecated'))
);

create index if not exists idx_drift_method_category on drift_method(method_category);
create index if not exists idx_drift_method_status on drift_method(status);

create table if not exists algorithm_variant (
  algorithm_variant_id bigserial primary key,
  variant_code varchar(120) not null unique,
  display_name text,
  variant_family varchar(120),
  status varchar(20) not null default 'active',
  use_when_text text,
  good_for_text text,
  avoid_when_text text,
  caution_text text,
  report_guidance_text text,
  source_document_id bigint references source_document(source_document_id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint ck_algorithm_variant_status
    check (status in ('draft','active','deprecated'))
);

create index if not exists idx_algorithm_variant_family on algorithm_variant(variant_family);
create index if not exists idx_algorithm_variant_status on algorithm_variant(status);

create table if not exists method_variant (
  method_variant_id bigserial primary key,
  drift_method_id bigint not null references drift_method(drift_method_id),
  algorithm_variant_id bigint not null references algorithm_variant(algorithm_variant_id),
  is_default_variant boolean not null default false,
  selection_priority integer,
  selection_rule_text text,
  source_document_id bigint references source_document(source_document_id),
  unique(drift_method_id, algorithm_variant_id)
);

create index if not exists idx_method_variant_method on method_variant(drift_method_id);
create index if not exists idx_method_variant_variant on method_variant(algorithm_variant_id);
create index if not exists idx_method_variant_priority on method_variant(selection_priority);

create table if not exists measurement (
  measurement_pk bigserial primary key,
  measurement_id varchar(40) not null unique,
  measurement_code varchar(120) not null unique,
  canonical_name text not null unique,
  measurement_category varchar(80),
  value_type varchar(50),
  unit varchar(50),
  higher_is_more_drift boolean,
  valid_range_text text,
  interpretation_text text,
  caution_text text
);

create index if not exists idx_measurement_category on measurement(measurement_category);
create index if not exists idx_measurement_value_type on measurement(value_type);

create table if not exists variant_measurement (
  variant_measurement_id bigserial primary key,
  method_variant_id bigint not null references method_variant(method_variant_id),
  measurement_pk bigint not null references measurement(measurement_pk),
  raw_measurement_name text not null,
  output_order integer,
  is_primary boolean not null default false,
  required_for_report boolean not null default false,
  interpretation_override_text text,
  source_document_id bigint references source_document(source_document_id),
  unique(method_variant_id, measurement_pk, raw_measurement_name)
);

create index if not exists idx_variant_measurement_measurement on variant_measurement(measurement_pk);
create index if not exists idx_variant_measurement_raw on variant_measurement(raw_measurement_name);

create table if not exists parameter (
  parameter_id bigserial primary key,
  parameter_code varchar(100) not null unique,
  display_name text,
  value_type varchar(50),
  default_value_text text,
  allowed_values_json jsonb,
  description_text text,
  tuning_effect_text text
);

create index if not exists idx_parameter_value_type on parameter(value_type);

create table if not exists variant_parameter (
  variant_parameter_id bigserial primary key,
  method_variant_id bigint not null references method_variant(method_variant_id),
  parameter_id bigint not null references parameter(parameter_id),
  is_required boolean not null default false,
  default_value_text text,
  allowed_values_json jsonb,
  parameter_role varchar(80),
  caution_text text,
  source_document_id bigint references source_document(source_document_id),
  unique(method_variant_id, parameter_id)
);

create index if not exists idx_variant_parameter_parameter on variant_parameter(parameter_id);
create index if not exists idx_variant_parameter_role on variant_parameter(parameter_role);

create table if not exists chart_definition (
  chart_definition_id bigserial primary key,
  chart_code varchar(80) not null unique,
  chart_family varchar(80),
  display_title text,
  purpose_text text,
  component_summary_text text,
  input_contract_json jsonb,
  output_contract_json jsonb,
  status varchar(20) not null default 'active',
  source_document_id bigint references source_document(source_document_id),
  constraint ck_chart_definition_status
    check (status in ('draft','active','deprecated'))
);

create index if not exists idx_chart_definition_family on chart_definition(chart_family);
create index if not exists idx_chart_definition_status on chart_definition(status);

create table if not exists variant_chart (
  variant_chart_id bigserial primary key,
  method_variant_id bigint not null references method_variant(method_variant_id),
  chart_definition_id bigint not null references chart_definition(chart_definition_id),
  is_primary_chart boolean not null default false,
  selection_reason_text text,
  display_order integer,
  source_document_id bigint references source_document(source_document_id),
  unique(method_variant_id, chart_definition_id)
);

create index if not exists idx_variant_chart_chart on variant_chart(chart_definition_id);
create index if not exists idx_variant_chart_primary on variant_chart(is_primary_chart);

create table if not exists chart_asset (
  chart_asset_id bigserial primary key,
  chart_definition_id bigint not null references chart_definition(chart_definition_id),
  asset_type varchar(30) not null,
  asset_path text not null unique,
  checksum_sha256 char(64),
  is_generated boolean not null default false,
  created_at timestamptz not null default now(),
  unique(chart_definition_id, asset_type, asset_path)
);

create index if not exists idx_chart_asset_chart on chart_asset(chart_definition_id);
create index if not exists idx_chart_asset_type on chart_asset(asset_type);

create table if not exists chart_component (
  chart_component_id bigserial primary key,
  component_code varchar(120) not null unique,
  display_name text not null,
  purpose_text text,
  shows_text text,
  interpretation_text text,
  caution_text text,
  input_contract_json jsonb,
  config_schema_json jsonb,
  renderer_status varchar(20) not null default 'active',
  source_document_id bigint references source_document(source_document_id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint ck_chart_component_renderer_status
    check (renderer_status in ('draft','active','deprecated'))
);

create index if not exists idx_chart_component_status on chart_component(renderer_status);

create table if not exists chart_component_usage (
  chart_component_usage_id bigserial primary key,
  chart_definition_id bigint not null references chart_definition(chart_definition_id),
  chart_component_id bigint not null references chart_component(chart_component_id),
  usage_role varchar(80),
  display_order integer,
  usage_reason_text text,
  source_document_id bigint references source_document(source_document_id),
  unique(chart_definition_id, chart_component_id, usage_role)
);

create index if not exists idx_chart_component_usage_chart on chart_component_usage(chart_definition_id);
create index if not exists idx_chart_component_usage_component on chart_component_usage(chart_component_id);

create table if not exists chart_component_raw_mapping (
  chart_component_raw_mapping_id bigserial primary key,
  chart_definition_id bigint not null references chart_definition(chart_definition_id),
  raw_component_text text not null,
  normalized_component_id bigint references chart_component(chart_component_id),
  source_document_id bigint references source_document(source_document_id),
  unique(chart_definition_id, raw_component_text)
);

create index if not exists idx_chart_component_raw_chart on chart_component_raw_mapping(chart_definition_id);
create index if not exists idx_chart_component_raw_component on chart_component_raw_mapping(normalized_component_id);

create table if not exists chart_component_interpretation_rule (
  chart_component_interpretation_rule_id bigserial primary key,
  chart_component_id bigint not null references chart_component(chart_component_id),
  rule_code varchar(120) not null,
  signal_type varchar(120),
  condition_json jsonb not null default '{}'::jsonb,
  severity_mapping_json jsonb not null default '{}'::jsonb,
  interpretation_template_text text not null,
  caution_text text,
  source_document_id bigint references source_document(source_document_id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(chart_component_id, rule_code)
);

create index if not exists idx_chart_component_rule_component on chart_component_interpretation_rule(chart_component_id);
create index if not exists idx_chart_component_rule_signal on chart_component_interpretation_rule(signal_type);

create table if not exists chart_interpretation_guide (
  chart_interpretation_guide_id bigserial primary key,
  chart_definition_id bigint not null references chart_definition(chart_definition_id),
  guide_code varchar(120) not null,
  interpretation_flow_json jsonb not null default '[]'::jsonb,
  synthesis_rule_json jsonb not null default '{}'::jsonb,
  interpretation_template_text text not null,
  caution_text text,
  source_document_id bigint references source_document(source_document_id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(chart_definition_id, guide_code)
);

create index if not exists idx_chart_interpretation_guide_chart on chart_interpretation_guide(chart_definition_id);
create index if not exists idx_chart_interpretation_guide_code on chart_interpretation_guide(guide_code);

create table if not exists document_section (
  document_section_id bigserial primary key,
  source_document_id bigint not null references source_document(source_document_id),
  section_key varchar(200) not null,
  section_type varchar(80),
  heading_text text,
  heading_level integer,
  body_markdown text,
  body_plain_text text,
  body_html text,
  line_start integer,
  line_end integer,
  content_hash char(64),
  display_order integer,
  is_active boolean not null default true,
  unique(source_document_id, section_key)
);

create index if not exists idx_document_section_type on document_section(section_type);
create index if not exists idx_document_section_source_order on document_section(source_document_id, display_order);
create index if not exists idx_document_section_active on document_section(is_active);
create index if not exists idx_document_section_fts
  on document_section
  using gin(to_tsvector('simple', coalesce(body_plain_text, '')));

create table if not exists section_entity_link (
  section_entity_link_id bigserial primary key,
  document_section_id bigint not null references document_section(document_section_id),
  entity_type varchar(40) not null,
  entity_id bigint not null,
  link_role varchar(80) not null,
  confidence numeric(5,4),
  unique(document_section_id, entity_type, entity_id, link_role)
);

create index if not exists idx_section_entity on section_entity_link(entity_type, entity_id);
create index if not exists idx_section_entity_role on section_entity_link(link_role);

create table if not exists algorithm_implementation (
  algorithm_implementation_id bigserial primary key,
  method_variant_id bigint not null references method_variant(method_variant_id),
  implementation_code varchar(120) not null unique,
  runtime_type varchar(40),
  module_path text,
  callable_name text,
  input_schema_json jsonb,
  output_schema_json jsonb,
  default_params_json jsonb,
  version varchar(40),
  status varchar(20) not null default 'draft',
  created_at timestamptz not null default now(),
  unique(method_variant_id, implementation_code, version),
  constraint ck_algorithm_implementation_status
    check (status in ('draft','active','deprecated'))
);

create table if not exists algorithm_run (
  algorithm_run_id bigserial primary key,
  algorithm_implementation_id bigint not null references algorithm_implementation(algorithm_implementation_id),
  run_key varchar(160) not null unique,
  dataset_ref text,
  reference_window_ref text,
  current_window_ref text,
  input_signal varchar(80),
  target_feature text,
  params_json jsonb,
  run_status varchar(20) not null default 'queued',
  started_at timestamptz,
  finished_at timestamptz,
  error_message text,
  constraint ck_algorithm_run_status
    check (run_status in ('queued','running','success','failed','cancelled'))
);

create index if not exists idx_algorithm_run_status_started on algorithm_run(run_status, started_at);

create table if not exists algorithm_result (
  algorithm_result_id bigserial primary key,
  algorithm_run_id bigint not null references algorithm_run(algorithm_run_id),
  measurement_pk bigint not null references measurement(measurement_pk),
  raw_measurement_name text not null,
  value_float double precision,
  value_text text,
  value_bool boolean,
  value_json jsonb,
  unit varchar(50),
  is_primary boolean not null default false,
  created_at timestamptz not null default now(),
  unique(algorithm_run_id, measurement_pk, raw_measurement_name)
);

create index if not exists idx_algorithm_result_run_measurement on algorithm_result(algorithm_run_id, measurement_pk);

create table if not exists chart_render_job (
  chart_render_job_id bigserial primary key,
  chart_definition_id bigint not null references chart_definition(chart_definition_id),
  algorithm_run_id bigint references algorithm_run(algorithm_run_id),
  render_key varchar(160) not null unique,
  renderer_type varchar(40),
  renderer_version varchar(40),
  input_payload_json jsonb,
  render_status varchar(20) not null default 'queued',
  started_at timestamptz,
  finished_at timestamptz,
  error_message text,
  constraint ck_chart_render_status
    check (render_status in ('queued','running','success','failed'))
);

create index if not exists idx_chart_render_status_started on chart_render_job(render_status, started_at);

create table if not exists chart_render_output (
  chart_render_output_id bigserial primary key,
  chart_render_job_id bigint not null references chart_render_job(chart_render_job_id),
  output_type varchar(30) not null,
  output_path text not null unique,
  mime_type varchar(80),
  checksum_sha256 char(64),
  created_at timestamptz not null default now()
);
