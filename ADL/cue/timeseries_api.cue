package adl

#TimeseriesDataResponse: {
	sourceId: string
	modelId:  string
	fullDomain: [#ISOTime, #ISOTime]
	features: [...#TimeseriesFeature]
	series: {
		[string]: [...#TimeseriesPoint]
	}
	events: {
		[string]: [...#DriftEventMarker]
	}
	resolution: string
	pollIntervalMs?: int & >0
}

#TimeseriesFeature: {
	featureId: string
	label:     string
	valueType?: "numeric" | "categorical" | "multivariate" | string
	unit?:     string | null
	...
}

#TimeseriesPoint: {
	time:        #ISOTime
	windowStart: #ISOTime
	windowEnd:   #ISOTime
	value:       number | null
	rowCount:    int & >=0
	errorCount?: int & >=0 | null
	errorRate?:  number | null
	meanConfidence?: number | null
	status?: "observed" | "empty" | "partial" | "missing" | "ok" | string
	...
}

#DriftEventMarker: {
	eventId:      string
	methodRunId?: string
	assignmentId?: string
	featureId:    string
	eventStart:   #ISOTime
	eventEnd:     #ISOTime
	eventLevel:   "normal" | "warning" | "drift" | "unknown"
	title?:       string
	score?:       number | null
	...
}

#ISOTime: string
