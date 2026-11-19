package adl

#RuntimeMethodOutput: {
	runStatus: "success" | "error" | "skipped"
	level:     "normal" | "warning" | "drift" | "unknown"
	score:     number | null
	event:     #RuntimeDriftEvent | null
	nextState?: _
	metrics: {...}
	diagnostics: {...}
	payloadHints: {...}
}

#RuntimeDriftEvent: {
	eventStart: #ISOTime
	eventEnd:   #ISOTime
	eventLevel: "warning" | "drift"
	eventTitle: string
	...
}

#SuccessfulRuntimeMethodOutput: #RuntimeMethodOutput & {
	runStatus: "success"
	nextState: _
}

#RuntimeOutputInvariant: {
	output: #RuntimeMethodOutput
	// Cross-field checks such as "event != null implies level is warning
	// or drift" should be instantiated in concrete CUE values or tests.
}
