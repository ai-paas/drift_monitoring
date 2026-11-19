package adl

#ChartPayload: {
	chartId:   string
	sourceId?: string
	eventId?:  string
	featureId?: string
	title?:    string
	metadata?: {...}
	data: {
		[string]: [...{[string]: _}]
	}
	components: [...#ChartComponent]
	...
}

#ChartComponent: {
	componentInstanceId: string
	componentType:       string
	dataBinding?: {
		source: string
		xField?: string
		yField?: string
		labelField?: string
		[string]: _
	}
	config?: {...}
	text?:   string
	...
}

#ChartPayloadInvariant: {
	payload: #ChartPayload
	// Express cross-field source existence checks in tests or CUE values that
	// instantiate concrete components. This schema keeps the reusable shape.
}
