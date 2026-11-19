# Component Guide: Bar Chart

Explain bar charts as category-to-value comparisons.

Mention:

- category field and value field,
- bar length or height meaning,
- threshold, target, or tolerance line when present,
- bars above/below the threshold,
- largest and smallest bars,
- whether higher values are better, worse, or simply larger.

For grouped expected/observed bars, compare the two bars category by category and name the largest positive and negative gaps. For contribution bars, explain that larger bars identify which category contributes most to the test statistic, not whether that category alone proves drift.

Do not treat every large bar as drift. Explain what the value measures and whether the chart defines a target or tolerance.

When a target, threshold, or tolerance is present, explicitly compare the important bar values against it. Use wording such as `tail error 0.041 exceeds target 0.03` or `spread 0.028 is below tolerance 0.04`.
