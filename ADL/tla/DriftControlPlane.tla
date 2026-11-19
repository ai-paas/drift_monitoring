---- MODULE DriftControlPlane ----
EXTENDS Naturals, Sequences, FiniteSets, TLC

VARIABLES
  sources,
  sourceAdapterBindings,
  rawEvents,
  metricBuckets,
  methodAssignments,
  methodRuns,
  methodState,
  driftEvents,
  analysisChartRegistrations,
  adapterCursor,
  logicalNow

(*
--algorithm DriftControlPlane
variables
  sources = {"case-010"},
  sourceAdapterBindings = {[source |-> "case-010", adapter |-> "adapter-case010"]},
  rawEvents = {},
  metricBuckets = {},
  methodAssignments = {"assign-case010"},
  methodRuns = {},
  methodState = {},
  driftEvents = {},
  analysisChartRegistrations = {"analysis-case010-adwin-stream"},
  adapterCursor = 0,
  logicalNow = 0;

define
  HasBucketForRun(run) ==
    \E bucket \in metricBuckets : bucket = run.bucket

  HasRunForEvent(event) ==
    \E run \in methodRuns : run = event.run

  NoMethodRunWithoutBucket ==
    \A run \in methodRuns : HasBucketForRun(run)

  NoEventWithoutMethodRun ==
    \A event \in driftEvents : HasRunForEvent(event)

  OneAdapterPerSource ==
    \A source \in sources :
      \E binding \in sourceAdapterBindings :
        binding.source = source

  NoDuplicateAdapterPerSource ==
    \A b1 \in sourceAdapterBindings :
      \A b2 \in sourceAdapterBindings :
        (b1.source = b2.source) => b1.adapter = b2.adapter

  OneSourcePerAdapter ==
    \A b1 \in sourceAdapterBindings :
      \A b2 \in sourceAdapterBindings :
        (b1.adapter = b2.adapter) => b1.source = b2.source

  NoDuplicateMethodRunPerAssignmentBucket ==
    \A r1 \in methodRuns :
      \A r2 \in methodRuns :
        (r1.assignment = r2.assignment /\ r1.bucket = r2.bucket) => r1 = r2
end define;

process TestFeederServer = "test-feeder"
begin
  FeederTick:
    logicalNow := logicalNow + 1;
    rawEvents := rawEvents \cup {[source |-> "case-010", time |-> logicalNow, value |-> logicalNow]};
    goto FeederTick;
end process;

process DriftServer = "drift-server"
variables bucket, run, event;
begin
  PollOnce:
    if rawEvents # {} then
      adapterCursor := adapterCursor + 1;
      bucket := [id |-> adapterCursor, source |-> "case-010", adapter |-> "adapter-case010"];
      metricBuckets := metricBuckets \cup {bucket};
      goto RunRuntimeMethod;
    else
      goto PollOnce;
    end if;

  RunRuntimeMethod:
    run := [assignment |-> "assign-case010", bucket |-> bucket, level |-> IF adapterCursor % 3 = 0 THEN "drift" ELSE "normal"];
    methodRuns := methodRuns \cup {run};
    methodState := methodState \cup {[assignment |-> "assign-case010", lastBucket |-> bucket]};
    if run.level = "drift" then
      goto InsertDriftEvent;
    else
      goto PollOnce;
    end if;

  InsertDriftEvent:
    event := [id |-> adapterCursor, run |-> run, source |-> "case-010", level |-> "drift"];
    driftEvents := driftEvents \cup {event};
    goto PollOnce;
end process;
end algorithm;
*)

NoMethodRunWithoutBucket ==
  \A run \in methodRuns :
    \E bucket \in metricBuckets : bucket = run.bucket

NoEventWithoutMethodRun ==
  \A event \in driftEvents :
    \E run \in methodRuns : run = event.run

OneAdapterPerSource ==
  \A source \in sources :
    \E binding \in sourceAdapterBindings :
      binding.source = source

NoDuplicateAdapterPerSource ==
  \A b1 \in sourceAdapterBindings :
    \A b2 \in sourceAdapterBindings :
      (b1.source = b2.source) => b1.adapter = b2.adapter

OneSourcePerAdapter ==
  \A b1 \in sourceAdapterBindings :
    \A b2 \in sourceAdapterBindings :
      (b1.adapter = b2.adapter) => b1.source = b2.source

NoDuplicateMethodRunPerAssignmentBucket ==
  \A r1 \in methodRuns :
    \A r2 \in methodRuns :
      (r1.assignment = r2.assignment /\ r1.bucket = r2.bucket) => r1 = r2

BoundedModel ==
  /\ logicalNow <= 4
  /\ adapterCursor <= 4
  /\ Cardinality(sources) = 1
  /\ Cardinality(sourceAdapterBindings) = 1
  /\ Cardinality(rawEvents) <= 4
  /\ Cardinality(metricBuckets) <= 4
  /\ Cardinality(methodRuns) <= 4
  /\ Cardinality(driftEvents) <= 2

Init ==
  /\ sources = {"case-010"}
  /\ sourceAdapterBindings = {[source |-> "case-010", adapter |-> "adapter-case010"]}
  /\ rawEvents = {}
  /\ metricBuckets = {}
  /\ methodAssignments = {"assign-case010"}
  /\ methodRuns = {}
  /\ methodState = {}
  /\ driftEvents = {}
  /\ analysisChartRegistrations = {"analysis-case010-adwin-stream"}
  /\ adapterCursor = 0
  /\ logicalNow = 0

FeederTick ==
  /\ logicalNow' = logicalNow + 1
  /\ rawEvents' = rawEvents \cup {[source |-> "case-010", time |-> logicalNow + 1, value |-> logicalNow + 1]}
  /\ UNCHANGED <<sources, sourceAdapterBindings, metricBuckets, methodAssignments, methodRuns, methodState, driftEvents,
                 analysisChartRegistrations, adapterCursor>>

PollOnce ==
  /\ rawEvents # {}
  /\ LET nextCursor == adapterCursor + 1
         bucket == [id |-> nextCursor, source |-> "case-010", adapter |-> "adapter-case010"]
         level == IF nextCursor % 3 = 0 THEN "drift" ELSE "normal"
         run == [assignment |-> "assign-case010", bucket |-> bucket, level |-> level]
     IN
       /\ adapterCursor' = nextCursor
       /\ metricBuckets' = metricBuckets \cup {bucket}
       /\ methodRuns' = methodRuns \cup {run}
       /\ methodState' = methodState \cup {[assignment |-> "assign-case010", lastBucket |-> bucket]}
       /\ driftEvents' = IF level = "drift"
                         THEN driftEvents \cup {[id |-> nextCursor, run |-> run, source |-> "case-010", level |-> "drift"]}
                         ELSE driftEvents
  /\ UNCHANGED <<sources, sourceAdapterBindings, rawEvents, methodAssignments, analysisChartRegistrations, logicalNow>>

Stutter ==
  UNCHANGED <<sources, sourceAdapterBindings, rawEvents, metricBuckets, methodAssignments, methodRuns, methodState,
              driftEvents, analysisChartRegistrations, adapterCursor, logicalNow>>

Next ==
  FeederTick \/ PollOnce \/ Stutter

Spec ==
  Init /\ [][Next]_<<sources, sourceAdapterBindings, rawEvents, metricBuckets, methodAssignments, methodRuns, methodState,
                    driftEvents, analysisChartRegistrations, adapterCursor, logicalNow>>

====
