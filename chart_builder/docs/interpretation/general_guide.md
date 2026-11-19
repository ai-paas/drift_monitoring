# General Interpretation Guide

The goal is not to guess a drift label first. Explain what each visible component shows, what evidence appears in the current payload, and how that evidence should be read.

## Component Note Order

For every evidence component, write in this order:

1. Component role
   - State what the component is designed to show.
   - Use component knowledge and component guide context.
   - Do not start with a drift/normal conclusion.

2. Visual encoding
   - Explain axes, marks, colors, states, events, cards, table fields, bars, cells, lines, bands, or markers when present.
   - Mention data fields only when they help the reader understand the visual.
   - If the component is notes-only, legend-only, or context-only, state that it is not graph evidence.

3. Current visible evidence
   - Describe actual values and patterns in the current payload.
   - Prefer concrete values: latest, first, min/max, before/after, event times, state sequence, dominant category, and table deltas.
   - Do not use stale guide examples when payload values differ.

4. Reading rule
   - Explain what the pattern suggests in Korean report style.
   - Separate observation from judgment.

5. Caution
   - State what cannot be concluded from this component alone.
   - Do not infer root cause, business impact, or model failure unless the payload explicitly supports it.
   - For context-only components, state that they are supporting context, not primary evidence.

## Prohibited Behavior

- Do not treat y-axis ticks or display grid lines as thresholds.
- Do not treat higher values as worse unless metric direction, label, or rule says so.
- Do not overwrite or propose changes to `layout`, `components`, `componentType`, `config`, or `dataBinding`.
- Do not invent values absent from the payload or supplied context.
- Do not hide uncertainty behind confident language.
- Do not output debug text, implementation notes, or markdown fences unless explicitly requested.

## Style

- Write in Korean report style.
- Be concise but evidence-based.
- Use 1 to 3 paragraphs for a component note.
- Include concrete values where available.
- Keep observations, synthesis, and cautions separated.
