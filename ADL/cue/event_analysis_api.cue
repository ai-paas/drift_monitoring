package adl

#EventAnalysisResponse: {
	sourceId:          string
	eventId:           string
	analysisChartId:   string
	chartId:           string
	chartDefinitionId: string
	chartDefinition:   _
	chartPayload:      #ChartPayload
}

#EventAnalysisContext: {
	source: {
		sourceId: string
		sourceTitle?: string
		sourceType?: string | null
		sourceUrl?:  string | null
	}
	adapter: {...}
	feature: {
		featureId: string
		featureLabel?: string
		valueType?: string
		unit?: string | null
	}
	assignment: {
		assignmentId: string
		sourceId: string
		adapterId: string
		featureId: string
		runtimeMethodKey: string
		params: _
		threshold: _
		windowConfig: _
	}
	methodRun: {
		methodRunId: string
		windowStart: #ISOTime
		windowEnd: #ISOTime
		runStatus: "success" | "error" | "skipped" | string
		level: "normal" | "warning" | "drift" | "unknown"
		score?: number | null
		result: _
	}
	driftEvent: {
		eventId: string
		eventStart: #ISOTime
		eventEnd: #ISOTime
		level: "warning" | "drift"
		score?: number | null
		payload: _
	}
	analysisChart: {
		analysisChartId: string
		chartId: string
		chartDefinitionId: string
		payloadAdapterKey: string
	}
	chartDefinition: _
	buckets: [...#PayloadBucket]
	runtimeResult: _
	payloadAdapterConfig: _
}

#PayloadBucket: {
	bucketId: string
	bucketStart: #ISOTime
	bucketEnd: #ISOTime
	v: number | null
	count: int & >=0
	min?: number | null
	max?: number | null
	errorCount?: int | null
	errorRate?: number | null
	meanConfidence?: number | null
	status: string
	payload?: _
}
