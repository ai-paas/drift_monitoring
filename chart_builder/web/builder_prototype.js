(function () {
  // @managed-contract contract_id=chart_builder.componentTypes level=P1
  const componentTypes = [
    {
      code: "trend_line",
      name: "Trend Line",
      implemented: true,
      overlayCapable: false,
      defaultArea: "top_left",
      defaultConfig: {
        x_field: "time",
        y_field: "value",
        series_field: null,
        show_points: true,
        interpolation: "linear"
      },
      defaultBinding: {
        source: "sample.trend",
        x_field: "time",
        y_field: "value"
      }
    },
    {
      code: "bar_chart",
      name: "Bar Chart",
      implemented: true,
      overlayCapable: false,
      defaultArea: "top_right",
      defaultConfig: {
        orientation: "horizontal",
        category_field: "feature",
        value_field: "score",
        highlight_rule: "max_value",
        sort_order: "value_desc"
      },
      defaultBinding: {
        source: "sample.bars",
        category_field: "feature",
        value_field: "score"
      }
    },
    {
      code: "detector_statistic_view",
      name: "Detector Statistic",
      implemented: true,
      overlayCapable: false,
      defaultArea: "bottom_left",
      defaultConfig: {
        statistic_field: "statistic",
        time_field: "time",
        decision_direction: "higher_is_drift",
        scale: "linear"
      },
      defaultBinding: {
        source: "sample.detector",
        time_field: "time",
        statistic_field: "statistic"
      }
    },
    {
      code: "threshold_line",
      name: "Threshold Line",
      implemented: true,
      overlayCapable: true,
      defaultArea: "bottom_left",
      defaultConfig: {
        threshold_value: 0.68,
        threshold_type: "upper",
        line_style: "dashed",
        label: "threshold"
      },
      defaultBinding: {
        source: "sample.detector",
        threshold_value: "threshold"
      }
    },
    {
      code: "state_timeline",
      name: "State Timeline",
      implemented: true,
      overlayCapable: false,
      defaultArea: "bottom_right",
      defaultConfig: {
        time_field: "time",
        state_field: "state",
        segment_merge: true
      },
      defaultBinding: {
        source: "sample.states",
        time_field: "time",
        state_field: "state"
      }
    },
    {
      code: "event_marker",
      name: "Event Marker",
      implemented: true,
      overlayCapable: true,
      defaultArea: "bottom_left",
      defaultConfig: {
        time_field: "time",
        event_type_field: "event_type",
        label_field: "label",
        marker_style: "flag"
      },
      defaultBinding: {
        source: "sample.events",
        time_field: "time",
        event_type_field: "event_type",
        label_field: "label"
      }
    },
    {
      code: "reference_current_comparison",
      name: "Reference Current Comparison",
      implemented: true,
      overlayCapable: false,
      defaultArea: "top_right",
      defaultConfig: {
        metric_field: "metric",
        reference_field: "reference",
        current_field: "current",
        delta_mode: "absolute"
      },
      defaultBinding: {
        source: "sample.referenceCurrent",
        metric_field: "metric",
        reference_field: "reference",
        current_field: "current"
      }
    },
    {
      code: "distribution_view",
      name: "Distribution View",
      implemented: true,
      overlayCapable: false,
      defaultArea: "top_left",
      defaultConfig: {
        value_field: "value",
        group_field: "group",
        bin_count: 12,
        display_mode: "histogram_overlay"
      },
      defaultBinding: {
        source: "sample.distribution",
        value_field: "value",
        group_field: "group"
      }
    },
    {
      code: "adaptive_model_structure_view",
      name: "Adaptive Model Structure",
      implemented: true,
      overlayCapable: false,
      defaultArea: "top_left",
      defaultConfig: {
        time_field: "time",
        primary_series_field: "primary_score",
        secondary_series_field: "secondary_score",
        event_field: "event",
        primary_label: "main model",
        secondary_label: "alternate model",
        event_types: ["replacement", "promotion", "retrain"]
      },
      defaultBinding: {
        source: "sample.adaptiveModelStructure",
        time_field: "time",
        primary_series_field: "primary_score",
        secondary_series_field: "secondary_score",
        event_field: "event"
      }
    },
    {
      code: "annotation_callout",
      name: "Annotation Callout",
      implemented: true,
      overlayCapable: true,
      defaultArea: "top_right",
      defaultConfig: {
        x: 0.72,
        y: 0.28,
        text: "important segment",
        direction: "right",
        severity: "warning"
      },
      defaultBinding: {
        source: "sample.annotationCallout",
        x: "x",
        y: "y",
        text: "text"
      }
    },
    {
      code: "comparison_table",
      name: "Comparison Table",
      implemented: true,
      overlayCapable: false,
      defaultArea: "top_right",
      defaultConfig: {
        row_field: "metric",
        reference_field: "reference",
        current_field: "current",
        delta_mode: "absolute"
      },
      defaultBinding: {
        source: "sample.comparisonTable",
        row_field: "metric",
        reference_field: "reference",
        current_field: "current"
      }
    },
    {
      code: "contribution_view",
      name: "Contribution View",
      implemented: true,
      overlayCapable: false,
      defaultArea: "top_right",
      defaultConfig: {
        contributor_field: "feature",
        contribution_field: "contribution",
        top_n: 6,
        signed: true
      },
      defaultBinding: {
        source: "sample.contributions",
        contributor_field: "feature",
        contribution_field: "contribution"
      }
    },
    {
      code: "control_chart",
      name: "Control Chart",
      implemented: true,
      overlayCapable: false,
      defaultArea: "top_left",
      defaultConfig: {
        time_field: "time",
        statistic_field: "statistic",
        center_value: 0.50,
        ucl: 0.78,
        lcl: 0.22,
        show_points: true
      },
      defaultBinding: {
        source: "sample.control",
        time_field: "time",
        statistic_field: "statistic"
      }
    },
    {
      code: "cumulative_curve",
      name: "Cumulative Curve",
      implemented: true,
      overlayCapable: false,
      defaultArea: "top_left",
      defaultConfig: {
        x_field: "x",
        y_field: "cumulative",
        series_field: "series",
        normalize: true,
        gap_marker: true
      },
      defaultBinding: {
        source: "sample.cumulative",
        x_field: "x",
        y_field: "cumulative",
        series_field: "series"
      }
    },
    {
      code: "decision_card",
      name: "Decision Card",
      implemented: true,
      overlayCapable: false,
      defaultArea: "top_left",
      defaultConfig: {
        decision_field: "decision",
        primary_metric_field: "metric_value",
        threshold_field: "threshold",
        label_field: "label"
      },
      defaultBinding: {
        source: "sample.decision",
        decision_field: "decision",
        primary_metric_field: "metric_value",
        threshold_field: "threshold",
        label_field: "label"
      }
    },
    {
      code: "distance_metric_view",
      name: "Distance Metric View",
      implemented: true,
      overlayCapable: false,
      defaultArea: "top_right",
      defaultConfig: {
        distance_field: "distance",
        group_field: "feature",
        baseline_distance: 0.20,
        normalize: false,
        sort_order: "value_desc"
      },
      defaultBinding: {
        source: "sample.distances",
        distance_field: "distance",
        group_field: "feature"
      }
    },
    {
      code: "distribution_summary_plot",
      name: "Distribution Summary Plot",
      implemented: true,
      overlayCapable: false,
      defaultArea: "top_left",
      defaultConfig: {
        plot_type: "box_violin",
        group_field: "group",
        value_field: "value",
        show_outliers: true
      },
      defaultBinding: {
        source: "sample.distribution",
        group_field: "group",
        value_field: "value"
      }
    },
    {
      code: "domain_specific_visual",
      name: "Domain Specific Visual",
      implemented: true,
      overlayCapable: false,
      defaultArea: "top_left",
      defaultConfig: {
        visual_code: "edf_area_gap",
        fallback_component: "cumulative_curve",
        generalization_candidate: true,
        input_schema: ["x", "reference", "current", "gap"]
      },
      defaultBinding: {
        source: "sample.domainSpecific",
        x_field: "x",
        reference_field: "reference",
        current_field: "current",
        gap_field: "gap"
      }
    },
    {
      code: "heatmap",
      name: "Heatmap",
      implemented: true,
      overlayCapable: false,
      defaultArea: "top_left",
      defaultConfig: {
        x_field: "bucket",
        y_field: "feature",
        value_field: "score",
        color_scale: "sequential",
        highlight_threshold: 0.70
      },
      defaultBinding: {
        source: "sample.heatmap",
        x_field: "bucket",
        y_field: "feature",
        value_field: "score"
      }
    },
    {
      code: "histogram_view",
      name: "Histogram View",
      implemented: true,
      overlayCapable: false,
      defaultArea: "top_left",
      defaultConfig: {
        bin_field: "bin",
        count_field: "count",
        series_field: "series",
        overlay_mode: "side_by_side"
      },
      defaultBinding: {
        source: "sample.histogram",
        bin_field: "bin",
        count_field: "count",
        series_field: "series"
      }
    },
    {
      code: "matrix_view",
      name: "Matrix View",
      implemented: true,
      overlayCapable: false,
      defaultArea: "top_left",
      defaultConfig: {
        row_field: "method",
        column_field: "condition",
        cell_value_field: "status",
        cell_palette: "status"
      },
      defaultBinding: {
        source: "sample.matrix",
        row_field: "method",
        column_field: "condition",
        cell_value_field: "status"
      }
    },
    {
      code: "model_diagnostic_curve",
      name: "Model Diagnostic Curve",
      implemented: true,
      overlayCapable: false,
      defaultArea: "top_left",
      defaultConfig: {
        curve_type: "roc",
        x_field: "fpr",
        y_field: "tpr",
        reference_line: true,
        auc: 0.84
      },
      defaultBinding: {
        source: "sample.modelDiagnostic",
        x_field: "fpr",
        y_field: "tpr"
      }
    },
    {
      code: "p_value_view",
      name: "P-value View",
      implemented: true,
      overlayCapable: false,
      defaultArea: "top_right",
      defaultConfig: {
        p_value_field: "p_value",
        label_field: "feature",
        alpha: 0.05,
        transform: "none",
        multiple_testing_adjustment: "none"
      },
      defaultBinding: {
        source: "sample.pValues",
        p_value_field: "p_value",
        label_field: "feature"
      }
    },
    {
      code: "performance_metric_view",
      name: "Performance Metric View",
      implemented: true,
      overlayCapable: false,
      defaultArea: "top_right",
      defaultConfig: {
        metric_field: "metric",
        value_field: "value",
        baseline_field: "baseline",
        target_field: "target",
        direction_field: "direction"
      },
      defaultBinding: {
        source: "sample.performance",
        metric_field: "metric",
        value_field: "value",
        baseline_field: "baseline",
        target_field: "target",
        direction_field: "direction"
      }
    },
    {
      code: "projection_scatter",
      name: "Projection Scatter",
      implemented: true,
      overlayCapable: false,
      defaultArea: "top_left",
      defaultConfig: {
        x_field: "x",
        y_field: "y",
        group_field: "group",
        centroid: true,
        sample_limit: 40
      },
      defaultBinding: {
        source: "sample.projection",
        x_field: "x",
        y_field: "y",
        group_field: "group"
      }
    },
    {
      code: "proportion_view",
      name: "Proportion View",
      implemented: true,
      overlayCapable: false,
      defaultArea: "top_right",
      defaultConfig: {
        category_field: "category",
        proportion_field: "proportion",
        series_field: "series",
        display_mode: "stacked"
      },
      defaultBinding: {
        source: "sample.proportions",
        category_field: "category",
        proportion_field: "proportion",
        series_field: "series"
      }
    },
    {
      code: "quantile_view",
      name: "Quantile View",
      implemented: true,
      overlayCapable: false,
      defaultArea: "top_right",
      defaultConfig: {
        quantile_field: "quantile",
        value_field: "delta",
        target_line: 0,
        tail_emphasis: true
      },
      defaultBinding: {
        source: "sample.quantiles",
        quantile_field: "quantile",
        value_field: "delta"
      }
    },
    {
      code: "ranking_view",
      name: "Ranking View",
      implemented: true,
      overlayCapable: false,
      defaultArea: "top_right",
      defaultConfig: {
        item_field: "item",
        score_field: "score",
        top_n: 6,
        sort_order: "score_desc"
      },
      defaultBinding: {
        source: "sample.ranking",
        item_field: "item",
        score_field: "score"
      }
    },
    {
      code: "raw_signal_trend",
      name: "Raw Signal Trend",
      implemented: true,
      overlayCapable: false,
      defaultArea: "top_left",
      defaultConfig: {
        time_field: "time",
        value_field: "signal",
        reference_value: 0.50,
        smoothing_window: 3
      },
      defaultBinding: {
        source: "sample.rawSignal",
        time_field: "time",
        value_field: "signal"
      }
    },
    {
      code: "small_multiples",
      name: "Small Multiples",
      implemented: true,
      overlayCapable: false,
      defaultArea: "top_left",
      defaultConfig: {
        facet_field: "feature",
        time_field: "time",
        value_field: "value",
        shared_scale: true,
        max_panels: 4
      },
      defaultBinding: {
        source: "sample.smallMultiples",
        facet_field: "feature",
        time_field: "time",
        value_field: "value"
      }
    },
    {
      code: "uncertainty_band",
      name: "Uncertainty Band",
      implemented: true,
      overlayCapable: true,
      defaultArea: "top_left",
      defaultConfig: {
        time_field: "time",
        lower_field: "lower",
        upper_field: "upper",
        center_field: "center",
        band_opacity: 0.24,
        band_mode: "confidence_interval"
      },
      defaultBinding: {
        source: "sample.uncertainty",
        time_field: "time",
        lower_field: "lower",
        upper_field: "upper",
        center_field: "center"
      }
    },
    {
      code: "window_view",
      name: "Window View",
      implemented: true,
      overlayCapable: false,
      defaultArea: "bottom_right",
      defaultConfig: {
        window_id_field: "window",
        start_field: "start",
        end_field: "end",
        window_role_field: "role",
        show_boundaries: true
      },
      defaultBinding: {
        source: "sample.windows",
        window_id_field: "window",
        start_field: "start",
        end_field: "end",
        window_role_field: "role"
      }
    }
  ];

  // @managed-contract contract_id=chart_builder.sampleData level=P1
  const sampleData = {
    trend: [
      { time: 1, value: 0.28 }, { time: 2, value: 0.30 }, { time: 3, value: 0.31 },
      { time: 4, value: 0.33 }, { time: 5, value: 0.36 }, { time: 6, value: 0.43 },
      { time: 7, value: 0.48 }, { time: 8, value: 0.53 }, { time: 9, value: 0.57 },
      { time: 10, value: 0.64 }, { time: 11, value: 0.69 }, { time: 12, value: 0.73 }
    ],
    bars: [
      { feature: "age", score: 0.34 }, { feature: "income", score: 0.72 },
      { feature: "region", score: 0.51 }, { feature: "channel", score: 0.47 },
      { feature: "device", score: 0.29 }
    ],
    detector: [
      { time: 1, statistic: 0.18, threshold: 0.68 }, { time: 2, statistic: 0.22, threshold: 0.68 },
      { time: 3, statistic: 0.28, threshold: 0.68 }, { time: 4, statistic: 0.31, threshold: 0.68 },
      { time: 5, statistic: 0.37, threshold: 0.68 }, { time: 6, statistic: 0.45, threshold: 0.68 },
      { time: 7, statistic: 0.59, threshold: 0.68 }, { time: 8, statistic: 0.67, threshold: 0.68 },
      { time: 9, statistic: 0.74, threshold: 0.68 }, { time: 10, statistic: 0.79, threshold: 0.68 },
      { time: 11, statistic: 0.82, threshold: 0.68 }, { time: 12, statistic: 0.86, threshold: 0.68 }
    ],
    states: [
      { time: 1, state: "normal" }, { time: 2, state: "normal" }, { time: 3, state: "normal" },
      { time: 4, state: "normal" }, { time: 5, state: "warning" }, { time: 6, state: "warning" },
      { time: 7, state: "warning" }, { time: 8, state: "drift" }, { time: 9, state: "drift" },
      { time: 10, state: "drift" }, { time: 11, state: "drift" }, { time: 12, state: "drift" }
    ],
    events: [
      { time: 4, event_type: "deploy", label: "deploy" },
      { time: 8, event_type: "drift", label: "drift" },
      { time: 11, event_type: "review", label: "review" }
    ],
    referenceCurrent: [
      { metric: "mean", reference: 0.42, current: 0.58 },
      { metric: "p95", reference: 0.71, current: 0.84 },
      { metric: "missing", reference: 0.03, current: 0.08 },
      { metric: "psi", reference: 0.10, current: 0.26 }
    ],
    distribution: [
      { group: "reference", value: 0.18 }, { group: "reference", value: 0.22 },
      { group: "reference", value: 0.25 }, { group: "reference", value: 0.28 },
      { group: "reference", value: 0.31 }, { group: "reference", value: 0.34 },
      { group: "reference", value: 0.36 }, { group: "reference", value: 0.40 },
      { group: "reference", value: 0.43 }, { group: "reference", value: 0.46 },
      { group: "reference", value: 0.50 }, { group: "reference", value: 0.54 },
      { group: "current", value: 0.32 }, { group: "current", value: 0.37 },
      { group: "current", value: 0.42 }, { group: "current", value: 0.48 },
      { group: "current", value: 0.53 }, { group: "current", value: 0.57 },
      { group: "current", value: 0.61 }, { group: "current", value: 0.66 },
      { group: "current", value: 0.70 }, { group: "current", value: 0.74 },
      { group: "current", value: 0.78 }, { group: "current", value: 0.82 }
    ],
    pValues: [
      { feature: "age", p_value: 0.180 },
      { feature: "income", p_value: 0.032 },
      { feature: "region", p_value: 0.006 },
      { feature: "channel", p_value: 0.074 },
      { feature: "device", p_value: 0.012 },
      { feature: "tenure", p_value: 0.240 }
    ],
    distances: [
      { feature: "income", distance: 0.42 },
      { feature: "region", distance: 0.31 },
      { feature: "device", distance: 0.26 },
      { feature: "channel", distance: 0.18 },
      { feature: "age", distance: 0.12 },
      { feature: "tenure", distance: 0.09 }
    ],
    performance: [
      { metric: "AUC", value: 0.82, baseline: 0.87, target: 0.85, direction: "higher_is_better" },
      { metric: "F1", value: 0.76, baseline: 0.79, target: 0.78, direction: "higher_is_better" },
      { metric: "error", value: 0.18, baseline: 0.12, target: 0.15, direction: "lower_is_better" },
      { metric: "latency", value: 0.34, baseline: 0.28, target: 0.32, direction: "lower_is_better" }
    ],
    proportions: [
      { series: "reference", category: "A", proportion: 0.42 },
      { series: "reference", category: "B", proportion: 0.28 },
      { series: "reference", category: "C", proportion: 0.18 },
      { series: "reference", category: "D", proportion: 0.12 },
      { series: "current", category: "A", proportion: 0.31 },
      { series: "current", category: "B", proportion: 0.34 },
      { series: "current", category: "C", proportion: 0.25 },
      { series: "current", category: "D", proportion: 0.10 }
    ],
    projection: [
      { group: "reference", x: -1.2, y: -0.4 }, { group: "reference", x: -1.0, y: -0.2 },
      { group: "reference", x: -0.8, y: -0.5 }, { group: "reference", x: -0.6, y: -0.1 },
      { group: "reference", x: -1.1, y: 0.1 }, { group: "reference", x: -0.9, y: 0.2 },
      { group: "reference", x: -0.7, y: 0.0 }, { group: "reference", x: -1.3, y: -0.1 },
      { group: "reference", x: -0.5, y: -0.4 }, { group: "reference", x: -0.9, y: -0.7 },
      { group: "current", x: 0.2, y: 0.1 }, { group: "current", x: 0.4, y: 0.3 },
      { group: "current", x: 0.6, y: 0.0 }, { group: "current", x: 0.8, y: 0.4 },
      { group: "current", x: 0.5, y: 0.6 }, { group: "current", x: 0.9, y: 0.2 },
      { group: "current", x: 0.3, y: -0.1 }, { group: "current", x: 0.7, y: -0.2 },
      { group: "current", x: 1.0, y: 0.5 }, { group: "current", x: 0.5, y: 0.1 }
    ],
    histogram: [
      { series: "reference", bin: "0.0-0.2", count: 18 },
      { series: "reference", bin: "0.2-0.4", count: 34 },
      { series: "reference", bin: "0.4-0.6", count: 29 },
      { series: "reference", bin: "0.6-0.8", count: 15 },
      { series: "reference", bin: "0.8-1.0", count: 4 },
      { series: "current", bin: "0.0-0.2", count: 9 },
      { series: "current", bin: "0.2-0.4", count: 21 },
      { series: "current", bin: "0.4-0.6", count: 31 },
      { series: "current", bin: "0.6-0.8", count: 25 },
      { series: "current", bin: "0.8-1.0", count: 14 }
    ],
    heatmap: [
      { feature: "income", bucket: "w1", score: 0.22 }, { feature: "income", bucket: "w2", score: 0.34 }, { feature: "income", bucket: "w3", score: 0.61 }, { feature: "income", bucket: "w4", score: 0.78 },
      { feature: "region", bucket: "w1", score: 0.18 }, { feature: "region", bucket: "w2", score: 0.29 }, { feature: "region", bucket: "w3", score: 0.45 }, { feature: "region", bucket: "w4", score: 0.66 },
      { feature: "device", bucket: "w1", score: 0.12 }, { feature: "device", bucket: "w2", score: 0.31 }, { feature: "device", bucket: "w3", score: 0.74 }, { feature: "device", bucket: "w4", score: 0.82 },
      { feature: "channel", bucket: "w1", score: 0.08 }, { feature: "channel", bucket: "w2", score: 0.21 }, { feature: "channel", bucket: "w3", score: 0.38 }, { feature: "channel", bucket: "w4", score: 0.52 }
    ],
    ranking: [
      { item: "income", score: 0.86 },
      { item: "device", score: 0.74 },
      { item: "region", score: 0.66 },
      { item: "channel", score: 0.52 },
      { item: "age", score: 0.31 },
      { item: "tenure", score: 0.24 },
      { item: "segment", score: 0.18 }
    ],
    contributions: [
      { feature: "income", contribution: 0.34 },
      { feature: "device", contribution: 0.27 },
      { feature: "region", contribution: 0.18 },
      { feature: "channel", contribution: -0.14 },
      { feature: "age", contribution: 0.11 },
      { feature: "tenure", contribution: -0.08 },
      { feature: "segment", contribution: 0.06 }
    ],
    decision: [
      {
        decision: "drift",
        metric_value: 0.86,
        threshold: 0.68,
        label: "Detector statistic exceeds threshold"
      }
    ],
    comparisonTable: [
      { metric: "AUC", reference: 0.87, current: 0.82 },
      { metric: "F1", reference: 0.79, current: 0.76 },
      { metric: "error", reference: 0.12, current: 0.18 },
      { metric: "latency", reference: 0.28, current: 0.34 }
    ],
    control: [
      { time: 1, statistic: 0.44 }, { time: 2, statistic: 0.48 },
      { time: 3, statistic: 0.52 }, { time: 4, statistic: 0.55 },
      { time: 5, statistic: 0.61 }, { time: 6, statistic: 0.66 },
      { time: 7, statistic: 0.72 }, { time: 8, statistic: 0.81 },
      { time: 9, statistic: 0.76 }, { time: 10, statistic: 0.84 },
      { time: 11, statistic: 0.69 }, { time: 12, statistic: 0.58 }
    ],
    annotationCallout: [
      { x: 0.72, y: 0.28, text: "one-sided drift band" },
      { x: 0.31, y: 0.64, text: "not counted region" },
      { x: 0.54, y: 0.42, text: "exact check required" }
    ],
    adaptiveModelStructure: [
      { time: 1, primary_score: 0.42, secondary_score: 0.31, event: "" },
      { time: 2, primary_score: 0.45, secondary_score: 0.34, event: "" },
      { time: 3, primary_score: 0.48, secondary_score: 0.36, event: "retrain" },
      { time: 4, primary_score: 0.50, secondary_score: 0.39, event: "" },
      { time: 5, primary_score: 0.53, secondary_score: 0.43, event: "promotion" },
      { time: 6, primary_score: 0.56, secondary_score: 0.47, event: "" },
      { time: 7, primary_score: 0.60, secondary_score: 0.51, event: "replacement" },
      { time: 8, primary_score: 0.66, secondary_score: 0.58, event: "" },
      { time: 9, primary_score: 0.70, secondary_score: 0.62, event: "" },
      { time: 10, primary_score: 0.74, secondary_score: 0.67, event: "retrain" }
    ],
    cumulative: [
      { series: "reference", x: 0.10, cumulative: 0.08 }, { series: "reference", x: 0.20, cumulative: 0.18 },
      { series: "reference", x: 0.30, cumulative: 0.31 }, { series: "reference", x: 0.40, cumulative: 0.44 },
      { series: "reference", x: 0.50, cumulative: 0.56 }, { series: "reference", x: 0.60, cumulative: 0.68 },
      { series: "reference", x: 0.70, cumulative: 0.79 }, { series: "reference", x: 0.80, cumulative: 0.88 },
      { series: "reference", x: 0.90, cumulative: 0.95 }, { series: "reference", x: 1.00, cumulative: 1.00 },
      { series: "current", x: 0.10, cumulative: 0.04 }, { series: "current", x: 0.20, cumulative: 0.10 },
      { series: "current", x: 0.30, cumulative: 0.19 }, { series: "current", x: 0.40, cumulative: 0.31 },
      { series: "current", x: 0.50, cumulative: 0.46 }, { series: "current", x: 0.60, cumulative: 0.61 },
      { series: "current", x: 0.70, cumulative: 0.75 }, { series: "current", x: 0.80, cumulative: 0.86 },
      { series: "current", x: 0.90, cumulative: 0.94 }, { series: "current", x: 1.00, cumulative: 1.00 }
    ],
    domainSpecific: [
      { x: 0.10, reference: 0.08, current: 0.04, gap: -0.04 },
      { x: 0.20, reference: 0.18, current: 0.10, gap: -0.08 },
      { x: 0.30, reference: 0.31, current: 0.19, gap: -0.12 },
      { x: 0.40, reference: 0.44, current: 0.31, gap: -0.13 },
      { x: 0.50, reference: 0.56, current: 0.46, gap: -0.10 },
      { x: 0.60, reference: 0.68, current: 0.61, gap: -0.07 },
      { x: 0.70, reference: 0.79, current: 0.75, gap: -0.04 },
      { x: 0.80, reference: 0.88, current: 0.86, gap: -0.02 }
    ],
    matrix: [
      { method: "KS", condition: "numeric", status: "recommended" },
      { method: "KS", condition: "categorical", status: "blocked" },
      { method: "PSI", condition: "numeric", status: "supported" },
      { method: "PSI", condition: "categorical", status: "supported" },
      { method: "MMD", condition: "numeric", status: "supported" },
      { method: "MMD", condition: "categorical", status: "limited" },
      { method: "Chi2", condition: "numeric", status: "limited" },
      { method: "Chi2", condition: "categorical", status: "recommended" }
    ],
    modelDiagnostic: [
      { fpr: 0.00, tpr: 0.00 }, { fpr: 0.05, tpr: 0.24 },
      { fpr: 0.12, tpr: 0.43 }, { fpr: 0.20, tpr: 0.61 },
      { fpr: 0.34, tpr: 0.76 }, { fpr: 0.48, tpr: 0.85 },
      { fpr: 0.66, tpr: 0.93 }, { fpr: 1.00, tpr: 1.00 }
    ],
    quantiles: [
      { quantile: "q05", delta: -0.10 },
      { quantile: "q25", delta: -0.04 },
      { quantile: "q50", delta: 0.03 },
      { quantile: "q75", delta: 0.11 },
      { quantile: "q95", delta: 0.22 }
    ],
    rawSignal: [
      { time: 1, signal: 0.47 }, { time: 2, signal: 0.49 }, { time: 3, signal: 0.51 },
      { time: 4, signal: 0.50 }, { time: 5, signal: 0.56 }, { time: 6, signal: 0.62 },
      { time: 7, signal: 0.70 }, { time: 8, signal: 0.66 }, { time: 9, signal: 0.73 },
      { time: 10, signal: 0.78 }, { time: 11, signal: 0.74 }, { time: 12, signal: 0.81 }
    ],
    smallMultiples: [
      { feature: "income", time: 1, value: 0.22 }, { feature: "income", time: 2, value: 0.31 }, { feature: "income", time: 3, value: 0.48 }, { feature: "income", time: 4, value: 0.64 },
      { feature: "device", time: 1, value: 0.18 }, { feature: "device", time: 2, value: 0.28 }, { feature: "device", time: 3, value: 0.52 }, { feature: "device", time: 4, value: 0.72 },
      { feature: "region", time: 1, value: 0.15 }, { feature: "region", time: 2, value: 0.22 }, { feature: "region", time: 3, value: 0.35 }, { feature: "region", time: 4, value: 0.49 },
      { feature: "channel", time: 1, value: 0.12 }, { feature: "channel", time: 2, value: 0.17 }, { feature: "channel", time: 3, value: 0.25 }, { feature: "channel", time: 4, value: 0.39 }
    ],
    uncertainty: [
      { time: 1, lower: 0.30, center: 0.40, upper: 0.50 },
      { time: 2, lower: 0.34, center: 0.45, upper: 0.56 },
      { time: 3, lower: 0.38, center: 0.51, upper: 0.64 },
      { time: 4, lower: 0.43, center: 0.59, upper: 0.74 },
      { time: 5, lower: 0.50, center: 0.68, upper: 0.86 },
      { time: 6, lower: 0.58, center: 0.76, upper: 0.94 }
    ],
    windows: [
      { window: "ref", start: 1, end: 4, role: "reference" },
      { window: "cur", start: 5, end: 8, role: "current" },
      { window: "slide", start: 7, end: 10, role: "warning" },
      { window: "adapt", start: 10, end: 12, role: "drift" }
    ]
  };

  // @managed-contract contract_id=chart_builder.layoutPresets level=P1
  const layoutPresets = {
    prototype_2x2: {
      presetCode: "prototype_2x2",
      displayName: "2x2 Grid",
      layoutType: "semantic_grid",
      columns: 2,
      rows: 2,
      areas: [
        { area: "top_left", role: "primary_visual", x: 0, y: 0, w: 1, h: 1 },
        { area: "top_right", role: "secondary_visual", x: 1, y: 0, w: 1, h: 1 },
        { area: "bottom_left", role: "primary_visual", x: 0, y: 1, w: 1, h: 1 },
        { area: "bottom_right", role: "secondary_visual", x: 1, y: 1, w: 1, h: 1 }
      ]
    },
    default_3_panel: {
      presetCode: "default_3_panel",
      displayName: "Default 3 Panel",
      layoutType: "semantic_grid",
      columns: 12,
      rows: 8,
      areas: [
        { area: "summary", role: "summary", x: 0, y: 0, w: 12, h: 1 },
        { area: "main", role: "primary_visual", x: 0, y: 1, w: 8, h: 5 },
        { area: "side_top", role: "secondary_visual", x: 8, y: 1, w: 4, h: 2 },
        { area: "side_bottom", role: "secondary_visual", x: 8, y: 3, w: 4, h: 3 },
        { area: "notes", role: "interpretation", x: 0, y: 6, w: 12, h: 2 }
      ]
    }
  };

  // @managed-contract contract_id=chart_builder.defaultPayload level=P1
  const defaultPayload = {
    chartId: "CHART-PROTOTYPE-001",
    layout: cloneLayoutPreset("prototype_2x2"),
    components: []
  };

  const chartContainer = document.getElementById("chartContainer");
  const componentPalette = document.getElementById("componentPalette");
  const selectionSummary = document.getElementById("selectionSummary");
  const configEditor = document.getElementById("configEditor");
  const bindingEditor = document.getElementById("bindingEditor");
  const payloadViewer = document.getElementById("payloadViewer");
  const builderStatus = document.getElementById("builderStatus");
  const layoutPresetSelect = document.getElementById("layoutPresetSelect");
  const savedLayoutSelect = document.getElementById("savedLayoutSelect");
  const openLayoutDesignerButton = document.getElementById("openLayoutDesignerButton");
  const savedChartSelect = document.getElementById("savedChartSelect");
  const chartNameInput = document.getElementById("chartNameInput");
  const newChartButton = document.getElementById("newChartButton");
  const saveChartButton = document.getElementById("saveChartButton");
  const deleteChartButton = document.getElementById("deleteChartButton");
  const buildButton = document.getElementById("buildButton");
  const resetButton = document.getElementById("resetButton");
  const applyPropertiesButton = document.getElementById("applyPropertiesButton");
  const deleteComponentButton = document.getElementById("deleteComponentButton");

  let payload = clone(defaultPayload);
  let selectedComponentType = "trend_line";
  let selectedArea = null;
  let selectedInstanceId = null;
  const resizeObservers = new Map();
  let dragState = null;
  let savedLayouts = [];
  let savedCharts = [];

  function clone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function cloneLayoutPreset(presetCode) {
    const preset = layoutPresets[presetCode] || layoutPresets.prototype_2x2;
    return clone(preset);
  }

  function typeByCode(code) {
    return componentTypes.find((item) => item.code === code);
  }

  function componentApiUrl() {
    if (window.location.protocol === "http:" || window.location.protocol === "https:") {
      return `${window.location.origin}/api/chart-builder/prototype`;
    }
    return "http://127.0.0.1:8766/api/chart-builder/prototype";
  }

  function layoutsApiUrl(layoutName) {
    const base = window.location.protocol === "http:" || window.location.protocol === "https:"
      ? `${window.location.origin}/api/chart-builder/layouts`
      : "http://127.0.0.1:8766/api/chart-builder/layouts";
    return layoutName ? `${base}/${encodeURIComponent(layoutName)}` : base;
  }

  function chartsApiUrl(chartName) {
    const base = window.location.protocol === "http:" || window.location.protocol === "https:"
      ? `${window.location.origin}/api/chart-builder/charts`
      : "http://127.0.0.1:8766/api/chart-builder/charts";
    return chartName ? `${base}/${encodeURIComponent(chartName)}` : base;
  }

  function uid(prefix) {
    return `${prefix}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 7)}`;
  }

  function setStatus(message, kind = "") {
    builderStatus.textContent = message;
    builderStatus.dataset.kind = kind;
  }

  function renderPalette() {
    componentPalette.innerHTML = "";
    const sortedComponentTypes = componentTypes.slice().sort((a, b) => {
      if (Boolean(a.implemented) !== Boolean(b.implemented)) {
        return a.implemented ? -1 : 1;
      }
      return a.name.localeCompare(b.name);
    });
    sortedComponentTypes.forEach((component) => {
      const button = document.createElement("button");
      button.type = "button";
      button.draggable = true;
      button.className = [
        "palette-item",
        component.code === selectedComponentType ? "active" : "",
        component.implemented ? "implemented" : "draft"
      ].filter(Boolean).join(" ");
      button.dataset.componentType = component.code;
      button.innerHTML = [
        `<span class="palette-name">${component.name}</span>`,
        `<span class="palette-meta">${component.code}${component.overlayCapable ? " / overlay" : ""} / ${component.implemented ? "implemented" : "draft placeholder"}</span>`
      ].join("");
      button.addEventListener("click", () => {
        selectedComponentType = component.code;
        selectedInstanceId = null;
        renderPalette();
        updateProperties();
        setStatus(`${component.name} 선택됨. ${component.implemented ? "배치할 영역으로 드래그하세요." : "아직 renderer가 없어 placeholder로 배치됩니다."}`);
      });
      button.addEventListener("dragstart", (event) => {
        selectedComponentType = component.code;
        event.dataTransfer.effectAllowed = "copy";
        event.dataTransfer.setData("text/plain", component.code);
        renderPalette();
        setStatus(`${component.name}을 배치할 영역으로 드래그하세요.`);
      });
      button.addEventListener("pointerdown", (event) => {
        startPointerDrag(event, component);
      });
      componentPalette.appendChild(button);
    });
  }

  function startPointerDrag(event, component) {
    if (event.button !== 0) return;
    selectedComponentType = component.code;
    renderPalette();

    const ghost = document.createElement("div");
    ghost.className = "drag-ghost";
    ghost.textContent = component.name;
    document.body.appendChild(ghost);

    dragState = {
      componentCode: component.code,
      ghost,
      lastArea: null,
      moved: false
    };
    moveDragGhost(event.clientX, event.clientY);
    window.addEventListener("pointermove", onPointerDragMove);
    window.addEventListener("pointerup", onPointerDragEnd, { once: true });
    event.preventDefault();
    setStatus(`${component.name}을 배치할 영역으로 끌어 놓으세요.`);
  }

  function moveDragGhost(clientX, clientY) {
    if (!dragState) return;
    dragState.ghost.style.transform = `translate(${clientX + 12}px, ${clientY + 12}px)`;
  }

  function onPointerDragMove(event) {
    if (!dragState) return;
    dragState.moved = true;
    moveDragGhost(event.clientX, event.clientY);
    const area = document.elementFromPoint(event.clientX, event.clientY)?.closest(".chart-area");
    if (dragState.lastArea && dragState.lastArea !== area) {
      dragState.lastArea.classList.remove("drag-over");
    }
    if (area) area.classList.add("drag-over");
    dragState.lastArea = area || null;
  }

  function onPointerDragEnd(event) {
    if (!dragState) return;
    const area = document.elementFromPoint(event.clientX, event.clientY)?.closest(".chart-area");
    if (dragState.lastArea) dragState.lastArea.classList.remove("drag-over");
    dragState.ghost.remove();
    const componentCode = dragState.componentCode;
    const moved = dragState.moved;
    dragState = null;
    window.removeEventListener("pointermove", onPointerDragMove);

    if (area && moved) {
      selectedComponentType = componentCode;
      selectedArea = area.dataset.area;
      addSelectedComponent(selectedArea, { replaceBase: true });
      renderPalette();
    }
  }

  // @managed-contract contract_id=chart_builder.renderContainer level=P1
  function renderContainer() {
    cleanupObservers();
    chartContainer.innerHTML = "";
    layoutPresetSelect.value = payload.layout.presetCode || detectPresetCode(payload.layout);

    const runtimePayload = buildRuntimePayload();
    window.ChartRuntime.renderChartPayload(chartContainer, runtimePayload);
    chartContainer.querySelectorAll(".chart-area").forEach((areaEl) => {
      const areaCode = areaEl.dataset.area;
      const area = payload.layout.areas.find((item) => item.area === areaCode);
      if (!area) return;
      // The Builder catalog has its own field/visual contracts (including
      // controls such as ROC references and control limits). Keep the shared
      // Runtime shell and use the matching dedicated preview renderers.
      areaEl.querySelectorAll("[data-instance-id]").forEach((wrapper) => {
        const instance = payload.components.find((item) => item.componentInstanceId === wrapper.dataset.instanceId);
        const type = instance && typeByCode(instance.componentType);
        if (!type?.implemented) return;
        const usesCatalogConfig = Object.keys(type.defaultConfig || {}).every((key) =>
          Object.prototype.hasOwnProperty.call(instance.config || {}, key));
        const usesSample = String(instance.dataBinding?.source || "").startsWith("sample.");
        // Imported report charts already speak the shared Runtime contract.
        if (!usesSample && !usesCatalogConfig) return;
        if (!instance.isOverlay) areaEl.classList.add("builder-catalog-area");
        const renderInto = (target) => {
          const rect = target.getBoundingClientRect();
          const size = readableRenderSize(instance, Math.max(1, rect.width), Math.max(1, rect.height));
          target.innerHTML = renderComponent(instance, {
            width: size.width, height: size.height, mode: renderMode(size.width, size.height)
          });
        };
        const renderDedicated = () => renderInto(wrapper);
        renderDedicated();
        const observer = new ResizeObserver(renderDedicated);
        observer.observe(wrapper);
        resizeObservers.set(wrapper, observer);
        areaEl.querySelector(".area-zoom-link")?.addEventListener("click", () => {
          // Runtime opens the dialog on its bubbling listener. Fill the same
          // instance after that listener completes, using the Builder contract.
          requestAnimationFrame(() => {
            const zoomWrapper = [...document.querySelectorAll("#componentZoomPopup [data-instance-id]")]
              .find((item) => item.dataset.instanceId === instance.componentInstanceId);
            if (zoomWrapper) renderInto(zoomWrapper);
          });
        });
      });
      areaEl.classList.toggle("selected", selectedArea === area.area);
      if (!payload.components.some((item) => item.area === area.area)) {
        const body = areaEl.querySelector(".area-body");
        if (body) body.insertAdjacentHTML("beforeend", '<div class="empty-area">이 영역을 클릭하면 선택된 component가 배치됩니다.</div>');
      }
      areaEl.addEventListener("click", (event) => {
        if (event.target.closest("button, a")) return;
        const instanceEl = event.target.closest("[data-instance-id]");
        if (instanceEl) {
          selectedInstanceId = instanceEl.dataset.instanceId;
          selectedArea = area.area;
          updateProperties();
          renderContainer();
          return;
        }
        selectedArea = area.area;
        selectedInstanceId = null;
        if (selectedComponentType) {
          addSelectedComponent(area.area, { replaceBase: true });
          return;
        }
        updateProperties();
        renderContainer();
        setStatus(`${area.area} 영역을 선택했습니다. component 배치 또는 area 분할을 선택하세요.`);
      });
      areaEl.addEventListener("dragover", (event) => {
        event.preventDefault();
        areaEl.classList.add("drag-over");
        event.dataTransfer.dropEffect = "copy";
      });
      areaEl.addEventListener("dragleave", (event) => {
        if (!areaEl.contains(event.relatedTarget)) {
          areaEl.classList.remove("drag-over");
        }
      });
      areaEl.addEventListener("drop", (event) => {
        event.preventDefault();
        areaEl.classList.remove("drag-over");
        const componentCode = event.dataTransfer.getData("text/plain");
        if (componentCode) {
          selectedComponentType = componentCode;
          selectedArea = area.area;
          addSelectedComponent(area.area, { replaceBase: true });
          renderPalette();
        }
      });
    });
  }

  // @managed-contract contract_id=chart_builder.buildRuntimePayload level=P1
  function buildRuntimePayload() {
    const runtimePayload = clone(payload);
    runtimePayload.layout = clone(payload.layout);
    runtimePayload.layout.showAreaLabels = false;
    runtimePayload.layout.areas = (runtimePayload.layout.areas || []).map((area) => ({
      ...area,
      title: area.title || area.area,
      noteLabel: area.noteLabel || "Note"
    }));
    // Use the same source names as the catalog and local binding resolver.
    // Explicit chart data wins over preview samples, including empty arrays.
    runtimePayload.data = Object.fromEntries(
      Object.entries(sampleData).map(([name, rows]) => [`sample.${name}`, clone(rows)])
    );
    runtimePayload.data["sample.reference_current"] = clone(sampleData.referenceCurrent);
    runtimePayload.data["sample.p_values"] = clone(sampleData.pValues);
    Object.assign(runtimePayload.data, clone(payload.data || {}));
    runtimePayload.components = runtimePayload.components.map((instance) => {
      if (instance.componentType !== "adaptive_model_structure_view") return instance;
      // Preserve saved Builder aliases while supplying the shared line contract.
      const config = instance.config || {};
      return {
        ...instance,
        config: {
          ...config,
          value_field: config.value_field || config.primary_series_field || "value",
          secondary_value_field: config.secondary_value_field || config.secondary_series_field
        }
      };
    });
    return runtimePayload;
  }

  function detectPresetCode(layout) {
    const areaNames = (layout.areas || []).map((area) => area.area).sort().join(",");
    if (areaNames === "bottom_left,bottom_right,top_left,top_right") return "prototype_2x2";
    if (areaNames === "main,notes,side_bottom,side_top,summary") return "default_3_panel";
    return "prototype_2x2";
  }

  function changeLayoutPreset(presetCode) {
    const previousAreas = new Set((payload.layout.areas || []).map((area) => area.area));
    const nextLayout = cloneLayoutPreset(presetCode);
    const nextAreas = new Set(nextLayout.areas.map((area) => area.area));
    const areaMap = layoutAreaMap(payload.layout, nextLayout);
    payload.layout = nextLayout;
    payload.components = payload.components
      .map((component) => ({ ...component, area: areaMap[component.area] || component.area }))
      .filter((component) => nextAreas.has(component.area));
    selectedArea = null;
    selectedInstanceId = null;
    updatePayloadViewer();
    updateProperties();
    renderContainer();
    const removed = Array.from(previousAreas).filter((area) => !nextAreas.has(area));
    setStatus(`${nextLayout.displayName} layout을 적용했습니다.${removed.length ? " 일부 area component는 새 layout에 맞춰 이동 또는 제거되었습니다." : ""}`);
  }

  function layoutAreaMap(previousLayout, nextLayout) {
    const prevCode = detectPresetCode(previousLayout);
    const nextCode = nextLayout.presetCode;
    if (prevCode === "prototype_2x2" && nextCode === "default_3_panel") {
      return {
        top_left: "main",
        top_right: "side_top",
        bottom_left: "side_bottom",
        bottom_right: "notes"
      };
    }
    if (prevCode === "default_3_panel" && nextCode === "prototype_2x2") {
      return {
        summary: "top_left",
        main: "top_left",
        side_top: "top_right",
        side_bottom: "bottom_left",
        notes: "bottom_right"
      };
    }
    return {};
  }

  function renderArea(areaEl, areaCode) {
    const body = areaEl.querySelector(".area-body");
    const instances = payload.components.filter((item) => item.area === areaCode);
    if (!instances.length) {
      body.innerHTML = '<div class="empty-area">이 영역을 클릭하면 선택된 component가 배치됩니다.</div>';
      return;
    }

    const baseInstances = instances.filter((item) => !item.isOverlay);
    const overlayInstances = instances.filter((item) => item.isOverlay);

    if (!baseInstances.length && overlayInstances.length) {
      body.innerHTML = '<div class="empty-area">overlay 대상 component가 필요합니다.</div>';
      return;
    }

    const stack = document.createElement("div");
    stack.className = "component-stack";
    body.innerHTML = "";
    body.appendChild(stack);

    baseInstances.forEach((instance, index) => {
      const card = createComponentCard(instance);
      stack.appendChild(card);
      const overlays = index === 0 ? overlayInstances : [];
      observeAndRender(card, instance, overlays);
    });
  }

  function createComponentCard(instance) {
    const card = document.createElement("section");
    card.className = `component-card${selectedInstanceId === instance.componentInstanceId ? " selected" : ""}`;
    card.dataset.instanceId = instance.componentInstanceId;
    card.innerHTML = [
      `<div class="component-title">${instance.componentType}</div>`,
      '<div class="component-stage"></div>',
      '<div class="component-overlay"></div>'
    ].join("");
    card.addEventListener("click", (event) => {
      event.stopPropagation();
      selectedInstanceId = instance.componentInstanceId;
      selectedArea = instance.area;
      updateProperties();
      renderContainer();
    });
    return card;
  }

  function observeAndRender(card, instance, overlays) {
    const observer = new ResizeObserver(() => renderComponentCard(card, instance, overlays));
    observer.observe(card);
    resizeObservers.set(card, observer);
    renderComponentCard(card, instance, overlays);
  }

  function cleanupObservers() {
    resizeObservers.forEach((observer) => observer.disconnect());
    resizeObservers.clear();
  }

  function renderComponentCard(card, instance, overlays) {
    const stage = card.querySelector(".component-stage");
    const overlayStage = card.querySelector(".component-overlay");
    const rect = stage.getBoundingClientRect();
    const viewportWidth = Math.max(1, Math.floor(rect.width));
    const viewportHeight = Math.max(1, Math.floor(rect.height));
    const renderSize = readableRenderSize(instance, viewportWidth, viewportHeight);
    const width = renderSize.width;
    const height = renderSize.height;
    const context = { width, height, mode: renderMode(width, height) };
    stage.classList.toggle("scroll-x", renderSize.scrollX);
    stage.classList.toggle("scroll-y", renderSize.scrollY);
    stage.innerHTML = `<div class="component-render-surface" style="width: ${width}px; height: ${height}px;">${renderComponent(instance, context)}</div>`;
    overlayStage.innerHTML = overlays.map((overlay) => renderComponent(overlay, context)).join("");
  }

  function renderMode(width, height) {
    if (width < 190 || height < 115) return "summary_only";
    if (width < 320 || height < 190) return "compact";
    return "normal";
  }

  function readableRenderSize(instance, viewportWidth, viewportHeight) {
    const minSize = componentReadableMinimum(instance, viewportWidth, viewportHeight);
    const width = Math.max(viewportWidth, minSize.width);
    const height = Math.max(viewportHeight, minSize.height);
    return {
      width,
      height,
      scrollX: width > viewportWidth,
      scrollY: height > viewportHeight
    };
  }

  function componentReadableMinimum(instance, viewportWidth, viewportHeight) {
    if (instance.componentType === "bar_chart") {
      const data = dataForBinding(instance.dataBinding);
      const categoryField = instance.config.category_field || "feature";
      const longestCategory = data.reduce((max, item) => Math.max(max, String(item[categoryField] || "").length), 0);
      return {
        width: Math.max(220, longestCategory * 8 + 138),
        height: Math.max(130, data.length * 24 + 34)
      };
    }
    if (instance.componentType === "state_timeline") {
      const data = dataForBinding(instance.dataBinding);
      return {
        width: Math.max(220, data.length * 16 + 36),
        height: 110
      };
    }
    if (instance.componentType === "trend_line" || instance.componentType === "detector_statistic_view") {
      return {
        width: 220,
        height: 130
      };
    }
    if (instance.componentType === "event_marker") {
      return {
        width: 180,
        height: 90
      };
    }
    if (instance.componentType === "reference_current_comparison") {
      const data = dataForBinding(instance.dataBinding);
      return {
        width: 260,
        height: Math.max(140, data.length * 28 + 42)
      };
    }
    if (instance.componentType === "distribution_view") {
      return {
        width: 240,
        height: 150
      };
    }
    if (instance.componentType === "distribution_summary_plot") {
      return {
        width: 260,
        height: 160
      };
    }
    if (instance.componentType === "p_value_view") {
      const data = dataForBinding(instance.dataBinding);
      return {
        width: 240,
        height: Math.max(140, data.length * 24 + 42)
      };
    }
    if (instance.componentType === "distance_metric_view") {
      const data = dataForBinding(instance.dataBinding);
      return {
        width: 240,
        height: Math.max(140, data.length * 24 + 42)
      };
    }
    if (instance.componentType === "performance_metric_view") {
      const data = dataForBinding(instance.dataBinding);
      return {
        width: 270,
        height: Math.max(150, data.length * 30 + 44)
      };
    }
    if (instance.componentType === "proportion_view") {
      return {
        width: 260,
        height: 150
      };
    }
    if (instance.componentType === "projection_scatter") {
      return {
        width: 240,
        height: 180
      };
    }
    if (instance.componentType === "histogram_view") {
      const data = dataForBinding(instance.dataBinding);
      const binField = instance.config.bin_field || "bin";
      const binCount = new Set(data.map((item) => String(item[binField] || ""))).size;
      return {
        width: Math.max(260, binCount * 42 + 70),
        height: 160
      };
    }
    if (instance.componentType === "heatmap") {
      const data = dataForBinding(instance.dataBinding);
      const xField = instance.config.x_field || "bucket";
      const yField = instance.config.y_field || "feature";
      const columns = new Set(data.map((item) => String(item[xField] || ""))).size;
      const rows = new Set(data.map((item) => String(item[yField] || ""))).size;
      return {
        width: Math.max(240, columns * 46 + 90),
        height: Math.max(150, rows * 28 + 54)
      };
    }
    if (instance.componentType === "ranking_view") {
      const data = dataForBinding(instance.dataBinding);
      const topN = Math.min(data.length || 1, Number(instance.config.top_n || 6));
      return {
        width: 250,
        height: Math.max(150, topN * 26 + 44)
      };
    }
    if (instance.componentType === "contribution_view") {
      const data = dataForBinding(instance.dataBinding);
      const topN = Math.min(data.length || 1, Number(instance.config.top_n || 6));
      return {
        width: 260,
        height: Math.max(150, topN * 26 + 44)
      };
    }
    if (instance.componentType === "decision_card") {
      return {
        width: 220,
        height: 130
      };
    }
    if (instance.componentType === "comparison_table") {
      const data = dataForBinding(instance.dataBinding);
      return {
        width: 300,
        height: Math.max(150, data.length * 28 + 54)
      };
    }
    if (instance.componentType === "control_chart") {
      return {
        width: 240,
        height: 150
      };
    }
    if (instance.componentType === "annotation_callout") {
      return {
        width: 200,
        height: 110
      };
    }
    if (instance.componentType === "adaptive_model_structure_view") {
      return {
        width: 280,
        height: 180
      };
    }
    if (instance.componentType === "cumulative_curve") {
      return {
        width: 250,
        height: 160
      };
    }
    if (instance.componentType === "domain_specific_visual") {
      return {
        width: 260,
        height: 160
      };
    }
    if (instance.componentType === "matrix_view") {
      const data = dataForBinding(instance.dataBinding);
      const rowField = instance.config.row_field || "method";
      const columnField = instance.config.column_field || "condition";
      const rows = new Set(data.map((item) => String(item[rowField] || ""))).size;
      const columns = new Set(data.map((item) => String(item[columnField] || ""))).size;
      return {
        width: Math.max(240, columns * 70 + 90),
        height: Math.max(140, rows * 28 + 54)
      };
    }
    if (instance.componentType === "model_diagnostic_curve" || instance.componentType === "raw_signal_trend" || instance.componentType === "uncertainty_band") {
      return {
        width: 250,
        height: 160
      };
    }
    if (instance.componentType === "quantile_view") {
      const data = dataForBinding(instance.dataBinding);
      return {
        width: 240,
        height: Math.max(140, data.length * 24 + 42)
      };
    }
    if (instance.componentType === "small_multiples") {
      const panels = Math.max(1, Number(instance.config.max_panels || 4));
      return {
        width: 280,
        height: Math.max(180, Math.ceil(panels / 2) * 88)
      };
    }
    if (instance.componentType === "window_view") {
      const data = dataForBinding(instance.dataBinding);
      return {
        width: 260,
        height: Math.max(140, data.length * 26 + 44)
      };
    }
    return {
      width: Math.min(viewportWidth, 1),
      height: Math.min(viewportHeight, 1)
    };
  }

  function addSelectedComponent(areaCode, options = {}) {
    const type = typeByCode(selectedComponentType);
    if (!type) return;
    const hasBaseComponent = payload.components.some((item) => item.area === areaCode && !item.isOverlay);
    const replacedCount = options.replaceBase && !type.overlayCapable
      ? replaceBaseComponents(areaCode)
      : 0;
    const shouldUseOverlay = type.overlayCapable && hasBaseComponent;
    const instance = {
      componentInstanceId: uid(type.code),
      componentType: type.code,
      area: areaCode,
      isOverlay: shouldUseOverlay,
      zIndex: shouldUseOverlay ? 20 : 10,
      config: clone(type.defaultConfig || {}),
      dataBinding: clone(type.defaultBinding || {})
    };
    payload.components.push(instance);
    selectedInstanceId = instance.componentInstanceId;
    updatePayloadViewer();
    updateProperties();
    renderContainer();
    const action = replacedCount ? "교체했습니다" : "배치했습니다";
    const mode = shouldUseOverlay ? "overlay로 " : "";
    setStatus(`${type.name} component를 ${areaCode} 영역에 ${mode}${action}.`);
  }

  function replaceBaseComponents(areaCode) {
    const before = payload.components.length;
    payload.components = payload.components.filter((item) => item.area !== areaCode || item.isOverlay);
    return before - payload.components.length;
  }

  function updateProperties() {
    const instance = payload.components.find((item) => item.componentInstanceId === selectedInstanceId);
    if (!instance) {
      const type = typeByCode(selectedComponentType);
      selectionSummary.textContent = type
        ? `${type.name} 선택됨. 배치할 영역을 클릭하세요.`
        : "선택된 component가 없습니다.";
      configEditor.value = "";
      bindingEditor.value = "";
      return;
    }
    selectionSummary.innerHTML = [
      `<strong>${instance.componentType}</strong>`,
      `<br>area: <code>${instance.area}</code>`,
      `<br>${instance.isOverlay ? "overlay component" : "base component"}`
    ].join("");
    configEditor.value = JSON.stringify(instance.config, null, 2);
    bindingEditor.value = JSON.stringify(instance.dataBinding, null, 2);
  }

  function applyProperties() {
    const instance = payload.components.find((item) => item.componentInstanceId === selectedInstanceId);
    if (!instance) {
      setStatus("수정할 component를 먼저 선택하세요.", "warning");
      return;
    }
    try {
      instance.config = JSON.parse(configEditor.value || "{}");
      instance.dataBinding = JSON.parse(bindingEditor.value || "{}");
      updatePayloadViewer();
      renderContainer();
      setStatus("component 설정을 적용했습니다.");
    } catch (error) {
      setStatus(`JSON 오류: ${error.message}`, "error");
    }
  }

  function deleteSelectedComponent() {
    if (!selectedInstanceId) return;
    payload.components = payload.components.filter((item) => item.componentInstanceId !== selectedInstanceId);
    selectedInstanceId = null;
    updatePayloadViewer();
    updateProperties();
    renderContainer();
    setStatus("component를 삭제했습니다.");
  }

  function updatePayloadViewer() {
    payloadViewer.value = JSON.stringify(payload, null, 2);
  }

  function resetPrototype() {
    payload = clone(defaultPayload);
    selectedInstanceId = null;
    selectedArea = null;
    selectedComponentType = "trend_line";
    chartNameInput.value = "";
    renderAll();
    setStatus("초기 2x2 prototype으로 reset했습니다.");
  }

  async function loadPrototype() {
    try {
      const response = await fetch(componentApiUrl());
      const result = await response.json();
      if (!response.ok || !result.ok) throw new Error(result.error || "load failed");
      payload = result.payload || clone(defaultPayload);
      selectedInstanceId = null;
      selectedArea = null;
      renderAll();
      setStatus("서버에서 prototype payload를 불러왔습니다.");
    } catch (error) {
      const local = window.localStorage.getItem("chart_builder_prototype_payload");
      payload = local ? JSON.parse(local) : clone(defaultPayload);
      renderAll();
      setStatus(`서버 load 실패. local payload를 사용합니다: ${error.message}`, "warning");
    }
  }

  async function loadSavedLayouts() {
    try {
      const response = await fetch(layoutsApiUrl());
      const result = await response.json();
      if (!response.ok || !result.ok) throw new Error(result.error || "layout load failed");
      savedLayouts = Array.isArray(result.layouts) ? result.layouts : [];
      renderSavedLayoutSelect();
    } catch (error) {
      savedLayouts = JSON.parse(window.localStorage.getItem("chart_builder_saved_layouts") || "[]");
      renderSavedLayoutSelect();
      setStatus(`저장 layout 목록을 서버에서 불러오지 못해 localStorage를 사용합니다: ${error.message}`, "warning");
    }
  }

  function renderSavedLayoutSelect() {
    savedLayoutSelect.innerHTML = "";
    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = savedLayouts.length ? "저장 layout 선택" : "저장된 layout 없음";
    savedLayoutSelect.appendChild(placeholder);
    if (!savedLayouts.length) {
      return;
    }
    savedLayouts.forEach((item) => {
      const option = document.createElement("option");
      option.value = item.name;
      option.textContent = item.name;
      savedLayoutSelect.appendChild(option);
    });
  }

  function applySavedLayout() {
    const name = savedLayoutSelect.value;
    const saved = savedLayouts.find((item) => item.name === name);
    if (!saved || !saved.layout) {
      setStatus("불러올 layout을 선택하세요.", "warning");
      return;
    }
    payload.layout = clone(saved.layout);
    const validAreas = new Set((payload.layout.areas || []).map((area) => area.area));
    payload.components = payload.components.filter((component) => validAreas.has(component.area));
    selectedArea = null;
    selectedInstanceId = null;
    updatePayloadViewer();
    updateProperties();
    renderContainer();
    setStatus(`${name} layout을 적용했습니다. 새 layout에 없는 area의 component는 제거되었습니다.`);
  }

  async function loadSavedCharts() {
    try {
      const response = await fetch(chartsApiUrl());
      const result = await response.json();
      if (!response.ok || !result.ok) throw new Error(result.error || "chart load failed");
      savedCharts = Array.isArray(result.charts) ? result.charts : [];
      renderSavedChartSelect();
    } catch (error) {
      savedCharts = JSON.parse(window.localStorage.getItem("chart_builder_saved_charts") || "[]");
      renderSavedChartSelect();
      setStatus(`저장 chart 목록을 서버에서 불러오지 못해 localStorage를 사용합니다: ${error.message}`, "warning");
    }
  }

  function renderSavedChartSelect() {
    savedChartSelect.innerHTML = "";
    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = savedCharts.length ? "저장 chart 선택" : "저장된 chart 없음";
    savedChartSelect.appendChild(placeholder);
    savedCharts.forEach((item) => {
      const option = document.createElement("option");
      option.value = item.name;
      option.textContent = item.name;
      savedChartSelect.appendChild(option);
    });
  }

  function newChart() {
    const name = chartNameInput.value.trim();
    payload = clone(defaultPayload);
    if (name) {
      payload.chartId = name;
    }
    selectedInstanceId = null;
    selectedArea = null;
    selectedComponentType = "trend_line";
    renderAll();
    setStatus(name ? `${name} 새 chart를 시작했습니다.` : "새 chart를 시작했습니다.");
  }

  async function saveCurrentChart() {
    const name = chartNameInput.value.trim() || savedChartSelect.value || payload.chartId;
    if (!name) {
      setStatus("저장할 chart 이름을 입력하세요.", "warning");
      return;
    }
    const chartPayload = clone(payload);
    chartPayload.chartId = name;
    const body = { name, payload: chartPayload };
    try {
      const response = await fetch(chartsApiUrl(), {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      const result = await response.json();
      if (!response.ok || !result.ok) throw new Error(result.error || "chart save failed");
      savedCharts = result.charts || [];
      window.localStorage.setItem("chart_builder_saved_charts", JSON.stringify(savedCharts));
      payload = chartPayload;
      renderSavedChartSelect();
      savedChartSelect.value = name;
      chartNameInput.value = name;
      updatePayloadViewer();
      setStatus(`${name} chart를 저장했습니다.`);
    } catch (error) {
      savedCharts = savedCharts.filter((item) => item.name !== name).concat([body]);
      savedCharts.sort((a, b) => String(a.name).localeCompare(String(b.name)));
      window.localStorage.setItem("chart_builder_saved_charts", JSON.stringify(savedCharts));
      payload = chartPayload;
      renderSavedChartSelect();
      savedChartSelect.value = name;
      chartNameInput.value = name;
      updatePayloadViewer();
      setStatus(`서버 저장 실패. localStorage에 chart를 저장했습니다: ${error.message}`, "warning");
    }
  }

  function loadSelectedChart() {
    const name = savedChartSelect.value;
    const saved = savedCharts.find((item) => item.name === name);
    if (!saved || !saved.payload) {
      setStatus("불러올 chart를 선택하세요.", "warning");
      return;
    }
    payload = clone(saved.payload);
    selectedInstanceId = null;
    selectedArea = null;
    chartNameInput.value = name;
    renderAll();
    setStatus(`${name} chart를 불러왔습니다.`);
  }

  async function deleteSelectedChart() {
    const name = savedChartSelect.value;
    if (!name) {
      setStatus("삭제할 chart를 선택하세요.", "warning");
      return;
    }
    try {
      const response = await fetch(chartsApiUrl(name), { method: "DELETE" });
      const result = await response.json();
      if (!response.ok || !result.ok) throw new Error(result.error || "chart delete failed");
      savedCharts = result.charts || [];
      window.localStorage.setItem("chart_builder_saved_charts", JSON.stringify(savedCharts));
      renderSavedChartSelect();
      setStatus(`${name} chart를 삭제했습니다.`);
    } catch (error) {
      savedCharts = savedCharts.filter((item) => item.name !== name);
      window.localStorage.setItem("chart_builder_saved_charts", JSON.stringify(savedCharts));
      renderSavedChartSelect();
      setStatus(`서버 삭제 실패. localStorage에서는 삭제했습니다: ${error.message}`, "warning");
    }
  }

  async function savePrototype() {
    try {
      const response = await fetch(componentApiUrl(), {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const result = await response.json();
      if (!response.ok || !result.ok) throw new Error(result.error || "save failed");
      window.localStorage.setItem("chart_builder_prototype_payload", JSON.stringify(payload));
      setStatus("prototype payload를 서버에 저장했습니다.");
    } catch (error) {
      window.localStorage.setItem("chart_builder_prototype_payload", JSON.stringify(payload));
      setStatus(`서버 save 실패. localStorage에 저장했습니다: ${error.message}`, "warning");
    }
  }

  function buildPreview() {
    renderContainer();
    updatePayloadViewer();
    setStatus("runtime payload로 chart preview를 다시 렌더링했습니다.");
  }

  function renderAll() {
    renderPalette();
    renderContainer();
    updateProperties();
    updatePayloadViewer();
    renderSavedLayoutSelect();
    renderSavedChartSelect();
  }

  // @managed-contract contract_id=chart_builder.dataForBinding level=P1
  function dataForBinding(binding) {
    const source = binding && binding.source ? String(binding.source) : "";
    if (payload.data && Array.isArray(payload.data[source])) return payload.data[source];
    if (source === "sample.trend") return sampleData.trend;
    if (source === "sample.bars") return sampleData.bars;
    if (source === "sample.detector") return sampleData.detector;
    if (source === "sample.states") return sampleData.states;
    if (source === "sample.events") return sampleData.events;
    if (source === "sample.referenceCurrent") return sampleData.referenceCurrent;
    if (source === "sample.distribution") return sampleData.distribution;
    if (source === "sample.pValues") return sampleData.pValues;
    if (source === "sample.distances") return sampleData.distances;
    if (source === "sample.performance") return sampleData.performance;
    if (source === "sample.proportions") return sampleData.proportions;
    if (source === "sample.projection") return sampleData.projection;
    if (source === "sample.histogram") return sampleData.histogram;
    if (source === "sample.heatmap") return sampleData.heatmap;
    if (source === "sample.ranking") return sampleData.ranking;
    if (source === "sample.contributions") return sampleData.contributions;
    if (source === "sample.decision") return sampleData.decision;
    if (source === "sample.comparisonTable") return sampleData.comparisonTable;
    if (source === "sample.control") return sampleData.control;
    if (source === "sample.annotationCallout") return sampleData.annotationCallout;
    if (source === "sample.adaptiveModelStructure") return sampleData.adaptiveModelStructure;
    if (source === "sample.cumulative") return sampleData.cumulative;
    if (source === "sample.domainSpecific") return sampleData.domainSpecific;
    if (source === "sample.matrix") return sampleData.matrix;
    if (source === "sample.modelDiagnostic") return sampleData.modelDiagnostic;
    if (source === "sample.quantiles") return sampleData.quantiles;
    if (source === "sample.rawSignal") return sampleData.rawSignal;
    if (source === "sample.smallMultiples") return sampleData.smallMultiples;
    if (source === "sample.uncertainty") return sampleData.uncertainty;
    if (source === "sample.windows") return sampleData.windows;
    return [];
  }

  // @managed-contract contract_id=chart_builder.renderComponent level=P1
  function renderComponent(instance, context) {
    if (instance.componentType === "trend_line") return renderTrendLine(instance, context);
    if (instance.componentType === "bar_chart") return renderBarChart(instance, context);
    if (instance.componentType === "detector_statistic_view") return renderDetectorStatistic(instance, context);
    if (instance.componentType === "threshold_line") return renderThresholdLine(instance, context);
    if (instance.componentType === "state_timeline") return renderStateTimeline(instance, context);
    if (instance.componentType === "event_marker") return renderEventMarker(instance, context);
    if (instance.componentType === "reference_current_comparison") return renderReferenceCurrentComparison(instance, context);
    if (instance.componentType === "distribution_view") return renderDistributionView(instance, context);
    if (instance.componentType === "distribution_summary_plot") return renderDistributionSummaryPlot(instance, context);
    if (instance.componentType === "p_value_view") return renderPValueView(instance, context);
    if (instance.componentType === "distance_metric_view") return renderDistanceMetricView(instance, context);
    if (instance.componentType === "performance_metric_view") return renderPerformanceMetricView(instance, context);
    if (instance.componentType === "proportion_view") return renderProportionView(instance, context);
    if (instance.componentType === "projection_scatter") return renderProjectionScatter(instance, context);
    if (instance.componentType === "histogram_view") return renderHistogramView(instance, context);
    if (instance.componentType === "heatmap") return renderHeatmap(instance, context);
    if (instance.componentType === "ranking_view") return renderRankingView(instance, context);
    if (instance.componentType === "contribution_view") return renderContributionView(instance, context);
    if (instance.componentType === "decision_card") return renderDecisionCard(instance, context);
    if (instance.componentType === "comparison_table") return renderComparisonTable(instance, context);
    if (instance.componentType === "control_chart") return renderControlChart(instance, context);
    if (instance.componentType === "annotation_callout") return renderAnnotationCallout(instance, context);
    if (instance.componentType === "adaptive_model_structure_view") return renderAdaptiveModelStructureView(instance, context);
    if (instance.componentType === "cumulative_curve") return renderCumulativeCurve(instance, context);
    if (instance.componentType === "domain_specific_visual") return renderDomainSpecificVisual(instance, context);
    if (instance.componentType === "matrix_view") return renderMatrixView(instance, context);
    if (instance.componentType === "model_diagnostic_curve") return renderModelDiagnosticCurve(instance, context);
    if (instance.componentType === "quantile_view") return renderQuantileView(instance, context);
    if (instance.componentType === "raw_signal_trend") return renderRawSignalTrend(instance, context);
    if (instance.componentType === "small_multiples") return renderSmallMultiples(instance, context);
    if (instance.componentType === "uncertainty_band") return renderUncertaintyBand(instance, context);
    if (instance.componentType === "window_view") return renderWindowView(instance, context);
    return renderMissing(`Unknown component: ${instance.componentType}`, context);
  }

  function svgText(value) {
    return String(value).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
  }

  function clamp(min, value, max) {
    return Math.max(min, Math.min(max, value));
  }

  function pathFromPoints(points) {
    return points.map((point, index) => `${index ? "L" : "M"}${point[0].toFixed(2)},${point[1].toFixed(2)}`).join(" ");
  }

  function renderMissing(message, context) {
    const fontSize = clamp(10, Math.min(context.width, context.height) * 0.07, 14);
    return `<svg class="chart-svg" viewBox="0 0 ${context.width} ${context.height}" role="img">
      <text x="${context.width / 2}" y="${context.height / 2}" text-anchor="middle" class="chart-label" font-size="${fontSize}">${svgText(message)}</text>
    </svg>`;
  }

  function numericExtent(data, field) {
    const values = data.map((item) => Number(item[field])).filter((value) => Number.isFinite(value));
    if (!values.length) return [0, 1];
    const min = Math.min(...values);
    const max = Math.max(...values);
    if (min === max) return [min - 1, max + 1];
    return [min, max];
  }

  function renderTrendLine(instance, context) {
    const data = dataForBinding(instance.dataBinding);
    const xField = instance.config.x_field || "time";
    const yField = instance.config.y_field || "value";
    if (!data.length) return renderMissing("missing data", context);
    return renderLineChart(data, xField, yField, context, "series-line", instance.config.show_points);
  }

  function renderDetectorStatistic(instance, context) {
    const data = dataForBinding(instance.dataBinding);
    const xField = instance.config.time_field || "time";
    const yField = instance.config.statistic_field || "statistic";
    if (!data.length) return renderMissing("missing statistic", context);
    return renderLineChart(data, xField, yField, context, "stat-line", true);
  }

  function renderLineChart(data, xField, yField, context, lineClass, showPoints) {
    const { width, height, mode } = context;
    const compact = mode !== "normal";
    const margin = {
      left: compact ? 28 : 42,
      right: 16,
      top: 14,
      bottom: compact ? 24 : 34
    };
    const plotW = Math.max(10, width - margin.left - margin.right);
    const plotH = Math.max(10, height - margin.top - margin.bottom);
    const [xMin, xMax] = numericExtent(data, xField);
    const [yMinRaw, yMaxRaw] = numericExtent(data, yField);
    const yMin = Math.min(0, yMinRaw);
    const yMax = yMaxRaw * 1.08;
    const x = (value) => margin.left + ((Number(value) - xMin) / (xMax - xMin || 1)) * plotW;
    const y = (value) => margin.top + (1 - ((Number(value) - yMin) / (yMax - yMin || 1))) * plotH;
    const points = data.map((item) => [x(item[xField]), y(item[yField])]);
    const fontSize = clamp(9, Math.min(width, height) * 0.055, 13);
    const ticks = compact ? [yMin, yMax] : [yMin, (yMin + yMax) / 2, yMax];
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      ${ticks.map((tick) => `<line class="grid-line" x1="${margin.left}" x2="${width - margin.right}" y1="${y(tick)}" y2="${y(tick)}"></line>`).join("")}
      <line class="axis-line" x1="${margin.left}" x2="${width - margin.right}" y1="${height - margin.bottom}" y2="${height - margin.bottom}"></line>
      <line class="axis-line" x1="${margin.left}" x2="${margin.left}" y1="${margin.top}" y2="${height - margin.bottom}"></line>
      <path class="${lineClass}" d="${pathFromPoints(points)}"></path>
      ${showPoints && mode === "normal" ? points.map((point) => `<circle cx="${point[0]}" cy="${point[1]}" r="3" fill="#2f6f9f"></circle>`).join("") : ""}
      ${ticks.map((tick) => `<text class="chart-label" x="${margin.left - 7}" y="${y(tick) + 4}" text-anchor="end" font-size="${fontSize}">${tick.toFixed(2)}</text>`).join("")}
      <text class="chart-label" x="${margin.left}" y="${height - 7}" font-size="${fontSize}">t=${xMin}</text>
      <text class="chart-label" x="${width - margin.right}" y="${height - 7}" text-anchor="end" font-size="${fontSize}">t=${xMax}</text>
    </svg>`;
  }

  function renderBarChart(instance, context) {
    const data = dataForBinding(instance.dataBinding).slice();
    const categoryField = instance.config.category_field || "feature";
    const valueField = instance.config.value_field || "score";
    if (!data.length) return renderMissing("missing bar data", context);
    if (instance.config.sort_order === "value_desc") {
      data.sort((a, b) => Number(b[valueField]) - Number(a[valueField]));
    }
    const { width, height, mode } = context;
    const margin = { left: mode === "normal" ? 76 : 54, right: 18, top: 12, bottom: 18 };
    const plotW = Math.max(10, width - margin.left - margin.right);
    const rowH = Math.max(20, (height - margin.top - margin.bottom) / data.length);
    const maxValue = Math.max(...data.map((item) => Number(item[valueField]) || 0), 1);
    const fontSize = clamp(9, Math.min(width, height) * 0.055, 13);
    const maxItem = data.reduce((best, item) => Number(item[valueField]) > Number(best[valueField]) ? item : best, data[0]);
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      ${data.map((item, index) => {
        const value = Number(item[valueField]) || 0;
        const y = margin.top + index * rowH + 4;
        const barW = (value / maxValue) * plotW;
        const label = String(item[categoryField] || "");
        const highlight = instance.config.highlight_rule === "max_value" && item === maxItem;
        return `<text class="chart-label" x="${margin.left - 8}" y="${y + rowH * 0.55}" text-anchor="end" font-size="${fontSize}">${svgText(label.slice(0, mode === "normal" ? 12 : 8))}</text>
          <rect class="bar${highlight ? " highlight" : ""}" x="${margin.left}" y="${y}" width="${barW}" height="${Math.max(8, rowH - 8)}" rx="4"></rect>
          ${mode === "normal" ? `<text class="chart-value" x="${margin.left + barW + 5}" y="${y + rowH * 0.55}" font-size="${fontSize}">${value.toFixed(2)}</text>` : ""}`;
      }).join("")}
    </svg>`;
  }

  function renderThresholdLine(instance, context) {
    const data = sampleData.detector;
    const threshold = Number(instance.config.threshold_value || 0.68);
    const { width, height, mode } = context;
    const margin = {
      left: mode === "normal" ? 42 : 28,
      right: 16,
      top: 14,
      bottom: mode === "normal" ? 34 : 24
    };
    const [, yMaxRaw] = numericExtent(data, "statistic");
    const yMin = 0;
    const yMax = Math.max(yMaxRaw * 1.08, threshold * 1.1);
    const plotH = Math.max(10, height - margin.top - margin.bottom);
    const y = margin.top + (1 - ((threshold - yMin) / (yMax - yMin || 1))) * plotH;
    const fontSize = clamp(8, Math.min(width, height) * 0.06, 12);
    const label = `${instance.config.label || "threshold"}: ${threshold.toFixed(2)}`;
    const labelX = Math.max(margin.left + 4, width - margin.right - 4);
    const labelY = clamp(fontSize + 2, y - 7, height - 6);
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      <line class="threshold-line" x1="${margin.left}" x2="${width - margin.right}" y1="${y}" y2="${y}"></line>
      <text x="${labelX}" y="${labelY}" text-anchor="end" fill="#b84444" font-size="${fontSize}" font-weight="800">${svgText(label)}</text>
    </svg>`;
  }

  function renderStateTimeline(instance, context) {
    const data = dataForBinding(instance.dataBinding);
    if (!data.length) return renderMissing("missing state data", context);
    const { width, height, mode } = context;
    const margin = { left: 18, right: 18, top: 26, bottom: 24 };
    const plotW = Math.max(10, width - margin.left - margin.right);
    const barY = margin.top + Math.max(8, (height - margin.top - margin.bottom) * 0.25);
    const barH = Math.max(18, Math.min(44, height * 0.22));
    const segmentW = plotW / data.length;
    const fontSize = clamp(9, Math.min(width, height) * 0.055, 13);
    const stateCounts = data.reduce((acc, item) => {
      acc[item.state] = (acc[item.state] || 0) + 1;
      return acc;
    }, {});
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      ${data.map((item, index) => `<rect class="timeline-segment ${item.state}" x="${margin.left + index * segmentW}" y="${barY}" width="${Math.max(1, segmentW - 1)}" height="${barH}" rx="3"></rect>`).join("")}
      <line class="axis-line" x1="${margin.left}" x2="${width - margin.right}" y1="${barY + barH + 10}" y2="${barY + barH + 10}"></line>
      ${mode === "normal" ? `<text class="chart-label" x="${margin.left}" y="${barY - 8}" font-size="${fontSize}">normal ${stateCounts.normal || 0} / warning ${stateCounts.warning || 0} / drift ${stateCounts.drift || 0}</text>` : ""}
      <text class="chart-value" x="${width / 2}" y="${height - 8}" text-anchor="middle" font-size="${fontSize}">state timeline</text>
    </svg>`;
  }

  function renderEventMarker(instance, context) {
    const data = dataForBinding(instance.dataBinding);
    const timeField = instance.config.time_field || "time";
    const labelField = instance.config.label_field || "label";
    if (!data.length) return renderMissing("missing events", context);
    const { width, height, mode } = context;
    const margin = { left: 28, right: 18, top: 16, bottom: 24 };
    const plotW = Math.max(10, width - margin.left - margin.right);
    const [xMin, xMax] = numericExtent(data, timeField);
    const x = (value) => margin.left + ((Number(value) - xMin) / (xMax - xMin || 1)) * plotW;
    const fontSize = clamp(8, Math.min(width, height) * 0.06, 12);
    const baseline = height - margin.bottom;
    const labelLimit = mode === "normal" ? 10 : 6;
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      <line class="axis-line" x1="${margin.left}" x2="${width - margin.right}" y1="${baseline}" y2="${baseline}"></line>
      ${data.map((item, index) => {
        const px = x(item[timeField]);
        const markerTop = margin.top + (index % 2) * Math.max(12, height * 0.16);
        const label = String(item[labelField] || item.event_type || "event").slice(0, labelLimit);
        return `<line class="event-line" x1="${px}" x2="${px}" y1="${markerTop + 10}" y2="${baseline}"></line>
          <path class="event-flag" d="M${px},${markerTop} l8,4 l-8,4 z"></path>
          <text class="chart-label" x="${clamp(margin.left, px + 4, width - margin.right)}" y="${markerTop + fontSize}" font-size="${fontSize}">${svgText(label)}</text>`;
      }).join("")}
      <text class="chart-value" x="${margin.left}" y="${height - 7}" font-size="${fontSize}">${data.length} events</text>
    </svg>`;
  }

  function renderReferenceCurrentComparison(instance, context) {
    const data = dataForBinding(instance.dataBinding).slice();
    const metricField = instance.config.metric_field || "metric";
    const referenceField = instance.config.reference_field || "reference";
    const currentField = instance.config.current_field || "current";
    if (!data.length) return renderMissing("missing comparison data", context);
    const { width, height, mode } = context;
    const margin = { left: mode === "normal" ? 82 : 58, right: 24, top: 16, bottom: 22 };
    const plotW = Math.max(10, width - margin.left - margin.right);
    const rowH = Math.max(24, (height - margin.top - margin.bottom) / data.length);
    const maxValue = Math.max(...data.flatMap((item) => [Number(item[referenceField]) || 0, Number(item[currentField]) || 0]), 1);
    const fontSize = clamp(9, Math.min(width, height) * 0.052, 13);
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      ${data.map((item, index) => {
        const ref = Number(item[referenceField]) || 0;
        const cur = Number(item[currentField]) || 0;
        const y = margin.top + index * rowH;
        const refW = (ref / maxValue) * plotW;
        const curW = (cur / maxValue) * plotW;
        const metric = String(item[metricField] || "").slice(0, mode === "normal" ? 12 : 8);
        const delta = cur - ref;
        return `<text class="chart-label" x="${margin.left - 8}" y="${y + rowH * 0.62}" text-anchor="end" font-size="${fontSize}">${svgText(metric)}</text>
          <rect class="comparison-bar reference" x="${margin.left}" y="${y + 4}" width="${refW}" height="${Math.max(7, rowH * 0.28)}" rx="3"></rect>
          <rect class="comparison-bar current" x="${margin.left}" y="${y + rowH * 0.48}" width="${curW}" height="${Math.max(7, rowH * 0.28)}" rx="3"></rect>
          ${mode === "normal" ? `<text class="chart-value" x="${width - margin.right}" y="${y + rowH * 0.62}" text-anchor="end" font-size="${fontSize}">${delta >= 0 ? "+" : ""}${delta.toFixed(2)}</text>` : ""}`;
      }).join("")}
      ${mode === "normal" ? `<text class="legend-text" x="${margin.left}" y="${height - 7}" font-size="${fontSize}">reference / current</text>` : ""}
    </svg>`;
  }

  function renderDistributionView(instance, context) {
    const data = dataForBinding(instance.dataBinding);
    const valueField = instance.config.value_field || "value";
    const groupField = instance.config.group_field || "group";
    if (!data.length) return renderMissing("missing distribution", context);
    const { width, height, mode } = context;
    const margin = { left: 34, right: 18, top: 18, bottom: mode === "normal" ? 34 : 24 };
    const plotW = Math.max(10, width - margin.left - margin.right);
    const plotH = Math.max(10, height - margin.top - margin.bottom);
    const values = data.map((item) => Number(item[valueField])).filter((value) => Number.isFinite(value));
    if (!values.length) return renderMissing("missing numeric values", context);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const binCount = clamp(4, Number(instance.config.bin_count || 12), 18);
    const groups = Array.from(new Set(data.map((item) => String(item[groupField] || "value")))).slice(0, 2);
    const histograms = groups.map((group) => histogram(data.filter((item) => String(item[groupField] || "value") === group), valueField, min, max, binCount));
    const maxCount = Math.max(...histograms.flat(), 1);
    const binW = plotW / binCount;
    const fontSize = clamp(9, Math.min(width, height) * 0.052, 13);
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      <line class="axis-line" x1="${margin.left}" x2="${width - margin.right}" y1="${height - margin.bottom}" y2="${height - margin.bottom}"></line>
      <line class="axis-line" x1="${margin.left}" x2="${margin.left}" y1="${margin.top}" y2="${height - margin.bottom}"></line>
      ${histograms.map((counts, groupIndex) => counts.map((count, index) => {
        const barH = (count / maxCount) * plotH;
        const x = margin.left + index * binW + groupIndex * Math.max(2, binW * 0.08);
        const y = height - margin.bottom - barH;
        const w = Math.max(2, binW * 0.42);
        return `<rect class="distribution-bar group-${groupIndex}" x="${x}" y="${y}" width="${w}" height="${barH}" rx="2"></rect>`;
      }).join("")).join("")}
      <text class="chart-label" x="${margin.left}" y="${height - 7}" font-size="${fontSize}">${min.toFixed(2)}</text>
      <text class="chart-label" x="${width - margin.right}" y="${height - 7}" text-anchor="end" font-size="${fontSize}">${max.toFixed(2)}</text>
      ${mode === "normal" ? `<text class="legend-text" x="${margin.left}" y="${margin.top - 5}" font-size="${fontSize}">${groups.map(svgText).join(" / ")}</text>` : ""}
    </svg>`;
  }

  function histogram(data, field, min, max, binCount) {
    const counts = Array.from({ length: binCount }, () => 0);
    const span = max - min || 1;
    data.forEach((item) => {
      const value = Number(item[field]);
      if (!Number.isFinite(value)) return;
      const index = Math.min(binCount - 1, Math.max(0, Math.floor(((value - min) / span) * binCount)));
      counts[index] += 1;
    });
    return counts;
  }

  function quantile(sortedValues, p) {
    if (!sortedValues.length) return NaN;
    const index = (sortedValues.length - 1) * p;
    const lower = Math.floor(index);
    const upper = Math.ceil(index);
    if (lower === upper) return sortedValues[lower];
    return sortedValues[lower] + (sortedValues[upper] - sortedValues[lower]) * (index - lower);
  }

  function distributionSummary(values) {
    const sorted = values.filter((value) => Number.isFinite(value)).sort((a, b) => a - b);
    if (!sorted.length) return null;
    const q1 = quantile(sorted, 0.25);
    const median = quantile(sorted, 0.5);
    const q3 = quantile(sorted, 0.75);
    const iqr = q3 - q1;
    const lowerFence = q1 - 1.5 * iqr;
    const upperFence = q3 + 1.5 * iqr;
    const inliers = sorted.filter((value) => value >= lowerFence && value <= upperFence);
    return {
      min: sorted[0],
      max: sorted[sorted.length - 1],
      whiskerLow: inliers[0] ?? sorted[0],
      whiskerHigh: inliers[inliers.length - 1] ?? sorted[sorted.length - 1],
      q1,
      median,
      q3,
      outliers: sorted.filter((value) => value < lowerFence || value > upperFence),
      count: sorted.length
    };
  }

  function renderDistributionSummaryPlot(instance, context) {
    const data = dataForBinding(instance.dataBinding);
    const valueField = instance.config.value_field || "value";
    const groupField = instance.config.group_field || "group";
    if (!data.length) return renderMissing("missing distribution summary", context);
    const valid = data.filter((item) => Number.isFinite(Number(item[valueField])));
    if (!valid.length) return renderMissing("missing numeric values", context);
    const { width, height, mode } = context;
    const margin = { left: mode === "normal" ? 54 : 38, right: 22, top: 16, bottom: mode === "normal" ? 34 : 24 };
    const plotW = Math.max(10, width - margin.left - margin.right);
    const plotH = Math.max(10, height - margin.top - margin.bottom);
    const allValues = valid.map((item) => Number(item[valueField]));
    const globalMin = Math.min(...allValues);
    const globalMax = Math.max(...allValues);
    const x = (value) => margin.left + ((Number(value) - globalMin) / (globalMax - globalMin || 1)) * plotW;
    const groups = Array.from(new Set(valid.map((item) => String(item[groupField] || "value")))).slice(0, mode === "summary_only" ? 1 : 4);
    const rowH = plotH / groups.length;
    const fontSize = clamp(9, Math.min(width, height) * 0.052, 13);
    const plotType = String(instance.config.plot_type || "box_violin");
    const showOutliers = instance.config.show_outliers !== false;
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      <line class="axis-line" x1="${margin.left}" x2="${width - margin.right}" y1="${height - margin.bottom}" y2="${height - margin.bottom}"></line>
      ${groups.map((group, index) => {
        const values = valid.filter((item) => String(item[groupField] || "value") === group).map((item) => Number(item[valueField]));
        const summary = distributionSummary(values);
        if (!summary) return "";
        const centerY = margin.top + rowH * (index + 0.5);
        const boxH = Math.max(12, Math.min(28, rowH * 0.42));
        const violinH = Math.max(boxH + 4, Math.min(36, rowH * 0.58));
        const density = histogram(values.map((value) => ({ value })), "value", globalMin, globalMax, 12);
        const maxDensity = Math.max(...density, 1);
        const binW = plotW / density.length;
        const top = density.map((count, binIndex) => {
          const px = margin.left + binIndex * binW + binW / 2;
          const py = centerY - (count / maxDensity) * violinH * 0.5;
          return [px, py];
        });
        const bottom = density.slice().reverse().map((count, reverseIndex) => {
          const binIndex = density.length - 1 - reverseIndex;
          const px = margin.left + binIndex * binW + binW / 2;
          const py = centerY + (count / maxDensity) * violinH * 0.5;
          return [px, py];
        });
        const violinPath = top.length ? `${pathFromPoints(top)} ${bottom.map((point) => `L${point[0].toFixed(2)},${point[1].toFixed(2)}`).join(" ")} Z` : "";
        const label = group.slice(0, mode === "normal" ? 14 : 8);
        return `<text class="chart-label" x="${margin.left - 8}" y="${centerY + fontSize * 0.35}" text-anchor="end" font-size="${fontSize}">${svgText(label)}</text>
          ${plotType.includes("violin") ? `<path class="distribution-summary-violin group-${index % 4}" d="${violinPath}"></path>` : ""}
          <line class="distribution-summary-whisker" x1="${x(summary.whiskerLow)}" x2="${x(summary.whiskerHigh)}" y1="${centerY}" y2="${centerY}"></line>
          <line class="distribution-summary-whisker" x1="${x(summary.whiskerLow)}" x2="${x(summary.whiskerLow)}" y1="${centerY - boxH * 0.34}" y2="${centerY + boxH * 0.34}"></line>
          <line class="distribution-summary-whisker" x1="${x(summary.whiskerHigh)}" x2="${x(summary.whiskerHigh)}" y1="${centerY - boxH * 0.34}" y2="${centerY + boxH * 0.34}"></line>
          ${plotType.includes("box") ? `<rect class="distribution-summary-box group-${index % 4}" x="${x(summary.q1)}" y="${centerY - boxH / 2}" width="${Math.max(2, x(summary.q3) - x(summary.q1))}" height="${boxH}" rx="4"></rect>` : ""}
          <line class="distribution-summary-median" x1="${x(summary.median)}" x2="${x(summary.median)}" y1="${centerY - boxH * 0.62}" y2="${centerY + boxH * 0.62}"></line>
          ${showOutliers ? summary.outliers.map((value) => `<circle class="distribution-summary-outlier" cx="${x(value)}" cy="${centerY}" r="2.5"></circle>`).join("") : ""}
          ${mode === "normal" ? `<text class="chart-value" x="${width - margin.right}" y="${centerY + fontSize * 0.35}" text-anchor="end" font-size="${fontSize}">n=${summary.count} med=${summary.median.toFixed(2)}</text>` : ""}`;
      }).join("")}
      <text class="chart-label" x="${margin.left}" y="${height - 7}" font-size="${fontSize}">${globalMin.toFixed(2)}</text>
      <text class="chart-label" x="${width - margin.right}" y="${height - 7}" text-anchor="end" font-size="${fontSize}">${globalMax.toFixed(2)}</text>
    </svg>`;
  }

  function renderPValueView(instance, context) {
    const data = dataForBinding(instance.dataBinding).slice();
    const pField = instance.config.p_value_field || "p_value";
    const labelField = instance.config.label_field || "feature";
    const alpha = Number(instance.config.alpha || 0.05);
    const transform = instance.config.transform || "none";
    if (!data.length) return renderMissing("missing p-values", context);
    const { width, height, mode } = context;
    const margin = { left: mode === "normal" ? 76 : 54, right: 18, top: 16, bottom: 24 };
    const plotW = Math.max(10, width - margin.left - margin.right);
    const rowH = Math.max(22, (height - margin.top - margin.bottom) / data.length);
    const valueOf = (item) => {
      const p = Math.max(1e-12, Number(item[pField]) || 1);
      return transform === "-log10" ? -Math.log10(p) : p;
    };
    const alphaValue = transform === "-log10" ? -Math.log10(Math.max(1e-12, alpha)) : alpha;
    const maxValue = Math.max(...data.map(valueOf), alphaValue, transform === "-log10" ? 1 : 0.25);
    const fontSize = clamp(9, Math.min(width, height) * 0.052, 13);
    const thresholdX = margin.left + (alphaValue / maxValue) * plotW;
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      <line class="pvalue-alpha-line" x1="${thresholdX}" x2="${thresholdX}" y1="${margin.top}" y2="${height - margin.bottom}"></line>
      ${data.map((item, index) => {
        const p = Number(item[pField]);
        const value = valueOf(item);
        const barW = (value / maxValue) * plotW;
        const y = margin.top + index * rowH + 4;
        const significant = Number.isFinite(p) && p <= alpha;
        const label = String(item[labelField] || "").slice(0, mode === "normal" ? 12 : 8);
        return `<text class="chart-label" x="${margin.left - 8}" y="${y + rowH * 0.55}" text-anchor="end" font-size="${fontSize}">${svgText(label)}</text>
          <rect class="pvalue-bar${significant ? " significant" : ""}" x="${margin.left}" y="${y}" width="${barW}" height="${Math.max(8, rowH - 8)}" rx="4"></rect>
          ${mode === "normal" ? `<text class="chart-value" x="${margin.left + barW + 5}" y="${y + rowH * 0.55}" font-size="${fontSize}">${Number.isFinite(p) ? p.toFixed(3) : "NA"}</text>` : ""}`;
      }).join("")}
      <text class="legend-text" x="${clamp(margin.left, thresholdX + 4, width - margin.right)}" y="${height - 7}" font-size="${fontSize}">alpha ${alpha.toFixed(2)}</text>
    </svg>`;
  }

  function renderDistanceMetricView(instance, context) {
    const data = dataForBinding(instance.dataBinding).slice();
    const distanceField = instance.config.distance_field || "distance";
    const groupField = instance.config.group_field || "feature";
    const baseline = Number(instance.config.baseline_distance || 0);
    if (!data.length) return renderMissing("missing distance data", context);
    if (instance.config.sort_order === "value_desc") {
      data.sort((a, b) => Number(b[distanceField]) - Number(a[distanceField]));
    }
    const { width, height, mode } = context;
    const margin = { left: mode === "normal" ? 78 : 56, right: 22, top: 16, bottom: 24 };
    const plotW = Math.max(10, width - margin.left - margin.right);
    const rowH = Math.max(22, (height - margin.top - margin.bottom) / data.length);
    const maxValue = Math.max(...data.map((item) => Number(item[distanceField]) || 0), baseline, 1e-6) * 1.08;
    const baselineX = margin.left + (baseline / maxValue) * plotW;
    const fontSize = clamp(9, Math.min(width, height) * 0.052, 13);
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      ${baseline > 0 ? `<line class="distance-baseline-line" x1="${baselineX}" x2="${baselineX}" y1="${margin.top}" y2="${height - margin.bottom}"></line>` : ""}
      ${data.map((item, index) => {
        const value = Number(item[distanceField]) || 0;
        const barW = (value / maxValue) * plotW;
        const y = margin.top + index * rowH + 4;
        const label = String(item[groupField] || "").slice(0, mode === "normal" ? 12 : 8);
        const exceeds = baseline > 0 && value >= baseline;
        return `<text class="chart-label" x="${margin.left - 8}" y="${y + rowH * 0.55}" text-anchor="end" font-size="${fontSize}">${svgText(label)}</text>
          <rect class="distance-bar${exceeds ? " exceeds" : ""}" x="${margin.left}" y="${y}" width="${barW}" height="${Math.max(8, rowH - 8)}" rx="4"></rect>
          ${mode === "normal" ? `<text class="chart-value" x="${margin.left + barW + 5}" y="${y + rowH * 0.55}" font-size="${fontSize}">${value.toFixed(2)}</text>` : ""}`;
      }).join("")}
      ${baseline > 0 ? `<text class="legend-text" x="${clamp(margin.left, baselineX + 4, width - margin.right)}" y="${height - 7}" font-size="${fontSize}">baseline ${baseline.toFixed(2)}</text>` : ""}
    </svg>`;
  }

  function renderPerformanceMetricView(instance, context) {
    const data = dataForBinding(instance.dataBinding).slice();
    const metricField = instance.config.metric_field || "metric";
    const valueField = instance.config.value_field || "value";
    const baselineField = instance.config.baseline_field || "baseline";
    const targetField = instance.config.target_field || "target";
    const directionField = instance.config.direction_field || "direction";
    if (!data.length) return renderMissing("missing performance data", context);
    const { width, height, mode } = context;
    const margin = { left: mode === "normal" ? 76 : 54, right: 28, top: 16, bottom: 24 };
    const plotW = Math.max(10, width - margin.left - margin.right);
    const rowH = Math.max(28, (height - margin.top - margin.bottom) / data.length);
    const maxValue = Math.max(...data.flatMap((item) => [
      Number(item[valueField]) || 0,
      Number(item[baselineField]) || 0,
      Number(item[targetField]) || 0
    ]), 1);
    const fontSize = clamp(9, Math.min(width, height) * 0.052, 13);
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      ${data.map((item, index) => {
        const value = Number(item[valueField]) || 0;
        const baseline = Number(item[baselineField]);
        const target = Number(item[targetField]);
        const direction = String(item[directionField] || "higher_is_better");
        const good = direction === "lower_is_better"
          ? (Number.isFinite(target) ? value <= target : value <= baseline)
          : (Number.isFinite(target) ? value >= target : value >= baseline);
        const y = margin.top + index * rowH;
        const barW = (value / maxValue) * plotW;
        const baselineX = margin.left + ((Number.isFinite(baseline) ? baseline : 0) / maxValue) * plotW;
        const targetX = margin.left + ((Number.isFinite(target) ? target : 0) / maxValue) * plotW;
        const metric = String(item[metricField] || "").slice(0, mode === "normal" ? 12 : 8);
        return `<text class="chart-label" x="${margin.left - 8}" y="${y + rowH * 0.58}" text-anchor="end" font-size="${fontSize}">${svgText(metric)}</text>
          <line class="metric-track" x1="${margin.left}" x2="${width - margin.right}" y1="${y + rowH * 0.5}" y2="${y + rowH * 0.5}"></line>
          <rect class="performance-bar${good ? " good" : " warning"}" x="${margin.left}" y="${y + rowH * 0.28}" width="${barW}" height="${Math.max(8, rowH * 0.34)}" rx="4"></rect>
          ${Number.isFinite(baseline) ? `<line class="performance-marker baseline" x1="${baselineX}" x2="${baselineX}" y1="${y + 4}" y2="${y + rowH - 4}"></line>` : ""}
          ${Number.isFinite(target) ? `<line class="performance-marker target" x1="${targetX}" x2="${targetX}" y1="${y + 4}" y2="${y + rowH - 4}"></line>` : ""}
          ${mode === "normal" ? `<text class="chart-value" x="${width - margin.right}" y="${y + rowH * 0.58}" text-anchor="end" font-size="${fontSize}">${value.toFixed(2)}</text>` : ""}`;
      }).join("")}
      ${mode === "normal" ? `<text class="legend-text" x="${margin.left}" y="${height - 7}" font-size="${fontSize}">baseline | target</text>` : ""}
    </svg>`;
  }

  function renderProportionView(instance, context) {
    const data = dataForBinding(instance.dataBinding);
    const categoryField = instance.config.category_field || "category";
    const proportionField = instance.config.proportion_field || "proportion";
    const seriesField = instance.config.series_field || "series";
    if (!data.length) return renderMissing("missing proportion data", context);
    const { width, height, mode } = context;
    const margin = { left: mode === "normal" ? 76 : 54, right: 18, top: 18, bottom: mode === "normal" ? 42 : 24 };
    const plotW = Math.max(10, width - margin.left - margin.right);
    const rowH = Math.max(24, (height - margin.top - margin.bottom) / 2);
    const series = Array.from(new Set(data.map((item) => String(item[seriesField] || "series")))).slice(0, 2);
    const categories = Array.from(new Set(data.map((item) => String(item[categoryField] || "")))).filter(Boolean);
    const bySeries = new Map(series.map((name) => [name, data.filter((item) => String(item[seriesField] || "series") === name)]));
    const fontSize = clamp(9, Math.min(width, height) * 0.052, 13);
    const valueFor = (seriesName, category) => {
      const item = (bySeries.get(seriesName) || []).find((entry) => String(entry[categoryField]) === category);
      return item ? Number(item[proportionField]) || 0 : 0;
    };
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      ${series.map((seriesName, rowIndex) => {
        const y = margin.top + rowIndex * rowH + 6;
        let x = margin.left;
        const total = Math.max(1e-6, (bySeries.get(seriesName) || []).reduce((sum, item) => sum + (Number(item[proportionField]) || 0), 0));
        const segments = categories.map((category, index) => {
          const value = valueFor(seriesName, category);
          const w = (value / total) * plotW;
          const segment = `<rect class="proportion-segment cat-${index % 6}" x="${x}" y="${y}" width="${w}" height="${Math.max(14, rowH * 0.42)}" rx="${index === 0 ? 4 : 0}"></rect>`;
          x += w;
          return segment;
        }).join("");
        return `<text class="chart-label" x="${margin.left - 8}" y="${y + rowH * 0.28}" text-anchor="end" font-size="${fontSize}">${svgText(seriesName)}</text>${segments}`;
      }).join("")}
      ${mode === "normal" ? categories.map((category, index) => {
        const ref = valueFor(series[0], category);
        const cur = valueFor(series[1], category);
        const delta = cur - ref;
        const x = margin.left + (index / Math.max(1, categories.length)) * plotW;
        return `<circle class="proportion-dot cat-${index % 6}" cx="${x + 5}" cy="${height - 16}" r="4"></circle>
          <text class="legend-text" x="${x + 12}" y="${height - 12}" font-size="${fontSize}">${svgText(category)} ${delta >= 0 ? "+" : ""}${Math.round(delta * 100)}pp</text>`;
      }).join("") : ""}
    </svg>`;
  }

  function renderProjectionScatter(instance, context) {
    const data = dataForBinding(instance.dataBinding).slice(0, Number(instance.config.sample_limit || 40));
    const xField = instance.config.x_field || "x";
    const yField = instance.config.y_field || "y";
    const groupField = instance.config.group_field || "group";
    if (!data.length) return renderMissing("missing projection data", context);
    const { width, height, mode } = context;
    const margin = { left: mode === "normal" ? 34 : 22, right: 18, top: 18, bottom: mode === "normal" ? 32 : 22 };
    const plotW = Math.max(10, width - margin.left - margin.right);
    const plotH = Math.max(10, height - margin.top - margin.bottom);
    const [xMinRaw, xMaxRaw] = numericExtent(data, xField);
    const [yMinRaw, yMaxRaw] = numericExtent(data, yField);
    const xPad = Math.max(0.1, (xMaxRaw - xMinRaw) * 0.08);
    const yPad = Math.max(0.1, (yMaxRaw - yMinRaw) * 0.08);
    const xMin = xMinRaw - xPad;
    const xMax = xMaxRaw + xPad;
    const yMin = yMinRaw - yPad;
    const yMax = yMaxRaw + yPad;
    const x = (value) => margin.left + ((Number(value) - xMin) / (xMax - xMin || 1)) * plotW;
    const y = (value) => margin.top + (1 - ((Number(value) - yMin) / (yMax - yMin || 1))) * plotH;
    const groups = Array.from(new Set(data.map((item) => String(item[groupField] || "sample")))).slice(0, 4);
    const centroids = groups.map((group, index) => {
      const rows = data.filter((item) => String(item[groupField] || "sample") === group);
      const cx = rows.reduce((sum, item) => sum + Number(item[xField] || 0), 0) / Math.max(1, rows.length);
      const cy = rows.reduce((sum, item) => sum + Number(item[yField] || 0), 0) / Math.max(1, rows.length);
      return { group, index, x: cx, y: cy };
    });
    const fontSize = clamp(9, Math.min(width, height) * 0.052, 13);
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      <line class="grid-line" x1="${margin.left}" x2="${width - margin.right}" y1="${y(0)}" y2="${y(0)}"></line>
      <line class="grid-line" x1="${x(0)}" x2="${x(0)}" y1="${margin.top}" y2="${height - margin.bottom}"></line>
      <rect class="scatter-frame" x="${margin.left}" y="${margin.top}" width="${plotW}" height="${plotH}" rx="3"></rect>
      ${data.map((item) => {
        const group = String(item[groupField] || "sample");
        const groupIndex = Math.max(0, groups.indexOf(group));
        return `<circle class="scatter-point group-${groupIndex}" cx="${x(item[xField])}" cy="${y(item[yField])}" r="${mode === "normal" ? 4 : 3}"></circle>`;
      }).join("")}
      ${instance.config.centroid !== false && centroids.length >= 2 ? `<line class="centroid-shift-line" x1="${x(centroids[0].x)}" y1="${y(centroids[0].y)}" x2="${x(centroids[1].x)}" y2="${y(centroids[1].y)}"></line>` : ""}
      ${instance.config.centroid !== false ? centroids.map((centroid) => `<circle class="centroid-point group-${centroid.index}" cx="${x(centroid.x)}" cy="${y(centroid.y)}" r="6"></circle>`).join("") : ""}
      ${mode === "normal" ? groups.map((group, index) => `<circle class="scatter-point group-${index}" cx="${margin.left + index * 82}" cy="${height - 10}" r="4"></circle><text class="legend-text" x="${margin.left + index * 82 + 8}" y="${height - 7}" font-size="${fontSize}">${svgText(group)}</text>`).join("") : ""}
    </svg>`;
  }

  function renderHistogramView(instance, context) {
    const data = dataForBinding(instance.dataBinding);
    const binField = instance.config.bin_field || "bin";
    const countField = instance.config.count_field || "count";
    const seriesField = instance.config.series_field || "series";
    if (!data.length) return renderMissing("missing histogram data", context);
    const { width, height, mode } = context;
    const margin = { left: 36, right: 18, top: 18, bottom: mode === "normal" ? 42 : 26 };
    const plotW = Math.max(10, width - margin.left - margin.right);
    const plotH = Math.max(10, height - margin.top - margin.bottom);
    const bins = Array.from(new Set(data.map((item) => String(item[binField] || "")))).filter(Boolean);
    const series = Array.from(new Set(data.map((item) => String(item[seriesField] || "series")))).slice(0, 2);
    const maxCount = Math.max(...data.map((item) => Number(item[countField]) || 0), 1);
    const binW = plotW / Math.max(1, bins.length);
    const barW = Math.max(3, binW / Math.max(3, series.length + 1));
    const fontSize = clamp(9, Math.min(width, height) * 0.052, 13);
    const valueFor = (seriesName, bin) => {
      const item = data.find((entry) => String(entry[seriesField] || "series") === seriesName && String(entry[binField] || "") === bin);
      return item ? Number(item[countField]) || 0 : 0;
    };
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      <line class="axis-line" x1="${margin.left}" x2="${width - margin.right}" y1="${height - margin.bottom}" y2="${height - margin.bottom}"></line>
      <line class="axis-line" x1="${margin.left}" x2="${margin.left}" y1="${margin.top}" y2="${height - margin.bottom}"></line>
      ${bins.map((bin, binIndex) => {
        const x0 = margin.left + binIndex * binW;
        const bars = series.map((seriesName, seriesIndex) => {
          const count = valueFor(seriesName, bin);
          const barH = (count / maxCount) * plotH;
          const x = x0 + seriesIndex * barW + Math.max(2, binW * 0.15);
          const y = height - margin.bottom - barH;
          return `<rect class="histogram-bar series-${seriesIndex}" x="${x}" y="${y}" width="${barW}" height="${barH}" rx="2"></rect>`;
        }).join("");
        const label = mode === "normal" || binIndex % 2 === 0 ? `<text class="chart-label" x="${x0 + binW / 2}" y="${height - 8}" text-anchor="middle" font-size="${fontSize}">${svgText(bin)}</text>` : "";
        return `${bars}${label}`;
      }).join("")}
      ${mode === "normal" ? series.map((seriesName, index) => `<rect class="histogram-bar series-${index}" x="${margin.left + index * 92}" y="${margin.top - 11}" width="10" height="8" rx="2"></rect><text class="legend-text" x="${margin.left + index * 92 + 14}" y="${margin.top - 4}" font-size="${fontSize}">${svgText(seriesName)}</text>`).join("") : ""}
    </svg>`;
  }

  function renderHeatmap(instance, context) {
    const data = dataForBinding(instance.dataBinding);
    const xField = instance.config.x_field || "bucket";
    const yField = instance.config.y_field || "feature";
    const valueField = instance.config.value_field || "score";
    const threshold = Number(instance.config.highlight_threshold || 0);
    if (!data.length) return renderMissing("missing heatmap data", context);
    const { width, height, mode } = context;
    const margin = { left: mode === "normal" ? 72 : 52, right: 18, top: 22, bottom: mode === "normal" ? 34 : 22 };
    const plotW = Math.max(10, width - margin.left - margin.right);
    const plotH = Math.max(10, height - margin.top - margin.bottom);
    const columns = Array.from(new Set(data.map((item) => String(item[xField] || "")))).filter(Boolean);
    const rows = Array.from(new Set(data.map((item) => String(item[yField] || "")))).filter(Boolean);
    const cellW = plotW / Math.max(1, columns.length);
    const cellH = plotH / Math.max(1, rows.length);
    const maxValue = Math.max(...data.map((item) => Number(item[valueField]) || 0), threshold, 1);
    const fontSize = clamp(9, Math.min(width, height) * 0.052, 13);
    const valueFor = (row, column) => {
      const item = data.find((entry) => String(entry[yField] || "") === row && String(entry[xField] || "") === column);
      return item ? Number(item[valueField]) || 0 : 0;
    };
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      ${rows.map((row, rowIndex) => `<text class="chart-label" x="${margin.left - 8}" y="${margin.top + rowIndex * cellH + cellH * 0.58}" text-anchor="end" font-size="${fontSize}">${svgText(row.slice(0, mode === "normal" ? 12 : 8))}</text>`).join("")}
      ${columns.map((column, colIndex) => mode === "normal" ? `<text class="chart-label" x="${margin.left + colIndex * cellW + cellW / 2}" y="${height - 8}" text-anchor="middle" font-size="${fontSize}">${svgText(column)}</text>` : "").join("")}
      ${rows.map((row, rowIndex) => columns.map((column, colIndex) => {
        const value = valueFor(row, column);
        const intensity = clamp(0.08, value / maxValue, 1);
        const x = margin.left + colIndex * cellW;
        const y = margin.top + rowIndex * cellH;
        const highlight = threshold > 0 && value >= threshold;
        return `<rect class="heatmap-cell${highlight ? " highlight" : ""}" x="${x}" y="${y}" width="${Math.max(1, cellW - 2)}" height="${Math.max(1, cellH - 2)}" rx="3" fill="rgba(47, 111, 159, ${intensity.toFixed(2)})"></rect>
          ${mode === "normal" && cellW > 42 && cellH > 24 ? `<text class="heatmap-value" x="${x + cellW / 2}" y="${y + cellH * 0.58}" text-anchor="middle" font-size="${fontSize}">${value.toFixed(2)}</text>` : ""}`;
      }).join("")).join("")}
      ${mode === "normal" ? `<text class="legend-text" x="${margin.left}" y="${margin.top - 7}" font-size="${fontSize}">threshold ${threshold.toFixed(2)}</text>` : ""}
    </svg>`;
  }

  function renderRankingView(instance, context) {
    const data = dataForBinding(instance.dataBinding).slice();
    const itemField = instance.config.item_field || "item";
    const scoreField = instance.config.score_field || "score";
    const topN = Number(instance.config.top_n || 6);
    if (!data.length) return renderMissing("missing ranking data", context);
    data.sort((a, b) => Number(b[scoreField]) - Number(a[scoreField]));
    const rows = data.slice(0, Math.max(1, topN));
    const { width, height, mode } = context;
    const margin = { left: mode === "normal" ? 92 : 66, right: 22, top: 16, bottom: 22 };
    const plotW = Math.max(10, width - margin.left - margin.right);
    const rowH = Math.max(22, (height - margin.top - margin.bottom) / rows.length);
    const maxScore = Math.max(...rows.map((item) => Number(item[scoreField]) || 0), 1);
    const fontSize = clamp(9, Math.min(width, height) * 0.052, 13);
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      ${rows.map((item, index) => {
        const score = Number(item[scoreField]) || 0;
        const y = margin.top + index * rowH + 4;
        const barW = (score / maxScore) * plotW;
        const label = String(item[itemField] || "").slice(0, mode === "normal" ? 14 : 9);
        return `<text class="ranking-rank" x="${margin.left - 62}" y="${y + rowH * 0.55}" font-size="${fontSize}">#${index + 1}</text>
          <text class="chart-label" x="${margin.left - 8}" y="${y + rowH * 0.55}" text-anchor="end" font-size="${fontSize}">${svgText(label)}</text>
          <rect class="ranking-bar${index === 0 ? " top" : ""}" x="${margin.left}" y="${y}" width="${barW}" height="${Math.max(8, rowH - 8)}" rx="4"></rect>
          ${mode === "normal" ? `<text class="chart-value" x="${margin.left + barW + 5}" y="${y + rowH * 0.55}" font-size="${fontSize}">${score.toFixed(2)}</text>` : ""}`;
      }).join("")}
    </svg>`;
  }

  function renderContributionView(instance, context) {
    const data = dataForBinding(instance.dataBinding).slice();
    const contributorField = instance.config.contributor_field || "feature";
    const contributionField = instance.config.contribution_field || "contribution";
    const topN = Number(instance.config.top_n || 6);
    const signed = instance.config.signed !== false;
    if (!data.length) return renderMissing("missing contribution data", context);
    data.sort((a, b) => Math.abs(Number(b[contributionField]) || 0) - Math.abs(Number(a[contributionField]) || 0));
    const rows = data.slice(0, Math.max(1, topN));
    const { width, height, mode } = context;
    const margin = { left: mode === "normal" ? 82 : 60, right: 24, top: 16, bottom: 22 };
    const plotW = Math.max(10, width - margin.left - margin.right);
    const rowH = Math.max(22, (height - margin.top - margin.bottom) / rows.length);
    const maxAbs = Math.max(...rows.map((item) => Math.abs(Number(item[contributionField]) || 0)), 1e-6);
    const zeroX = signed ? margin.left + plotW / 2 : margin.left;
    const halfW = signed ? plotW / 2 : plotW;
    const fontSize = clamp(9, Math.min(width, height) * 0.052, 13);
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      ${signed ? `<line class="contribution-zero-line" x1="${zeroX}" x2="${zeroX}" y1="${margin.top}" y2="${height - margin.bottom}"></line>` : ""}
      ${rows.map((item, index) => {
        const value = Number(item[contributionField]) || 0;
        const barW = Math.abs(value) / maxAbs * halfW;
        const x = signed ? (value >= 0 ? zeroX : zeroX - barW) : margin.left;
        const y = margin.top + index * rowH + 4;
        const label = String(item[contributorField] || "").slice(0, mode === "normal" ? 12 : 8);
        return `<text class="chart-label" x="${margin.left - 8}" y="${y + rowH * 0.55}" text-anchor="end" font-size="${fontSize}">${svgText(label)}</text>
          <rect class="contribution-bar${value >= 0 ? " positive" : " negative"}" x="${x}" y="${y}" width="${barW}" height="${Math.max(8, rowH - 8)}" rx="4"></rect>
          ${mode === "normal" ? `<text class="chart-value" x="${value >= 0 ? x + barW + 5 : x - 5}" y="${y + rowH * 0.55}" text-anchor="${value >= 0 ? "start" : "end"}" font-size="${fontSize}">${value >= 0 ? "+" : ""}${value.toFixed(2)}</text>` : ""}`;
      }).join("")}
    </svg>`;
  }

  function renderDecisionCard(instance, context) {
    const data = dataForBinding(instance.dataBinding);
    if (!data.length) return renderMissing("missing decision", context);
    const item = data[0];
    const decisionField = instance.config.decision_field || "decision";
    const metricField = instance.config.primary_metric_field || "metric_value";
    const thresholdField = instance.config.threshold_field || "threshold";
    const labelField = instance.config.label_field || "label";
    const decision = String(item[decisionField] || "unknown").toLowerCase();
    const metric = Number(item[metricField]);
    const threshold = Number(item[thresholdField]);
    const label = String(item[labelField] || "decision summary");
    const { width, height, mode } = context;
    const statusClass = decision.includes("drift") || decision.includes("reject")
      ? "drift"
      : decision.includes("warn")
        ? "warning"
        : "normal";
    const titleSize = clamp(13, Math.min(width, height) * 0.11, 20);
    const bodySize = clamp(9, Math.min(width, height) * 0.065, 13);
    const statusText = decision.toUpperCase();
    const metricText = Number.isFinite(metric) ? metric.toFixed(2) : "NA";
    const thresholdText = Number.isFinite(threshold) ? threshold.toFixed(2) : "NA";
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      <rect class="decision-card-bg ${statusClass}" x="1" y="1" width="${width - 2}" height="${height - 2}" rx="6"></rect>
      <rect class="decision-card-band ${statusClass}" x="1" y="1" width="${Math.max(8, width * 0.04)}" height="${height - 2}" rx="5"></rect>
      <text class="decision-status ${statusClass}" x="${width * 0.09}" y="${Math.max(24, height * 0.25)}" font-size="${titleSize}">${svgText(statusText)}</text>
      <text class="decision-metric" x="${width * 0.09}" y="${Math.max(48, height * 0.52)}" font-size="${bodySize}">metric ${metricText} / threshold ${thresholdText}</text>
      ${mode === "normal" ? `<text class="decision-label" x="${width * 0.09}" y="${Math.max(70, height * 0.74)}" font-size="${bodySize}">${svgText(label.slice(0, 42))}</text>` : ""}
    </svg>`;
  }

  function renderComparisonTable(instance, context) {
    const data = dataForBinding(instance.dataBinding);
    const rowField = instance.config.row_field || "metric";
    const referenceField = instance.config.reference_field || "reference";
    const currentField = instance.config.current_field || "current";
    if (!data.length) return renderMissing("missing table data", context);
    const { width, height, mode } = context;
    const margin = { left: 12, right: 12, top: 14, bottom: 12 };
    const tableW = Math.max(10, width - margin.left - margin.right);
    const headerH = mode === "normal" ? 28 : 20;
    const rowH = Math.max(24, (height - margin.top - margin.bottom - headerH) / data.length);
    const metricW = mode === "normal" ? tableW * 0.34 : tableW * 0.44;
    const valueW = (tableW - metricW) / (mode === "normal" ? 3 : 1);
    const fontSize = clamp(9, Math.min(width, height) * 0.052, 13);
    const fmt = (value) => Number.isFinite(Number(value)) ? Number(value).toFixed(2) : "NA";
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      <rect class="comparison-table-header" x="${margin.left}" y="${margin.top}" width="${tableW}" height="${headerH}" rx="4"></rect>
      <text class="comparison-table-head-text" x="${margin.left + 8}" y="${margin.top + headerH * 0.65}" font-size="${fontSize}">metric</text>
      ${mode === "normal" ? `<text class="comparison-table-head-text" x="${margin.left + metricW + valueW * 0.5}" y="${margin.top + headerH * 0.65}" text-anchor="middle" font-size="${fontSize}">ref</text>
        <text class="comparison-table-head-text" x="${margin.left + metricW + valueW * 1.5}" y="${margin.top + headerH * 0.65}" text-anchor="middle" font-size="${fontSize}">cur</text>
        <text class="comparison-table-head-text" x="${margin.left + metricW + valueW * 2.5}" y="${margin.top + headerH * 0.65}" text-anchor="middle" font-size="${fontSize}">delta</text>` : `<text class="comparison-table-head-text" x="${width - margin.right - 8}" y="${margin.top + headerH * 0.65}" text-anchor="end" font-size="${fontSize}">delta</text>`}
      ${data.map((item, index) => {
        const y = margin.top + headerH + index * rowH;
        const ref = Number(item[referenceField]);
        const cur = Number(item[currentField]);
        const delta = Number.isFinite(ref) && Number.isFinite(cur) ? cur - ref : NaN;
        const rowClass = index % 2 === 0 ? "even" : "odd";
        return `<rect class="comparison-table-row ${rowClass}" x="${margin.left}" y="${y}" width="${tableW}" height="${rowH}"></rect>
          <text class="chart-label" x="${margin.left + 8}" y="${y + rowH * 0.62}" font-size="${fontSize}">${svgText(String(item[rowField] || "").slice(0, 14))}</text>
          ${mode === "normal" ? `<text class="chart-value" x="${margin.left + metricW + valueW * 0.5}" y="${y + rowH * 0.62}" text-anchor="middle" font-size="${fontSize}">${fmt(ref)}</text>
            <text class="chart-value" x="${margin.left + metricW + valueW * 1.5}" y="${y + rowH * 0.62}" text-anchor="middle" font-size="${fontSize}">${fmt(cur)}</text>
            <text class="comparison-delta ${delta >= 0 ? "positive" : "negative"}" x="${margin.left + metricW + valueW * 2.5}" y="${y + rowH * 0.62}" text-anchor="middle" font-size="${fontSize}">${Number.isFinite(delta) ? `${delta >= 0 ? "+" : ""}${delta.toFixed(2)}` : "NA"}</text>` : `<text class="comparison-delta ${delta >= 0 ? "positive" : "negative"}" x="${width - margin.right - 8}" y="${y + rowH * 0.62}" text-anchor="end" font-size="${fontSize}">${Number.isFinite(delta) ? `${delta >= 0 ? "+" : ""}${delta.toFixed(2)}` : "NA"}</text>`}`;
      }).join("")}
    </svg>`;
  }

  function renderControlChart(instance, context) {
    const data = dataForBinding(instance.dataBinding);
    const timeField = instance.config.time_field || "time";
    const statisticField = instance.config.statistic_field || "statistic";
    const center = Number(instance.config.center_value ?? 0.5);
    const ucl = Number(instance.config.ucl ?? 0.78);
    const lcl = Number(instance.config.lcl ?? 0.22);
    if (!data.length) return renderMissing("missing control data", context);
    const { width, height, mode } = context;
    const margin = { left: mode === "normal" ? 42 : 30, right: 18, top: 16, bottom: mode === "normal" ? 34 : 24 };
    const plotW = Math.max(10, width - margin.left - margin.right);
    const plotH = Math.max(10, height - margin.top - margin.bottom);
    const [xMin, xMax] = numericExtent(data, timeField);
    const [yMinRaw, yMaxRaw] = numericExtent(data, statisticField);
    const yMin = Math.min(yMinRaw, lcl, center) - 0.05;
    const yMax = Math.max(yMaxRaw, ucl, center) + 0.05;
    const x = (value) => margin.left + ((Number(value) - xMin) / (xMax - xMin || 1)) * plotW;
    const y = (value) => margin.top + (1 - ((Number(value) - yMin) / (yMax - yMin || 1))) * plotH;
    const points = data.map((item) => [x(item[timeField]), y(item[statisticField]), Number(item[statisticField])]);
    const fontSize = clamp(9, Math.min(width, height) * 0.052, 13);
    const line = (value, cls, label) => `<line class="${cls}" x1="${margin.left}" x2="${width - margin.right}" y1="${y(value)}" y2="${y(value)}"></line>${mode === "normal" ? `<text class="legend-text" x="${width - margin.right}" y="${y(value) - 4}" text-anchor="end" font-size="${fontSize}">${label}</text>` : ""}`;
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      ${line(ucl, "control-limit-line", "UCL")}
      ${line(center, "control-center-line", "CL")}
      ${line(lcl, "control-limit-line", "LCL")}
      <path class="control-stat-line" d="${pathFromPoints(points)}"></path>
      ${instance.config.show_points !== false ? points.map((point) => {
        const alarm = point[2] > ucl || point[2] < lcl;
        return `<circle class="control-point${alarm ? " alarm" : ""}" cx="${point[0]}" cy="${point[1]}" r="${alarm ? 4 : 3}"></circle>`;
      }).join("") : ""}
      <line class="axis-line" x1="${margin.left}" x2="${width - margin.right}" y1="${height - margin.bottom}" y2="${height - margin.bottom}"></line>
      ${mode === "normal" ? `<text class="chart-label" x="${margin.left}" y="${height - 7}" font-size="${fontSize}">t=${xMin}</text><text class="chart-label" x="${width - margin.right}" y="${height - 7}" text-anchor="end" font-size="${fontSize}">t=${xMax}</text>` : ""}
    </svg>`;
  }

  function renderAnnotationCallout(instance, context) {
    const data = dataForBinding(instance.dataBinding);
    const item = data[0] || null;
    const xValue = Number(item ? item[instance.dataBinding?.x || "x"] : instance.config.x);
    const yValue = Number(item ? item[instance.dataBinding?.y || "y"] : instance.config.y);
    const text = String(item ? item[instance.dataBinding?.text || "text"] : instance.config.text || "annotation");
    const direction = String(instance.config.direction || "right").toLowerCase();
    const severity = String(instance.config.severity || "warning").toLowerCase();
    if (!Number.isFinite(xValue) || !Number.isFinite(yValue)) return renderMissing("missing annotation", context);
    const { width, height, mode } = context;
    const margin = { left: 12, right: 12, top: 12, bottom: 12 };
    const anchorX = margin.left + clamp(0, xValue, 1) * (width - margin.left - margin.right);
    const anchorY = margin.top + clamp(0, yValue, 1) * (height - margin.top - margin.bottom);
    const boxW = mode === "normal" ? 108 : 92;
    const boxH = mode === "normal" ? 34 : 30;
    const offset = 16;
    const boxX = direction === "left" ? anchorX - offset - boxW : direction === "right" ? anchorX + offset : anchorX - boxW / 2;
    const boxY = direction === "up" ? anchorY - offset - boxH : direction === "down" ? anchorY + offset : anchorY - boxH / 2;
    const boxLeft = clamp(6, boxX, width - boxW - 6);
    const boxTop = clamp(6, boxY, height - boxH - 6);
    const tailX = clamp(8, anchorX, width - 8);
    const tailY = clamp(8, anchorY, height - 8);
    const lineTargetX = direction === "left" ? boxLeft + boxW : direction === "right" ? boxLeft : boxLeft + boxW / 2;
    const lineTargetY = direction === "up" ? boxTop + boxH : direction === "down" ? boxTop : boxTop + boxH / 2;
    const boxClass = `annotation-box ${severity}`;
    const badgeText = severity.toUpperCase();
    const fontSize = clamp(8, Math.min(width, height) * 0.08, 12);
    return `<svg class="chart-svg annotation-overlay" viewBox="0 0 ${width} ${height}" role="img">
      <defs>
        <marker id="annotation-arrow-${severity}" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto" markerUnits="strokeWidth">
          <path d="M0,0 L8,4 L0,8 z" fill="${severity === "critical" ? "#b84444" : severity === "info" ? "#2f6f9f" : "#c47d1f"}"></path>
        </marker>
      </defs>
      <line class="annotation-connector ${severity}" x1="${tailX}" y1="${tailY}" x2="${lineTargetX}" y2="${lineTargetY}" marker-end="url(#annotation-arrow-${severity})"></line>
      <circle class="annotation-anchor ${severity}" cx="${tailX}" cy="${tailY}" r="4"></circle>
      <rect class="${boxClass}" x="${boxLeft}" y="${boxTop}" width="${boxW}" height="${boxH}" rx="6"></rect>
      <text class="annotation-badge ${severity}" x="${boxLeft + 8}" y="${boxTop + 11}" font-size="${fontSize}">${svgText(badgeText)}</text>
      <text class="annotation-text" x="${boxLeft + 8}" y="${boxTop + boxH - 10}" font-size="${fontSize}">${svgText(text.slice(0, 34))}</text>
    </svg>`;
  }

  function renderAdaptiveModelStructureView(instance, context) {
    const data = dataForBinding(instance.dataBinding);
    const timeField = instance.config.time_field || "time";
    const primaryField = instance.config.primary_series_field || "primary_score";
    const secondaryField = instance.config.secondary_series_field || "secondary_score";
    const eventField = instance.config.event_field || "event";
    if (!data.length) return renderMissing("missing adaptive data", context);
    const valid = data.filter((item) =>
      Number.isFinite(Number(item[timeField])) &&
      Number.isFinite(Number(item[primaryField])) &&
      Number.isFinite(Number(item[secondaryField]))
    );
    if (!valid.length) return renderMissing("missing adaptive data", context);
    const { width, height, mode } = context;
    const margin = { left: mode === "normal" ? 42 : 30, right: 18, top: 16, bottom: mode === "normal" ? 34 : 24 };
    const plotW = Math.max(10, width - margin.left - margin.right);
    const plotH = Math.max(10, height - margin.top - margin.bottom);
    const [xMin, xMax] = numericExtent(valid, timeField);
    const [yMinRaw1, yMaxRaw1] = numericExtent(valid, primaryField);
    const [yMinRaw2, yMaxRaw2] = numericExtent(valid, secondaryField);
    const yMin = Math.min(yMinRaw1, yMinRaw2) - 0.04;
    const yMax = Math.max(yMaxRaw1, yMaxRaw2) + 0.04;
    const x = (value) => margin.left + ((Number(value) - xMin) / (xMax - xMin || 1)) * plotW;
    const y = (value) => margin.top + (1 - ((Number(value) - yMin) / (yMax - yMin || 1))) * plotH;
    const primary = valid.map((item) => [x(item[timeField]), y(item[primaryField]), Number(item[timeField]), Number(item[primaryField])]);
    const secondary = valid.map((item) => [x(item[timeField]), y(item[secondaryField]), Number(item[timeField]), Number(item[secondaryField])]);
    const events = valid
      .filter((item) => {
        const allowed = Array.isArray(instance.config.event_types) && instance.config.event_types.length
          ? instance.config.event_types
          : ["replacement", "promotion", "retrain"];
        return allowed.includes(String(item[eventField] || ""));
      })
      .map((item) => ({
        x: x(item[timeField]),
        y: y(Math.max(Number(item[primaryField]), Number(item[secondaryField]))),
        label: String(item[eventField] || "")
      }));
    const fontSize = clamp(9, Math.min(width, height) * 0.05, 13);
    const ticks = mode === "normal" ? [yMin, (yMin + yMax) / 2, yMax] : [yMin, yMax];
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      ${ticks.map((tick) => `<line class="grid-line" x1="${margin.left}" x2="${width - margin.right}" y1="${y(tick)}" y2="${y(tick)}"></line>`).join("")}
      <line class="axis-line" x1="${margin.left}" x2="${width - margin.right}" y1="${height - margin.bottom}" y2="${height - margin.bottom}"></line>
      <line class="axis-line" x1="${margin.left}" x2="${margin.left}" y1="${margin.top}" y2="${height - margin.bottom}"></line>
      <path class="adaptive-primary-line" d="${pathFromPoints(primary)}"></path>
      <path class="adaptive-secondary-line" d="${pathFromPoints(secondary)}"></path>
      ${events.map((event) => `<g transform="translate(${event.x},${event.y})"><circle class="adaptive-event-marker ${event.label}" r="5"></circle><text class="adaptive-event-label" x="8" y="4" font-size="${fontSize}">${svgText(event.label)}</text></g>`).join("")}
      ${ticks.map((tick) => `<text class="chart-label" x="${margin.left - 7}" y="${y(tick) + 4}" text-anchor="end" font-size="${fontSize}">${tick.toFixed(2)}</text>`).join("")}
      ${mode === "normal" ? `<text class="legend-text adaptive-legend primary" x="${margin.left}" y="${margin.top + 10}" font-size="${fontSize}">${svgText(instance.config.primary_label || "main model")}</text><text class="legend-text adaptive-legend secondary" x="${margin.left + 102}" y="${margin.top + 10}" font-size="${fontSize}">${svgText(instance.config.secondary_label || "alternate model")}</text>` : ""}
      ${mode === "normal" ? `<text class="chart-label" x="${margin.left}" y="${height - 7}" font-size="${fontSize}">t=${xMin}</text><text class="chart-label" x="${width - margin.right}" y="${height - 7}" text-anchor="end" font-size="${fontSize}">t=${xMax}</text>` : ""}
    </svg>`;
  }

  function renderCumulativeCurve(instance, context) {
    const data = dataForBinding(instance.dataBinding);
    const xField = instance.config.x_field || "x";
    const yField = instance.config.y_field || "cumulative";
    const seriesField = instance.config.series_field || "series";
    if (!data.length) return renderMissing("missing cumulative data", context);
    const valid = data.filter((item) => Number.isFinite(Number(item[xField])) && Number.isFinite(Number(item[yField])));
    if (!valid.length) return renderMissing("missing cumulative data", context);
    const { width, height, mode } = context;
    const margin = { left: mode === "normal" ? 42 : 30, right: 18, top: 16, bottom: mode === "normal" ? 34 : 24 };
    const plotW = Math.max(10, width - margin.left - margin.right);
    const plotH = Math.max(10, height - margin.top - margin.bottom);
    const [xMin, xMax] = numericExtent(valid, xField);
    const [yMinRaw, yMaxRaw] = numericExtent(valid, yField);
    const yMin = instance.config.normalize === false ? Math.min(0, yMinRaw) : 0;
    const yMax = instance.config.normalize === false ? yMaxRaw * 1.06 : Math.max(1, yMaxRaw);
    const x = (value) => margin.left + ((Number(value) - xMin) / (xMax - xMin || 1)) * plotW;
    const y = (value) => margin.top + (1 - ((Number(value) - yMin) / (yMax - yMin || 1))) * plotH;
    const seriesNames = Array.from(new Set(valid.map((item) => String(item[seriesField] || "series"))));
    const series = seriesNames.map((name) => ({
      name,
      points: valid
        .filter((item) => String(item[seriesField] || "series") === name)
        .sort((a, b) => Number(a[xField]) - Number(b[xField]))
        .map((item) => [x(item[xField]), y(item[yField]), Number(item[xField]), Number(item[yField])])
    }));
    const byX = new Map();
    valid.forEach((item) => {
      const key = Number(item[xField]).toFixed(6);
      if (!byX.has(key)) byX.set(key, {});
      byX.get(key)[String(item[seriesField] || "series")] = Number(item[yField]);
    });
    let gap = null;
    if (seriesNames.length >= 2) {
      byX.forEach((values, key) => {
        const diff = Math.abs((values[seriesNames[0]] ?? NaN) - (values[seriesNames[1]] ?? NaN));
        if (Number.isFinite(diff) && (!gap || diff > gap.diff)) {
          gap = { xValue: Number(key), low: Math.min(values[seriesNames[0]], values[seriesNames[1]]), high: Math.max(values[seriesNames[0]], values[seriesNames[1]]), diff };
        }
      });
    }
    const ticks = mode === "normal" ? [yMin, (yMin + yMax) / 2, yMax] : [yMin, yMax];
    const fontSize = clamp(9, Math.min(width, height) * 0.052, 13);
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      ${ticks.map((tick) => `<line class="grid-line" x1="${margin.left}" x2="${width - margin.right}" y1="${y(tick)}" y2="${y(tick)}"></line>`).join("")}
      <line class="axis-line" x1="${margin.left}" x2="${width - margin.right}" y1="${height - margin.bottom}" y2="${height - margin.bottom}"></line>
      <line class="axis-line" x1="${margin.left}" x2="${margin.left}" y1="${margin.top}" y2="${height - margin.bottom}"></line>
      ${series.map((item, index) => `<path class="cumulative-line series-${index % 4}" d="${pathFromPoints(item.points)}"></path>`).join("")}
      ${instance.config.gap_marker !== false && gap ? `<line class="cumulative-gap-line" x1="${x(gap.xValue)}" x2="${x(gap.xValue)}" y1="${y(gap.low)}" y2="${y(gap.high)}"></line>${mode === "normal" ? `<text class="cumulative-gap-label" x="${x(gap.xValue) + 5}" y="${y(gap.high) - 5}" font-size="${fontSize}">gap ${gap.diff.toFixed(2)}</text>` : ""}` : ""}
      ${ticks.map((tick) => `<text class="chart-label" x="${margin.left - 7}" y="${y(tick) + 4}" text-anchor="end" font-size="${fontSize}">${tick.toFixed(2)}</text>`).join("")}
      ${mode === "normal" ? series.map((item, index) => `<text class="legend-text cumulative-legend series-${index % 4}" x="${margin.left + index * 82}" y="${margin.top + 10}" font-size="${fontSize}">${svgText(item.name.slice(0, 10))}</text>`).join("") : ""}
      ${mode === "normal" ? `<text class="chart-label" x="${margin.left}" y="${height - 7}" font-size="${fontSize}">${xMin.toFixed(2)}</text><text class="chart-label" x="${width - margin.right}" y="${height - 7}" text-anchor="end" font-size="${fontSize}">${xMax.toFixed(2)}</text>` : ""}
    </svg>`;
  }

  function renderDomainSpecificVisual(instance, context) {
    const data = dataForBinding(instance.dataBinding);
    const xField = instance.config.x_field || instance.dataBinding?.x_field || "x";
    const referenceField = instance.config.reference_field || instance.dataBinding?.reference_field || "reference";
    const currentField = instance.config.current_field || instance.dataBinding?.current_field || "current";
    if (!data.length) return renderMissing("missing domain visual", context);
    const valid = data.filter((item) => Number.isFinite(Number(item[xField])) && Number.isFinite(Number(item[referenceField])) && Number.isFinite(Number(item[currentField])));
    if (!valid.length) return renderMissing("missing domain fields", context);
    const { width, height, mode } = context;
    const margin = { left: mode === "normal" ? 42 : 30, right: 18, top: 18, bottom: mode === "normal" ? 38 : 26 };
    const plotW = Math.max(10, width - margin.left - margin.right);
    const plotH = Math.max(10, height - margin.top - margin.bottom);
    const [xMin, xMax] = numericExtent(valid, xField);
    const yMin = 0;
    const yMax = Math.max(...valid.flatMap((item) => [Number(item[referenceField]), Number(item[currentField])]), 1);
    const x = (value) => margin.left + ((Number(value) - xMin) / (xMax - xMin || 1)) * plotW;
    const y = (value) => margin.top + (1 - ((Number(value) - yMin) / (yMax - yMin || 1))) * plotH;
    const reference = valid.map((item) => [x(item[xField]), y(item[referenceField])]);
    const current = valid.map((item) => [x(item[xField]), y(item[currentField])]);
    const areaPath = `${pathFromPoints(reference)} ${current.slice().reverse().map((point) => `L${point[0].toFixed(2)},${point[1].toFixed(2)}`).join(" ")} Z`;
    const maxGap = valid.reduce((best, item) => {
      const diff = Math.abs(Number(item[currentField]) - Number(item[referenceField]));
      return diff > best.diff ? { diff, item } : best;
    }, { diff: -1, item: valid[0] });
    const fontSize = clamp(9, Math.min(width, height) * 0.052, 13);
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      <path class="domain-gap-area" d="${areaPath}"></path>
      <path class="domain-reference-line" d="${pathFromPoints(reference)}"></path>
      <path class="domain-current-line" d="${pathFromPoints(current)}"></path>
      <line class="axis-line" x1="${margin.left}" x2="${width - margin.right}" y1="${height - margin.bottom}" y2="${height - margin.bottom}"></line>
      <line class="axis-line" x1="${margin.left}" x2="${margin.left}" y1="${margin.top}" y2="${height - margin.bottom}"></line>
      <line class="domain-gap-marker" x1="${x(maxGap.item[xField])}" x2="${x(maxGap.item[xField])}" y1="${y(maxGap.item[referenceField])}" y2="${y(maxGap.item[currentField])}"></line>
      <text class="chart-value" x="${margin.left}" y="${margin.top + 10}" font-size="${fontSize}">${svgText(instance.config.visual_code || "domain visual")}</text>
      ${mode === "normal" ? `<text class="legend-text" x="${margin.left}" y="${height - 7}" font-size="${fontSize}">fallback ${svgText(instance.config.fallback_component || "none")} / gap ${maxGap.diff.toFixed(2)}</text>` : ""}
    </svg>`;
  }

  function renderMatrixView(instance, context) {
    const data = dataForBinding(instance.dataBinding);
    const rowField = instance.config.row_field || "method";
    const columnField = instance.config.column_field || "condition";
    const valueField = instance.config.cell_value_field || "status";
    if (!data.length) return renderMissing("missing matrix data", context);
    const rows = Array.from(new Set(data.map((item) => String(item[rowField] || "")))).filter(Boolean);
    const columns = Array.from(new Set(data.map((item) => String(item[columnField] || "")))).filter(Boolean);
    if (!rows.length || !columns.length) return renderMissing("missing matrix fields", context);
    const { width, height, mode } = context;
    const margin = { left: mode === "normal" ? 76 : 54, right: 14, top: mode === "normal" ? 34 : 22, bottom: 14 };
    const cellW = Math.max(24, (width - margin.left - margin.right) / columns.length);
    const cellH = Math.max(22, (height - margin.top - margin.bottom) / rows.length);
    const fontSize = clamp(8, Math.min(width, height) * 0.05, 12);
    const cell = (row, column) => data.find((item) => String(item[rowField] || "") === row && String(item[columnField] || "") === column);
    const statusClass = (value) => {
      const text = String(value || "").toLowerCase();
      if (text.includes("recommend")) return "recommended";
      if (text.includes("block")) return "blocked";
      if (text.includes("limit")) return "limited";
      return "supported";
    };
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      ${columns.map((column, index) => `<text class="matrix-head" x="${margin.left + index * cellW + cellW / 2}" y="${margin.top - 10}" text-anchor="middle" font-size="${fontSize}">${svgText(column.slice(0, 10))}</text>`).join("")}
      ${rows.map((row, rowIndex) => `<text class="matrix-row-label" x="${margin.left - 8}" y="${margin.top + rowIndex * cellH + cellH * 0.62}" text-anchor="end" font-size="${fontSize}">${svgText(row.slice(0, 12))}</text>
        ${columns.map((column, columnIndex) => {
          const item = cell(row, column);
          const value = item ? item[valueField] : "";
          const cls = statusClass(value);
          const x = margin.left + columnIndex * cellW;
          const y = margin.top + rowIndex * cellH;
          return `<rect class="matrix-cell ${cls}" x="${x}" y="${y}" width="${Math.max(2, cellW - 3)}" height="${Math.max(2, cellH - 3)}" rx="4"></rect>
            ${mode === "normal" ? `<text class="matrix-cell-text" x="${x + cellW / 2}" y="${y + cellH * 0.62}" text-anchor="middle" font-size="${fontSize}">${svgText(String(value).slice(0, 4))}</text>` : ""}`;
        }).join("")}`).join("")}
    </svg>`;
  }

  function renderModelDiagnosticCurve(instance, context) {
    const data = dataForBinding(instance.dataBinding);
    const xField = instance.config.x_field || "fpr";
    const yField = instance.config.y_field || "tpr";
    if (!data.length) return renderMissing("missing diagnostic curve", context);
    const valid = data.filter((item) => Number.isFinite(Number(item[xField])) && Number.isFinite(Number(item[yField]))).sort((a, b) => Number(a[xField]) - Number(b[xField]));
    if (!valid.length) return renderMissing("missing curve fields", context);
    const { width, height, mode } = context;
    const margin = { left: mode === "normal" ? 42 : 30, right: 18, top: 16, bottom: mode === "normal" ? 34 : 24 };
    const plotW = Math.max(10, width - margin.left - margin.right);
    const plotH = Math.max(10, height - margin.top - margin.bottom);
    const x = (value) => margin.left + clamp(0, Number(value), 1) * plotW;
    const y = (value) => margin.top + (1 - clamp(0, Number(value), 1)) * plotH;
    const points = valid.map((item) => [x(item[xField]), y(item[yField])]);
    const fontSize = clamp(9, Math.min(width, height) * 0.052, 13);
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      <rect class="diagnostic-frame" x="${margin.left}" y="${margin.top}" width="${plotW}" height="${plotH}"></rect>
      ${instance.config.reference_line !== false ? `<line class="diagnostic-reference-line" x1="${margin.left}" x2="${width - margin.right}" y1="${height - margin.bottom}" y2="${margin.top}"></line>` : ""}
      <path class="diagnostic-curve-line" d="${pathFromPoints(points)}"></path>
      ${mode === "normal" ? points.map((point) => `<circle class="diagnostic-point" cx="${point[0]}" cy="${point[1]}" r="3"></circle>`).join("") : ""}
      <text class="chart-value" x="${margin.left}" y="${margin.top + 12}" font-size="${fontSize}">${svgText(instance.config.curve_type || "curve")} ${instance.config.auc ? `AUC ${Number(instance.config.auc).toFixed(2)}` : ""}</text>
      ${mode === "normal" ? `<text class="chart-label" x="${margin.left}" y="${height - 7}" font-size="${fontSize}">0</text><text class="chart-label" x="${width - margin.right}" y="${height - 7}" text-anchor="end" font-size="${fontSize}">1</text>` : ""}
    </svg>`;
  }

  function renderQuantileView(instance, context) {
    const data = dataForBinding(instance.dataBinding).slice();
    const quantileField = instance.config.quantile_field || "quantile";
    const valueField = instance.config.value_field || "delta";
    if (!data.length) return renderMissing("missing quantiles", context);
    const valid = data.filter((item) => Number.isFinite(Number(item[valueField])));
    if (!valid.length) return renderMissing("missing quantile values", context);
    const { width, height, mode } = context;
    const margin = { left: mode === "normal" ? 58 : 44, right: 18, top: 16, bottom: 24 };
    const plotW = Math.max(10, width - margin.left - margin.right);
    const rowH = Math.max(22, (height - margin.top - margin.bottom) / valid.length);
    const target = Number(instance.config.target_line ?? 0);
    const maxAbs = Math.max(...valid.map((item) => Math.abs(Number(item[valueField]))), Math.abs(target), 0.1);
    const zeroX = margin.left + plotW / 2;
    const fontSize = clamp(9, Math.min(width, height) * 0.052, 13);
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      <line class="quantile-target-line" x1="${zeroX + (target / (maxAbs * 2)) * plotW}" x2="${zeroX + (target / (maxAbs * 2)) * plotW}" y1="${margin.top}" y2="${height - margin.bottom}"></line>
      ${valid.map((item, index) => {
        const value = Number(item[valueField]);
        const barX = value >= 0 ? zeroX : zeroX + (value / (maxAbs * 2)) * plotW;
        const barW = Math.max(2, Math.abs(value) / (maxAbs * 2) * plotW);
        const y = margin.top + index * rowH + 4;
        const label = String(item[quantileField] || "").slice(0, 8);
        const tail = instance.config.tail_emphasis !== false && (index === 0 || index === valid.length - 1);
        return `<text class="chart-label" x="${margin.left - 8}" y="${y + rowH * 0.55}" text-anchor="end" font-size="${fontSize}">${svgText(label)}</text>
          <rect class="quantile-bar ${value >= 0 ? "positive" : "negative"}${tail ? " tail" : ""}" x="${barX}" y="${y}" width="${barW}" height="${Math.max(8, rowH - 8)}" rx="4"></rect>
          ${mode === "normal" ? `<text class="chart-value" x="${value >= 0 ? barX + barW + 5 : barX - 5}" y="${y + rowH * 0.55}" text-anchor="${value >= 0 ? "start" : "end"}" font-size="${fontSize}">${value >= 0 ? "+" : ""}${value.toFixed(2)}</text>` : ""}`;
      }).join("")}
    </svg>`;
  }

  function renderRawSignalTrend(instance, context) {
    const data = dataForBinding(instance.dataBinding);
    const timeField = instance.config.time_field || "time";
    const valueField = instance.config.value_field || "signal";
    if (!data.length) return renderMissing("missing raw signal", context);
    const valid = data.filter((item) => Number.isFinite(Number(item[timeField])) && Number.isFinite(Number(item[valueField])));
    if (!valid.length) return renderMissing("missing signal values", context);
    const { width, height, mode } = context;
    const margin = { left: mode === "normal" ? 42 : 30, right: 18, top: 16, bottom: mode === "normal" ? 34 : 24 };
    const plotW = Math.max(10, width - margin.left - margin.right);
    const plotH = Math.max(10, height - margin.top - margin.bottom);
    const reference = Number(instance.config.reference_value ?? 0.5);
    const [xMin, xMax] = numericExtent(valid, timeField);
    const [yMinRaw, yMaxRaw] = numericExtent(valid, valueField);
    const yMin = Math.min(yMinRaw, reference) - 0.04;
    const yMax = Math.max(yMaxRaw, reference) + 0.04;
    const x = (value) => margin.left + ((Number(value) - xMin) / (xMax - xMin || 1)) * plotW;
    const y = (value) => margin.top + (1 - ((Number(value) - yMin) / (yMax - yMin || 1))) * plotH;
    const rawPoints = valid.map((item) => [x(item[timeField]), y(item[valueField])]);
    const smoothN = Math.max(1, Number(instance.config.smoothing_window || 1));
    const smooth = valid.map((item, index) => {
      const slice = valid.slice(Math.max(0, index - smoothN + 1), index + 1);
      const avg = slice.reduce((sum, row) => sum + Number(row[valueField]), 0) / slice.length;
      return [x(item[timeField]), y(avg)];
    });
    const fontSize = clamp(9, Math.min(width, height) * 0.052, 13);
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      <line class="raw-reference-line" x1="${margin.left}" x2="${width - margin.right}" y1="${y(reference)}" y2="${y(reference)}"></line>
      <path class="raw-signal-line" d="${pathFromPoints(rawPoints)}"></path>
      ${smoothN > 1 ? `<path class="raw-smooth-line" d="${pathFromPoints(smooth)}"></path>` : ""}
      ${mode === "normal" ? rawPoints.map((point) => `<circle class="raw-signal-point" cx="${point[0]}" cy="${point[1]}" r="2.5"></circle>`).join("") : ""}
      <line class="axis-line" x1="${margin.left}" x2="${width - margin.right}" y1="${height - margin.bottom}" y2="${height - margin.bottom}"></line>
      <text class="chart-value" x="${margin.left}" y="${margin.top + 10}" font-size="${fontSize}">latest ${Number(valid[valid.length - 1][valueField]).toFixed(2)}</text>
    </svg>`;
  }

  function renderSmallMultiples(instance, context) {
    const data = dataForBinding(instance.dataBinding);
    const facetField = instance.config.facet_field || "feature";
    const timeField = instance.config.time_field || "time";
    const valueField = instance.config.value_field || "value";
    if (!data.length) return renderMissing("missing small multiples", context);
    const facets = Array.from(new Set(data.map((item) => String(item[facetField] || "")))).filter(Boolean).slice(0, Number(instance.config.max_panels || 4));
    if (!facets.length) return renderMissing("missing facets", context);
    const { width, height, mode } = context;
    const cols = facets.length > 2 && mode !== "summary_only" ? 2 : 1;
    const rows = Math.ceil(facets.length / cols);
    const gap = 8;
    const panelW = (width - gap * (cols + 1)) / cols;
    const panelH = (height - gap * (rows + 1)) / rows;
    const allValid = data.filter((item) => Number.isFinite(Number(item[timeField])) && Number.isFinite(Number(item[valueField])));
    const [globalYMin, globalYMax] = numericExtent(allValid, valueField);
    const fontSize = clamp(8, Math.min(width, height) * 0.045, 12);
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      ${facets.map((facet, index) => {
        const col = index % cols;
        const row = Math.floor(index / cols);
        const left = gap + col * (panelW + gap);
        const top = gap + row * (panelH + gap);
        const rowsForFacet = allValid.filter((item) => String(item[facetField] || "") === facet).sort((a, b) => Number(a[timeField]) - Number(b[timeField]));
        const [xMin, xMax] = numericExtent(rowsForFacet, timeField);
        const [localYMin, localYMax] = numericExtent(rowsForFacet, valueField);
        const yMin = instance.config.shared_scale === false ? localYMin : globalYMin;
        const yMax = instance.config.shared_scale === false ? localYMax : globalYMax;
        const x = (value) => left + 8 + ((Number(value) - xMin) / (xMax - xMin || 1)) * Math.max(10, panelW - 16);
        const y = (value) => top + 18 + (1 - ((Number(value) - yMin) / (yMax - yMin || 1))) * Math.max(10, panelH - 28);
        const points = rowsForFacet.map((item) => [x(item[timeField]), y(item[valueField])]);
        return `<rect class="small-panel-frame" x="${left}" y="${top}" width="${panelW}" height="${panelH}" rx="5"></rect>
          <text class="small-panel-title" x="${left + 8}" y="${top + 13}" font-size="${fontSize}">${svgText(facet.slice(0, 12))}</text>
          <path class="small-panel-line" d="${pathFromPoints(points)}"></path>`;
      }).join("")}
    </svg>`;
  }

  function renderUncertaintyBand(instance, context) {
    const data = dataForBinding(instance.dataBinding);
    const timeField = instance.config.time_field || "time";
    const lowerField = instance.config.lower_field || "lower";
    const upperField = instance.config.upper_field || "upper";
    const centerField = instance.config.center_field || "center";
    if (!data.length) return renderMissing("missing uncertainty", context);
    const valid = data.filter((item) => Number.isFinite(Number(item[timeField])) && Number.isFinite(Number(item[lowerField])) && Number.isFinite(Number(item[upperField])));
    if (!valid.length) return renderMissing("missing band fields", context);
    const { width, height, mode } = context;
    const margin = { left: mode === "normal" ? 42 : 30, right: 18, top: 16, bottom: mode === "normal" ? 34 : 24 };
    const plotW = Math.max(10, width - margin.left - margin.right);
    const plotH = Math.max(10, height - margin.top - margin.bottom);
    const [xMin, xMax] = numericExtent(valid, timeField);
    const yMin = Math.min(...valid.map((item) => Number(item[lowerField]))) - 0.04;
    const yMax = Math.max(...valid.map((item) => Number(item[upperField]))) + 0.04;
    const x = (value) => margin.left + ((Number(value) - xMin) / (xMax - xMin || 1)) * plotW;
    const y = (value) => margin.top + (1 - ((Number(value) - yMin) / (yMax - yMin || 1))) * plotH;
    const upper = valid.map((item) => [x(item[timeField]), y(item[upperField])]);
    const lower = valid.map((item) => [x(item[timeField]), y(item[lowerField])]);
    const center = valid.filter((item) => Number.isFinite(Number(item[centerField]))).map((item) => [x(item[timeField]), y(item[centerField])]);
    const areaPath = `${pathFromPoints(upper)} ${lower.slice().reverse().map((point) => `L${point[0].toFixed(2)},${point[1].toFixed(2)}`).join(" ")} Z`;
    const fontSize = clamp(9, Math.min(width, height) * 0.052, 13);
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      <path class="uncertainty-band-area" style="opacity: ${clamp(0.08, Number(instance.config.band_opacity || 0.24), 0.65)}" d="${areaPath}"></path>
      <path class="uncertainty-bound-line" d="${pathFromPoints(upper)}"></path>
      <path class="uncertainty-bound-line" d="${pathFromPoints(lower)}"></path>
      ${center.length ? `<path class="uncertainty-center-line" d="${pathFromPoints(center)}"></path>` : ""}
      <line class="axis-line" x1="${margin.left}" x2="${width - margin.right}" y1="${height - margin.bottom}" y2="${height - margin.bottom}"></line>
      ${mode === "normal" ? `<text class="legend-text" x="${margin.left}" y="${margin.top + 10}" font-size="${fontSize}">${svgText(instance.config.band_mode || "uncertainty")}</text>` : ""}
    </svg>`;
  }

  function renderWindowView(instance, context) {
    const data = dataForBinding(instance.dataBinding);
    const idField = instance.config.window_id_field || "window";
    const startField = instance.config.start_field || "start";
    const endField = instance.config.end_field || "end";
    const roleField = instance.config.window_role_field || "role";
    if (!data.length) return renderMissing("missing windows", context);
    const valid = data.filter((item) => Number.isFinite(Number(item[startField])) && Number.isFinite(Number(item[endField])));
    if (!valid.length) return renderMissing("missing window bounds", context);
    const { width, height, mode } = context;
    const margin = { left: mode === "normal" ? 58 : 42, right: 18, top: 18, bottom: 24 };
    const plotW = Math.max(10, width - margin.left - margin.right);
    const rowH = Math.max(22, (height - margin.top - margin.bottom) / valid.length);
    const min = Math.min(...valid.map((item) => Number(item[startField])));
    const max = Math.max(...valid.map((item) => Number(item[endField])));
    const x = (value) => margin.left + ((Number(value) - min) / (max - min || 1)) * plotW;
    const fontSize = clamp(9, Math.min(width, height) * 0.052, 13);
    return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      ${valid.map((item, index) => {
        const y = margin.top + index * rowH + 4;
        const start = Number(item[startField]);
        const end = Number(item[endField]);
        const role = String(item[roleField] || "window").toLowerCase();
        const label = String(item[idField] || role).slice(0, 10);
        return `<text class="chart-label" x="${margin.left - 8}" y="${y + rowH * 0.55}" text-anchor="end" font-size="${fontSize}">${svgText(label)}</text>
          <rect class="window-bar ${role}" x="${x(start)}" y="${y}" width="${Math.max(2, x(end) - x(start))}" height="${Math.max(9, rowH - 8)}" rx="5"></rect>
          ${instance.config.show_boundaries !== false ? `<line class="window-boundary" x1="${x(start)}" x2="${x(start)}" y1="${y - 2}" y2="${y + rowH - 4}"></line><line class="window-boundary" x1="${x(end)}" x2="${x(end)}" y1="${y - 2}" y2="${y + rowH - 4}"></line>` : ""}
          ${mode === "normal" ? `<text class="chart-value" x="${x(end) + 5}" y="${y + rowH * 0.55}" font-size="${fontSize}">${start}-${end}</text>` : ""}`;
      }).join("")}
      <line class="axis-line" x1="${margin.left}" x2="${width - margin.right}" y1="${height - margin.bottom}" y2="${height - margin.bottom}"></line>
    </svg>`;
  }

  applyPropertiesButton.addEventListener("click", applyProperties);
  deleteComponentButton.addEventListener("click", deleteSelectedComponent);
  savedLayoutSelect.addEventListener("change", applySavedLayout);
  openLayoutDesignerButton.addEventListener("click", () => {
    window.open("./split_layout_practice.html", "chart_layout_designer", "width=1280,height=840");
  });
  newChartButton.addEventListener("click", newChart);
  savedChartSelect.addEventListener("change", loadSelectedChart);
  saveChartButton.addEventListener("click", saveCurrentChart);
  deleteChartButton.addEventListener("click", deleteSelectedChart);
  buildButton.addEventListener("click", buildPreview);
  resetButton.addEventListener("click", resetPrototype);
  layoutPresetSelect.addEventListener("change", () => changeLayoutPreset(layoutPresetSelect.value));
  window.addEventListener("focus", () => {
    loadSavedLayouts();
    loadSavedCharts();
  });

  renderAll();
  loadSavedLayouts();
  loadSavedCharts();
})();
