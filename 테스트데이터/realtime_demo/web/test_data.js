(function () {
  "use strict";

  window.DRIFT_METRIC_YEARLY_TEST_DATA = {
    modelId: "case-010-adwin-realtime-demo",
    asOfDate: "2026-01-01T00:00:00.000Z",
    fullDomain: ["2026-01-01T00:00:00.000Z", "2026-12-31T23:59:00.000Z"],
    features: [
      {
        featureId: "case010_metric_mean",
        label: "CASE-010 metric mean",
        unit: "score",
        description: "CASE-010 stream numeric mean shift hourly aggregate",
        defaultYScale: "auto",
        missingPolicy: {
          calendarMode: "always",
          showClosed: false,
          allowImputed: false
        }
      }
    ],
    series: { case010_metric_mean: [] },
    seriesByResolution: { case010_metric_mean: { "1h": [], "1d": [] } },
    events: { case010_metric_mean: [] }
  };
})();

