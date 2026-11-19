# Component Guide: State Timeline

Explain colored horizontal segments, state labels, start/end order, and how state changes relate to metric trends or event markers.

Use the interval semantics supplied by the payload. If start/end values behave like half-open ranges, avoid converting them into inclusive ranges that shift the visible state by one step. Prefer wording such as `normal from t=1 until t=11, warning from t=11 until t=14` when the exact boundary convention is ambiguous.

Do not infer an adaptive-tree replacement, retraining, or alarm result unless the current chart also contains the relevant event, state, or structure evidence.
