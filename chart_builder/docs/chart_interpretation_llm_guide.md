# Chart Interpretation LLM Guide

## Purpose

This guide defines how an LLM should interpret a chart built from chart components and payload data.
The goal is not to guess a drift label first. The goal is to explain what each component graph shows, what visible evidence appears in the current payload, and how that evidence should be read in the chart context.

## Component Interpretation Order

For every component, write the interpretation in this order.

1. Component role
   - State what this component graph is designed to show.
   - Use `purpose_text` and `shows_text` from `chart_component`.
   - Do not start with a drift/normal conclusion.

2. Visual encoding
   - Explain what the axes, marks, colors, states, events, cards, or table fields represent when they are present in the payload/config.
   - Mention the data source and fields only when they help the report reader understand the graph.
   - If the component is a notes-only, legend-only, or context-only area, state that it is not graph evidence and use it only as supporting context.

3. Current visible evidence
   - Describe the actual pattern in the payload data.
   - Use concrete values that are present in the data: latest value, min/max, event times, state sequence, dominant category, before/after values.
   - If a value is only an axis tick or display scale, do not call it a threshold.

4. Reading rule
   - Use the component LLM guide from `llm_component_interpretation_context` as interpretation context, not as a sentence template.
   - Explain what the pattern suggests in plain Korean report style.
   - Separate observation from judgment.

5. Caution
   - State what cannot be concluded from this component alone.
   - Do not infer root cause, business impact, or model failure unless the payload/context explicitly supports it.
   - For context-only components, state that they should not be treated as primary visual evidence.

## Chart-Level Interpretation Order

For the full chart, write the interpretation in this order.

1. Chart purpose
   - Use the chart guide and chart id to state what the chart is trying to explain.

2. Component evidence summary
   - Treat `componentContexts[].machineObservation`, `componentContexts[].visualEncodingHint`, `componentContexts[].signal`, and `componentContexts[].dataSample` as current evidence, but write fresh component prose yourself.
   - Summarize each major component's observed evidence in chart-specific order before writing the overall interpretation.
   - Do not simply list component names; explain how each component contributes evidence.
   - Do not copy example values or stale prose from a chart template when component evidence says something different.

3. Cross-component synthesis
   - Synthesize the full chart from component interpretations, not from the chart id alone.
   - Link event markers, state timeline, performance trend, and structure/feature changes when the same time window or category appears.
   - For adaptive tree charts, connect online accuracy trend, detector state timeline, replacement/event marker, and tree-size trend only when those components exist in the current payload.
   - Prefer before/after comparisons and temporal ordering over generic drift labels.
   - Avoid repeating the same sentence in both evidence and judgment sections.

4. Judgment boundary
   - Only make a drift/candidate/normal judgment when the payload contains an explicit decision, threshold, detector state, alarm, or documented rule.
   - If the evidence is descriptive only, say that it is a graph pattern to check, not a confirmed drift decision.

5. Follow-up checks
   - Mention missing checks or ambiguity when the chart lacks thresholds, metric direction, sample size, or baseline/current labels.
   - Every chart-level `detail` must include a judgment boundary or caution section, even when the main judgment is supported by visible evidence.

## Prohibited Behavior

- Do not treat y-axis ticks as thresholds.
- Do not treat higher values as worse unless `direction`, metric name, or rule says so.
- Do not overwrite or propose changes to `layout`, `components`, `componentType`, or `dataBinding`.
- Do not invent values that are not present in the payload or supplied context.
- Do not hide uncertainty behind confident language.
- Do not output implementation notes, markdown tables, or debugging text unless asked.

## Output Style

- Write in Korean report style.
- Be concise but evidence-based.
- Use 1 to 3 paragraphs for a component note.
- For a chart-level note, use short section labels such as `컴포넌트별 근거`, `종합 판독`, and `주의 및 추가 확인` when the output format allows it.
- Include concrete values where they are available.
- Keep observations, synthesis, and cautions separated.

## LLM Generation Principle

The rule-based fields in the prompt are not final prose. They are only machine observations extracted from the payload.
The LLM must write fresh Korean report text by combining:

- component type knowledge,
- visual encoding from `config`, `layout.areas`, and component placement,
- current values from `dataSample` and `signal`,
- chart-specific examples in this guide.

Do not copy example sentences or old template values. Examples show the expected reasoning pattern only.
If the current payload says a different feature, time, value, threshold, marker, or group, use the current payload.

## Component Knowledge Checklist

### Line-like metric components

Applies to `trend_line`, `raw_signal_trend`, `performance_metric_view`, `distance_metric_view`, `control_chart`, `cumulative_curve`, `model_diagnostic_curve`, and similar line components.

Explain these elements when present:

- x-axis field and y-axis field.
- main line meaning.
- sampled round points or highlighted points.
- secondary line meaning.
- horizontal marker meaning; call it a threshold only when config/label/rule says it is a threshold, limit, target, or baseline.
- vertical marker or event overlay meaning.
- actual current pattern: first/latest/min/max, crossing point, event point, and post-event direction.

Good example:

```text
? ??? ?? ?? time index? ?? ??? ??? ??? ?????. ?? ???? ??? ? ??? baseline 0.042??, ?? ???? 2026-02-01 drift ???? ??? ??? ????. ?? ?????? ?? 0.04??? ??? ?? ??? ?? 0.11~0.13?? ?????, ? ??? ???? ??? ? ???? ??? ??? ????. ?? ? ???? ?? ???? ???? ??? ??? ?? ??.
```

Bad example:

```text
? ???? drift? ???? ?? ?? ??? ????. ?? ????? drift??.
```

### Projection scatter components

Applies to `projection_scatter` and `feature_projection_view`.

Explain these elements when present:

- each point represents a sample/window projected to x-y space,
- color/group means reference/current/outlier/class,
- group center movement,
- overlap or separation,
- whether the current group moves in a consistent direction.

Good example:

```text
???? ? ?? embedding sample? 2???? ??? ????, ??? reference? current ??? ????. ?? payload??? reference ??? ?? ??? ?? ?? current ??? ?? ???? ??? ? ? ??? ?? ??? ???. ??? ? ??? ?? ? ????? ?? ??? ?? ??? embedding ?? ??? ?????? ???? ???.
```

### Distribution and histogram components

Applies to `histogram_view`, `distribution_view`, `distribution_summary_plot`, and `quantile_view`.

Explain these elements when present:

- bars/area mean frequency, count, density, or distribution mass,
- reference/current or null/observed comparison,
- vertical marker meaning,
- whether observed value is inside the body of the distribution or in the tail,
- what cannot be concluded without sample size and test definition.

Good example:

```text
?? ?? ??? ??? ??? ?? ???? ??? ????, ?? ???? ?? ??? MMD ??? ??? ????. ?? ???? ??? ?? ????? ??? ??? ??? reference/current ??? ??? ?? ???? ? ??? ???. ?, p-value ?? ??? ?? ??? ?? ???? ??.
```

### State timeline components

Explain the meaning of colored horizontal segments, their start/end order, and how they relate to metric trends or event markers.
Do not infer an adaptive-tree replacement unless the current chart actually contains replacement state or tree-size evidence.
When describing segment boundaries, use the interval semantics supplied by the payload. If the payload provides start/end values that behave like half-open ranges, avoid converting them into inclusive ranges that shift the visible state by one step. Prefer wording such as `normal from t=1 until t=11, warning from t=11 until t=14` when the exact boundary convention is ambiguous.

### Decision or summary cards

Explain cards as context, not as graph evidence. Use them to identify the analyzed feature, event date, score, sample count, or summary metric.

### Notes, legend, and context-only components

Some `domain_specific_visual`, notes, legend, or text components are visible but are not graph or table evidence. For these components:

- Do not force them into the same evidence standard as line, scatter, distribution, timeline, table, or card components.
- It is acceptable to summarize that the component is a supporting notes/context area.
- Do not use a notes-only component as the main reason for a drift judgment.
- Do not require the note to cite numeric data if the component itself only contains explanatory text.
- If the server fallback marks these components with a non-LLM provider, this is acceptable when the note correctly says the area is not primary graph evidence.

## Full Chart Output Requirements

The JSON output must contain:

- `componentNotes`: one note per major visible graph, table, card, state, or marker component. Each evidence component note must describe the visual encoding and the current data pattern. It must not be a generic component definition.
- `summary`: one full-chart summary sentence.
- `detail`: full-chart synthesis using the evidence component notes, followed by a judgment boundary or caution.

For `componentNotes`, use the exact `componentInstanceId` from `componentContexts`.
Skip only pure decorative or empty note components when they contain no graph evidence. If a notes/context component is included, identify it as supporting context rather than primary evidence.

The chart-level `detail` should synthesize the LLM-written component notes, not the rule-based draft wording.
