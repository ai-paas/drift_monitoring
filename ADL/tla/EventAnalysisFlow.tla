---- MODULE EventAnalysisFlow ----
EXTENDS Naturals, Sequences, FiniteSets, TLC

VARIABLES
  driftEvents,
  methodRuns,
  methodAssignments,
  analysisChartRegistrations,
  buckets,
  eventAnalysisResponses,
  chartPayloads

(*
--algorithm EventAnalysisFlow
variables
  driftEvents = {[id |-> "event-1", methodRunId |-> "run-1", assignmentId |-> "assign-1"]},
  methodRuns = {[id |-> "run-1", bucketId |-> "bucket-1", result |-> "runtime-result"]},
  methodAssignments = {[id |-> "assign-1", runtimeMethodKey |-> "adwin_mean_stream"]},
  analysisChartRegistrations = {[id |-> "analysis-1", assignmentId |-> "assign-1", chartId |-> "CHART-STREAM-001", payloadAdapterKey |-> "adwin_mean_stream_to_chart_stream_001"]},
  buckets = {[id |-> "bucket-1", sourceId |-> "case-010", v |-> 0.42]},
  eventAnalysisResponses = {},
  chartPayloads = {};

define
  EventExists(eventId) ==
    \E event \in driftEvents : event.id = eventId

  MethodRunExists(runId) ==
    \E run \in methodRuns : run.id = runId

  RegistrationExists(assignmentId) ==
    \E registration \in analysisChartRegistrations : registration.assignmentId = assignmentId

  EventAnalysisSuccessRequiresEvent ==
    \A response \in eventAnalysisResponses : EventExists(response.eventId)

  EventAnalysisSuccessRequiresMethodRun ==
    \A response \in eventAnalysisResponses : MethodRunExists(response.methodRunId)

  EventAnalysisSuccessRequiresAnalysisChartRegistration ==
    \A response \in eventAnalysisResponses : RegistrationExists(response.assignmentId)

  ChartPayloadDataSourcesMatchComponents ==
    \A payload \in chartPayloads : payload.hasRequiredDataSources = TRUE
end define;

process DriftServer = "drift-server"
variables event, response, payload;
begin
  BuildEventAnalysis:
    event := CHOOSE e \in driftEvents : TRUE;
    if MethodRunExists(event.methodRunId) /\ RegistrationExists(event.assignmentId) then
      payload := [
        chartId |-> "CHART-STREAM-001",
        eventId |-> event.id,
        hasRequiredDataSources |-> TRUE
      ];
      chartPayloads := chartPayloads \cup {payload};
      response := [
        sourceId |-> "case-010",
        eventId |-> event.id,
        methodRunId |-> event.methodRunId,
        assignmentId |-> event.assignmentId,
        chartPayload |-> payload
      ];
      eventAnalysisResponses := eventAnalysisResponses \cup {response};
    end if;
end process;
end algorithm;
*)

EventExists(eventId) ==
  \E event \in driftEvents : event.id = eventId

MethodRunExists(runId) ==
  \E run \in methodRuns : run.id = runId

RegistrationExists(assignmentId) ==
  \E registration \in analysisChartRegistrations : registration.assignmentId = assignmentId

EventAnalysisSuccessRequiresEvent ==
  \A response \in eventAnalysisResponses : EventExists(response.eventId)

EventAnalysisSuccessRequiresMethodRun ==
  \A response \in eventAnalysisResponses : MethodRunExists(response.methodRunId)

EventAnalysisSuccessRequiresAnalysisChartRegistration ==
  \A response \in eventAnalysisResponses : RegistrationExists(response.assignmentId)

ChartPayloadDataSourcesMatchComponents ==
  \A payload \in chartPayloads : payload.hasRequiredDataSources = TRUE

BoundedModel ==
  /\ Cardinality(eventAnalysisResponses) <= 1
  /\ Cardinality(chartPayloads) <= 1

Init ==
  /\ driftEvents = {[id |-> "event-1", methodRunId |-> "run-1", assignmentId |-> "assign-1"]}
  /\ methodRuns = {[id |-> "run-1", bucketId |-> "bucket-1", result |-> "runtime-result"]}
  /\ methodAssignments = {[id |-> "assign-1", runtimeMethodKey |-> "adwin_mean_stream"]}
  /\ analysisChartRegistrations = {
       [id |-> "analysis-1", assignmentId |-> "assign-1",
        chartId |-> "CHART-STREAM-001", payloadAdapterKey |-> "adwin_mean_stream_to_chart_stream_001"]
     }
  /\ buckets = {[id |-> "bucket-1", sourceId |-> "case-010", v |-> 42]}
  /\ eventAnalysisResponses = {}
  /\ chartPayloads = {}

BuildEventAnalysis ==
  /\ LET event == CHOOSE e \in driftEvents : TRUE
         payload == [chartId |-> "CHART-STREAM-001", eventId |-> event.id, hasRequiredDataSources |-> TRUE]
         response == [sourceId |-> "case-010", eventId |-> event.id,
                      methodRunId |-> event.methodRunId, assignmentId |-> event.assignmentId,
                      chartPayload |-> payload]
     IN
       /\ MethodRunExists(event.methodRunId)
       /\ RegistrationExists(event.assignmentId)
       /\ chartPayloads' = chartPayloads \cup {payload}
       /\ eventAnalysisResponses' = eventAnalysisResponses \cup {response}
  /\ UNCHANGED <<driftEvents, methodRuns, methodAssignments, analysisChartRegistrations, buckets>>

Stutter ==
  UNCHANGED <<driftEvents, methodRuns, methodAssignments, analysisChartRegistrations, buckets,
              eventAnalysisResponses, chartPayloads>>

Next ==
  BuildEventAnalysis \/ Stutter

Spec ==
  Init /\ [][Next]_<<driftEvents, methodRuns, methodAssignments, analysisChartRegistrations,
                    buckets, eventAnalysisResponses, chartPayloads>>

====
