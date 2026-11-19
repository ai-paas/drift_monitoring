# Chart-Level Interpretation Guide

Use this guide for full chart `summary`, `detail`, and chart-level `componentNotes`.

## Chart Detail Order

1. Chart purpose
   - State what the current chart id is meant to explain.
   - Use chart-specific guide and chart context when available.

2. Component evidence summary
   - Summarize each major component's evidence in chart-specific reading order.
   - Explain how each component contributes evidence; do not merely list component names.
   - Use current `componentContexts`, `visualEncodingHint`, `signal`, `config`, and `dataSample`.

3. Cross-component synthesis
   - Link event markers, state timelines, metric trends, distributions, tables, matrices, and structure changes when they share the same time window, category, or decision rule.
   - Prefer temporal ordering and before/after comparisons over generic drift labels.
   - Avoid repeating the same sentence in evidence and judgment sections.

4. Judgment boundary
   - Make a candidate/drift/normal judgment only when the payload contains explicit decision, threshold, detector state, alarm, p-value, or documented rule.
   - If evidence is descriptive only, say it is a pattern to check, not a confirmed decision.

5. Follow-up checks
   - Every chart-level `detail` must include caution or judgment-boundary text.
   - Mention missing thresholds, sample size, metric direction, baseline/current labels, delayed labels, or operational constraints when relevant.

## Output Requirements

- Return `componentNotes` for every major visible graph, table, card, state, marker, matrix, or comparison component with data.
- Evidence component notes must describe visual encoding and current data pattern.
- Skip pure decorative or empty notes components. If a notes/context component is included, identify it as supporting context.
- The chart-level `summary` should be one evidence-based sentence.
- The chart-level `detail` should synthesize the LLM-written component notes, followed by caution or judgment boundary.
