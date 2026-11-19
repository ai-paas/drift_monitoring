package adl

#ContractLevel: "P0" | "P1"

#ManagedContractRow: {
	contract_id:       =~"^[A-Za-z0-9_.:-]+$"
	contract_level:    #ContractLevel
	contract_type:     string
	owner_module:      string
	file_path:         string
	qualified_name?:   string | null
	source_of_truth_doc?: string | null
	input_contract?:   string | null
	output_contract?:  string | null
	dependent_tests?:  string | null
	signature_hash?:   string | null
	body_hash?:        string | null
	content_hash?:     string | null
	last_git_commit?:  string | null
	status:            *"active" | "deprecated" | "draft"
	description?:      string | null
}
