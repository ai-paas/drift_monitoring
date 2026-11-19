package adl

#AggregationMode: "mean"

#DatasourceAdapterBinding: {
	sourceId:        string
	adapterId:       string
	pollIntervalMs: int & >0
	aggregation: {
		windowMs: int & >0
		metric:   #AggregationMode
	}
	status?: *"active" | "paused" | "disabled"
	...
}

#DatasourceAdapterRegistry: {
	cardinality: "one_to_one"
	bindings: [...#DatasourceAdapterBinding]
}

#DatasourceAdapterInvariant: {
	name: "DatasourceAdapterOneToOne"
	description: "Each datasource has exactly one adapter, and each adapter belongs to exactly one datasource."
}
