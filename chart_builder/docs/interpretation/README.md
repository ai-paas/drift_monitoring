# Chart Interpretation Guide Structure

This directory separates interpretation guidance into three explicit layers.

## Layers

1. General guide
   - File: `general_guide.md`
   - Applies to every chart and component.
   - Defines output order, evidence rules, prohibited behavior, and style.

2. Chart-level guide
   - File: `chart_level_guide.md`
   - Applies when writing the full chart `summary` and `detail`.
   - Defines component evidence synthesis, judgment boundaries, and chart-level caution.

3. Component and chart-specific guides
   - Component files: `component_guides/*.md`
   - Chart files: `chart_guides/CHART-*.md`
   - Component guides describe how each component family should explain visual encoding and payload evidence.
   - Chart-specific guides describe the intended reading order and domain logic for a concrete chart id.

## Runtime Use

The interpretation server composes the prompt from:

```text
general_guide.md
+ chart_level_guide.md
+ component_guides/<component family>.md for each visible component
+ chart_guides/<chart id>.md when available
+ current payload componentContexts, signal, config, visualEncodingHint, and dataSample
```

Legacy file `docs/chart_interpretation_llm_guide.md` remains as a fallback.
