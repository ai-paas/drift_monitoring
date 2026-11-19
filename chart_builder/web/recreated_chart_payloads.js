// @managed-contract contract_id=chart_builder.recreated_payloads level=P1
window.RECREATED_CHART_PAYLOADS = [
  {
    "chartId": "CHART-ADAPT-001",
    "title": "CHART-ADAPT-001 - HAT 모델의 드리프트 감지와 대체 트리 교체 과정",
    "originalPath": "./drift_report_charts/chart_adapt_001.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_adapt_001",
      "displayName": "CHART-ADAPT-001 source layout",
      "columns": 12,
      "rows": 3,
      "gridTemplateRows": "76px 250px 250px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "온라인 정확도 추세",
          "description": "t=1~8에는 accuracy가 0.91 수준으로 안정적이다가 t=11 warning 이후 계속 하락해 t=19에서 0.72까지 내려간다. t=23 replacement marker 이후에는 0.84, 0.86, 0.90대로 회복되는지를 읽는다.",
          "headerHeight": 76,
          "stageInset": {
            "top": 84,
            "right": 16,
            "bottom": -8,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "감지기 상태 타임라인",
          "description": "상태가 normal(t=1~10) → warning(t=11~13) → alternate(t=14~22) → replace(t=23 이후) 순서로 이어지는지 본다. 이 순서가 맞아야 단순 성능 하락이 아니라 HAT의 적응 절차로 해석할 수 있다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "트리 크기 추세",
          "description": "alternate tree node가 t=11부터 4, 8, 12...로 증가해 t=22에서 64 nodes까지 커지고, t=23 replacement에서 0으로 내려가는지 본다. 동시에 main tree size가 57에서 42로 재구성되면 교체가 반영된 것이다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-ADAPT-001.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-ADAPT-001.summary",
          "label_field": "label",
          "primary_metric_field": "value"
        }
      },
      {
        "componentInstanceId": "CHART-ADAPT-001.accuracy.0",
        "componentType": "performance_metric_view",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "time_field": "time",
          "value_field": "value",
          "y_min": 0.68,
          "y_max": 0.94,
          "label": "online accuracy",
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 28,
            "bottom": 62,
            "left": 58
          },
          "x_ticks": [
            1,
            8,
            16,
            24,
            32
          ],
          "y_ticks": [
            0.7,
            0.78,
            0.86,
            0.94
          ],
          "x_axis_label": "time index",
          "y_axis_label": "online accuracy",
          "point_sample_every": 3,
          "point_radius": 3.5
        },
        "dataBinding": {
          "source": "chart.CHART-ADAPT-001.accuracy",
          "time_field": "time",
          "value_field": "value"
        }
      },
      {
        "componentInstanceId": "CHART-ADAPT-001.events.0",
        "componentType": "event_marker",
        "area": "main",
        "isOverlay": true,
        "zIndex": 20,
        "config": {
          "time_field": "time",
          "event_type_field": "event_type",
          "label_field": "label",
          "x_min": 1,
          "x_max": 32,
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 28,
            "bottom": 62,
            "left": 58
          },
          "value_source_component_id": "CHART-ADAPT-001.accuracy.0",
          "highlight_event_type": "replacement",
          "highlight_point": true,
          "highlight_radius": 7,
          "annotation_label": "alternate replacement restores accuracy",
          "annotation_dx": -8,
          "annotation_dy_fraction": 0.35
        },
        "dataBinding": {
          "source": "chart.CHART-ADAPT-001.events",
          "time_field": "time",
          "event_type_field": "event_type",
          "label_field": "label"
        }
      },
      {
        "componentInstanceId": "CHART-ADAPT-001.states.0",
        "componentType": "state_timeline",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "window_id_field": "window",
          "start_field": "start",
          "end_field": "end",
          "window_role_field": "role",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 32,
            "right": 24,
            "bottom": 38,
            "left": 48
          },
          "track_y": 74,
          "track_height": 30,
          "axis_label": "node detector state timeline",
          "axis_label_x": 228,
          "axis_label_y": 179,
          "role_class_map": {
            "normal": "state-normal",
            "warning": "state-warning",
            "alternate": "state-alt",
            "replace": "state-replace"
          },
          "label_map": {
            "alternate": "alt",
            "replace": "repl"
          },
          "marker_role": "replace",
          "marker_position_field": "start",
          "marker_circle": true,
          "marker_radius": 7
        },
        "dataBinding": {
          "source": "chart.CHART-ADAPT-001.states",
          "window_id_field": "window",
          "start_field": "start",
          "end_field": "end",
          "window_role_field": "role"
        }
      },
      {
        "componentInstanceId": "CHART-ADAPT-001.tree_size.0",
        "componentType": "adaptive_model_structure_view",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "time_field": "time",
          "value_field": "value",
          "secondary_value_field": "secondary_value",
          "y_min": 0,
          "y_max": 70,
          "label": "main / alternate tree size",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 22,
            "bottom": 34,
            "left": 48
          },
          "y_ticks": [
            0,
            20,
            40,
            60
          ],
          "x_ticks": [],
          "x_axis_label": "main / alternate tree size",
          "y_axis_label": false,
          "axis_label_x": 208,
          "axis_label_y": 177,
          "line_class": "main-line",
          "secondary_line_class": "alt-line",
          "show_points": false,
          "show_secondary_points": false,
          "vertical_markers": [
            {
              "x": 23,
              "class": "marker-line"
            }
          ],
          "annotations": [
            {
              "text": "alternate grows",
              "x": 13,
              "y": 60,
              "class": "callout"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-ADAPT-001.tree_size",
          "time_field": "time",
          "value_field": "value",
          "secondary_value_field": "secondary_value"
        }
      },
      {
        "componentInstanceId": "CHART-ADAPT-001.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label": "HAT replacement restores accuracy after alternate tree growth.",
          "visual_code": "interpretation"
        },
        "dataBinding": {
          "source": "chart.CHART-ADAPT-001.summary"
        }
      }
    ],
    "data": {
      "chart.CHART-ADAPT-001.summary": [
        {
          "label": "accuracy min",
          "value": 0.72
        },
        {
          "label": "replacement",
          "value": 23,
          "displayValue": "t=23"
        },
        {
          "label": "alt nodes",
          "value": 64
        }
      ],
      "chart.CHART-ADAPT-001.accuracy": [
        {
          "time": 1,
          "value": 0.91
        },
        {
          "time": 2,
          "value": 0.92
        },
        {
          "time": 3,
          "value": 0.91
        },
        {
          "time": 4,
          "value": 0.9
        },
        {
          "time": 5,
          "value": 0.91
        },
        {
          "time": 6,
          "value": 0.9
        },
        {
          "time": 7,
          "value": 0.89
        },
        {
          "time": 8,
          "value": 0.88
        },
        {
          "time": 9,
          "value": 0.86
        },
        {
          "time": 10,
          "value": 0.84
        },
        {
          "time": 11,
          "value": 0.82
        },
        {
          "time": 12,
          "value": 0.8
        },
        {
          "time": 13,
          "value": 0.78
        },
        {
          "time": 14,
          "value": 0.77
        },
        {
          "time": 15,
          "value": 0.76
        },
        {
          "time": 16,
          "value": 0.75
        },
        {
          "time": 17,
          "value": 0.74
        },
        {
          "time": 18,
          "value": 0.73
        },
        {
          "time": 19,
          "value": 0.72
        },
        {
          "time": 20,
          "value": 0.73
        },
        {
          "time": 21,
          "value": 0.75
        },
        {
          "time": 22,
          "value": 0.78
        },
        {
          "time": 23,
          "value": 0.81
        },
        {
          "time": 24,
          "value": 0.84
        },
        {
          "time": 25,
          "value": 0.86
        },
        {
          "time": 26,
          "value": 0.88
        },
        {
          "time": 27,
          "value": 0.89
        },
        {
          "time": 28,
          "value": 0.9
        },
        {
          "time": 29,
          "value": 0.91
        },
        {
          "time": 30,
          "value": 0.91
        },
        {
          "time": 31,
          "value": 0.92
        },
        {
          "time": 32,
          "value": 0.92
        }
      ],
      "chart.CHART-ADAPT-001.states": [
        {
          "window": "normal",
          "start": 1,
          "end": 11,
          "role": "normal"
        },
        {
          "window": "warn",
          "start": 11,
          "end": 14,
          "role": "warning"
        },
        {
          "window": "alternate",
          "start": 14,
          "end": 23,
          "role": "alternate"
        },
        {
          "window": "replace",
          "start": 23,
          "end": 32,
          "role": "replace"
        }
      ],
      "chart.CHART-ADAPT-001.tree_size": [
        {
          "time": 1,
          "value": 18,
          "secondary_value": 0
        },
        {
          "time": 2,
          "value": 20,
          "secondary_value": 0
        },
        {
          "time": 3,
          "value": 22,
          "secondary_value": 0
        },
        {
          "time": 4,
          "value": 24,
          "secondary_value": 0
        },
        {
          "time": 5,
          "value": 25,
          "secondary_value": 0
        },
        {
          "time": 6,
          "value": 27,
          "secondary_value": 0
        },
        {
          "time": 7,
          "value": 29,
          "secondary_value": 0
        },
        {
          "time": 8,
          "value": 31,
          "secondary_value": 0
        },
        {
          "time": 9,
          "value": 34,
          "secondary_value": 0
        },
        {
          "time": 10,
          "value": 36,
          "secondary_value": 0
        },
        {
          "time": 11,
          "value": 38,
          "secondary_value": 4
        },
        {
          "time": 12,
          "value": 40,
          "secondary_value": 8
        },
        {
          "time": 13,
          "value": 42,
          "secondary_value": 12
        },
        {
          "time": 14,
          "value": 44,
          "secondary_value": 17
        },
        {
          "time": 15,
          "value": 46,
          "secondary_value": 22
        },
        {
          "time": 16,
          "value": 48,
          "secondary_value": 28
        },
        {
          "time": 17,
          "value": 50,
          "secondary_value": 34
        },
        {
          "time": 18,
          "value": 52,
          "secondary_value": 40
        },
        {
          "time": 19,
          "value": 54,
          "secondary_value": 46
        },
        {
          "time": 20,
          "value": 55,
          "secondary_value": 52
        },
        {
          "time": 21,
          "value": 56,
          "secondary_value": 58
        },
        {
          "time": 22,
          "value": 57,
          "secondary_value": 64
        },
        {
          "time": 23,
          "value": 42,
          "secondary_value": 0
        },
        {
          "time": 24,
          "value": 43,
          "secondary_value": 0
        },
        {
          "time": 25,
          "value": 45,
          "secondary_value": 0
        },
        {
          "time": 26,
          "value": 47,
          "secondary_value": 0
        },
        {
          "time": 27,
          "value": 49,
          "secondary_value": 0
        },
        {
          "time": 28,
          "value": 51,
          "secondary_value": 0
        },
        {
          "time": 29,
          "value": 53,
          "secondary_value": 0
        },
        {
          "time": 30,
          "value": 54,
          "secondary_value": 0
        },
        {
          "time": 31,
          "value": 55,
          "secondary_value": 0
        },
        {
          "time": 32,
          "value": 56,
          "secondary_value": 0
        }
      ],
      "chart.CHART-ADAPT-001.events": [
        {
          "time": 11,
          "event_type": "warning",
          "label": "warning"
        },
        {
          "time": 14,
          "event_type": "alternate",
          "label": "alternate"
        },
        {
          "time": 23,
          "event_type": "replacement",
          "label": "replace"
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-ADAPT-002",
    "title": "CHART-ADAPT-002 - 재학습 전후 성능",
    "originalPath": "./drift_report_charts/chart_adapt_002.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_adapt_002",
      "displayName": "CHART-ADAPT-002 source layout",
      "columns": 12,
      "rows": 3,
      "gridTemplateRows": "76px 250px 250px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "재학습 전후 성능",
          "description": "Champion AUC가 t=18 전후 0.74까지 하락한 뒤, t=24 retrain event 이후 challenger 성능이 0.86 이상으로 회복되는지 읽는다.",
          "headerHeight": 76,
          "stageInset": {
            "top": 84,
            "right": 16,
            "bottom": -8,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "경보 및 재학습 타임라인",
          "description": "normal(t=1~13) → warning(t=13~18) → alarm(t=18~24) → retrain/monitor(t=24 이후) 순서인지 확인한다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "운영 모델과 후보 모델 비교",
          "description": "Challenger는 AUC 0.87, F1 0.82로 개선되지만 latency가 0.53으로 증가하므로 승격 전 운영 영향을 점검한다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-ADAPT-002.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-ADAPT-002.summary",
          "label_field": "label",
          "primary_metric_field": "value"
        }
      },
      {
        "componentInstanceId": "CHART-ADAPT-002.performance.0",
        "componentType": "performance_metric_view",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "time_field": "time",
          "value_field": "champion",
          "secondary_value_field": "challenger",
          "y_min": 0.7,
          "y_max": 0.92,
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 30,
            "bottom": 62,
            "left": 58
          },
          "x_ticks": [
            1,
            8,
            16,
            24,
            32
          ],
          "y_ticks": [
            0.72,
            0.78,
            0.84,
            0.9
          ],
          "x_axis_label": "time index",
          "y_axis_label": "validation AUC",
          "line_class": "champion-line",
          "secondary_line_class": "challenger-line",
          "point_sample_every": 3,
          "point_radius": 3.5,
          "background_regions": [
            {
              "x0": 1,
              "x1": 24,
              "fill": "rgba(201,149,47,0.08)"
            },
            {
              "x0": 24,
              "x1": 32,
              "fill": "rgba(58,128,100,0.08)"
            }
          ],
          "horizontal_markers": [
            {
              "y": 0.84,
              "class": "baseline-line",
              "label": "target AUC 0.84",
              "label_x": 2,
              "label_dy": -8,
              "label_class": "axis-label"
            }
          ],
          "vertical_markers": [
            {
              "x": 18,
              "class": "alarm-line"
            },
            {
              "x": 24,
              "class": "retrain-line"
            }
          ],
          "point_highlights": [
            {
              "x": 18,
              "field": "champion",
              "class": "alarm-point",
              "r": 6
            },
            {
              "x": 24,
              "field": "challenger",
              "class": "retrain-point",
              "r": 3.5
            },
            {
              "x": 27,
              "field": "challenger",
              "class": "challenger-point",
              "r": 6
            }
          ],
          "annotations": [
            {
              "text": "drift alarm",
              "x": 15,
              "y": 0.72,
              "class": "callout-alarm"
            },
            {
              "text": "retrain event",
              "x": 25,
              "y": 0.72,
              "class": "callout-retrain"
            },
            {
              "text": "challenger promoted",
              "x": 26,
              "y": 0.89,
              "class": "callout-win"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-ADAPT-002.performance",
          "time_field": "time",
          "value_field": "champion",
          "secondary_value_field": "challenger"
        }
      },
      {
        "componentInstanceId": "CHART-ADAPT-002.timeline.0",
        "componentType": "state_timeline",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "window_id_field": "window",
          "start_field": "start",
          "end_field": "end",
          "window_role_field": "role",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 34,
            "right": 24,
            "bottom": 38,
            "left": 48
          },
          "track_y": 76,
          "track_height": 30,
          "axis_label": "workflow event timeline",
          "axis_label_x": 226,
          "axis_label_y": 179,
          "role_class_map": {
            "normal": "state-normal",
            "warning": "state-warning",
            "alarm": "state-drift",
            "retrain_monitor": "state-retrain"
          },
          "label_map": {
            "retrain_monitor": "retrain/monitor"
          },
          "markers": [
            {
              "role": "alarm",
              "position_field": "start",
              "class": "alarm-line",
              "circle": true,
              "circle_class": "alarm-point",
              "radius": 6
            },
            {
              "role": "retrain_monitor",
              "position_field": "start",
              "class": "retrain-line",
              "circle": true,
              "circle_class": "retrain-point",
              "radius": 6
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-ADAPT-002.timeline",
          "window_id_field": "window",
          "start_field": "start",
          "end_field": "end",
          "window_role_field": "role"
        }
      },
      {
        "componentInstanceId": "CHART-ADAPT-002.comparison.0",
        "componentType": "reference_current_comparison",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "category_field": "metric",
          "series_fields": [
            "champion",
            "challenger"
          ],
          "series_labels": [
            "champion",
            "challenger"
          ],
          "series_classes": [
            "bar-champion",
            "bar-challenger"
          ],
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 14,
            "right": 32,
            "bottom": 36,
            "left": 112
          },
          "x_max": 1,
          "first_y": 32,
          "row_gap": 42,
          "bar_height": 13,
          "annotations": [
            {
              "text": "performance improves, latency needs review",
              "x": 244,
              "y": 18,
              "class": "callout-win"
            }
          ],
          "series_class_fields": [
            null,
            "challenger_class"
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-ADAPT-002.comparison",
          "category_field": "metric",
          "series_fields": [
            "champion",
            "challenger"
          ]
        }
      },
      {
        "componentInstanceId": "CHART-ADAPT-002.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label": "Champion drift alarm leads to retraining; challenger improves AUC/F1 with latency tradeoff.",
          "visual_code": "interpretation"
        },
        "dataBinding": {
          "source": "chart.CHART-ADAPT-002.summary"
        }
      }
    ],
    "data": {
      "chart.CHART-ADAPT-002.summary": [
        {
          "label": "pre AUC",
          "value": 0.74
        },
        {
          "label": "post AUC",
          "value": 0.86
        },
        {
          "label": "retrain",
          "value": 24,
          "displayValue": "t=24"
        }
      ],
      "chart.CHART-ADAPT-002.performance": [
        {
          "time": 1,
          "champion": 0.88,
          "challenger": null
        },
        {
          "time": 2,
          "champion": 0.88,
          "challenger": null
        },
        {
          "time": 3,
          "champion": 0.87,
          "challenger": null
        },
        {
          "time": 4,
          "champion": 0.87,
          "challenger": null
        },
        {
          "time": 5,
          "champion": 0.86,
          "challenger": null
        },
        {
          "time": 6,
          "champion": 0.86,
          "challenger": null
        },
        {
          "time": 7,
          "champion": 0.85,
          "challenger": null
        },
        {
          "time": 8,
          "champion": 0.84,
          "challenger": null
        },
        {
          "time": 9,
          "champion": 0.83,
          "challenger": null
        },
        {
          "time": 10,
          "champion": 0.82,
          "challenger": null
        },
        {
          "time": 11,
          "champion": 0.81,
          "challenger": null
        },
        {
          "time": 12,
          "champion": 0.79,
          "challenger": null
        },
        {
          "time": 13,
          "champion": 0.78,
          "challenger": null
        },
        {
          "time": 14,
          "champion": 0.77,
          "challenger": null
        },
        {
          "time": 15,
          "champion": 0.76,
          "challenger": null
        },
        {
          "time": 16,
          "champion": 0.75,
          "challenger": null
        },
        {
          "time": 17,
          "champion": 0.74,
          "challenger": null
        },
        {
          "time": 18,
          "champion": 0.74,
          "challenger": null
        },
        {
          "time": 19,
          "champion": 0.73,
          "challenger": null
        },
        {
          "time": 20,
          "champion": 0.73,
          "challenger": null
        },
        {
          "time": 21,
          "champion": 0.74,
          "challenger": 0.78
        },
        {
          "time": 22,
          "champion": 0.75,
          "challenger": 0.8
        },
        {
          "time": 23,
          "champion": 0.76,
          "challenger": 0.82
        },
        {
          "time": 24,
          "champion": 0.77,
          "challenger": 0.84
        },
        {
          "time": 25,
          "champion": 0.77,
          "challenger": 0.85
        },
        {
          "time": 26,
          "champion": 0.78,
          "challenger": 0.86
        },
        {
          "time": 27,
          "champion": 0.78,
          "challenger": 0.87
        },
        {
          "time": 28,
          "champion": 0.79,
          "challenger": 0.87
        },
        {
          "time": 29,
          "champion": 0.79,
          "challenger": 0.88
        },
        {
          "time": 30,
          "champion": 0.8,
          "challenger": 0.88
        },
        {
          "time": 31,
          "champion": 0.8,
          "challenger": 0.89
        },
        {
          "time": 32,
          "champion": 0.81,
          "challenger": 0.89
        }
      ],
      "chart.CHART-ADAPT-002.timeline": [
        {
          "window": "normal",
          "start": 1,
          "end": 13,
          "role": "normal"
        },
        {
          "window": "warning",
          "start": 13,
          "end": 18,
          "role": "warning"
        },
        {
          "window": "alarm",
          "start": 18,
          "end": 24,
          "role": "alarm"
        },
        {
          "window": "retrain_monitor",
          "start": 24,
          "end": 32,
          "role": "retrain_monitor"
        }
      ],
      "chart.CHART-ADAPT-002.comparison": [
        {
          "metric": "AUC",
          "champion": 0.77,
          "challenger": 0.87,
          "challenger_class": "bar-challenger"
        },
        {
          "metric": "F1",
          "champion": 0.7,
          "challenger": 0.82,
          "challenger_class": "bar-challenger"
        },
        {
          "metric": "latency",
          "champion": 0.46,
          "challenger": 0.53,
          "challenger_class": "bar-latency"
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-ANNOT-001",
    "title": "CHART-ANNOT-001 - 단방향 검정의 증가·감소 방향 판단 기준",
    "originalPath": "./drift_report_charts/chart_annot_001.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_annot_001",
      "displayName": "CHART-ANNOT-001 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 146px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "단측 방향 표시",
          "description": "이 예시는 direction이 upper이므로 index 12 부근의 D+ gap +0.11을 drift 증거로 읽고, 반대 lower gap -0.08은 참고 신호로만 본다.",
          "headerHeight": 62,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 16,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "상방/하방 검정",
          "description": "Upper/greater는 p=0.018로 drift candidate지만, lower/less는 p=0.214라 이 검정의 drift 근거로 계산하지 않는다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": -18,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "변형 사용 매트릭스",
          "description": "KS, Fisher, MWU, CUSUM, EWMA/GMA처럼 upper 또는 lower를 선언한 one-sided 변종에 붙여 읽는다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": -18,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "notes",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1,
          "className": "notes-area"
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-ANNOT-001.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-ANNOT-001.summary",
          "label_field": "label",
          "primary_metric_field": "value"
        }
      },
      {
        "componentInstanceId": "CHART-ANNOT-001.direction.0",
        "componentType": "performance_metric_view",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "time_field": "time",
          "value_field": "current",
          "secondary_value_field": "baseline",
          "y_min": 0,
          "y_max": 1,
          "line_class": "direction-current-line",
          "secondary_line_class": "direction-baseline-line",
          "show_points": true,
          "show_secondary_points": false,
          "point_sample_every": 3,
          "point_radius": 3,
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 30,
            "bottom": 62,
            "left": 58
          },
          "x_ticks": [
            1,
            4,
            8,
            12,
            16
          ],
          "y_ticks": [
            0,
            0.25,
            0.5,
            0.75,
            1
          ],
          "x_axis_label": "ordered value / threshold index",
          "y_axis_label": "cumulative probability",
          "horizontal_markers": [
            {
              "y": 0.5,
              "class": "neutral-line"
            }
          ],
          "fill_between": [
            {
              "x0": 10,
              "x1": 14,
              "upper_field": "current",
              "lower_field": "baseline",
              "class": "upper-fill"
            },
            {
              "x0": 4,
              "x1": 7,
              "upper_field": "baseline",
              "lower_field": "current",
              "class": "lower-fill"
            }
          ],
          "gap_markers": [
            {
              "x": 12,
              "upper_field": "current",
              "lower_field": "baseline",
              "class": "upper-line"
            },
            {
              "x": 5,
              "upper_field": "baseline",
              "lower_field": "current",
              "class": "lower-line"
            }
          ],
          "point_highlights": [
            {
              "x": 12,
              "field": "current",
              "class": "upper-point",
              "r": 6
            },
            {
              "x": 12,
              "field": "baseline",
              "class": "baseline-point",
              "r": 4
            },
            {
              "x": 5,
              "field": "current",
              "class": "lower-point",
              "r": 6
            },
            {
              "x": 5,
              "field": "baseline",
              "class": "baseline-point",
              "r": 4
            }
          ],
          "annotations": [
            {
              "text": "upper one-sided evidence: current > baseline",
              "x": 9.7,
              "y": 0.92,
              "class": "callout-upper"
            },
            {
              "text": "opposite direction is not counted",
              "x": 2.3,
              "y": 0.2,
              "class": "callout-lower"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-ANNOT-001.direction",
          "time_field": "time",
          "value_field": "current",
          "secondary_value_field": "baseline"
        }
      },
      {
        "componentInstanceId": "CHART-ANNOT-001.tests.0",
        "componentType": "decision_card",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "test_cards",
          "view_box": [
            472,
            185
          ],
          "caption": "One-sided test must match declared direction"
        },
        "dataBinding": {
          "source": "chart.CHART-ANNOT-001.tests"
        }
      },
      {
        "componentInstanceId": "CHART-ANNOT-001.matrix.0",
        "componentType": "matrix_view",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "matrix_style": "direction_dots",
          "x_field": "direction",
          "y_field": "method",
          "value_field": "active",
          "view_box": [
            472,
            185
          ],
          "caption": "annotation applies when variant declares one-sided direction"
        },
        "dataBinding": {
          "source": "chart.CHART-ANNOT-001.matrix",
          "x_field": "direction",
          "y_field": "method",
          "value_field": "active"
        }
      },
      {
        "componentInstanceId": "CHART-ANNOT-001.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-ANNOT-001.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-ANNOT-001.summary": [
        {
          "label": "direction",
          "value": 1,
          "displayValue": "upper"
        },
        {
          "label": "D+ gap",
          "value": 0.11,
          "displayValue": "+0.11"
        },
        {
          "label": "one-sided p",
          "value": 0.018,
          "displayValue": "0.018"
        }
      ],
      "chart.CHART-ANNOT-001.direction": [
        {
          "time": 1,
          "current": 0.08,
          "baseline": 0.12
        },
        {
          "time": 2,
          "current": 0.12,
          "baseline": 0.18
        },
        {
          "time": 3,
          "current": 0.17,
          "baseline": 0.24
        },
        {
          "time": 4,
          "current": 0.23,
          "baseline": 0.3
        },
        {
          "time": 5,
          "current": 0.3,
          "baseline": 0.38
        },
        {
          "time": 6,
          "current": 0.38,
          "baseline": 0.45
        },
        {
          "time": 7,
          "current": 0.46,
          "baseline": 0.52
        },
        {
          "time": 8,
          "current": 0.55,
          "baseline": 0.58
        },
        {
          "time": 9,
          "current": 0.63,
          "baseline": 0.64
        },
        {
          "time": 10,
          "current": 0.71,
          "baseline": 0.7
        },
        {
          "time": 11,
          "current": 0.79,
          "baseline": 0.75
        },
        {
          "time": 12,
          "current": 0.86,
          "baseline": 0.8
        },
        {
          "time": 13,
          "current": 0.91,
          "baseline": 0.84
        },
        {
          "time": 14,
          "current": 0.95,
          "baseline": 0.88
        },
        {
          "time": 15,
          "current": 0.98,
          "baseline": 0.91
        },
        {
          "time": 16,
          "current": 0.99,
          "baseline": 0.94
        }
      ],
      "chart.CHART-ANNOT-001.tests": [
        {
          "title": "상방/증가",
          "hypothesis": "H1: current is larger",
          "stat": "D+ = +0.11, p=0.018",
          "decision": "DRIFT CANDIDATE",
          "class": "decision-pass",
          "decision_class": "callout-upper"
        },
        {
          "title": "하방/감소",
          "hypothesis": "H1: current is smaller",
          "stat": "D- = -0.08, p=0.214",
          "decision": "not counted",
          "class": "decision-fail",
          "decision_class": "callout-lower"
        }
      ],
      "chart.CHART-ANNOT-001.matrix": [
        {
          "method": "KS",
          "direction": "upper",
          "active": 1
        },
        {
          "method": "KS",
          "direction": "lower",
          "active": 1
        },
        {
          "method": "KS",
          "direction": "two-sided",
          "active": 0
        },
        {
          "method": "Fisher",
          "direction": "upper",
          "active": 1
        },
        {
          "method": "Fisher",
          "direction": "lower",
          "active": 1
        },
        {
          "method": "Fisher",
          "direction": "two-sided",
          "active": 0
        },
        {
          "method": "MWU",
          "direction": "upper",
          "active": 1
        },
        {
          "method": "MWU",
          "direction": "lower",
          "active": 1
        },
        {
          "method": "MWU",
          "direction": "two-sided",
          "active": 0
        },
        {
          "method": "CUSUM",
          "direction": "upper",
          "active": 1
        },
        {
          "method": "CUSUM",
          "direction": "lower",
          "active": 1
        },
        {
          "method": "CUSUM",
          "direction": "two-sided",
          "active": 0
        },
        {
          "method": "EWMA",
          "direction": "upper",
          "active": 1
        },
        {
          "method": "EWMA",
          "direction": "lower",
          "active": 1
        },
        {
          "method": "EWMA",
          "direction": "two-sided",
          "active": 0
        }
      ],
      "chart.CHART-ANNOT-001.notes": [
        {
          "title": "해석",
          "text": "현재 상황은 one-sided 변종이 upper 방향을 선언한 상태에서 current 곡선이 baseline보다 커지는 구간을 drift 후보로 볼 수 있는지 판단하는 사례다. D+ gap은 +0.11이고 one-sided p-value는 0.018이므로 증가 방향 후보는 성립하지만, lower 방향 차이는 이 검정의 대립가설과 반대이므로 drift 증거로 계산하지 않는다.",
          "legend": [
            {
              "label": "baseline",
              "class": "swatch-baseline"
            },
            {
              "label": "current",
              "class": "swatch-current"
            },
            {
              "label": "upper direction",
              "class": "swatch-upper"
            },
            {
              "label": "lower direction",
              "class": "swatch-lower"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-ANNOT-002",
    "title": "CHART-ANNOT-002 - 근사 드리프트 점수의 오차와 안정성 점검",
    "originalPath": "./drift_report_charts/chart_annot_002.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_annot_002",
      "displayName": "CHART-ANNOT-002 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 146px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "근사 오차 대역",
          "description": "Exact/reference score와 approx score가 threshold 0.42 근처에서도 tolerance 0.04 안에서 같이 움직이는지 확인한다.",
          "headerHeight": 62,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 16,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "투영 안정성",
          "description": "Projection count가 16, 32일 때는 spread가 크지만 128 이상에서는 tolerance 0.04 아래로 안정화되는지 본다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "분위수 오차 상세",
          "description": "q25~q75 error는 target 0.03 안에 있지만 tail error 0.041은 초과하므로 tail 해석은 재검증한다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "notes",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1,
          "className": "notes-area"
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-ANNOT-002.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-ANNOT-002.summary",
          "label_field": "label",
          "primary_metric_field": "value"
        }
      },
      {
        "componentInstanceId": "CHART-ANNOT-002.error.0",
        "componentType": "performance_metric_view",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "time_field": "time",
          "value_field": "exact",
          "secondary_value_field": "approx",
          "y_min": 0,
          "y_max": 0.58,
          "line_class": "exact-line",
          "secondary_line_class": "approx-line",
          "primary_point_class": "exact-point",
          "secondary_point_class": "approx-point",
          "show_points": true,
          "show_secondary_points": true,
          "point_sample_every": 3,
          "secondary_point_radius": 3.5,
          "point_radius": 3.5,
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 30,
            "bottom": 62,
            "left": 58
          },
          "x_ticks": [
            1,
            4,
            8,
            12,
            16
          ],
          "y_ticks": [
            0,
            0.15,
            0.3,
            0.45
          ],
          "x_axis_label": "time window",
          "y_axis_label": "distance / statistic",
          "horizontal_markers": [
            {
              "y": 0.42,
              "class": "limit-line",
              "label": "drift threshold",
              "label_x": 1.3,
              "label_dy": -8,
              "label_class": "callout-annot"
            }
          ],
          "fill_between": [
            {
              "x0": 1,
              "x1": 16,
              "upper_field": "approx_upper",
              "lower_field": "approx_lower",
              "class": "band-fill"
            }
          ],
          "point_highlights": [
            {
              "x": 12,
              "field": "approx",
              "class": "warn-point",
              "r": 5
            }
          ],
          "annotations": [
            {
              "text": "approximation band within tolerance",
              "x": 6,
              "y": 0.54,
              "class": "ok-text-annot"
            },
            {
              "text": "threshold region requires exact check",
              "x": 10.5,
              "y": 0.47,
              "class": "callout-annot"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-ANNOT-002.error",
          "time_field": "time",
          "value_field": "exact",
          "secondary_value_field": "approx"
        }
      },
      {
        "componentInstanceId": "CHART-ANNOT-002.projection.0",
        "componentType": "bar_chart",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "vertical_threshold",
          "category_field": "count",
          "value_field": "spread",
          "threshold": 0.04,
          "threshold_label": "tolerance 0.04",
          "threshold_class": "tolerance-line",
          "bar_class": "bar-projection",
          "over_class": "bar-over",
          "y_max": 0.09,
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 20,
            "right": 30,
            "bottom": 38,
            "left": 58
          },
          "caption": "projection count",
          "annotations": [
            {
              "text": "128+ projections stable",
              "x": 257,
              "y": 46,
              "class": "ok-text-annot"
            }
          ],
          "first_y": 36,
          "bar_width": 34
        },
        "dataBinding": {
          "source": "chart.CHART-ANNOT-002.projection",
          "category_field": "count",
          "value_field": "spread"
        }
      },
      {
        "componentInstanceId": "CHART-ANNOT-002.quantile.0",
        "componentType": "bar_chart",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "horizontal_threshold",
          "category_field": "quantile",
          "value_field": "error",
          "threshold": 0.03,
          "threshold_label": "target 0.03",
          "threshold_class": "limit-line",
          "threshold_label_class": "callout-annot",
          "bar_class": "bar-error",
          "over_class": "bar-over",
          "x_max": 0.05,
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 24,
            "right": 40,
            "bottom": 38,
            "left": 88
          },
          "caption": "quantile absolute error",
          "first_y": 42,
          "row_gap": 27
        },
        "dataBinding": {
          "source": "chart.CHART-ANNOT-002.quantile",
          "category_field": "quantile",
          "value_field": "error"
        }
      },
      {
        "componentInstanceId": "CHART-ANNOT-002.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-ANNOT-002.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-ANNOT-002.summary": [
        {
          "label": "approx error",
          "value": 0.03,
          "displayValue": "0.03"
        },
        {
          "label": "projections",
          "value": 128,
          "displayValue": "128"
        },
        {
          "label": "q error max",
          "value": 0.022,
          "displayValue": "0.022"
        }
      ],
      "chart.CHART-ANNOT-002.error": [
        {
          "time": 1,
          "exact": 0.06,
          "approx": 0.05,
          "approx_upper": 0.09,
          "approx_lower": 0
        },
        {
          "time": 2,
          "exact": 0.07,
          "approx": 0.08,
          "approx_upper": 0.12,
          "approx_lower": 0
        },
        {
          "time": 3,
          "exact": 0.08,
          "approx": 0.07,
          "approx_upper": 0.11000000000000001,
          "approx_lower": 0
        },
        {
          "time": 4,
          "exact": 0.1,
          "approx": 0.11,
          "approx_upper": 0.15,
          "approx_lower": 0
        },
        {
          "time": 5,
          "exact": 0.11,
          "approx": 0.1,
          "approx_upper": 0.14,
          "approx_lower": 0
        },
        {
          "time": 6,
          "exact": 0.13,
          "approx": 0.14,
          "approx_upper": 0.18000000000000002,
          "approx_lower": 0
        },
        {
          "time": 7,
          "exact": 0.17,
          "approx": 0.16,
          "approx_upper": 0.2,
          "approx_lower": 0
        },
        {
          "time": 8,
          "exact": 0.22,
          "approx": 0.2,
          "approx_upper": 0.24000000000000002,
          "approx_lower": 0
        },
        {
          "time": 9,
          "exact": 0.28,
          "approx": 0.27,
          "approx_upper": 0.31,
          "approx_lower": 0
        },
        {
          "time": 10,
          "exact": 0.34,
          "approx": 0.33,
          "approx_upper": 0.37,
          "approx_lower": 0
        },
        {
          "time": 11,
          "exact": 0.39,
          "approx": 0.36,
          "approx_upper": 0.39999999999999997,
          "approx_lower": 0
        },
        {
          "time": 12,
          "exact": 0.43,
          "approx": 0.4,
          "approx_upper": 0.44,
          "approx_lower": 0
        },
        {
          "time": 13,
          "exact": 0.46,
          "approx": 0.44,
          "approx_upper": 0.48,
          "approx_lower": 0
        },
        {
          "time": 14,
          "exact": 0.49,
          "approx": 0.46,
          "approx_upper": 0.5,
          "approx_lower": 0
        },
        {
          "time": 15,
          "exact": 0.51,
          "approx": 0.48,
          "approx_upper": 0.52,
          "approx_lower": 0
        },
        {
          "time": 16,
          "exact": 0.52,
          "approx": 0.5,
          "approx_upper": 0.54,
          "approx_lower": 0
        }
      ],
      "chart.CHART-ANNOT-002.projection": [
        {
          "count": "16",
          "spread": 0.081
        },
        {
          "count": "32",
          "spread": 0.054
        },
        {
          "count": "64",
          "spread": 0.035
        },
        {
          "count": "128",
          "spread": 0.022
        },
        {
          "count": "256",
          "spread": 0.019
        }
      ],
      "chart.CHART-ANNOT-002.quantile": [
        {
          "quantile": "q25",
          "error": 0.014
        },
        {
          "quantile": "q50",
          "error": 0.018
        },
        {
          "quantile": "q75",
          "error": 0.022
        },
        {
          "quantile": "tail",
          "error": 0.041
        }
      ],
      "chart.CHART-ANNOT-002.notes": [
        {
          "title": "해석",
          "text": "현재 상황은 계산량을 줄이기 위해 exact score 대신 approximate, sliced, quantile 계산을 쓰는 사례다. 평균 근사 오차는 0.03이고 projection 128개부터 score spread가 안정화되지만, tail quantile error가 target을 넘기 때문에 tail-sensitive 결론은 exact 계산이나 projection 증가로 다시 확인해야 한다.",
          "legend": [
            {
              "label": "exact/reference",
              "class": "swatch-exact"
            },
            {
              "label": "approx/quantile",
              "class": "swatch-approx"
            },
            {
              "label": "error band",
              "class": "swatch-band"
            },
            {
              "label": "tolerance",
              "class": "swatch-limit"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-ANOM-001",
    "title": "CHART-ANOM-001 - 정상 영역 밖 샘플 증가와 이상치 드리프트 후보",
    "originalPath": "./drift_report_charts/chart_anom_001.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_anom_001",
      "displayName": "CHART-ANOM-001 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 146px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "이상 점수 분포",
          "description": "Current score 분포가 baseline보다 오른쪽으로 이동하고 threshold 0.62 초과 영역이 커지는지 확인한다.",
          "headerHeight": 62,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 16,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "이상 비율 추세",
          "description": "Outlier rate가 t=14에서 기준선 0.20을 넘고 최종 0.37까지 계속 상승하는지 읽는다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "차원축소 투영",
          "description": "빨간 outlier가 baseline 정상 cluster 밖의 current 영역에 모여 있는지 확인한다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "notes",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1,
          "className": "notes-area"
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-ANOM-001.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-ANOM-001.summary"
        }
      },
      {
        "componentInstanceId": "CHART-ANOM-001.score.0",
        "componentType": "distribution_view",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "distribution_style": "density_area",
          "x_field": "score",
          "primary_value_field": "baseline",
          "secondary_value_field": "current",
          "x_min": 0.05,
          "x_max": 0.9,
          "y_min": 0,
          "y_max": 44,
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 28,
            "bottom": 62,
            "left": 58
          },
          "x_ticks": [
            0.1,
            0.3,
            0.5,
            0.7,
            0.9
          ],
          "y_ticks": [
            0,
            10,
            20,
            30,
            40
          ],
          "x_axis_label": "anomaly score",
          "y_axis_label": "density",
          "vertical_markers": [
            {
              "x": 0.62,
              "class": "threshold-line",
              "label": "threshold 0.62",
              "label_y": 34,
              "label_class": "warning-text"
            }
          ],
          "annotations": [
            {
              "text": "current shifts into novelty region",
              "x": 0.36,
              "y": 41,
              "class": "warning-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-ANOM-001.score"
        }
      },
      {
        "componentInstanceId": "CHART-ANOM-001.rate.0",
        "componentType": "performance_metric_view",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "time_field": "time",
          "value_field": "rate",
          "y_min": 0,
          "y_max": 0.42,
          "line_class": "rate-line",
          "primary_point_class": "rate-point",
          "point_sample_every": 3,
          "point_radius": 4.2,
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 22,
            "bottom": 34,
            "left": 48
          },
          "x_ticks": [],
          "y_ticks": [
            0,
            0.2,
            0.4
          ],
          "x_axis_label": "time index",
          "y_axis_label": false,
          "horizontal_markers": [
            {
              "y": 0.2,
              "class": "threshold-line",
              "label": "rate threshold",
              "label_x": 12,
              "label_dy": -7,
              "label_class": "warning-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-ANOM-001.rate",
          "time_field": "time",
          "value_field": "rate"
        }
      },
      {
        "componentInstanceId": "CHART-ANOM-001.projection.0",
        "componentType": "projection_scatter",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "x",
          "y_field": "y",
          "group_field": "group",
          "x_min": -2.4,
          "x_max": 3,
          "y_min": -1.8,
          "y_max": 1.8,
          "y_ticks": [
            -1,
            0,
            1
          ],
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 24,
            "bottom": 42,
            "left": 44
          },
          "group_class_map": {
            "baseline": "base-dot",
            "current": "current-dot",
            "outlier": "outlier-dot"
          },
          "group_radius_map": {
            "baseline": 4,
            "current": 4,
            "outlier": 5
          },
          "x_axis_label": "projection-1",
          "x_tick_dy": 6,
          "axis_label_y": 164,
          "annotations": [
            {
              "text": "outliers outside baseline",
              "x": 0.45,
              "y": 1.45,
              "class": "callout"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-ANOM-001.projection",
          "x_field": "x",
          "y_field": "y",
          "group_field": "group"
        }
      },
      {
        "componentInstanceId": "CHART-ANOM-001.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-ANOM-001.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-ANOM-001.summary": [
        {
          "label": "outlier rate",
          "value": 0.37,
          "displayValue": "0.37"
        },
        {
          "label": "threshold",
          "value": 0.62,
          "displayValue": "0.62"
        },
        {
          "label": "alarm",
          "value": 14,
          "displayValue": "t=14"
        }
      ],
      "chart.CHART-ANOM-001.score": [
        {
          "score": 0.05,
          "baseline": 6,
          "current": 0
        },
        {
          "score": 0.1,
          "baseline": 14,
          "current": 1
        },
        {
          "score": 0.15,
          "baseline": 26,
          "current": 3
        },
        {
          "score": 0.2,
          "baseline": 36,
          "current": 6
        },
        {
          "score": 0.25,
          "baseline": 40,
          "current": 10
        },
        {
          "score": 0.3,
          "baseline": 34,
          "current": 15
        },
        {
          "score": 0.35,
          "baseline": 24,
          "current": 22
        },
        {
          "score": 0.4,
          "baseline": 14,
          "current": 29
        },
        {
          "score": 0.45,
          "baseline": 8,
          "current": 34
        },
        {
          "score": 0.5,
          "baseline": 4,
          "current": 37
        },
        {
          "score": 0.55,
          "baseline": 2,
          "current": 34
        },
        {
          "score": 0.6,
          "baseline": 1,
          "current": 28
        },
        {
          "score": 0.65,
          "baseline": 0,
          "current": 20
        },
        {
          "score": 0.7,
          "baseline": 0,
          "current": 13
        },
        {
          "score": 0.75,
          "baseline": 0,
          "current": 8
        },
        {
          "score": 0.8,
          "baseline": 0,
          "current": 5
        },
        {
          "score": 0.85,
          "baseline": 0,
          "current": 3
        },
        {
          "score": 0.9,
          "baseline": 0,
          "current": 1
        }
      ],
      "chart.CHART-ANOM-001.rate": [
        {
          "time": 1,
          "rate": 0.03
        },
        {
          "time": 2,
          "rate": 0.04
        },
        {
          "time": 3,
          "rate": 0.04
        },
        {
          "time": 4,
          "rate": 0.05
        },
        {
          "time": 5,
          "rate": 0.05
        },
        {
          "time": 6,
          "rate": 0.06
        },
        {
          "time": 7,
          "rate": 0.07
        },
        {
          "time": 8,
          "rate": 0.08
        },
        {
          "time": 9,
          "rate": 0.09
        },
        {
          "time": 10,
          "rate": 0.11
        },
        {
          "time": 11,
          "rate": 0.13
        },
        {
          "time": 12,
          "rate": 0.16
        },
        {
          "time": 13,
          "rate": 0.19
        },
        {
          "time": 14,
          "rate": 0.22
        },
        {
          "time": 15,
          "rate": 0.24
        },
        {
          "time": 16,
          "rate": 0.27
        },
        {
          "time": 17,
          "rate": 0.3
        },
        {
          "time": 18,
          "rate": 0.32
        },
        {
          "time": 19,
          "rate": 0.34
        },
        {
          "time": 20,
          "rate": 0.35
        },
        {
          "time": 21,
          "rate": 0.36
        },
        {
          "time": 22,
          "rate": 0.37
        },
        {
          "time": 23,
          "rate": 0.37
        },
        {
          "time": 24,
          "rate": 0.38
        }
      ],
      "chart.CHART-ANOM-001.projection": [
        {
          "x": -1.35,
          "y": -0.28,
          "group": "baseline"
        },
        {
          "x": 0.35,
          "y": 0.26,
          "group": "current"
        },
        {
          "x": -1.1111,
          "y": -0.3381,
          "group": "baseline"
        },
        {
          "x": 0.6571,
          "y": 0.2163,
          "group": "current"
        },
        {
          "x": -0.9263,
          "y": -0.416,
          "group": "baseline"
        },
        {
          "x": 0.8512,
          "y": 0.1329,
          "group": "current"
        },
        {
          "x": -0.8001,
          "y": -0.3843,
          "group": "baseline"
        },
        {
          "x": 0.985,
          "y": 0.101,
          "group": "current"
        },
        {
          "x": -0.683,
          "y": -0.2957,
          "group": "baseline"
        },
        {
          "x": 1.1993,
          "y": 0.1554,
          "group": "current"
        },
        {
          "x": -0.5171,
          "y": -0.2972,
          "group": "baseline"
        },
        {
          "x": 1.5172,
          "y": 0.2367,
          "group": "current"
        },
        {
          "x": -0.2896,
          "y": -0.3864,
          "group": "baseline"
        },
        {
          "x": 0.4299,
          "y": 0.416,
          "group": "current"
        },
        {
          "x": -1.304,
          "y": -0.2351,
          "group": "baseline"
        },
        {
          "x": 0.6055,
          "y": 0.3523,
          "group": "current"
        },
        {
          "x": -1.1007,
          "y": -0.1558,
          "group": "baseline"
        },
        {
          "x": 0.7438,
          "y": 0.2751,
          "group": "current"
        },
        {
          "x": -0.9612,
          "y": -0.1,
          "group": "baseline"
        },
        {
          "x": 0.979,
          "y": 0.2689,
          "group": "current"
        },
        {
          "x": -0.8481,
          "y": -0.1604,
          "group": "baseline"
        },
        {
          "x": 1.3036,
          "y": 0.3404,
          "group": "current"
        },
        {
          "x": -0.7,
          "y": -0.2367,
          "group": "baseline"
        },
        {
          "x": 1.5789,
          "y": 0.4115,
          "group": "current"
        },
        {
          "x": -0.4876,
          "y": -0.2022,
          "group": "baseline"
        },
        {
          "x": 0.3586,
          "y": 0.5645,
          "group": "current"
        },
        {
          "x": -0.2406,
          "y": -0.1143,
          "group": "baseline"
        },
        {
          "x": 0.5057,
          "y": 0.487,
          "group": "current"
        },
        {
          "x": -1.2807,
          "y": 0.0612,
          "group": "baseline"
        },
        {
          "x": 0.7616,
          "y": 0.4238,
          "group": "current"
        },
        {
          "x": -1.1245,
          "y": -0.0283,
          "group": "baseline"
        },
        {
          "x": 1.0884,
          "y": 0.4438,
          "group": "current"
        },
        {
          "x": -1.0102,
          "y": -0.0542,
          "group": "baseline"
        },
        {
          "x": 1.3443,
          "y": 0.5253,
          "group": "current"
        },
        {
          "x": -0.8773,
          "y": 0.0265,
          "group": "baseline"
        },
        {
          "x": 1.4913,
          "y": 0.5791,
          "group": "current"
        },
        {
          "x": -0.6826,
          "y": 0.0798,
          "group": "baseline"
        },
        {
          "x": 0.271,
          "y": 0.7065,
          "group": "current"
        },
        {
          "x": -0.4395,
          "y": 0.0172,
          "group": "baseline"
        },
        {
          "x": 0.5465,
          "y": 0.6231,
          "group": "current"
        },
        {
          "x": -0.2061,
          "y": -0.0574,
          "group": "baseline"
        },
        {
          "x": 0.871,
          "y": 0.58,
          "group": "current"
        },
        {
          "x": -1.2914,
          "y": 0.1599,
          "group": "baseline"
        },
        {
          "x": 1.1062,
          "y": 0.6243,
          "group": "current"
        },
        {
          "x": -1.1706,
          "y": 0.2471,
          "group": "baseline"
        },
        {
          "x": 1.2444,
          "y": 0.7077,
          "group": "current"
        },
        {
          "x": -1.0492,
          "y": 0.2396,
          "group": "baseline"
        },
        {
          "x": 1.4201,
          "y": 0.7389,
          "group": "current"
        },
        {
          "x": -0.8734,
          "y": 0.1497,
          "group": "baseline"
        },
        {
          "x": 0.3329,
          "y": 0.8439,
          "group": "current"
        },
        {
          "x": -0.6393,
          "y": 0.1267,
          "group": "baseline"
        },
        {
          "x": 0.6507,
          "y": 0.7628,
          "group": "current"
        },
        {
          "x": -0.3966,
          "y": 0.2088,
          "group": "baseline"
        },
        {
          "x": 0.865,
          "y": 0.7442,
          "group": "current"
        },
        {
          "x": -0.2031,
          "y": 0.2596,
          "group": "baseline"
        },
        {
          "x": 0.9987,
          "y": 0.8084,
          "group": "current"
        },
        {
          "x": -1.331,
          "y": 0.3749,
          "group": "baseline"
        },
        {
          "x": 1.1929,
          "y": 0.8853,
          "group": "current"
        },
        {
          "x": -1.2165,
          "y": 0.302,
          "group": "baseline"
        },
        {
          "x": 1.5001,
          "y": 0.8908,
          "group": "current"
        },
        {
          "x": -1.0592,
          "y": 0.342,
          "group": "baseline"
        },
        {
          "x": 0.4271,
          "y": 0.9789,
          "group": "current"
        },
        {
          "x": -0.8383,
          "y": 0.4285,
          "group": "baseline"
        },
        {
          "x": 0.6212,
          "y": 0.9082,
          "group": "current"
        },
        {
          "x": -0.5914,
          "y": 0.4179,
          "group": "baseline"
        },
        {
          "x": 0.7549,
          "y": 0.916,
          "group": "current"
        },
        {
          "x": -0.38,
          "y": 0.3278,
          "group": "baseline"
        },
        {
          "x": 0.9694,
          "y": 0.9937,
          "group": "current"
        },
        {
          "x": 1.68,
          "y": 0.8,
          "group": "outlier"
        },
        {
          "x": 1.9579,
          "y": 0.7414,
          "group": "outlier"
        },
        {
          "x": 2.0446,
          "y": 0.6514,
          "group": "outlier"
        },
        {
          "x": 2.2182,
          "y": 0.6619,
          "group": "outlier"
        },
        {
          "x": 2.5435,
          "y": 0.7575,
          "group": "outlier"
        },
        {
          "x": 1.713,
          "y": 0.9981,
          "group": "outlier"
        },
        {
          "x": 1.8015,
          "y": 0.9243,
          "group": "outlier"
        },
        {
          "x": 2.0827,
          "y": 0.8442,
          "group": "outlier"
        },
        {
          "x": 2.3573,
          "y": 0.8751,
          "group": "outlier"
        },
        {
          "x": 2.4422,
          "y": 0.9718,
          "group": "outlier"
        },
        {
          "x": 1.6199,
          "y": 1.1926,
          "group": "outlier"
        },
        {
          "x": 1.9451,
          "y": 1.107,
          "group": "outlier"
        },
        {
          "x": 2.1105,
          "y": 1.0405,
          "group": "outlier"
        }
      ],
      "chart.CHART-ANOM-001.notes": [
        {
          "title": "해석",
          "text": "현재 상황은 baseline 정상 영역을 학습한 novelty detector가 current sample 중 정상 영역 밖으로 벗어난 점들을 outlier로 표시하는 사례다. Current score 분포가 threshold 0.62 오른쪽으로 이동하고 outlier rate가 t=14 이후 기준선 0.20을 넘으며, projection에서도 outlier가 current cluster에 집중되므로 이상치 기반 drift 후보로 해석한다.",
          "legend": [
            {
              "label": "baseline normal",
              "class": "swatch-base"
            },
            {
              "label": "current normal",
              "class": "swatch-current"
            },
            {
              "label": "current outlier",
              "class": "swatch-outlier"
            },
            {
              "label": "threshold",
              "class": "swatch-threshold"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-BOCD-001",
    "title": "CHART-BOCD-001 - 베이지안 온라인 변화점 사후확률과 스트림 이동",
    "originalPath": "./drift_report_charts/chart_bocd_001.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_bocd_001",
      "displayName": "CHART-BOCD-001 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 146px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "변화점 확률 히트맵",
          "description": "t=18에서 change point probability가 0.87로 가장 높고, t=27에도 보조 peak가 나타나는지 읽는다.",
          "headerHeight": 62,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 16,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "런 길이 사후분포",
          "description": "t=18 변화점 후보에서 run length가 낮은 값으로 reset되는지 확인한다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "스트림 추세",
          "description": "stream 평균이 0.55에서 0.87, 다시 1.10 수준으로 이동하는지 본다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "interpretation",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-BOCD-001.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-BOCD-001.summary"
        }
      },
      {
        "componentInstanceId": "CHART-BOCD-001.cp_heatmap.0",
        "componentType": "heatmap",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "matrix_style": "heatmap_grid",
          "x_field": "time",
          "y_field": "row",
          "values_field": "values",
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 28,
            "bottom": 62,
            "left": 58
          },
          "x_values": [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
            27,
            28,
            29,
            30,
            31,
            32
          ],
          "y_values": [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12
          ],
          "value_min": 0,
          "value_max": 1,
          "palette": [
            [
              0,
              "#d9e6ef"
            ],
            [
              0.55,
              "#c9952f"
            ],
            [
              1,
              "#b95a50"
            ]
          ],
          "x_ticks": [
            1,
            8,
            16,
            24,
            32
          ],
          "y_min": 0,
          "y_max": 1,
          "y_ticks": [
            0,
            0.5,
            1
          ],
          "x_axis_label": "time index",
          "y_axis_label": "P(change point)",
          "cell_class": "cell",
          "vertical_markers": [
            {
              "x": 18,
              "class": "marker-line"
            },
            {
              "x": 27,
              "class": "marker-line",
              "opacity": 0.75
            }
          ],
          "annotations": [
            {
              "text": "posterior spike",
              "x": 15,
              "y": 0.93,
              "class": "warning-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-BOCD-001.cp_heatmap"
        }
      },
      {
        "componentInstanceId": "CHART-BOCD-001.run_length.0",
        "componentType": "heatmap",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "matrix_style": "heatmap_grid",
          "x_field": "time",
          "y_field": "row",
          "values_field": "values",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 22,
            "bottom": 34,
            "left": 48
          },
          "x_values": [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
            27,
            28,
            29,
            30,
            31,
            32
          ],
          "y_values": [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12
          ],
          "value_min": 0,
          "value_max": 1,
          "palette": [
            [
              0,
              "#d9e6ef"
            ],
            [
              0.55,
              "#c9952f"
            ],
            [
              1,
              "#b95a50"
            ]
          ],
          "x_ticks": [],
          "show_y_axis": false,
          "caption": "run length posterior resets",
          "vertical_markers": [
            {
              "x": 18,
              "class": "marker-line"
            }
          ],
          "annotations": [
            {
              "text": "reset",
              "x": 20,
              "y": 0.88,
              "class": "warning-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-BOCD-001.run_length"
        }
      },
      {
        "componentInstanceId": "CHART-BOCD-001.stream.0",
        "componentType": "trend_line",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "time",
          "time_field": "time",
          "value_field": "value",
          "y_field": "value",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 22,
            "bottom": 34,
            "left": 48
          },
          "y_min": 0.4,
          "y_max": 1.2,
          "y_ticks": [
            0.5,
            0.8,
            1.1
          ],
          "x_ticks": [],
          "x_axis_label": "stream with change markers",
          "axis_label_x": 204,
          "axis_label_y": 177,
          "y_axis_label": false,
          "line_class": "stream-line",
          "show_points": false,
          "horizontal_markers": [
            {
              "y": 0.55,
              "x0": 1,
              "x1": 18,
              "class": "mean-line"
            },
            {
              "y": 0.87,
              "x0": 18,
              "x1": 27,
              "class": "mean-line"
            },
            {
              "y": 1.1,
              "x0": 27,
              "x1": 32,
              "class": "mean-line"
            }
          ],
          "vertical_markers": [
            {
              "x": 18,
              "class": "marker-line"
            },
            {
              "x": 27,
              "class": "marker-line"
            }
          ],
          "point_highlights": [
            {
              "x": 18,
              "class": "marker-point",
              "r": 6
            },
            {
              "x": 27,
              "class": "marker-point",
              "r": 6
            }
          ],
          "annotations": [
            {
              "text": "mean shift",
              "x": 19,
              "y": 1.05,
              "class": "warning-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-BOCD-001.stream"
        }
      },
      {
        "componentInstanceId": "CHART-BOCD-001.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-BOCD-001.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-BOCD-001.summary": [
        {
          "label": "peak cp prob",
          "value": 0.87,
          "displayValue": "0.87"
        },
        {
          "label": "primary change",
          "value": 18,
          "displayValue": "t=18"
        },
        {
          "label": "run length",
          "value": 1,
          "displayValue": "reset"
        }
      ],
      "chart.CHART-BOCD-001.cp_heatmap": [
        {
          "row": 1,
          "values": [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0.135,
            0.597,
            0.813,
            0.597,
            0.135,
            0,
            0,
            0,
            0,
            0,
            0.179,
            0.384,
            0.179,
            0,
            0,
            0,
            0
          ]
        },
        {
          "row": 2,
          "values": [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0.189,
            0.651,
            0.867,
            0.651,
            0.189,
            0,
            0,
            0,
            0,
            0,
            0.233,
            0.438,
            0.233,
            0,
            0,
            0,
            0
          ]
        },
        {
          "row": 3,
          "values": [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0.244,
            0.705,
            0.819,
            0.705,
            0.244,
            0,
            0,
            0,
            0,
            0,
            0.288,
            0.492,
            0.288,
            0,
            0,
            0,
            0
          ]
        },
        {
          "row": 4,
          "values": [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0.298,
            0.719,
            0.765,
            0.719,
            0.298,
            0,
            0,
            0,
            0,
            0,
            0.342,
            0.546,
            0.342,
            0,
            0,
            0,
            0
          ]
        },
        {
          "row": 5,
          "values": [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0.352,
            0.665,
            0.711,
            0.665,
            0.352,
            0,
            0,
            0,
            0,
            0.016,
            0.396,
            0.6,
            0.396,
            0.016,
            0,
            0,
            0
          ]
        },
        {
          "row": 6,
          "values": [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0.014,
            0.406,
            0.611,
            0.657,
            0.611,
            0.406,
            0.014,
            0,
            0,
            0,
            0.071,
            0.45,
            0.566,
            0.45,
            0.07,
            0,
            0,
            0
          ]
        },
        {
          "row": 7,
          "values": [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0.068,
            0.459,
            0.557,
            0.602,
            0.557,
            0.459,
            0.068,
            0,
            0,
            0,
            0.125,
            0.468,
            0.511,
            0.468,
            0.125,
            0,
            0,
            0
          ]
        },
        {
          "row": 8,
          "values": [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0.122,
            0.405,
            0.503,
            0.548,
            0.503,
            0.405,
            0.122,
            0,
            0,
            0,
            0.179,
            0.414,
            0.457,
            0.414,
            0.179,
            0,
            0,
            0
          ]
        },
        {
          "row": 9,
          "values": [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0.177,
            0.35,
            0.448,
            0.494,
            0.448,
            0.35,
            0.177,
            0,
            0,
            0,
            0.233,
            0.36,
            0.403,
            0.36,
            0.233,
            0,
            0,
            0
          ]
        },
        {
          "row": 10,
          "values": [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0.031,
            0.213,
            0.296,
            0.394,
            0.44,
            0.394,
            0.296,
            0.213,
            0.033,
            0,
            0.047,
            0.225,
            0.306,
            0.349,
            0.306,
            0.225,
            0.044,
            0,
            0
          ]
        },
        {
          "row": 11,
          "values": [
            0.001,
            0.001,
            0.001,
            0.001,
            0.001,
            0.001,
            0.001,
            0.001,
            0.001,
            0.001,
            0.002,
            0.004,
            0.019,
            0.085,
            0.159,
            0.242,
            0.34,
            0.386,
            0.34,
            0.242,
            0.159,
            0.087,
            0.036,
            0.101,
            0.171,
            0.251,
            0.295,
            0.251,
            0.171,
            0.099,
            0.018,
            0.003
          ]
        },
        {
          "row": 12,
          "values": [
            0.045,
            0.045,
            0.045,
            0.045,
            0.045,
            0.045,
            0.045,
            0.045,
            0.045,
            0.045,
            0.045,
            0.045,
            0.048,
            0.062,
            0.105,
            0.188,
            0.286,
            0.332,
            0.286,
            0.188,
            0.105,
            0.063,
            0.052,
            0.066,
            0.117,
            0.197,
            0.241,
            0.197,
            0.117,
            0.065,
            0.048,
            0.045
          ]
        }
      ],
      "chart.CHART-BOCD-001.run_length": [
        {
          "row": 1,
          "values": [
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04
          ]
        },
        {
          "row": 2,
          "values": [
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04
          ]
        },
        {
          "row": 3,
          "values": [
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.042,
            0.059,
            0.082,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04
          ]
        },
        {
          "row": 4,
          "values": [
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.048,
            0.067,
            0.094,
            0.131,
            0.183,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04
          ]
        },
        {
          "row": 5,
          "values": [
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.055,
            0.077,
            0.108,
            0.15,
            0.21,
            0.293,
            0.408,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04
          ]
        },
        {
          "row": 6,
          "values": [
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.045,
            0.063,
            0.088,
            0.123,
            0.172,
            0.24,
            0.334,
            0.466,
            0.651,
            0.795,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.045,
            0.063,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04
          ]
        },
        {
          "row": 7,
          "values": [
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.052,
            0.072,
            0.101,
            0.141,
            0.196,
            0.274,
            0.382,
            0.533,
            0.744,
            0.696,
            0.499,
            0.357,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.052,
            0.072,
            0.101,
            0.141,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.052
          ]
        },
        {
          "row": 8,
          "values": [
            0.04,
            0.04,
            0.042,
            0.059,
            0.082,
            0.115,
            0.161,
            0.224,
            0.313,
            0.436,
            0.609,
            0.85,
            0.609,
            0.436,
            0.313,
            0.224,
            0.161,
            0.04,
            0.04,
            0.042,
            0.059,
            0.082,
            0.115,
            0.161,
            0.224,
            0.313,
            0.04,
            0.04,
            0.042,
            0.059,
            0.082,
            0.115
          ]
        },
        {
          "row": 9,
          "values": [
            0.048,
            0.067,
            0.094,
            0.131,
            0.183,
            0.256,
            0.357,
            0.499,
            0.696,
            0.744,
            0.533,
            0.382,
            0.274,
            0.196,
            0.141,
            0.101,
            0.072,
            0.048,
            0.067,
            0.094,
            0.131,
            0.183,
            0.256,
            0.357,
            0.499,
            0.696,
            0.048,
            0.067,
            0.094,
            0.131,
            0.183,
            0.256
          ]
        },
        {
          "row": 10,
          "values": [
            0.108,
            0.15,
            0.21,
            0.293,
            0.408,
            0.57,
            0.795,
            0.651,
            0.466,
            0.334,
            0.24,
            0.172,
            0.123,
            0.088,
            0.063,
            0.045,
            0.04,
            0.108,
            0.15,
            0.21,
            0.293,
            0.408,
            0.57,
            0.795,
            0.651,
            0.466,
            0.108,
            0.15,
            0.21,
            0.293,
            0.408,
            0.57
          ]
        },
        {
          "row": 11,
          "values": [
            0.24,
            0.334,
            0.466,
            0.651,
            0.795,
            0.57,
            0.408,
            0.293,
            0.21,
            0.15,
            0.108,
            0.077,
            0.055,
            0.04,
            0.04,
            0.04,
            0.04,
            1.04,
            0.334,
            0.466,
            0.651,
            0.795,
            0.57,
            0.408,
            0.293,
            0.21,
            1.04,
            0.334,
            0.466,
            0.651,
            0.795,
            0.57
          ]
        },
        {
          "row": 12,
          "values": [
            0.533,
            0.744,
            0.696,
            0.499,
            0.357,
            0.256,
            0.183,
            0.131,
            0.094,
            0.067,
            0.048,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            0.04,
            1.333,
            0.744,
            0.696,
            0.499,
            0.357,
            0.256,
            0.183,
            0.131,
            0.094,
            1.333,
            0.744,
            0.696,
            0.499,
            0.357,
            0.256
          ]
        }
      ],
      "chart.CHART-BOCD-001.stream": [
        {
          "time": 1,
          "value": 0.48
        },
        {
          "time": 2,
          "value": 0.51
        },
        {
          "time": 3,
          "value": 0.49
        },
        {
          "time": 4,
          "value": 0.52
        },
        {
          "time": 5,
          "value": 0.5
        },
        {
          "time": 6,
          "value": 0.53
        },
        {
          "time": 7,
          "value": 0.55
        },
        {
          "time": 8,
          "value": 0.54
        },
        {
          "time": 9,
          "value": 0.56
        },
        {
          "time": 10,
          "value": 0.57
        },
        {
          "time": 11,
          "value": 0.55
        },
        {
          "time": 12,
          "value": 0.58
        },
        {
          "time": 13,
          "value": 0.59
        },
        {
          "time": 14,
          "value": 0.6
        },
        {
          "time": 15,
          "value": 0.62
        },
        {
          "time": 16,
          "value": 0.63
        },
        {
          "time": 17,
          "value": 0.66
        },
        {
          "time": 18,
          "value": 0.79
        },
        {
          "time": 19,
          "value": 0.83
        },
        {
          "time": 20,
          "value": 0.86
        },
        {
          "time": 21,
          "value": 0.87
        },
        {
          "time": 22,
          "value": 0.89
        },
        {
          "time": 23,
          "value": 0.88
        },
        {
          "time": 24,
          "value": 0.91
        },
        {
          "time": 25,
          "value": 0.92
        },
        {
          "time": 26,
          "value": 0.94
        },
        {
          "time": 27,
          "value": 1.04
        },
        {
          "time": 28,
          "value": 1.07
        },
        {
          "time": 29,
          "value": 1.1
        },
        {
          "time": 30,
          "value": 1.12
        },
        {
          "time": 31,
          "value": 1.13
        },
        {
          "time": 32,
          "value": 1.15
        }
      ],
      "chart.CHART-BOCD-001.notes": [
        {
          "title": "해석",
          "text": "BOCD는 매 시점의 change point probability와 run length posterior를 갱신한다. 이 예시에서는 t=18에 posterior가 집중되고 run length가 reset되며 stream 수준이 0.55에서 0.87로 올라간다. t=27의 보조 peak와 추가 상승까지 함께 보이면 stream segment가 두 차례 바뀐 BOCD 기반 drift 후보로 해석한다. 단, 변화 원인과 모델 성능 영향은 별도 feature, segment, label 분석으로 확인해야 한다.",
          "legend": [
            {
              "label": "low posterior",
              "class": "swatch-low"
            },
            {
              "label": "medium",
              "class": "swatch-mid"
            },
            {
              "label": "high posterior",
              "class": "swatch-high"
            },
            {
              "label": "change marker",
              "class": "swatch-marker"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-CAT-001",
    "title": "CHART-CAT-001 - C/D 등급 증가와 A 등급 감소 범주 드리프트",
    "originalPath": "./drift_report_charts/chart_cat_001.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_cat_001",
      "displayName": "CHART-CAT-001 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 146px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "관측값과 기대값 비교",
          "description": "C등급은 176건 기대 대비 225건 관측되고 A등급은 132건 기대 대비 101건인지 본다.",
          "headerHeight": 62,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 16,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "표준화 잔차",
          "description": "C등급 +3.7, D등급 +2.6과 A등급 -2.7 잔차의 방향을 확인한다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "카이제곱 기여",
          "description": "C등급 기여도 13.6이 전체 통계량을 가장 크게 키우는지 읽는다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "interpretation",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-CAT-001.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-CAT-001.summary"
        }
      },
      {
        "componentInstanceId": "CHART-CAT-001.observed_expected.0",
        "componentType": "bar_chart",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "vertical_grouped",
          "category_field": "category",
          "series_fields": [
            "expected",
            "observed"
          ],
          "series_classes": [
            "expected-bar",
            "observed-bar"
          ],
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 20,
            "right": 22,
            "bottom": 58,
            "left": 62
          },
          "y_max": 250,
          "y_ticks": [
            0,
            63,
            125,
            188,
            250
          ],
          "x_axis_label": "category",
          "y_axis_label": "빈도",
          "group_padding": 12,
          "bar_gap": 5,
          "bar_radius": 3,
          "annotations": [
            {
              "text": "기여 최대: C등급",
              "x": 298,
              "y": 40,
              "class": "callout"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-CAT-001.categories"
        }
      },
      {
        "componentInstanceId": "CHART-CAT-001.residuals.0",
        "componentType": "matrix_view",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "matrix_style": "category_cells",
          "category_field": "category",
          "value_field": "residual",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 22,
            "bottom": 28,
            "left": 76
          },
          "cell_height": 48,
          "cell_gap": 3,
          "cell_radius": 6,
          "start_y": 48,
          "class_rules": [
            {
              "lt": -1.5,
              "class": "res-low"
            },
            {
              "gt": 1.5,
              "class": "res-high"
            },
            {
              "min": -1.5,
              "max": 1.5,
              "class": "res-neutral"
            }
          ],
          "labels": [
            {
              "text": "과소",
              "x": 76,
              "y": 34,
              "class": "axis-tick"
            },
            {
              "text": "과대",
              "x": 418,
              "y": 34,
              "class": "axis-tick"
            }
          ],
          "caption": "표준화 잔차 = (관측 - 기대) / sqrt(기대)",
          "caption_x": 76,
          "caption_y": 150
        },
        "dataBinding": {
          "source": "chart.CHART-CAT-001.categories"
        }
      },
      {
        "componentInstanceId": "CHART-CAT-001.contribution.0",
        "componentType": "contribution_view",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "horizontal_ranked",
          "category_field": "category",
          "value_field": "contribution",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 8,
            "right": 22,
            "bottom": 28,
            "left": 84
          },
          "limit": 5,
          "x_max": 16.1,
          "first_y": 18,
          "row_gap": 27,
          "bar_height": 16,
          "bar_radius": 4,
          "bar_class": "contrib-bar",
          "highlight_class": "contrib-highlight",
          "caption": "(O-E)^2 / E"
        },
        "dataBinding": {
          "source": "chart.CHART-CAT-001.categories"
        }
      },
      {
        "componentInstanceId": "CHART-CAT-001.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-CAT-001.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-CAT-001.summary": [
        {
          "label": "Chi-square",
          "value": 38.0,
          "displayValue": "38.0"
        },
        {
          "label": "df / p-value",
          "value": 0.003,
          "displayValue": "5 / 0.003"
        },
        {
          "label": "낮은 기대빈도",
          "value": 0,
          "displayValue": "0개"
        }
      ],
      "chart.CHART-CAT-001.categories": [
        {
          "category": "A등급",
          "expected": 132,
          "observed": 101,
          "residual": -2.7,
          "contribution": 7.3
        },
        {
          "category": "B등급",
          "expected": 210,
          "observed": 194,
          "residual": -1.1,
          "contribution": 1.2
        },
        {
          "category": "C등급",
          "expected": 176,
          "observed": 225,
          "residual": 3.7,
          "contribution": 13.6
        },
        {
          "category": "D등급",
          "expected": 112,
          "observed": 139,
          "residual": 2.6,
          "contribution": 6.5
        },
        {
          "category": "기타",
          "expected": 58,
          "observed": 39,
          "residual": -2.5,
          "contribution": 6.2
        },
        {
          "category": "미상",
          "expected": 32,
          "observed": 22,
          "residual": -1.8,
          "contribution": 3.1
        }
      ],
      "chart.CHART-CAT-001.notes": [
        {
          "title": "해석",
          "text": "이 예시에서는 C등급이 기대 176건보다 많은 225건, D등급이 기대 112건보다 많은 139건 관측된다. 반대로 A등급은 132건 기대 대비 101건으로 줄어든다. Chi-square 38.0, p-value 0.003, 낮은 기대빈도 0개이므로 A/기타/미상에서 C/D등급 쪽으로 이동한 범주형 drift 후보로 해석한다.",
          "legend": [
            {
              "label": "기대 빈도",
              "class": "swatch-expected"
            },
            {
              "label": "관측 빈도",
              "class": "swatch-observed"
            },
            {
              "label": "과대 관측",
              "class": "swatch-res-high"
            },
            {
              "label": "과소 관측",
              "class": "swatch-res-low"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-CAT-002",
    "title": "CHART-CAT-002 - 검색 감소와 구매 증가로 본 범주 구성 드리프트",
    "originalPath": "./drift_report_charts/chart_cat_002.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_cat_002",
      "displayName": "CHART-CAT-002 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 146px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "범주 비율 비교",
          "description": "검색은 0.26에서 0.18로 줄고 구매는 0.16에서 0.24로 늘어 탐색 단계 비중이 전환 단계로 이동했다.",
          "headerHeight": 62,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 16,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "절대 변화량",
          "description": "검색 -0.08과 구매 +0.08이 가장 큰 이동이며 장바구니 +0.04, 문의 -0.04가 뒤따른다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "총변동거리 추세",
          "description": "TV가 0.07에서 0.16까지 상승한 뒤 현재 0.15로 관리 기준선에 걸쳐 있다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "interpretation",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-CAT-002.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-CAT-002.summary"
        }
      },
      {
        "componentInstanceId": "CHART-CAT-002.proportion.0",
        "componentType": "proportion_view",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "vertical_grouped",
          "category_field": "category",
          "series_fields": [
            "reference",
            "current"
          ],
          "series_classes": [
            "ref-bar",
            "cur-bar"
          ],
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 20,
            "right": 22,
            "bottom": 70,
            "left": 58
          },
          "y_max": 0.3,
          "y_tick_max": 0.3,
          "y_ticks": [
            0,
            0.1,
            0.2,
            0.3
          ],
          "x_axis_label": "category",
          "y_axis_label": "비율",
          "group_padding": 8,
          "bar_gap": 4,
          "bar_radius": 3,
          "annotations": [
            {
              "text": "최대 이동: 검색 -0.08",
              "x": 288,
              "y": 40,
              "class": "callout"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-CAT-002.categories"
        }
      },
      {
        "componentInstanceId": "CHART-CAT-002.delta.0",
        "componentType": "contribution_view",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "horizontal_ranked",
          "category_field": "category",
          "value_field": "absDelta",
          "value_label_field": "deltaLabel",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 8,
            "right": 22,
            "bottom": 28,
            "left": 98
          },
          "limit": 7,
          "x_max": 0.098,
          "first_y": 13,
          "row_gap": 21,
          "bar_height": 14,
          "bar_radius": 4,
          "bar_class": "delta-bar",
          "highlight_class": "delta-highlight",
          "caption": "|현재 - 기준|"
        },
        "dataBinding": {
          "source": "chart.CHART-CAT-002.categories"
        }
      },
      {
        "componentInstanceId": "CHART-CAT-002.trend.0",
        "componentType": "trend_line",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "window",
          "time_field": "window",
          "value_field": "tv",
          "y_field": "tv",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 18,
            "bottom": 34,
            "left": 48
          },
          "y_min": 0,
          "y_max": 0.24,
          "y_ticks": [
            0,
            0.15,
            0.24
          ],
          "x_ticks": [],
          "x_axis_label": "window",
          "y_axis_label": false,
          "line_class": "trend-line",
          "primary_point_class": "trend-point",
          "point_sample_every": 1,
          "point_radius": 4,
          "horizontal_markers": [
            {
              "y": 0.15,
              "class": "threshold-line",
              "label": "관리 기준",
              "label_x": 6.0,
              "label_dy": -7,
              "label_class": "callout"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-CAT-002.trend"
        }
      },
      {
        "componentInstanceId": "CHART-CAT-002.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-CAT-002.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-CAT-002.summary": [
        {
          "label": "Total Variation",
          "value": 0.15,
          "displayValue": "0.150"
        },
        {
          "label": "총 절대 이동",
          "value": 0.3,
          "displayValue": "0.300"
        },
        {
          "label": "최대 Delta",
          "value": -0.08,
          "displayValue": "검색 -0.08"
        }
      ],
      "chart.CHART-CAT-002.categories": [
        {
          "category": "검색",
          "reference": 0.26,
          "current": 0.18,
          "delta": -0.08,
          "absDelta": 0.08,
          "deltaLabel": "0.08 (-0.08)"
        },
        {
          "category": "상세",
          "reference": 0.21,
          "current": 0.19,
          "delta": -0.02,
          "absDelta": 0.02,
          "deltaLabel": "0.02 (-0.02)"
        },
        {
          "category": "장바구니",
          "reference": 0.14,
          "current": 0.18,
          "delta": 0.04,
          "absDelta": 0.04,
          "deltaLabel": "0.04 (+0.04)"
        },
        {
          "category": "구매",
          "reference": 0.16,
          "current": 0.24,
          "delta": 0.08,
          "absDelta": 0.08,
          "deltaLabel": "0.08 (+0.08)"
        },
        {
          "category": "반품",
          "reference": 0.05,
          "current": 0.08,
          "delta": 0.03,
          "absDelta": 0.03,
          "deltaLabel": "0.03 (+0.03)"
        },
        {
          "category": "문의",
          "reference": 0.12,
          "current": 0.08,
          "delta": -0.04,
          "absDelta": 0.04,
          "deltaLabel": "0.04 (-0.04)"
        },
        {
          "category": "리뷰",
          "reference": 0.06,
          "current": 0.05,
          "delta": -0.01,
          "absDelta": 0.01,
          "deltaLabel": "0.01 (-0.01)"
        }
      ],
      "chart.CHART-CAT-002.trend": [
        {
          "window": 1,
          "tv": 0.07
        },
        {
          "window": 2,
          "tv": 0.08
        },
        {
          "window": 3,
          "tv": 0.1
        },
        {
          "window": 4,
          "tv": 0.12
        },
        {
          "window": 5,
          "tv": 0.14
        },
        {
          "window": 6,
          "tv": 0.16
        },
        {
          "window": 7,
          "tv": 0.15
        }
      ],
      "chart.CHART-CAT-002.notes": [
        {
          "title": "해석",
          "text": "이 예시에서는 Total Variation이 0.150, 총 절대 이동이 0.300이다. 검색 비율은 0.26에서 0.18로 0.08 감소했고 구매 비율은 0.16에서 0.24로 0.08 증가했다. TV 추세가 0.07에서 0.16까지 오른 뒤 현재 0.15 관리 기준선에 걸쳐 있으므로 단일 수치만이 아니라 검색 감소와 구매 증가가 함께 만든 category mix drift 후보로 읽는다.",
          "legend": [
            {
              "label": "기준 비율",
              "class": "swatch-reference"
            },
            {
              "label": "현재 비율",
              "class": "swatch-current-prop"
            },
            {
              "label": "절대 변화량",
              "class": "swatch-delta"
            },
            {
              "label": "관리 기준",
              "class": "swatch-threshold-line"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-CAT-003",
    "title": "CHART-CAT-003 - 검색 감소로 나타난 최대거리 범주 드리프트 신호",
    "originalPath": "./drift_report_charts/chart_cat_003.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_cat_003",
      "displayName": "CHART-CAT-003 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 146px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "범주 비율 비교",
          "description": "검색 비율이 기준 0.28에서 현재 0.16으로 줄어 가장 큰 단일 변화를 만든다.",
          "headerHeight": 62,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 16,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "최대 범주 변화량",
          "description": "|delta| 0.12인 검색 감소가 1순위다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "최대거리 추세",
          "description": "최근 window 값 0.12가 관리기준 0.10을 넘었다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "interpretation",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-CAT-003.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-CAT-003.summary"
        }
      },
      {
        "componentInstanceId": "CHART-CAT-003.proportion.0",
        "componentType": "proportion_view",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "vertical_grouped",
          "category_field": "category",
          "series_fields": [
            "reference",
            "current"
          ],
          "series_classes": [
            "ref-bar",
            "cur-bar"
          ],
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 20,
            "right": 22,
            "bottom": 70,
            "left": 58
          },
          "y_max": 0.32,
          "y_tick_max": 0.32,
          "y_ticks": [
            0,
            0.1,
            0.2,
            0.3
          ],
          "x_axis_label": "category",
          "y_axis_label": "비율",
          "group_padding": 8,
          "bar_gap": 4,
          "bar_radius": 3,
          "category_highlights": [
            {
              "category": "검색",
              "class": "highlight-band",
              "dx": 5,
              "rx": 8
            }
          ],
          "annotations": [
            {
              "text": "최대 변화: 검색 -0.12",
              "x": 278,
              "y": 40,
              "class": "callout"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-CAT-003.categories"
        }
      },
      {
        "componentInstanceId": "CHART-CAT-003.max_delta.0",
        "componentType": "contribution_view",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "horizontal_ranked",
          "category_field": "category",
          "value_field": "absDelta",
          "value_label_field": "deltaLabel",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 8,
            "right": 22,
            "bottom": 28,
            "left": 98
          },
          "limit": 7,
          "x_max": 0.146,
          "first_y": 13,
          "row_gap": 21,
          "bar_height": 14,
          "bar_radius": 4,
          "bar_class": "other-bar",
          "highlight_class": "max-bar",
          "caption": "max |현재 - 기준|"
        },
        "dataBinding": {
          "source": "chart.CHART-CAT-003.categories"
        }
      },
      {
        "componentInstanceId": "CHART-CAT-003.trend.0",
        "componentType": "trend_line",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "window",
          "time_field": "window",
          "value_field": "linf",
          "y_field": "linf",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 18,
            "bottom": 34,
            "left": 48
          },
          "y_min": 0,
          "y_max": 0.18,
          "y_ticks": [
            0,
            0.1,
            0.18
          ],
          "x_ticks": [],
          "x_axis_label": "window",
          "y_axis_label": false,
          "line_class": "trend-line",
          "primary_point_class": "trend-point",
          "point_sample_every": 1,
          "point_radius": 4,
          "horizontal_markers": [
            {
              "y": 0.1,
              "class": "threshold-line",
              "label": "관리 기준",
              "label_x": 6.0,
              "label_dy": -7,
              "label_class": "callout"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-CAT-003.trend"
        }
      },
      {
        "componentInstanceId": "CHART-CAT-003.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-CAT-003.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-CAT-003.summary": [
        {
          "label": "L-infinity",
          "value": 0.12,
          "displayValue": "0.120"
        },
        {
          "label": "최대 category",
          "value": 1,
          "displayValue": "검색"
        },
        {
          "label": "변화 방향",
          "value": -0.12,
          "displayValue": "감소 -0.12"
        }
      ],
      "chart.CHART-CAT-003.categories": [
        {
          "category": "검색",
          "reference": 0.28,
          "current": 0.16,
          "delta": -0.12,
          "absDelta": 0.12,
          "deltaLabel": "0.12 (-0.12)"
        },
        {
          "category": "상세",
          "reference": 0.2,
          "current": 0.19,
          "delta": -0.01,
          "absDelta": 0.01,
          "deltaLabel": "0.01 (-0.01)"
        },
        {
          "category": "장바구니",
          "reference": 0.13,
          "current": 0.15,
          "delta": 0.02,
          "absDelta": 0.02,
          "deltaLabel": "0.02 (+0.02)"
        },
        {
          "category": "구매",
          "reference": 0.15,
          "current": 0.23,
          "delta": 0.08,
          "absDelta": 0.08,
          "deltaLabel": "0.08 (+0.08)"
        },
        {
          "category": "반품",
          "reference": 0.05,
          "current": 0.08,
          "delta": 0.03,
          "absDelta": 0.03,
          "deltaLabel": "0.03 (+0.03)"
        },
        {
          "category": "문의",
          "reference": 0.13,
          "current": 0.12,
          "delta": -0.01,
          "absDelta": 0.01,
          "deltaLabel": "0.01 (-0.01)"
        },
        {
          "category": "리뷰",
          "reference": 0.06,
          "current": 0.07,
          "delta": 0.01,
          "absDelta": 0.01,
          "deltaLabel": "0.01 (+0.01)"
        }
      ],
      "chart.CHART-CAT-003.trend": [
        {
          "window": 1,
          "linf": 0.05
        },
        {
          "window": 2,
          "linf": 0.06
        },
        {
          "window": 3,
          "linf": 0.07
        },
        {
          "window": 4,
          "linf": 0.08
        },
        {
          "window": 5,
          "linf": 0.09
        },
        {
          "window": 6,
          "linf": 0.11
        },
        {
          "window": 7,
          "linf": 0.12
        }
      ],
      "chart.CHART-CAT-003.notes": [
        {
          "title": "해석",
          "text": "이 예시는 검색 category가 기준 0.28에서 현재 0.16으로 0.12 감소하면서 L-infinity 0.120을 만든다. 구매는 0.15에서 0.23으로 0.08 증가하지만 최대 변화는 검색 감소이며, 추세도 0.05에서 0.12까지 올라 관리기준 0.10을 넘었다. 따라서 전체 범주가 고르게 흔들린 상황보다 검색 유입 감소에 집중된 category drift 후보로 읽는다.",
          "legend": [
            {
              "label": "기준 비율",
              "class": "swatch-reference"
            },
            {
              "label": "현재 비율",
              "class": "swatch-current-prop"
            },
            {
              "label": "최대 Delta",
              "class": "swatch-max"
            },
            {
              "label": "관리 기준",
              "class": "swatch-threshold-line"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-CAT-004",
    "title": "CHART-CAT-004 - 피셔 검정으로 본 사건 비율 증가",
    "originalPath": "./drift_report_charts/chart_cat_004.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_cat_004",
      "displayName": "CHART-CAT-004 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 146px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "2x2 분할표 모자이크",
          "description": "기준 6/42, 현재 14/38로 event 비율이 14.3%에서 36.8%로 커졌는지 본다.",
          "headerHeight": 62,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 16,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "사건 비율 비교",
          "description": "현재 event rate가 기준보다 +22.6pp 높다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "Odds Ratio",
          "description": "OR 3.50, 95% CI [1.18, 10.4]가 null 1을 넘는지 확인한다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "interpretation",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-CAT-004.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-CAT-004.summary"
        }
      },
      {
        "componentInstanceId": "CHART-CAT-004.mosaic.0",
        "componentType": "matrix_view",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "matrix_style": "mosaic_2x2",
          "label_field": "label",
          "event_field": "event",
          "nonevent_field": "nonevent",
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 32,
            "right": 36,
            "bottom": 52,
            "left": 70
          },
          "row_gap": 28,
          "event_title": "Event",
          "nonevent_title": "Non-event",
          "current_label": "현재",
          "event_class": "event-fill",
          "nonevent_class": "nonevent-fill",
          "current_outline_class": "current-outline",
          "count_suffix": "건",
          "caption": "two-sided p=0.018, one-sided p=0.009"
        },
        "dataBinding": {
          "source": "chart.CHART-CAT-004.table"
        }
      },
      {
        "componentInstanceId": "CHART-CAT-004.rate.0",
        "componentType": "proportion_view",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "vertical_grouped",
          "category_field": "label",
          "category_sub_label_field": "eventLabel",
          "series_fields": [
            "rate"
          ],
          "series_class_fields": [
            "barClass"
          ],
          "value_label_fields": [
            "rateLabel"
          ],
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 8,
            "right": 26,
            "bottom": 35,
            "left": 54
          },
          "y_max": 0.45,
          "y_tick_max": 0.45,
          "y_ticks": [
            0,
            0.15,
            0.3,
            0.45
          ],
          "y_tick_format": "percent",
          "x_axis_label": "",
          "y_axis_label": "Event rate",
          "group_padding": 44,
          "bar_width": 72,
          "bar_radius": 5,
          "show_value_labels": true,
          "value_label_class": "title-text",
          "value_label_dy": -8,
          "category_sub_label_y": -8
        },
        "dataBinding": {
          "source": "chart.CHART-CAT-004.table"
        }
      },
      {
        "componentInstanceId": "CHART-CAT-004.forest.0",
        "componentType": "forest_plot",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "value_field": "oddsRatio",
          "low_field": "ciLow",
          "high_field": "ciHigh",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 20,
            "right": 28,
            "bottom": 42,
            "left": 60
          },
          "x_min": 0.3,
          "x_max": 12,
          "x_ticks": [
            0.5,
            1,
            2,
            4,
            8
          ],
          "null_value": 1,
          "null_label": "Null",
          "null_line_class": "threshold-line",
          "interval_class": "or-line",
          "point_class": "or-point",
          "point_radius": 8,
          "point_y": 82,
          "label": "OR 3.50  [1.18, 10.4]",
          "x_axis_label": "현재 event odds / 기준 event odds"
        },
        "dataBinding": {
          "source": "chart.CHART-CAT-004.forest"
        }
      },
      {
        "componentInstanceId": "CHART-CAT-004.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-CAT-004.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-CAT-004.summary": [
        {
          "label": "Fisher p-value",
          "value": 0.018,
          "displayValue": "0.018"
        },
        {
          "label": "Odds ratio",
          "value": 3.5,
          "displayValue": "3.50"
        },
        {
          "label": "Event rate 변화",
          "value": 0.226,
          "displayValue": "+22.6pp"
        }
      ],
      "chart.CHART-CAT-004.table": [
        {
          "label": "기준",
          "event": 6,
          "nonevent": 36,
          "rate": 0.142857,
          "rateLabel": "14.3%",
          "eventLabel": "event 6/42",
          "barClass": "ref-bar"
        },
        {
          "label": "현재",
          "event": 14,
          "nonevent": 24,
          "rate": 0.368421,
          "rateLabel": "36.8%",
          "eventLabel": "event 14/38",
          "barClass": "cur-bar"
        }
      ],
      "chart.CHART-CAT-004.forest": [
        {
          "oddsRatio": 3.5,
          "ciLow": 1.18,
          "ciHigh": 10.4
        }
      ],
      "chart.CHART-CAT-004.notes": [
        {
          "title": "해석",
          "text": "이 예시에서는 기준 구간 event가 6/42(14.3%)인 반면 현재 구간은 14/38(36.8%)이다. Fisher two-sided p-value 0.018과 one-sided p-value 0.009가 0.05보다 작고, odds ratio 3.50의 95% 신뢰구간 [1.18, 10.4]가 1을 벗어나므로 현재 구간 event 증가를 작은 표본 category drift 후보로 본다.",
          "legend": [
            {
              "label": "Event",
              "class": "swatch-event"
            },
            {
              "label": "Non-event",
              "class": "swatch-nonevent"
            },
            {
              "label": "현재 구간",
              "class": "swatch-current-prop"
            },
            {
              "label": "Null OR = 1",
              "class": "swatch-threshold-line"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-CLS-001",
    "title": "CHART-CLS-001 - 도메인 분류기 성능 곡선과 점수 분리",
    "originalPath": "./drift_report_charts/chart_cls_001.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_cls_001",
      "displayName": "CHART-CLS-001 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 146px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 0,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "도메인 분류기 성능 곡선",
          "description": "ROC-AUC 0.89로 classifier가 baseline/current sample을 구분한다.",
          "headerHeight": 62,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 16,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "점수 분포",
          "description": "baseline peak는 0.19/38, current peak는 0.68/36으로 분리된다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "중요도와 투영",
          "description": "emb_17 importance 0.31이 가장 높고 projection도 좌우로 분리된다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "interpretation",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-CLS-001.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-CLS-001.summary"
        }
      },
      {
        "componentInstanceId": "CHART-CLS-001.roc.0",
        "componentType": "model_diagnostic_curve",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "fpr",
          "y_field": "tpr",
          "x_min": 0,
          "x_max": 1,
          "y_min": 0,
          "y_max": 1,
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 30,
            "bottom": 62,
            "left": 58
          },
          "x_ticks": [
            0,
            0.25,
            0.5,
            0.75,
            1
          ],
          "y_ticks": [
            0,
            0.25,
            0.5,
            0.75,
            1
          ],
          "x_axis_label": "false positive rate",
          "y_axis_label": "true positive rate",
          "line_class": "roc-line",
          "primary_point_class": "current-dot",
          "point_sample_every": 2,
          "point_radius": 4,
          "area_under_line": {
            "class": "roc-fill",
            "baseline": 0
          },
          "diagonal_markers": [
            {
              "x0": 0,
              "y0": 0,
              "x1": 1,
              "y1": 1,
              "class": "random-line"
            }
          ],
          "annotations": [
            {
              "text": "domain classifier separates periods: AUC 0.89",
              "x": 0.22,
              "y": 0.92,
              "class": "callout-roc"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-CLS-001.roc"
        }
      },
      {
        "componentInstanceId": "CHART-CLS-001.scores.0",
        "componentType": "distribution_view",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "distribution_style": "density_area",
          "x_field": "score",
          "primary_value_field": "baseline",
          "secondary_value_field": "current",
          "x_min": 0.05,
          "x_max": 0.96,
          "y_min": 0,
          "y_max": 42,
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 14,
            "right": 24,
            "bottom": 34,
            "left": 46
          },
          "x_ticks": [
            0.05,
            0.5,
            0.96
          ],
          "y_ticks": [
            0,
            14,
            28,
            42
          ],
          "x_axis_label": "domain probability",
          "y_axis_label": false,
          "primary_area_class": "base-area",
          "secondary_area_class": "current-area",
          "vertical_markers": [
            {
              "x": 0.5,
              "class": "random-line"
            }
          ],
          "annotations": [
            {
              "text": "score distributions separated",
              "x": 0.36,
              "y": 38,
              "class": "callout-roc"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-CLS-001.scores"
        }
      },
      {
        "componentInstanceId": "CHART-CLS-001.importance_projection.0",
        "componentType": "feature_projection_view",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "kind_field": "kind",
          "feature_kind": "feature",
          "point_kind": "point",
          "feature_name_field": "feature",
          "feature_value_field": "value",
          "point_x_field": "x",
          "point_y_field": "y",
          "point_group_field": "group",
          "view_box": [
            472,
            185
          ],
          "feature_area": {
            "x": 72,
            "y": 24,
            "width": 180,
            "x_max": 0.34,
            "row_gap": 25,
            "bar_height": 15,
            "axis_y": 151
          },
          "projection_area": {
            "x0": 292,
            "x1": 452,
            "y0": 20,
            "y1": 151,
            "x_min": -1.7,
            "x_max": 2.3,
            "y_min": -1.2,
            "y_max": 1.4
          },
          "projection_frame": false,
          "feature_bar_class": "bar-feature",
          "point_radius": 4,
          "group_class_map": {
            "baseline": "base-dot",
            "current": "current-dot"
          },
          "labels": [
            {
              "text": "중요도",
              "x": 72,
              "y": 14,
              "class": "feature-text"
            },
            {
              "text": "투영",
              "x": 292,
              "y": 14,
              "class": "feature-text"
            }
          ],
          "annotations": [
            {
              "text": "emb_17 top",
              "x": 133,
              "y": 116,
              "class": "feature-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-CLS-001.importance_projection"
        }
      },
      {
        "componentInstanceId": "CHART-CLS-001.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-CLS-001.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-CLS-001.summary": [
        {
          "label": "ROC-AUC",
          "value": 0.89,
          "displayValue": "0.89"
        },
        {
          "label": "score gap",
          "value": 0.41,
          "displayValue": "0.41"
        },
        {
          "label": "top feature",
          "value": 0.31,
          "displayValue": "emb_17"
        }
      ],
      "chart.CHART-CLS-001.roc": [
        {
          "fpr": 0,
          "tpr": 0
        },
        {
          "fpr": 0.03,
          "tpr": 0.18
        },
        {
          "fpr": 0.07,
          "tpr": 0.34
        },
        {
          "fpr": 0.12,
          "tpr": 0.49
        },
        {
          "fpr": 0.2,
          "tpr": 0.64
        },
        {
          "fpr": 0.31,
          "tpr": 0.77
        },
        {
          "fpr": 0.46,
          "tpr": 0.87
        },
        {
          "fpr": 0.64,
          "tpr": 0.94
        },
        {
          "fpr": 0.82,
          "tpr": 0.98
        },
        {
          "fpr": 1,
          "tpr": 1
        }
      ],
      "chart.CHART-CLS-001.scores": [
        {
          "score": 0.05,
          "baseline": 26,
          "current": 0
        },
        {
          "score": 0.12,
          "baseline": 34,
          "current": 0
        },
        {
          "score": 0.19,
          "baseline": 38,
          "current": 1
        },
        {
          "score": 0.26,
          "baseline": 31,
          "current": 2
        },
        {
          "score": 0.33,
          "baseline": 22,
          "current": 5
        },
        {
          "score": 0.4,
          "baseline": 13,
          "current": 9
        },
        {
          "score": 0.47,
          "baseline": 7,
          "current": 15
        },
        {
          "score": 0.54,
          "baseline": 3,
          "current": 23
        },
        {
          "score": 0.61,
          "baseline": 1,
          "current": 31
        },
        {
          "score": 0.68,
          "baseline": 0,
          "current": 36
        },
        {
          "score": 0.75,
          "baseline": 0,
          "current": 33
        },
        {
          "score": 0.82,
          "baseline": 0,
          "current": 24
        },
        {
          "score": 0.89,
          "baseline": 0,
          "current": 13
        },
        {
          "score": 0.96,
          "baseline": 0,
          "current": 5
        }
      ],
      "chart.CHART-CLS-001.importance_projection": [
        {
          "kind": "feature",
          "feature": "emb_17",
          "value": 0.31,
          "displayValue": "0.31"
        },
        {
          "kind": "feature",
          "feature": "emb_04",
          "value": 0.24,
          "displayValue": "0.24"
        },
        {
          "kind": "feature",
          "feature": "emb_22",
          "value": 0.19,
          "displayValue": "0.19"
        },
        {
          "kind": "feature",
          "feature": "emb_09",
          "value": 0.14,
          "displayValue": "0.14"
        },
        {
          "kind": "point",
          "group": "baseline",
          "x": -1.0,
          "y": -0.23
        },
        {
          "kind": "point",
          "group": "current",
          "x": 0.55,
          "y": 0.15
        },
        {
          "kind": "point",
          "group": "baseline",
          "x": -0.828,
          "y": -0.253
        },
        {
          "kind": "point",
          "group": "current",
          "x": 0.769,
          "y": 0.118
        },
        {
          "kind": "point",
          "group": "baseline",
          "x": -0.695,
          "y": -0.301
        },
        {
          "kind": "point",
          "group": "current",
          "x": 0.907,
          "y": 0.063
        },
        {
          "kind": "point",
          "group": "baseline",
          "x": -0.603,
          "y": -0.329
        },
        {
          "kind": "point",
          "group": "current",
          "x": 1.016,
          "y": 0.055
        },
        {
          "kind": "point",
          "group": "baseline",
          "x": -0.518,
          "y": -0.313
        },
        {
          "kind": "point",
          "group": "current",
          "x": 1.198,
          "y": 0.104
        },
        {
          "kind": "point",
          "group": "baseline",
          "x": -0.398,
          "y": -0.266
        },
        {
          "kind": "point",
          "group": "current",
          "x": 1.433,
          "y": 0.148
        },
        {
          "kind": "point",
          "group": "baseline",
          "x": -1.014,
          "y": -0.082
        },
        {
          "kind": "point",
          "group": "current",
          "x": 0.593,
          "y": 0.29
        },
        {
          "kind": "point",
          "group": "baseline",
          "x": -0.837,
          "y": -0.092
        },
        {
          "kind": "point",
          "group": "current",
          "x": 0.702,
          "y": 0.234
        },
        {
          "kind": "point",
          "group": "baseline",
          "x": -0.691,
          "y": -0.137
        },
        {
          "kind": "point",
          "group": "current",
          "x": 0.841,
          "y": 0.211
        },
        {
          "kind": "point",
          "group": "baseline",
          "x": -0.589,
          "y": -0.176
        },
        {
          "kind": "point",
          "group": "current",
          "x": 1.062,
          "y": 0.25
        },
        {
          "kind": "point",
          "group": "baseline",
          "x": -0.507,
          "y": -0.172
        },
        {
          "kind": "point",
          "group": "current",
          "x": 1.28,
          "y": 0.302
        },
        {
          "kind": "point",
          "group": "baseline",
          "x": -0.4,
          "y": -0.13
        },
        {
          "kind": "point",
          "group": "current",
          "x": 1.415,
          "y": 0.3
        },
        {
          "kind": "point",
          "group": "baseline",
          "x": -1.027,
          "y": 0.062
        },
        {
          "kind": "point",
          "group": "current",
          "x": 0.506,
          "y": 0.407
        },
        {
          "kind": "point",
          "group": "baseline",
          "x": -0.849,
          "y": 0.065
        },
        {
          "kind": "point",
          "group": "current",
          "x": 0.69,
          "y": 0.37
        },
        {
          "kind": "point",
          "group": "baseline",
          "x": -0.69,
          "y": 0.027
        },
        {
          "kind": "point",
          "group": "current",
          "x": 0.924,
          "y": 0.397
        },
        {
          "kind": "point",
          "group": "baseline",
          "x": -0.577,
          "y": -0.018
        },
        {
          "kind": "point",
          "group": "current",
          "x": 1.102,
          "y": 0.453
        },
        {
          "kind": "point",
          "group": "baseline",
          "x": -0.494,
          "y": -0.028
        },
        {
          "kind": "point",
          "group": "current",
          "x": 1.21,
          "y": 0.467
        },
        {
          "kind": "point",
          "group": "baseline",
          "x": -0.398,
          "y": 0.006
        },
        {
          "kind": "point",
          "group": "current",
          "x": 1.351,
          "y": 0.421
        },
        {
          "kind": "point",
          "group": "baseline",
          "x": -1.038,
          "y": 0.203
        },
        {
          "kind": "point",
          "group": "current",
          "x": 0.553,
          "y": 0.534
        },
        {
          "kind": "point",
          "group": "baseline",
          "x": -0.863,
          "y": 0.219
        },
        {
          "kind": "point",
          "group": "current",
          "x": 0.77,
          "y": 0.545
        },
        {
          "kind": "point",
          "group": "baseline",
          "x": -0.694,
          "y": 0.19
        },
        {
          "kind": "point",
          "group": "current",
          "x": 0.904,
          "y": 0.601
        },
        {
          "kind": "point",
          "group": "baseline",
          "x": -0.568,
          "y": 0.143
        },
        {
          "kind": "point",
          "group": "current",
          "x": 1.015,
          "y": 0.63
        },
        {
          "kind": "point",
          "group": "baseline",
          "x": -0.48,
          "y": 0.12
        },
        {
          "kind": "point",
          "group": "current",
          "x": 1.201,
          "y": 0.595
        },
        {
          "kind": "point",
          "group": "baseline",
          "x": -0.392,
          "y": 0.143
        },
        {
          "kind": "point",
          "group": "current",
          "x": 1.435,
          "y": 0.541
        }
      ],
      "chart.CHART-CLS-001.notes": [
        {
          "title": "해석",
          "text": "Domain classifier가 baseline과 current를 높은 ROC-AUC로 구분하고 score distribution이 분리되면 embedding 또는 feature space drift 후보로 해석한다. 이 예시에서는 emb_17 0.31과 score gap 0.41이 함께 나타나 classifier-based drift 설명력이 높아진다.",
          "legend": [
            {
              "label": "baseline",
              "class": "swatch-base"
            },
            {
              "label": "current",
              "class": "swatch-current"
            },
            {
              "label": "ROC curve",
              "class": "swatch-roc"
            },
            {
              "label": "feature importance",
              "class": "swatch-feature"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-CTRL-001",
    "title": "CHART-CTRL-001 - 누적 편차로 확인하는 상방 평균 이동 경보",
    "originalPath": "./drift_report_charts/chart_ctrl_001.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_ctrl_001",
      "displayName": "CHART-CTRL-001 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 146px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "원시 지표 추세",
          "description": "target 0.53 주변에서 시작한 metric이 t=16 이후 0.60 이상으로 올라가고 t=25에서 alarm이 찍히는지 본다.",
          "headerHeight": 62,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 16,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "CUSUM 관리도",
          "description": "C+가 control limit 25를 넘어 52.9까지 누적되고 C-는 0.1 수준에 머무는지 확인한다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "방향 요약",
          "description": "C+ 막대가 C-보다 압도적으로 커서 상방 평균 이동이 지배적인지 읽는다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "interpretation",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-CTRL-001.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-CTRL-001.summary"
        }
      },
      {
        "componentInstanceId": "CHART-CTRL-001.raw.0",
        "componentType": "raw_signal_trend",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "time",
          "y_field": "raw",
          "x_min": 1,
          "x_max": 32,
          "y_min": 0.45,
          "y_max": 0.9,
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 28,
            "bottom": 62,
            "left": 58
          },
          "x_ticks": [
            1,
            8,
            16,
            24,
            32
          ],
          "y_ticks": [
            0.5,
            0.6,
            0.7,
            0.8,
            0.9
          ],
          "x_axis_label": "time index",
          "y_axis_label": "metric",
          "line_class": "raw-line",
          "show_points": false,
          "horizontal_markers": [
            {
              "y": 0.53,
              "class": "target-line",
              "label": "target 0.53",
              "label_class": "callout",
              "label_x": 2,
              "label_dy": -8
            }
          ],
          "vertical_markers": [
            {
              "x": 25,
              "class": "cusum-alarm-line"
            }
          ],
          "point_highlights": [
            {
              "x": 25,
              "class": "cusum-alarm-point",
              "r": 7
            }
          ],
          "annotations": [
            {
              "text": "상방 CUSUM alarm",
              "x": 25.5,
              "y": 0.82,
              "class": "warning-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-CTRL-001.series"
        }
      },
      {
        "componentInstanceId": "CHART-CTRL-001.cusum.0",
        "componentType": "control_chart",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "time",
          "y_field": "cplus",
          "secondary_value_field": "cminus",
          "x_min": 1,
          "x_max": 32,
          "y_min": 0,
          "y_max": 56,
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 22,
            "bottom": 34,
            "left": 48
          },
          "x_ticks": [],
          "y_ticks": [
            0,
            20,
            40
          ],
          "x_axis_label": "time index",
          "axis_label_x": 208,
          "axis_label_y": 177,
          "y_axis_label": false,
          "line_class": "pos-line",
          "secondary_line_class": "neg-line",
          "primary_point_class": "pos-point",
          "point_sample_every": 3,
          "point_radius": 3.4,
          "show_secondary_points": false,
          "horizontal_markers": [
            {
              "y": 25,
              "class": "cusum-limit-line",
              "label": "control limit 25",
              "label_class": "warning-text",
              "label_x": 23.5,
              "label_dy": -6
            }
          ],
          "point_highlights": [
            {
              "x": 25,
              "class": "cusum-alarm-point",
              "r": 4.6
            },
            {
              "x": 26,
              "class": "cusum-alarm-point",
              "r": 4.6
            },
            {
              "x": 27,
              "class": "cusum-alarm-point",
              "r": 4.6
            },
            {
              "x": 28,
              "class": "cusum-alarm-point",
              "r": 4.6
            },
            {
              "x": 29,
              "class": "cusum-alarm-point",
              "r": 4.6
            },
            {
              "x": 30,
              "class": "cusum-alarm-point",
              "r": 4.6
            },
            {
              "x": 31,
              "class": "cusum-alarm-point",
              "r": 4.6
            },
            {
              "x": 32,
              "class": "cusum-alarm-point",
              "r": 4.6
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-CTRL-001.series"
        }
      },
      {
        "componentInstanceId": "CHART-CTRL-001.direction.0",
        "componentType": "ranking_view",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "horizontal_threshold",
          "category_field": "label",
          "value_field": "value",
          "threshold": 25,
          "threshold_class": "cusum-limit-line",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 18,
            "right": 32,
            "bottom": 34,
            "left": 86
          },
          "x_max": 60,
          "first_y": 34,
          "row_gap": 48,
          "bar_height": 22,
          "caption": "상방 변화가 지배적"
        },
        "dataBinding": {
          "source": "chart.CHART-CTRL-001.direction"
        }
      },
      {
        "componentInstanceId": "CHART-CTRL-001.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-CTRL-001.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-CTRL-001.summary": [
        {
          "label": "C+ max",
          "value": 52.9,
          "displayValue": "52.9"
        },
        {
          "label": "C- max",
          "value": 0.1,
          "displayValue": "0.1"
        },
        {
          "label": "shift",
          "value": 0.29,
          "displayValue": "+0.29"
        }
      ],
      "chart.CHART-CTRL-001.series": [
        {
          "time": 1,
          "raw": 0.5,
          "cplus": 0,
          "cminus": 0
        },
        {
          "time": 2,
          "raw": 0.49,
          "cplus": 0,
          "cminus": 0.1
        },
        {
          "time": 3,
          "raw": 0.51,
          "cplus": 0.1,
          "cminus": 0
        },
        {
          "time": 4,
          "raw": 0.5,
          "cplus": 0.1,
          "cminus": 0
        },
        {
          "time": 5,
          "raw": 0.52,
          "cplus": 0.3,
          "cminus": 0
        },
        {
          "time": 6,
          "raw": 0.51,
          "cplus": 0.4,
          "cminus": 0
        },
        {
          "time": 7,
          "raw": 0.53,
          "cplus": 0.7,
          "cminus": 0
        },
        {
          "time": 8,
          "raw": 0.52,
          "cplus": 0.9,
          "cminus": 0
        },
        {
          "time": 9,
          "raw": 0.54,
          "cplus": 1.3,
          "cminus": 0
        },
        {
          "time": 10,
          "raw": 0.53,
          "cplus": 1.6,
          "cminus": 0
        },
        {
          "time": 11,
          "raw": 0.55,
          "cplus": 2.1,
          "cminus": 0
        },
        {
          "time": 12,
          "raw": 0.56,
          "cplus": 2.7,
          "cminus": 0
        },
        {
          "time": 13,
          "raw": 0.54,
          "cplus": 3.0,
          "cminus": 0
        },
        {
          "time": 14,
          "raw": 0.57,
          "cplus": 3.8,
          "cminus": 0
        },
        {
          "time": 15,
          "raw": 0.58,
          "cplus": 4.7,
          "cminus": 0
        },
        {
          "time": 16,
          "raw": 0.6,
          "cplus": 5.8,
          "cminus": 0
        },
        {
          "time": 17,
          "raw": 0.62,
          "cplus": 7.1,
          "cminus": 0
        },
        {
          "time": 18,
          "raw": 0.63,
          "cplus": 8.5,
          "cminus": 0
        },
        {
          "time": 19,
          "raw": 0.65,
          "cplus": 10.2,
          "cminus": 0
        },
        {
          "time": 20,
          "raw": 0.67,
          "cplus": 12.1,
          "cminus": 0
        },
        {
          "time": 21,
          "raw": 0.7,
          "cplus": 14.5,
          "cminus": 0
        },
        {
          "time": 22,
          "raw": 0.72,
          "cplus": 17.1,
          "cminus": 0
        },
        {
          "time": 23,
          "raw": 0.73,
          "cplus": 19.8,
          "cminus": 0
        },
        {
          "time": 24,
          "raw": 0.75,
          "cplus": 22.8,
          "cminus": 0
        },
        {
          "time": 25,
          "raw": 0.76,
          "cplus": 25.9,
          "cminus": 0
        },
        {
          "time": 26,
          "raw": 0.78,
          "cplus": 29.3,
          "cminus": 0
        },
        {
          "time": 27,
          "raw": 0.8,
          "cplus": 33.0,
          "cminus": 0
        },
        {
          "time": 28,
          "raw": 0.79,
          "cplus": 36.4,
          "cminus": 0
        },
        {
          "time": 29,
          "raw": 0.82,
          "cplus": 40.2,
          "cminus": 0
        },
        {
          "time": 30,
          "raw": 0.83,
          "cplus": 44.2,
          "cminus": 0
        },
        {
          "time": 31,
          "raw": 0.84,
          "cplus": 48.4,
          "cminus": 0
        },
        {
          "time": 32,
          "raw": 0.86,
          "cplus": 52.9,
          "cminus": 0
        }
      ],
      "chart.CHART-CTRL-001.direction": [
        {
          "label": "C+ 상방",
          "value": 52.9,
          "class": "bar-pos"
        },
        {
          "label": "C- 하방",
          "value": 0.1,
          "class": "bar-neg"
        }
      ],
      "chart.CHART-CTRL-001.notes": [
        {
          "title": "해석",
          "text": "CUSUM은 기준 평균에서 작게 반복되는 편차를 누적해 빠른 평균 shift를 감지한다. 이 예시에서는 raw metric이 target 0.53보다 계속 높아지고 C+가 control limit 25를 넘어 52.9까지 증가한다. C-는 0.1 수준이라 하방 변화 신호는 약하므로, 상방 평균 이동에 의한 CUSUM drift 후보로 해석한다. 단, target mean과 CUSUM 설정값, seasonality를 확인하지 않고 원인이나 성능 저하를 단정하지 않는다.",
          "legend": [
            {
              "label": "raw metric",
              "class": "swatch-raw"
            },
            {
              "label": "C+ CUSUM",
              "class": "swatch-pos"
            },
            {
              "label": "C- CUSUM",
              "class": "swatch-neg"
            },
            {
              "label": "control limit",
              "class": "swatch-control-limit"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-CTRL-002",
    "title": "CHART-CTRL-002 - EWMA 평활화로 확인하는 점진적 상방 평균 이동",
    "originalPath": "./drift_report_charts/chart_ctrl_002.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_ctrl_002",
      "displayName": "CHART-CTRL-002 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 146px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "원시 지표와 평활 평균",
          "description": "raw metric은 흔들리지만 EWMA가 t=16 이후 0.56에서 0.80까지 점진적으로 상승하는지 본다.",
          "headerHeight": 62,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 16,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "EWMA 관리도",
          "description": "EWMA가 UCL 0.72를 t=27 부근부터 넘고 final 0.80까지 올라가는지 확인한다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "경보 타임라인",
          "description": "normal(t=1~20)에서 warning(t=21~26)을 거쳐 alarm(t=27 이후)으로 이어지는지 읽는다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "interpretation",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-CTRL-002.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-CTRL-002.summary"
        }
      },
      {
        "componentInstanceId": "CHART-CTRL-002.raw_ewma.0",
        "componentType": "raw_signal_trend",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "time",
          "y_field": "raw",
          "secondary_value_field": "ewma",
          "x_min": 1,
          "x_max": 32,
          "y_min": 0.25,
          "y_max": 0.85,
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 28,
            "bottom": 62,
            "left": 58
          },
          "x_ticks": [
            1,
            8,
            16,
            24,
            32
          ],
          "y_ticks": [
            0.3,
            0.5,
            0.7
          ],
          "x_axis_label": "time index",
          "y_axis_label": "metric",
          "line_class": "raw-noise-line",
          "secondary_line_class": "smooth-line",
          "show_points": false,
          "show_secondary_points": false,
          "horizontal_markers": [
            {
              "y": 0.5,
              "class": "center-line"
            }
          ],
          "vertical_markers": [
            {
              "x": 27,
              "class": "ewma-alarm-line"
            }
          ],
          "point_highlights": [
            {
              "x": 27,
              "field": "ewma",
              "class": "ewma-alarm-point",
              "r": 7
            }
          ],
          "annotations": [
            {
              "text": "EWMA가 raw noise를 완화해 상승 추세를 포착",
              "x": 10,
              "y": 0.8,
              "class": "callout"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-CTRL-002.series"
        }
      },
      {
        "componentInstanceId": "CHART-CTRL-002.control.0",
        "componentType": "control_chart",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "time",
          "y_field": "ewma",
          "x_min": 1,
          "x_max": 32,
          "y_min": 0.2,
          "y_max": 0.86,
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 22,
            "bottom": 34,
            "left": 48
          },
          "x_ticks": [],
          "y_ticks": [
            0.3,
            0.5,
            0.7
          ],
          "x_axis_label": "time index",
          "axis_label_x": 208,
          "axis_label_y": 177,
          "y_axis_label": false,
          "line_class": "smooth-line",
          "primary_point_class": "smooth-point",
          "point_sample_every": 3,
          "point_radius": 3.4,
          "horizontal_markers": [
            {
              "y": 0.72,
              "class": "ewma-limit-line",
              "label": "UCL 0.72",
              "label_class": "warning-text",
              "label_x": 26.6,
              "label_dy": -6
            },
            {
              "y": 0.28,
              "class": "ewma-limit-line"
            },
            {
              "y": 0.5,
              "class": "center-line"
            }
          ],
          "point_highlights": [
            {
              "x": 27,
              "class": "ewma-alarm-point",
              "r": 4.8
            },
            {
              "x": 28,
              "class": "ewma-alarm-point",
              "r": 4.8
            },
            {
              "x": 29,
              "class": "ewma-alarm-point",
              "r": 4.8
            },
            {
              "x": 30,
              "class": "ewma-alarm-point",
              "r": 4.8
            },
            {
              "x": 31,
              "class": "ewma-alarm-point",
              "r": 4.8
            },
            {
              "x": 32,
              "class": "ewma-alarm-point",
              "r": 4.8
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-CTRL-002.series"
        }
      },
      {
        "componentInstanceId": "CHART-CTRL-002.timeline.0",
        "componentType": "state_timeline",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "start_field": "start",
          "end_field": "end",
          "window_role_field": "role",
          "window_id_field": "label",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 32,
            "right": 24,
            "bottom": 38,
            "left": 48
          },
          "track_y": 74,
          "track_height": 30,
          "axis_label": "EWMA alarm marker timeline",
          "axis_label_x": 228,
          "axis_label_y": 179,
          "role_class_map": {
            "normal": "state-normal",
            "warning": "state-warning",
            "alarm": "state-alarm"
          },
          "markers": [
            {
              "x": 27,
              "class": "ewma-alarm-line",
              "circle": true,
              "circle_class": "ewma-alarm-point",
              "radius": 7
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-CTRL-002.timeline"
        }
      },
      {
        "componentInstanceId": "CHART-CTRL-002.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-CTRL-002.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-CTRL-002.summary": [
        {
          "label": "EWMA final",
          "value": 0.8,
          "displayValue": "0.80"
        },
        {
          "label": "lambda",
          "value": 0.2,
          "displayValue": "0.20"
        },
        {
          "label": "shift",
          "value": 0.3,
          "displayValue": "+0.30"
        }
      ],
      "chart.CHART-CTRL-002.series": [
        {
          "time": 1,
          "raw": 0.48,
          "ewma": 0.5
        },
        {
          "time": 2,
          "raw": 0.52,
          "ewma": 0.51
        },
        {
          "time": 3,
          "raw": 0.49,
          "ewma": 0.5
        },
        {
          "time": 4,
          "raw": 0.51,
          "ewma": 0.51
        },
        {
          "time": 5,
          "raw": 0.5,
          "ewma": 0.5
        },
        {
          "time": 6,
          "raw": 0.54,
          "ewma": 0.52
        },
        {
          "time": 7,
          "raw": 0.49,
          "ewma": 0.51
        },
        {
          "time": 8,
          "raw": 0.53,
          "ewma": 0.52
        },
        {
          "time": 9,
          "raw": 0.52,
          "ewma": 0.52
        },
        {
          "time": 10,
          "raw": 0.55,
          "ewma": 0.53
        },
        {
          "time": 11,
          "raw": 0.51,
          "ewma": 0.52
        },
        {
          "time": 12,
          "raw": 0.56,
          "ewma": 0.54
        },
        {
          "time": 13,
          "raw": 0.54,
          "ewma": 0.54
        },
        {
          "time": 14,
          "raw": 0.57,
          "ewma": 0.55
        },
        {
          "time": 15,
          "raw": 0.55,
          "ewma": 0.55
        },
        {
          "time": 16,
          "raw": 0.59,
          "ewma": 0.56
        },
        {
          "time": 17,
          "raw": 0.61,
          "ewma": 0.58
        },
        {
          "time": 18,
          "raw": 0.58,
          "ewma": 0.58
        },
        {
          "time": 19,
          "raw": 0.63,
          "ewma": 0.6
        },
        {
          "time": 20,
          "raw": 0.64,
          "ewma": 0.61
        },
        {
          "time": 21,
          "raw": 0.66,
          "ewma": 0.63
        },
        {
          "time": 22,
          "raw": 0.68,
          "ewma": 0.65
        },
        {
          "time": 23,
          "raw": 0.69,
          "ewma": 0.66
        },
        {
          "time": 24,
          "raw": 0.71,
          "ewma": 0.68
        },
        {
          "time": 25,
          "raw": 0.73,
          "ewma": 0.7
        },
        {
          "time": 26,
          "raw": 0.74,
          "ewma": 0.71
        },
        {
          "time": 27,
          "raw": 0.76,
          "ewma": 0.73
        },
        {
          "time": 28,
          "raw": 0.75,
          "ewma": 0.74
        },
        {
          "time": 29,
          "raw": 0.78,
          "ewma": 0.75
        },
        {
          "time": 30,
          "raw": 0.8,
          "ewma": 0.77
        },
        {
          "time": 31,
          "raw": 0.79,
          "ewma": 0.78
        },
        {
          "time": 32,
          "raw": 0.82,
          "ewma": 0.8
        }
      ],
      "chart.CHART-CTRL-002.timeline": [
        {
          "label": "normal",
          "start": 1,
          "end": 21,
          "role": "normal"
        },
        {
          "label": "warning",
          "start": 21,
          "end": 27,
          "role": "warning"
        },
        {
          "label": "alarm",
          "start": 27,
          "end": 32,
          "role": "alarm"
        }
      ],
      "chart.CHART-CTRL-002.notes": [
        {
          "title": "해석",
          "text": "EWMA/GMA는 최근 값에 더 큰 가중치를 주어 noisy metric의 작은 평균 변화를 부드럽게 감지한다. 이 예시에서는 raw metric이 흔들리지만 EWMA가 꾸준히 상승해 t=27 부근에서 UCL 0.72를 넘고 final 0.80에 도달한다. Timeline도 warning 이후 alarm으로 전환되므로 noisy metric의 점진적 상방 평균 이동 후보로 해석한다. 단, lambda 0.20과 control limit 산정 방식, baseline 조건을 확인하지 않고 원인이나 성능 저하를 단정하지 않는다.",
          "legend": [
            {
              "label": "raw metric",
              "class": "swatch-raw"
            },
            {
              "label": "EWMA/GMA",
              "class": "swatch-smooth"
            },
            {
              "label": "alarm",
              "class": "swatch-alarm"
            },
            {
              "label": "UCL/LCL",
              "class": "swatch-control-limit"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-CTRL-003",
    "title": "CHART-CTRL-003 - MEWMA로 확인하는 여러 지표의 동시 상승 경보",
    "originalPath": "./drift_report_charts/chart_ctrl_003.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_ctrl_003",
      "displayName": "CHART-CTRL-003 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 146px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "MEWMA 통계량 관리도",
          "description": "MEWMA statistic이 점진적으로 올라 t=23 부근에서 UCL 12.0을 넘고 final 19.1에 도달하는지 본다.",
          "headerHeight": 62,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 16,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "지표 기여도",
          "description": "alarm 기여도가 risk_score 38%, amount 24%, frequency 18% 순으로 집중되는지 확인한다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "다변량 소형 추세",
          "description": "risk_score, amount, frequency가 같은 구간에서 함께 상승하는지 읽는다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "interpretation",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-CTRL-003.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-CTRL-003.summary"
        }
      },
      {
        "componentInstanceId": "CHART-CTRL-003.stat.0",
        "componentType": "control_chart",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "time",
          "y_field": "stat",
          "x_min": 1,
          "x_max": 32,
          "y_min": 0,
          "y_max": 22,
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 28,
            "bottom": 62,
            "left": 58
          },
          "x_ticks": [
            1,
            8,
            16,
            24,
            32
          ],
          "y_ticks": [
            0,
            5,
            10,
            15,
            20
          ],
          "x_axis_label": "time index",
          "y_axis_label": "MEWMA statistic",
          "line_class": "mewma-stat-line",
          "show_points": false,
          "horizontal_markers": [
            {
              "y": 12,
              "class": "ewma-limit-line",
              "label": "UCL 12.0",
              "label_class": "warning-text",
              "label_x": 28,
              "label_dy": -8
            }
          ],
          "vertical_markers": [
            {
              "x": 23,
              "class": "ewma-alarm-line"
            }
          ],
          "point_highlights": [
            {
              "x": 1,
              "class": "stat-point",
              "r": 3.6
            },
            {
              "x": 4,
              "class": "stat-point",
              "r": 3.6
            },
            {
              "x": 7,
              "class": "stat-point",
              "r": 3.6
            },
            {
              "x": 10,
              "class": "stat-point",
              "r": 3.6
            },
            {
              "x": 13,
              "class": "stat-point",
              "r": 3.6
            },
            {
              "x": 16,
              "class": "stat-point",
              "r": 3.6
            },
            {
              "x": 19,
              "class": "stat-point",
              "r": 3.6
            },
            {
              "x": 22,
              "class": "stat-point",
              "r": 3.6
            },
            {
              "x": 23,
              "class": "ewma-alarm-point",
              "r": 7
            },
            {
              "x": 24,
              "class": "ewma-alarm-point",
              "r": 4.8
            },
            {
              "x": 25,
              "class": "ewma-alarm-point",
              "r": 4.8
            },
            {
              "x": 26,
              "class": "ewma-alarm-point",
              "r": 4.8
            },
            {
              "x": 27,
              "class": "ewma-alarm-point",
              "r": 4.8
            },
            {
              "x": 28,
              "class": "ewma-alarm-point",
              "r": 4.8
            },
            {
              "x": 29,
              "class": "ewma-alarm-point",
              "r": 4.8
            },
            {
              "x": 30,
              "class": "ewma-alarm-point",
              "r": 4.8
            },
            {
              "x": 31,
              "class": "ewma-alarm-point",
              "r": 4.8
            },
            {
              "x": 32,
              "class": "ewma-alarm-point",
              "r": 4.8
            }
          ],
          "annotations": [
            {
              "text": "alarm: multivariate statistic crosses UCL",
              "x": 12,
              "y": 20.5,
              "class": "warning-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-CTRL-003.stat"
        }
      },
      {
        "componentInstanceId": "CHART-CTRL-003.contribution.0",
        "componentType": "contribution_view",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "horizontal_ranked",
          "category_field": "metric",
          "value_field": "value",
          "value_label_field": "valueLabel",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 14,
            "right": 32,
            "bottom": 26,
            "left": 96
          },
          "x_max": 42,
          "first_y": 17,
          "row_gap": 27,
          "bar_height": 16,
          "bar_radius": 4,
          "row_background_class": "row-bg",
          "bar_class": "bar-fill",
          "highlight_class": "bar-fill hot",
          "caption": "alarm contribution share"
        },
        "dataBinding": {
          "source": "chart.CHART-CTRL-003.contribution"
        }
      },
      {
        "componentInstanceId": "CHART-CTRL-003.small_multiples.0",
        "componentType": "small_multiple_lines",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "series_field": "series",
          "label_field": "series",
          "x_field": "time",
          "y_field": "value",
          "class_field": "class",
          "series_order": [
            "risk_score",
            "amount",
            "frequency"
          ],
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 8,
            "right": 22,
            "bottom": 22,
            "left": 82
          },
          "row_height": 48,
          "row_base_offset": 36,
          "row_top_offset": 5,
          "x_min": 1,
          "x_max": 16,
          "y_min": 0.35,
          "y_max": 0.72,
          "vertical_markers": [
            {
              "x": 12.2,
              "class": "ewma-alarm-line",
              "label": "동시 상승",
              "label_class": "warning-text",
              "label_dx": 10,
              "label_y": 31
            }
          ],
          "x_axis_label": "time aligned metrics",
          "axis_label_x": 232,
          "axis_label_y": 180
        },
        "dataBinding": {
          "source": "chart.CHART-CTRL-003.small"
        }
      },
      {
        "componentInstanceId": "CHART-CTRL-003.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-CTRL-003.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-CTRL-003.summary": [
        {
          "label": "MEWMA final",
          "value": 19.1,
          "displayValue": "19.1"
        },
        {
          "label": "UCL",
          "value": 12.0,
          "displayValue": "12.0"
        },
        {
          "label": "Top metric",
          "value": 38,
          "displayValue": "risk_score"
        }
      ],
      "chart.CHART-CTRL-003.stat": [
        {
          "time": 1,
          "stat": 3.1
        },
        {
          "time": 2,
          "stat": 3.4
        },
        {
          "time": 3,
          "stat": 3.0
        },
        {
          "time": 4,
          "stat": 3.8
        },
        {
          "time": 5,
          "stat": 4.2
        },
        {
          "time": 6,
          "stat": 3.7
        },
        {
          "time": 7,
          "stat": 4.5
        },
        {
          "time": 8,
          "stat": 5.1
        },
        {
          "time": 9,
          "stat": 4.8
        },
        {
          "time": 10,
          "stat": 5.4
        },
        {
          "time": 11,
          "stat": 5.9
        },
        {
          "time": 12,
          "stat": 6.2
        },
        {
          "time": 13,
          "stat": 6.8
        },
        {
          "time": 14,
          "stat": 7.1
        },
        {
          "time": 15,
          "stat": 7.5
        },
        {
          "time": 16,
          "stat": 8.0
        },
        {
          "time": 17,
          "stat": 8.6
        },
        {
          "time": 18,
          "stat": 9.2
        },
        {
          "time": 19,
          "stat": 9.8
        },
        {
          "time": 20,
          "stat": 10.3
        },
        {
          "time": 21,
          "stat": 11.1
        },
        {
          "time": 22,
          "stat": 11.8
        },
        {
          "time": 23,
          "stat": 12.6
        },
        {
          "time": 24,
          "stat": 13.4
        },
        {
          "time": 25,
          "stat": 14.1
        },
        {
          "time": 26,
          "stat": 15.0
        },
        {
          "time": 27,
          "stat": 15.8
        },
        {
          "time": 28,
          "stat": 16.9
        },
        {
          "time": 29,
          "stat": 17.5
        },
        {
          "time": 30,
          "stat": 18.2
        },
        {
          "time": 31,
          "stat": 18.6
        },
        {
          "time": 32,
          "stat": 19.1
        }
      ],
      "chart.CHART-CTRL-003.contribution": [
        {
          "metric": "risk_score",
          "value": 38,
          "valueLabel": "38%",
          "class": "bar-fill hot"
        },
        {
          "metric": "amount",
          "value": 24,
          "valueLabel": "24%",
          "class": "bar-fill"
        },
        {
          "metric": "frequency",
          "value": 18,
          "valueLabel": "18%",
          "class": "bar-fill"
        },
        {
          "metric": "latency",
          "value": 12,
          "valueLabel": "12%",
          "class": "bar-fill"
        },
        {
          "metric": "region_mix",
          "value": 8,
          "valueLabel": "8%",
          "class": "bar-fill"
        }
      ],
      "chart.CHART-CTRL-003.small": [
        {
          "series": "risk_score",
          "time": 1,
          "value": 0.42,
          "class": "metric-line"
        },
        {
          "series": "risk_score",
          "time": 2,
          "value": 0.43,
          "class": "metric-line"
        },
        {
          "series": "risk_score",
          "time": 3,
          "value": 0.41,
          "class": "metric-line"
        },
        {
          "series": "risk_score",
          "time": 4,
          "value": 0.44,
          "class": "metric-line"
        },
        {
          "series": "risk_score",
          "time": 5,
          "value": 0.45,
          "class": "metric-line"
        },
        {
          "series": "risk_score",
          "time": 6,
          "value": 0.46,
          "class": "metric-line"
        },
        {
          "series": "risk_score",
          "time": 7,
          "value": 0.47,
          "class": "metric-line"
        },
        {
          "series": "risk_score",
          "time": 8,
          "value": 0.48,
          "class": "metric-line"
        },
        {
          "series": "risk_score",
          "time": 9,
          "value": 0.5,
          "class": "metric-line"
        },
        {
          "series": "risk_score",
          "time": 10,
          "value": 0.51,
          "class": "metric-line"
        },
        {
          "series": "risk_score",
          "time": 11,
          "value": 0.53,
          "class": "metric-line"
        },
        {
          "series": "risk_score",
          "time": 12,
          "value": 0.54,
          "class": "metric-line"
        },
        {
          "series": "risk_score",
          "time": 13,
          "value": 0.56,
          "class": "metric-line"
        },
        {
          "series": "risk_score",
          "time": 14,
          "value": 0.58,
          "class": "metric-line"
        },
        {
          "series": "risk_score",
          "time": 15,
          "value": 0.6,
          "class": "metric-line"
        },
        {
          "series": "risk_score",
          "time": 16,
          "value": 0.62,
          "class": "metric-line"
        },
        {
          "series": "amount",
          "time": 1,
          "value": 0.51,
          "class": "metric-line alt"
        },
        {
          "series": "amount",
          "time": 2,
          "value": 0.5,
          "class": "metric-line alt"
        },
        {
          "series": "amount",
          "time": 3,
          "value": 0.52,
          "class": "metric-line alt"
        },
        {
          "series": "amount",
          "time": 4,
          "value": 0.51,
          "class": "metric-line alt"
        },
        {
          "series": "amount",
          "time": 5,
          "value": 0.53,
          "class": "metric-line alt"
        },
        {
          "series": "amount",
          "time": 6,
          "value": 0.54,
          "class": "metric-line alt"
        },
        {
          "series": "amount",
          "time": 7,
          "value": 0.55,
          "class": "metric-line alt"
        },
        {
          "series": "amount",
          "time": 8,
          "value": 0.57,
          "class": "metric-line alt"
        },
        {
          "series": "amount",
          "time": 9,
          "value": 0.58,
          "class": "metric-line alt"
        },
        {
          "series": "amount",
          "time": 10,
          "value": 0.6,
          "class": "metric-line alt"
        },
        {
          "series": "amount",
          "time": 11,
          "value": 0.61,
          "class": "metric-line alt"
        },
        {
          "series": "amount",
          "time": 12,
          "value": 0.63,
          "class": "metric-line alt"
        },
        {
          "series": "amount",
          "time": 13,
          "value": 0.64,
          "class": "metric-line alt"
        },
        {
          "series": "amount",
          "time": 14,
          "value": 0.66,
          "class": "metric-line alt"
        },
        {
          "series": "amount",
          "time": 15,
          "value": 0.68,
          "class": "metric-line alt"
        },
        {
          "series": "amount",
          "time": 16,
          "value": 0.69,
          "class": "metric-line alt"
        },
        {
          "series": "frequency",
          "time": 1,
          "value": 0.38,
          "class": "metric-line third"
        },
        {
          "series": "frequency",
          "time": 2,
          "value": 0.39,
          "class": "metric-line third"
        },
        {
          "series": "frequency",
          "time": 3,
          "value": 0.38,
          "class": "metric-line third"
        },
        {
          "series": "frequency",
          "time": 4,
          "value": 0.4,
          "class": "metric-line third"
        },
        {
          "series": "frequency",
          "time": 5,
          "value": 0.39,
          "class": "metric-line third"
        },
        {
          "series": "frequency",
          "time": 6,
          "value": 0.41,
          "class": "metric-line third"
        },
        {
          "series": "frequency",
          "time": 7,
          "value": 0.42,
          "class": "metric-line third"
        },
        {
          "series": "frequency",
          "time": 8,
          "value": 0.43,
          "class": "metric-line third"
        },
        {
          "series": "frequency",
          "time": 9,
          "value": 0.45,
          "class": "metric-line third"
        },
        {
          "series": "frequency",
          "time": 10,
          "value": 0.46,
          "class": "metric-line third"
        },
        {
          "series": "frequency",
          "time": 11,
          "value": 0.47,
          "class": "metric-line third"
        },
        {
          "series": "frequency",
          "time": 12,
          "value": 0.49,
          "class": "metric-line third"
        },
        {
          "series": "frequency",
          "time": 13,
          "value": 0.5,
          "class": "metric-line third"
        },
        {
          "series": "frequency",
          "time": 14,
          "value": 0.51,
          "class": "metric-line third"
        },
        {
          "series": "frequency",
          "time": 15,
          "value": 0.52,
          "class": "metric-line third"
        },
        {
          "series": "frequency",
          "time": 16,
          "value": 0.54,
          "class": "metric-line third"
        }
      ],
      "chart.CHART-CTRL-003.notes": [
        {
          "title": "해석",
          "text": "MEWMA는 여러 metric vector를 smoothing한 뒤 하나의 multivariate statistic으로 관리한다. 이 예시에서는 statistic이 t=23 부근에서 UCL 12.0을 넘고 final 19.1까지 상승한다. risk_score가 38%로 가장 크게 기여하며 amount와 frequency도 함께 상승하므로, 여러 지표의 공동 이동에 의한 다변량 drift 후보로 해석한다. 단, metric scaling과 covariance 추정 방식을 확인하지 않고 특정 지표 하나를 원인으로 단정하지 않는다.",
          "legend": [
            {
              "label": "MEWMA statistic",
              "class": "swatch-stat"
            },
            {
              "label": "UCL",
              "class": "swatch-control-limit"
            },
            {
              "label": "contribution",
              "class": "swatch-contrib"
            },
            {
              "label": "alarm",
              "class": "swatch-alarm"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-DIST-001",
    "title": "CHART-DIST-001 - 결제금액 분포의 오른쪽 이동과 거리 증가",
    "originalPath": "./drift_report_charts/chart_dist_001.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_dist_001",
      "displayName": "CHART-DIST-001 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 146px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "기준/현재 분포 비교",
          "description": "평균이 -0.07에서 0.61로, 중앙값이 -0.06에서 0.58로 오른쪽 이동했는지 본다.",
          "headerHeight": 62,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 16,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "거리 추세",
          "description": "distance가 관리 기준 0.30을 넘고 최근 window에서 0.68까지 증가하는지 확인한다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "특징 거리 순위",
          "description": "결제금액 distance 0.68이 feature 순위에서 가장 큰 이동인지 읽는다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "interpretation",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-DIST-001.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-DIST-001.summary"
        }
      },
      {
        "componentInstanceId": "CHART-DIST-001.distribution.0",
        "componentType": "distribution_view",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "distribution_style": "density_area",
          "x_field": "x",
          "primary_value_field": "reference",
          "secondary_value_field": "current",
          "x_min": -3.5,
          "x_max": 4.5,
          "y_min": 0,
          "y_max": 0.4455,
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 20,
            "right": 22,
            "bottom": 50,
            "left": 58
          },
          "x_ticks": [
            -3.5,
            0,
            4.5
          ],
          "y_ticks": [
            0,
            0.1485,
            0.297,
            0.4455
          ],
          "x_axis_label": "특성값",
          "y_axis_label": "밀도",
          "primary_area_class": "ref-area",
          "secondary_area_class": "cur-area",
          "segment_markers": [
            {
              "x0": -0.752,
              "x1": -0.165,
              "y": 0.3141,
              "class": "transport",
              "point_class": "trend-point",
              "r": 4
            },
            {
              "x0": -0.06,
              "x1": 0.582,
              "y": 0.2896,
              "class": "transport",
              "point_class": "trend-point",
              "r": 4
            },
            {
              "x0": 0.607,
              "x1": 1.269,
              "y": 0.2651,
              "class": "transport",
              "point_class": "trend-point",
              "r": 4
            }
          ],
          "annotations": [
            {
              "text": "분위수 이동량의 평균이 Wasserstein 거리",
              "x": -1.23,
              "y": 0.419,
              "class": "transport-label"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-DIST-001.density"
        }
      },
      {
        "componentInstanceId": "CHART-DIST-001.trend.0",
        "componentType": "distance_metric_view",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "window",
          "y_field": "distance",
          "x_min": 1,
          "x_max": 9,
          "y_min": 0,
          "y_max": 0.8,
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 18,
            "bottom": 34,
            "left": 48
          },
          "x_ticks": [],
          "y_ticks": [
            0,
            0.3,
            0.8
          ],
          "x_axis_label": "window",
          "axis_label_x": 209,
          "axis_label_y": 177,
          "y_axis_label": false,
          "line_class": "trend-line",
          "primary_point_class": "trend-point",
          "point_sample_every": 1,
          "point_radius": 4,
          "horizontal_markers": [
            {
              "y": 0.3,
              "class": "threshold-line",
              "label": "관리 기준",
              "label_class": "transport-label",
              "label_x": 7.6,
              "label_dy": -7
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-DIST-001.trend"
        }
      },
      {
        "componentInstanceId": "CHART-DIST-001.ranking.0",
        "componentType": "ranking_view",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "horizontal_ranked",
          "category_field": "feature",
          "value_field": "distance",
          "value_label_field": "distanceLabel",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 8,
            "right": 22,
            "bottom": 28,
            "left": 112
          },
          "x_max": 0.8,
          "first_y": 18,
          "row_gap": 27,
          "bar_height": 16,
          "bar_radius": 4,
          "caption": "distance"
        },
        "dataBinding": {
          "source": "chart.CHART-DIST-001.ranking"
        }
      },
      {
        "componentInstanceId": "CHART-DIST-001.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-DIST-001.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-DIST-001.summary": [
        {
          "label": "Wasserstein",
          "value": 0.6791,
          "displayValue": "0.68"
        },
        {
          "label": "평균 이동",
          "value": 0.6791,
          "displayValue": "0.68"
        },
        {
          "label": "상위 10% 이동",
          "value": 0.8611,
          "displayValue": "0.86"
        }
      ],
      "chart.CHART-DIST-001.density": [
        {
          "x": -3.5,
          "reference": 0.0009,
          "current": 0
        },
        {
          "x": -3.337,
          "reference": 0.0024,
          "current": 0
        },
        {
          "x": -3.173,
          "reference": 0.0045,
          "current": 0
        },
        {
          "x": -3.01,
          "reference": 0.0067,
          "current": 0
        },
        {
          "x": -2.847,
          "reference": 0.0089,
          "current": 0
        },
        {
          "x": -2.684,
          "reference": 0.0122,
          "current": 0.0001
        },
        {
          "x": -2.52,
          "reference": 0.0169,
          "current": 0.0003
        },
        {
          "x": -2.357,
          "reference": 0.0229,
          "current": 0.0014
        },
        {
          "x": -2.194,
          "reference": 0.0313,
          "current": 0.0045
        },
        {
          "x": -2.031,
          "reference": 0.0441,
          "current": 0.0105
        },
        {
          "x": -1.867,
          "reference": 0.0645,
          "current": 0.0197
        },
        {
          "x": -1.704,
          "reference": 0.0962,
          "current": 0.0315
        },
        {
          "x": -1.541,
          "reference": 0.1408,
          "current": 0.0462
        },
        {
          "x": -1.378,
          "reference": 0.1932,
          "current": 0.0652
        },
        {
          "x": -1.214,
          "reference": 0.242,
          "current": 0.0878
        },
        {
          "x": -1.051,
          "reference": 0.2777,
          "current": 0.1127
        },
        {
          "x": -0.888,
          "reference": 0.3038,
          "current": 0.1422
        },
        {
          "x": -0.724,
          "reference": 0.3284,
          "current": 0.1803
        },
        {
          "x": -0.561,
          "reference": 0.3509,
          "current": 0.226
        },
        {
          "x": -0.398,
          "reference": 0.3641,
          "current": 0.2711
        },
        {
          "x": -0.235,
          "reference": 0.3688,
          "current": 0.3072
        },
        {
          "x": -0.071,
          "reference": 0.3733,
          "current": 0.3319
        },
        {
          "x": 0.092,
          "reference": 0.3778,
          "current": 0.3484
        },
        {
          "x": 0.255,
          "reference": 0.3723,
          "current": 0.3613
        },
        {
          "x": 0.418,
          "reference": 0.3542,
          "current": 0.372
        },
        {
          "x": 0.582,
          "reference": 0.329,
          "current": 0.3769
        },
        {
          "x": 0.745,
          "reference": 0.2976,
          "current": 0.3702
        },
        {
          "x": 0.908,
          "reference": 0.2588,
          "current": 0.3514
        },
        {
          "x": 1.071,
          "reference": 0.2163,
          "current": 0.3272
        },
        {
          "x": 1.235,
          "reference": 0.1755,
          "current": 0.3009
        },
        {
          "x": 1.398,
          "reference": 0.1394,
          "current": 0.2682
        },
        {
          "x": 1.561,
          "reference": 0.1073,
          "current": 0.2274
        },
        {
          "x": 1.724,
          "reference": 0.0782,
          "current": 0.187
        },
        {
          "x": 1.888,
          "reference": 0.0538,
          "current": 0.1561
        },
        {
          "x": 2.051,
          "reference": 0.0355,
          "current": 0.1346
        },
        {
          "x": 2.214,
          "reference": 0.0223,
          "current": 0.1158
        },
        {
          "x": 2.378,
          "reference": 0.0142,
          "current": 0.0949
        },
        {
          "x": 2.541,
          "reference": 0.011,
          "current": 0.0722
        },
        {
          "x": 2.704,
          "reference": 0.0102,
          "current": 0.0508
        },
        {
          "x": 2.867,
          "reference": 0.0085,
          "current": 0.0346
        },
        {
          "x": 3.031,
          "reference": 0.0052,
          "current": 0.0251
        },
        {
          "x": 3.194,
          "reference": 0.0023,
          "current": 0.0214
        },
        {
          "x": 3.357,
          "reference": 0.0007,
          "current": 0.0208
        },
        {
          "x": 3.52,
          "reference": 0.0001,
          "current": 0.0199
        },
        {
          "x": 3.684,
          "reference": 0,
          "current": 0.0167
        },
        {
          "x": 3.847,
          "reference": 0,
          "current": 0.0122
        },
        {
          "x": 4.01,
          "reference": 0,
          "current": 0.0085
        },
        {
          "x": 4.173,
          "reference": 0,
          "current": 0.0057
        },
        {
          "x": 4.337,
          "reference": 0,
          "current": 0.0035
        },
        {
          "x": 4.5,
          "reference": 0,
          "current": 0.0017
        }
      ],
      "chart.CHART-DIST-001.trend": [
        {
          "window": 1,
          "distance": 0.12
        },
        {
          "window": 2,
          "distance": 0.16
        },
        {
          "window": 3,
          "distance": 0.14
        },
        {
          "window": 4,
          "distance": 0.19
        },
        {
          "window": 5,
          "distance": 0.24
        },
        {
          "window": 6,
          "distance": 0.31
        },
        {
          "window": 7,
          "distance": 0.37
        },
        {
          "window": 8,
          "distance": 0.46
        },
        {
          "window": 9,
          "distance": 0.6791
        }
      ],
      "chart.CHART-DIST-001.ranking": [
        {
          "feature": "결제금액",
          "distance": 0.6791,
          "distanceLabel": "0.68",
          "class": "dist-bar-highlight"
        },
        {
          "feature": "접속시간",
          "distance": 0.41,
          "distanceLabel": "0.41",
          "class": "dist-bar"
        },
        {
          "feature": "방문빈도",
          "distance": 0.34,
          "distanceLabel": "0.34",
          "class": "dist-bar"
        },
        {
          "feature": "상품수",
          "distance": 0.27,
          "distanceLabel": "0.27",
          "class": "dist-bar"
        },
        {
          "feature": "할인율",
          "distance": 0.19,
          "distanceLabel": "0.19",
          "class": "dist-bar"
        }
      ],
      "chart.CHART-DIST-001.notes": [
        {
          "title": "해석",
          "text": "이 예시에서는 Wasserstein distance가 0.68이고 평균 이동도 +0.68이다. 현재 분포는 기준보다 오른쪽으로 이동하며 상위 10% 분위수도 1.13에서 1.99로 커진다. 최근 window distance가 관리 기준 0.30을 넘고 결제금액이 feature 순위 1위이므로, 해당 feature의 분포 이동 후보로 해석한다.",
          "legend": [
            {
              "label": "기준 구간",
              "class": "swatch-reference"
            },
            {
              "label": "현재 구간",
              "class": "swatch-current-prop"
            },
            {
              "label": "이동 거리",
              "class": "swatch-distance"
            },
            {
              "label": "관리 기준",
              "class": "swatch-threshold"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-DISTSHAPE-001",
    "title": "CHART-DISTSHAPE-001 - 현재 분포의 오른쪽 어깨와 다봉성 변화",
    "originalPath": "./drift_report_charts/chart_distshape_001.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_distshape_001",
      "displayName": "CHART-DISTSHAPE-001 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 146px",
      "gap": "16px",
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "분포 비교",
          "description": "기준은 50 부근 단봉형이고, 현재는 65 부근 봉우리와 오른쪽 shoulder가 두드러지는지 본다.",
          "headerHeight": 62,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 16,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "특성함수 차이",
          "description": "t=2.0에서 real 0.24, imaginary 0.19로 차이가 가장 크다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "통계량 기여",
          "description": "최대 기여 주파수와 ES statistic 12.8, p-value 0.006을 함께 확인한다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "interpretation",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-DISTSHAPE-001.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-DISTSHAPE-001.summary"
        }
      },
      {
        "componentInstanceId": "CHART-DISTSHAPE-001.distribution.0",
        "componentType": "distribution_view",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "distribution_style": "density_area",
          "x_field": "x",
          "primary_value_field": "reference",
          "secondary_value_field": "current",
          "difference_value_field": "difference",
          "x_min": 18,
          "x_max": 82,
          "y_min": 0,
          "y_max": 1.05,
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 28,
            "bottom": 62,
            "left": 58
          },
          "x_ticks": [
            20,
            40,
            60,
            80
          ],
          "y_ticks": [
            0,
            0.25,
            0.5,
            0.75,
            1.0
          ],
          "x_axis_label": "feature value",
          "y_axis_label": "density",
          "difference_area_class": "diff-band",
          "primary_area_class": "ref-area",
          "secondary_area_class": "cur-area",
          "annotations": [
            {
              "text": "현재 분포는 65 부근 봉우리와 오른쪽 shoulder가 커짐",
              "x": 30,
              "y": 0.99,
              "class": "callout"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-DISTSHAPE-001.density"
        }
      },
      {
        "componentInstanceId": "CHART-DISTSHAPE-001.ecf.0",
        "componentType": "distance_metric_view",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "frequency",
          "y_field": "real",
          "secondary_value_field": "imaginary",
          "x_min": 0.5,
          "x_max": 3.0,
          "y_min": -0.03,
          "y_max": 0.27,
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 22,
            "bottom": 34,
            "left": 48
          },
          "x_ticks": [],
          "y_ticks": [
            0,
            0.1,
            0.2
          ],
          "x_axis_label": "frequency t",
          "axis_label_x": 249,
          "axis_label_y": 177,
          "y_axis_label": false,
          "line_class": "real-line",
          "secondary_line_class": "imag-line",
          "primary_point_class": "real-point",
          "secondary_point_class": "imag-point",
          "point_sample_every": 1,
          "point_radius": 4,
          "secondary_point_radius": 4,
          "horizontal_markers": [
            {
              "y": 0,
              "class": "zero-line"
            }
          ],
          "annotations": [
            {
              "text": "Real diff",
              "x": 2.45,
              "y": 0.24,
              "class": "callout"
            },
            {
              "text": "Imag diff",
              "x": 2.45,
              "y": 0.2,
              "class": "warning"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-DISTSHAPE-001.ecf"
        }
      },
      {
        "componentInstanceId": "CHART-DISTSHAPE-001.stat.0",
        "componentType": "contribution_view",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "horizontal_ranked",
          "category_field": "label",
          "value_field": "value",
          "value_label_field": "valueLabel",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 8,
            "right": 22,
            "bottom": 30,
            "left": 70
          },
          "x_max": 0.1172,
          "first_y": 13,
          "row_gap": 23,
          "bar_height": 16,
          "bar_radius": 4,
          "annotations": [
            {
              "text": "stat=12.8, p=0.006",
              "x": 220,
              "y": 179,
              "class": "axis-label"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-DISTSHAPE-001.stat"
        }
      },
      {
        "componentInstanceId": "CHART-DISTSHAPE-001.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-DISTSHAPE-001.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-DISTSHAPE-001.summary": [
        {
          "label": "ES statistic",
          "value": 12.8,
          "displayValue": "12.8"
        },
        {
          "label": "p-value",
          "value": 0.006,
          "displayValue": "0.006"
        },
        {
          "label": "최대 특성함수 차이",
          "value": 2.0,
          "displayValue": "t=2.0"
        }
      ],
      "chart.CHART-DISTSHAPE-001.density": [
        {
          "x": 20,
          "reference": 0.03,
          "current": 0.05,
          "difference": 0.02
        },
        {
          "x": 25,
          "reference": 0.08,
          "current": 0.12,
          "difference": 0.04
        },
        {
          "x": 30,
          "reference": 0.18,
          "current": 0.25,
          "difference": 0.07
        },
        {
          "x": 35,
          "reference": 0.36,
          "current": 0.42,
          "difference": 0.06
        },
        {
          "x": 40,
          "reference": 0.62,
          "current": 0.54,
          "difference": 0.08
        },
        {
          "x": 45,
          "reference": 0.84,
          "current": 0.5,
          "difference": 0.34
        },
        {
          "x": 50,
          "reference": 0.96,
          "current": 0.38,
          "difference": 0.58
        },
        {
          "x": 55,
          "reference": 0.86,
          "current": 0.46,
          "difference": 0.4
        },
        {
          "x": 60,
          "reference": 0.62,
          "current": 0.7,
          "difference": 0.08
        },
        {
          "x": 65,
          "reference": 0.36,
          "current": 0.9,
          "difference": 0.54
        },
        {
          "x": 70,
          "reference": 0.18,
          "current": 0.72,
          "difference": 0.54
        },
        {
          "x": 75,
          "reference": 0.08,
          "current": 0.38,
          "difference": 0.3
        },
        {
          "x": 80,
          "reference": 0.03,
          "current": 0.14,
          "difference": 0.11
        }
      ],
      "chart.CHART-DISTSHAPE-001.ecf": [
        {
          "frequency": 0.5,
          "real": 0.05,
          "imaginary": 0.03
        },
        {
          "frequency": 1.0,
          "real": 0.11,
          "imaginary": 0.08
        },
        {
          "frequency": 1.5,
          "real": 0.18,
          "imaginary": 0.15
        },
        {
          "frequency": 2.0,
          "real": 0.24,
          "imaginary": 0.19
        },
        {
          "frequency": 2.5,
          "real": 0.21,
          "imaginary": 0.16
        },
        {
          "frequency": 3.0,
          "real": 0.14,
          "imaginary": 0.1
        }
      ],
      "chart.CHART-DISTSHAPE-001.stat": [
        {
          "label": "t=2.0",
          "value": 0.0937,
          "valueLabel": "0.094",
          "class": "top-stat-bar"
        },
        {
          "label": "t=2.5",
          "value": 0.0697,
          "valueLabel": "0.070",
          "class": "stat-bar"
        },
        {
          "label": "t=1.5",
          "value": 0.0549,
          "valueLabel": "0.055",
          "class": "stat-bar"
        },
        {
          "label": "t=3.0",
          "value": 0.0296,
          "valueLabel": "0.030",
          "class": "stat-bar"
        },
        {
          "label": "t=1.0",
          "value": 0.0185,
          "valueLabel": "0.019",
          "class": "stat-bar"
        },
        {
          "label": "t=0.5",
          "value": 0.0034,
          "valueLabel": "0.003",
          "class": "stat-bar"
        }
      ],
      "chart.CHART-DISTSHAPE-001.notes": [
        {
          "title": "현재 상황 요약",
          "text": "현재 예시는 기준 분포의 50 부근 단봉 구조가 약해지고 65 부근 현재 봉우리가 커진 사례다. ES statistic은 12.8, p-value는 0.006이며 특성함수 차이와 통계량 기여가 t=2.0에서 가장 크게 나타나 분포 형태 drift 후보로 읽는다.",
          "legend": [
            {
              "label": "기준 분포",
              "class": "swatch-reference"
            },
            {
              "label": "현재 분포",
              "class": "swatch-current-prop"
            },
            {
              "label": "특성함수 차이",
              "class": "swatch-ecf"
            },
            {
              "label": "판단 기준",
              "class": "swatch-threshold"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-EDF-001",
    "title": "CHART-EDF-001 - KS 검정으로 확인하는 현재 분포의 오른쪽 이동",
    "originalPath": "./drift_report_charts/chart_edf_001.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_edf_001",
      "displayName": "CHART-EDF-001 source layout",
      "columns": 12,
      "rows": 3,
      "gridTemplateRows": "76px 508px 146px",
      "gap": "16px",
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 1,
          "title": "경험 누적분포 비교",
          "description": "x≈0.74에서 기준 CDF 0.804와 현재 CDF 0.587의 최대 차이 D=0.217이 나타나는지 본다.",
          "headerHeight": 62,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 16,
            "left": 16
          }
        },
        {
          "area": "side",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "분포 비교",
          "description": "현재 구간 평균이 -0.02에서 0.49 수준으로 올라가며 붉은 분포가 오른쪽으로 밀렸는지 확인한다.",
          "headerHeight": 62,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 16,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "interpretation",
          "x": 0,
          "y": 2,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-EDF-001.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-EDF-001.summary"
        }
      },
      {
        "componentInstanceId": "CHART-EDF-001.ecdf.0",
        "componentType": "cumulative_curve",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "x",
          "y_field": "reference",
          "secondary_value_field": "current",
          "x_min": -2.5,
          "x_max": 4.0,
          "y_min": 0,
          "y_max": 1,
          "view_box": [
            650,
            470
          ],
          "margin": {
            "top": 22,
            "right": 24,
            "bottom": 52,
            "left": 58
          },
          "x_ticks": [
            -2.5,
            -0.875,
            0.75,
            2.375,
            4.0
          ],
          "y_ticks": [
            0,
            0.25,
            0.5,
            0.75,
            1
          ],
          "x_axis_label": "특성값",
          "y_axis_label": "경험 CDF",
          "line_class": "ref-line",
          "secondary_line_class": "cur-line",
          "show_points": false,
          "show_secondary_points": false,
          "gap_markers": [
            {
              "x": 0.7444,
              "upper_field": "reference",
              "lower_field": "current",
              "class": "gap-line",
              "point_class": "gap-point",
              "r": 4
            }
          ],
          "annotations": [
            {
              "text": "D = 0.217",
              "x": 0.8644,
              "y": 0.7754,
              "class": "gap-label"
            }
          ],
          "x_tick_format": "fixed1",
          "y_tick_format": "fixed1"
        },
        "dataBinding": {
          "source": "chart.CHART-EDF-001.ecdf"
        }
      },
      {
        "componentInstanceId": "CHART-EDF-001.hist.0",
        "componentType": "histogram_view",
        "area": "side",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "distribution_style": "histogram_overlay",
          "x0_field": "x0",
          "x1_field": "x1",
          "primary_value_field": "reference",
          "secondary_value_field": "current",
          "x_min": -2.5,
          "x_max": 4.0,
          "y_min": 0,
          "y_max": 0.5061,
          "view_box": [
            390,
            470
          ],
          "margin": {
            "top": 22,
            "right": 24,
            "bottom": 52,
            "left": 58
          },
          "x_ticks": [
            -2.5,
            0.75,
            4.0
          ],
          "y_ticks": [
            0,
            0.2530650887573965,
            0.506130177514793
          ],
          "x_axis_label": "특성값",
          "y_axis_label": "밀도",
          "primary_bar_class": "bar-ref",
          "secondary_bar_class": "bar-cur",
          "primary_width_fraction": 0.96,
          "secondary_width_fraction": 0.64,
          "secondary_offset_fraction": 0.18,
          "bin_gap": 1,
          "x_tick_format": "fixed1",
          "y_tick_format": "fixed1"
        },
        "dataBinding": {
          "source": "chart.CHART-EDF-001.hist"
        }
      },
      {
        "componentInstanceId": "CHART-EDF-001.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-EDF-001.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-EDF-001.summary": [
        {
          "label": "KS 통계량",
          "value": 0.2169,
          "displayValue": "0.217"
        },
        {
          "label": "근사 p-value",
          "value": 1.57e-05,
          "displayValue": "<0.001"
        },
        {
          "label": "표본 수",
          "value": 490,
          "displayValue": "260 / 230"
        }
      ],
      "chart.CHART-EDF-001.ecdf": [
        {
          "x": -2.5,
          "reference": 0.0,
          "current": 0.0
        },
        {
          "x": -2.4637,
          "reference": 0.0,
          "current": 0.0
        },
        {
          "x": -2.4274,
          "reference": 0.0,
          "current": 0.0
        },
        {
          "x": -2.3911,
          "reference": 0.0,
          "current": 0.0
        },
        {
          "x": -2.3547,
          "reference": 0.0038,
          "current": 0.0
        },
        {
          "x": -2.3184,
          "reference": 0.0038,
          "current": 0.0
        },
        {
          "x": -2.2821,
          "reference": 0.0038,
          "current": 0.0
        },
        {
          "x": -2.2458,
          "reference": 0.0038,
          "current": 0.0043
        },
        {
          "x": -2.2095,
          "reference": 0.0077,
          "current": 0.0043
        },
        {
          "x": -2.1732,
          "reference": 0.0077,
          "current": 0.0043
        },
        {
          "x": -2.1369,
          "reference": 0.0154,
          "current": 0.0087
        },
        {
          "x": -2.1006,
          "reference": 0.0154,
          "current": 0.0087
        },
        {
          "x": -2.0642,
          "reference": 0.0192,
          "current": 0.0087
        },
        {
          "x": -2.0279,
          "reference": 0.0192,
          "current": 0.0087
        },
        {
          "x": -1.9916,
          "reference": 0.0192,
          "current": 0.0087
        },
        {
          "x": -1.9553,
          "reference": 0.0192,
          "current": 0.0087
        },
        {
          "x": -1.919,
          "reference": 0.0192,
          "current": 0.0087
        },
        {
          "x": -1.8827,
          "reference": 0.0269,
          "current": 0.0087
        },
        {
          "x": -1.8464,
          "reference": 0.0346,
          "current": 0.0087
        },
        {
          "x": -1.8101,
          "reference": 0.0385,
          "current": 0.0087
        },
        {
          "x": -1.7737,
          "reference": 0.0423,
          "current": 0.0087
        },
        {
          "x": -1.7374,
          "reference": 0.0462,
          "current": 0.0087
        },
        {
          "x": -1.7011,
          "reference": 0.0538,
          "current": 0.0087
        },
        {
          "x": -1.6648,
          "reference": 0.0615,
          "current": 0.0087
        },
        {
          "x": -1.6285,
          "reference": 0.0654,
          "current": 0.0087
        },
        {
          "x": -1.5922,
          "reference": 0.0654,
          "current": 0.0087
        },
        {
          "x": -1.5559,
          "reference": 0.0731,
          "current": 0.013
        },
        {
          "x": -1.5196,
          "reference": 0.0769,
          "current": 0.013
        },
        {
          "x": -1.4832,
          "reference": 0.0808,
          "current": 0.0174
        },
        {
          "x": -1.4469,
          "reference": 0.0808,
          "current": 0.0217
        },
        {
          "x": -1.4106,
          "reference": 0.0808,
          "current": 0.0217
        },
        {
          "x": -1.3743,
          "reference": 0.0846,
          "current": 0.0217
        },
        {
          "x": -1.338,
          "reference": 0.0846,
          "current": 0.0217
        },
        {
          "x": -1.3017,
          "reference": 0.0923,
          "current": 0.0304
        },
        {
          "x": -1.2654,
          "reference": 0.1,
          "current": 0.0391
        },
        {
          "x": -1.2291,
          "reference": 0.1038,
          "current": 0.0435
        },
        {
          "x": -1.1927,
          "reference": 0.1115,
          "current": 0.0652
        },
        {
          "x": -1.1564,
          "reference": 0.1192,
          "current": 0.0696
        },
        {
          "x": -1.1201,
          "reference": 0.1308,
          "current": 0.0696
        },
        {
          "x": -1.0838,
          "reference": 0.1308,
          "current": 0.0739
        },
        {
          "x": -1.0475,
          "reference": 0.1423,
          "current": 0.0783
        },
        {
          "x": -1.0112,
          "reference": 0.1577,
          "current": 0.0783
        },
        {
          "x": -0.9749,
          "reference": 0.1731,
          "current": 0.087
        },
        {
          "x": -0.9385,
          "reference": 0.1731,
          "current": 0.1
        },
        {
          "x": -0.9022,
          "reference": 0.1808,
          "current": 0.1
        },
        {
          "x": -0.8659,
          "reference": 0.1923,
          "current": 0.1087
        },
        {
          "x": -0.8296,
          "reference": 0.1962,
          "current": 0.1174
        },
        {
          "x": -0.7933,
          "reference": 0.2038,
          "current": 0.1217
        },
        {
          "x": -0.757,
          "reference": 0.2154,
          "current": 0.1304
        },
        {
          "x": -0.7207,
          "reference": 0.2231,
          "current": 0.1348
        },
        {
          "x": -0.6844,
          "reference": 0.2231,
          "current": 0.1435
        },
        {
          "x": -0.648,
          "reference": 0.2423,
          "current": 0.1478
        },
        {
          "x": -0.6117,
          "reference": 0.2538,
          "current": 0.1565
        },
        {
          "x": -0.5754,
          "reference": 0.2654,
          "current": 0.1652
        },
        {
          "x": -0.5391,
          "reference": 0.2923,
          "current": 0.1826
        },
        {
          "x": -0.5028,
          "reference": 0.3038,
          "current": 0.2
        },
        {
          "x": -0.4665,
          "reference": 0.3231,
          "current": 0.2174
        },
        {
          "x": -0.4302,
          "reference": 0.3308,
          "current": 0.2261
        },
        {
          "x": -0.3939,
          "reference": 0.3615,
          "current": 0.2391
        },
        {
          "x": -0.3575,
          "reference": 0.3692,
          "current": 0.2522
        },
        {
          "x": -0.3212,
          "reference": 0.3962,
          "current": 0.2565
        },
        {
          "x": -0.2849,
          "reference": 0.4,
          "current": 0.2609
        },
        {
          "x": -0.2486,
          "reference": 0.4192,
          "current": 0.2783
        },
        {
          "x": -0.2123,
          "reference": 0.4308,
          "current": 0.2913
        },
        {
          "x": -0.176,
          "reference": 0.4346,
          "current": 0.3
        },
        {
          "x": -0.1397,
          "reference": 0.4538,
          "current": 0.313
        },
        {
          "x": -0.1034,
          "reference": 0.4731,
          "current": 0.3261
        },
        {
          "x": -0.067,
          "reference": 0.4885,
          "current": 0.3261
        },
        {
          "x": -0.0307,
          "reference": 0.5077,
          "current": 0.3348
        },
        {
          "x": 0.0056,
          "reference": 0.5115,
          "current": 0.3391
        },
        {
          "x": 0.0419,
          "reference": 0.5269,
          "current": 0.3522
        },
        {
          "x": 0.0782,
          "reference": 0.55,
          "current": 0.3522
        },
        {
          "x": 0.1145,
          "reference": 0.5654,
          "current": 0.3739
        },
        {
          "x": 0.1508,
          "reference": 0.5808,
          "current": 0.3826
        },
        {
          "x": 0.1872,
          "reference": 0.5962,
          "current": 0.4
        },
        {
          "x": 0.2235,
          "reference": 0.6231,
          "current": 0.4217
        },
        {
          "x": 0.2598,
          "reference": 0.6269,
          "current": 0.4348
        },
        {
          "x": 0.2961,
          "reference": 0.6346,
          "current": 0.4478
        },
        {
          "x": 0.3324,
          "reference": 0.65,
          "current": 0.4609
        },
        {
          "x": 0.3687,
          "reference": 0.6654,
          "current": 0.4652
        },
        {
          "x": 0.405,
          "reference": 0.6654,
          "current": 0.4783
        },
        {
          "x": 0.4413,
          "reference": 0.6808,
          "current": 0.4913
        },
        {
          "x": 0.4777,
          "reference": 0.6962,
          "current": 0.5043
        },
        {
          "x": 0.514,
          "reference": 0.7077,
          "current": 0.513
        },
        {
          "x": 0.5503,
          "reference": 0.7231,
          "current": 0.5174
        },
        {
          "x": 0.5866,
          "reference": 0.7269,
          "current": 0.5348
        },
        {
          "x": 0.6229,
          "reference": 0.7423,
          "current": 0.5391
        },
        {
          "x": 0.6592,
          "reference": 0.75,
          "current": 0.5522
        },
        {
          "x": 0.6955,
          "reference": 0.7692,
          "current": 0.5652
        },
        {
          "x": 0.7318,
          "reference": 0.7885,
          "current": 0.587
        },
        {
          "x": 0.7444,
          "reference": 0.8038,
          "current": 0.587
        },
        {
          "x": 0.7682,
          "reference": 0.8077,
          "current": 0.6043
        },
        {
          "x": 0.8045,
          "reference": 0.8231,
          "current": 0.613
        },
        {
          "x": 0.8408,
          "reference": 0.8308,
          "current": 0.6261
        },
        {
          "x": 0.8771,
          "reference": 0.8346,
          "current": 0.6435
        },
        {
          "x": 0.9134,
          "reference": 0.8462,
          "current": 0.6826
        },
        {
          "x": 0.9497,
          "reference": 0.8538,
          "current": 0.687
        },
        {
          "x": 0.986,
          "reference": 0.8615,
          "current": 0.687
        },
        {
          "x": 1.0223,
          "reference": 0.8692,
          "current": 0.7
        },
        {
          "x": 1.0587,
          "reference": 0.8731,
          "current": 0.7043
        },
        {
          "x": 1.095,
          "reference": 0.8769,
          "current": 0.7174
        },
        {
          "x": 1.1313,
          "reference": 0.8769,
          "current": 0.7304
        },
        {
          "x": 1.1676,
          "reference": 0.8846,
          "current": 0.7391
        },
        {
          "x": 1.2039,
          "reference": 0.8962,
          "current": 0.7435
        },
        {
          "x": 1.2402,
          "reference": 0.9038,
          "current": 0.7609
        },
        {
          "x": 1.2765,
          "reference": 0.9077,
          "current": 0.7696
        },
        {
          "x": 1.3128,
          "reference": 0.9077,
          "current": 0.7739
        },
        {
          "x": 1.3492,
          "reference": 0.9192,
          "current": 0.7739
        },
        {
          "x": 1.3855,
          "reference": 0.9192,
          "current": 0.7783
        },
        {
          "x": 1.4218,
          "reference": 0.9269,
          "current": 0.7826
        },
        {
          "x": 1.4581,
          "reference": 0.9269,
          "current": 0.7957
        },
        {
          "x": 1.4944,
          "reference": 0.9346,
          "current": 0.8043
        },
        {
          "x": 1.5307,
          "reference": 0.9462,
          "current": 0.8174
        },
        {
          "x": 1.567,
          "reference": 0.95,
          "current": 0.8304
        },
        {
          "x": 1.6034,
          "reference": 0.95,
          "current": 0.8435
        },
        {
          "x": 1.6397,
          "reference": 0.9577,
          "current": 0.8478
        },
        {
          "x": 1.676,
          "reference": 0.9577,
          "current": 0.8652
        },
        {
          "x": 1.7123,
          "reference": 0.9654,
          "current": 0.8739
        },
        {
          "x": 1.7486,
          "reference": 0.9654,
          "current": 0.8783
        },
        {
          "x": 1.7849,
          "reference": 0.9654,
          "current": 0.8826
        },
        {
          "x": 1.8212,
          "reference": 0.9692,
          "current": 0.887
        },
        {
          "x": 1.8575,
          "reference": 0.9692,
          "current": 0.8913
        },
        {
          "x": 1.8939,
          "reference": 0.9769,
          "current": 0.8957
        },
        {
          "x": 1.9302,
          "reference": 0.9769,
          "current": 0.9
        },
        {
          "x": 1.9665,
          "reference": 0.9769,
          "current": 0.9043
        },
        {
          "x": 2.0028,
          "reference": 0.9808,
          "current": 0.913
        },
        {
          "x": 2.0391,
          "reference": 0.9808,
          "current": 0.9217
        },
        {
          "x": 2.0754,
          "reference": 0.9808,
          "current": 0.9261
        },
        {
          "x": 2.1117,
          "reference": 0.9846,
          "current": 0.9304
        },
        {
          "x": 2.148,
          "reference": 0.9885,
          "current": 0.9348
        },
        {
          "x": 2.1844,
          "reference": 0.9885,
          "current": 0.9391
        },
        {
          "x": 2.2207,
          "reference": 0.9923,
          "current": 0.9391
        },
        {
          "x": 2.257,
          "reference": 0.9923,
          "current": 0.9435
        },
        {
          "x": 2.2933,
          "reference": 0.9923,
          "current": 0.9435
        },
        {
          "x": 2.3296,
          "reference": 0.9923,
          "current": 0.9435
        },
        {
          "x": 2.3659,
          "reference": 0.9923,
          "current": 0.9435
        },
        {
          "x": 2.4022,
          "reference": 0.9923,
          "current": 0.9478
        },
        {
          "x": 2.4385,
          "reference": 0.9923,
          "current": 0.9478
        },
        {
          "x": 2.4749,
          "reference": 0.9923,
          "current": 0.9522
        },
        {
          "x": 2.5112,
          "reference": 0.9923,
          "current": 0.9565
        },
        {
          "x": 2.5475,
          "reference": 0.9923,
          "current": 0.9565
        },
        {
          "x": 2.5838,
          "reference": 0.9923,
          "current": 0.9652
        },
        {
          "x": 2.6201,
          "reference": 0.9923,
          "current": 0.9652
        },
        {
          "x": 2.6564,
          "reference": 0.9923,
          "current": 0.9652
        },
        {
          "x": 2.6927,
          "reference": 0.9923,
          "current": 0.9696
        },
        {
          "x": 2.7291,
          "reference": 0.9923,
          "current": 0.9739
        },
        {
          "x": 2.7654,
          "reference": 0.9923,
          "current": 0.9783
        },
        {
          "x": 2.8017,
          "reference": 0.9923,
          "current": 0.9783
        },
        {
          "x": 2.838,
          "reference": 0.9923,
          "current": 0.9826
        },
        {
          "x": 2.8743,
          "reference": 0.9923,
          "current": 0.9913
        },
        {
          "x": 2.9106,
          "reference": 0.9923,
          "current": 0.9913
        },
        {
          "x": 2.9469,
          "reference": 0.9923,
          "current": 0.9913
        },
        {
          "x": 2.9832,
          "reference": 0.9962,
          "current": 0.9913
        },
        {
          "x": 3.0196,
          "reference": 0.9962,
          "current": 0.9957
        },
        {
          "x": 3.0559,
          "reference": 0.9962,
          "current": 0.9957
        },
        {
          "x": 3.0922,
          "reference": 0.9962,
          "current": 0.9957
        },
        {
          "x": 3.1285,
          "reference": 0.9962,
          "current": 0.9957
        },
        {
          "x": 3.1648,
          "reference": 0.9962,
          "current": 0.9957
        },
        {
          "x": 3.2011,
          "reference": 0.9962,
          "current": 0.9957
        },
        {
          "x": 3.2374,
          "reference": 0.9962,
          "current": 1.0
        },
        {
          "x": 3.2737,
          "reference": 0.9962,
          "current": 1.0
        },
        {
          "x": 3.3101,
          "reference": 0.9962,
          "current": 1.0
        },
        {
          "x": 3.3464,
          "reference": 0.9962,
          "current": 1.0
        },
        {
          "x": 3.3827,
          "reference": 0.9962,
          "current": 1.0
        },
        {
          "x": 3.419,
          "reference": 0.9962,
          "current": 1.0
        },
        {
          "x": 3.4553,
          "reference": 0.9962,
          "current": 1.0
        },
        {
          "x": 3.4916,
          "reference": 0.9962,
          "current": 1.0
        },
        {
          "x": 3.5279,
          "reference": 0.9962,
          "current": 1.0
        },
        {
          "x": 3.5642,
          "reference": 0.9962,
          "current": 1.0
        },
        {
          "x": 3.6006,
          "reference": 0.9962,
          "current": 1.0
        },
        {
          "x": 3.6369,
          "reference": 0.9962,
          "current": 1.0
        },
        {
          "x": 3.6732,
          "reference": 0.9962,
          "current": 1.0
        },
        {
          "x": 3.7095,
          "reference": 0.9962,
          "current": 1.0
        },
        {
          "x": 3.7458,
          "reference": 0.9962,
          "current": 1.0
        },
        {
          "x": 3.7821,
          "reference": 0.9962,
          "current": 1.0
        },
        {
          "x": 3.8184,
          "reference": 0.9962,
          "current": 1.0
        },
        {
          "x": 3.8547,
          "reference": 1.0,
          "current": 1.0
        },
        {
          "x": 3.8911,
          "reference": 1.0,
          "current": 1.0
        },
        {
          "x": 3.9274,
          "reference": 1.0,
          "current": 1.0
        },
        {
          "x": 3.9637,
          "reference": 1.0,
          "current": 1.0
        },
        {
          "x": 4.0,
          "reference": 1.0,
          "current": 1.0
        }
      ],
      "chart.CHART-EDF-001.hist": [
        {
          "x0": -2.5,
          "x1": -2.2292,
          "reference": 0.0284,
          "current": 0.0161
        },
        {
          "x0": -2.2292,
          "x1": -1.9583,
          "reference": 0.0426,
          "current": 0.0161
        },
        {
          "x0": -1.9583,
          "x1": -1.6875,
          "reference": 0.142,
          "current": 0.0
        },
        {
          "x0": -1.6875,
          "x1": -1.4167,
          "reference": 0.0852,
          "current": 0.0482
        },
        {
          "x0": -1.4167,
          "x1": -1.1458,
          "reference": 0.142,
          "current": 0.1766
        },
        {
          "x0": -1.1458,
          "x1": -0.875,
          "reference": 0.2698,
          "current": 0.1445
        },
        {
          "x0": -0.875,
          "x1": -0.6042,
          "reference": 0.2414,
          "current": 0.1766
        },
        {
          "x0": -0.6042,
          "x1": -0.3333,
          "reference": 0.4686,
          "current": 0.3692
        },
        {
          "x0": -0.3333,
          "x1": -0.0625,
          "reference": 0.3976,
          "current": 0.2729
        },
        {
          "x0": -0.0625,
          "x1": 0.2083,
          "reference": 0.4402,
          "current": 0.305
        },
        {
          "x0": 0.2083,
          "x1": 0.4792,
          "reference": 0.3124,
          "current": 0.3371
        },
        {
          "x0": 0.4792,
          "x1": 0.75,
          "reference": 0.3976,
          "current": 0.3211
        },
        {
          "x0": 0.75,
          "x1": 1.0208,
          "reference": 0.2414,
          "current": 0.4013
        },
        {
          "x0": 1.0208,
          "x1": 1.2917,
          "reference": 0.142,
          "current": 0.2569
        },
        {
          "x0": 1.2917,
          "x1": 1.5625,
          "reference": 0.1562,
          "current": 0.2247
        },
        {
          "x0": 1.5625,
          "x1": 1.8333,
          "reference": 0.071,
          "current": 0.2087
        },
        {
          "x0": 1.8333,
          "x1": 2.1042,
          "reference": 0.0426,
          "current": 0.1605
        },
        {
          "x0": 2.1042,
          "x1": 2.375,
          "reference": 0.0426,
          "current": 0.0482
        },
        {
          "x0": 2.375,
          "x1": 2.6458,
          "reference": 0.0,
          "current": 0.0803
        },
        {
          "x0": 2.6458,
          "x1": 2.9167,
          "reference": 0.0,
          "current": 0.0963
        },
        {
          "x0": 2.9167,
          "x1": 3.1875,
          "reference": 0.0142,
          "current": 0.0161
        },
        {
          "x0": 3.1875,
          "x1": 3.4583,
          "reference": 0.0,
          "current": 0.0161
        },
        {
          "x0": 3.4583,
          "x1": 3.7292,
          "reference": 0.0,
          "current": 0.0
        },
        {
          "x0": 3.7292,
          "x1": 4.0,
          "reference": 0.0142,
          "current": 0.0
        }
      ],
      "chart.CHART-EDF-001.notes": [
        {
          "title": "해석",
          "text": "이 예시에서는 KS 통계량이 0.217이고 p-value가 0.001보다 작다. x≈0.74에서 기준 구간 누적비율은 0.804인데 현재 구간은 0.587에 머물러 현재 값들이 전반적으로 더 큰 쪽에 분포한다. 히스토그램에서도 현재 분포가 오른쪽으로 이동하므로 단변량 feature drift 후보로 해석하되, 성능 저하나 원인은 별도 분석으로 확인한다.",
          "legend": [
            {
              "label": "기준 구간",
              "class": "swatch-reference"
            },
            {
              "label": "현재 구간",
              "class": "swatch-current-prop"
            },
            {
              "label": "최대 KS 차이",
              "class": "swatch-gap"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-EDF-002",
    "title": "CHART-EDF-002 - 상위 꼬리 극단값 확대로 보는 분포 변화",
    "originalPath": "./drift_report_charts/chart_edf_002.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_edf_002",
      "displayName": "CHART-EDF-002 source layout",
      "columns": 12,
      "rows": 3,
      "gridTemplateRows": "76px 508px 146px",
      "gap": "16px",
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 6,
          "h": 1,
          "title": "꼬리 가중 누적분포 비교",
          "description": "중심부보다 하위 5%, 상위 5% tail에서 기준/현재 CDF가 벌어지는지 본다.",
          "headerHeight": 62,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 16,
            "left": 16
          }
        },
        {
          "area": "side",
          "role": "secondary_visual",
          "x": 6,
          "y": 1,
          "w": 6,
          "h": 1,
          "title": "분위수-분위수 비교",
          "description": "상위 99% 분위수가 기준 2.60에서 현재 3.61로 커지는 tail 확장을 확인한다.",
          "headerHeight": 62,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 16,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "interpretation",
          "x": 0,
          "y": 2,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-EDF-002.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-EDF-002.summary"
        }
      },
      {
        "componentInstanceId": "CHART-EDF-002.tail.0",
        "componentType": "cumulative_curve",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "x",
          "y_field": "reference",
          "secondary_value_field": "current",
          "x_min": -5.0,
          "x_max": 7.0,
          "y_min": 0,
          "y_max": 1,
          "view_box": [
            535,
            450
          ],
          "margin": {
            "top": 22,
            "right": 26,
            "bottom": 52,
            "left": 58
          },
          "x_ticks": [
            -5.0,
            0,
            7.0
          ],
          "y_ticks": [
            0,
            0.25,
            0.5,
            0.75,
            1
          ],
          "x_axis_label": "특성값",
          "y_axis_label": "경험 CDF",
          "line_class": "ref-line",
          "secondary_line_class": "cur-line",
          "show_points": false,
          "show_secondary_points": false,
          "background_regions": [
            {
              "x0": -5.0,
              "x1": -1.8566,
              "fill": "rgba(122, 93, 199, 0.10)"
            },
            {
              "x0": 1.7185,
              "x1": 7.0,
              "fill": "rgba(122, 93, 199, 0.10)"
            }
          ],
          "annotations": [
            {
              "text": "하위 tail",
              "x": -4.78,
              "y": 0.965,
              "class": "tail-label"
            },
            {
              "text": "상위 tail",
              "x": 5.25,
              "y": 0.965,
              "class": "tail-label"
            }
          ],
          "x_tick_format": "fixed1",
          "y_tick_format": "fixed1"
        },
        "dataBinding": {
          "source": "chart.CHART-EDF-002.tail"
        }
      },
      {
        "componentInstanceId": "CHART-EDF-002.qq.0",
        "componentType": "projection_scatter",
        "area": "side",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "reference",
          "y_field": "current",
          "x_min": -2.5,
          "x_max": 3.0,
          "y_min": -2.5,
          "y_max": 3.0,
          "view_box": [
            535,
            450
          ],
          "margin": {
            "top": 22,
            "right": 26,
            "bottom": 52,
            "left": 58
          },
          "x_ticks": [
            -2.5,
            0,
            3.0
          ],
          "y_ticks": [
            -2.5,
            0,
            3.0
          ],
          "x_axis_label": "기준 분위수",
          "y_axis_label": "현재 분위수",
          "crosshair": false,
          "group_class_map": {
            "value": "qq-point"
          },
          "diagonal_markers": [
            {
              "x0": -2.5,
              "x1": 3.0,
              "y0": -2.5,
              "y1": 3.0,
              "class": "qq-ref"
            }
          ],
          "annotations": [
            {
              "text": "점선에서 멀수록 분위수 차이가 큼",
              "x": -2.38,
              "y": 2.76,
              "class": "tail-label"
            }
          ],
          "x_tick_format": "fixed1",
          "y_tick_format": "fixed1"
        },
        "dataBinding": {
          "source": "chart.CHART-EDF-002.qq"
        }
      },
      {
        "componentInstanceId": "CHART-EDF-002.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-EDF-002.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-EDF-002.summary": [
        {
          "label": "AD 통계량",
          "value": 2.84,
          "displayValue": "2.84"
        },
        {
          "label": "근사 p-value",
          "value": 0.012,
          "displayValue": "0.012"
        },
        {
          "label": "Tail 차이",
          "value": 0.4996,
          "displayValue": "0.50"
        }
      ],
      "chart.CHART-EDF-002.tail": [
        {
          "x": -5.0,
          "reference": 0.0,
          "current": 0.0
        },
        {
          "x": -4.933,
          "reference": 0.0,
          "current": 0.0
        },
        {
          "x": -4.8659,
          "reference": 0.0,
          "current": 0.0
        },
        {
          "x": -4.7989,
          "reference": 0.0,
          "current": 0.0
        },
        {
          "x": -4.7318,
          "reference": 0.0,
          "current": 0.0
        },
        {
          "x": -4.6648,
          "reference": 0.0,
          "current": 0.0
        },
        {
          "x": -4.5978,
          "reference": 0.0,
          "current": 0.0038
        },
        {
          "x": -4.5307,
          "reference": 0.0,
          "current": 0.0038
        },
        {
          "x": -4.4637,
          "reference": 0.0,
          "current": 0.0038
        },
        {
          "x": -4.3966,
          "reference": 0.0,
          "current": 0.0038
        },
        {
          "x": -4.3296,
          "reference": 0.0,
          "current": 0.0038
        },
        {
          "x": -4.2626,
          "reference": 0.0,
          "current": 0.0038
        },
        {
          "x": -4.1955,
          "reference": 0.0,
          "current": 0.0038
        },
        {
          "x": -4.1285,
          "reference": 0.0,
          "current": 0.0038
        },
        {
          "x": -4.0615,
          "reference": 0.0,
          "current": 0.0038
        },
        {
          "x": -3.9944,
          "reference": 0.0,
          "current": 0.0038
        },
        {
          "x": -3.9274,
          "reference": 0.0,
          "current": 0.0038
        },
        {
          "x": -3.8603,
          "reference": 0.0,
          "current": 0.0038
        },
        {
          "x": -3.7933,
          "reference": 0.0,
          "current": 0.0038
        },
        {
          "x": -3.7263,
          "reference": 0.0,
          "current": 0.0038
        },
        {
          "x": -3.6592,
          "reference": 0.0,
          "current": 0.0038
        },
        {
          "x": -3.5922,
          "reference": 0.0,
          "current": 0.0077
        },
        {
          "x": -3.5251,
          "reference": 0.0,
          "current": 0.0077
        },
        {
          "x": -3.4581,
          "reference": 0.0,
          "current": 0.0115
        },
        {
          "x": -3.3911,
          "reference": 0.0,
          "current": 0.0115
        },
        {
          "x": -3.324,
          "reference": 0.0038,
          "current": 0.0115
        },
        {
          "x": -3.257,
          "reference": 0.0038,
          "current": 0.0115
        },
        {
          "x": -3.1899,
          "reference": 0.0038,
          "current": 0.0115
        },
        {
          "x": -3.1229,
          "reference": 0.0038,
          "current": 0.0115
        },
        {
          "x": -3.0559,
          "reference": 0.0038,
          "current": 0.0115
        },
        {
          "x": -2.9888,
          "reference": 0.0038,
          "current": 0.0115
        },
        {
          "x": -2.9218,
          "reference": 0.0038,
          "current": 0.0115
        },
        {
          "x": -2.8547,
          "reference": 0.0038,
          "current": 0.0115
        },
        {
          "x": -2.7877,
          "reference": 0.0038,
          "current": 0.0115
        },
        {
          "x": -2.7207,
          "reference": 0.0038,
          "current": 0.0115
        },
        {
          "x": -2.6536,
          "reference": 0.0038,
          "current": 0.0115
        },
        {
          "x": -2.5866,
          "reference": 0.0038,
          "current": 0.0154
        },
        {
          "x": -2.5196,
          "reference": 0.0115,
          "current": 0.0192
        },
        {
          "x": -2.4525,
          "reference": 0.0115,
          "current": 0.0192
        },
        {
          "x": -2.3855,
          "reference": 0.0115,
          "current": 0.0269
        },
        {
          "x": -2.3184,
          "reference": 0.0154,
          "current": 0.0269
        },
        {
          "x": -2.2514,
          "reference": 0.0192,
          "current": 0.0269
        },
        {
          "x": -2.1844,
          "reference": 0.0231,
          "current": 0.0308
        },
        {
          "x": -2.1173,
          "reference": 0.0269,
          "current": 0.0308
        },
        {
          "x": -2.0503,
          "reference": 0.0308,
          "current": 0.0308
        },
        {
          "x": -1.9832,
          "reference": 0.0423,
          "current": 0.0346
        },
        {
          "x": -1.9162,
          "reference": 0.05,
          "current": 0.0385
        },
        {
          "x": -1.8492,
          "reference": 0.0538,
          "current": 0.0423
        },
        {
          "x": -1.7821,
          "reference": 0.0692,
          "current": 0.05
        },
        {
          "x": -1.7151,
          "reference": 0.0692,
          "current": 0.05
        },
        {
          "x": -1.648,
          "reference": 0.0731,
          "current": 0.0577
        },
        {
          "x": -1.581,
          "reference": 0.0885,
          "current": 0.0615
        },
        {
          "x": -1.514,
          "reference": 0.0962,
          "current": 0.0615
        },
        {
          "x": -1.4469,
          "reference": 0.1038,
          "current": 0.0731
        },
        {
          "x": -1.3799,
          "reference": 0.1115,
          "current": 0.0769
        },
        {
          "x": -1.3128,
          "reference": 0.1269,
          "current": 0.0846
        },
        {
          "x": -1.2458,
          "reference": 0.1385,
          "current": 0.0923
        },
        {
          "x": -1.1788,
          "reference": 0.1577,
          "current": 0.1077
        },
        {
          "x": -1.1117,
          "reference": 0.1731,
          "current": 0.1192
        },
        {
          "x": -1.0447,
          "reference": 0.1846,
          "current": 0.1192
        },
        {
          "x": -0.9777,
          "reference": 0.2,
          "current": 0.1269
        },
        {
          "x": -0.9106,
          "reference": 0.2192,
          "current": 0.1385
        },
        {
          "x": -0.8436,
          "reference": 0.2385,
          "current": 0.1577
        },
        {
          "x": -0.7765,
          "reference": 0.2692,
          "current": 0.1769
        },
        {
          "x": -0.7095,
          "reference": 0.2808,
          "current": 0.1808
        },
        {
          "x": -0.6425,
          "reference": 0.3038,
          "current": 0.1962
        },
        {
          "x": -0.5754,
          "reference": 0.3192,
          "current": 0.2154
        },
        {
          "x": -0.5084,
          "reference": 0.3423,
          "current": 0.2423
        },
        {
          "x": -0.4413,
          "reference": 0.3692,
          "current": 0.2615
        },
        {
          "x": -0.3743,
          "reference": 0.3846,
          "current": 0.2846
        },
        {
          "x": -0.3073,
          "reference": 0.4077,
          "current": 0.3115
        },
        {
          "x": -0.2402,
          "reference": 0.4231,
          "current": 0.3308
        },
        {
          "x": -0.1732,
          "reference": 0.4462,
          "current": 0.3692
        },
        {
          "x": -0.1061,
          "reference": 0.4692,
          "current": 0.4115
        },
        {
          "x": -0.0391,
          "reference": 0.5154,
          "current": 0.45
        },
        {
          "x": 0.0279,
          "reference": 0.5423,
          "current": 0.4654
        },
        {
          "x": 0.095,
          "reference": 0.5731,
          "current": 0.5
        },
        {
          "x": 0.162,
          "reference": 0.6038,
          "current": 0.5154
        },
        {
          "x": 0.2291,
          "reference": 0.6269,
          "current": 0.5462
        },
        {
          "x": 0.2961,
          "reference": 0.6385,
          "current": 0.5615
        },
        {
          "x": 0.3631,
          "reference": 0.6692,
          "current": 0.5923
        },
        {
          "x": 0.4302,
          "reference": 0.6923,
          "current": 0.6385
        },
        {
          "x": 0.4972,
          "reference": 0.7115,
          "current": 0.6577
        },
        {
          "x": 0.5642,
          "reference": 0.7423,
          "current": 0.6885
        },
        {
          "x": 0.6313,
          "reference": 0.7769,
          "current": 0.7231
        },
        {
          "x": 0.6983,
          "reference": 0.8,
          "current": 0.7462
        },
        {
          "x": 0.7654,
          "reference": 0.8115,
          "current": 0.7615
        },
        {
          "x": 0.8324,
          "reference": 0.8269,
          "current": 0.7962
        },
        {
          "x": 0.8994,
          "reference": 0.8346,
          "current": 0.8308
        },
        {
          "x": 0.9665,
          "reference": 0.8423,
          "current": 0.8346
        },
        {
          "x": 1.0335,
          "reference": 0.8577,
          "current": 0.8654
        },
        {
          "x": 1.1006,
          "reference": 0.8769,
          "current": 0.8692
        },
        {
          "x": 1.1676,
          "reference": 0.8846,
          "current": 0.8808
        },
        {
          "x": 1.2346,
          "reference": 0.9,
          "current": 0.8885
        },
        {
          "x": 1.3017,
          "reference": 0.9,
          "current": 0.8923
        },
        {
          "x": 1.3687,
          "reference": 0.9115,
          "current": 0.9038
        },
        {
          "x": 1.4358,
          "reference": 0.9115,
          "current": 0.9231
        },
        {
          "x": 1.5028,
          "reference": 0.9231,
          "current": 0.9269
        },
        {
          "x": 1.5698,
          "reference": 0.9346,
          "current": 0.9269
        },
        {
          "x": 1.6369,
          "reference": 0.9423,
          "current": 0.9308
        },
        {
          "x": 1.7039,
          "reference": 0.9462,
          "current": 0.9308
        },
        {
          "x": 1.7709,
          "reference": 0.95,
          "current": 0.9308
        },
        {
          "x": 1.838,
          "reference": 0.9577,
          "current": 0.9308
        },
        {
          "x": 1.905,
          "reference": 0.9577,
          "current": 0.9346
        },
        {
          "x": 1.9721,
          "reference": 0.9615,
          "current": 0.9385
        },
        {
          "x": 2.0391,
          "reference": 0.9615,
          "current": 0.9462
        },
        {
          "x": 2.1061,
          "reference": 0.9654,
          "current": 0.95
        },
        {
          "x": 2.1732,
          "reference": 0.9731,
          "current": 0.9577
        },
        {
          "x": 2.2402,
          "reference": 0.9731,
          "current": 0.9577
        },
        {
          "x": 2.3073,
          "reference": 0.9769,
          "current": 0.9615
        },
        {
          "x": 2.3743,
          "reference": 0.9769,
          "current": 0.9692
        },
        {
          "x": 2.4413,
          "reference": 0.9808,
          "current": 0.9692
        },
        {
          "x": 2.5084,
          "reference": 0.9808,
          "current": 0.9692
        },
        {
          "x": 2.5754,
          "reference": 0.9808,
          "current": 0.9692
        },
        {
          "x": 2.6425,
          "reference": 0.9923,
          "current": 0.9731
        },
        {
          "x": 2.7095,
          "reference": 0.9923,
          "current": 0.9731
        },
        {
          "x": 2.7765,
          "reference": 0.9923,
          "current": 0.9731
        },
        {
          "x": 2.8436,
          "reference": 0.9923,
          "current": 0.9731
        },
        {
          "x": 2.9106,
          "reference": 0.9923,
          "current": 0.9731
        },
        {
          "x": 2.9777,
          "reference": 0.9923,
          "current": 0.9769
        },
        {
          "x": 3.0447,
          "reference": 0.9923,
          "current": 0.9769
        },
        {
          "x": 3.1117,
          "reference": 0.9962,
          "current": 0.9769
        },
        {
          "x": 3.1788,
          "reference": 0.9962,
          "current": 0.9808
        },
        {
          "x": 3.2458,
          "reference": 0.9962,
          "current": 0.9846
        },
        {
          "x": 3.3128,
          "reference": 0.9962,
          "current": 0.9846
        },
        {
          "x": 3.3799,
          "reference": 0.9962,
          "current": 0.9846
        },
        {
          "x": 3.4469,
          "reference": 0.9962,
          "current": 0.9846
        },
        {
          "x": 3.514,
          "reference": 1.0,
          "current": 0.9885
        },
        {
          "x": 3.581,
          "reference": 1.0,
          "current": 0.9885
        },
        {
          "x": 3.648,
          "reference": 1.0,
          "current": 0.9885
        },
        {
          "x": 3.7151,
          "reference": 1.0,
          "current": 0.9885
        },
        {
          "x": 3.7821,
          "reference": 1.0,
          "current": 0.9923
        },
        {
          "x": 3.8492,
          "reference": 1.0,
          "current": 0.9923
        },
        {
          "x": 3.9162,
          "reference": 1.0,
          "current": 0.9923
        },
        {
          "x": 3.9832,
          "reference": 1.0,
          "current": 0.9923
        },
        {
          "x": 4.0503,
          "reference": 1.0,
          "current": 0.9923
        },
        {
          "x": 4.1173,
          "reference": 1.0,
          "current": 0.9923
        },
        {
          "x": 4.1844,
          "reference": 1.0,
          "current": 0.9923
        },
        {
          "x": 4.2514,
          "reference": 1.0,
          "current": 0.9923
        },
        {
          "x": 4.3184,
          "reference": 1.0,
          "current": 0.9923
        },
        {
          "x": 4.3855,
          "reference": 1.0,
          "current": 0.9923
        },
        {
          "x": 4.4525,
          "reference": 1.0,
          "current": 0.9923
        },
        {
          "x": 4.5196,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 4.5866,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 4.6536,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 4.7207,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 4.7877,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 4.8547,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 4.9218,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 4.9888,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 5.0559,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 5.1229,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 5.1899,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 5.257,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 5.324,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 5.3911,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 5.4581,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 5.5251,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 5.5922,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 5.6592,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 5.7263,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 5.7933,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 5.8603,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 5.9274,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 5.9944,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 6.0615,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 6.1285,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 6.1955,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 6.2626,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 6.3296,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 6.3966,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 6.4637,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 6.5307,
          "reference": 1.0,
          "current": 0.9962
        },
        {
          "x": 6.5978,
          "reference": 1.0,
          "current": 1.0
        },
        {
          "x": 6.6648,
          "reference": 1.0,
          "current": 1.0
        },
        {
          "x": 6.7318,
          "reference": 1.0,
          "current": 1.0
        },
        {
          "x": 6.7989,
          "reference": 1.0,
          "current": 1.0
        },
        {
          "x": 6.8659,
          "reference": 1.0,
          "current": 1.0
        },
        {
          "x": 6.933,
          "reference": 1.0,
          "current": 1.0
        },
        {
          "x": 7.0,
          "reference": 1.0,
          "current": 1.0
        }
      ],
      "chart.CHART-EDF-002.qq": [
        {
          "reference": -2.1374,
          "current": -2.3009,
          "group": "value",
          "r": 5
        },
        {
          "reference": -1.8566,
          "current": -1.6765,
          "group": "value",
          "r": 5
        },
        {
          "reference": -1.6296,
          "current": -1.3998,
          "group": "value",
          "r": 5
        },
        {
          "reference": -1.4847,
          "current": -1.2238,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": -1.3105,
          "current": -0.9801,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": -1.2159,
          "current": -0.8511,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": -1.0989,
          "current": -0.7759,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": -0.9725,
          "current": -0.6266,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": -0.8979,
          "current": -0.5396,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": -0.8229,
          "current": -0.4829,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": -0.7527,
          "current": -0.3879,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": -0.6467,
          "current": -0.3214,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": -0.5375,
          "current": -0.2816,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": -0.4723,
          "current": -0.2074,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": -0.3995,
          "current": -0.1668,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": -0.3297,
          "current": -0.1194,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": -0.2254,
          "current": -0.0662,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": -0.1648,
          "current": -0.0369,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": -0.0954,
          "current": 0.0362,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": -0.056,
          "current": 0.0994,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": -0.033,
          "current": 0.1861,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": 0.0468,
          "current": 0.2421,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": 0.1095,
          "current": 0.3369,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": 0.1436,
          "current": 0.3761,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": 0.2151,
          "current": 0.4126,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": 0.3395,
          "current": 0.4725,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": 0.3792,
          "current": 0.5104,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": 0.4492,
          "current": 0.5822,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": 0.521,
          "current": 0.6363,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": 0.5709,
          "current": 0.705,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": 0.6093,
          "current": 0.7803,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": 0.6787,
          "current": 0.8349,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": 0.8147,
          "current": 0.8794,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": 0.9913,
          "current": 0.9933,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": 1.0904,
          "current": 1.1314,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": 1.2257,
          "current": 1.3539,
          "group": "value",
          "r": 3.5
        },
        {
          "reference": 1.4908,
          "current": 1.4365,
          "group": "value",
          "r": 5
        },
        {
          "reference": 1.7185,
          "current": 2.0687,
          "group": "value",
          "r": 5
        },
        {
          "reference": 2.2037,
          "current": 2.7804,
          "group": "value",
          "r": 5
        }
      ],
      "chart.CHART-EDF-002.notes": [
        {
          "title": "해석",
          "text": "이 예시에서는 AD 통계량이 2.84, p-value가 0.012이고 tail 차이 요약은 0.50이다. 분위수-분위수 비교에서 상위 98% 분위수는 2.38에서 3.10, 상위 99% 분위수는 2.60에서 3.61로 벌어진다. 현재 구간의 상위 tail 극단값이 커진 drift 후보로 해석하되, outlier 처리 정책과 tail 표본 수를 함께 확인해야 한다.",
          "legend": [
            {
              "label": "기준 구간",
              "class": "swatch-reference"
            },
            {
              "label": "현재 구간",
              "class": "swatch-current-prop"
            },
            {
              "label": "Tail 강조 구간",
              "class": "swatch-tail"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-EDF-003",
    "title": "CHART-EDF-003 - 중간값 이후 누적되는 누적분포 차이로 보는 분포 변화",
    "originalPath": "./drift_report_charts/chart_edf_003.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_edf_003",
      "displayName": "CHART-EDF-003 source layout",
      "columns": 12,
      "rows": 3,
      "gridTemplateRows": "76px 508px 146px",
      "gap": "16px",
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 6,
          "h": 1,
          "title": "경험 누적분포 비교",
          "description": "x≈0.07에서 기준 CDF 0.550, 현재 CDF 0.436처럼 중간 구간 이후 차이가 반복되는지 본다.",
          "headerHeight": 62,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 16,
            "left": 16
          }
        },
        {
          "area": "side",
          "role": "secondary_visual",
          "x": 6,
          "y": 1,
          "w": 6,
          "h": 1,
          "title": "누적분포 제곱차 누적",
          "description": "누적 면적 0.014가 어느 값 범위부터 빠르게 쌓이는지 확인한다.",
          "headerHeight": 62,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 16,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "interpretation",
          "x": 0,
          "y": 2,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-EDF-003.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-EDF-003.summary"
        }
      },
      {
        "componentInstanceId": "CHART-EDF-003.cdf.0",
        "componentType": "cumulative_curve",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "x",
          "y_field": "reference",
          "secondary_value_field": "current",
          "x_min": -3.0,
          "x_max": 3.0,
          "y_min": 0,
          "y_max": 1,
          "view_box": [
            535,
            450
          ],
          "margin": {
            "top": 22,
            "right": 26,
            "bottom": 52,
            "left": 58
          },
          "x_ticks": [
            -3.0,
            0,
            3.0
          ],
          "y_ticks": [
            0,
            0.25,
            0.5,
            0.75,
            1
          ],
          "x_axis_label": "특성값",
          "y_axis_label": "경험 CDF",
          "line_class": "ref-line",
          "secondary_line_class": "cur-line",
          "show_points": false,
          "show_secondary_points": false,
          "gap_markers": [
            {
              "x": -1.3562,
              "upper_field": "reference",
              "lower_field": "current",
              "class": "gap-marker"
            },
            {
              "x": -1.1918,
              "upper_field": "reference",
              "lower_field": "current",
              "class": "gap-marker"
            },
            {
              "x": -1.0274,
              "upper_field": "reference",
              "lower_field": "current",
              "class": "gap-marker"
            },
            {
              "x": -0.863,
              "upper_field": "reference",
              "lower_field": "current",
              "class": "gap-marker"
            },
            {
              "x": -0.6986,
              "upper_field": "reference",
              "lower_field": "current",
              "class": "gap-marker"
            },
            {
              "x": -0.5342,
              "upper_field": "reference",
              "lower_field": "current",
              "class": "gap-marker"
            },
            {
              "x": -0.3699,
              "upper_field": "reference",
              "lower_field": "current",
              "class": "gap-marker"
            },
            {
              "x": -0.2055,
              "upper_field": "reference",
              "lower_field": "current",
              "class": "gap-marker"
            },
            {
              "x": -0.0411,
              "upper_field": "reference",
              "lower_field": "current",
              "class": "gap-marker"
            },
            {
              "x": 0.1233,
              "upper_field": "reference",
              "lower_field": "current",
              "class": "gap-marker"
            },
            {
              "x": 0.2877,
              "upper_field": "reference",
              "lower_field": "current",
              "class": "gap-marker"
            },
            {
              "x": 0.4521,
              "upper_field": "reference",
              "lower_field": "current",
              "class": "gap-marker"
            }
          ],
          "annotations": [
            {
              "text": "여러 구간의 작은 누적분포 차이를 함께 누적",
              "x": -2.86,
              "y": 0.95,
              "class": "callout"
            }
          ],
          "x_tick_format": "fixed1",
          "y_tick_format": "fixed1"
        },
        "dataBinding": {
          "source": "chart.CHART-EDF-003.cdf"
        }
      },
      {
        "componentInstanceId": "CHART-EDF-003.cvm.0",
        "componentType": "cumulative_curve",
        "area": "side",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "x",
          "y_field": "value",
          "x_min": -3.0,
          "x_max": 3.0,
          "y_min": 0,
          "y_max": 0.02,
          "view_box": [
            535,
            450
          ],
          "margin": {
            "top": 22,
            "right": 26,
            "bottom": 52,
            "left": 58
          },
          "x_ticks": [
            -3.0,
            0,
            3.0
          ],
          "y_ticks": [
            0,
            0.005,
            0.01,
            0.015,
            0.02
          ],
          "x_axis_label": "특성값",
          "y_axis_label": "누적 제곱 차이",
          "line_class": "cvm-line",
          "show_points": false,
          "area_under_line": {
            "baseline": 0,
            "class": "cvm-area"
          },
          "background_regions": [
            {
              "x0": -0.1115,
              "x1": 0.2485,
              "fill": "rgba(216, 161, 58, 0.16)"
            }
          ],
          "annotations": [
            {
              "text": "기여 증가 구간",
              "x": -0.4441,
              "y": 0.01112,
              "class": "callout"
            }
          ],
          "x_tick_format": "fixed1",
          "y_tick_format": "fixed3"
        },
        "dataBinding": {
          "source": "chart.CHART-EDF-003.cumulative"
        }
      },
      {
        "componentInstanceId": "CHART-EDF-003.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-EDF-003.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-EDF-003.summary": [
        {
          "label": "CvM 통계량",
          "value": 1.8914,
          "displayValue": "1.89"
        },
        {
          "label": "근사 p-value",
          "value": 0.018,
          "displayValue": "0.018"
        },
        {
          "label": "누적 면적",
          "value": 0.01351,
          "displayValue": "0.014"
        }
      ],
      "chart.CHART-EDF-003.cdf": [
        {
          "x": -3.0,
          "reference": 0.0,
          "current": 0.0
        },
        {
          "x": -2.9726,
          "reference": 0.0,
          "current": 0.0
        },
        {
          "x": -2.9452,
          "reference": 0.0,
          "current": 0.0
        },
        {
          "x": -2.9178,
          "reference": 0.0,
          "current": 0.0
        },
        {
          "x": -2.8904,
          "reference": 0.0,
          "current": 0.0
        },
        {
          "x": -2.863,
          "reference": 0.0036,
          "current": 0.0
        },
        {
          "x": -2.8356,
          "reference": 0.0036,
          "current": 0.0
        },
        {
          "x": -2.8082,
          "reference": 0.0036,
          "current": 0.0
        },
        {
          "x": -2.7808,
          "reference": 0.0036,
          "current": 0.0
        },
        {
          "x": -2.7534,
          "reference": 0.0036,
          "current": 0.0
        },
        {
          "x": -2.726,
          "reference": 0.0036,
          "current": 0.0
        },
        {
          "x": -2.6986,
          "reference": 0.0036,
          "current": 0.0
        },
        {
          "x": -2.6712,
          "reference": 0.0036,
          "current": 0.0036
        },
        {
          "x": -2.6438,
          "reference": 0.0036,
          "current": 0.0036
        },
        {
          "x": -2.6164,
          "reference": 0.0036,
          "current": 0.0036
        },
        {
          "x": -2.589,
          "reference": 0.0036,
          "current": 0.0036
        },
        {
          "x": -2.5616,
          "reference": 0.0036,
          "current": 0.0036
        },
        {
          "x": -2.5342,
          "reference": 0.0036,
          "current": 0.0036
        },
        {
          "x": -2.5068,
          "reference": 0.0036,
          "current": 0.0036
        },
        {
          "x": -2.4795,
          "reference": 0.0036,
          "current": 0.0071
        },
        {
          "x": -2.4521,
          "reference": 0.0036,
          "current": 0.0071
        },
        {
          "x": -2.4247,
          "reference": 0.0071,
          "current": 0.0071
        },
        {
          "x": -2.3973,
          "reference": 0.0071,
          "current": 0.0107
        },
        {
          "x": -2.3699,
          "reference": 0.0107,
          "current": 0.0107
        },
        {
          "x": -2.3425,
          "reference": 0.0107,
          "current": 0.0107
        },
        {
          "x": -2.3151,
          "reference": 0.0107,
          "current": 0.0143
        },
        {
          "x": -2.2877,
          "reference": 0.0107,
          "current": 0.0143
        },
        {
          "x": -2.2603,
          "reference": 0.0107,
          "current": 0.0143
        },
        {
          "x": -2.2329,
          "reference": 0.0107,
          "current": 0.0179
        },
        {
          "x": -2.2055,
          "reference": 0.0107,
          "current": 0.0214
        },
        {
          "x": -2.1781,
          "reference": 0.0179,
          "current": 0.0214
        },
        {
          "x": -2.1507,
          "reference": 0.0179,
          "current": 0.0214
        },
        {
          "x": -2.1233,
          "reference": 0.0179,
          "current": 0.0214
        },
        {
          "x": -2.0959,
          "reference": 0.0179,
          "current": 0.0321
        },
        {
          "x": -2.0685,
          "reference": 0.0214,
          "current": 0.0321
        },
        {
          "x": -2.0411,
          "reference": 0.025,
          "current": 0.0321
        },
        {
          "x": -2.0137,
          "reference": 0.0286,
          "current": 0.0321
        },
        {
          "x": -1.9863,
          "reference": 0.0286,
          "current": 0.0321
        },
        {
          "x": -1.9589,
          "reference": 0.0321,
          "current": 0.0357
        },
        {
          "x": -1.9315,
          "reference": 0.0357,
          "current": 0.0357
        },
        {
          "x": -1.9041,
          "reference": 0.0393,
          "current": 0.0357
        },
        {
          "x": -1.8767,
          "reference": 0.0429,
          "current": 0.0357
        },
        {
          "x": -1.8493,
          "reference": 0.0464,
          "current": 0.0429
        },
        {
          "x": -1.8219,
          "reference": 0.0571,
          "current": 0.05
        },
        {
          "x": -1.7945,
          "reference": 0.0643,
          "current": 0.05
        },
        {
          "x": -1.7671,
          "reference": 0.075,
          "current": 0.05
        },
        {
          "x": -1.7397,
          "reference": 0.075,
          "current": 0.05
        },
        {
          "x": -1.7123,
          "reference": 0.075,
          "current": 0.05
        },
        {
          "x": -1.6849,
          "reference": 0.075,
          "current": 0.05
        },
        {
          "x": -1.6575,
          "reference": 0.0821,
          "current": 0.05
        },
        {
          "x": -1.6301,
          "reference": 0.0857,
          "current": 0.0571
        },
        {
          "x": -1.6027,
          "reference": 0.0929,
          "current": 0.0571
        },
        {
          "x": -1.5753,
          "reference": 0.0964,
          "current": 0.0571
        },
        {
          "x": -1.5479,
          "reference": 0.1,
          "current": 0.0571
        },
        {
          "x": -1.5205,
          "reference": 0.1036,
          "current": 0.0607
        },
        {
          "x": -1.4932,
          "reference": 0.1143,
          "current": 0.0643
        },
        {
          "x": -1.4658,
          "reference": 0.1214,
          "current": 0.0643
        },
        {
          "x": -1.4384,
          "reference": 0.125,
          "current": 0.0679
        },
        {
          "x": -1.411,
          "reference": 0.125,
          "current": 0.0714
        },
        {
          "x": -1.3836,
          "reference": 0.1286,
          "current": 0.0786
        },
        {
          "x": -1.3562,
          "reference": 0.1357,
          "current": 0.0821
        },
        {
          "x": -1.3288,
          "reference": 0.1429,
          "current": 0.0857
        },
        {
          "x": -1.3014,
          "reference": 0.1429,
          "current": 0.0857
        },
        {
          "x": -1.274,
          "reference": 0.1429,
          "current": 0.0857
        },
        {
          "x": -1.2466,
          "reference": 0.15,
          "current": 0.0964
        },
        {
          "x": -1.2192,
          "reference": 0.1536,
          "current": 0.1
        },
        {
          "x": -1.1918,
          "reference": 0.1607,
          "current": 0.1036
        },
        {
          "x": -1.1644,
          "reference": 0.1714,
          "current": 0.1036
        },
        {
          "x": -1.137,
          "reference": 0.1714,
          "current": 0.1071
        },
        {
          "x": -1.1096,
          "reference": 0.1786,
          "current": 0.1071
        },
        {
          "x": -1.0822,
          "reference": 0.1929,
          "current": 0.1071
        },
        {
          "x": -1.0548,
          "reference": 0.1964,
          "current": 0.1143
        },
        {
          "x": -1.0274,
          "reference": 0.2,
          "current": 0.1143
        },
        {
          "x": -1.0,
          "reference": 0.2,
          "current": 0.125
        },
        {
          "x": -0.9726,
          "reference": 0.2036,
          "current": 0.1286
        },
        {
          "x": -0.9452,
          "reference": 0.2107,
          "current": 0.1393
        },
        {
          "x": -0.9178,
          "reference": 0.2143,
          "current": 0.1393
        },
        {
          "x": -0.8904,
          "reference": 0.2179,
          "current": 0.1429
        },
        {
          "x": -0.863,
          "reference": 0.225,
          "current": 0.1536
        },
        {
          "x": -0.8356,
          "reference": 0.225,
          "current": 0.1679
        },
        {
          "x": -0.8082,
          "reference": 0.2321,
          "current": 0.1821
        },
        {
          "x": -0.7808,
          "reference": 0.2357,
          "current": 0.1857
        },
        {
          "x": -0.7534,
          "reference": 0.2357,
          "current": 0.2
        },
        {
          "x": -0.726,
          "reference": 0.25,
          "current": 0.2143
        },
        {
          "x": -0.6986,
          "reference": 0.2643,
          "current": 0.2179
        },
        {
          "x": -0.6712,
          "reference": 0.2786,
          "current": 0.225
        },
        {
          "x": -0.6438,
          "reference": 0.2821,
          "current": 0.2286
        },
        {
          "x": -0.6164,
          "reference": 0.2964,
          "current": 0.2286
        },
        {
          "x": -0.589,
          "reference": 0.3071,
          "current": 0.2393
        },
        {
          "x": -0.5616,
          "reference": 0.3179,
          "current": 0.2464
        },
        {
          "x": -0.5342,
          "reference": 0.3286,
          "current": 0.2643
        },
        {
          "x": -0.5068,
          "reference": 0.3429,
          "current": 0.2679
        },
        {
          "x": -0.4795,
          "reference": 0.3464,
          "current": 0.275
        },
        {
          "x": -0.4521,
          "reference": 0.3571,
          "current": 0.2857
        },
        {
          "x": -0.4247,
          "reference": 0.3643,
          "current": 0.2964
        },
        {
          "x": -0.3973,
          "reference": 0.375,
          "current": 0.3
        },
        {
          "x": -0.3699,
          "reference": 0.3929,
          "current": 0.3107
        },
        {
          "x": -0.3425,
          "reference": 0.4071,
          "current": 0.3286
        },
        {
          "x": -0.3151,
          "reference": 0.4179,
          "current": 0.3286
        },
        {
          "x": -0.2877,
          "reference": 0.4214,
          "current": 0.3393
        },
        {
          "x": -0.2603,
          "reference": 0.4393,
          "current": 0.35
        },
        {
          "x": -0.2329,
          "reference": 0.45,
          "current": 0.35
        },
        {
          "x": -0.2055,
          "reference": 0.4607,
          "current": 0.3536
        },
        {
          "x": -0.1781,
          "reference": 0.4643,
          "current": 0.3607
        },
        {
          "x": -0.1507,
          "reference": 0.475,
          "current": 0.3679
        },
        {
          "x": -0.1233,
          "reference": 0.4821,
          "current": 0.3821
        },
        {
          "x": -0.0959,
          "reference": 0.4893,
          "current": 0.3893
        },
        {
          "x": -0.0685,
          "reference": 0.5,
          "current": 0.3929
        },
        {
          "x": -0.0411,
          "reference": 0.5214,
          "current": 0.4107
        },
        {
          "x": -0.0137,
          "reference": 0.525,
          "current": 0.4179
        },
        {
          "x": 0.0137,
          "reference": 0.525,
          "current": 0.4179
        },
        {
          "x": 0.0411,
          "reference": 0.5357,
          "current": 0.4321
        },
        {
          "x": 0.0685,
          "reference": 0.55,
          "current": 0.4357
        },
        {
          "x": 0.0959,
          "reference": 0.5571,
          "current": 0.4429
        },
        {
          "x": 0.1233,
          "reference": 0.5679,
          "current": 0.4571
        },
        {
          "x": 0.1507,
          "reference": 0.5679,
          "current": 0.4714
        },
        {
          "x": 0.1781,
          "reference": 0.575,
          "current": 0.4964
        },
        {
          "x": 0.2055,
          "reference": 0.5964,
          "current": 0.5143
        },
        {
          "x": 0.2329,
          "reference": 0.6107,
          "current": 0.5286
        },
        {
          "x": 0.2603,
          "reference": 0.6179,
          "current": 0.5393
        },
        {
          "x": 0.2877,
          "reference": 0.6286,
          "current": 0.5429
        },
        {
          "x": 0.3151,
          "reference": 0.6393,
          "current": 0.5571
        },
        {
          "x": 0.3425,
          "reference": 0.6464,
          "current": 0.5643
        },
        {
          "x": 0.3699,
          "reference": 0.6679,
          "current": 0.5714
        },
        {
          "x": 0.3973,
          "reference": 0.6786,
          "current": 0.5857
        },
        {
          "x": 0.4247,
          "reference": 0.6786,
          "current": 0.5964
        },
        {
          "x": 0.4521,
          "reference": 0.6857,
          "current": 0.6036
        },
        {
          "x": 0.4795,
          "reference": 0.6929,
          "current": 0.6214
        },
        {
          "x": 0.5068,
          "reference": 0.7071,
          "current": 0.6393
        },
        {
          "x": 0.5342,
          "reference": 0.7179,
          "current": 0.6464
        },
        {
          "x": 0.5616,
          "reference": 0.7214,
          "current": 0.6536
        },
        {
          "x": 0.589,
          "reference": 0.725,
          "current": 0.6679
        },
        {
          "x": 0.6164,
          "reference": 0.725,
          "current": 0.6821
        },
        {
          "x": 0.6438,
          "reference": 0.725,
          "current": 0.6964
        },
        {
          "x": 0.6712,
          "reference": 0.7321,
          "current": 0.7
        },
        {
          "x": 0.6986,
          "reference": 0.7393,
          "current": 0.7214
        },
        {
          "x": 0.726,
          "reference": 0.7464,
          "current": 0.7321
        },
        {
          "x": 0.7534,
          "reference": 0.7536,
          "current": 0.7464
        },
        {
          "x": 0.7808,
          "reference": 0.7536,
          "current": 0.75
        },
        {
          "x": 0.8082,
          "reference": 0.7607,
          "current": 0.7643
        },
        {
          "x": 0.8356,
          "reference": 0.7643,
          "current": 0.7643
        },
        {
          "x": 0.863,
          "reference": 0.7679,
          "current": 0.7679
        },
        {
          "x": 0.8904,
          "reference": 0.7857,
          "current": 0.7786
        },
        {
          "x": 0.9178,
          "reference": 0.7857,
          "current": 0.7857
        },
        {
          "x": 0.9452,
          "reference": 0.7929,
          "current": 0.7893
        },
        {
          "x": 0.9726,
          "reference": 0.7964,
          "current": 0.8071
        },
        {
          "x": 1.0,
          "reference": 0.7964,
          "current": 0.8107
        },
        {
          "x": 1.0274,
          "reference": 0.8036,
          "current": 0.825
        },
        {
          "x": 1.0548,
          "reference": 0.8214,
          "current": 0.8321
        },
        {
          "x": 1.0822,
          "reference": 0.8286,
          "current": 0.8464
        },
        {
          "x": 1.1096,
          "reference": 0.8286,
          "current": 0.8571
        },
        {
          "x": 1.137,
          "reference": 0.85,
          "current": 0.8607
        },
        {
          "x": 1.1644,
          "reference": 0.8714,
          "current": 0.8643
        },
        {
          "x": 1.1918,
          "reference": 0.8786,
          "current": 0.8821
        },
        {
          "x": 1.2192,
          "reference": 0.8821,
          "current": 0.8893
        },
        {
          "x": 1.2466,
          "reference": 0.8857,
          "current": 0.9
        },
        {
          "x": 1.274,
          "reference": 0.8929,
          "current": 0.9036
        },
        {
          "x": 1.3014,
          "reference": 0.8964,
          "current": 0.9107
        },
        {
          "x": 1.3288,
          "reference": 0.9036,
          "current": 0.9143
        },
        {
          "x": 1.3562,
          "reference": 0.9107,
          "current": 0.9179
        },
        {
          "x": 1.3836,
          "reference": 0.9143,
          "current": 0.9214
        },
        {
          "x": 1.411,
          "reference": 0.925,
          "current": 0.925
        },
        {
          "x": 1.4384,
          "reference": 0.9286,
          "current": 0.9286
        },
        {
          "x": 1.4658,
          "reference": 0.9393,
          "current": 0.9357
        },
        {
          "x": 1.4932,
          "reference": 0.9429,
          "current": 0.9429
        },
        {
          "x": 1.5205,
          "reference": 0.9429,
          "current": 0.9429
        },
        {
          "x": 1.5479,
          "reference": 0.9464,
          "current": 0.95
        },
        {
          "x": 1.5753,
          "reference": 0.95,
          "current": 0.9536
        },
        {
          "x": 1.6027,
          "reference": 0.9536,
          "current": 0.9536
        },
        {
          "x": 1.6301,
          "reference": 0.9536,
          "current": 0.9536
        },
        {
          "x": 1.6575,
          "reference": 0.9571,
          "current": 0.9536
        },
        {
          "x": 1.6849,
          "reference": 0.9643,
          "current": 0.9571
        },
        {
          "x": 1.7123,
          "reference": 0.9643,
          "current": 0.9571
        },
        {
          "x": 1.7397,
          "reference": 0.9679,
          "current": 0.9607
        },
        {
          "x": 1.7671,
          "reference": 0.9679,
          "current": 0.9607
        },
        {
          "x": 1.7945,
          "reference": 0.9714,
          "current": 0.9643
        },
        {
          "x": 1.8219,
          "reference": 0.975,
          "current": 0.9679
        },
        {
          "x": 1.8493,
          "reference": 0.975,
          "current": 0.9679
        },
        {
          "x": 1.8767,
          "reference": 0.975,
          "current": 0.9714
        },
        {
          "x": 1.9041,
          "reference": 0.9786,
          "current": 0.9786
        },
        {
          "x": 1.9315,
          "reference": 0.9821,
          "current": 0.9786
        },
        {
          "x": 1.9589,
          "reference": 0.9821,
          "current": 0.9786
        },
        {
          "x": 1.9863,
          "reference": 0.9857,
          "current": 0.9857
        },
        {
          "x": 2.0137,
          "reference": 0.9857,
          "current": 0.9857
        },
        {
          "x": 2.0411,
          "reference": 0.9893,
          "current": 0.9857
        },
        {
          "x": 2.0685,
          "reference": 0.9929,
          "current": 0.9857
        },
        {
          "x": 2.0959,
          "reference": 0.9964,
          "current": 0.9893
        },
        {
          "x": 2.1233,
          "reference": 0.9964,
          "current": 0.9893
        },
        {
          "x": 2.1507,
          "reference": 0.9964,
          "current": 0.9893
        },
        {
          "x": 2.1781,
          "reference": 0.9964,
          "current": 0.9893
        },
        {
          "x": 2.2055,
          "reference": 0.9964,
          "current": 0.9893
        },
        {
          "x": 2.2329,
          "reference": 0.9964,
          "current": 0.9893
        },
        {
          "x": 2.2603,
          "reference": 1.0,
          "current": 0.9893
        },
        {
          "x": 2.2877,
          "reference": 1.0,
          "current": 0.9893
        },
        {
          "x": 2.3151,
          "reference": 1.0,
          "current": 0.9893
        },
        {
          "x": 2.3425,
          "reference": 1.0,
          "current": 0.9929
        },
        {
          "x": 2.3699,
          "reference": 1.0,
          "current": 0.9929
        },
        {
          "x": 2.3973,
          "reference": 1.0,
          "current": 0.9964
        },
        {
          "x": 2.4247,
          "reference": 1.0,
          "current": 0.9964
        },
        {
          "x": 2.4521,
          "reference": 1.0,
          "current": 0.9964
        },
        {
          "x": 2.4795,
          "reference": 1.0,
          "current": 0.9964
        },
        {
          "x": 2.5068,
          "reference": 1.0,
          "current": 0.9964
        },
        {
          "x": 2.5342,
          "reference": 1.0,
          "current": 0.9964
        },
        {
          "x": 2.5616,
          "reference": 1.0,
          "current": 0.9964
        },
        {
          "x": 2.589,
          "reference": 1.0,
          "current": 0.9964
        },
        {
          "x": 2.6164,
          "reference": 1.0,
          "current": 1.0
        },
        {
          "x": 2.6438,
          "reference": 1.0,
          "current": 1.0
        },
        {
          "x": 2.6712,
          "reference": 1.0,
          "current": 1.0
        },
        {
          "x": 2.6986,
          "reference": 1.0,
          "current": 1.0
        },
        {
          "x": 2.726,
          "reference": 1.0,
          "current": 1.0
        },
        {
          "x": 2.7534,
          "reference": 1.0,
          "current": 1.0
        },
        {
          "x": 2.7808,
          "reference": 1.0,
          "current": 1.0
        },
        {
          "x": 2.8082,
          "reference": 1.0,
          "current": 1.0
        },
        {
          "x": 2.8356,
          "reference": 1.0,
          "current": 1.0
        },
        {
          "x": 2.863,
          "reference": 1.0,
          "current": 1.0
        },
        {
          "x": 2.8904,
          "reference": 1.0,
          "current": 1.0
        },
        {
          "x": 2.9178,
          "reference": 1.0,
          "current": 1.0
        },
        {
          "x": 2.9452,
          "reference": 1.0,
          "current": 1.0
        },
        {
          "x": 2.9726,
          "reference": 1.0,
          "current": 1.0
        },
        {
          "x": 3.0,
          "reference": 1.0,
          "current": 1.0
        }
      ],
      "chart.CHART-EDF-003.cumulative": [
        {
          "x": -3.0,
          "value": 0.0
        },
        {
          "x": -2.9726,
          "value": 0.0
        },
        {
          "x": -2.9452,
          "value": 0.0
        },
        {
          "x": -2.9178,
          "value": 0.0
        },
        {
          "x": -2.8904,
          "value": 0.0
        },
        {
          "x": -2.863,
          "value": 0.0
        },
        {
          "x": -2.8356,
          "value": 1e-06
        },
        {
          "x": -2.8082,
          "value": 1e-06
        },
        {
          "x": -2.7808,
          "value": 1e-06
        },
        {
          "x": -2.7534,
          "value": 2e-06
        },
        {
          "x": -2.726,
          "value": 2e-06
        },
        {
          "x": -2.6986,
          "value": 2e-06
        },
        {
          "x": -2.6712,
          "value": 2e-06
        },
        {
          "x": -2.6438,
          "value": 2e-06
        },
        {
          "x": -2.6164,
          "value": 2e-06
        },
        {
          "x": -2.589,
          "value": 2e-06
        },
        {
          "x": -2.5616,
          "value": 2e-06
        },
        {
          "x": -2.5342,
          "value": 2e-06
        },
        {
          "x": -2.5068,
          "value": 2e-06
        },
        {
          "x": -2.4795,
          "value": 3e-06
        },
        {
          "x": -2.4521,
          "value": 3e-06
        },
        {
          "x": -2.4247,
          "value": 3e-06
        },
        {
          "x": -2.3973,
          "value": 3e-06
        },
        {
          "x": -2.3699,
          "value": 3e-06
        },
        {
          "x": -2.3425,
          "value": 3e-06
        },
        {
          "x": -2.3151,
          "value": 4e-06
        },
        {
          "x": -2.2877,
          "value": 4e-06
        },
        {
          "x": -2.2603,
          "value": 5e-06
        },
        {
          "x": -2.2329,
          "value": 6e-06
        },
        {
          "x": -2.2055,
          "value": 9e-06
        },
        {
          "x": -2.1781,
          "value": 9e-06
        },
        {
          "x": -2.1507,
          "value": 1e-05
        },
        {
          "x": -2.1233,
          "value": 1e-05
        },
        {
          "x": -2.0959,
          "value": 1.6e-05
        },
        {
          "x": -2.0685,
          "value": 1.9e-05
        },
        {
          "x": -2.0411,
          "value": 2e-05
        },
        {
          "x": -2.0137,
          "value": 2.1e-05
        },
        {
          "x": -1.9863,
          "value": 2.1e-05
        },
        {
          "x": -1.9589,
          "value": 2.1e-05
        },
        {
          "x": -1.9315,
          "value": 2.1e-05
        },
        {
          "x": -1.9041,
          "value": 2.2e-05
        },
        {
          "x": -1.8767,
          "value": 2.3e-05
        },
        {
          "x": -1.8493,
          "value": 2.3e-05
        },
        {
          "x": -1.8219,
          "value": 2.5e-05
        },
        {
          "x": -1.7945,
          "value": 3e-05
        },
        {
          "x": -1.7671,
          "value": 4.8e-05
        },
        {
          "x": -1.7397,
          "value": 6.5e-05
        },
        {
          "x": -1.7123,
          "value": 8.2e-05
        },
        {
          "x": -1.6849,
          "value": 9.9e-05
        },
        {
          "x": -1.6575,
          "value": 0.000127
        },
        {
          "x": -1.6301,
          "value": 0.00015
        },
        {
          "x": -1.6027,
          "value": 0.000185
        },
        {
          "x": -1.5753,
          "value": 0.000227
        },
        {
          "x": -1.5479,
          "value": 0.000277
        },
        {
          "x": -1.5205,
          "value": 0.000327
        },
        {
          "x": -1.4932,
          "value": 0.000396
        },
        {
          "x": -1.4658,
          "value": 0.000485
        },
        {
          "x": -1.4384,
          "value": 0.000575
        },
        {
          "x": -1.411,
          "value": 0.000653
        },
        {
          "x": -1.3836,
          "value": 0.000722
        },
        {
          "x": -1.3562,
          "value": 0.000801
        },
        {
          "x": -1.3288,
          "value": 0.00089
        },
        {
          "x": -1.3014,
          "value": 0.00098
        },
        {
          "x": -1.274,
          "value": 0.001069
        },
        {
          "x": -1.2466,
          "value": 0.001148
        },
        {
          "x": -1.2192,
          "value": 0.001226
        },
        {
          "x": -1.1918,
          "value": 0.001316
        },
        {
          "x": -1.1644,
          "value": 0.001442
        },
        {
          "x": -1.137,
          "value": 0.001555
        },
        {
          "x": -1.1096,
          "value": 0.001695
        },
        {
          "x": -1.0822,
          "value": 0.001896
        },
        {
          "x": -1.0548,
          "value": 0.002081
        },
        {
          "x": -1.0274,
          "value": 0.002282
        },
        {
          "x": -1.0,
          "value": 0.002436
        },
        {
          "x": -0.9726,
          "value": 0.002591
        },
        {
          "x": -0.9452,
          "value": 0.00273
        },
        {
          "x": -0.9178,
          "value": 0.002884
        },
        {
          "x": -0.8904,
          "value": 0.003039
        },
        {
          "x": -0.863,
          "value": 0.003178
        },
        {
          "x": -0.8356,
          "value": 0.003268
        },
        {
          "x": -0.8082,
          "value": 0.003336
        },
        {
          "x": -0.7808,
          "value": 0.003405
        },
        {
          "x": -0.7534,
          "value": 0.00344
        },
        {
          "x": -0.726,
          "value": 0.003475
        },
        {
          "x": -0.6986,
          "value": 0.003534
        },
        {
          "x": -0.6712,
          "value": 0.003612
        },
        {
          "x": -0.6438,
          "value": 0.003691
        },
        {
          "x": -0.6164,
          "value": 0.003817
        },
        {
          "x": -0.589,
          "value": 0.003943
        },
        {
          "x": -0.5616,
          "value": 0.004083
        },
        {
          "x": -0.5342,
          "value": 0.004196
        },
        {
          "x": -0.5068,
          "value": 0.00435
        },
        {
          "x": -0.4795,
          "value": 0.00449
        },
        {
          "x": -0.4521,
          "value": 0.00463
        },
        {
          "x": -0.4247,
          "value": 0.004756
        },
        {
          "x": -0.3973,
          "value": 0.00491
        },
        {
          "x": -0.3699,
          "value": 0.005095
        },
        {
          "x": -0.3425,
          "value": 0.005264
        },
        {
          "x": -0.3151,
          "value": 0.005483
        },
        {
          "x": -0.2877,
          "value": 0.005667
        },
        {
          "x": -0.2603,
          "value": 0.005886
        },
        {
          "x": -0.2329,
          "value": 0.00616
        },
        {
          "x": -0.2055,
          "value": 0.006474
        },
        {
          "x": -0.1781,
          "value": 0.006768
        },
        {
          "x": -0.1507,
          "value": 0.007083
        },
        {
          "x": -0.1233,
          "value": 0.007357
        },
        {
          "x": -0.0959,
          "value": 0.007631
        },
        {
          "x": -0.0685,
          "value": 0.007945
        },
        {
          "x": -0.0411,
          "value": 0.008281
        },
        {
          "x": -0.0137,
          "value": 0.008596
        },
        {
          "x": 0.0137,
          "value": 0.00891
        },
        {
          "x": 0.0411,
          "value": 0.009204
        },
        {
          "x": 0.0685,
          "value": 0.009562
        },
        {
          "x": 0.0959,
          "value": 0.00992
        },
        {
          "x": 0.1233,
          "value": 0.010255
        },
        {
          "x": 0.1507,
          "value": 0.01051
        },
        {
          "x": 0.1781,
          "value": 0.010679
        },
        {
          "x": 0.2055,
          "value": 0.010864
        },
        {
          "x": 0.2329,
          "value": 0.011049
        },
        {
          "x": 0.2603,
          "value": 0.011218
        },
        {
          "x": 0.2877,
          "value": 0.011419
        },
        {
          "x": 0.3151,
          "value": 0.011604
        },
        {
          "x": 0.3425,
          "value": 0.011789
        },
        {
          "x": 0.3699,
          "value": 0.012044
        },
        {
          "x": 0.3973,
          "value": 0.01228
        },
        {
          "x": 0.4247,
          "value": 0.012465
        },
        {
          "x": 0.4521,
          "value": 0.01265
        },
        {
          "x": 0.4795,
          "value": 0.01279
        },
        {
          "x": 0.5068,
          "value": 0.012916
        },
        {
          "x": 0.5342,
          "value": 0.013056
        },
        {
          "x": 0.5616,
          "value": 0.013182
        },
        {
          "x": 0.589,
          "value": 0.013271
        },
        {
          "x": 0.6164,
          "value": 0.013322
        },
        {
          "x": 0.6438,
          "value": 0.013344
        },
        {
          "x": 0.6712,
          "value": 0.013372
        },
        {
          "x": 0.6986,
          "value": 0.013381
        },
        {
          "x": 0.726,
          "value": 0.013387
        },
        {
          "x": 0.7534,
          "value": 0.013388
        },
        {
          "x": 0.7808,
          "value": 0.013388
        },
        {
          "x": 0.8082,
          "value": 0.013389
        },
        {
          "x": 0.8356,
          "value": 0.013389
        },
        {
          "x": 0.863,
          "value": 0.013389
        },
        {
          "x": 0.8904,
          "value": 0.01339
        },
        {
          "x": 0.9178,
          "value": 0.01339
        },
        {
          "x": 0.9452,
          "value": 0.01339
        },
        {
          "x": 0.9726,
          "value": 0.013394
        },
        {
          "x": 1.0,
          "value": 0.013399
        },
        {
          "x": 1.0274,
          "value": 0.013412
        },
        {
          "x": 1.0548,
          "value": 0.013415
        },
        {
          "x": 1.0822,
          "value": 0.013424
        },
        {
          "x": 1.1096,
          "value": 0.013446
        },
        {
          "x": 1.137,
          "value": 0.013449
        },
        {
          "x": 1.1644,
          "value": 0.013451
        },
        {
          "x": 1.1918,
          "value": 0.013451
        },
        {
          "x": 1.2192,
          "value": 0.013452
        },
        {
          "x": 1.2466,
          "value": 0.013458
        },
        {
          "x": 1.274,
          "value": 0.013461
        },
        {
          "x": 1.3014,
          "value": 0.013467
        },
        {
          "x": 1.3288,
          "value": 0.01347
        },
        {
          "x": 1.3562,
          "value": 0.013471
        },
        {
          "x": 1.3836,
          "value": 0.013473
        },
        {
          "x": 1.411,
          "value": 0.013473
        },
        {
          "x": 1.4384,
          "value": 0.013473
        },
        {
          "x": 1.4658,
          "value": 0.013473
        },
        {
          "x": 1.4932,
          "value": 0.013473
        },
        {
          "x": 1.5205,
          "value": 0.013473
        },
        {
          "x": 1.5479,
          "value": 0.013473
        },
        {
          "x": 1.5753,
          "value": 0.013474
        },
        {
          "x": 1.6027,
          "value": 0.013474
        },
        {
          "x": 1.6301,
          "value": 0.013474
        },
        {
          "x": 1.6575,
          "value": 0.013474
        },
        {
          "x": 1.6849,
          "value": 0.013475
        },
        {
          "x": 1.7123,
          "value": 0.013477
        },
        {
          "x": 1.7397,
          "value": 0.013478
        },
        {
          "x": 1.7671,
          "value": 0.01348
        },
        {
          "x": 1.7945,
          "value": 0.013481
        },
        {
          "x": 1.8219,
          "value": 0.013482
        },
        {
          "x": 1.8493,
          "value": 0.013484
        },
        {
          "x": 1.8767,
          "value": 0.013484
        },
        {
          "x": 1.9041,
          "value": 0.013484
        },
        {
          "x": 1.9315,
          "value": 0.013484
        },
        {
          "x": 1.9589,
          "value": 0.013485
        },
        {
          "x": 1.9863,
          "value": 0.013485
        },
        {
          "x": 2.0137,
          "value": 0.013485
        },
        {
          "x": 2.0411,
          "value": 0.013485
        },
        {
          "x": 2.0685,
          "value": 0.013487
        },
        {
          "x": 2.0959,
          "value": 0.013488
        },
        {
          "x": 2.1233,
          "value": 0.013489
        },
        {
          "x": 2.1507,
          "value": 0.013491
        },
        {
          "x": 2.1781,
          "value": 0.013492
        },
        {
          "x": 2.2055,
          "value": 0.013494
        },
        {
          "x": 2.2329,
          "value": 0.013495
        },
        {
          "x": 2.2603,
          "value": 0.013498
        },
        {
          "x": 2.2877,
          "value": 0.013501
        },
        {
          "x": 2.3151,
          "value": 0.013504
        },
        {
          "x": 2.3425,
          "value": 0.013506
        },
        {
          "x": 2.3699,
          "value": 0.013507
        },
        {
          "x": 2.3973,
          "value": 0.013507
        },
        {
          "x": 2.4247,
          "value": 0.013508
        },
        {
          "x": 2.4521,
          "value": 0.013508
        },
        {
          "x": 2.4795,
          "value": 0.013509
        },
        {
          "x": 2.5068,
          "value": 0.013509
        },
        {
          "x": 2.5342,
          "value": 0.013509
        },
        {
          "x": 2.5616,
          "value": 0.01351
        },
        {
          "x": 2.589,
          "value": 0.01351
        },
        {
          "x": 2.6164,
          "value": 0.01351
        },
        {
          "x": 2.6438,
          "value": 0.01351
        },
        {
          "x": 2.6712,
          "value": 0.01351
        },
        {
          "x": 2.6986,
          "value": 0.01351
        },
        {
          "x": 2.726,
          "value": 0.01351
        },
        {
          "x": 2.7534,
          "value": 0.01351
        },
        {
          "x": 2.7808,
          "value": 0.01351
        },
        {
          "x": 2.8082,
          "value": 0.01351
        },
        {
          "x": 2.8356,
          "value": 0.01351
        },
        {
          "x": 2.863,
          "value": 0.01351
        },
        {
          "x": 2.8904,
          "value": 0.01351
        },
        {
          "x": 2.9178,
          "value": 0.01351
        },
        {
          "x": 2.9452,
          "value": 0.01351
        },
        {
          "x": 2.9726,
          "value": 0.01351
        },
        {
          "x": 3.0,
          "value": 0.01351
        }
      ],
      "chart.CHART-EDF-003.notes": [
        {
          "title": "해석",
          "text": "이 예시에서는 CvM 통계량이 1.89, p-value가 0.018이고 누적 면적은 0.014다. x≈0.07에서 기준 CDF 0.550과 현재 CDF 0.436의 차이가 크며, 중간값 이후 여러 구간에서 작은 누적분포 차이가 반복적으로 누적된다. 단일 최대 편차보다 전체 분포 형태의 누적 변화 후보로 해석하되, 어떤 feature/source가 원인인지는 별도 확인한다.",
          "legend": [
            {
              "label": "기준 구간",
              "class": "swatch-reference"
            },
            {
              "label": "현재 구간",
              "class": "swatch-current-prop"
            },
            {
              "label": "누적분포 차이",
              "class": "swatch-cdf-gap"
            },
            {
              "label": "누적 기여",
              "class": "swatch-cumulative"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-EDF-004",
    "title": "CHART-EDF-004 - 원형 데이터의 피크 각도 이동과 누적분포 편차",
    "originalPath": "./drift_report_charts/chart_edf_004.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_edf_004",
      "displayName": "CHART-EDF-004 source layout",
      "columns": 12,
      "rows": 3,
      "gridTemplateRows": "76px 508px 146px",
      "gap": "16px",
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 6,
          "h": 1,
          "title": "경험누적분포 양/음 편차",
          "description": "49.5° 부근에서 D-=0.365가 크게 나타나고 D+=0.012는 작은지 확인한다.",
          "headerHeight": 62,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 16,
            "left": 16
          }
        },
        {
          "area": "side",
          "role": "secondary_visual",
          "x": 6,
          "y": 1,
          "w": 6,
          "h": 1,
          "title": "원형 히스토그램",
          "description": "기준 peak가 20~40°에 집중된 반면 현재는 40~80°와 240~260° 쪽으로 이동했는지 본다.",
          "headerHeight": 62,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 16,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "interpretation",
          "x": 0,
          "y": 2,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-EDF-004.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-EDF-004.summary"
        }
      },
      {
        "componentInstanceId": "CHART-EDF-004.deviation.0",
        "componentType": "cumulative_curve",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "angle",
          "y_field": "diff",
          "x_min": 0,
          "x_max": 360,
          "y_min": -0.39,
          "y_max": 0.39,
          "view_box": [
            535,
            450
          ],
          "margin": {
            "top": 22,
            "right": 26,
            "bottom": 52,
            "left": 58
          },
          "x_ticks": [
            0,
            90,
            180,
            270,
            360
          ],
          "y_ticks": [
            -0.39,
            -0.195,
            0,
            0.195,
            0.39
          ],
          "x_tick_suffix": "°",
          "x_axis_label": "각도 또는 순환 위치",
          "y_axis_label": "현재 CDF - 기준 CDF",
          "line_class": "dev-line",
          "show_points": false,
          "signed_area_under_line": {
            "baseline": 0,
            "positive_class": "pos-area",
            "negative_class": "neg-area"
          },
          "horizontal_markers": [
            {
              "y": 0,
              "class": "zero-line"
            }
          ],
          "vertical_markers": [],
          "annotations": [
            {
              "text": "D+ 0.012",
              "x": 328.5,
              "y": 0.031538,
              "class": "callout-strong"
            },
            {
              "text": "D- 0.365",
              "x": 55.5,
              "y": -0.405385,
              "class": "callout-strong"
            }
          ],
          "y_tick_format": "fixed2",
          "gap_markers": [
            {
              "x": 322.5,
              "upper_field": "diff",
              "lower_field": "zero",
              "class": "pos-marker"
            },
            {
              "x": 49.5,
              "upper_field": "zero",
              "lower_field": "diff",
              "class": "neg-marker"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-EDF-004.deviation"
        }
      },
      {
        "componentInstanceId": "CHART-EDF-004.circular.0",
        "componentType": "circular_histogram",
        "area": "side",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "start_field": "start",
          "end_field": "end",
          "mid_field": "mid",
          "primary_value_field": "reference",
          "secondary_value_field": "current",
          "label_field": "label",
          "view_box": [
            535,
            450
          ],
          "cx": 268,
          "cy": 224,
          "inner_radius": 70,
          "max_radius": 176,
          "primary_radius_span": 78,
          "secondary_radius_span": 112,
          "secondary_inner_offset": 36,
          "secondary_radius_base_offset": 0,
          "secondary_allow_inverted_radius": true,
          "primary_bar_class": "ref-bar",
          "secondary_bar_class": "cur-bar",
          "ring_class": "ring",
          "angle_labels": [
            0,
            90,
            180,
            270
          ],
          "angle_label_suffix": "°",
          "label_class": "callout",
          "annotations": [
            {
              "text": "기준/현재 peak 각도 이동",
              "x": 268,
              "y": 228,
              "class": "callout-strong",
              "anchor": "middle"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-EDF-004.circular"
        }
      },
      {
        "componentInstanceId": "CHART-EDF-004.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-EDF-004.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-EDF-004.summary": [
        {
          "label": "Kuiper V",
          "value": 0.377,
          "displayValue": "0.377"
        },
        {
          "label": "D+ / D-",
          "value": 1,
          "displayValue": "0.012 / 0.365"
        },
        {
          "label": "근사 p-value",
          "value": 0.009,
          "displayValue": "0.009"
        }
      ],
      "chart.CHART-EDF-004.deviation": [
        {
          "angle": 0.0,
          "diff": 0.0,
          "zero": 0
        },
        {
          "angle": 1.5,
          "diff": 0.0,
          "zero": 0
        },
        {
          "angle": 3.0,
          "diff": -0.003846,
          "zero": 0
        },
        {
          "angle": 4.5,
          "diff": -0.003846,
          "zero": 0
        },
        {
          "angle": 6.0,
          "diff": -0.007692,
          "zero": 0
        },
        {
          "angle": 7.5,
          "diff": -0.011538,
          "zero": 0
        },
        {
          "angle": 9.0,
          "diff": -0.019231,
          "zero": 0
        },
        {
          "angle": 10.5,
          "diff": -0.026923,
          "zero": 0
        },
        {
          "angle": 12.0,
          "diff": -0.034615,
          "zero": 0
        },
        {
          "angle": 13.5,
          "diff": -0.042308,
          "zero": 0
        },
        {
          "angle": 15.0,
          "diff": -0.038462,
          "zero": 0
        },
        {
          "angle": 16.5,
          "diff": -0.046154,
          "zero": 0
        },
        {
          "angle": 18.0,
          "diff": -0.05,
          "zero": 0
        },
        {
          "angle": 19.5,
          "diff": -0.061538,
          "zero": 0
        },
        {
          "angle": 21.0,
          "diff": -0.076923,
          "zero": 0
        },
        {
          "angle": 22.5,
          "diff": -0.084615,
          "zero": 0
        },
        {
          "angle": 24.0,
          "diff": -0.103846,
          "zero": 0
        },
        {
          "angle": 25.5,
          "diff": -0.119231,
          "zero": 0
        },
        {
          "angle": 27.0,
          "diff": -0.146154,
          "zero": 0
        },
        {
          "angle": 28.5,
          "diff": -0.161538,
          "zero": 0
        },
        {
          "angle": 30.0,
          "diff": -0.169231,
          "zero": 0
        },
        {
          "angle": 31.5,
          "diff": -0.184615,
          "zero": 0
        },
        {
          "angle": 33.0,
          "diff": -0.219231,
          "zero": 0
        },
        {
          "angle": 34.5,
          "diff": -0.234615,
          "zero": 0
        },
        {
          "angle": 36.0,
          "diff": -0.265385,
          "zero": 0
        },
        {
          "angle": 37.5,
          "diff": -0.280769,
          "zero": 0
        },
        {
          "angle": 39.0,
          "diff": -0.292308,
          "zero": 0
        },
        {
          "angle": 40.5,
          "diff": -0.303846,
          "zero": 0
        },
        {
          "angle": 42.0,
          "diff": -0.315385,
          "zero": 0
        },
        {
          "angle": 43.5,
          "diff": -0.315385,
          "zero": 0
        },
        {
          "angle": 45.0,
          "diff": -0.334615,
          "zero": 0
        },
        {
          "angle": 46.5,
          "diff": -0.334615,
          "zero": 0
        },
        {
          "angle": 48.0,
          "diff": -0.35,
          "zero": 0
        },
        {
          "angle": 49.5,
          "diff": -0.365385,
          "zero": 0
        },
        {
          "angle": 51.0,
          "diff": -0.365385,
          "zero": 0
        },
        {
          "angle": 52.5,
          "diff": -0.35,
          "zero": 0
        },
        {
          "angle": 54.0,
          "diff": -0.346154,
          "zero": 0
        },
        {
          "angle": 55.5,
          "diff": -0.319231,
          "zero": 0
        },
        {
          "angle": 57.0,
          "diff": -0.311538,
          "zero": 0
        },
        {
          "angle": 58.5,
          "diff": -0.3,
          "zero": 0
        },
        {
          "angle": 60.0,
          "diff": -0.3,
          "zero": 0
        },
        {
          "angle": 61.5,
          "diff": -0.296154,
          "zero": 0
        },
        {
          "angle": 63.0,
          "diff": -0.288462,
          "zero": 0
        },
        {
          "angle": 64.5,
          "diff": -0.296154,
          "zero": 0
        },
        {
          "angle": 66.0,
          "diff": -0.288462,
          "zero": 0
        },
        {
          "angle": 67.5,
          "diff": -0.276923,
          "zero": 0
        },
        {
          "angle": 69.0,
          "diff": -0.273077,
          "zero": 0
        },
        {
          "angle": 70.5,
          "diff": -0.253846,
          "zero": 0
        },
        {
          "angle": 72.0,
          "diff": -0.257692,
          "zero": 0
        },
        {
          "angle": 73.5,
          "diff": -0.238462,
          "zero": 0
        },
        {
          "angle": 75.0,
          "diff": -0.226923,
          "zero": 0
        },
        {
          "angle": 76.5,
          "diff": -0.211538,
          "zero": 0
        },
        {
          "angle": 78.0,
          "diff": -0.2,
          "zero": 0
        },
        {
          "angle": 79.5,
          "diff": -0.188462,
          "zero": 0
        },
        {
          "angle": 81.0,
          "diff": -0.176923,
          "zero": 0
        },
        {
          "angle": 82.5,
          "diff": -0.176923,
          "zero": 0
        },
        {
          "angle": 84.0,
          "diff": -0.173077,
          "zero": 0
        },
        {
          "angle": 85.5,
          "diff": -0.169231,
          "zero": 0
        },
        {
          "angle": 87.0,
          "diff": -0.161538,
          "zero": 0
        },
        {
          "angle": 88.5,
          "diff": -0.153846,
          "zero": 0
        },
        {
          "angle": 90.0,
          "diff": -0.146154,
          "zero": 0
        },
        {
          "angle": 91.5,
          "diff": -0.142308,
          "zero": 0
        },
        {
          "angle": 93.0,
          "diff": -0.138462,
          "zero": 0
        },
        {
          "angle": 94.5,
          "diff": -0.134615,
          "zero": 0
        },
        {
          "angle": 96.0,
          "diff": -0.134615,
          "zero": 0
        },
        {
          "angle": 97.5,
          "diff": -0.134615,
          "zero": 0
        },
        {
          "angle": 99.0,
          "diff": -0.130769,
          "zero": 0
        },
        {
          "angle": 100.5,
          "diff": -0.123077,
          "zero": 0
        },
        {
          "angle": 102.0,
          "diff": -0.119231,
          "zero": 0
        },
        {
          "angle": 103.5,
          "diff": -0.115385,
          "zero": 0
        },
        {
          "angle": 105.0,
          "diff": -0.107692,
          "zero": 0
        },
        {
          "angle": 106.5,
          "diff": -0.107692,
          "zero": 0
        },
        {
          "angle": 108.0,
          "diff": -0.107692,
          "zero": 0
        },
        {
          "angle": 109.5,
          "diff": -0.107692,
          "zero": 0
        },
        {
          "angle": 111.0,
          "diff": -0.103846,
          "zero": 0
        },
        {
          "angle": 112.5,
          "diff": -0.103846,
          "zero": 0
        },
        {
          "angle": 114.0,
          "diff": -0.103846,
          "zero": 0
        },
        {
          "angle": 115.5,
          "diff": -0.1,
          "zero": 0
        },
        {
          "angle": 117.0,
          "diff": -0.1,
          "zero": 0
        },
        {
          "angle": 118.5,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 120.0,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 121.5,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 123.0,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 124.5,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 126.0,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 127.5,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 129.0,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 130.5,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 132.0,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 133.5,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 135.0,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 136.5,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 138.0,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 139.5,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 141.0,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 142.5,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 144.0,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 145.5,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 147.0,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 148.5,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 150.0,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 151.5,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 153.0,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 154.5,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 156.0,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 157.5,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 159.0,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 160.5,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 162.0,
          "diff": -0.096154,
          "zero": 0
        },
        {
          "angle": 163.5,
          "diff": -0.103846,
          "zero": 0
        },
        {
          "angle": 165.0,
          "diff": -0.107692,
          "zero": 0
        },
        {
          "angle": 166.5,
          "diff": -0.107692,
          "zero": 0
        },
        {
          "angle": 168.0,
          "diff": -0.107692,
          "zero": 0
        },
        {
          "angle": 169.5,
          "diff": -0.111538,
          "zero": 0
        },
        {
          "angle": 171.0,
          "diff": -0.111538,
          "zero": 0
        },
        {
          "angle": 172.5,
          "diff": -0.111538,
          "zero": 0
        },
        {
          "angle": 174.0,
          "diff": -0.115385,
          "zero": 0
        },
        {
          "angle": 175.5,
          "diff": -0.115385,
          "zero": 0
        },
        {
          "angle": 177.0,
          "diff": -0.115385,
          "zero": 0
        },
        {
          "angle": 178.5,
          "diff": -0.123077,
          "zero": 0
        },
        {
          "angle": 180.0,
          "diff": -0.123077,
          "zero": 0
        },
        {
          "angle": 181.5,
          "diff": -0.130769,
          "zero": 0
        },
        {
          "angle": 183.0,
          "diff": -0.130769,
          "zero": 0
        },
        {
          "angle": 184.5,
          "diff": -0.138462,
          "zero": 0
        },
        {
          "angle": 186.0,
          "diff": -0.138462,
          "zero": 0
        },
        {
          "angle": 187.5,
          "diff": -0.142308,
          "zero": 0
        },
        {
          "angle": 189.0,
          "diff": -0.153846,
          "zero": 0
        },
        {
          "angle": 190.5,
          "diff": -0.153846,
          "zero": 0
        },
        {
          "angle": 192.0,
          "diff": -0.157692,
          "zero": 0
        },
        {
          "angle": 193.5,
          "diff": -0.157692,
          "zero": 0
        },
        {
          "angle": 195.0,
          "diff": -0.161538,
          "zero": 0
        },
        {
          "angle": 196.5,
          "diff": -0.173077,
          "zero": 0
        },
        {
          "angle": 198.0,
          "diff": -0.173077,
          "zero": 0
        },
        {
          "angle": 199.5,
          "diff": -0.176923,
          "zero": 0
        },
        {
          "angle": 201.0,
          "diff": -0.180769,
          "zero": 0
        },
        {
          "angle": 202.5,
          "diff": -0.184615,
          "zero": 0
        },
        {
          "angle": 204.0,
          "diff": -0.2,
          "zero": 0
        },
        {
          "angle": 205.5,
          "diff": -0.203846,
          "zero": 0
        },
        {
          "angle": 207.0,
          "diff": -0.215385,
          "zero": 0
        },
        {
          "angle": 208.5,
          "diff": -0.211538,
          "zero": 0
        },
        {
          "angle": 210.0,
          "diff": -0.219231,
          "zero": 0
        },
        {
          "angle": 211.5,
          "diff": -0.238462,
          "zero": 0
        },
        {
          "angle": 213.0,
          "diff": -0.234615,
          "zero": 0
        },
        {
          "angle": 214.5,
          "diff": -0.242308,
          "zero": 0
        },
        {
          "angle": 216.0,
          "diff": -0.25,
          "zero": 0
        },
        {
          "angle": 217.5,
          "diff": -0.253846,
          "zero": 0
        },
        {
          "angle": 219.0,
          "diff": -0.257692,
          "zero": 0
        },
        {
          "angle": 220.5,
          "diff": -0.257692,
          "zero": 0
        },
        {
          "angle": 222.0,
          "diff": -0.276923,
          "zero": 0
        },
        {
          "angle": 223.5,
          "diff": -0.280769,
          "zero": 0
        },
        {
          "angle": 225.0,
          "diff": -0.280769,
          "zero": 0
        },
        {
          "angle": 226.5,
          "diff": -0.284615,
          "zero": 0
        },
        {
          "angle": 228.0,
          "diff": -0.280769,
          "zero": 0
        },
        {
          "angle": 229.5,
          "diff": -0.280769,
          "zero": 0
        },
        {
          "angle": 231.0,
          "diff": -0.284615,
          "zero": 0
        },
        {
          "angle": 232.5,
          "diff": -0.273077,
          "zero": 0
        },
        {
          "angle": 234.0,
          "diff": -0.276923,
          "zero": 0
        },
        {
          "angle": 235.5,
          "diff": -0.265385,
          "zero": 0
        },
        {
          "angle": 237.0,
          "diff": -0.273077,
          "zero": 0
        },
        {
          "angle": 238.5,
          "diff": -0.265385,
          "zero": 0
        },
        {
          "angle": 240.0,
          "diff": -0.25,
          "zero": 0
        },
        {
          "angle": 241.5,
          "diff": -0.25,
          "zero": 0
        },
        {
          "angle": 243.0,
          "diff": -0.238462,
          "zero": 0
        },
        {
          "angle": 244.5,
          "diff": -0.238462,
          "zero": 0
        },
        {
          "angle": 246.0,
          "diff": -0.234615,
          "zero": 0
        },
        {
          "angle": 247.5,
          "diff": -0.219231,
          "zero": 0
        },
        {
          "angle": 249.0,
          "diff": -0.223077,
          "zero": 0
        },
        {
          "angle": 250.5,
          "diff": -0.211538,
          "zero": 0
        },
        {
          "angle": 252.0,
          "diff": -0.2,
          "zero": 0
        },
        {
          "angle": 253.5,
          "diff": -0.184615,
          "zero": 0
        },
        {
          "angle": 255.0,
          "diff": -0.184615,
          "zero": 0
        },
        {
          "angle": 256.5,
          "diff": -0.169231,
          "zero": 0
        },
        {
          "angle": 258.0,
          "diff": -0.15,
          "zero": 0
        },
        {
          "angle": 259.5,
          "diff": -0.138462,
          "zero": 0
        },
        {
          "angle": 261.0,
          "diff": -0.126923,
          "zero": 0
        },
        {
          "angle": 262.5,
          "diff": -0.123077,
          "zero": 0
        },
        {
          "angle": 264.0,
          "diff": -0.115385,
          "zero": 0
        },
        {
          "angle": 265.5,
          "diff": -0.103846,
          "zero": 0
        },
        {
          "angle": 267.0,
          "diff": -0.1,
          "zero": 0
        },
        {
          "angle": 268.5,
          "diff": -0.084615,
          "zero": 0
        },
        {
          "angle": 270.0,
          "diff": -0.076923,
          "zero": 0
        },
        {
          "angle": 271.5,
          "diff": -0.069231,
          "zero": 0
        },
        {
          "angle": 273.0,
          "diff": -0.069231,
          "zero": 0
        },
        {
          "angle": 274.5,
          "diff": -0.061538,
          "zero": 0
        },
        {
          "angle": 276.0,
          "diff": -0.05,
          "zero": 0
        },
        {
          "angle": 277.5,
          "diff": -0.046154,
          "zero": 0
        },
        {
          "angle": 279.0,
          "diff": -0.038462,
          "zero": 0
        },
        {
          "angle": 280.5,
          "diff": -0.038462,
          "zero": 0
        },
        {
          "angle": 282.0,
          "diff": -0.038462,
          "zero": 0
        },
        {
          "angle": 283.5,
          "diff": -0.030769,
          "zero": 0
        },
        {
          "angle": 285.0,
          "diff": -0.026923,
          "zero": 0
        },
        {
          "angle": 286.5,
          "diff": -0.019231,
          "zero": 0
        },
        {
          "angle": 288.0,
          "diff": -0.019231,
          "zero": 0
        },
        {
          "angle": 289.5,
          "diff": -0.015385,
          "zero": 0
        },
        {
          "angle": 291.0,
          "diff": -0.011538,
          "zero": 0
        },
        {
          "angle": 292.5,
          "diff": -0.007692,
          "zero": 0
        },
        {
          "angle": 294.0,
          "diff": -0.007692,
          "zero": 0
        },
        {
          "angle": 295.5,
          "diff": -0.007692,
          "zero": 0
        },
        {
          "angle": 297.0,
          "diff": -0.007692,
          "zero": 0
        },
        {
          "angle": 298.5,
          "diff": -0.007692,
          "zero": 0
        },
        {
          "angle": 300.0,
          "diff": -0.007692,
          "zero": 0
        },
        {
          "angle": 301.5,
          "diff": 0.0,
          "zero": 0
        },
        {
          "angle": 303.0,
          "diff": 0.0,
          "zero": 0
        },
        {
          "angle": 304.5,
          "diff": 0.0,
          "zero": 0
        },
        {
          "angle": 306.0,
          "diff": 0.0,
          "zero": 0
        },
        {
          "angle": 307.5,
          "diff": 0.0,
          "zero": 0
        },
        {
          "angle": 309.0,
          "diff": 0.0,
          "zero": 0
        },
        {
          "angle": 310.5,
          "diff": 0.0,
          "zero": 0
        },
        {
          "angle": 312.0,
          "diff": 0.007692,
          "zero": 0
        },
        {
          "angle": 313.5,
          "diff": 0.007692,
          "zero": 0
        },
        {
          "angle": 315.0,
          "diff": 0.007692,
          "zero": 0
        },
        {
          "angle": 316.5,
          "diff": 0.007692,
          "zero": 0
        },
        {
          "angle": 318.0,
          "diff": 0.007692,
          "zero": 0
        },
        {
          "angle": 319.5,
          "diff": 0.007692,
          "zero": 0
        },
        {
          "angle": 321.0,
          "diff": 0.007692,
          "zero": 0
        },
        {
          "angle": 322.5,
          "diff": 0.011538,
          "zero": 0
        },
        {
          "angle": 324.0,
          "diff": 0.011538,
          "zero": 0
        },
        {
          "angle": 325.5,
          "diff": 0.011538,
          "zero": 0
        },
        {
          "angle": 327.0,
          "diff": 0.011538,
          "zero": 0
        },
        {
          "angle": 328.5,
          "diff": 0.011538,
          "zero": 0
        },
        {
          "angle": 330.0,
          "diff": 0.011538,
          "zero": 0
        },
        {
          "angle": 331.5,
          "diff": 0.011538,
          "zero": 0
        },
        {
          "angle": 333.0,
          "diff": 0.011538,
          "zero": 0
        },
        {
          "angle": 334.5,
          "diff": 0.011538,
          "zero": 0
        },
        {
          "angle": 336.0,
          "diff": 0.011538,
          "zero": 0
        },
        {
          "angle": 337.5,
          "diff": 0.011538,
          "zero": 0
        },
        {
          "angle": 339.0,
          "diff": 0.011538,
          "zero": 0
        },
        {
          "angle": 340.5,
          "diff": 0.011538,
          "zero": 0
        },
        {
          "angle": 342.0,
          "diff": 0.011538,
          "zero": 0
        },
        {
          "angle": 343.5,
          "diff": 0.011538,
          "zero": 0
        },
        {
          "angle": 345.0,
          "diff": 0.011538,
          "zero": 0
        },
        {
          "angle": 346.5,
          "diff": 0.011538,
          "zero": 0
        },
        {
          "angle": 348.0,
          "diff": 0.011538,
          "zero": 0
        },
        {
          "angle": 349.5,
          "diff": 0.007692,
          "zero": 0
        },
        {
          "angle": 351.0,
          "diff": 0.007692,
          "zero": 0
        },
        {
          "angle": 352.5,
          "diff": 0.007692,
          "zero": 0
        },
        {
          "angle": 354.0,
          "diff": 0.007692,
          "zero": 0
        },
        {
          "angle": 355.5,
          "diff": 0.007692,
          "zero": 0
        },
        {
          "angle": 357.0,
          "diff": 0.003846,
          "zero": 0
        },
        {
          "angle": 358.5,
          "diff": 0.0,
          "zero": 0
        },
        {
          "angle": 360.0,
          "diff": 0.0,
          "zero": 0
        }
      ],
      "chart.CHART-EDF-004.circular": [
        {
          "start": 1.5,
          "end": 18.5,
          "mid": 10.0,
          "reference": 0.080769,
          "current": 0.011538,
          "label": "shift"
        },
        {
          "start": 21.5,
          "end": 38.5,
          "mid": 30.0,
          "reference": 0.288462,
          "current": 0.061538,
          "label": "shift"
        },
        {
          "start": 41.5,
          "end": 58.5,
          "mid": 50.0,
          "reference": 0.192308,
          "current": 0.188462,
          "label": ""
        },
        {
          "start": 61.5,
          "end": 78.5,
          "mid": 70.0,
          "reference": 0.065385,
          "current": 0.180769,
          "label": "shift"
        },
        {
          "start": 81.5,
          "end": 98.5,
          "mid": 90.0,
          "reference": 0.003846,
          "current": 0.065385,
          "label": "shift"
        },
        {
          "start": 101.5,
          "end": 118.5,
          "mid": 110.0,
          "reference": 0.0,
          "current": 0.026923,
          "label": ""
        },
        {
          "start": 121.5,
          "end": 138.5,
          "mid": 130.0,
          "reference": 0.0,
          "current": 0.0,
          "label": ""
        },
        {
          "start": 141.5,
          "end": 158.5,
          "mid": 150.0,
          "reference": 0.0,
          "current": 0.0,
          "label": ""
        },
        {
          "start": 161.5,
          "end": 178.5,
          "mid": 170.0,
          "reference": 0.026923,
          "current": 0.0,
          "label": ""
        },
        {
          "start": 181.5,
          "end": 198.5,
          "mid": 190.0,
          "reference": 0.061538,
          "current": 0.003846,
          "label": "shift"
        },
        {
          "start": 201.5,
          "end": 218.5,
          "mid": 210.0,
          "reference": 0.096154,
          "current": 0.019231,
          "label": "shift"
        },
        {
          "start": 221.5,
          "end": 238.5,
          "mid": 230.0,
          "reference": 0.084615,
          "current": 0.092308,
          "label": ""
        },
        {
          "start": 241.5,
          "end": 258.5,
          "mid": 250.0,
          "reference": 0.076923,
          "current": 0.188462,
          "label": "shift"
        },
        {
          "start": 261.5,
          "end": 278.5,
          "mid": 270.0,
          "reference": 0.007692,
          "current": 0.111538,
          "label": "shift"
        },
        {
          "start": 281.5,
          "end": 298.5,
          "mid": 290.0,
          "reference": 0.003846,
          "current": 0.030769,
          "label": ""
        },
        {
          "start": 301.5,
          "end": 318.5,
          "mid": 310.0,
          "reference": 0.0,
          "current": 0.015385,
          "label": ""
        },
        {
          "start": 321.5,
          "end": 338.5,
          "mid": 330.0,
          "reference": 0.0,
          "current": 0.003846,
          "label": ""
        },
        {
          "start": 341.5,
          "end": 358.5,
          "mid": 350.0,
          "reference": 0.011538,
          "current": 0.0,
          "label": ""
        }
      ],
      "chart.CHART-EDF-004.notes": [
        {
          "title": "해석",
          "text": "이 예시에서는 Kuiper V가 0.377, p-value가 0.009이고 D-=0.365가 49.5° 부근에서 지배적이다. 원형 히스토그램에서도 기준 peak가 20~40°에 많고 현재는 40~80° 및 240~260° 구간으로 이동한다. 시작점이 임의적인 circular data의 위치 이동 후보로 해석하되, wrap-around 처리와 시간대/계절성 원인은 별도 확인한다.",
          "legend": [
            {
              "label": "양의 편차 D+",
              "class": "swatch-positive"
            },
            {
              "label": "음의 편차 D-",
              "class": "swatch-negative"
            },
            {
              "label": "기준 구간",
              "class": "swatch-reference"
            },
            {
              "label": "현재 구간",
              "class": "swatch-current-prop"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-ERR-001",
    "title": "CHART-ERR-001 - 오류율 상승과 DDM 드리프트 경보",
    "originalPath": "./drift_report_charts/chart_err_001.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_err_001",
      "displayName": "CHART-ERR-001 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 146px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "오류율 추세",
          "description": "오류율이 0.27 warning 기준과 0.36 drift 기준을 차례로 넘는 흐름을 읽는다.",
          "headerHeight": 76,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 0,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "드리프트 기준 초과 여유",
          "description": "t=26부터 drift 기준 대비 여유가 0을 넘어서는지 본다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "경고 버퍼 타임라인",
          "description": "t=22 warning buffer가 t=26 drift 경보로 이어지는 순서",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "notes",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-ERR-001.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-001.summary"
        }
      },
      {
        "componentInstanceId": "CHART-ERR-001.error.0",
        "componentType": "trend_line",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "time",
          "y_field": "error",
          "x_min": 1,
          "x_max": 32,
          "y_min": 0,
          "y_max": 0.52,
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 28,
            "bottom": 62,
            "left": 58
          },
          "x_ticks": [
            1,
            8,
            16,
            24,
            32
          ],
          "y_ticks": [
            0,
            0.1,
            0.2,
            0.3,
            0.4,
            0.5
          ],
          "x_axis_label": "time index",
          "y_axis_label": "error rate",
          "line_class": "error-line",
          "primary_point_class": "error-point",
          "point_sample_every": 3,
          "point_radius": 3.6,
          "horizontal_markers": [
            {
              "y": 0.27,
              "class": "warning-line",
              "label": "warning threshold",
              "label_class": "warning-threshold-text",
              "label_x": 3,
              "label_dy": -8
            },
            {
              "y": 0.36,
              "class": "drift-line",
              "label": "drift threshold",
              "label_class": "drift-text",
              "label_x": 3,
              "label_dy": -8
            }
          ],
          "vertical_markers": [
            {
              "x": 22,
              "class": "state-line"
            },
            {
              "x": 26,
              "class": "state-line"
            }
          ],
          "point_highlights": [
            {
              "x": 22,
              "class": "error-point",
              "r": 3.6
            },
            {
              "x": 23,
              "class": "error-point",
              "r": 3.6
            },
            {
              "x": 24,
              "class": "error-point",
              "r": 3.6
            },
            {
              "x": 25,
              "class": "error-point",
              "r": 3.6
            },
            {
              "x": 26,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 27,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 28,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 29,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 30,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 31,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 32,
              "class": "drift-point",
              "r": 4.8
            }
          ],
          "annotations": [
            {
              "text": "drift alarm",
              "x": 26.7,
              "y": 0.47,
              "class": "drift-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-001.error"
        }
      },
      {
        "componentInstanceId": "CHART-ERR-001.margin.0",
        "componentType": "distance_metric_view",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "time",
          "y_field": "margin",
          "x_min": 1,
          "x_max": 32,
          "y_min": -0.12,
          "y_max": 0.28,
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 24,
            "bottom": 34,
            "left": 58
          },
          "x_ticks": [],
          "y_ticks": [
            -0.1,
            0,
            0.1,
            0.2
          ],
          "x_axis_label": "p+s minus drift threshold",
          "axis_label_x": 216,
          "axis_label_y": 177,
          "y_axis_label": false,
          "line_class": "error-line",
          "show_points": false,
          "horizontal_markers": [
            {
              "y": 0,
              "class": "drift-line"
            }
          ],
          "vertical_markers": [
            {
              "x": 26,
              "class": "state-line"
            }
          ],
          "annotations": [
            {
              "text": "0 초과: drift",
              "x": 19,
              "y": 0.18,
              "class": "drift-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-001.error"
        }
      },
      {
        "componentInstanceId": "CHART-ERR-001.timeline.0",
        "componentType": "state_timeline",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "start_field": "start",
          "end_field": "end",
          "window_role_field": "role",
          "window_id_field": "label",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 32,
            "right": 24,
            "bottom": 38,
            "left": 48
          },
          "track_y": 74,
          "track_height": 30,
          "x_ticks": [
            1,
            8,
            16,
            24,
            32
          ],
          "axis_label": "DDM state timeline",
          "axis_label_x": 228,
          "axis_label_y": 179,
          "role_class_map": {
            "normal": "normal-fill",
            "warning": "warning-fill",
            "drift": "drift-fill"
          },
          "track_overlays": [
            {
              "x0": 22,
              "x1": 26,
              "y": 52,
              "height": 12,
              "class": "buffer-fill",
              "label": "buffer",
              "label_class": "bar-label",
              "label_dy": 10
            }
          ],
          "markers": [
            {
              "x": 26,
              "class": "state-line",
              "circle": true,
              "circle_class": "drift-point",
              "radius": 7
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-001.timeline"
        }
      },
      {
        "componentInstanceId": "CHART-ERR-001.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-001.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-ERR-001.summary": [
        {
          "label": "final error",
          "value": 0.46,
          "displayValue": "0.46"
        },
        {
          "label": "warning start",
          "value": 22,
          "displayValue": "t=22"
        },
        {
          "label": "drift alarm",
          "value": 26,
          "displayValue": "t=26"
        }
      ],
      "chart.CHART-ERR-001.error": [
        {
          "time": 1,
          "error": 0.08,
          "margin": -0.28
        },
        {
          "time": 2,
          "error": 0.09,
          "margin": -0.27
        },
        {
          "time": 3,
          "error": 0.08,
          "margin": -0.28
        },
        {
          "time": 4,
          "error": 0.1,
          "margin": -0.26
        },
        {
          "time": 5,
          "error": 0.09,
          "margin": -0.27
        },
        {
          "time": 6,
          "error": 0.1,
          "margin": -0.26
        },
        {
          "time": 7,
          "error": 0.11,
          "margin": -0.25
        },
        {
          "time": 8,
          "error": 0.1,
          "margin": -0.26
        },
        {
          "time": 9,
          "error": 0.12,
          "margin": -0.24
        },
        {
          "time": 10,
          "error": 0.13,
          "margin": -0.23
        },
        {
          "time": 11,
          "error": 0.12,
          "margin": -0.24
        },
        {
          "time": 12,
          "error": 0.14,
          "margin": -0.22
        },
        {
          "time": 13,
          "error": 0.15,
          "margin": -0.21
        },
        {
          "time": 14,
          "error": 0.16,
          "margin": -0.2
        },
        {
          "time": 15,
          "error": 0.17,
          "margin": -0.19
        },
        {
          "time": 16,
          "error": 0.18,
          "margin": -0.18
        },
        {
          "time": 17,
          "error": 0.19,
          "margin": -0.17
        },
        {
          "time": 18,
          "error": 0.21,
          "margin": -0.15
        },
        {
          "time": 19,
          "error": 0.22,
          "margin": -0.14
        },
        {
          "time": 20,
          "error": 0.24,
          "margin": -0.12
        },
        {
          "time": 21,
          "error": 0.26,
          "margin": -0.1
        },
        {
          "time": 22,
          "error": 0.28,
          "margin": -0.08
        },
        {
          "time": 23,
          "error": 0.3,
          "margin": -0.06
        },
        {
          "time": 24,
          "error": 0.33,
          "margin": -0.03
        },
        {
          "time": 25,
          "error": 0.35,
          "margin": -0.01
        },
        {
          "time": 26,
          "error": 0.37,
          "margin": 0.01
        },
        {
          "time": 27,
          "error": 0.39,
          "margin": 0.03
        },
        {
          "time": 28,
          "error": 0.41,
          "margin": 0.05
        },
        {
          "time": 29,
          "error": 0.42,
          "margin": 0.06
        },
        {
          "time": 30,
          "error": 0.44,
          "margin": 0.08
        },
        {
          "time": 31,
          "error": 0.45,
          "margin": 0.09
        },
        {
          "time": 32,
          "error": 0.46,
          "margin": 0.1
        }
      ],
      "chart.CHART-ERR-001.timeline": [
        {
          "label": "normal",
          "role": "normal",
          "start": 1,
          "end": 22
        },
        {
          "label": "warning",
          "role": "warning",
          "start": 22,
          "end": 26
        },
        {
          "label": "drift",
          "role": "drift",
          "start": 26,
          "end": 32
        }
      ],
      "chart.CHART-ERR-001.notes": [
        {
          "title": "해석",
          "text": "DDM은 error rate의 p + s가 최소 error 상태의 p_min + 2s_min을 넘으면 warning, p_min + 3s_min을 넘으면 drift로 표시한다. 이 예시에서는 오류율이 0.46까지 상승하고 t=22 warning buffer가 t=26 drift 경보로 이어져 DDM 기준 drift 후보로 해석한다.",
          "legend": [
            {
              "label": "error rate",
              "class": "swatch-error-rate"
            },
            {
              "label": "warning threshold",
              "class": "swatch-warning-threshold"
            },
            {
              "label": "drift threshold",
              "class": "swatch-drift-threshold"
            },
            {
              "label": "warning buffer",
              "class": "swatch-warning-buffer"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-ERR-002",
    "title": "CHART-ERR-002 - RDDM의 경보 구간 보존과 재설정 과정",
    "originalPath": "./drift_report_charts/chart_err_002.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_err_002",
      "displayName": "CHART-ERR-002 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 146px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "RDDM 오류율과 재설정",
          "description": "오류율이 0.28 경보 기준을 지나 0.38 드리프트 기준에 닿은 뒤 reset 이후 낮아지는 흐름을 읽는다.",
          "headerHeight": 76,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 0,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "보존 윈도 크기",
          "description": "t=25의 156개 보존 window가 t=26 reset 직후 44개로 줄어드는지 본다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "DDM과 RDDM 비교",
          "description": "DDM은 drift 후 reset으로, RDDM은 warning 데이터를 retain한 뒤 reactive reset으로 이어진다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "notes",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-ERR-002.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-002.summary"
        }
      },
      {
        "componentInstanceId": "CHART-ERR-002.error.0",
        "componentType": "trend_line",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "time",
          "y_field": "error",
          "x_min": 1,
          "x_max": 32,
          "y_min": 0,
          "y_max": 0.5,
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 28,
            "bottom": 62,
            "left": 58
          },
          "x_ticks": [
            1,
            8,
            16,
            24,
            32
          ],
          "y_ticks": [
            0,
            0.1,
            0.2,
            0.3,
            0.4,
            0.5
          ],
          "x_axis_label": "time index",
          "y_axis_label": "error rate",
          "line_class": "error-line",
          "show_points": false,
          "horizontal_markers": [
            {
              "y": 0.28,
              "class": "warning-line",
              "label": "warning",
              "label_class": "warning-threshold-text",
              "label_x": 4,
              "label_dy": -8
            },
            {
              "y": 0.38,
              "class": "drift-line",
              "label": "drift",
              "label_class": "drift-text",
              "label_x": 4,
              "label_dy": -8
            }
          ],
          "vertical_markers": [
            {
              "x": 20,
              "class": "reset-line"
            },
            {
              "x": 25,
              "class": "reset-line"
            },
            {
              "x": 26,
              "class": "reset-line"
            }
          ],
          "point_highlights": [
            {
              "x": 1,
              "class": "error-point",
              "r": 3.5
            },
            {
              "x": 4,
              "class": "error-point",
              "r": 3.5
            },
            {
              "x": 7,
              "class": "error-point",
              "r": 3.5
            },
            {
              "x": 10,
              "class": "error-point",
              "r": 3.5
            },
            {
              "x": 13,
              "class": "error-point",
              "r": 3.5
            },
            {
              "x": 16,
              "class": "error-point",
              "r": 3.5
            },
            {
              "x": 19,
              "class": "error-point",
              "r": 3.5
            },
            {
              "x": 20,
              "class": "error-point",
              "r": 3.5
            },
            {
              "x": 21,
              "class": "error-point",
              "r": 3.5
            },
            {
              "x": 22,
              "class": "error-point",
              "r": 3.5
            },
            {
              "x": 23,
              "class": "error-point",
              "r": 3.5
            },
            {
              "x": 24,
              "class": "error-point",
              "r": 3.5
            },
            {
              "x": 25,
              "class": "drift-point",
              "r": 5
            },
            {
              "x": 26,
              "class": "drift-point",
              "r": 5
            },
            {
              "x": 27,
              "class": "error-point",
              "r": 3.5
            },
            {
              "x": 28,
              "class": "error-point",
              "r": 3.5
            },
            {
              "x": 29,
              "class": "error-point",
              "r": 3.5
            },
            {
              "x": 30,
              "class": "error-point",
              "r": 3.5
            },
            {
              "x": 31,
              "class": "error-point",
              "r": 3.5
            },
            {
              "x": 32,
              "class": "error-point",
              "r": 3.5
            }
          ],
          "annotations": [
            {
              "text": "reactive reset",
              "x": 26.45,
              "y": 0.47,
              "class": "drift-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-002.series"
        }
      },
      {
        "componentInstanceId": "CHART-ERR-002.window.0",
        "componentType": "trend_line",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "time",
          "y_field": "retained",
          "x_min": 1,
          "x_max": 32,
          "y_min": 30,
          "y_max": 170,
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 22,
            "bottom": 34,
            "left": 48
          },
          "x_ticks": [],
          "y_ticks": [
            40,
            80,
            120,
            160
          ],
          "x_axis_label": "retained window size",
          "axis_label_x": 208,
          "axis_label_y": 177,
          "y_axis_label": false,
          "line_class": "window-line",
          "show_points": false,
          "vertical_markers": [
            {
              "x": 26,
              "class": "reset-line"
            }
          ],
          "point_highlights": [
            {
              "x": 1,
              "class": "window-point",
              "r": 3.5
            },
            {
              "x": 5,
              "class": "window-point",
              "r": 3.5
            },
            {
              "x": 9,
              "class": "window-point",
              "r": 3.5
            },
            {
              "x": 13,
              "class": "window-point",
              "r": 3.5
            },
            {
              "x": 17,
              "class": "window-point",
              "r": 3.5
            },
            {
              "x": 21,
              "class": "window-point",
              "r": 3.5
            },
            {
              "x": 25,
              "class": "window-point",
              "r": 3.5
            },
            {
              "x": 26,
              "class": "window-point",
              "r": 5
            },
            {
              "x": 29,
              "class": "window-point",
              "r": 3.5
            }
          ],
          "annotations": [
            {
              "text": "reset 후 축소",
              "x": 26.7,
              "y": 58,
              "class": "retained-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-002.series"
        }
      },
      {
        "componentInstanceId": "CHART-ERR-002.comparison.0",
        "componentType": "state_timeline",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "start_field": "start",
          "end_field": "end",
          "window_role_field": "role",
          "window_id_field": "label",
          "track_field": "track",
          "track_order": [
            "DDM",
            "RDDM"
          ],
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 24,
            "right": 24,
            "bottom": 34,
            "left": 82
          },
          "first_track_y": 48,
          "track_gap": 56,
          "track_height": 30,
          "x_ticks": [
            1,
            8,
            16,
            24,
            32
          ],
          "axis_label": "RDDM keeps warning data before reactive reset",
          "axis_label_x": 252,
          "axis_label_y": 179,
          "role_class_map": {
            "normal": "normal-fill",
            "warning": "warning-fill",
            "reset": "ddm-fill",
            "retain": "retained-fill",
            "reactive": "drift-fill"
          },
          "markers": [
            {
              "x": 26,
              "class": "reset-line",
              "y1": 24,
              "y2": 148
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-002.comparison"
        }
      },
      {
        "componentInstanceId": "CHART-ERR-002.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-002.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-ERR-002.summary": [
        {
          "label": "warning start",
          "value": 20,
          "displayValue": "t=20"
        },
        {
          "label": "reactive reset",
          "value": 26,
          "displayValue": "t=26"
        },
        {
          "label": "retained window",
          "value": 44,
          "displayValue": "44"
        }
      ],
      "chart.CHART-ERR-002.series": [
        {
          "time": 1,
          "error": 0.07,
          "retained": 60
        },
        {
          "time": 2,
          "error": 0.08,
          "retained": 64
        },
        {
          "time": 3,
          "error": 0.09,
          "retained": 68
        },
        {
          "time": 4,
          "error": 0.08,
          "retained": 72
        },
        {
          "time": 5,
          "error": 0.1,
          "retained": 76
        },
        {
          "time": 6,
          "error": 0.09,
          "retained": 80
        },
        {
          "time": 7,
          "error": 0.11,
          "retained": 84
        },
        {
          "time": 8,
          "error": 0.1,
          "retained": 88
        },
        {
          "time": 9,
          "error": 0.12,
          "retained": 92
        },
        {
          "time": 10,
          "error": 0.13,
          "retained": 96
        },
        {
          "time": 11,
          "error": 0.12,
          "retained": 100
        },
        {
          "time": 12,
          "error": 0.14,
          "retained": 104
        },
        {
          "time": 13,
          "error": 0.15,
          "retained": 108
        },
        {
          "time": 14,
          "error": 0.16,
          "retained": 112
        },
        {
          "time": 15,
          "error": 0.18,
          "retained": 116
        },
        {
          "time": 16,
          "error": 0.19,
          "retained": 120
        },
        {
          "time": 17,
          "error": 0.21,
          "retained": 124
        },
        {
          "time": 18,
          "error": 0.24,
          "retained": 128
        },
        {
          "time": 19,
          "error": 0.26,
          "retained": 132
        },
        {
          "time": 20,
          "error": 0.28,
          "retained": 136
        },
        {
          "time": 21,
          "error": 0.3,
          "retained": 140
        },
        {
          "time": 22,
          "error": 0.32,
          "retained": 144
        },
        {
          "time": 23,
          "error": 0.34,
          "retained": 148
        },
        {
          "time": 24,
          "error": 0.37,
          "retained": 152
        },
        {
          "time": 25,
          "error": 0.4,
          "retained": 156
        },
        {
          "time": 26,
          "error": 0.42,
          "retained": 44
        },
        {
          "time": 27,
          "error": 0.43,
          "retained": 48
        },
        {
          "time": 28,
          "error": 0.36,
          "retained": 52
        },
        {
          "time": 29,
          "error": 0.33,
          "retained": 58
        },
        {
          "time": 30,
          "error": 0.31,
          "retained": 64
        },
        {
          "time": 31,
          "error": 0.3,
          "retained": 70
        },
        {
          "time": 32,
          "error": 0.29,
          "retained": 76
        }
      ],
      "chart.CHART-ERR-002.comparison": [
        {
          "track": "DDM",
          "label": "normal",
          "role": "normal",
          "start": 1,
          "end": 20
        },
        {
          "track": "DDM",
          "label": "warning",
          "role": "warning",
          "start": 20,
          "end": 25
        },
        {
          "track": "DDM",
          "label": "reset",
          "role": "reset",
          "start": 25,
          "end": 32
        },
        {
          "track": "RDDM",
          "label": "normal",
          "role": "normal",
          "start": 1,
          "end": 20
        },
        {
          "track": "RDDM",
          "label": "retain",
          "role": "retain",
          "start": 20,
          "end": 26
        },
        {
          "track": "RDDM",
          "label": "reactive",
          "role": "reactive",
          "start": 26,
          "end": 32
        }
      ],
      "chart.CHART-ERR-002.notes": [
        {
          "title": "해석",
          "text": "이 예시에서는 error rate가 t=20에 warning 기준 0.28에 도달하고 t=25에 drift 기준 0.38을 넘은 뒤 t=26 reactive reset 이후 0.42에서 0.36으로 낮아진다. Retained window는 reset 직전 156개에서 reset 직후 44개로 축소되어, RDDM이 warning 구간을 보존한 뒤 새 window로 전환한 상황으로 읽는다.",
          "legend": [
            {
              "label": "error rate",
              "class": "swatch-error-rate"
            },
            {
              "label": "warning",
              "class": "swatch-warning-threshold"
            },
            {
              "label": "drift/reset",
              "class": "swatch-drift-threshold"
            },
            {
              "label": "retained window",
              "class": "swatch-retained-window"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-ERR-003",
    "title": "CHART-ERR-003 - 오류 간격 축소로 나타난 점진적 성능 저하",
    "originalPath": "./drift_report_charts/chart_err_003.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_err_003",
      "displayName": "CHART-ERR-003 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 146px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "오류 간격 점수 하락",
          "description": "score가 1.00에서 0.44까지 내려가며 t=11 warning, t=19 drift 기준을 지난다.",
          "headerHeight": 76,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 0,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "상태 전환 구간",
          "description": "t=1~10 normal 이후 t=11 warning, t=19부터 drift로 읽는다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "오류 이벤트 밀집",
          "description": "t=20 이후 오류가 이어지고 t=27~32에서는 매 시점 발생한다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "notes",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-ERR-003.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-003.summary"
        }
      },
      {
        "componentInstanceId": "CHART-ERR-003.distance.0",
        "componentType": "trend_line",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "time",
          "y_field": "score",
          "x_min": 1,
          "x_max": 32,
          "y_min": 0.35,
          "y_max": 1.05,
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 28,
            "bottom": 62,
            "left": 58
          },
          "x_ticks": [
            1,
            8,
            16,
            24,
            32
          ],
          "y_ticks": [
            0.4,
            0.6,
            0.8,
            1.0
          ],
          "x_axis_label": "time index",
          "y_axis_label": "distance score ratio",
          "line_class": "distance-line",
          "show_points": false,
          "horizontal_markers": [
            {
              "y": 0.9,
              "class": "warning-line",
              "label": "warning 0.90",
              "label_class": "warning-threshold-text",
              "label_x": 3,
              "label_dy": -8
            },
            {
              "y": 0.75,
              "class": "drift-line",
              "label": "drift 0.75",
              "label_class": "drift-text",
              "label_x": 3,
              "label_dy": -8
            }
          ],
          "vertical_markers": [
            {
              "x": 11,
              "class": "state-line"
            },
            {
              "x": 19,
              "class": "state-line"
            }
          ],
          "point_highlights": [
            {
              "x": 1,
              "class": "distance-point",
              "r": 3.5
            },
            {
              "x": 4,
              "class": "distance-point",
              "r": 3.5
            },
            {
              "x": 7,
              "class": "distance-point",
              "r": 3.5
            },
            {
              "x": 10,
              "class": "distance-point",
              "r": 3.5
            },
            {
              "x": 11,
              "class": "distance-point",
              "r": 3.5
            },
            {
              "x": 12,
              "class": "distance-point",
              "r": 3.5
            },
            {
              "x": 13,
              "class": "distance-point",
              "r": 3.5
            },
            {
              "x": 14,
              "class": "distance-point",
              "r": 3.5
            },
            {
              "x": 15,
              "class": "distance-point",
              "r": 3.5
            },
            {
              "x": 16,
              "class": "distance-point",
              "r": 3.5
            },
            {
              "x": 17,
              "class": "distance-point",
              "r": 3.5
            },
            {
              "x": 18,
              "class": "distance-point",
              "r": 3.5
            },
            {
              "x": 19,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 20,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 21,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 22,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 23,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 24,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 25,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 26,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 27,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 28,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 29,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 30,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 31,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 32,
              "class": "drift-point",
              "r": 4.8
            }
          ],
          "annotations": [
            {
              "text": "오류 간격 감소",
              "x": 20,
              "y": 0.48,
              "class": "drift-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-003.score"
        }
      },
      {
        "componentInstanceId": "CHART-ERR-003.timeline.0",
        "componentType": "state_timeline",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "start_field": "start",
          "end_field": "end",
          "window_role_field": "role",
          "window_id_field": "label",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 32,
            "right": 24,
            "bottom": 38,
            "left": 48
          },
          "track_y": 74,
          "track_height": 30,
          "x_ticks": [
            1,
            8,
            16,
            24,
            32
          ],
          "axis_label": "EDDM state timeline",
          "axis_label_x": 228,
          "axis_label_y": 179,
          "role_class_map": {
            "normal": "normal-fill",
            "warning": "warning-fill",
            "drift": "drift-fill"
          },
          "markers": [
            {
              "x": 19,
              "class": "state-line",
              "circle": true,
              "circle_class": "drift-point",
              "radius": 7
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-003.timeline"
        }
      },
      {
        "componentInstanceId": "CHART-ERR-003.events.0",
        "componentType": "event_raster",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "time",
          "x_min": 1,
          "x_max": 32,
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 22,
            "right": 24,
            "bottom": 38,
            "left": 48
          },
          "row_count": 4,
          "row_gap": 27,
          "jitter_mod": 4,
          "jitter_step": 2,
          "event_class": "event-mark",
          "hot_event_class": "event-mark hot",
          "hot_gte": 19,
          "vertical_markers": [
            {
              "x": 19,
              "class": "state-line",
              "y1": 22,
              "y2": 138
            }
          ],
          "x_ticks": [
            1,
            8,
            16,
            24,
            32
          ],
          "x_axis_label": "error events become denser",
          "axis_label_x": 213,
          "axis_label_y": 179,
          "annotations": [
            {
              "text": "밀집",
              "x": 26,
              "y": 38,
              "class": "drift-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-003.events"
        }
      },
      {
        "componentInstanceId": "CHART-ERR-003.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-003.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-ERR-003.summary": [
        {
          "label": "final score",
          "value": 0.44,
          "displayValue": "0.44"
        },
        {
          "label": "warning",
          "value": 11,
          "displayValue": "t=11"
        },
        {
          "label": "drift",
          "value": 19,
          "displayValue": "t=19"
        }
      ],
      "chart.CHART-ERR-003.score": [
        {
          "time": 1,
          "score": 1.0
        },
        {
          "time": 2,
          "score": 0.99
        },
        {
          "time": 3,
          "score": 0.98
        },
        {
          "time": 4,
          "score": 0.97
        },
        {
          "time": 5,
          "score": 0.98
        },
        {
          "time": 6,
          "score": 0.96
        },
        {
          "time": 7,
          "score": 0.95
        },
        {
          "time": 8,
          "score": 0.94
        },
        {
          "time": 9,
          "score": 0.92
        },
        {
          "time": 10,
          "score": 0.91
        },
        {
          "time": 11,
          "score": 0.89
        },
        {
          "time": 12,
          "score": 0.88
        },
        {
          "time": 13,
          "score": 0.86
        },
        {
          "time": 14,
          "score": 0.84
        },
        {
          "time": 15,
          "score": 0.82
        },
        {
          "time": 16,
          "score": 0.8
        },
        {
          "time": 17,
          "score": 0.78
        },
        {
          "time": 18,
          "score": 0.76
        },
        {
          "time": 19,
          "score": 0.74
        },
        {
          "time": 20,
          "score": 0.72
        },
        {
          "time": 21,
          "score": 0.7
        },
        {
          "time": 22,
          "score": 0.68
        },
        {
          "time": 23,
          "score": 0.66
        },
        {
          "time": 24,
          "score": 0.63
        },
        {
          "time": 25,
          "score": 0.6
        },
        {
          "time": 26,
          "score": 0.57
        },
        {
          "time": 27,
          "score": 0.54
        },
        {
          "time": 28,
          "score": 0.51
        },
        {
          "time": 29,
          "score": 0.49
        },
        {
          "time": 30,
          "score": 0.47
        },
        {
          "time": 31,
          "score": 0.45
        },
        {
          "time": 32,
          "score": 0.44
        }
      ],
      "chart.CHART-ERR-003.timeline": [
        {
          "label": "normal",
          "role": "normal",
          "start": 1,
          "end": 11
        },
        {
          "label": "warning",
          "role": "warning",
          "start": 11,
          "end": 19
        },
        {
          "label": "drift",
          "role": "drift",
          "start": 19,
          "end": 32
        }
      ],
      "chart.CHART-ERR-003.events": [
        {
          "time": 3
        },
        {
          "time": 8
        },
        {
          "time": 13
        },
        {
          "time": 17
        },
        {
          "time": 20
        },
        {
          "time": 22
        },
        {
          "time": 24
        },
        {
          "time": 25
        },
        {
          "time": 27
        },
        {
          "time": 28
        },
        {
          "time": 29
        },
        {
          "time": 30
        },
        {
          "time": 31
        },
        {
          "time": 32
        }
      ],
      "chart.CHART-ERR-003.notes": [
        {
          "title": "해석",
          "text": "이 예시에서는 오류 간격 score가 1.00에서 0.44까지 계속 낮아진다. t=11에 warning 기준 0.90 아래로 내려가고 t=19에 drift 기준 0.75를 통과하며, t=27~32 구간의 오류 이벤트가 연속되어 점진적 error-rate drift 후보로 해석한다.",
          "legend": [
            {
              "label": "distance score",
              "class": "swatch-distance-score"
            },
            {
              "label": "warning",
              "class": "swatch-warning-threshold"
            },
            {
              "label": "drift",
              "class": "swatch-drift-threshold"
            },
            {
              "label": "error event",
              "class": "swatch-error-event"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-ERR-004",
    "title": "CHART-ERR-004 - ECDD 통계량 상승과 오류율 드리프트 감지",
    "originalPath": "./drift_report_charts/chart_err_004.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_err_004",
      "displayName": "CHART-ERR-004 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 146px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "ECDD 통계량 관리도",
          "description": "통계량이 t=22에서 0.72 warning limit, t=26에서 0.95 drift limit을 넘는다.",
          "headerHeight": 76,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 0,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "오류율 추세",
          "description": "weighted error rate가 0.07에서 0.45까지 상승한다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "주의/드리프트 상태",
          "description": "t=1~21 normal, t=22~25 warning, t=26 이후 drift로 읽는다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "notes",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-ERR-004.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-004.summary"
        }
      },
      {
        "componentInstanceId": "CHART-ERR-004.stat.0",
        "componentType": "control_chart",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "time",
          "y_field": "stat",
          "x_min": 1,
          "x_max": 32,
          "y_min": 0,
          "y_max": 1.4,
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 28,
            "bottom": 62,
            "left": 58
          },
          "x_ticks": [
            1,
            8,
            16,
            24,
            32
          ],
          "y_ticks": [
            0,
            0.3,
            0.6,
            0.9,
            1.2
          ],
          "x_axis_label": "time index",
          "y_axis_label": "ECDD statistic",
          "line_class": "stat-line",
          "show_points": false,
          "horizontal_markers": [
            {
              "y": 0.72,
              "class": "warning-line",
              "label": "warning limit",
              "label_class": "warning-text",
              "label_x": 3,
              "label_dy": -8
            },
            {
              "y": 0.95,
              "class": "drift-line",
              "label": "drift limit",
              "label_class": "drift-text",
              "label_x": 3,
              "label_dy": -8
            }
          ],
          "vertical_markers": [
            {
              "x": 22,
              "class": "state-line",
              "opacity": 0.7
            },
            {
              "x": 26,
              "class": "state-line"
            }
          ],
          "point_highlights": [
            {
              "x": 1,
              "class": "stat-point",
              "r": 3.5
            },
            {
              "x": 4,
              "class": "stat-point",
              "r": 3.5
            },
            {
              "x": 7,
              "class": "stat-point",
              "r": 3.5
            },
            {
              "x": 10,
              "class": "stat-point",
              "r": 3.5
            },
            {
              "x": 13,
              "class": "stat-point",
              "r": 3.5
            },
            {
              "x": 16,
              "class": "stat-point",
              "r": 3.5
            },
            {
              "x": 19,
              "class": "stat-point",
              "r": 3.5
            },
            {
              "x": 22,
              "class": "stat-point",
              "r": 3.5
            },
            {
              "x": 23,
              "class": "stat-point",
              "r": 3.5
            },
            {
              "x": 24,
              "class": "stat-point",
              "r": 3.5
            },
            {
              "x": 25,
              "class": "stat-point",
              "r": 3.5
            },
            {
              "x": 26,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 27,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 28,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 29,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 30,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 31,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 32,
              "class": "drift-point",
              "r": 4.8
            }
          ],
          "annotations": [
            {
              "text": "weighted statistic crosses limit",
              "x": 17,
              "y": 1.28,
              "class": "callout"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-004.series"
        }
      },
      {
        "componentInstanceId": "CHART-ERR-004.error.0",
        "componentType": "performance_metric_view",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "time",
          "y_field": "error",
          "x_min": 1,
          "x_max": 32,
          "y_min": 0,
          "y_max": 0.5,
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 22,
            "bottom": 34,
            "left": 48
          },
          "x_ticks": [],
          "y_ticks": [
            0,
            0.15,
            0.3,
            0.45
          ],
          "x_axis_label": "weighted error rate",
          "axis_label_x": 208,
          "axis_label_y": 177,
          "y_axis_label": false,
          "line_class": "weighted-error-line",
          "show_points": false,
          "vertical_markers": [
            {
              "x": 26,
              "class": "state-line"
            }
          ],
          "point_highlights": [
            {
              "x": 1,
              "class": "weighted-error-point",
              "r": 3.5
            },
            {
              "x": 8,
              "class": "weighted-error-point",
              "r": 3.5
            },
            {
              "x": 16,
              "class": "weighted-error-point",
              "r": 3.5
            },
            {
              "x": 24,
              "class": "weighted-error-point",
              "r": 3.5
            },
            {
              "x": 32,
              "class": "weighted-error-point",
              "r": 3.5
            }
          ],
          "annotations": [
            {
              "text": "error stream 상승",
              "x": 20,
              "y": 0.42,
              "class": "drift-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-004.series"
        }
      },
      {
        "componentInstanceId": "CHART-ERR-004.timeline.0",
        "componentType": "state_timeline",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "start_field": "start",
          "end_field": "end",
          "window_role_field": "role",
          "window_id_field": "label",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 32,
            "right": 24,
            "bottom": 38,
            "left": 48
          },
          "track_y": 74,
          "track_height": 30,
          "x_ticks": [
            1,
            8,
            16,
            24,
            32
          ],
          "axis_label": "ECDD-WT state timeline",
          "axis_label_x": 228,
          "axis_label_y": 179,
          "role_class_map": {
            "normal": "normal-fill",
            "warning": "warning-fill",
            "drift": "drift-fill"
          },
          "markers": [
            {
              "x": 26,
              "class": "state-line",
              "circle": true,
              "circle_class": "drift-point",
              "radius": 7
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-004.timeline"
        }
      },
      {
        "componentInstanceId": "CHART-ERR-004.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-004.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-ERR-004.summary": [
        {
          "label": "final statistic",
          "value": 1.28,
          "displayValue": "1.28"
        },
        {
          "label": "warning",
          "value": 22,
          "displayValue": "t=22"
        },
        {
          "label": "drift",
          "value": 26,
          "displayValue": "t=26"
        }
      ],
      "chart.CHART-ERR-004.series": [
        {
          "time": 1,
          "stat": 0.18,
          "error": 0.07
        },
        {
          "time": 2,
          "stat": 0.2,
          "error": 0.08
        },
        {
          "time": 3,
          "stat": 0.19,
          "error": 0.08
        },
        {
          "time": 4,
          "stat": 0.22,
          "error": 0.09
        },
        {
          "time": 5,
          "stat": 0.21,
          "error": 0.08
        },
        {
          "time": 6,
          "stat": 0.23,
          "error": 0.1
        },
        {
          "time": 7,
          "stat": 0.25,
          "error": 0.1
        },
        {
          "time": 8,
          "stat": 0.24,
          "error": 0.11
        },
        {
          "time": 9,
          "stat": 0.27,
          "error": 0.12
        },
        {
          "time": 10,
          "stat": 0.29,
          "error": 0.12
        },
        {
          "time": 11,
          "stat": 0.31,
          "error": 0.13
        },
        {
          "time": 12,
          "stat": 0.34,
          "error": 0.15
        },
        {
          "time": 13,
          "stat": 0.36,
          "error": 0.16
        },
        {
          "time": 14,
          "stat": 0.39,
          "error": 0.17
        },
        {
          "time": 15,
          "stat": 0.43,
          "error": 0.18
        },
        {
          "time": 16,
          "stat": 0.46,
          "error": 0.2
        },
        {
          "time": 17,
          "stat": 0.5,
          "error": 0.22
        },
        {
          "time": 18,
          "stat": 0.54,
          "error": 0.23
        },
        {
          "time": 19,
          "stat": 0.59,
          "error": 0.25
        },
        {
          "time": 20,
          "stat": 0.63,
          "error": 0.27
        },
        {
          "time": 21,
          "stat": 0.68,
          "error": 0.29
        },
        {
          "time": 22,
          "stat": 0.73,
          "error": 0.31
        },
        {
          "time": 23,
          "stat": 0.79,
          "error": 0.33
        },
        {
          "time": 24,
          "stat": 0.85,
          "error": 0.35
        },
        {
          "time": 25,
          "stat": 0.92,
          "error": 0.37
        },
        {
          "time": 26,
          "stat": 0.98,
          "error": 0.38
        },
        {
          "time": 27,
          "stat": 1.04,
          "error": 0.4
        },
        {
          "time": 28,
          "stat": 1.1,
          "error": 0.41
        },
        {
          "time": 29,
          "stat": 1.15,
          "error": 0.42
        },
        {
          "time": 30,
          "stat": 1.2,
          "error": 0.43
        },
        {
          "time": 31,
          "stat": 1.24,
          "error": 0.44
        },
        {
          "time": 32,
          "stat": 1.28,
          "error": 0.45
        }
      ],
      "chart.CHART-ERR-004.timeline": [
        {
          "label": "normal",
          "role": "normal",
          "start": 1,
          "end": 22
        },
        {
          "label": "warning",
          "role": "warning",
          "start": 22,
          "end": 26
        },
        {
          "label": "drift",
          "role": "drift",
          "start": 26,
          "end": 32
        }
      ],
      "chart.CHART-ERR-004.notes": [
        {
          "title": "해석",
          "text": "ECDD-WT는 error stream을 가중 평균 형태로 누적해 statistic control chart로 감시한다. 이 예시에서는 statistic이 1.28까지 오르고 weighted error rate도 0.45까지 상승해, t=26 이후를 weighted error-rate detector 기반 drift 후보로 해석한다.",
          "legend": [
            {
              "label": "ECDD statistic",
              "class": "swatch-stat"
            },
            {
              "label": "error rate",
              "class": "swatch-weighted-error"
            },
            {
              "label": "warning limit",
              "class": "swatch-warning-threshold"
            },
            {
              "label": "drift limit",
              "class": "swatch-drift-threshold"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-ERR-005",
    "title": "CHART-ERR-005 - 평균 오류 차이 확대로 보는 HDDM 드리프트 경보",
    "originalPath": "./drift_report_charts/chart_err_005.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_err_005",
      "displayName": "CHART-ERR-005 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 146px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "회프딩 경계 차트",
          "description": "mean difference가 t=22에서 0.26 warning, t=26에서 0.36 drift bound를 넘는다.",
          "headerHeight": 76,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 0,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "오류율/가중 오류율 추세",
          "description": "error trend가 0.08에서 0.47까지 상승한다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "주의/드리프트 표시",
          "description": "t=1~21 normal, t=22~25 warning, t=26 이후 drift로 읽는다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "notes",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-ERR-005.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-005.summary"
        }
      },
      {
        "componentInstanceId": "CHART-ERR-005.bound.0",
        "componentType": "control_chart",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "time",
          "y_field": "diff",
          "x_min": 1,
          "x_max": 32,
          "y_min": -0.1,
          "y_max": 0.56,
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 28,
            "bottom": 62,
            "left": 58
          },
          "x_ticks": [
            1,
            8,
            16,
            24,
            32
          ],
          "y_ticks": [
            -0.1,
            0,
            0.2,
            0.4
          ],
          "x_axis_y": 0,
          "x_axis_label": "time index",
          "y_axis_label": "mean difference",
          "line_class": "diff-line",
          "show_points": false,
          "horizontal_markers": [
            {
              "y": 0.26,
              "class": "warning-line",
              "label": "warning bound",
              "label_class": "warning-text",
              "label_x": 3,
              "label_dy": -8
            },
            {
              "y": 0.36,
              "class": "drift-line",
              "label": "drift bound",
              "label_class": "drift-text",
              "label_x": 3,
              "label_dy": -8
            },
            {
              "y": -0.26,
              "class": "warning-line",
              "opacity": 0.55
            }
          ],
          "vertical_markers": [
            {
              "x": 22,
              "class": "state-line",
              "opacity": 0.7
            },
            {
              "x": 26,
              "class": "state-line"
            }
          ],
          "point_highlights": [
            {
              "x": 1,
              "class": "diff-point",
              "r": 3.5
            },
            {
              "x": 4,
              "class": "diff-point",
              "r": 3.5
            },
            {
              "x": 7,
              "class": "diff-point",
              "r": 3.5
            },
            {
              "x": 10,
              "class": "diff-point",
              "r": 3.5
            },
            {
              "x": 13,
              "class": "diff-point",
              "r": 3.5
            },
            {
              "x": 16,
              "class": "diff-point",
              "r": 3.5
            },
            {
              "x": 19,
              "class": "diff-point",
              "r": 3.5
            },
            {
              "x": 22,
              "class": "diff-point",
              "r": 3.5
            },
            {
              "x": 23,
              "class": "diff-point",
              "r": 3.5
            },
            {
              "x": 24,
              "class": "diff-point",
              "r": 3.5
            },
            {
              "x": 25,
              "class": "diff-point",
              "r": 3.5
            },
            {
              "x": 26,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 27,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 28,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 29,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 30,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 31,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 32,
              "class": "drift-point",
              "r": 4.8
            }
          ],
          "annotations": [
            {
              "text": "recent mean exceeds Hoeffding bound",
              "x": 14,
              "y": 0.51,
              "class": "callout"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-005.series"
        }
      },
      {
        "componentInstanceId": "CHART-ERR-005.error.0",
        "componentType": "performance_metric_view",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "time",
          "y_field": "error",
          "x_min": 1,
          "x_max": 32,
          "y_min": 0,
          "y_max": 0.52,
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 22,
            "bottom": 34,
            "left": 48
          },
          "x_ticks": [],
          "y_ticks": [
            0,
            0.15,
            0.3,
            0.45
          ],
          "x_axis_label": "weighted error trend",
          "axis_label_x": 208,
          "axis_label_y": 177,
          "y_axis_label": false,
          "line_class": "weighted-error-line",
          "show_points": false,
          "vertical_markers": [
            {
              "x": 26,
              "class": "state-line"
            }
          ],
          "point_highlights": [
            {
              "x": 1,
              "class": "weighted-error-point",
              "r": 3.5
            },
            {
              "x": 8,
              "class": "weighted-error-point",
              "r": 3.5
            },
            {
              "x": 16,
              "class": "weighted-error-point",
              "r": 3.5
            },
            {
              "x": 24,
              "class": "weighted-error-point",
              "r": 3.5
            },
            {
              "x": 32,
              "class": "weighted-error-point",
              "r": 3.5
            }
          ],
          "annotations": [
            {
              "text": "recent error 상승",
              "x": 19,
              "y": 0.43,
              "class": "drift-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-005.series"
        }
      },
      {
        "componentInstanceId": "CHART-ERR-005.timeline.0",
        "componentType": "state_timeline",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "start_field": "start",
          "end_field": "end",
          "window_role_field": "role",
          "window_id_field": "label",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 30,
            "right": 24,
            "bottom": 38,
            "left": 48
          },
          "track_y": 68,
          "track_height": 28,
          "x_ticks": [
            1,
            8,
            16,
            24,
            32
          ],
          "axis_label": "HDDM warning and drift markers",
          "axis_label_x": 228,
          "axis_label_y": 179,
          "role_class_map": {
            "normal": "normal-fill",
            "warning": "warning-fill",
            "drift": "drift-fill"
          },
          "track_overlays": [
            {
              "x0": 1,
              "x1": 32,
              "y": 116,
              "height": 18,
              "class": "two-sided-fill",
              "label": "two-sided guard band",
              "label_class": "bar-label",
              "label_dy": 14
            }
          ],
          "markers": [
            {
              "x": 26,
              "class": "state-line",
              "circle": true,
              "circle_class": "drift-point",
              "radius": 7
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-005.timeline"
        }
      },
      {
        "componentInstanceId": "CHART-ERR-005.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-005.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-ERR-005.summary": [
        {
          "label": "final diff",
          "value": 0.5,
          "displayValue": "0.50"
        },
        {
          "label": "warning",
          "value": 22,
          "displayValue": "t=22"
        },
        {
          "label": "drift",
          "value": 26,
          "displayValue": "t=26"
        }
      ],
      "chart.CHART-ERR-005.series": [
        {
          "time": 1,
          "diff": 0.01,
          "error": 0.08
        },
        {
          "time": 2,
          "diff": 0.02,
          "error": 0.08
        },
        {
          "time": 3,
          "diff": 0.01,
          "error": 0.09
        },
        {
          "time": 4,
          "diff": 0.03,
          "error": 0.09
        },
        {
          "time": 5,
          "diff": 0.02,
          "error": 0.1
        },
        {
          "time": 6,
          "diff": 0.04,
          "error": 0.1
        },
        {
          "time": 7,
          "diff": 0.05,
          "error": 0.11
        },
        {
          "time": 8,
          "diff": 0.05,
          "error": 0.12
        },
        {
          "time": 9,
          "diff": 0.06,
          "error": 0.12
        },
        {
          "time": 10,
          "diff": 0.07,
          "error": 0.13
        },
        {
          "time": 11,
          "diff": 0.08,
          "error": 0.14
        },
        {
          "time": 12,
          "diff": 0.09,
          "error": 0.15
        },
        {
          "time": 13,
          "diff": 0.1,
          "error": 0.16
        },
        {
          "time": 14,
          "diff": 0.12,
          "error": 0.17
        },
        {
          "time": 15,
          "diff": 0.13,
          "error": 0.19
        },
        {
          "time": 16,
          "diff": 0.15,
          "error": 0.2
        },
        {
          "time": 17,
          "diff": 0.16,
          "error": 0.22
        },
        {
          "time": 18,
          "diff": 0.18,
          "error": 0.23
        },
        {
          "time": 19,
          "diff": 0.2,
          "error": 0.25
        },
        {
          "time": 20,
          "diff": 0.22,
          "error": 0.27
        },
        {
          "time": 21,
          "diff": 0.24,
          "error": 0.29
        },
        {
          "time": 22,
          "diff": 0.27,
          "error": 0.31
        },
        {
          "time": 23,
          "diff": 0.29,
          "error": 0.33
        },
        {
          "time": 24,
          "diff": 0.32,
          "error": 0.35
        },
        {
          "time": 25,
          "diff": 0.35,
          "error": 0.38
        },
        {
          "time": 26,
          "diff": 0.38,
          "error": 0.4
        },
        {
          "time": 27,
          "diff": 0.41,
          "error": 0.42
        },
        {
          "time": 28,
          "diff": 0.43,
          "error": 0.43
        },
        {
          "time": 29,
          "diff": 0.45,
          "error": 0.44
        },
        {
          "time": 30,
          "diff": 0.47,
          "error": 0.45
        },
        {
          "time": 31,
          "diff": 0.49,
          "error": 0.46
        },
        {
          "time": 32,
          "diff": 0.5,
          "error": 0.47
        }
      ],
      "chart.CHART-ERR-005.timeline": [
        {
          "label": "normal",
          "role": "normal",
          "start": 1,
          "end": 22
        },
        {
          "label": "warning",
          "role": "warning",
          "start": 22,
          "end": 26
        },
        {
          "label": "drift",
          "role": "drift",
          "start": 26,
          "end": 32
        }
      ],
      "chart.CHART-ERR-005.notes": [
        {
          "title": "해석",
          "text": "HDDM은 reference window와 recent window의 error mean 차이를 Hoeffding bound와 비교한다. 이 예시에서는 mean difference가 0.50까지 커지고 error trend도 0.47까지 상승해, t=26 이후를 Hoeffding-bound 기반 error-rate drift 후보로 해석한다.",
          "legend": [
            {
              "label": "mean difference",
              "class": "swatch-mean-diff"
            },
            {
              "label": "error trend",
              "class": "swatch-error-trend"
            },
            {
              "label": "warning bound",
              "class": "swatch-warning-threshold"
            },
            {
              "label": "drift bound",
              "class": "swatch-drift-threshold"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-ERR-006",
    "title": "CHART-ERR-006 - 최근 정확도 하락으로 본 STEPD 드리프트 전환",
    "originalPath": "./drift_report_charts/chart_err_006.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_err_006",
      "displayName": "CHART-ERR-006 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 146px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "최근 정확도와 전체 정확도 비교",
          "description": "recent accuracy가 0.91에서 0.64까지 하락하며 overall보다 빠르게 낮아진다.",
          "headerHeight": 76,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 0,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "STEPD 임계값 차트",
          "description": "gap이 t=15에서 0.12, t=20에서 0.16으로 기준을 넘는다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "상태 타임라인",
          "description": "t=1~14 normal, t=15~19 warning, t=20 이후 drift로 읽는다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 64,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "notes",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-ERR-006.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-006.summary"
        }
      },
      {
        "componentInstanceId": "CHART-ERR-006.accuracy.0",
        "componentType": "performance_metric_view",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "time",
          "y_field": "recent",
          "secondary_value_field": "overall",
          "x_min": 1,
          "x_max": 30,
          "y_min": 0.58,
          "y_max": 0.94,
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 30,
            "bottom": 62,
            "left": 58
          },
          "x_ticks": [
            1,
            8,
            15,
            22,
            30
          ],
          "y_ticks": [
            0.6,
            0.7,
            0.8,
            0.9
          ],
          "x_axis_label": "stream index",
          "y_axis_label": "accuracy",
          "line_class": "recent-line",
          "secondary_line_class": "overall-line",
          "show_points": false,
          "show_secondary_points": false,
          "vertical_markers": [
            {
              "x": 15,
              "class": "warning-line"
            },
            {
              "x": 20,
              "class": "marker-line"
            }
          ],
          "point_highlights": [
            {
              "x": 1,
              "class": "recent-point",
              "r": 3.5
            },
            {
              "x": 4,
              "class": "recent-point",
              "r": 3.5
            },
            {
              "x": 7,
              "class": "recent-point",
              "r": 3.5
            },
            {
              "x": 10,
              "class": "recent-point",
              "r": 3.5
            },
            {
              "x": 13,
              "class": "recent-point",
              "r": 3.5
            },
            {
              "x": 15,
              "class": "warning-point",
              "r": 6
            },
            {
              "x": 16,
              "class": "recent-point",
              "r": 3.5
            },
            {
              "x": 19,
              "class": "recent-point",
              "r": 3.5
            },
            {
              "x": 20,
              "class": "drift-point",
              "r": 6
            },
            {
              "x": 22,
              "class": "recent-point",
              "r": 3.5
            },
            {
              "x": 25,
              "class": "recent-point",
              "r": 3.5
            },
            {
              "x": 28,
              "class": "recent-point",
              "r": 3.5
            },
            {
              "x": 1,
              "field": "overall",
              "class": "overall-point",
              "r": 3.5
            },
            {
              "x": 7,
              "field": "overall",
              "class": "overall-point",
              "r": 3.5
            },
            {
              "x": 13,
              "field": "overall",
              "class": "overall-point",
              "r": 3.5
            },
            {
              "x": 19,
              "field": "overall",
              "class": "overall-point",
              "r": 3.5
            },
            {
              "x": 25,
              "field": "overall",
              "class": "overall-point",
              "r": 3.5
            }
          ],
          "annotations": [
            {
              "text": "recent window drops below overall",
              "x": 10,
              "y": 0.91,
              "class": "callout"
            },
            {
              "text": "warning",
              "x": 14,
              "y": 0.62,
              "class": "warning-text"
            },
            {
              "text": "drift",
              "x": 20.6,
              "y": 0.62,
              "class": "drift-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-006.series"
        }
      },
      {
        "componentInstanceId": "CHART-ERR-006.gap.0",
        "componentType": "distance_metric_view",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "time",
          "y_field": "gap",
          "x_min": 1,
          "x_max": 30,
          "y_min": 0,
          "y_max": 0.22,
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 18,
            "right": 24,
            "bottom": 38,
            "left": 48
          },
          "x_ticks": [],
          "y_ticks": [
            0.0,
            0.1,
            0.15,
            0.2
          ],
          "x_axis_label": "overall - recent accuracy gap",
          "axis_label_x": 218,
          "axis_label_y": 179,
          "y_axis_label": false,
          "line_class": "distance-line",
          "primary_point_class": "distance-point",
          "show_points": false,
          "horizontal_markers": [
            {
              "y": 0.1,
              "class": "warning-line",
              "label": "warning",
              "label_class": "warning-text",
              "label_x": 25.5,
              "label_dy": -6
            },
            {
              "y": 0.15,
              "class": "drift-line",
              "label": "drift",
              "label_class": "drift-text",
              "label_x": 27.1,
              "label_dy": -6
            }
          ],
          "point_highlights": [
            {
              "x": 15,
              "class": "warning-point",
              "r": 5
            },
            {
              "x": 20,
              "class": "drift-point",
              "r": 6
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-006.series"
        }
      },
      {
        "componentInstanceId": "CHART-ERR-006.timeline.0",
        "componentType": "state_timeline",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "start_field": "start",
          "end_field": "end",
          "window_role_field": "role",
          "window_id_field": "label",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 34,
            "right": 24,
            "bottom": 38,
            "left": 48
          },
          "track_y": 74,
          "track_height": 30,
          "x_ticks": [],
          "axis_label": "STEPD supervised state timeline",
          "axis_label_x": 228,
          "axis_label_y": 179,
          "role_class_map": {
            "normal": "normal-fill",
            "warning": "warning-fill",
            "drift": "drift-fill"
          },
          "markers": [
            {
              "x": 15,
              "class": "warning-line",
              "circle": true,
              "circle_class": "warning-point",
              "radius": 6
            },
            {
              "x": 20,
              "class": "marker-line",
              "circle": true,
              "circle_class": "drift-point",
              "radius": 6
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-006.timeline"
        }
      },
      {
        "componentInstanceId": "CHART-ERR-006.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-ERR-006.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-ERR-006.summary": [
        {
          "label": "recent acc",
          "value": 0.68,
          "displayValue": "0.68"
        },
        {
          "label": "overall acc",
          "value": 0.78,
          "displayValue": "0.78"
        },
        {
          "label": "drift",
          "value": 20,
          "displayValue": "t=20"
        }
      ],
      "chart.CHART-ERR-006.series": [
        {
          "time": 1,
          "recent": 0.91,
          "overall": 0.91,
          "gap": 0
        },
        {
          "time": 2,
          "recent": 0.9,
          "overall": 0.91,
          "gap": 0.01
        },
        {
          "time": 3,
          "recent": 0.91,
          "overall": 0.91,
          "gap": 0
        },
        {
          "time": 4,
          "recent": 0.89,
          "overall": 0.91,
          "gap": 0.02
        },
        {
          "time": 5,
          "recent": 0.9,
          "overall": 0.9,
          "gap": 0
        },
        {
          "time": 6,
          "recent": 0.88,
          "overall": 0.9,
          "gap": 0.02
        },
        {
          "time": 7,
          "recent": 0.87,
          "overall": 0.9,
          "gap": 0.03
        },
        {
          "time": 8,
          "recent": 0.86,
          "overall": 0.9,
          "gap": 0.04
        },
        {
          "time": 9,
          "recent": 0.85,
          "overall": 0.89,
          "gap": 0.04
        },
        {
          "time": 10,
          "recent": 0.84,
          "overall": 0.89,
          "gap": 0.05
        },
        {
          "time": 11,
          "recent": 0.82,
          "overall": 0.89,
          "gap": 0.07
        },
        {
          "time": 12,
          "recent": 0.8,
          "overall": 0.88,
          "gap": 0.08
        },
        {
          "time": 13,
          "recent": 0.79,
          "overall": 0.88,
          "gap": 0.09
        },
        {
          "time": 14,
          "recent": 0.77,
          "overall": 0.87,
          "gap": 0.1
        },
        {
          "time": 15,
          "recent": 0.75,
          "overall": 0.87,
          "gap": 0.12
        },
        {
          "time": 16,
          "recent": 0.73,
          "overall": 0.86,
          "gap": 0.13
        },
        {
          "time": 17,
          "recent": 0.72,
          "overall": 0.86,
          "gap": 0.14
        },
        {
          "time": 18,
          "recent": 0.7,
          "overall": 0.85,
          "gap": 0.15
        },
        {
          "time": 19,
          "recent": 0.69,
          "overall": 0.84,
          "gap": 0.15
        },
        {
          "time": 20,
          "recent": 0.68,
          "overall": 0.84,
          "gap": 0.16
        },
        {
          "time": 21,
          "recent": 0.67,
          "overall": 0.83,
          "gap": 0.16
        },
        {
          "time": 22,
          "recent": 0.66,
          "overall": 0.82,
          "gap": 0.16
        },
        {
          "time": 23,
          "recent": 0.65,
          "overall": 0.82,
          "gap": 0.17
        },
        {
          "time": 24,
          "recent": 0.65,
          "overall": 0.81,
          "gap": 0.16
        },
        {
          "time": 25,
          "recent": 0.64,
          "overall": 0.8,
          "gap": 0.16
        },
        {
          "time": 26,
          "recent": 0.64,
          "overall": 0.8,
          "gap": 0.16
        },
        {
          "time": 27,
          "recent": 0.65,
          "overall": 0.79,
          "gap": 0.14
        },
        {
          "time": 28,
          "recent": 0.66,
          "overall": 0.79,
          "gap": 0.13
        },
        {
          "time": 29,
          "recent": 0.67,
          "overall": 0.78,
          "gap": 0.11
        },
        {
          "time": 30,
          "recent": 0.68,
          "overall": 0.78,
          "gap": 0.1
        }
      ],
      "chart.CHART-ERR-006.timeline": [
        {
          "label": "normal",
          "role": "normal",
          "start": 1,
          "end": 15
        },
        {
          "label": "warning",
          "role": "warning",
          "start": 15,
          "end": 20
        },
        {
          "label": "drift",
          "role": "drift",
          "start": 20,
          "end": 30
        }
      ],
      "chart.CHART-ERR-006.notes": [
        {
          "title": "해석",
          "text": "STEPD는 최근 window accuracy와 전체 historical accuracy를 비교한다. 이 예시에서는 t=20의 gap이 0.16으로 drift threshold 0.15를 넘어, 최근 supervised 성능 저하에 따른 error-rate drift 후보로 해석한다.",
          "legend": [
            {
              "label": "recent accuracy",
              "class": "swatch-recent-accuracy"
            },
            {
              "label": "overall accuracy",
              "class": "swatch-overall-accuracy"
            },
            {
              "label": "warning threshold",
              "class": "swatch-warning-threshold"
            },
            {
              "label": "drift threshold",
              "class": "swatch-drift-threshold"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-EXPL-001",
    "title": "CHART-EXPL-001 - risk_score 중심으로 바뀐 SHAP 설명 구조",
    "originalPath": "./drift_report_charts/chart_expl_001.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_expl_001",
      "displayName": "CHART-EXPL-001 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 146px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "SHAP 요약 비교",
          "description": "risk_score는 0.27에서 0.36으로 증가하고 amount는 0.31에서 0.18로 낮아진다.",
          "headerHeight": 76,
          "stageInset": {
            "top": 84,
            "right": 16,
            "bottom": -8,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "SHAP 값 분포",
          "description": "risk_score SHAP peak가 -0.04에서 0.12로 양수 방향 이동한다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "클래스별 SHAP 히트맵",
          "description": "class C risk_score heat가 0.48로 가장 높다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "notes",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-EXPL-001.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-EXPL-001.summary"
        }
      },
      {
        "componentInstanceId": "CHART-EXPL-001.shap_summary.0",
        "componentType": "bar_chart",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "horizontal_grouped",
          "category_field": "feature",
          "series_fields": [
            "baseline",
            "current"
          ],
          "series_classes": [
            "base-bar",
            "current-bar"
          ],
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 28,
            "bottom": 62,
            "left": 92
          },
          "x_max": 0.42,
          "x_ticks": [
            0,
            0.1,
            0.2,
            0.3,
            0.4
          ],
          "x_axis_label": "mean |SHAP|",
          "axis_label_x": 337,
          "axis_label_y": 428,
          "first_y": 38,
          "row_gap": 48,
          "bar_height": 13,
          "series_gap": 5,
          "bar_radius": 4,
          "rank_connectors": [
            {
              "from_field": "baseline",
              "to_field": "current",
              "class": "rank-line",
              "min_abs_delta": 0.08
            }
          ],
          "annotations": [
            {
              "text": "risk_score and channel gain importance",
              "x": 284,
              "y": 19,
              "class": "warning-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-EXPL-001.features"
        }
      },
      {
        "componentInstanceId": "CHART-EXPL-001.distribution.0",
        "componentType": "distribution_view",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "distribution_style": "density_area",
          "x_field": "shap",
          "primary_value_field": "baseline",
          "secondary_value_field": "current",
          "x_min": -0.38,
          "x_max": 0.38,
          "y_min": 0,
          "y_max": 40,
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 24,
            "bottom": 34,
            "left": 44
          },
          "x_ticks": [],
          "y_ticks": [
            0,
            20,
            40
          ],
          "x_axis_label": "risk_score SHAP value",
          "axis_label_x": 204,
          "axis_label_y": 177,
          "y_axis_label": false,
          "primary_area_class": "base-area",
          "secondary_area_class": "current-red-area",
          "vertical_markers": [
            {
              "x": 0,
              "class": "axis-line"
            }
          ],
          "annotations": [
            {
              "text": "current shifts positive",
              "x": 0.03,
              "y": 36,
              "class": "warning-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-EXPL-001.distribution"
        }
      },
      {
        "componentInstanceId": "CHART-EXPL-001.class_heatmap.0",
        "componentType": "heatmap",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "matrix_style": "heatmap_grid",
          "x_field": "feature",
          "y_field": "class",
          "values_field": "values",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 18,
            "right": 16,
            "bottom": 34,
            "left": 70
          },
          "x_values": [
            "amount",
            "risk_score",
            "tenure",
            "channel",
            "region",
            "device"
          ],
          "y_values": [
            "class A",
            "class B",
            "class C"
          ],
          "x_labels": [
            "amount",
            "risk",
            "tenure",
            "channel",
            "region",
            "device"
          ],
          "show_x_labels": true,
          "show_y_labels": true,
          "show_y_axis": false,
          "value_min": 0,
          "value_max": 0.5,
          "palette": [
            [
              0,
              "#dee9f1"
            ],
            [
              0.55,
              "#c9952f"
            ],
            [
              1,
              "#b95a50"
            ]
          ],
          "show_cell_values": true,
          "cell_value_min": 0.34,
          "cell_value_class": "bar-label",
          "cell_value_dy": 4,
          "x_axis_label": "class-wise SHAP drift",
          "axis_label_x": 232,
          "axis_label_y": 179
        },
        "dataBinding": {
          "source": "chart.CHART-EXPL-001.heatmap"
        }
      },
      {
        "componentInstanceId": "CHART-EXPL-001.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-EXPL-001.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-EXPL-001.summary": [
        {
          "label": "top shift",
          "value": "risk_score",
          "displayValue": "risk_score"
        },
        {
          "label": "rank change",
          "value": 3,
          "displayValue": "+3"
        },
        {
          "label": "class heat",
          "value": 0.48,
          "displayValue": "0.48"
        }
      ],
      "chart.CHART-EXPL-001.features": [
        {
          "feature": "amount",
          "baseline": 0.31,
          "current": 0.18
        },
        {
          "feature": "risk_score",
          "baseline": 0.27,
          "current": 0.36
        },
        {
          "feature": "tenure",
          "baseline": 0.22,
          "current": 0.14
        },
        {
          "feature": "channel",
          "baseline": 0.17,
          "current": 0.24
        },
        {
          "feature": "region",
          "baseline": 0.13,
          "current": 0.19
        },
        {
          "feature": "device",
          "baseline": 0.1,
          "current": 0.12
        }
      ],
      "chart.CHART-EXPL-001.distribution": [
        {
          "shap": -0.36,
          "baseline": 2,
          "current": 1
        },
        {
          "shap": -0.28,
          "baseline": 5,
          "current": 3
        },
        {
          "shap": -0.2,
          "baseline": 12,
          "current": 7
        },
        {
          "shap": -0.12,
          "baseline": 24,
          "current": 14
        },
        {
          "shap": -0.04,
          "baseline": 36,
          "current": 22
        },
        {
          "shap": 0.04,
          "baseline": 31,
          "current": 31
        },
        {
          "shap": 0.12,
          "baseline": 18,
          "current": 36
        },
        {
          "shap": 0.2,
          "baseline": 8,
          "current": 29
        },
        {
          "shap": 0.28,
          "baseline": 3,
          "current": 18
        },
        {
          "shap": 0.36,
          "baseline": 1,
          "current": 8
        }
      ],
      "chart.CHART-EXPL-001.heatmap": [
        {
          "class": "class A",
          "values": [
            0.12,
            0.22,
            0.18,
            0.16,
            0.14,
            0.1
          ]
        },
        {
          "class": "class B",
          "values": [
            0.18,
            0.36,
            0.21,
            0.29,
            0.22,
            0.16
          ]
        },
        {
          "class": "class C",
          "values": [
            0.16,
            0.48,
            0.2,
            0.34,
            0.31,
            0.19
          ]
        }
      ],
      "chart.CHART-EXPL-001.notes": [
        {
          "title": "해석",
          "text": "SHAP drift는 feature contribution 자체의 분포와 중요도 순위가 baseline 대비 바뀌는지 확인한다. 이 예시에서는 risk_score 중요도와 SHAP value가 함께 증가하고 class C heat가 0.48로 높아 explanation-level drift 후보로 해석한다.",
          "legend": [
            {
              "label": "baseline",
              "class": "swatch-base"
            },
            {
              "label": "current",
              "class": "swatch-current-red"
            },
            {
              "label": "rank shift",
              "class": "swatch-shift"
            },
            {
              "label": "class heat",
              "class": "swatch-heat"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-EXPL-002",
    "title": "CHART-EXPL-002 - query_age 분기로 드러난 현재 구간 분리",
    "originalPath": "./drift_report_charts/chart_expl_002.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_expl_002",
      "displayName": "CHART-EXPL-002 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 146px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "특징 중요도와 시간 분기 수",
          "description": "query_age가 importance 0.34, time split 18로 가장 높다.",
          "headerHeight": 76,
          "stageInset": {
            "top": 84,
            "right": 16,
            "bottom": -8,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "분기 경로 다이어그램",
          "description": "query_age > 14d 이후 device = mobile에서 current 82% leaf가 만들어진다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "세그먼트 분포",
          "description": "S4 segment는 baseline 18%, current 82%로 current가 지배적이다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "notes",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-EXPL-002.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-EXPL-002.summary"
        }
      },
      {
        "componentInstanceId": "CHART-EXPL-002.importance.0",
        "componentType": "bar_chart",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "horizontal_grouped",
          "category_field": "feature",
          "series_fields": [
            "importance",
            "timeSplits"
          ],
          "series_classes": [
            "importance-bar",
            "time-bar"
          ],
          "series_x_maxes": [
            0.38,
            20
          ],
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 46,
            "bottom": 62,
            "left": 94
          },
          "x_max": 0.38,
          "x_ticks": [
            0,
            0.1,
            0.2,
            0.3
          ],
          "x_axis_label": "feature importance / time split count",
          "axis_label_x": 332,
          "axis_label_y": 428,
          "first_y": 36,
          "row_gap": 48,
          "bar_height": 14,
          "series_gap": 5,
          "bar_radius": 4,
          "show_series_value_labels": true,
          "series_value_label_fields": [
            null,
            "timeLabel"
          ],
          "value_label_class": "axis-tick",
          "value_label_dx": 8,
          "value_label_dy": -2,
          "annotations": [
            {
              "text": "query_age dominates time/domain split",
              "x": 250,
              "y": 19,
              "class": "warning-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-EXPL-002.features"
        }
      },
      {
        "componentInstanceId": "CHART-EXPL-002.path.0",
        "componentType": "node_link_diagram",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "view_box": [
            472,
            185
          ],
          "id_field": "id",
          "label_field": "label",
          "class_field": "class",
          "links": [
            {
              "from": "root",
              "to": "region",
              "from_anchor": "bottom",
              "to_anchor": "top"
            },
            {
              "from": "root",
              "to": "device",
              "from_anchor": "bottom",
              "to_anchor": "top"
            },
            {
              "from": "device",
              "to": "leaf",
              "from_anchor": "bottom",
              "to_anchor": "top"
            }
          ],
          "caption": "representative drift path",
          "caption_x": 236,
          "caption_y": 178
        },
        "dataBinding": {
          "source": "chart.CHART-EXPL-002.path"
        }
      },
      {
        "componentInstanceId": "CHART-EXPL-002.segments.0",
        "componentType": "bar_chart",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "horizontal_stacked",
          "category_field": "segment",
          "series_fields": [
            "baseline",
            "current"
          ],
          "series_classes": [
            "base-bar",
            "current-bar"
          ],
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 18,
            "right": 24,
            "bottom": 32,
            "left": 52
          },
          "first_y": 22,
          "row_gap": 30,
          "bar_height": 16,
          "bar_radius": 4,
          "value_label_series_index": 1,
          "value_label_field": "currentLabel",
          "caption": "baseline / current segment mix",
          "caption_x": 222,
          "caption_y": 177
        },
        "dataBinding": {
          "source": "chart.CHART-EXPL-002.segments"
        }
      },
      {
        "componentInstanceId": "CHART-EXPL-002.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-EXPL-002.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-EXPL-002.summary": [
        {
          "label": "top feature",
          "value": "query_age",
          "displayValue": "query_age"
        },
        {
          "label": "time splits",
          "value": 18,
          "displayValue": "18"
        },
        {
          "label": "current leaf",
          "value": 0.82,
          "displayValue": "82%"
        }
      ],
      "chart.CHART-EXPL-002.features": [
        {
          "feature": "query_age",
          "importance": 0.34,
          "timeSplits": 18,
          "timeLabel": "18"
        },
        {
          "feature": "region",
          "importance": 0.26,
          "timeSplits": 13,
          "timeLabel": "13"
        },
        {
          "feature": "device",
          "importance": 0.18,
          "timeSplits": 8,
          "timeLabel": "8"
        },
        {
          "feature": "amount",
          "importance": 0.13,
          "timeSplits": 5,
          "timeLabel": "5"
        },
        {
          "feature": "channel",
          "importance": 0.08,
          "timeSplits": 4,
          "timeLabel": "4"
        },
        {
          "feature": "tenure",
          "importance": 0.05,
          "timeSplits": 2,
          "timeLabel": "2"
        }
      ],
      "chart.CHART-EXPL-002.path": [
        {
          "id": "root",
          "label": "query_age > 14d",
          "x": 170,
          "y": 14,
          "w": 150,
          "h": 34,
          "class": "node"
        },
        {
          "id": "region",
          "label": "region = APAC",
          "x": 72,
          "y": 78,
          "w": 142,
          "h": 34,
          "class": "node"
        },
        {
          "id": "device",
          "label": "device = mobile",
          "x": 272,
          "y": 78,
          "w": 142,
          "h": 34,
          "class": "node-current"
        },
        {
          "id": "leaf",
          "label": "current 82%",
          "x": 280,
          "y": 132,
          "w": 132,
          "h": 30,
          "class": "node-current"
        }
      ],
      "chart.CHART-EXPL-002.segments": [
        {
          "segment": "S1",
          "baseline": 0.72,
          "current": 0.28,
          "currentLabel": "28%"
        },
        {
          "segment": "S2",
          "baseline": 0.54,
          "current": 0.46,
          "currentLabel": "46%"
        },
        {
          "segment": "S3",
          "baseline": 0.31,
          "current": 0.69,
          "currentLabel": "69%"
        },
        {
          "segment": "S4",
          "baseline": 0.18,
          "current": 0.82,
          "currentLabel": "82%"
        }
      ],
      "chart.CHART-EXPL-002.notes": [
        {
          "title": "해석",
          "text": "Tree feature 기반 감지는 domain classifier tree가 시간 또는 domain을 구분하는 split을 학습했는지 확인한다. 이 예시에서는 query_age split 18회와 current 82% leaf가 함께 나타나 tree feature 기반 drift 후보로 해석한다.",
          "legend": [
            {
              "label": "importance",
              "class": "swatch-importance"
            },
            {
              "label": "time split",
              "class": "swatch-time"
            },
            {
              "label": "current segment",
              "class": "swatch-current-red"
            },
            {
              "label": "baseline",
              "class": "swatch-base"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-GEN-001",
    "title": "CHART-GEN-001 - 임시 지표 상승으로 확인한 일반 드리프트 후보",
    "originalPath": "./drift_report_charts/chart_gen_001.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_gen_001",
      "displayName": "CHART-GEN-001 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 146px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "임계값 포함 지표 추세",
          "description": "metric이 t=15에서 threshold 0.45를 넘고 최종 0.68까지 상승한다.",
          "headerHeight": 76,
          "stageInset": {
            "top": 84,
            "right": 16,
            "bottom": -8,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "기준/현재 분포",
          "description": "reference peak는 0.33/38, current peak는 0.54/37로 오른쪽 이동한다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "경보 근거 요약",
          "description": "final metric 0.68, effect size 0.52, p-value score 0.91을 함께 본다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "notes",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-GEN-001.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-GEN-001.summary"
        }
      },
      {
        "componentInstanceId": "CHART-GEN-001.trend.0",
        "componentType": "trend_line",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "time",
          "y_field": "metric",
          "x_min": 1,
          "x_max": 22,
          "y_min": 0,
          "y_max": 0.75,
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 30,
            "bottom": 62,
            "left": 58
          },
          "x_ticks": [
            1,
            6,
            12,
            18,
            22
          ],
          "y_ticks": [
            0.0,
            0.2,
            0.4,
            0.6
          ],
          "x_axis_label": "time window",
          "y_axis_label": "generic drift metric",
          "line_class": "gen-metric-line",
          "show_points": false,
          "horizontal_markers": [
            {
              "y": 0.45,
              "class": "threshold-line"
            }
          ],
          "vertical_markers": [
            {
              "x": 15,
              "class": "state-line"
            }
          ],
          "point_highlights": [
            {
              "x": 1,
              "class": "gen-metric-point",
              "r": 3.4
            },
            {
              "x": 3,
              "class": "gen-metric-point",
              "r": 3.4
            },
            {
              "x": 5,
              "class": "gen-metric-point",
              "r": 3.4
            },
            {
              "x": 7,
              "class": "gen-metric-point",
              "r": 3.4
            },
            {
              "x": 9,
              "class": "gen-metric-point",
              "r": 3.4
            },
            {
              "x": 11,
              "class": "gen-metric-point",
              "r": 3.4
            },
            {
              "x": 13,
              "class": "gen-metric-point",
              "r": 3.4
            },
            {
              "x": 15,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 16,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 17,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 18,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 19,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 20,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 21,
              "class": "drift-point",
              "r": 4.8
            },
            {
              "x": 22,
              "class": "drift-point",
              "r": 4.8
            }
          ],
          "annotations": [
            {
              "text": "threshold crossed",
              "x": 12.5,
              "y": 0.61,
              "class": "warning-text"
            },
            {
              "text": "fallback chart until method-specific chart exists",
              "x": 2.2,
              "y": 0.7,
              "class": "callout"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-GEN-001.metric"
        }
      },
      {
        "componentInstanceId": "CHART-GEN-001.distribution.0",
        "componentType": "distribution_view",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "distribution_style": "density_area",
          "x_field": "bin",
          "primary_value_field": "reference",
          "secondary_value_field": "current",
          "x_min": 0.05,
          "x_max": 0.89,
          "y_min": 0,
          "y_max": 42,
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 16,
            "right": 24,
            "bottom": 34,
            "left": 46
          },
          "x_ticks": [],
          "y_ticks": [],
          "x_axis_label": "metric value distribution",
          "axis_label_x": 220,
          "axis_label_y": 177,
          "y_axis_label": false,
          "primary_area_class": "gen-ref-area",
          "secondary_area_class": "gen-cur-area",
          "annotations": [
            {
              "text": "current shifts right",
              "x": 0.42,
              "y": 38,
              "class": "warning-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-GEN-001.distribution"
        }
      },
      {
        "componentInstanceId": "CHART-GEN-001.evidence.0",
        "componentType": "bar_chart",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "horizontal_ranked",
          "category_field": "label",
          "value_field": "value",
          "value_label_field": "valueLabel",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 20,
            "right": 28,
            "bottom": 34,
            "left": 118
          },
          "preserve_order": true,
          "x_max": 1,
          "first_y": 28,
          "row_gap": 28,
          "bar_height": 14,
          "bar_radius": 3,
          "caption": "normalized evidence"
        },
        "dataBinding": {
          "source": "chart.CHART-GEN-001.evidence"
        }
      },
      {
        "componentInstanceId": "CHART-GEN-001.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-GEN-001.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-GEN-001.summary": [
        {
          "label": "metric",
          "value": 0.68,
          "displayValue": "0.68"
        },
        {
          "label": "threshold",
          "value": 0.45,
          "displayValue": "0.45"
        },
        {
          "label": "alarm",
          "value": 15,
          "displayValue": "t=15"
        }
      ],
      "chart.CHART-GEN-001.metric": [
        {
          "time": 1,
          "metric": 0.12
        },
        {
          "time": 2,
          "metric": 0.13
        },
        {
          "time": 3,
          "metric": 0.14
        },
        {
          "time": 4,
          "metric": 0.15
        },
        {
          "time": 5,
          "metric": 0.16
        },
        {
          "time": 6,
          "metric": 0.17
        },
        {
          "time": 7,
          "metric": 0.19
        },
        {
          "time": 8,
          "metric": 0.21
        },
        {
          "time": 9,
          "metric": 0.24
        },
        {
          "time": 10,
          "metric": 0.27
        },
        {
          "time": 11,
          "metric": 0.3
        },
        {
          "time": 12,
          "metric": 0.34
        },
        {
          "time": 13,
          "metric": 0.38
        },
        {
          "time": 14,
          "metric": 0.43
        },
        {
          "time": 15,
          "metric": 0.48
        },
        {
          "time": 16,
          "metric": 0.53
        },
        {
          "time": 17,
          "metric": 0.58
        },
        {
          "time": 18,
          "metric": 0.61
        },
        {
          "time": 19,
          "metric": 0.64
        },
        {
          "time": 20,
          "metric": 0.66
        },
        {
          "time": 21,
          "metric": 0.67
        },
        {
          "time": 22,
          "metric": 0.68
        }
      ],
      "chart.CHART-GEN-001.distribution": [
        {
          "bin": 0.05,
          "reference": 4,
          "current": 0
        },
        {
          "bin": 0.12,
          "reference": 10,
          "current": 1
        },
        {
          "bin": 0.19,
          "reference": 20,
          "current": 3
        },
        {
          "bin": 0.26,
          "reference": 31,
          "current": 7
        },
        {
          "bin": 0.33,
          "reference": 38,
          "current": 13
        },
        {
          "bin": 0.4,
          "reference": 34,
          "current": 21
        },
        {
          "bin": 0.47,
          "reference": 24,
          "current": 30
        },
        {
          "bin": 0.54,
          "reference": 14,
          "current": 37
        },
        {
          "bin": 0.61,
          "reference": 7,
          "current": 35
        },
        {
          "bin": 0.68,
          "reference": 3,
          "current": 25
        },
        {
          "bin": 0.75,
          "reference": 1,
          "current": 15
        },
        {
          "bin": 0.82,
          "reference": 0,
          "current": 8
        },
        {
          "bin": 0.89,
          "reference": 0,
          "current": 3
        }
      ],
      "chart.CHART-GEN-001.evidence": [
        {
          "label": "final metric",
          "value": 0.68,
          "valueLabel": "0.68",
          "class": "bar-current"
        },
        {
          "label": "threshold",
          "value": 0.45,
          "valueLabel": "0.45",
          "class": "bar-metric"
        },
        {
          "label": "effect size",
          "value": 0.52,
          "valueLabel": "0.52",
          "class": "bar-current"
        },
        {
          "label": "p-value score",
          "value": 0.91,
          "valueLabel": "0.91",
          "class": "bar-current"
        }
      ],
      "chart.CHART-GEN-001.notes": [
        {
          "title": "해석",
          "text": "Generic chart는 전용 family가 아직 없는 method를 위한 최소 공통 설명이다. 이 예시에서는 metric이 t=15 이후 threshold를 넘고 current distribution도 오른쪽으로 이동해 drift 후보로 해석한다. 전용 chart가 정의되면 해당 family chart로 대체해야 한다.",
          "legend": [
            {
              "label": "drift metric",
              "class": "swatch-metric"
            },
            {
              "label": "reference",
              "class": "swatch-reference"
            },
            {
              "label": "current",
              "class": "swatch-current-red"
            },
            {
              "label": "threshold",
              "class": "swatch-threshold"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-HIST-001",
    "title": "CHART-HIST-001 - 높은 값 구간 증가로 줄어든 히스토그램 겹침",
    "originalPath": "./drift_report_charts/chart_hist_001.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_hist_001",
      "displayName": "CHART-HIST-001 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 146px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "히스토그램 중첩",
          "description": "20-30 bin은 0.16에서 0.10으로 줄고 70-80 bin은 0.05에서 0.10으로 늘어나는지 본다.",
          "headerHeight": 76,
          "stageInset": {
            "top": 84,
            "right": 16,
            "bottom": -8,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "교집합 기여",
          "description": "intersection 0.820 중 중심부 bin은 유지되고 낮은 bin 손실이 생기는지 확인한다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "거리 추세",
          "description": "HINC가 직전 0.24에서 현재 0.18로 관리 기준 0.22 아래로 내려왔는지 읽는다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "notes",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-HIST-001.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-HIST-001.summary"
        }
      },
      {
        "componentInstanceId": "CHART-HIST-001.histogram.0",
        "componentType": "distribution_view",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "distribution_style": "histogram_overlay",
          "x0_field": "x0",
          "x1_field": "x1",
          "primary_value_field": "reference",
          "secondary_value_field": "current",
          "overlap_value_field": "intersection",
          "x_min": 0,
          "x_max": 10,
          "y_min": 0,
          "y_max": 0.2375,
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 20,
            "right": 22,
            "bottom": 58,
            "left": 58
          },
          "x_ticks": [
            0.5,
            2.5,
            4.5,
            6.5,
            8.5
          ],
          "x_tick_labels": [
            "0-10",
            "20-30",
            "40-50",
            "60-70",
            "80-90"
          ],
          "y_ticks": [
            0,
            0.05,
            0.1,
            0.15,
            0.2
          ],
          "x_axis_label": "histogram bin",
          "y_axis_label": "확률",
          "primary_bar_class": "ref-bar",
          "secondary_bar_class": "cur-bar",
          "overlap_bar_class": "overlap-bar",
          "primary_width_fraction": 0.42,
          "secondary_width_fraction": 0.42,
          "secondary_offset_fraction": 0.5,
          "overlap_width_fraction": 0.45,
          "overlap_offset_fraction": 0.27,
          "bin_gap": 1,
          "bar_radius": 3,
          "annotations": [
            {
              "text": "intersection 0.82 / complement 0.18",
              "x": 3.4,
              "y": 0.226,
              "class": "callout"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-HIST-001.histogram"
        }
      },
      {
        "componentInstanceId": "CHART-HIST-001.intersection.0",
        "componentType": "bar_chart",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "horizontal_ranked",
          "category_field": "bin",
          "value_field": "intersection",
          "value_label_field": "intersectionLabel",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 8,
            "right": 22,
            "bottom": 28,
            "left": 92
          },
          "limit": 5,
          "x_max": 0.2,
          "first_y": 18,
          "row_gap": 27,
          "bar_height": 16,
          "bar_radius": 3,
          "bar_class": "intersection-bar",
          "highlight_class": "intersection-bar-highlight",
          "caption": "min(p, q)"
        },
        "dataBinding": {
          "source": "chart.CHART-HIST-001.intersection"
        }
      },
      {
        "componentInstanceId": "CHART-HIST-001.trend.0",
        "componentType": "trend_line",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "window",
          "y_field": "hinc",
          "x_min": 1,
          "x_max": 7,
          "y_min": 0,
          "y_max": 0.34,
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 18,
            "bottom": 34,
            "left": 48
          },
          "x_ticks": [],
          "y_ticks": [
            0,
            0.22,
            0.34
          ],
          "x_axis_label": "window",
          "axis_label_x": 218,
          "axis_label_y": 177,
          "y_axis_label": false,
          "line_class": "distance-trend-line",
          "primary_point_class": "distance-trend-point",
          "show_points": true,
          "point_radius": 4,
          "horizontal_markers": [
            {
              "y": 0.22,
              "class": "threshold-line",
              "label": "관리 기준",
              "label_class": "callout",
              "label_x": 5.7,
              "label_dy": -7
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-HIST-001.trend"
        }
      },
      {
        "componentInstanceId": "CHART-HIST-001.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-HIST-001.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-HIST-001.summary": [
        {
          "label": "HINC",
          "value": 0.18,
          "displayValue": "0.180"
        },
        {
          "label": "Intersection",
          "value": 0.82,
          "displayValue": "0.820"
        },
        {
          "label": "손실 최대 bin",
          "value": "20-30",
          "displayValue": "20-30"
        }
      ],
      "chart.CHART-HIST-001.histogram": [
        {
          "bin": "0-10",
          "x0": 0,
          "x1": 1,
          "reference": 0.06,
          "current": 0.03,
          "intersection": 0.03
        },
        {
          "bin": "10-20",
          "x0": 1,
          "x1": 2,
          "reference": 0.1,
          "current": 0.06,
          "intersection": 0.06
        },
        {
          "bin": "20-30",
          "x0": 2,
          "x1": 3,
          "reference": 0.16,
          "current": 0.1,
          "intersection": 0.1
        },
        {
          "bin": "30-40",
          "x0": 3,
          "x1": 4,
          "reference": 0.19,
          "current": 0.15,
          "intersection": 0.15
        },
        {
          "bin": "40-50",
          "x0": 4,
          "x1": 5,
          "reference": 0.18,
          "current": 0.17,
          "intersection": 0.17
        },
        {
          "bin": "50-60",
          "x0": 5,
          "x1": 6,
          "reference": 0.14,
          "current": 0.17,
          "intersection": 0.14
        },
        {
          "bin": "60-70",
          "x0": 6,
          "x1": 7,
          "reference": 0.09,
          "current": 0.13,
          "intersection": 0.09
        },
        {
          "bin": "70-80",
          "x0": 7,
          "x1": 8,
          "reference": 0.05,
          "current": 0.1,
          "intersection": 0.05
        },
        {
          "bin": "80-90",
          "x0": 8,
          "x1": 9,
          "reference": 0.02,
          "current": 0.06,
          "intersection": 0.02
        },
        {
          "bin": "90+",
          "x0": 9,
          "x1": 10,
          "reference": 0.01,
          "current": 0.03,
          "intersection": 0.01
        }
      ],
      "chart.CHART-HIST-001.intersection": [
        {
          "bin": "40-50",
          "intersection": 0.17,
          "intersectionLabel": "0.17"
        },
        {
          "bin": "30-40",
          "intersection": 0.15,
          "intersectionLabel": "0.15"
        },
        {
          "bin": "50-60",
          "intersection": 0.14,
          "intersectionLabel": "0.14"
        },
        {
          "bin": "20-30",
          "intersection": 0.1,
          "intersectionLabel": "0.10"
        },
        {
          "bin": "10-20",
          "intersection": 0.06,
          "intersectionLabel": "0.06"
        }
      ],
      "chart.CHART-HIST-001.trend": [
        {
          "window": 1,
          "hinc": 0.11
        },
        {
          "window": 2,
          "hinc": 0.13
        },
        {
          "window": 3,
          "hinc": 0.15
        },
        {
          "window": 4,
          "hinc": 0.18
        },
        {
          "window": 5,
          "hinc": 0.21
        },
        {
          "window": 6,
          "hinc": 0.24
        },
        {
          "window": 7,
          "hinc": 0.18
        }
      ],
      "chart.CHART-HIST-001.notes": [
        {
          "title": "해석",
          "text": "이 예시에서는 현재 histogram이 기준보다 높은 값 구간으로 이동해 70-80, 80-90 bin 확률이 늘고 20-30 bin 확률은 줄어든다. Intersection은 0.820이고 HINC는 0.180으로 현재 window에서는 관리 기준 0.220 아래다. 따라서 강한 drift 확정보다는 완화 중인 histogram 분포 이동 후보로 해석한다.",
          "legend": [
            {
              "label": "기준 확률",
              "class": "swatch-reference"
            },
            {
              "label": "현재 확률",
              "class": "swatch-current-red"
            },
            {
              "label": "Intersection",
              "class": "swatch-overlap"
            },
            {
              "label": "거리",
              "class": "swatch-distance"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-MEAN-001",
    "title": "CHART-MEAN-001 - 현재 구간 평균 상승으로 본 드리프트 후보",
    "originalPath": "./drift_report_charts/chart_mean_001.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_mean_001",
      "displayName": "CHART-MEAN-001 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 146px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "분포와 평균 위치",
          "description": "현재 평균 57.8이 기준 평균 51.2보다 6.6 높고 분포 중심도 오른쪽으로 이동한다.",
          "headerHeight": 76,
          "stageInset": {
            "top": 84,
            "right": 16,
            "bottom": -8,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "평균 95% CI",
          "description": "기준 49.6~52.8과 현재 55.9~59.7 CI가 분리된다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "검정과 효과크기",
          "description": "p=0.004와 d=0.72가 통계적 차이와 중간 이상 효과를 함께 가리킨다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "notes",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-MEAN-001.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-MEAN-001.summary"
        }
      },
      {
        "componentInstanceId": "CHART-MEAN-001.distribution.0",
        "componentType": "distribution_summary_plot",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "distribution_style": "violin_summary",
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 22,
            "right": 28,
            "bottom": 60,
            "left": 58
          },
          "y_min": 34,
          "y_max": 78,
          "y_ticks": [
            40,
            50,
            60,
            70
          ],
          "y_axis_label": "feature value",
          "x_positions": [
            243,
            448
          ],
          "density_width": 72,
          "box_width": 68,
          "mean_width": 84,
          "violin_classes": [
            "ref-fill",
            "cur-fill"
          ],
          "box_class": "summary-box",
          "median_class": "median-line",
          "mean_line_class": "mean-line-solid",
          "show_mean_points": false,
          "mean_label_class": "callout",
          "mean_label_dy": -10,
          "group_label_y": 418,
          "annotations": [
            {
              "text": "평균 이동: +6.6",
              "x": 330,
              "y": 40,
              "class": "callout"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-MEAN-001.distribution"
        }
      },
      {
        "componentInstanceId": "CHART-MEAN-001.ci.0",
        "componentType": "bar_chart",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "horizontal_intervals",
          "category_field": "label",
          "value_field": "mean",
          "low_field": "low",
          "high_field": "high",
          "class_field": "class",
          "value_label_field": "valueLabel",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 16,
            "right": 30,
            "bottom": 38,
            "left": 50
          },
          "x_min": 46,
          "x_max": 62,
          "x_ticks": [
            48,
            52,
            56,
            60
          ],
          "first_y": 62,
          "row_gap": 50,
          "point_class": "mean-point",
          "point_radius": 7,
          "x_axis_label": "mean value"
        },
        "dataBinding": {
          "source": "chart.CHART-MEAN-001.ci"
        }
      },
      {
        "componentInstanceId": "CHART-MEAN-001.effect.0",
        "componentType": "bar_chart",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "horizontal_threshold",
          "category_field": "label",
          "value_field": "score",
          "threshold_field": "threshold",
          "value_label_field": "valueLabel",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 15,
            "right": 28,
            "bottom": 32,
            "left": 112
          },
          "x_max": 1.08,
          "first_y": 33,
          "row_gap": 62,
          "bar_height": 18,
          "threshold_class": "threshold-line",
          "over_class": "effect-bar",
          "bar_class": "effect-bar",
          "value_label_dx": 7,
          "caption": "효과크기 기준 / p-value 기준"
        },
        "dataBinding": {
          "source": "chart.CHART-MEAN-001.effect"
        }
      },
      {
        "componentInstanceId": "CHART-MEAN-001.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-MEAN-001.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-MEAN-001.summary": [
        {
          "label": "평균 차이",
          "value": 6.6,
          "displayValue": "+6.6"
        },
        {
          "label": "p-value",
          "value": 0.004,
          "displayValue": "0.004"
        },
        {
          "label": "Cohen's d",
          "value": 0.72,
          "displayValue": "0.72"
        }
      ],
      "chart.CHART-MEAN-001.distribution": [
        {
          "label": "기준",
          "mean": 51.2,
          "meanLabel": "기준 mean 51.2",
          "ciLow": 49.6,
          "ciHigh": 52.8,
          "q1": 45.5,
          "median": 50.8,
          "q3": 56.4,
          "low": 36.5,
          "high": 66.0,
          "class": "ref-fill",
          "density": [
            [
              36,
              0.18
            ],
            [
              40,
              0.42
            ],
            [
              44,
              0.72
            ],
            [
              48,
              0.95
            ],
            [
              52,
              1.0
            ],
            [
              56,
              0.78
            ],
            [
              60,
              0.45
            ],
            [
              64,
              0.22
            ],
            [
              68,
              0.08
            ]
          ]
        },
        {
          "label": "현재",
          "mean": 57.8,
          "meanLabel": "현재 mean 57.8",
          "ciLow": 55.9,
          "ciHigh": 59.7,
          "q1": 51.2,
          "median": 57.4,
          "q3": 63.8,
          "low": 42.0,
          "high": 74.5,
          "class": "cur-fill",
          "density": [
            [
              42,
              0.12
            ],
            [
              46,
              0.3
            ],
            [
              50,
              0.58
            ],
            [
              54,
              0.86
            ],
            [
              58,
              1.0
            ],
            [
              62,
              0.88
            ],
            [
              66,
              0.58
            ],
            [
              70,
              0.32
            ],
            [
              74,
              0.12
            ]
          ]
        }
      ],
      "chart.CHART-MEAN-001.ci": [
        {
          "label": "기준",
          "mean": 51.2,
          "low": 49.6,
          "high": 52.8,
          "valueLabel": "51.2 [49.6, 52.8]",
          "class": "ci-line-ref"
        },
        {
          "label": "현재",
          "mean": 57.8,
          "low": 55.9,
          "high": 59.7,
          "valueLabel": "57.8 [55.9, 59.7]",
          "class": "ci-line-cur"
        }
      ],
      "chart.CHART-MEAN-001.effect": [
        {
          "label": "Cohen's d",
          "score": 0.6,
          "rawValue": 0.72,
          "threshold": 0.4167,
          "valueLabel": "0.72",
          "class": "effect-bar"
        },
        {
          "label": "1 - p-value",
          "score": 0.996,
          "rawValue": 0.004,
          "threshold": 0.95,
          "valueLabel": "p=0.004",
          "class": "pvalue-bar"
        }
      ],
      "chart.CHART-MEAN-001.notes": [
        {
          "title": "해석",
          "text": "이 예시에서는 현재 구간 평균이 57.8로 기준 구간 51.2보다 6.6 높다. 95% 신뢰구간도 기준 49.6~52.8, 현재 55.9~59.7로 겹치지 않고, p-value 0.004와 Cohen's d 0.72가 함께 나타나 평균 상승 drift 후보로 볼 수 있다. 다만 분산 또는 tail 변화가 원인인지 여부는 별도 분포 chart로 보완한다.",
          "legend": [
            {
              "label": "기준 구간",
              "class": "swatch-reference"
            },
            {
              "label": "현재 구간",
              "class": "swatch-current-red"
            },
            {
              "label": "평균",
              "class": "swatch-mean"
            },
            {
              "label": "판단 기준",
              "class": "swatch-threshold"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-MV-001",
    "title": "CHART-MV-001 - 기준·현재 구간의 다변량 분포 분리",
    "originalPath": "./drift_report_charts/chart_mv_001.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_mv_001",
      "displayName": "CHART-MV-001 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 146px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "다변량 투영 산점도",
          "description": "현재 sample이 기준 sample보다 우상단으로 이동하며 중심 간 gap 1.35를 만든다.",
          "headerHeight": 76,
          "stageInset": {
            "top": 84,
            "right": 16,
            "bottom": -8,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "에너지 거리 추세",
          "description": "7번째 window부터 관리 기준 0.45를 넘고 마지막 값은 0.73이다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "순열 영분포",
          "description": "관측값 0.73이 null 분포의 오른쪽 꼬리 밖에 있으며 p-value는 0.012이다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "notes",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-MV-001.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-MV-001.summary"
        }
      },
      {
        "componentInstanceId": "CHART-MV-001.projection.0",
        "componentType": "projection_scatter",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "x",
          "y_field": "y",
          "group_field": "group",
          "x_min": -2.5,
          "x_max": 3.5,
          "y_min": -2.0,
          "y_max": 3.0,
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 28,
            "bottom": 62,
            "left": 58
          },
          "x_ticks": [
            -2,
            -1,
            0,
            1,
            2,
            3
          ],
          "y_ticks": [
            -2,
            -1,
            0,
            1,
            2,
            3
          ],
          "x_axis_label": "projection 1",
          "y_axis_label": "projection 2",
          "crosshair": false,
          "point_radius": 5,
          "group_class_map": {
            "reference": "ref-point",
            "current": "cur-point"
          },
          "ellipses": [
            {
              "x": -0.45,
              "y": -0.55,
              "rx": 185,
              "ry": 112,
              "rotate": 18,
              "class": "ref-ellipse"
            },
            {
              "x": 1.45,
              "y": 1.45,
              "rx": 172,
              "ry": 116,
              "rotate": 22,
              "class": "cur-ellipse"
            }
          ],
          "diagonal_markers": [
            {
              "x0": -0.45,
              "y0": -0.55,
              "x1": 1.45,
              "y1": 1.45,
              "class": "threshold-line"
            }
          ],
          "annotations": [
            {
              "text": "현재 sample이 우상단으로 분리",
              "x": 1.2,
              "y": 2.75,
              "class": "callout"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-MV-001.points"
        }
      },
      {
        "componentInstanceId": "CHART-MV-001.trend.0",
        "componentType": "trend_line",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "window",
          "y_field": "energy",
          "x_min": 1,
          "x_max": 10,
          "y_min": 0,
          "y_max": 0.85,
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 22,
            "bottom": 34,
            "left": 48
          },
          "x_ticks": [],
          "y_ticks": [
            0,
            0.25,
            0.5,
            0.75
          ],
          "x_axis_label": "window",
          "axis_label_x": 249,
          "axis_label_y": 177,
          "y_axis_label": false,
          "line_class": "energy-line",
          "primary_point_class": "energy-point",
          "show_points": true,
          "point_radius": 4,
          "horizontal_markers": [
            {
              "y": 0.45,
              "class": "threshold-line",
              "label": "관리 기준 0.45",
              "label_class": "warning",
              "label_x": 7.9,
              "label_dy": -6
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-MV-001.trend"
        }
      },
      {
        "componentInstanceId": "CHART-MV-001.null.0",
        "componentType": "histogram_view",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "distribution_style": "histogram_overlay",
          "x0_field": "x0",
          "x1_field": "x1",
          "primary_value_field": "value",
          "primary_class_field": "class",
          "x_min": 0.08,
          "x_max": 0.76,
          "y_min": 0,
          "y_max": 29,
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 8,
            "right": 26,
            "bottom": 34,
            "left": 48
          },
          "x_ticks": [
            0.1,
            0.2,
            0.3,
            0.4,
            0.5
          ],
          "x_tick_labels": [
            "0.10",
            "0.20",
            "0.30",
            "0.40",
            "0.50"
          ],
          "y_ticks": [],
          "x_axis_label": "permutation energy distance",
          "axis_label_x": 216,
          "axis_label_y": 179,
          "y_axis_label": false,
          "primary_bar_class": "null-bar",
          "primary_width_fraction": 0.82,
          "bin_gap": 2,
          "bar_radius": 3,
          "vertical_markers": [
            {
              "x": 0.73,
              "class": "observed-line",
              "label": "observed 0.73",
              "label_class": "warning",
              "label_y": 22,
              "label_anchor": "end"
            },
            {
              "x": 0.73,
              "class": "observed-line",
              "label": "p=0.012",
              "label_class": "warning",
              "label_y": 39,
              "label_anchor": "end"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-MV-001.null"
        }
      },
      {
        "componentInstanceId": "CHART-MV-001.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-MV-001.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-MV-001.summary": [
        {
          "label": "Energy distance",
          "value": 0.73,
          "displayValue": "0.73"
        },
        {
          "label": "Permutation p-value",
          "value": 0.012,
          "displayValue": "0.012"
        },
        {
          "label": "Projection gap",
          "value": 1.35,
          "displayValue": "1.35"
        }
      ],
      "chart.CHART-MV-001.points": [
        {
          "x": -1.9,
          "y": -1.1,
          "group": "reference"
        },
        {
          "x": -1.6,
          "y": -0.6,
          "group": "reference"
        },
        {
          "x": -1.4,
          "y": -1.5,
          "group": "reference"
        },
        {
          "x": -1.1,
          "y": -0.9,
          "group": "reference"
        },
        {
          "x": -0.9,
          "y": -0.2,
          "group": "reference"
        },
        {
          "x": -0.7,
          "y": -1.1,
          "group": "reference"
        },
        {
          "x": -0.5,
          "y": -0.5,
          "group": "reference"
        },
        {
          "x": -0.2,
          "y": -1.4,
          "group": "reference"
        },
        {
          "x": 0.0,
          "y": -0.7,
          "group": "reference"
        },
        {
          "x": 0.2,
          "y": -0.1,
          "group": "reference"
        },
        {
          "x": 0.4,
          "y": -0.9,
          "group": "reference"
        },
        {
          "x": 0.6,
          "y": -0.3,
          "group": "reference"
        },
        {
          "x": 0.8,
          "y": -1.2,
          "group": "reference"
        },
        {
          "x": 1.0,
          "y": -0.6,
          "group": "reference"
        },
        {
          "x": 1.2,
          "y": 0.0,
          "group": "reference"
        },
        {
          "x": -1.3,
          "y": 0.2,
          "group": "reference"
        },
        {
          "x": -0.8,
          "y": 0.5,
          "group": "reference"
        },
        {
          "x": -0.1,
          "y": 0.3,
          "group": "reference"
        },
        {
          "x": 0.5,
          "y": 0.6,
          "group": "reference"
        },
        {
          "x": 1.0,
          "y": 0.4,
          "group": "reference"
        },
        {
          "x": -0.5,
          "y": 0.1,
          "group": "current"
        },
        {
          "x": -0.2,
          "y": 0.6,
          "group": "current"
        },
        {
          "x": 0.1,
          "y": 1.0,
          "group": "current"
        },
        {
          "x": 0.3,
          "y": 0.4,
          "group": "current"
        },
        {
          "x": 0.6,
          "y": 1.4,
          "group": "current"
        },
        {
          "x": 0.8,
          "y": 0.8,
          "group": "current"
        },
        {
          "x": 1.0,
          "y": 1.7,
          "group": "current"
        },
        {
          "x": 1.2,
          "y": 0.9,
          "group": "current"
        },
        {
          "x": 1.5,
          "y": 1.4,
          "group": "current"
        },
        {
          "x": 1.7,
          "y": 0.6,
          "group": "current"
        },
        {
          "x": 1.9,
          "y": 1.8,
          "group": "current"
        },
        {
          "x": 2.1,
          "y": 1.1,
          "group": "current"
        },
        {
          "x": 2.4,
          "y": 1.6,
          "group": "current"
        },
        {
          "x": 2.6,
          "y": 0.9,
          "group": "current"
        },
        {
          "x": 2.9,
          "y": 1.9,
          "group": "current"
        },
        {
          "x": 0.7,
          "y": 2.2,
          "group": "current"
        },
        {
          "x": 1.4,
          "y": 2.4,
          "group": "current"
        },
        {
          "x": 2.2,
          "y": 2.5,
          "group": "current"
        },
        {
          "x": 2.7,
          "y": 2.7,
          "group": "current"
        },
        {
          "x": 3.1,
          "y": 2.3,
          "group": "current"
        }
      ],
      "chart.CHART-MV-001.trend": [
        {
          "window": 1,
          "energy": 0.18
        },
        {
          "window": 2,
          "energy": 0.21
        },
        {
          "window": 3,
          "energy": 0.25
        },
        {
          "window": 4,
          "energy": 0.24
        },
        {
          "window": 5,
          "energy": 0.31
        },
        {
          "window": 6,
          "energy": 0.38
        },
        {
          "window": 7,
          "energy": 0.47
        },
        {
          "window": 8,
          "energy": 0.56
        },
        {
          "window": 9,
          "energy": 0.64
        },
        {
          "window": 10,
          "energy": 0.73
        }
      ],
      "chart.CHART-MV-001.null": [
        {
          "label": "0.10",
          "x0": 0.08,
          "x1": 0.14,
          "value": 4,
          "class": "null-bar"
        },
        {
          "label": "0.15",
          "x0": 0.14,
          "x1": 0.2,
          "value": 9,
          "class": "null-bar"
        },
        {
          "label": "0.20",
          "x0": 0.2,
          "x1": 0.26,
          "value": 17,
          "class": "null-bar"
        },
        {
          "label": "0.25",
          "x0": 0.26,
          "x1": 0.32,
          "value": 24,
          "class": "null-bar"
        },
        {
          "label": "0.30",
          "x0": 0.32,
          "x1": 0.38,
          "value": 22,
          "class": "null-bar"
        },
        {
          "label": "0.35",
          "x0": 0.38,
          "x1": 0.44,
          "value": 15,
          "class": "null-bar"
        },
        {
          "label": "0.40",
          "x0": 0.44,
          "x1": 0.5,
          "value": 8,
          "class": "null-bar"
        },
        {
          "label": "0.45",
          "x0": 0.5,
          "x1": 0.56,
          "value": 4,
          "class": "tail-bar"
        },
        {
          "label": "0.50",
          "x0": 0.56,
          "x1": 0.62,
          "value": 2,
          "class": "tail-bar"
        },
        {
          "label": "0.55",
          "x0": 0.62,
          "x1": 0.68,
          "value": 1,
          "class": "tail-bar"
        }
      ],
      "chart.CHART-MV-001.notes": [
        {
          "title": "해석",
          "text": "이 예시에서는 Energy distance가 0.73으로 관리 기준 0.45를 넘고, permutation p-value가 0.012로 작다. Projection scatter에서도 현재 구간 sample이 우상단으로 이동해 기준 구간과 분리되므로, 여러 feature의 결합 분포가 함께 달라진 다변량 drift 후보로 읽는다.",
          "legend": [
            {
              "label": "기준 구간",
              "class": "swatch-reference"
            },
            {
              "label": "현재 구간",
              "class": "swatch-current-red"
            },
            {
              "label": "Energy distance",
              "class": "swatch-energy"
            },
            {
              "label": "판단 기준",
              "class": "swatch-threshold"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-MV-002",
    "title": "커널 MMD로 본 임베딩 분포 변화",
    "originalPath": "./drift_report_charts/chart_mv_002.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_mv_002",
      "displayName": "CHART-MV-002 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 112px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "임베딩 투영 산점도",
          "description": "기준 중심 (-0.4, 0.25)에서 현재 중심 (1.55, 1.75)로 이동한 방향을 읽는다.",
          "headerHeight": 58,
          "stageInset": {
            "top": 66,
            "right": 16,
            "bottom": 12,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "MMD 점수 추세",
          "description": "7번째 window부터 관리 기준 0.18을 넘고 마지막 값은 0.36까지 증가한다.",
          "headerHeight": 56,
          "stageInset": {
            "top": 58,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "순열 영분포",
          "description": "귀무분포는 0.08~0.12 부근에 많고 관측 MMD 0.36은 오른쪽 밖에 있다.",
          "headerHeight": 56,
          "stageInset": {
            "top": 58,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "interpretation",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-MV-002.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "display_value_field": "displayValue",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-MV-002.summary"
        }
      },
      {
        "componentInstanceId": "CHART-MV-002.embedding.0",
        "componentType": "projection_scatter",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "x",
          "y_field": "y",
          "group_field": "group",
          "x_min": -2.5,
          "x_max": 3.5,
          "y_min": -1.2,
          "y_max": 3.2,
          "x_ticks": [
            -2,
            -1,
            0,
            1,
            2,
            3
          ],
          "y_ticks": [
            -1,
            0,
            1,
            2,
            3
          ],
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 28,
            "bottom": 62,
            "left": 58
          },
          "crosshair": false,
          "point_radius": 5,
          "group_class_map": {
            "reference": "ref-point",
            "current": "cur-point"
          },
          "ellipses": [
            {
              "class": "ref-kernel",
              "x": -0.4,
              "y": 0.25,
              "rx": 185,
              "ry": 102,
              "rotate": 12
            },
            {
              "class": "cur-kernel",
              "x": 1.55,
              "y": 1.75,
              "rx": 178,
              "ry": 114,
              "rotate": 18
            }
          ],
          "diagonal_markers": [
            {
              "class": "threshold-line",
              "x0": -0.4,
              "y0": 0.25,
              "x1": 1.55,
              "y1": 1.75
            }
          ],
          "annotations": [
            {
              "class": "callout",
              "x": 1.0,
              "y": 3.0,
              "text": "kernel mean embedding 차이 확대"
            }
          ],
          "x_axis_label": "embedding 1",
          "y_axis_label": "embedding 2",
          "axis_label_y": 428
        },
        "dataBinding": {
          "source": "chart.CHART-MV-002.embedding"
        }
      },
      {
        "componentInstanceId": "CHART-MV-002.mmd.0",
        "componentType": "distance_metric_view",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "time_field": "window",
          "value_field": "mmd",
          "x_min": 1,
          "x_max": 10,
          "y_min": 0,
          "y_max": 0.42,
          "y_ticks": [
            0,
            0.1,
            0.2,
            0.3,
            0.4
          ],
          "x_ticks": [],
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 22,
            "bottom": 34,
            "left": 48
          },
          "line_class": "mmd-line",
          "primary_point_class": "mmd-point",
          "point_radius": 4,
          "x_axis_label": "window",
          "y_axis_label": false,
          "horizontal_markers": [
            {
              "class": "threshold-line",
              "y": 0.18,
              "label": "관리 기준 0.18",
              "label_x": 7.6,
              "label_dy": -6,
              "label_class": "warning-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-MV-002.mmd"
        }
      },
      {
        "componentInstanceId": "CHART-MV-002.null.0",
        "componentType": "histogram_view",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "distribution_style": "histogram_overlay",
          "x0_field": "x0",
          "x1_field": "x1",
          "primary_value_field": "count",
          "x_min": 0.02,
          "x_max": 0.38,
          "y_min": 0,
          "y_max": 34,
          "x_ticks": [
            0.02,
            0.06,
            0.1,
            0.14,
            0.18
          ],
          "y_ticks": [],
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 8,
            "right": 26,
            "bottom": 34,
            "left": 48
          },
          "primary_bar_class": "null-bar",
          "primary_class_field": "class",
          "primary_width_fraction": 0.82,
          "bin_gap": 4,
          "bar_radius": 3,
          "x_axis_label": "permutation MMD score",
          "y_axis_label": false,
          "vertical_markers": [
            {
              "class": "observed-line",
              "x": 0.36,
              "label": "observed 0.36",
              "label_y": 22,
              "label_dx": -4,
              "label_class": "warning-text"
            },
            {
              "class": "observed-line",
              "x": 0.36,
              "label": "p=0.008",
              "label_y": 39,
              "label_dx": -4,
              "label_class": "warning-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-MV-002.null"
        }
      },
      {
        "componentInstanceId": "CHART-MV-002.notes.0",
        "componentType": "decision_card",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-MV-002.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-MV-002.summary": [
        {
          "label": "MMD score",
          "value": 0.36,
          "displayValue": "0.36"
        },
        {
          "label": "Permutation p-value",
          "value": 0.008,
          "displayValue": "0.008"
        },
        {
          "label": "Kernel bandwidth",
          "value": 1.2,
          "displayValue": "1.20"
        }
      ],
      "chart.CHART-MV-002.embedding": [
        {
          "x": -2.1,
          "y": -0.5,
          "group": "reference"
        },
        {
          "x": -1.8,
          "y": -0.1,
          "group": "reference"
        },
        {
          "x": -1.5,
          "y": -0.8,
          "group": "reference"
        },
        {
          "x": -1.2,
          "y": 0.2,
          "group": "reference"
        },
        {
          "x": -1.0,
          "y": -0.4,
          "group": "reference"
        },
        {
          "x": -0.7,
          "y": 0.4,
          "group": "reference"
        },
        {
          "x": -0.5,
          "y": -0.2,
          "group": "reference"
        },
        {
          "x": -0.2,
          "y": 0.1,
          "group": "reference"
        },
        {
          "x": 0.0,
          "y": -0.5,
          "group": "reference"
        },
        {
          "x": 0.2,
          "y": 0.4,
          "group": "reference"
        },
        {
          "x": 0.5,
          "y": -0.1,
          "group": "reference"
        },
        {
          "x": 0.7,
          "y": 0.5,
          "group": "reference"
        },
        {
          "x": 0.9,
          "y": -0.4,
          "group": "reference"
        },
        {
          "x": 1.0,
          "y": 0.2,
          "group": "reference"
        },
        {
          "x": 1.2,
          "y": 0.7,
          "group": "reference"
        },
        {
          "x": -1.4,
          "y": 0.9,
          "group": "reference"
        },
        {
          "x": -0.9,
          "y": 1.1,
          "group": "reference"
        },
        {
          "x": -0.1,
          "y": 1.0,
          "group": "reference"
        },
        {
          "x": 0.6,
          "y": 1.2,
          "group": "reference"
        },
        {
          "x": 1.2,
          "y": 1.3,
          "group": "reference"
        },
        {
          "x": -0.8,
          "y": 0.1,
          "group": "current"
        },
        {
          "x": -0.5,
          "y": 0.8,
          "group": "current"
        },
        {
          "x": -0.2,
          "y": 1.3,
          "group": "current"
        },
        {
          "x": 0.1,
          "y": 0.5,
          "group": "current"
        },
        {
          "x": 0.4,
          "y": 1.7,
          "group": "current"
        },
        {
          "x": 0.8,
          "y": 0.9,
          "group": "current"
        },
        {
          "x": 1.0,
          "y": 1.8,
          "group": "current"
        },
        {
          "x": 1.4,
          "y": 1.1,
          "group": "current"
        },
        {
          "x": 1.8,
          "y": 1.7,
          "group": "current"
        },
        {
          "x": 2.1,
          "y": 0.8,
          "group": "current"
        },
        {
          "x": 2.3,
          "y": 1.9,
          "group": "current"
        },
        {
          "x": 2.6,
          "y": 1.2,
          "group": "current"
        },
        {
          "x": 2.8,
          "y": 2.1,
          "group": "current"
        },
        {
          "x": 3.0,
          "y": 1.4,
          "group": "current"
        },
        {
          "x": 3.2,
          "y": 2.3,
          "group": "current"
        },
        {
          "x": 0.5,
          "y": 2.4,
          "group": "current"
        },
        {
          "x": 1.1,
          "y": 2.7,
          "group": "current"
        },
        {
          "x": 1.9,
          "y": 2.8,
          "group": "current"
        },
        {
          "x": 2.6,
          "y": 2.9,
          "group": "current"
        },
        {
          "x": 3.1,
          "y": 2.8,
          "group": "current"
        }
      ],
      "chart.CHART-MV-002.mmd": [
        {
          "window": 1,
          "mmd": 0.05
        },
        {
          "window": 2,
          "mmd": 0.06
        },
        {
          "window": 3,
          "mmd": 0.07
        },
        {
          "window": 4,
          "mmd": 0.08
        },
        {
          "window": 5,
          "mmd": 0.1
        },
        {
          "window": 6,
          "mmd": 0.14
        },
        {
          "window": 7,
          "mmd": 0.19
        },
        {
          "window": 8,
          "mmd": 0.25
        },
        {
          "window": 9,
          "mmd": 0.31
        },
        {
          "window": 10,
          "mmd": 0.36
        }
      ],
      "chart.CHART-MV-002.null": [
        {
          "x0": 0.02,
          "x1": 0.04,
          "count": 5,
          "class": "null-bar"
        },
        {
          "x0": 0.04,
          "x1": 0.06,
          "count": 12,
          "class": "null-bar"
        },
        {
          "x0": 0.06,
          "x1": 0.08,
          "count": 22,
          "class": "null-bar"
        },
        {
          "x0": 0.08,
          "x1": 0.1,
          "count": 28,
          "class": "null-bar"
        },
        {
          "x0": 0.1,
          "x1": 0.12,
          "count": 24,
          "class": "null-bar"
        },
        {
          "x0": 0.12,
          "x1": 0.14,
          "count": 16,
          "class": "null-bar"
        },
        {
          "x0": 0.14,
          "x1": 0.16,
          "count": 9,
          "class": "null-bar"
        },
        {
          "x0": 0.16,
          "x1": 0.18,
          "count": 5,
          "class": "tail-bar"
        },
        {
          "x0": 0.18,
          "x1": 0.2,
          "count": 2,
          "class": "tail-bar"
        },
        {
          "x0": 0.2,
          "x1": 0.22,
          "count": 1,
          "class": "tail-bar"
        }
      ],
      "chart.CHART-MV-002.notes": [
        {
          "title": "해석",
          "text": "이 예시에서는 MMD score가 0.36이고 permutation p-value가 0.008이다. window 추세는 관리 기준 0.18을 넘은 뒤 계속 커지고, embedding projection에서는 현재 구간이 우상향으로 이동한다. kernel bandwidth 1.20 설정에서 기준·현재 임베딩 분포가 달라진 고차원 drift 후보로 해석한다.",
          "legend": [
            {
              "label": "기준 구간",
              "class": "swatch-reference"
            },
            {
              "label": "현재 구간",
              "class": "swatch-current-red"
            },
            {
              "label": "MMD score",
              "class": "swatch-mmd"
            },
            {
              "label": "판단 기준",
              "class": "swatch-threshold"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-MV-003",
    "title": "밀도 차이로 본 신규 구간 유입과 기존 구간 감소",
    "originalPath": "./drift_report_charts/chart_mv_003.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_mv_003",
      "displayName": "CHART-MV-003 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 112px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "밀도 차이 히트맵",
          "description": "우상향은 현재 밀도 증가, 좌하향은 현재 밀도 감소 영역이다.",
          "headerHeight": 58,
          "stageInset": {
            "top": 66,
            "right": 16,
            "bottom": 12,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "LSDD 점수 추세",
          "description": "7번째 window부터 관리 기준 0.17을 넘는다.",
          "headerHeight": 56,
          "stageInset": {
            "top": 58,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "순열 영분포",
          "description": "관측값 0.34가 귀무분포의 오른쪽 꼬리 밖에 있다.",
          "headerHeight": 56,
          "stageInset": {
            "top": 58,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "interpretation",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-MV-003.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "display_value_field": "displayValue",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-MV-003.summary"
        }
      },
      {
        "componentInstanceId": "CHART-MV-003.heatmap.0",
        "componentType": "matrix_view",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "matrix_style": "heatmap_grid",
          "x_values": [
            -2,
            -1,
            0,
            1,
            2,
            3
          ],
          "y_values": [
            3,
            2,
            1,
            0,
            -1
          ],
          "values_field": "values",
          "x_ticks": [
            -2,
            -1,
            0,
            1,
            2,
            3
          ],
          "y_ticks": [
            -1,
            0,
            1,
            2,
            3
          ],
          "x_min": -2,
          "x_max": 3,
          "y_min": -1,
          "y_max": 3,
          "value_min": -0.5,
          "value_max": 0.5,
          "palette": [
            [
              0,
              "#2f6f9f"
            ],
            [
              0.5,
              "#f4f6f7"
            ],
            [
              1,
              "#b95a50"
            ]
          ],
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 34,
            "bottom": 62,
            "left": 58
          },
          "x_axis_label": "embedding 1",
          "y_axis_label": "embedding 2",
          "axis_label_y": 428,
          "ellipses": [
            {
              "class": "contour-decrease",
              "x": -1.1,
              "y": 0.0,
              "rx": 130,
              "ry": 84,
              "rotate": -12
            },
            {
              "class": "contour-increase",
              "x": 1.9,
              "y": 2.1,
              "rx": 142,
              "ry": 92,
              "rotate": 18
            }
          ],
          "annotations": [
            {
              "class": "warning-text",
              "x": 1.45,
              "y": 2.95,
              "text": "현재 밀도 증가 영역"
            },
            {
              "class": "callout",
              "x": -1.95,
              "y": 1.25,
              "text": "현재 밀도 감소 영역"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-MV-003.heatmap"
        }
      },
      {
        "componentInstanceId": "CHART-MV-003.lsdd.0",
        "componentType": "distance_metric_view",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "time_field": "window",
          "value_field": "lsdd",
          "x_min": 1,
          "x_max": 10,
          "y_min": 0,
          "y_max": 0.4,
          "y_ticks": [
            0,
            0.1,
            0.2,
            0.3,
            0.4
          ],
          "x_ticks": [],
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 22,
            "bottom": 34,
            "left": 48
          },
          "line_class": "lsdd-line",
          "primary_point_class": "lsdd-point",
          "point_radius": 4,
          "x_axis_label": "window",
          "y_axis_label": false,
          "horizontal_markers": [
            {
              "class": "threshold-line",
              "y": 0.17,
              "label": "관리 기준 0.17",
              "label_x": 7.6,
              "label_dy": -6,
              "label_class": "warning-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-MV-003.lsdd"
        }
      },
      {
        "componentInstanceId": "CHART-MV-003.null.0",
        "componentType": "histogram_view",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "distribution_style": "histogram_overlay",
          "x0_field": "x0",
          "x1_field": "x1",
          "primary_value_field": "count",
          "x_min": 0.03,
          "x_max": 0.36,
          "y_min": 0,
          "y_max": 36,
          "x_ticks": [
            0.03,
            0.07,
            0.11,
            0.15,
            0.19
          ],
          "y_ticks": [],
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 8,
            "right": 26,
            "bottom": 34,
            "left": 48
          },
          "primary_bar_class": "null-bar",
          "primary_class_field": "class",
          "primary_width_fraction": 0.82,
          "bin_gap": 4,
          "bar_radius": 3,
          "x_axis_label": "permutation LSDD score",
          "y_axis_label": false,
          "vertical_markers": [
            {
              "class": "observed-line",
              "x": 0.34,
              "label": "observed 0.34",
              "label_y": 22,
              "label_dx": -4,
              "label_class": "warning-text"
            },
            {
              "class": "observed-line",
              "x": 0.34,
              "label": "p=0.010",
              "label_y": 39,
              "label_dx": -4,
              "label_class": "warning-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-MV-003.null"
        }
      },
      {
        "componentInstanceId": "CHART-MV-003.notes.0",
        "componentType": "decision_card",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-MV-003.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-MV-003.summary": [
        {
          "label": "LSDD score",
          "value": 0.34,
          "displayValue": "0.34"
        },
        {
          "label": "Permutation p-value",
          "value": 0.01,
          "displayValue": "0.010"
        },
        {
          "label": "최대 밀도 delta",
          "value": 0.48,
          "displayValue": "+0.48"
        }
      ],
      "chart.CHART-MV-003.heatmap": [
        {
          "row": 3,
          "values": [
            0.04,
            0.08,
            0.18,
            0.28,
            0.4,
            0.3
          ]
        },
        {
          "row": 2,
          "values": [
            0.02,
            0.04,
            0.15,
            0.32,
            0.48,
            0.36
          ]
        },
        {
          "row": 1,
          "values": [
            -0.12,
            -0.16,
            -0.04,
            0.18,
            0.34,
            0.22
          ]
        },
        {
          "row": 0,
          "values": [
            -0.24,
            -0.3,
            -0.18,
            0.05,
            0.15,
            0.1
          ]
        },
        {
          "row": -1,
          "values": [
            -0.18,
            -0.22,
            -0.12,
            0.02,
            0.08,
            0.05
          ]
        }
      ],
      "chart.CHART-MV-003.lsdd": [
        {
          "window": 1,
          "lsdd": 0.04
        },
        {
          "window": 2,
          "lsdd": 0.05
        },
        {
          "window": 3,
          "lsdd": 0.06
        },
        {
          "window": 4,
          "lsdd": 0.07
        },
        {
          "window": 5,
          "lsdd": 0.09
        },
        {
          "window": 6,
          "lsdd": 0.13
        },
        {
          "window": 7,
          "lsdd": 0.18
        },
        {
          "window": 8,
          "lsdd": 0.24
        },
        {
          "window": 9,
          "lsdd": 0.3
        },
        {
          "window": 10,
          "lsdd": 0.34
        }
      ],
      "chart.CHART-MV-003.null": [
        {
          "x0": 0.03,
          "x1": 0.05,
          "count": 6,
          "class": "null-bar"
        },
        {
          "x0": 0.05,
          "x1": 0.07,
          "count": 14,
          "class": "null-bar"
        },
        {
          "x0": 0.07,
          "x1": 0.09,
          "count": 25,
          "class": "null-bar"
        },
        {
          "x0": 0.09,
          "x1": 0.11,
          "count": 30,
          "class": "null-bar"
        },
        {
          "x0": 0.11,
          "x1": 0.13,
          "count": 22,
          "class": "null-bar"
        },
        {
          "x0": 0.13,
          "x1": 0.15,
          "count": 13,
          "class": "null-bar"
        },
        {
          "x0": 0.15,
          "x1": 0.17,
          "count": 7,
          "class": "null-bar"
        },
        {
          "x0": 0.17,
          "x1": 0.19,
          "count": 3,
          "class": "tail-bar"
        },
        {
          "x0": 0.19,
          "x1": 0.21,
          "count": 1,
          "class": "tail-bar"
        },
        {
          "x0": 0.21,
          "x1": 0.23,
          "count": 1,
          "class": "tail-bar"
        }
      ],
      "chart.CHART-MV-003.notes": [
        {
          "title": "해석",
          "text": "이 예시에서는 LSDD score가 0.34로 관리 기준 0.17을 넘고, permutation p-value는 0.010이다. heatmap의 우상향 embedding 영역은 현재 밀도가 최대 +0.48까지 증가하고, 좌하향 기준 영역은 -0.30까지 감소한다. 신규 또는 증가 segment 유입과 기존 population 감소가 함께 나타난 밀도 차이 drift 후보로 읽는다.",
          "legend": [
            {
              "label": "현재 밀도 증가",
              "class": "swatch-increase"
            },
            {
              "label": "현재 밀도 감소",
              "class": "swatch-decrease"
            },
            {
              "label": "LSDD score",
              "class": "swatch-lsdd"
            },
            {
              "label": "판단 기준",
              "class": "swatch-threshold"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-MV-004",
    "title": "다변량 평균 벡터의 기준 범위 이탈",
    "originalPath": "./drift_report_charts/chart_mv_004.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_mv_004",
      "displayName": "CHART-MV-004 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 112px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "기준·현재 평균 위치",
          "description": "기준 평균 중심 (-0.2, -0.1)에서 현재 평균 중심 (1.9, 1.8)로 이동한 방향을 읽는다.",
          "headerHeight": 58,
          "stageInset": {
            "top": 66,
            "right": 16,
            "bottom": 12,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "T2 관리도",
          "description": "8번째 window부터 UCL 14.0을 넘고 마지막 값은 25.7이다.",
          "headerHeight": 56,
          "stageInset": {
            "top": 58,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "특성별 기여도",
          "description": "소득 36%, 거래금액 28%가 평균 이동 기여의 상위 항목이다.",
          "headerHeight": 56,
          "stageInset": {
            "top": 58,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "interpretation",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-MV-004.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "display_value_field": "displayValue",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-MV-004.summary"
        }
      },
      {
        "componentInstanceId": "CHART-MV-004.pca.0",
        "componentType": "projection_scatter",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "x",
          "y_field": "y",
          "group_field": "group",
          "x_min": -2.5,
          "x_max": 3.5,
          "y_min": -1.6,
          "y_max": 3.1,
          "x_ticks": [
            -2,
            -1,
            0,
            1,
            2,
            3
          ],
          "y_ticks": [
            -1,
            0,
            1,
            2,
            3
          ],
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 28,
            "bottom": 62,
            "left": 58
          },
          "crosshair": false,
          "point_radius": 5,
          "group_class_map": {
            "reference": "ref-point",
            "current": "cur-point",
            "mean_ref": "mean-point-ref",
            "mean_cur": "mean-point-cur"
          },
          "group_radius_map": {
            "mean_ref": 7,
            "mean_cur": 7
          },
          "ellipses": [
            {
              "class": "ref-ellipse",
              "x": -0.2,
              "y": -0.1,
              "rx": 198,
              "ry": 116,
              "rotate": 18
            }
          ],
          "diagonal_markers": [
            {
              "class": "mean-shift-line",
              "x0": -0.2,
              "y0": -0.1,
              "x1": 1.9,
              "y1": 1.8
            }
          ],
          "annotations": [
            {
              "class": "warning-text",
              "x": 1.1,
              "y": 2.85,
              "text": "현재 평균 중심이 기준 범위 밖으로 이동"
            }
          ],
          "x_axis_label": "PC1",
          "y_axis_label": "PC2",
          "axis_label_y": 428
        },
        "dataBinding": {
          "source": "chart.CHART-MV-004.pca"
        }
      },
      {
        "componentInstanceId": "CHART-MV-004.t2.0",
        "componentType": "control_chart",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "time_field": "window",
          "value_field": "t2",
          "x_min": 1,
          "x_max": 10,
          "y_min": 0,
          "y_max": 30,
          "y_ticks": [
            0,
            10,
            20,
            30
          ],
          "x_ticks": [],
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 22,
            "bottom": 34,
            "left": 48
          },
          "line_class": "t2-line",
          "primary_point_class": "t2-point",
          "point_radius": 4,
          "x_axis_label": "window",
          "y_axis_label": false,
          "horizontal_markers": [
            {
              "class": "threshold-line",
              "y": 14.0,
              "label": "UCL 14.0",
              "label_x": 8.0,
              "label_dy": -6,
              "label_class": "warning-text"
            }
          ],
          "point_highlights": [
            {
              "x": 8,
              "class": "alert-point",
              "r": 4.8
            },
            {
              "x": 9,
              "class": "alert-point",
              "r": 4.8
            },
            {
              "x": 10,
              "class": "alert-point",
              "r": 4.8
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-MV-004.t2"
        }
      },
      {
        "componentInstanceId": "CHART-MV-004.contrib.0",
        "componentType": "contribution_view",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "horizontal_ranked",
          "category_field": "label",
          "value_field": "value",
          "value_label_field": "displayValue",
          "preserve_order": true,
          "limit": 5,
          "x_max": 42.5,
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 8,
            "right": 32,
            "bottom": 30,
            "left": 86
          },
          "row_gap": 27,
          "first_y": 10,
          "bar_height": 18,
          "bar_class": "contrib-bar",
          "highlight_class": "top-contrib-bar",
          "caption": "T2 contribution"
        },
        "dataBinding": {
          "source": "chart.CHART-MV-004.contrib"
        }
      },
      {
        "componentInstanceId": "CHART-MV-004.notes.0",
        "componentType": "decision_card",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-MV-004.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-MV-004.summary": [
        {
          "label": "Hotelling T2",
          "value": 25.7,
          "displayValue": "25.7"
        },
        {
          "label": "p-value",
          "value": 0.004,
          "displayValue": "0.004"
        },
        {
          "label": "평균 shift",
          "value": 1.62,
          "displayValue": "1.62"
        }
      ],
      "chart.CHART-MV-004.pca": [
        {
          "x": -1.9,
          "y": -0.9,
          "group": "reference"
        },
        {
          "x": -1.6,
          "y": -0.3,
          "group": "reference"
        },
        {
          "x": -1.4,
          "y": -1.2,
          "group": "reference"
        },
        {
          "x": -1.1,
          "y": -0.7,
          "group": "reference"
        },
        {
          "x": -0.9,
          "y": 0.0,
          "group": "reference"
        },
        {
          "x": -0.6,
          "y": -0.8,
          "group": "reference"
        },
        {
          "x": -0.4,
          "y": -0.2,
          "group": "reference"
        },
        {
          "x": -0.1,
          "y": -1.0,
          "group": "reference"
        },
        {
          "x": 0.1,
          "y": -0.5,
          "group": "reference"
        },
        {
          "x": 0.3,
          "y": 0.2,
          "group": "reference"
        },
        {
          "x": 0.5,
          "y": -0.6,
          "group": "reference"
        },
        {
          "x": 0.7,
          "y": 0.0,
          "group": "reference"
        },
        {
          "x": 0.9,
          "y": -0.8,
          "group": "reference"
        },
        {
          "x": 1.1,
          "y": -0.2,
          "group": "reference"
        },
        {
          "x": 1.3,
          "y": 0.4,
          "group": "reference"
        },
        {
          "x": -1.2,
          "y": 0.5,
          "group": "reference"
        },
        {
          "x": -0.7,
          "y": 0.8,
          "group": "reference"
        },
        {
          "x": 0.0,
          "y": 0.7,
          "group": "reference"
        },
        {
          "x": 0.7,
          "y": 1.0,
          "group": "reference"
        },
        {
          "x": 1.2,
          "y": 0.8,
          "group": "reference"
        },
        {
          "x": 0.2,
          "y": 0.4,
          "group": "current"
        },
        {
          "x": 0.5,
          "y": 1.0,
          "group": "current"
        },
        {
          "x": 0.8,
          "y": 1.5,
          "group": "current"
        },
        {
          "x": 1.0,
          "y": 0.8,
          "group": "current"
        },
        {
          "x": 1.3,
          "y": 1.8,
          "group": "current"
        },
        {
          "x": 1.5,
          "y": 1.1,
          "group": "current"
        },
        {
          "x": 1.8,
          "y": 2.0,
          "group": "current"
        },
        {
          "x": 2.0,
          "y": 1.4,
          "group": "current"
        },
        {
          "x": 2.3,
          "y": 2.1,
          "group": "current"
        },
        {
          "x": 2.5,
          "y": 1.3,
          "group": "current"
        },
        {
          "x": 2.7,
          "y": 2.4,
          "group": "current"
        },
        {
          "x": 3.0,
          "y": 1.7,
          "group": "current"
        },
        {
          "x": 3.2,
          "y": 2.5,
          "group": "current"
        },
        {
          "x": 2.1,
          "y": 2.8,
          "group": "current"
        },
        {
          "x": 1.4,
          "y": 2.5,
          "group": "current"
        },
        {
          "x": -0.2,
          "y": -0.1,
          "group": "mean_ref"
        },
        {
          "x": 1.9,
          "y": 1.8,
          "group": "mean_cur"
        }
      ],
      "chart.CHART-MV-004.t2": [
        {
          "window": 1,
          "t2": 4.2
        },
        {
          "window": 2,
          "t2": 5.1
        },
        {
          "window": 3,
          "t2": 6.0
        },
        {
          "window": 4,
          "t2": 5.8
        },
        {
          "window": 5,
          "t2": 7.4
        },
        {
          "window": 6,
          "t2": 9.2
        },
        {
          "window": 7,
          "t2": 12.5
        },
        {
          "window": 8,
          "t2": 16.8
        },
        {
          "window": 9,
          "t2": 21.4
        },
        {
          "window": 10,
          "t2": 25.7
        }
      ],
      "chart.CHART-MV-004.contrib": [
        {
          "label": "소득",
          "value": 36,
          "displayValue": "36%",
          "class": "top-contrib-bar"
        },
        {
          "label": "거래금액",
          "value": 28,
          "displayValue": "28%",
          "class": "contrib-bar"
        },
        {
          "label": "이용빈도",
          "value": 18,
          "displayValue": "18%",
          "class": "contrib-bar"
        },
        {
          "label": "연체일수",
          "value": 11,
          "displayValue": "11%",
          "class": "contrib-bar"
        },
        {
          "label": "나이",
          "value": 7,
          "displayValue": "7%",
          "class": "contrib-bar"
        }
      ],
      "chart.CHART-MV-004.notes": [
        {
          "title": "해석",
          "text": "이 예시에서는 Hotelling T2가 25.7로 UCL 14.0을 초과하고 p-value는 0.004이다. PCA 화면에서는 현재 평균 중심이 기준 정상 변동 범위 밖의 우상향으로 이동하며, 소득 36%와 거래금액 28%가 평균 벡터 이동을 가장 크게 설명한다.",
          "legend": [
            {
              "label": "기준 구간",
              "class": "swatch-reference"
            },
            {
              "label": "현재 구간",
              "class": "swatch-current-red"
            },
            {
              "label": "T2 statistic",
              "class": "swatch-t2"
            },
            {
              "label": "UCL",
              "class": "swatch-threshold"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-MV-005",
    "title": "기준 공분산 범위 밖 고거리 샘플 집중",
    "originalPath": "./drift_report_charts/chart_mv_005.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_mv_005",
      "displayName": "CHART-MV-005 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 112px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "거리별 차원축소 산점도",
          "description": "threshold 4.5를 넘는 고거리 sample이 우상향에 집중되는지 읽는다.",
          "headerHeight": 58,
          "stageInset": {
            "top": 66,
            "right": 16,
            "bottom": 12,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "거리 추세",
          "description": "8번째 window부터 threshold를 넘고 6.1까지 상승한다.",
          "headerHeight": 56,
          "stageInset": {
            "top": 58,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "거리 분포",
          "description": "sample의 22%가 threshold 오른쪽 tail에 쌓인다.",
          "headerHeight": 56,
          "stageInset": {
            "top": 58,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "interpretation",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-MV-005.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "display_value_field": "displayValue",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-MV-005.summary"
        }
      },
      {
        "componentInstanceId": "CHART-MV-005.pca.0",
        "componentType": "projection_scatter",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "x",
          "y_field": "y",
          "group_field": "group",
          "x_min": -2.3,
          "x_max": 3.4,
          "y_min": -1.2,
          "y_max": 3.0,
          "x_ticks": [
            -2,
            -1,
            0,
            1,
            2,
            3
          ],
          "y_ticks": [
            -1,
            0,
            1,
            2,
            3
          ],
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 28,
            "bottom": 62,
            "left": 58
          },
          "crosshair": false,
          "group_class_map": {
            "low": "distance-point",
            "high": "alert-point"
          },
          "ellipses": [
            {
              "class": "normal-ellipse",
              "x": 0,
              "y": 0,
              "rx": 205,
              "ry": 120,
              "rotate": 18
            }
          ],
          "diagonal_markers": [
            {
              "class": "threshold-line",
              "x0": 0,
              "y0": 0,
              "x1": 2.55,
              "y1": 2.0
            }
          ],
          "annotations": [
            {
              "class": "warning-text",
              "x": 1.45,
              "y": 2.75,
              "text": "threshold 초과 sample이 우상향에 집중"
            }
          ],
          "x_axis_label": "PC1",
          "y_axis_label": "PC2",
          "axis_label_y": 428
        },
        "dataBinding": {
          "source": "chart.CHART-MV-005.pca"
        }
      },
      {
        "componentInstanceId": "CHART-MV-005.distance.0",
        "componentType": "distance_metric_view",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "time_field": "window",
          "value_field": "distance",
          "x_min": 1,
          "x_max": 10,
          "y_min": 0,
          "y_max": 7,
          "y_ticks": [
            0,
            2,
            4,
            6
          ],
          "x_ticks": [],
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 22,
            "bottom": 34,
            "left": 48
          },
          "line_class": "distance-line",
          "primary_point_class": "distance-point",
          "point_radius": 4,
          "x_axis_label": "window",
          "y_axis_label": false,
          "horizontal_markers": [
            {
              "class": "threshold-line",
              "y": 4.5,
              "label": "threshold 4.5",
              "label_x": 7.4,
              "label_dy": -6,
              "label_class": "warning-text"
            }
          ],
          "point_highlights": [
            {
              "x": 8,
              "class": "alert-point",
              "r": 4.8
            },
            {
              "x": 9,
              "class": "alert-point",
              "r": 4.8
            },
            {
              "x": 10,
              "class": "alert-point",
              "r": 4.8
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-MV-005.distance"
        }
      },
      {
        "componentInstanceId": "CHART-MV-005.hist.0",
        "componentType": "histogram_view",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "distribution_style": "histogram_overlay",
          "x0_field": "x0",
          "x1_field": "x1",
          "primary_value_field": "count",
          "x_min": 0.5,
          "x_max": 7.5,
          "y_min": 0,
          "y_max": 14,
          "x_ticks": [
            1,
            2,
            3,
            4,
            5,
            6,
            7
          ],
          "y_ticks": [],
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 8,
            "right": 26,
            "bottom": 34,
            "left": 48
          },
          "primary_bar_class": "hist-bar",
          "primary_class_field": "class",
          "primary_width_fraction": 0.82,
          "bin_gap": 5,
          "bar_radius": 3,
          "x_axis_label": "Mahalanobis distance",
          "y_axis_label": false,
          "vertical_markers": [
            {
              "class": "threshold-line",
              "x": 4.5,
              "label": "threshold",
              "label_y": 24,
              "label_dx": 6,
              "label_anchor": "start",
              "label_class": "warning-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-MV-005.hist"
        }
      },
      {
        "componentInstanceId": "CHART-MV-005.notes.0",
        "componentType": "decision_card",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-MV-005.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-MV-005.summary": [
        {
          "label": "평균 distance",
          "value": 6.1,
          "displayValue": "6.1"
        },
        {
          "label": "초과 비중",
          "value": 0.22,
          "displayValue": "22%"
        },
        {
          "label": "최대 distance",
          "value": 6.9,
          "displayValue": "6.9"
        }
      ],
      "chart.CHART-MV-005.pca": [
        {
          "x": -1.8,
          "y": -0.8,
          "group": "low",
          "r": 4.7
        },
        {
          "x": -1.5,
          "y": -0.3,
          "group": "low",
          "r": 4.8
        },
        {
          "x": -1.2,
          "y": 0.2,
          "group": "low",
          "r": 5.0
        },
        {
          "x": -0.9,
          "y": -0.7,
          "group": "low",
          "r": 4.9
        },
        {
          "x": -0.6,
          "y": 0.3,
          "group": "low",
          "r": 5.1
        },
        {
          "x": -0.3,
          "y": -0.4,
          "group": "low",
          "r": 5.0
        },
        {
          "x": 0.0,
          "y": 0.1,
          "group": "low",
          "r": 4.8
        },
        {
          "x": 0.3,
          "y": -0.6,
          "group": "low",
          "r": 5.2
        },
        {
          "x": 0.6,
          "y": 0.2,
          "group": "low",
          "r": 5.3
        },
        {
          "x": 0.9,
          "y": -0.2,
          "group": "low",
          "r": 5.4
        },
        {
          "x": 1.1,
          "y": 0.6,
          "group": "low",
          "r": 5.7
        },
        {
          "x": 1.4,
          "y": 0.9,
          "group": "low",
          "r": 5.9
        },
        {
          "x": 1.7,
          "y": 1.2,
          "group": "low",
          "r": 6.3
        },
        {
          "x": 2.0,
          "y": 1.4,
          "group": "high",
          "r": 6.6
        },
        {
          "x": 2.3,
          "y": 1.7,
          "group": "high",
          "r": 7.1
        },
        {
          "x": 2.6,
          "y": 2.0,
          "group": "high",
          "r": 7.4
        },
        {
          "x": 2.9,
          "y": 1.6,
          "group": "high",
          "r": 7.2
        },
        {
          "x": 3.1,
          "y": 2.3,
          "group": "high",
          "r": 7.8
        },
        {
          "x": 1.9,
          "y": 2.4,
          "group": "high",
          "r": 6.9
        },
        {
          "x": 2.5,
          "y": 2.7,
          "group": "high",
          "r": 7.6
        }
      ],
      "chart.CHART-MV-005.distance": [
        {
          "window": 1,
          "distance": 2.1
        },
        {
          "window": 2,
          "distance": 2.3
        },
        {
          "window": 3,
          "distance": 2.4
        },
        {
          "window": 4,
          "distance": 2.8
        },
        {
          "window": 5,
          "distance": 3.1
        },
        {
          "window": 6,
          "distance": 3.6
        },
        {
          "window": 7,
          "distance": 4.2
        },
        {
          "window": 8,
          "distance": 4.9
        },
        {
          "window": 9,
          "distance": 5.5
        },
        {
          "window": 10,
          "distance": 6.1
        }
      ],
      "chart.CHART-MV-005.hist": [
        {
          "x0": 0.5,
          "x1": 1.5,
          "count": 5,
          "class": "hist-bar"
        },
        {
          "x0": 1.5,
          "x1": 2.5,
          "count": 8,
          "class": "hist-bar"
        },
        {
          "x0": 2.5,
          "x1": 3.5,
          "count": 11,
          "class": "hist-bar"
        },
        {
          "x0": 3.5,
          "x1": 4.5,
          "count": 9,
          "class": "hist-bar"
        },
        {
          "x0": 4.5,
          "x1": 5.5,
          "count": 6,
          "class": "distance-tail-bar"
        },
        {
          "x0": 5.5,
          "x1": 6.5,
          "count": 4,
          "class": "distance-tail-bar"
        },
        {
          "x0": 6.5,
          "x1": 7.5,
          "count": 2,
          "class": "distance-tail-bar"
        }
      ],
      "chart.CHART-MV-005.notes": [
        {
          "title": "해석",
          "text": "평균 Mahalanobis distance는 threshold 4.5를 넘어 6.1까지 증가했고, 최대 distance는 6.9이다. PCA scatter에서는 threshold 초과 sample이 기준 정상 타원의 우상향 방향에 몰리며 histogram에서는 전체 sample의 22%가 threshold 오른쪽 tail에 쌓인다.",
          "legend": [
            {
              "label": "낮은 distance",
              "class": "swatch-low"
            },
            {
              "label": "높은 distance",
              "class": "swatch-high"
            },
            {
              "label": "평균 distance",
              "class": "swatch-distance"
            },
            {
              "label": "threshold",
              "class": "swatch-threshold"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-PROB-001",
    "title": "오른쪽 값 구간의 확률 증가와 KL 기여",
    "originalPath": "./drift_report_charts/chart_prob_001.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_prob_001",
      "displayName": "CHART-PROB-001 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 112px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "확률분포 중첩",
          "description": "오른쪽 0.8, 1.2, 1.6 bin에서 현재 확률이 기준 확률보다 높아지는지 본다.",
          "headerHeight": 58,
          "stageInset": {
            "top": 66,
            "right": 16,
            "bottom": 12,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "발산 추세",
          "description": "KL이 직전 0.086에서 현재 0.023으로 관리 기준 0.070 아래로 내려왔는지 확인한다.",
          "headerHeight": 56,
          "stageInset": {
            "top": 58,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "기여 구간 순위",
          "description": "1.2 bin 기여도 0.042가 가장 크고 오른쪽 bin들이 상위에 몰리는지 읽는다.",
          "headerHeight": 56,
          "stageInset": {
            "top": 58,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "interpretation",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-PROB-001.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "display_value_field": "displayValue",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-PROB-001.summary"
        }
      },
      {
        "componentInstanceId": "CHART-PROB-001.distribution.0",
        "componentType": "bar_chart",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "vertical_grouped",
          "category_field": "label",
          "series_fields": [
            "reference",
            "current"
          ],
          "series_classes": [
            "ref-bar",
            "cur-bar"
          ],
          "y_max": 0.2,
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 20,
            "right": 22,
            "bottom": 58,
            "left": 58
          },
          "y_ticks": [
            0,
            0.05,
            0.1,
            0.15,
            0.2
          ],
          "x_axis_label": "확률 bin",
          "y_axis_label": "확률",
          "label_every": 2,
          "gap_lines": [
            {
              "from_field": "reference",
              "to_field": "current",
              "min": 0.012,
              "positive_only": true,
              "class": "contrib-line"
            }
          ],
          "annotations": [
            {
              "class": "callout",
              "x": 400,
              "y": 38,
              "text": "기여 최대 bin: 1.2"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-PROB-001.distribution"
        }
      },
      {
        "componentInstanceId": "CHART-PROB-001.kl.0",
        "componentType": "distance_metric_view",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "time_field": "window",
          "value_field": "kl",
          "x_min": 1,
          "x_max": 8,
          "y_min": 0,
          "y_max": 0.11,
          "y_ticks": [
            0,
            0.07,
            0.11
          ],
          "x_ticks": [],
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 18,
            "bottom": 34,
            "left": 48
          },
          "line_class": "trend-line",
          "primary_point_class": "trend-point",
          "point_radius": 4,
          "x_axis_label": "window",
          "y_axis_label": false,
          "horizontal_markers": [
            {
              "class": "threshold-line",
              "y": 0.07,
              "label": "관리 기준",
              "label_x": 6.8,
              "label_dy": -7,
              "label_class": "callout"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-PROB-001.kl"
        }
      },
      {
        "componentInstanceId": "CHART-PROB-001.contrib.0",
        "componentType": "contribution_view",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "horizontal_ranked",
          "category_field": "label",
          "value_field": "value",
          "value_label_field": "displayValue",
          "preserve_order": true,
          "limit": 5,
          "x_max": 0.05,
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 8,
            "right": 22,
            "bottom": 28,
            "left": 112
          },
          "row_gap": 27,
          "first_y": 18,
          "bar_height": 16,
          "bar_class": "contrib-bar",
          "highlight_class": "bar-highlight",
          "caption": "q log(q / p)"
        },
        "dataBinding": {
          "source": "chart.CHART-PROB-001.contrib"
        }
      },
      {
        "componentInstanceId": "CHART-PROB-001.notes.0",
        "componentType": "decision_card",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-PROB-001.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-PROB-001.summary": [
        {
          "label": "KL(q||p)",
          "value": 0.0232103499,
          "displayValue": "0.023"
        },
        {
          "label": "역방향 KL",
          "value": 0.0621525604,
          "displayValue": "0.062"
        },
        {
          "label": "최대 기여 bin",
          "value": 1.2,
          "displayValue": "1.2"
        }
      ],
      "chart.CHART-PROB-001.distribution": [
        {
          "label": "<-2.0",
          "reference": 0.055,
          "current": 0.035,
          "contribution": -0.015819
        },
        {
          "label": "-1.6",
          "reference": 0.071,
          "current": 0.047,
          "contribution": -0.019389
        },
        {
          "label": "-1.2",
          "reference": 0.095,
          "current": 0.07,
          "contribution": -0.021377
        },
        {
          "label": "-0.8",
          "reference": 0.128,
          "current": 0.102,
          "contribution": -0.02316
        },
        {
          "label": "-0.4",
          "reference": 0.161,
          "current": 0.13,
          "contribution": -0.027803
        },
        {
          "label": "0.0",
          "reference": 0.152,
          "current": 0.141,
          "contribution": -0.010592
        },
        {
          "label": "0.4",
          "reference": 0.125,
          "current": 0.134,
          "contribution": 0.009316
        },
        {
          "label": "0.8",
          "reference": 0.091,
          "current": 0.115,
          "contribution": 0.026918
        },
        {
          "label": "1.2",
          "reference": 0.062,
          "current": 0.096,
          "contribution": 0.041973
        },
        {
          "label": "1.6",
          "reference": 0.04,
          "current": 0.066,
          "contribution": 0.033051
        },
        {
          "label": "2.0",
          "reference": 0.024,
          "current": 0.039,
          "contribution": 0.018935
        },
        {
          "label": ">2.4",
          "reference": 0.016,
          "current": 0.025,
          "contribution": 0.011157
        }
      ],
      "chart.CHART-PROB-001.kl": [
        {
          "window": 1,
          "kl": 0.028
        },
        {
          "window": 2,
          "kl": 0.034
        },
        {
          "window": 3,
          "kl": 0.041
        },
        {
          "window": 4,
          "kl": 0.038
        },
        {
          "window": 5,
          "kl": 0.052
        },
        {
          "window": 6,
          "kl": 0.071
        },
        {
          "window": 7,
          "kl": 0.086
        },
        {
          "window": 8,
          "kl": 0.0232103499
        }
      ],
      "chart.CHART-PROB-001.contrib": [
        {
          "label": "1.2",
          "value": 0.041973,
          "displayValue": "0.042",
          "class": "bar-highlight"
        },
        {
          "label": "1.6",
          "value": 0.033051,
          "displayValue": "0.033",
          "class": "contrib-bar"
        },
        {
          "label": "0.8",
          "value": 0.026918,
          "displayValue": "0.027",
          "class": "contrib-bar"
        },
        {
          "label": "2.0",
          "value": 0.018935,
          "displayValue": "0.019",
          "class": "contrib-bar"
        },
        {
          "label": ">2.4",
          "value": 0.011157,
          "displayValue": "0.011",
          "class": "contrib-bar"
        }
      ],
      "chart.CHART-PROB-001.notes": [
        {
          "title": "해석",
          "text": "이 예시에서는 현재 분포가 기준보다 오른쪽 값 구간에서 두꺼워진다. KL(q||p)는 0.023으로 현재 window에서는 관리 기준 0.070 아래지만, 직전 window에서 0.086까지 올랐고 1.2, 1.6, 0.8 bin이 KL 기여 상위 구간이다. 따라서 강한 drift 확정보다는 오른쪽 값 구간 확률 증가가 완화 중인 분포 변화 후보로 해석한다.",
          "legend": [
            {
              "label": "기준 확률",
              "class": "swatch-reference"
            },
            {
              "label": "현재 확률",
              "class": "swatch-current-red"
            },
            {
              "label": "KL 기여",
              "class": "swatch-divergence"
            },
            {
              "label": "관리 기준",
              "class": "swatch-threshold"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-PROB-002",
    "title": "탐색 감소와 구매 증가로 보는 카테고리 비중 변화",
    "originalPath": "./drift_report_charts/chart_prob_002.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_prob_002",
      "displayName": "CHART-PROB-002 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 112px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "확률분포 중첩",
          "description": "검색은 0.24에서 0.17로 줄고 구매는 0.18에서 0.25로 늘어나는지 본다.",
          "headerHeight": 58,
          "stageInset": {
            "top": 66,
            "right": 16,
            "bottom": 12,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "유계 거리 추세",
          "description": "JS가 직전 0.18에서 현재 0.121로 관리 기준 아래로 내려왔는지 확인한다.",
          "headerHeight": 56,
          "stageInset": {
            "top": 58,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "범주 변화량",
          "description": "구매 +0.07과 검색 -0.07이 가장 큰 category mix 변화인지 읽는다.",
          "headerHeight": 56,
          "stageInset": {
            "top": 58,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "interpretation",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-PROB-002.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "display_value_field": "displayValue",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-PROB-002.summary"
        }
      },
      {
        "componentInstanceId": "CHART-PROB-002.distribution.0",
        "componentType": "bar_chart",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "vertical_grouped",
          "category_field": "label",
          "series_fields": [
            "reference",
            "current"
          ],
          "series_classes": [
            "ref-bar",
            "cur-bar"
          ],
          "y_max": 0.305,
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 20,
            "right": 22,
            "bottom": 70,
            "left": 58
          },
          "y_ticks": [
            0,
            0.1,
            0.2,
            0.3
          ],
          "x_axis_label": "category",
          "y_axis_label": "확률",
          "group_padding": 8,
          "bar_gap": 4,
          "overlay_bars": [
            {
              "value_field": "overlap",
              "class": "overlap-band",
              "render_order": "before_bars",
              "x_offset_bar_width": 0,
              "width_bar_width": 2,
              "width_adjust": 4,
              "radius": 4
            }
          ],
          "annotations": [
            {
              "class": "callout",
              "x": 306,
              "y": 40,
              "text": "최대 변화: 검색 -0.07 / 구매 +0.07"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-PROB-002.distribution"
        }
      },
      {
        "componentInstanceId": "CHART-PROB-002.trend.0",
        "componentType": "distance_metric_view",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "time_field": "window",
          "value_field": "js",
          "secondary_value_field": "hellinger",
          "x_min": 1,
          "x_max": 7,
          "y_min": 0,
          "y_max": 0.35,
          "y_ticks": [
            0,
            0.18,
            0.35
          ],
          "x_ticks": [],
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 18,
            "bottom": 34,
            "left": 48
          },
          "line_class": "trend-line",
          "secondary_line_class": "hell-line",
          "primary_point_class": "trend-point",
          "secondary_point_class": "hell-point",
          "point_radius": 4,
          "secondary_point_radius": 4,
          "x_axis_label": "window",
          "y_axis_label": false,
          "horizontal_markers": [
            {
              "class": "threshold-line",
              "y": 0.18
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-PROB-002.trend"
        }
      },
      {
        "componentInstanceId": "CHART-PROB-002.delta.0",
        "componentType": "bar_chart",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "horizontal_diverging",
          "category_field": "label",
          "value_field": "delta",
          "value_label_field": "displayValue",
          "x_abs_max": 0.0875,
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 8,
            "right": 24,
            "bottom": 28,
            "left": 98
          },
          "row_gap": 21,
          "first_y": 13,
          "bar_height": 14,
          "positive_class": "delta-pos",
          "negative_class": "delta-neg",
          "caption": "현재 확률 - 기준 확률"
        },
        "dataBinding": {
          "source": "chart.CHART-PROB-002.delta"
        }
      },
      {
        "componentInstanceId": "CHART-PROB-002.notes.0",
        "componentType": "decision_card",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-PROB-002.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-PROB-002.summary": [
        {
          "label": "JS Distance",
          "value": 0.12114695384847626,
          "displayValue": "0.121"
        },
        {
          "label": "Hellinger",
          "value": 0.1009903993746954,
          "displayValue": "0.101"
        },
        {
          "label": "최대 Delta",
          "value": 0.07,
          "displayValue": "구매 +0.07"
        }
      ],
      "chart.CHART-PROB-002.distribution": [
        {
          "label": "검색",
          "reference": 0.24,
          "current": 0.17,
          "overlap": 0.17
        },
        {
          "label": "상세",
          "reference": 0.22,
          "current": 0.19,
          "overlap": 0.19
        },
        {
          "label": "장바구니",
          "reference": 0.15,
          "current": 0.18,
          "overlap": 0.15
        },
        {
          "label": "구매",
          "reference": 0.18,
          "current": 0.25,
          "overlap": 0.18
        },
        {
          "label": "환불",
          "reference": 0.05,
          "current": 0.08,
          "overlap": 0.05
        },
        {
          "label": "문의",
          "reference": 0.1,
          "current": 0.07,
          "overlap": 0.07
        },
        {
          "label": "리뷰",
          "reference": 0.06,
          "current": 0.06,
          "overlap": 0.06
        }
      ],
      "chart.CHART-PROB-002.trend": [
        {
          "window": 1,
          "js": 0.08,
          "hellinger": 0.07
        },
        {
          "window": 2,
          "js": 0.1,
          "hellinger": 0.09
        },
        {
          "window": 3,
          "js": 0.11,
          "hellinger": 0.1
        },
        {
          "window": 4,
          "js": 0.13,
          "hellinger": 0.12
        },
        {
          "window": 5,
          "js": 0.16,
          "hellinger": 0.15
        },
        {
          "window": 6,
          "js": 0.18,
          "hellinger": 0.17
        },
        {
          "window": 7,
          "js": 0.12114695384847626,
          "hellinger": 0.1009903993746954
        }
      ],
      "chart.CHART-PROB-002.delta": [
        {
          "label": "검색",
          "delta": -0.06999999999999998,
          "displayValue": "-0.07",
          "class": "delta-neg"
        },
        {
          "label": "상세",
          "delta": -0.03,
          "displayValue": "-0.03",
          "class": "delta-neg"
        },
        {
          "label": "장바구니",
          "delta": 0.03,
          "displayValue": "+0.03",
          "class": "delta-pos"
        },
        {
          "label": "구매",
          "delta": 0.07,
          "displayValue": "+0.07",
          "class": "delta-pos"
        },
        {
          "label": "환불",
          "delta": 0.03,
          "displayValue": "+0.03",
          "class": "delta-pos"
        },
        {
          "label": "문의",
          "delta": -0.03,
          "displayValue": "-0.03",
          "class": "delta-neg"
        },
        {
          "label": "리뷰",
          "delta": 0.0,
          "displayValue": "+0.00",
          "class": "delta-pos"
        }
      ],
      "chart.CHART-PROB-002.notes": [
        {
          "title": "해석",
          "text": "이 예시에서는 탐색 단계인 검색 비중이 0.24에서 0.17로 줄고, 구매 비중이 0.18에서 0.25로 늘어난다. JS Distance는 0.121, Hellinger는 0.101로 현재 window에서는 관리 기준 0.18 아래지만, 직전 window에서 JS가 0.18에 닿았으므로 완화 중인 category mix 변화 후보로 해석한다.",
          "legend": [
            {
              "label": "기준 확률",
              "class": "swatch-reference"
            },
            {
              "label": "현재 확률",
              "class": "swatch-current-red"
            },
            {
              "label": "증가 category",
              "class": "swatch-divergence"
            },
            {
              "label": "감소 category",
              "class": "swatch-threshold"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-PROB-003",
    "title": "오른쪽 이동으로 줄어든 기준·현재 분포 겹침",
    "originalPath": "./drift_report_charts/chart_prob_003.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_prob_003",
      "displayName": "CHART-PROB-003 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 112px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "확률분포 중첩",
          "description": "1.5 bin은 0.06에서 0.115로 늘고 -1 bin은 0.13에서 0.08로 줄어드는지 본다.",
          "headerHeight": 58,
          "stageInset": {
            "top": 66,
            "right": 16,
            "bottom": 12,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "겹침 계수",
          "description": "겹침 82.0%와 BC 0.977이 아직 높은 유사도를 뜻하는지 확인한다.",
          "headerHeight": 56,
          "stageInset": {
            "top": 58,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "거리 추세",
          "description": "distance가 직전 0.031에서 현재 0.023으로 관리 기준 0.030 아래로 내려왔는지 읽는다.",
          "headerHeight": 56,
          "stageInset": {
            "top": 58,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "interpretation",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-PROB-003.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "display_value_field": "displayValue",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-PROB-003.summary"
        }
      },
      {
        "componentInstanceId": "CHART-PROB-003.distribution.0",
        "componentType": "bar_chart",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "vertical_grouped",
          "category_field": "label",
          "series_fields": [
            "reference",
            "current"
          ],
          "series_classes": [
            "ref-bar",
            "cur-bar"
          ],
          "y_max": 0.2356,
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 20,
            "right": 22,
            "bottom": 58,
            "left": 58
          },
          "y_ticks": [
            0,
            0.05,
            0.1,
            0.15,
            0.2
          ],
          "x_axis_label": "확률 bin",
          "y_axis_label": "확률",
          "label_every": 2,
          "group_padding": 5,
          "bar_gap": 5,
          "annotations": [
            {
              "class": "callout",
              "x": 302,
              "y": 40,
              "text": "겹침 계수 0.82"
            }
          ],
          "overlay_bars": [
            {
              "value_field": "overlap",
              "class": "overlap-bar",
              "x_offset_bar_width": 0.48,
              "width_bar_width": 1.06,
              "radius": 3
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-PROB-003.distribution"
        }
      },
      {
        "componentInstanceId": "CHART-PROB-003.overlap.0",
        "componentType": "bar_chart",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "horizontal_stacked",
          "category_field": "label",
          "series_fields": [
            "overlap",
            "missing"
          ],
          "series_classes": [
            "overlap-fill",
            "missing-fill"
          ],
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 22,
            "bottom": 30,
            "left": 46
          },
          "first_y": 60,
          "bar_height": 34,
          "background_class": "overlap-bg",
          "background_radius": 8,
          "bar_radius": 8,
          "hide_category_label": true,
          "value_label_position": "segment_end",
          "value_label_series_index": 0,
          "value_label_field": "displayValue",
          "value_label_class": "bar-label",
          "annotations": [
            {
              "text": "겹침",
              "x": 46,
              "y": 48,
              "class": "callout"
            },
            {
              "text": "비겹침",
              "x": 396,
              "y": 48,
              "class": "bar-label"
            },
            {
              "text": "Bhattacharyya coefficient 0.977",
              "x": 46,
              "y": 132,
              "class": "axis-tick"
            },
            {
              "text": "확률 차이 최대 bin: 1.5",
              "x": 46,
              "y": 154,
              "class": "axis-tick"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-PROB-003.overlap"
        }
      },
      {
        "componentInstanceId": "CHART-PROB-003.trend.0",
        "componentType": "distance_metric_view",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "time_field": "window",
          "value_field": "distance",
          "x_min": 1,
          "x_max": 7,
          "y_min": 0,
          "y_max": 0.06,
          "y_ticks": [
            0,
            0.03,
            0.06
          ],
          "x_ticks": [],
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 18,
            "bottom": 34,
            "left": 48
          },
          "line_class": "trend-line",
          "primary_point_class": "trend-point",
          "point_radius": 4,
          "x_axis_label": "window",
          "y_axis_label": false,
          "horizontal_markers": [
            {
              "class": "threshold-line",
              "y": 0.03,
              "label": "관리 기준",
              "label_x": 6.1,
              "label_dy": -7,
              "label_class": "callout"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-PROB-003.trend"
        }
      },
      {
        "componentInstanceId": "CHART-PROB-003.notes.0",
        "componentType": "decision_card",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-PROB-003.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-PROB-003.summary": [
        {
          "label": "Bhattacharyya",
          "value": 0.023438972293096993,
          "displayValue": "0.023"
        },
        {
          "label": "겹침 계수",
          "value": 0.8200000000000001,
          "displayValue": "0.820"
        },
        {
          "label": "BC 계수",
          "value": 0.9768335867636566,
          "displayValue": "0.977"
        }
      ],
      "chart.CHART-PROB-003.distribution": [
        {
          "label": "<-2",
          "reference": 0.05,
          "current": 0.025,
          "overlap": 0.025
        },
        {
          "label": "-1.5",
          "reference": 0.08,
          "current": 0.045,
          "overlap": 0.045
        },
        {
          "label": "-1",
          "reference": 0.13,
          "current": 0.08,
          "overlap": 0.08
        },
        {
          "label": "-0.5",
          "reference": 0.17,
          "current": 0.13,
          "overlap": 0.13
        },
        {
          "label": "0",
          "reference": 0.19,
          "current": 0.16,
          "overlap": 0.16
        },
        {
          "label": "0.5",
          "reference": 0.16,
          "current": 0.17,
          "overlap": 0.16
        },
        {
          "label": "1",
          "reference": 0.11,
          "current": 0.16,
          "overlap": 0.11
        },
        {
          "label": "1.5",
          "reference": 0.06,
          "current": 0.115,
          "overlap": 0.06
        },
        {
          "label": "2",
          "reference": 0.03,
          "current": 0.07,
          "overlap": 0.03
        },
        {
          "label": ">2.5",
          "reference": 0.02,
          "current": 0.045,
          "overlap": 0.02
        }
      ],
      "chart.CHART-PROB-003.overlap": [
        {
          "label": "겹침",
          "overlap": 0.8200000000000001,
          "missing": 0.17999999999999994,
          "displayValue": "82.0%"
        }
      ],
      "chart.CHART-PROB-003.trend": [
        {
          "window": 1,
          "distance": 0.01
        },
        {
          "window": 2,
          "distance": 0.014
        },
        {
          "window": 3,
          "distance": 0.018
        },
        {
          "window": 4,
          "distance": 0.02
        },
        {
          "window": 5,
          "distance": 0.026
        },
        {
          "window": 6,
          "distance": 0.031
        },
        {
          "window": 7,
          "distance": 0.023438972293096993
        }
      ],
      "chart.CHART-PROB-003.notes": [
        {
          "title": "해석",
          "text": "이 예시에서는 현재 분포가 기준보다 오른쪽으로 이동해 1, 1.5, 2 bin 확률이 커지고 왼쪽 bin 확률은 줄어든다. 겹침 계수는 0.820이고 Bhattacharyya distance는 0.023으로 현재 window에서는 관리 기준 0.030 아래다. 따라서 강한 분리 확정보다는 완만한 overlap 감소가 완화 중인 분포 변화 후보로 해석한다.",
          "legend": [
            {
              "label": "기준 확률",
              "class": "swatch-reference"
            },
            {
              "label": "현재 확률",
              "class": "swatch-current-red"
            },
            {
              "label": "겹침 영역",
              "class": "swatch-overlap"
            },
            {
              "label": "거리",
              "class": "swatch-threshold"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-PSI-001",
    "title": "상위 점수 구간 증가로 본 PSI 드리프트",
    "originalPath": "./drift_report_charts/chart_psi_001.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_psi_001",
      "displayName": "CHART-PSI-001 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 112px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "구간 비율 비교",
          "description": "80-100 bin은 기준 12%에서 현재 20%로 +8pp 증가한다.",
          "headerHeight": 58,
          "stageInset": {
            "top": 66,
            "right": 16,
            "bottom": 12,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "PSI 기여도",
          "description": "80-100 bin 기여도 0.041이 전체 PSI를 가장 크게 만든다.",
          "headerHeight": 56,
          "stageInset": {
            "top": 58,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "PSI 추세",
          "description": "최근 window PSI 0.123이 관리 기준 0.10을 넘는다.",
          "headerHeight": 56,
          "stageInset": {
            "top": 58,
            "right": 16,
            "bottom": 10,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "interpretation",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-PSI-001.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "display_value_field": "displayValue",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-PSI-001.summary"
        }
      },
      {
        "componentInstanceId": "CHART-PSI-001.bins.0",
        "componentType": "bar_chart",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "vertical_grouped",
          "category_field": "label",
          "series_fields": [
            "reference",
            "current"
          ],
          "series_classes": [
            "ref-bar",
            "cur-bar"
          ],
          "y_max": 0.38,
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 22,
            "right": 24,
            "bottom": 70,
            "left": 58
          },
          "y_ticks": [
            0,
            0.1,
            0.2,
            0.3
          ],
          "y_tick_format": "percent",
          "x_axis_label": "score band / feature bin",
          "y_axis_label": "비율",
          "group_padding": 14,
          "bar_gap": 5,
          "category_sub_label_field": "deltaLabel",
          "category_sub_label_y": 43,
          "category_highlights": [
            {
              "category": "80-100",
              "class": "highlight-band",
              "dx": 7,
              "y": 22,
              "height": 348,
              "rx": 8
            }
          ],
          "annotations": [
            {
              "class": "callout",
              "x": 278,
              "y": 42,
              "text": "상위 기여: 80-100 bin"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-PSI-001.bins"
        }
      },
      {
        "componentInstanceId": "CHART-PSI-001.contrib.0",
        "componentType": "contribution_view",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "horizontal_ranked",
          "category_field": "label",
          "value_field": "value",
          "value_label_field": "displayValue",
          "preserve_order": true,
          "limit": 5,
          "x_max": 0.05108256237659908,
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 8,
            "right": 24,
            "bottom": 30,
            "left": 72
          },
          "row_gap": 27,
          "first_y": 13,
          "bar_height": 18,
          "bar_class": "contrib-bar",
          "highlight_class": "top-contribution",
          "caption": "PSI contribution"
        },
        "dataBinding": {
          "source": "chart.CHART-PSI-001.contrib"
        }
      },
      {
        "componentInstanceId": "CHART-PSI-001.trend.0",
        "componentType": "distance_metric_view",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "time_field": "window",
          "value_field": "psi",
          "x_min": 1,
          "x_max": 7,
          "y_min": 0,
          "y_max": 0.18,
          "y_ticks": [
            0,
            0.1,
            0.18
          ],
          "x_ticks": [],
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 18,
            "bottom": 34,
            "left": 48
          },
          "line_class": "trend-line",
          "primary_point_class": "trend-point",
          "point_radius": 4,
          "x_axis_label": "window",
          "y_axis_label": false,
          "horizontal_markers": [
            {
              "class": "threshold-line",
              "y": 0.1,
              "label": "관리 기준",
              "label_x": 6.1,
              "label_dy": -7,
              "label_class": "callout"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-PSI-001.trend"
        }
      },
      {
        "componentInstanceId": "CHART-PSI-001.notes.0",
        "componentType": "decision_card",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-PSI-001.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-PSI-001.summary": [
        {
          "label": "PSI",
          "value": 0.12336393213761043,
          "displayValue": "0.123"
        },
        {
          "label": "상위 기여 bin",
          "value": "80-100",
          "displayValue": "80-100"
        },
        {
          "label": "주요 이동",
          "value": 0.08000000000000002,
          "displayValue": "증가 8.0pp"
        }
      ],
      "chart.CHART-PSI-001.bins": [
        {
          "label": "0-20",
          "reference": 0.12,
          "current": 0.07,
          "deltaLabel": "-5pp"
        },
        {
          "label": "20-40",
          "reference": 0.22,
          "current": 0.15,
          "deltaLabel": "-7pp"
        },
        {
          "label": "40-60",
          "reference": 0.3,
          "current": 0.26,
          "deltaLabel": "-4pp"
        },
        {
          "label": "60-80",
          "reference": 0.24,
          "current": 0.32,
          "deltaLabel": "+8pp"
        },
        {
          "label": "80-100",
          "reference": 0.12,
          "current": 0.2,
          "deltaLabel": "+8pp"
        }
      ],
      "chart.CHART-PSI-001.contrib": [
        {
          "label": "80-100",
          "value": 0.04086604990127927,
          "displayValue": "0.041 (+8pp)",
          "class": "top-contribution"
        },
        {
          "label": "0-20",
          "value": 0.026949825036634338,
          "displayValue": "0.027 (-5pp)",
          "class": "contrib-bar"
        },
        {
          "label": "20-40",
          "value": 0.026809457657927412,
          "displayValue": "0.027 (-7pp)",
          "class": "contrib-bar"
        },
        {
          "label": "60-80",
          "value": 0.023014565796142486,
          "displayValue": "0.023 (+8pp)",
          "class": "contrib-bar"
        },
        {
          "label": "40-60",
          "value": 0.005724033745626929,
          "displayValue": "0.006 (-4pp)",
          "class": "contrib-bar"
        }
      ],
      "chart.CHART-PSI-001.trend": [
        {
          "window": 1,
          "psi": 0.035
        },
        {
          "window": 2,
          "psi": 0.044
        },
        {
          "window": 3,
          "psi": 0.052
        },
        {
          "window": 4,
          "psi": 0.071
        },
        {
          "window": 5,
          "psi": 0.092
        },
        {
          "window": 6,
          "psi": 0.118
        },
        {
          "window": 7,
          "psi": 0.12336393213761043
        }
      ],
      "chart.CHART-PSI-001.notes": [
        {
          "title": "해석",
          "text": "이 예시에서는 PSI가 0.123으로 관리 기준 0.10을 초과한다. 80-100 bin은 기준 12%에서 현재 20%로 +8pp 늘어 기여도 0.041로 가장 크고, 60-80 bin도 24%에서 32%로 +8pp 증가한다. 상위 score band로 population이 이동한 PSI drift 후보로 해석한다.",
          "legend": [
            {
              "label": "기준 비율",
              "class": "swatch-reference"
            },
            {
              "label": "현재 비율",
              "class": "swatch-current-red"
            },
            {
              "label": "PSI 기여",
              "class": "swatch-divergence"
            },
            {
              "label": "관리 기준",
              "class": "swatch-threshold"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-RANK-001",
    "title": "높은 순위로 치우친 현재 구간의 위치 이동",
    "originalPath": "./drift_report_charts/chart_rank_001.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_rank_001",
      "displayName": "CHART-RANK-001 source layout",
      "columns": 12,
      "rows": 3,
      "gridTemplateRows": "76px 544px 128px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 6,
          "h": 1,
          "title": "상자/바이올린 분포 비교",
          "description": "중앙값이 -0.07에서 0.50으로 올라가고 IQR도 높은 값 쪽으로 이동했는지 본다.",
          "headerHeight": 58,
          "stageInset": {
            "top": 66,
            "right": 14,
            "bottom": 12,
            "left": 14
          }
        },
        {
          "area": "side_top",
          "role": "primary_visual",
          "x": 6,
          "y": 1,
          "w": 6,
          "h": 1,
          "title": "결합 순위 분포",
          "description": "순위 AUC 0.652처럼 현재 샘플이 기준보다 높은 결합 순위에 더 자주 놓이는지 확인한다.",
          "headerHeight": 58,
          "stageInset": {
            "top": 66,
            "right": 14,
            "bottom": 12,
            "left": 14
          }
        },
        {
          "area": "notes",
          "role": "interpretation",
          "x": 0,
          "y": 2,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-RANK-001.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "label_field": "label",
          "primary_metric_field": "value",
          "display_value_field": "displayValue",
          "visual_code": "summary_metrics"
        },
        "dataBinding": {
          "source": "chart.CHART-RANK-001.summary"
        }
      },
      {
        "componentInstanceId": "CHART-RANK-001.distribution.0",
        "componentType": "distribution_summary_plot",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "distribution_style": "violin_summary",
          "value_field": "observed",
          "view_box": [
            535,
            450
          ],
          "margin": {
            "top": 22,
            "right": 26,
            "bottom": 52,
            "left": 58
          },
          "y_min": -3.0,
          "y_max": 3.5,
          "y_ticks": [
            -3.0,
            -1,
            0,
            1,
            3.5
          ],
          "x_positions": [
            205,
            350
          ],
          "density_width": 46,
          "box_width": 58,
          "mean_width": 0,
          "violin_classes": [
            "violin-ref",
            "violin-cur"
          ],
          "box_class": "box-ref",
          "whisker_class": "whisker",
          "median_class": "median-line",
          "mean_line_class": "median-line",
          "mean_label_class": "axis-label",
          "mean_label_dy": -999,
          "group_label_y": 396,
          "y_axis_label": "관측값",
          "annotations": [
            {
              "class": "callout",
              "x": 270,
              "y": 166,
              "text": "중앙값 차이 0.57"
            }
          ],
          "connectors": [
            {
              "from_index": 0,
              "to_index": 1,
              "field": "median",
              "class": "median-line",
              "x1_offset": 38,
              "x2_offset": -38
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-RANK-001.distribution"
        }
      },
      {
        "componentInstanceId": "CHART-RANK-001.rank.0",
        "componentType": "bar_chart",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "vertical_grouped",
          "category_field": "label",
          "series_fields": [
            "reference",
            "current"
          ],
          "series_classes": [
            "rank-ref",
            "rank-cur"
          ],
          "y_max": 31,
          "view_box": [
            535,
            450
          ],
          "margin": {
            "top": 22,
            "right": 26,
            "bottom": 52,
            "left": 58
          },
          "y_ticks": [
            0,
            16,
            31
          ],
          "x_axis_label": "결합 순위",
          "y_axis_label": "빈도",
          "label_every": 3,
          "group_padding": 5,
          "bar_gap": 3,
          "overlay_lines": [
            {
              "value_field": "balance",
              "class": "rank-balance"
            }
          ],
          "annotations": [
            {
              "class": "callout",
              "x": 266,
              "y": 44,
              "text": "현재 구간이 높은 순위에 더 많이 분포"
            }
          ],
          "hide_category_labels": true,
          "x_min": 1,
          "x_max": 440,
          "x_value_ticks": [
            1,
            110,
            220,
            330,
            440
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-RANK-001.rank"
        }
      },
      {
        "componentInstanceId": "CHART-RANK-001.notes.0",
        "componentType": "decision_card",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-RANK-001.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-RANK-001.summary": [
        {
          "label": "Mann-Whitney U",
          "value": 31551.0,
          "displayValue": "31,551"
        },
        {
          "label": "순위 AUC",
          "value": 0.6518801652892562,
          "displayValue": "0.652"
        },
        {
          "label": "중앙값 차이",
          "value": 0.5720226535604314,
          "displayValue": "0.57"
        }
      ],
      "chart.CHART-RANK-001.distribution": [
        {
          "label": "기준 구간",
          "class": "violin-ref",
          "box_class": "box-ref",
          "x": 205,
          "low": -1.7422049626930762,
          "q1": -0.7442057122461005,
          "median": -0.068039113482641,
          "q3": 0.6108736196406165,
          "high": 1.3276282518279932,
          "mean": -0.068039113482641,
          "density": [
            [
              -3.0,
              0.015580470567210713
            ],
            [
              -2.931578947368421,
              0.021176818191988564
            ],
            [
              -2.863157894736842,
              0.02810402544635303
            ],
            [
              -2.794736842105263,
              0.036485911053739724
            ],
            [
              -2.7263157894736842,
              0.04640498072349644
            ],
            [
              -2.6578947368421053,
              0.05787837243160133
            ],
            [
              -2.5894736842105264,
              0.07083150619225301
            ],
            [
              -2.5210526315789474,
              0.08507743148808145
            ],
            [
              -2.4526315789473685,
              0.10031230973301748
            ],
            [
              -2.3842105263157896,
              0.11613641017650553
            ],
            [
              -2.3157894736842106,
              0.13210486214218947
            ],
            [
              -2.2473684210526317,
              0.14780422140834412
            ],
            [
              -2.1789473684210527,
              0.1629420199258685
            ],
            [
              -2.110526315789474,
              0.17742977860849352
            ],
            [
              -2.042105263157895,
              0.19143803841193285
            ],
            [
              -1.9736842105263157,
              0.20540624523503934
            ],
            [
              -1.9052631578947368,
              0.22000051988470057
            ],
            [
              -1.8368421052631578,
              0.2360261242509949
            ],
            [
              -1.768421052631579,
              0.25431466912264483
            ],
            [
              -1.7,
              0.27561394604513817
            ],
            [
              -1.631578947368421,
              0.3005069743304037
            ],
            [
              -1.563157894736842,
              0.3293757847507611
            ],
            [
              -1.4947368421052631,
              0.3624080785149204
            ],
            [
              -1.4263157894736842,
              0.39962802475730447
            ],
            [
              -1.3578947368421053,
              0.4409236393360636
            ],
            [
              -1.2894736842105263,
              0.4860471558392744
            ],
            [
              -1.2210526315789474,
              0.5345807104729955
            ],
            [
              -1.1526315789473685,
              0.5858807285949178
            ],
            [
              -1.0842105263157895,
              0.6390305885374882
            ],
            [
              -1.0157894736842106,
              0.6928340016352925
            ],
            [
              -0.9473684210526314,
              0.7458688643209299
            ],
            [
              -0.8789473684210525,
              0.7965988659806322
            ],
            [
              -0.8105263157894735,
              0.8435190142991174
            ],
            [
              -0.7421052631578946,
              0.885301987157799
            ],
            [
              -0.6736842105263157,
              0.9209185689395669
            ],
            [
              -0.6052631578947367,
              0.9497218402970785
            ],
            [
              -0.5368421052631578,
              0.9714996541969076
            ],
            [
              -0.46842105263157885,
              0.9865029682044986
            ],
            [
              -0.3999999999999999,
              0.9954469883772435
            ],
            [
              -0.331578947368421,
              0.9994664638626883
            ],
            [
              -0.26315789473684204,
              1.0
            ],
            [
              -0.1947368421052631,
              0.9985912655930441
            ],
            [
              -0.12631578947368416,
              0.9966262027152852
            ],
            [
              -0.05789473684210522,
              0.9950610337240917
            ],
            [
              0.010526315789473717,
              0.9942167421164881
            ],
            [
              0.07894736842105265,
              0.9937079717878892
            ],
            [
              0.1473684210526316,
              0.9925377554732964
            ],
            [
              0.21578947368421053,
              0.9893380716830629
            ],
            [
              0.28421052631578947,
              0.9826907320626079
            ],
            [
              0.3526315789473684,
              0.9714407989664562
            ],
            [
              0.42105263157894735,
              0.9549218910813613
            ],
            [
              0.4894736842105263,
              0.9330435534612974
            ],
            [
              0.5578947368421052,
              0.9062322446225717
            ],
            [
              0.6263157894736842,
              0.8752558424799147
            ],
            [
              0.6947368421052631,
              0.8409877145319338
            ],
            [
              0.763157894736842,
              0.8041767262078641
            ],
            [
              0.831578947368421,
              0.765284400990117
            ],
            [
              0.8999999999999999,
              0.724431965132678
            ],
            [
              0.9684210526315788,
              0.6814714636279082
            ],
            [
              1.0368421052631582,
              0.6361615452951356
            ],
            [
              1.1052631578947372,
              0.5883974051878877
            ],
            [
              1.173684210526316,
              0.5384249232749609
            ],
            [
              1.242105263157895,
              0.4869691561913668
            ],
            [
              1.310526315789474,
              0.4352297460693704
            ],
            [
              1.378947368421053,
              0.38473536841481093
            ],
            [
              1.4473684210526319,
              0.33709359202134104
            ],
            [
              1.5157894736842108,
              0.29370591290812764
            ],
            [
              1.5842105263157897,
              0.25552792217473796
            ],
            [
              1.6526315789473687,
              0.2229379268961897
            ],
            [
              1.7210526315789476,
              0.19574066932871548
            ],
            [
              1.7894736842105265,
              0.17329037965942265
            ],
            [
              1.8578947368421055,
              0.15468475292521608
            ],
            [
              1.9263157894736844,
              0.13896879434995518
            ],
            [
              1.9947368421052634,
              0.12529623266769582
            ],
            [
              2.0631578947368423,
              0.11301964408044002
            ],
            [
              2.1315789473684212,
              0.10170776394825697
            ],
            [
              2.2,
              0.09110974644312639
            ],
            [
              2.268421052631579,
              0.08109576653223695
            ],
            [
              2.336842105263158,
              0.07160104901817166
            ],
            [
              2.405263157894737,
              0.06258993485782412
            ],
            [
              2.473684210526316,
              0.05404352039962852
            ],
            [
              2.542105263157895,
              0.0459638374927048
            ],
            [
              2.610526315789474,
              0.03838258797433014
            ],
            [
              2.6789473684210527,
              0.03136360234943002
            ],
            [
              2.7473684210526317,
              0.024993658054394217
            ],
            [
              2.8157894736842106,
              0.01936299943248075
            ],
            [
              2.8842105263157896,
              0.014541876016458158
            ],
            [
              2.9526315789473685,
              0.010560935068319009
            ],
            [
              3.0210526315789474,
              0.007401383225634351
            ],
            [
              3.0894736842105264,
              0.004996895470826814
            ],
            [
              3.1578947368421053,
              0.003245249208223617
            ],
            [
              3.2263157894736842,
              0.0020251367902929768
            ],
            [
              3.294736842105263,
              0.0012131424519801406
            ],
            [
              3.363157894736842,
              0.0006970911626177312
            ],
            [
              3.431578947368421,
              0.00038398860486955265
            ],
            [
              3.5,
              0.00020266449850595773
            ]
          ]
        },
        {
          "label": "현재 구간",
          "class": "violin-cur",
          "box_class": "box-cur",
          "x": 350,
          "low": -1.1145822713818208,
          "q1": -0.23073999200113188,
          "median": 0.5039835400777903,
          "q3": 1.1299454027315239,
          "high": 2.293494358730534,
          "mean": 0.5039835400777903,
          "density": [
            [
              -3.0,
              0.016650151037634925
            ],
            [
              -2.931578947368421,
              0.018493001038174143
            ],
            [
              -2.863157894736842,
              0.020429788890411877
            ],
            [
              -2.794736842105263,
              0.02272768091408811
            ],
            [
              -2.7263157894736842,
              0.02571392894118748
            ],
            [
              -2.6578947368421053,
              0.029704767753056027
            ],
            [
              -2.5894736842105264,
              0.034922617506800695
            ],
            [
              -2.5210526315789474,
              0.04142402278513037
            ],
            [
              -2.4526315789473685,
              0.049060577846990215
            ],
            [
              -2.3842105263157896,
              0.05748745764749403
            ],
            [
              -2.3157894736842106,
              0.06622088432847174
            ],
            [
              -2.2473684210526317,
              0.07473109308146071
            ],
            [
              -2.1789473684210527,
              0.08254643701856475
            ],
            [
              -2.110526315789474,
              0.08934161106919863
            ],
            [
              -2.042105263157895,
              0.09499002874489856
            ],
            [
              -1.9736842105263157,
              0.09957450939907096
            ],
            [
              -1.9052631578947368,
              0.10336557398416778
            ],
            [
              -1.8368421052631578,
              0.10678589670300932
            ],
            [
              -1.768421052631579,
              0.11037848698521804
            ],
            [
              -1.7,
              0.11478577055745885
            ],
            [
              -1.631578947368421,
              0.12073285559753283
            ],
            [
              -1.563157894736842,
              0.1289991537440372
            ],
            [
              -1.4947368421052631,
              0.14036418203127973
            ],
            [
              -1.4263157894736842,
              0.155525871044414
            ],
            [
              -1.3578947368421053,
              0.17500662361593605
            ],
            [
              -1.2894736842105263,
              0.1990740410839735
            ],
            [
              -1.2210526315789474,
              0.22770220871456054
            ],
            [
              -1.1526315789473685,
              0.260585022452321
            ],
            [
              -1.0842105263157895,
              0.29719216231411205
            ],
            [
              -1.0157894736842106,
              0.3368418940305425
            ],
            [
              -0.9473684210526314,
              0.37876175141962304
            ],
            [
              -0.8789473684210525,
              0.4221200442197479
            ],
            [
              -0.8105263157894735,
              0.46603164323942897
            ],
            [
              -0.7421052631578946,
              0.5095596422603305
            ],
            [
              -0.6736842105263157,
              0.5517407264654665
            ],
            [
              -0.6052631578947367,
              0.5916531604000241
            ],
            [
              -0.5368421052631578,
              0.6285265463505377
            ],
            [
              -0.46842105263157885,
              0.6618709642544282
            ],
            [
              -0.3999999999999999,
              0.6915888891528248
            ],
            [
              -0.331578947368421,
              0.7180315981141917
            ],
            [
              -0.26315789473684204,
              0.741972587240869
            ],
            [
              -0.1947368421052631,
              0.7644897495420231
            ],
            [
              -0.12631578947368416,
              0.7867700248095347
            ],
            [
              -0.05789473684210522,
              0.8098696910669246
            ],
            [
              0.010526315789473717,
              0.8344766110090005
            ],
            [
              0.07894736842105265,
              0.8607251659844865
            ],
            [
              0.1473684210526316,
              0.8881089524778323
            ],
            [
              0.21578947368421053,
              0.9155202409567758
            ],
            [
              0.28421052631578947,
              0.9414198995538069
            ],
            [
              0.3526315789473684,
              0.9641105928960311
            ],
            [
              0.42105263157894735,
              0.9820562345984736
            ],
            [
              0.4894736842105263,
              0.9941709404397225
            ],
            [
              0.5578947368421052,
              1.0
            ],
            [
              0.6263157894736842,
              0.9997384111616927
            ],
            [
              0.6947368421052631,
              0.9940761690604035
            ],
            [
              0.763157894736842,
              0.9839117299652363
            ],
            [
              0.831578947368421,
              0.9700182433737001
            ],
            [
              0.8999999999999999,
              0.9527649225640688
            ],
            [
              0.9684210526315788,
              0.9319805961972628
            ],
            [
              1.0368421052631582,
              0.907002812873648
            ],
            [
              1.1052631578947372,
              0.876899192119878
            ],
            [
              1.173684210526316,
              0.8407972774338651
            ],
            [
              1.242105263157895,
              0.7982302896897059
            ],
            [
              1.310526315789474,
              0.749405267949162
            ],
            [
              1.378947368421053,
              0.6953240529738391
            ],
            [
              1.4473684210526319,
              0.6377270950784912
            ],
            [
              1.5157894736842108,
              0.5788738020406552
            ],
            [
              1.5842105263157897,
              0.5212108157195103
            ],
            [
              1.6526315789473687,
              0.4670035085198689
            ],
            [
              1.7210526315789476,
              0.418011605398424
            ],
            [
              1.7894736842105265,
              0.37527643554832535
            ],
            [
              1.8578947368421055,
              0.3390584448187233
            ],
            [
              1.9263157894736844,
              0.30892667925566125
            ],
            [
              1.9947368421052634,
              0.2839665108498555
            ],
            [
              2.0631578947368423,
              0.2630468245083007
            ],
            [
              2.1315789473684212,
              0.24507895676999714
            ],
            [
              2.2,
              0.22920809066609713
            ],
            [
              2.268421052631579,
              0.21490038564274938
            ],
            [
              2.336842105263158,
              0.2019194346118658
            ],
            [
              2.405263157894737,
              0.19021566328933243
            ],
            [
              2.473684210526316,
              0.17977418884121643
            ],
            [
              2.542105263157895,
              0.17047467531556534
            ],
            [
              2.610526315789474,
              0.16200885907523843
            ],
            [
              2.6789473684210527,
              0.1538803328165441
            ],
            [
              2.7473684210526317,
              0.1454836943084803
            ],
            [
              2.8157894736842106,
              0.1362351632329314
            ],
            [
              2.8842105263157896,
              0.12571210979523598
            ],
            [
              2.9526315789473685,
              0.11375867501925946
            ],
            [
              3.0210526315789474,
              0.10052773296153204
            ],
            [
              3.0894736842105264,
              0.08645039785094505
            ],
            [
              3.1578947368421053,
              0.07214561422517056
            ],
            [
              3.2263157894736842,
              0.058297395415646734
            ],
            [
              3.294736842105263,
              0.04553230037765388
            ],
            [
              3.363157894736842,
              0.0343248394857379
            ],
            [
              3.431578947368421,
              0.02494685411955341
            ],
            [
              3.5,
              0.017463188028312402
            ]
          ]
        }
      ],
      "chart.CHART-RANK-001.rank": [
        {
          "label": "1",
          "reference": 26,
          "current": 11,
          "balance": 8.027027027027028
        },
        {
          "label": "2",
          "reference": 26,
          "current": 11,
          "balance": 8.027027027027028
        },
        {
          "label": "3",
          "reference": 20,
          "current": 16,
          "balance": 12.0
        },
        {
          "label": "4",
          "reference": 23,
          "current": 14,
          "balance": 10.216216216216218
        },
        {
          "label": "5",
          "reference": 18,
          "current": 19,
          "balance": 13.864864864864865
        },
        {
          "label": "6",
          "reference": 21,
          "current": 15,
          "balance": 11.25
        },
        {
          "label": "7",
          "reference": 20,
          "current": 17,
          "balance": 12.405405405405405
        },
        {
          "label": "8",
          "reference": 14,
          "current": 23,
          "balance": 16.783783783783782
        },
        {
          "label": "9",
          "reference": 16,
          "current": 20,
          "balance": 15.0
        },
        {
          "label": "10",
          "reference": 16,
          "current": 21,
          "balance": 15.324324324324323
        },
        {
          "label": "11",
          "reference": 10,
          "current": 27,
          "balance": 19.7027027027027
        },
        {
          "label": "12",
          "reference": 10,
          "current": 26,
          "balance": 19.5
        }
      ],
      "chart.CHART-RANK-001.notes": [
        {
          "title": "해석",
          "text": "이 예시에서는 Mann-Whitney U가 31,551이고 순위 AUC가 0.652다. 현재 중앙값은 0.50으로 기준 중앙값 -0.07보다 0.57 높고, 현재 구간 막대도 높은 순위 쪽에 더 많이 분포한다. 따라서 rank 기반 위치 이동 후보로 해석하되, 평균 변화나 모델 성능 저하는 별도 검증해야 한다.",
          "legend": [
            {
              "label": "기준 구간",
              "class": "swatch-reference"
            },
            {
              "label": "현재 구간",
              "class": "swatch-current-red"
            },
            {
              "label": "중앙값",
              "class": "swatch-threshold-line"
            },
            {
              "label": "순위 밀도",
              "class": "swatch-overlap"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-REP-001",
    "title": "CHART-REP-001 - block3 활성 변화로 본 표현 드리프트",
    "originalPath": "./drift_report_charts/chart_rep_001.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "chart_rep_001_source",
      "displayName": "CHART-REP-001 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 112px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "레이어별 드리프트 히트맵",
          "description": "block3 c6~c9가 0.81, 0.88, 0.92, 0.84로 높은지 확인한다.",
          "headerHeight": 76,
          "stageInset": {
            "top": 84,
            "right": 16,
            "bottom": -8,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "활성값 분포",
          "description": "baseline peak는 bin 5의 35, current peak는 bin 7의 34로 오른쪽 이동한다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "레이어별 임베딩 투영",
          "description": "baseline cluster는 왼쪽, current cluster는 오른쪽으로 분리된다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "notes",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-REP-001.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 1,
        "config": {},
        "dataBinding": {
          "source": "chart.CHART-REP-001.summary"
        }
      },
      {
        "componentInstanceId": "CHART-REP-001.heatmap.0",
        "componentType": "matrix_view",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "matrix_style": "heatmap_grid",
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 30,
            "right": 28,
            "bottom": 72,
            "left": 78
          },
          "x_values": [
            "c1",
            "c2",
            "c3",
            "c4",
            "c5",
            "c6",
            "c7",
            "c8",
            "c9",
            "c10",
            "c11",
            "c12"
          ],
          "y_values": [
            "conv1",
            "block1",
            "block2",
            "block3",
            "head"
          ],
          "values_field": "values",
          "value_min": 0,
          "value_max": 1,
          "show_x_labels": true,
          "x_labels": [
            "c1",
            "",
            "",
            "c4",
            "",
            "",
            "",
            "c8",
            "",
            "",
            "",
            "c12"
          ],
          "show_y_labels": true,
          "show_cell_values": true,
          "cell_value_min": 0.8,
          "row_highlights": [
            {
              "row": "block3",
              "class": "layer-ring",
              "rx": 3
            }
          ],
          "x_axis_label": "channel index",
          "y_axis_label": "layer",
          "annotations": [
            {
              "text": "block3 channels show concentrated drift",
              "x": "c7",
              "y": 1.06,
              "class": "warning-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-REP-001.heatmap"
        }
      },
      {
        "componentInstanceId": "CHART-REP-001.activation.0",
        "componentType": "bar_chart",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "vertical_grouped",
          "category_field": "bin",
          "series_fields": [
            "baseline",
            "current"
          ],
          "series_classes": [
            "base-bar",
            "rep-current-bar"
          ],
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 24,
            "bottom": 34,
            "left": 44
          },
          "y_max": 40,
          "y_ticks": [
            0,
            20,
            40
          ],
          "label_every": 0,
          "x_axis_label": "activation bin",
          "axis_label_x": 204,
          "axis_label_y": 177,
          "annotations": [
            {
              "text": "current activation shifts right",
              "x": 245,
              "y": 28,
              "class": "warning-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-REP-001.activation"
        }
      },
      {
        "componentInstanceId": "CHART-REP-001.projection.0",
        "componentType": "projection_scatter",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 24,
            "bottom": 34,
            "left": 44
          },
          "x_min": -2.2,
          "x_max": 2.8,
          "y_min": -1.8,
          "y_max": 1.8,
          "x_ticks": [],
          "y_ticks": [],
          "group_class_map": {
            "baseline": "base-dot",
            "current": "rep-current-dot"
          },
          "point_radius": 4,
          "x_axis_label": "UMAP-1",
          "axis_label_x": 204,
          "axis_label_y": 177,
          "annotations": [
            {
              "text": "layer embedding separates",
              "x": 0.78,
              "y": 1.52,
              "class": "callout"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-REP-001.projection"
        }
      },
      {
        "componentInstanceId": "CHART-REP-001.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 1,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-REP-001.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-REP-001.summary": [
        {
          "label": "max drift",
          "displayValue": "0.92"
        },
        {
          "label": "hot layer",
          "displayValue": "block3"
        },
        {
          "label": "method",
          "displayValue": "MMD/KS"
        }
      ],
      "chart.CHART-REP-001.heatmap": [
        {
          "layer": "conv1",
          "values": [
            0.12,
            0.18,
            0.16,
            0.2,
            0.24,
            0.22,
            0.19,
            0.25,
            0.28,
            0.21,
            0.18,
            0.16
          ]
        },
        {
          "layer": "block1",
          "values": [
            0.2,
            0.24,
            0.27,
            0.3,
            0.33,
            0.29,
            0.31,
            0.35,
            0.38,
            0.34,
            0.3,
            0.28
          ]
        },
        {
          "layer": "block2",
          "values": [
            0.31,
            0.36,
            0.42,
            0.48,
            0.54,
            0.57,
            0.62,
            0.66,
            0.59,
            0.52,
            0.45,
            0.4
          ]
        },
        {
          "layer": "block3",
          "values": [
            0.42,
            0.5,
            0.58,
            0.66,
            0.74,
            0.81,
            0.88,
            0.92,
            0.84,
            0.76,
            0.68,
            0.56
          ]
        },
        {
          "layer": "head",
          "values": [
            0.28,
            0.33,
            0.38,
            0.44,
            0.49,
            0.52,
            0.55,
            0.58,
            0.53,
            0.47,
            0.4,
            0.35
          ]
        }
      ],
      "chart.CHART-REP-001.activation": [
        {
          "bin": "1",
          "baseline": 4,
          "current": 2
        },
        {
          "bin": "2",
          "baseline": 9,
          "current": 5
        },
        {
          "bin": "3",
          "baseline": 16,
          "current": 9
        },
        {
          "bin": "4",
          "baseline": 28,
          "current": 16
        },
        {
          "bin": "5",
          "baseline": 35,
          "current": 24
        },
        {
          "bin": "6",
          "baseline": 31,
          "current": 31
        },
        {
          "bin": "7",
          "baseline": 22,
          "current": 34
        },
        {
          "bin": "8",
          "baseline": 13,
          "current": 27
        },
        {
          "bin": "9",
          "baseline": 7,
          "current": 18
        },
        {
          "bin": "10",
          "baseline": 3,
          "current": 9
        }
      ],
      "chart.CHART-REP-001.projection": [
        {
          "x": -1.35,
          "y": -0.27,
          "group": "baseline"
        },
        {
          "x": 0.82,
          "y": 0.23,
          "group": "current"
        },
        {
          "x": -1.093,
          "y": -0.36,
          "group": "baseline"
        },
        {
          "x": 1.107,
          "y": 0.164,
          "group": "current"
        },
        {
          "x": -0.897,
          "y": -0.427,
          "group": "baseline"
        },
        {
          "x": 1.281,
          "y": 0.075,
          "group": "current"
        },
        {
          "x": -0.769,
          "y": -0.32,
          "group": "baseline"
        },
        {
          "x": 1.395,
          "y": 0.111,
          "group": "current"
        },
        {
          "x": -0.651,
          "y": -0.28,
          "group": "baseline"
        },
        {
          "x": 1.589,
          "y": 0.212,
          "group": "current"
        },
        {
          "x": -0.477,
          "y": -0.398,
          "group": "baseline"
        },
        {
          "x": 1.887,
          "y": 0.21,
          "group": "current"
        },
        {
          "x": -0.232,
          "y": -0.407,
          "group": "baseline"
        },
        {
          "x": 2.16,
          "y": 0.108,
          "group": "current"
        },
        {
          "x": -1.297,
          "y": -0.117,
          "group": "baseline"
        },
        {
          "x": 0.846,
          "y": 0.256,
          "group": "current"
        },
        {
          "x": -1.081,
          "y": -0.139,
          "group": "baseline"
        },
        {
          "x": 0.964,
          "y": 0.346,
          "group": "current"
        },
        {
          "x": -0.937,
          "y": -0.253,
          "group": "baseline"
        },
        {
          "x": 1.179,
          "y": 0.41,
          "group": "current"
        },
        {
          "x": -0.824,
          "y": -0.202,
          "group": "baseline"
        },
        {
          "x": 1.484,
          "y": 0.341,
          "group": "current"
        },
        {
          "x": -0.67,
          "y": -0.101,
          "group": "baseline"
        },
        {
          "x": 1.739,
          "y": 0.254,
          "group": "current"
        },
        {
          "x": -0.443,
          "y": -0.178,
          "group": "baseline"
        },
        {
          "x": 1.879,
          "y": 0.293,
          "group": "current"
        },
        {
          "x": -0.176,
          "y": -0.26,
          "group": "baseline"
        },
        {
          "x": 2.006,
          "y": 0.394,
          "group": "current"
        },
        {
          "x": -1.271,
          "y": 0.009,
          "group": "baseline"
        },
        {
          "x": 0.772,
          "y": 0.569,
          "group": "current"
        },
        {
          "x": -1.108,
          "y": 0.065,
          "group": "baseline"
        },
        {
          "x": 1.078,
          "y": 0.466,
          "group": "current"
        },
        {
          "x": -0.993,
          "y": -0.048,
          "group": "baseline"
        },
        {
          "x": 1.314,
          "y": 0.437,
          "group": "current"
        },
        {
          "x": -0.857,
          "y": -0.075,
          "group": "baseline"
        },
        {
          "x": 1.441,
          "y": 0.529,
          "group": "current"
        },
        {
          "x": -0.65,
          "y": 0.045,
          "group": "baseline"
        },
        {
          "x": 1.581,
          "y": 0.59,
          "group": "current"
        },
        {
          "x": -0.388,
          "y": 0.041,
          "group": "baseline"
        },
        {
          "x": 1.836,
          "y": 0.518,
          "group": "current"
        },
        {
          "x": -0.137,
          "y": -0.078,
          "group": "baseline"
        },
        {
          "x": 2.141,
          "y": 0.433,
          "group": "current"
        },
        {
          "x": -1.283,
          "y": 0.127,
          "group": "baseline"
        },
        {
          "x": 0.886,
          "y": 0.656,
          "group": "current"
        },
        {
          "x": -1.161,
          "y": 0.236,
          "group": "baseline"
        },
        {
          "x": 1.004,
          "y": 0.755,
          "group": "current"
        },
        {
          "x": -1.038,
          "y": 0.174,
          "group": "baseline"
        },
        {
          "x": 1.16,
          "y": 0.747,
          "group": "current"
        },
        {
          "x": -0.852,
          "y": 0.08,
          "group": "baseline"
        },
        {
          "x": 1.433,
          "y": 0.644,
          "group": "current"
        },
        {
          "x": -0.601,
          "y": 0.167,
          "group": "baseline"
        },
        {
          "x": 1.731,
          "y": 0.618,
          "group": "current"
        },
        {
          "x": -0.339,
          "y": 0.238,
          "group": "baseline"
        },
        {
          "x": 1.925,
          "y": 0.711,
          "group": "current"
        },
        {
          "x": -0.133,
          "y": 0.133,
          "group": "baseline"
        },
        {
          "x": 2.039,
          "y": 0.77,
          "group": "current"
        },
        {
          "x": -1.328,
          "y": 0.259,
          "group": "baseline"
        },
        {
          "x": 0.743,
          "y": 0.876,
          "group": "current"
        },
        {
          "x": -1.213,
          "y": 0.376,
          "group": "baseline"
        },
        {
          "x": 1.03,
          "y": 0.792,
          "group": "current"
        },
        {
          "x": -1.049,
          "y": 0.389,
          "group": "baseline"
        },
        {
          "x": 1.317,
          "y": 0.838,
          "group": "current"
        },
        {
          "x": -0.812,
          "y": 0.269,
          "group": "baseline"
        },
        {
          "x": 1.491,
          "y": 0.937,
          "group": "current"
        },
        {
          "x": -0.546,
          "y": 0.286,
          "group": "baseline"
        },
        {
          "x": 1.605,
          "y": 0.925,
          "group": "current"
        },
        {
          "x": -0.32,
          "y": 0.402,
          "group": "baseline"
        },
        {
          "x": 1.799,
          "y": 0.822,
          "group": "current"
        }
      ],
      "chart.CHART-REP-001.notes": [
        {
          "title": "해석",
          "text": "Feature map drift는 모델 내부 layer activation의 분포 변화가 특정 layer와 channel에 집중되는지 확인한다. 이 예시에서는 block3 c8의 drift score가 0.92이고 activation peak와 embedding도 오른쪽으로 이동해 block3 representation-level drift 후보로 해석한다.",
          "legend": [
            {
              "label": "baseline",
              "class": "swatch-base"
            },
            {
              "label": "current",
              "class": "swatch-current-red"
            },
            {
              "label": "high drift",
              "class": "swatch-high"
            },
            {
              "label": "selected layer",
              "class": "swatch-layer"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-REP-002",
    "title": "CHART-REP-002 - 복원 오차 증가로 본 오토인코더 표현 드리프트",
    "originalPath": "./drift_report_charts/chart_rep_002.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "chart_rep_002_source",
      "displayName": "CHART-REP-002 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 112px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "복원 오차 분포",
          "description": "baseline peak는 0.14/38, current peak는 0.26/37로 오른쪽 이동한다.",
          "headerHeight": 76,
          "stageInset": {
            "top": 84,
            "right": 16,
            "bottom": -8,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "임계값 포함 오류 추세",
          "description": "trend가 t=23에서 threshold 0.36을 넘어 t=32의 0.54까지 상승한다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "잠재공간 투영 산점도",
          "description": "baseline cluster는 왼쪽, current cluster는 오른쪽으로 분리된다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "notes",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-REP-002.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 1,
        "config": {},
        "dataBinding": {
          "source": "chart.CHART-REP-002.summary"
        }
      },
      {
        "componentInstanceId": "CHART-REP-002.distribution.0",
        "componentType": "distribution_view",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "distribution_style": "density_area",
          "x_field": "x",
          "primary_value_field": "baseline",
          "secondary_value_field": "current",
          "primary_area_class": "base-area",
          "secondary_area_class": "rep-current-area",
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 28,
            "bottom": 62,
            "left": 58
          },
          "x_min": 0.02,
          "x_max": 0.42,
          "y_min": 0,
          "y_max": 42,
          "x_ticks": [
            0.05,
            0.15,
            0.25,
            0.35
          ],
          "y_ticks": [
            0,
            10,
            20,
            30,
            40
          ],
          "x_axis_label": "reconstruction error",
          "y_axis_label": "density",
          "vertical_markers": [
            {
              "x": 0.36,
              "class": "threshold-line",
              "label": "threshold 0.36",
              "label_y": 34
            }
          ],
          "annotations": [
            {
              "text": "current error distribution shifts right",
              "x": 0.19,
              "y": 39,
              "class": "warning-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-REP-002.distribution"
        }
      },
      {
        "componentInstanceId": "CHART-REP-002.trend.0",
        "componentType": "trend_line",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "time",
          "y_field": "value",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 22,
            "bottom": 34,
            "left": 48
          },
          "x_min": 1,
          "x_max": 32,
          "y_min": 0.05,
          "y_max": 0.58,
          "y_ticks": [
            0.1,
            0.3,
            0.5
          ],
          "x_ticks": [],
          "x_axis_label": "time index",
          "axis_label_x": 208,
          "axis_label_y": 177,
          "y_axis_label": false,
          "line_class": "rep-trend-line",
          "show_points": false,
          "horizontal_markers": [
            {
              "y": 0.36,
              "class": "threshold-line"
            }
          ],
          "point_highlights": [
            {
              "x": 1,
              "class": "trend-point",
              "r": 3.4
            },
            {
              "x": 5,
              "class": "trend-point",
              "r": 3.4
            },
            {
              "x": 9,
              "class": "trend-point",
              "r": 3.4
            },
            {
              "x": 13,
              "class": "trend-point",
              "r": 3.4
            },
            {
              "x": 17,
              "class": "trend-point",
              "r": 3.4
            },
            {
              "x": 21,
              "class": "trend-point",
              "r": 3.4
            },
            {
              "x": 23,
              "class": "alarm-point",
              "r": 4.8
            },
            {
              "x": 24,
              "class": "alarm-point",
              "r": 4.8
            },
            {
              "x": 28,
              "class": "alarm-point",
              "r": 4.8
            },
            {
              "x": 32,
              "class": "alarm-point",
              "r": 4.8
            }
          ],
          "annotations": [
            {
              "text": "threshold exceeded",
              "x": 21,
              "y": 0.52,
              "class": "warning-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-REP-002.trend"
        }
      },
      {
        "componentInstanceId": "CHART-REP-002.latent.0",
        "componentType": "projection_scatter",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 24,
            "bottom": 34,
            "left": 44
          },
          "x_min": -2.4,
          "x_max": 3.0,
          "y_min": -1.8,
          "y_max": 1.8,
          "x_ticks": [],
          "y_ticks": [],
          "group_class_map": {
            "baseline": "base-dot",
            "current": "rep-current-dot"
          },
          "point_radius": 4,
          "x_axis_label": "latent-1",
          "axis_label_x": 204,
          "axis_label_y": 177,
          "annotations": [
            {
              "text": "latent clusters separate",
              "x": 0.78,
              "y": 1.48,
              "class": "callout"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-REP-002.latent"
        }
      },
      {
        "componentInstanceId": "CHART-REP-002.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 1,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-REP-002.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-REP-002.summary": [
        {
          "label": "p95 error",
          "displayValue": "0.51"
        },
        {
          "label": "threshold",
          "displayValue": "0.36"
        },
        {
          "label": "latent AUC",
          "displayValue": "0.84"
        }
      ],
      "chart.CHART-REP-002.distribution": [
        {
          "x": 0.02,
          "baseline": 3,
          "current": 0
        },
        {
          "x": 0.05,
          "baseline": 9,
          "current": 1
        },
        {
          "x": 0.08,
          "baseline": 18,
          "current": 3
        },
        {
          "x": 0.11,
          "baseline": 31,
          "current": 7
        },
        {
          "x": 0.14,
          "baseline": 38,
          "current": 12
        },
        {
          "x": 0.17,
          "baseline": 34,
          "current": 18
        },
        {
          "x": 0.2,
          "baseline": 25,
          "current": 26
        },
        {
          "x": 0.23,
          "baseline": 15,
          "current": 33
        },
        {
          "x": 0.26,
          "baseline": 8,
          "current": 37
        },
        {
          "x": 0.29,
          "baseline": 4,
          "current": 34
        },
        {
          "x": 0.32,
          "baseline": 2,
          "current": 26
        },
        {
          "x": 0.35,
          "baseline": 1,
          "current": 17
        },
        {
          "x": 0.38,
          "baseline": 0,
          "current": 9
        },
        {
          "x": 0.41,
          "baseline": 0,
          "current": 4
        }
      ],
      "chart.CHART-REP-002.trend": [
        {
          "time": 1,
          "value": 0.1
        },
        {
          "time": 2,
          "value": 0.11
        },
        {
          "time": 3,
          "value": 0.1
        },
        {
          "time": 4,
          "value": 0.12
        },
        {
          "time": 5,
          "value": 0.13
        },
        {
          "time": 6,
          "value": 0.12
        },
        {
          "time": 7,
          "value": 0.14
        },
        {
          "time": 8,
          "value": 0.15
        },
        {
          "time": 9,
          "value": 0.16
        },
        {
          "time": 10,
          "value": 0.17
        },
        {
          "time": 11,
          "value": 0.18
        },
        {
          "time": 12,
          "value": 0.19
        },
        {
          "time": 13,
          "value": 0.21
        },
        {
          "time": 14,
          "value": 0.22
        },
        {
          "time": 15,
          "value": 0.24
        },
        {
          "time": 16,
          "value": 0.25
        },
        {
          "time": 17,
          "value": 0.27
        },
        {
          "time": 18,
          "value": 0.28
        },
        {
          "time": 19,
          "value": 0.3
        },
        {
          "time": 20,
          "value": 0.31
        },
        {
          "time": 21,
          "value": 0.33
        },
        {
          "time": 22,
          "value": 0.35
        },
        {
          "time": 23,
          "value": 0.37
        },
        {
          "time": 24,
          "value": 0.39
        },
        {
          "time": 25,
          "value": 0.42
        },
        {
          "time": 26,
          "value": 0.44
        },
        {
          "time": 27,
          "value": 0.46
        },
        {
          "time": 28,
          "value": 0.47
        },
        {
          "time": 29,
          "value": 0.49
        },
        {
          "time": 30,
          "value": 0.51
        },
        {
          "time": 31,
          "value": 0.52
        },
        {
          "time": 32,
          "value": 0.54
        }
      ],
      "chart.CHART-REP-002.latent": [
        {
          "x": -1.25,
          "y": -0.11,
          "group": "baseline"
        },
        {
          "x": 0.86,
          "y": 0.3,
          "group": "current"
        },
        {
          "x": -0.991,
          "y": -0.175,
          "group": "baseline"
        },
        {
          "x": 1.209,
          "y": 0.249,
          "group": "current"
        },
        {
          "x": -0.786,
          "y": -0.249,
          "group": "baseline"
        },
        {
          "x": 1.41,
          "y": 0.161,
          "group": "current"
        },
        {
          "x": -0.64,
          "y": -0.195,
          "group": "baseline"
        },
        {
          "x": 1.562,
          "y": 0.148,
          "group": "current"
        },
        {
          "x": -0.503,
          "y": -0.113,
          "group": "baseline"
        },
        {
          "x": 1.843,
          "y": 0.227,
          "group": "current"
        },
        {
          "x": -0.317,
          "y": -0.156,
          "group": "baseline"
        },
        {
          "x": 2.219,
          "y": 0.297,
          "group": "current"
        },
        {
          "x": -1.27,
          "y": -0.104,
          "group": "baseline"
        },
        {
          "x": 0.937,
          "y": 0.419,
          "group": "current"
        },
        {
          "x": -1.004,
          "y": -0.073,
          "group": "baseline"
        },
        {
          "x": 1.087,
          "y": 0.328,
          "group": "current"
        },
        {
          "x": -0.781,
          "y": 0.019,
          "group": "baseline"
        },
        {
          "x": 1.292,
          "y": 0.291,
          "group": "current"
        },
        {
          "x": -0.621,
          "y": 0.002,
          "group": "baseline"
        },
        {
          "x": 1.643,
          "y": 0.354,
          "group": "current"
        },
        {
          "x": -0.488,
          "y": -0.093,
          "group": "baseline"
        },
        {
          "x": 1.989,
          "y": 0.438,
          "group": "current"
        },
        {
          "x": -0.32,
          "y": -0.089,
          "group": "baseline"
        },
        {
          "x": 2.187,
          "y": 0.434,
          "group": "current"
        },
        {
          "x": -1.288,
          "y": 0.146,
          "group": "baseline"
        },
        {
          "x": 0.78,
          "y": 0.499,
          "group": "current"
        },
        {
          "x": -1.021,
          "y": 0.156,
          "group": "baseline"
        },
        {
          "x": 1.066,
          "y": 0.44,
          "group": "current"
        },
        {
          "x": -0.781,
          "y": 0.062,
          "group": "baseline"
        },
        {
          "x": 1.441,
          "y": 0.483,
          "group": "current"
        },
        {
          "x": -0.604,
          "y": 0.039,
          "group": "baseline"
        },
        {
          "x": 1.715,
          "y": 0.573,
          "group": "current"
        },
        {
          "x": -0.47,
          "y": 0.13,
          "group": "baseline"
        },
        {
          "x": 1.864,
          "y": 0.595,
          "group": "current"
        },
        {
          "x": -0.317,
          "y": 0.165,
          "group": "baseline"
        },
        {
          "x": 2.073,
          "y": 0.522,
          "group": "current"
        },
        {
          "x": -1.303,
          "y": 0.22,
          "group": "baseline"
        },
        {
          "x": 0.866,
          "y": 0.596,
          "group": "current"
        },
        {
          "x": -1.04,
          "y": 0.172,
          "group": "baseline"
        },
        {
          "x": 1.21,
          "y": 0.615,
          "group": "current"
        },
        {
          "x": -0.786,
          "y": 0.251,
          "group": "baseline"
        },
        {
          "x": 1.404,
          "y": 0.704,
          "group": "current"
        },
        {
          "x": -0.591,
          "y": 0.31,
          "group": "baseline"
        },
        {
          "x": 1.559,
          "y": 0.75,
          "group": "current"
        },
        {
          "x": -0.451,
          "y": 0.239,
          "group": "baseline"
        },
        {
          "x": 1.848,
          "y": 0.694,
          "group": "current"
        },
        {
          "x": -0.309,
          "y": 0.17,
          "group": "baseline"
        },
        {
          "x": 2.224,
          "y": 0.608,
          "group": "current"
        },
        {
          "x": -1.313,
          "y": 0.371,
          "group": "baseline"
        },
        {
          "x": 0.934,
          "y": 0.751,
          "group": "current"
        },
        {
          "x": -1.059,
          "y": 0.449,
          "group": "baseline"
        },
        {
          "x": 1.081,
          "y": 0.832,
          "group": "current"
        },
        {
          "x": -0.797,
          "y": 0.399,
          "group": "baseline"
        },
        {
          "x": 1.293,
          "y": 0.898,
          "group": "current"
        },
        {
          "x": -0.583,
          "y": 0.314,
          "group": "baseline"
        },
        {
          "x": 1.649,
          "y": 0.864,
          "group": "current"
        },
        {
          "x": -0.431,
          "y": 0.352,
          "group": "baseline"
        },
        {
          "x": 1.99,
          "y": 0.774,
          "group": "current"
        },
        {
          "x": -0.296,
          "y": 0.442,
          "group": "baseline"
        },
        {
          "x": 2.181,
          "y": 0.742,
          "group": "current"
        },
        {
          "x": -1.319,
          "y": 0.557,
          "group": "baseline"
        },
        {
          "x": 0.778,
          "y": 0.96,
          "group": "current"
        },
        {
          "x": -1.078,
          "y": 0.463,
          "group": "baseline"
        },
        {
          "x": 1.071,
          "y": 1.04,
          "group": "current"
        },
        {
          "x": -0.811,
          "y": 0.475,
          "group": "baseline"
        },
        {
          "x": 1.446,
          "y": 1.031,
          "group": "current"
        },
        {
          "x": -0.58,
          "y": 0.57,
          "group": "baseline"
        },
        {
          "x": 1.712,
          "y": 0.944,
          "group": "current"
        },
        {
          "x": -0.413,
          "y": 0.572,
          "group": "baseline"
        },
        {
          "x": 1.859,
          "y": 0.89,
          "group": "current"
        },
        {
          "x": -0.28,
          "y": 0.477,
          "group": "baseline"
        },
        {
          "x": 2.074,
          "y": 0.938,
          "group": "current"
        }
      ],
      "chart.CHART-REP-002.notes": [
        {
          "title": "해석",
          "text": "Autoencoder representation drift는 reconstruction error와 latent space 변화를 함께 본다. 이 예시에서는 p95 error 0.51이 threshold 0.36을 넘고 latent AUC도 0.84로 나타나 autoencoder representation drift 후보로 해석한다.",
          "legend": [
            {
              "label": "baseline",
              "class": "swatch-base"
            },
            {
              "label": "current",
              "class": "swatch-current-red"
            },
            {
              "label": "threshold",
              "class": "swatch-threshold"
            },
            {
              "label": "latent drift",
              "class": "swatch-layer"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-REP-003",
    "title": "CHART-REP-003 - 그래프 임베딩 분리와 허브 노드 드리프트",
    "originalPath": "./drift_report_charts/chart_rep_003.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "chart_rep_003_source",
      "displayName": "CHART-REP-003 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 112px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "그래프 임베딩 투영",
          "description": "baseline cluster는 왼쪽, current cluster는 오른쪽으로 분리된다.",
          "headerHeight": 76,
          "stageInset": {
            "top": 84,
            "right": 16,
            "bottom": -8,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "노드 드리프트 점수 히트맵",
          "description": "hub는 0.70, bridge는 0.66까지 올라 후반 구간에 drift가 집중된다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "그래프 수준 거리 추세",
          "description": "distance가 t=15에서 0.40 threshold를 넘고 최종 0.67까지 상승한다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "notes",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-REP-003.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 1,
        "config": {},
        "dataBinding": {
          "source": "chart.CHART-REP-003.summary"
        }
      },
      {
        "componentInstanceId": "CHART-REP-003.projection.0",
        "componentType": "projection_scatter",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 28,
            "bottom": 62,
            "left": 58
          },
          "x_min": -2.4,
          "x_max": 3.2,
          "y_min": -1.8,
          "y_max": 1.9,
          "x_ticks": [],
          "y_ticks": [
            -1,
            0,
            1
          ],
          "group_class_map": {
            "baseline": "base-dot",
            "current": "current-dot",
            "bridge": "bridge-dot"
          },
          "group_radius_map": {
            "bridge": 5
          },
          "point_radius": 4,
          "x_axis_label": "embedding projection-1",
          "y_axis_label": "embedding projection-2",
          "annotations": [
            {
              "text": "current graph embeddings separate from baseline",
              "x": -0.08,
              "y": 1.58,
              "class": "callout"
            },
            {
              "text": "bridge nodes high drift",
              "x": 1.42,
              "y": 1.18,
              "class": "warning-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-REP-003.projection"
        }
      },
      {
        "componentInstanceId": "CHART-REP-003.heatmap.0",
        "componentType": "matrix_view",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "matrix_style": "heatmap_grid",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 20,
            "right": 66,
            "bottom": 34,
            "left": 70
          },
          "x_values": [
            "t1",
            "t2",
            "t3",
            "t4",
            "t5",
            "t6"
          ],
          "y_values": [
            "core",
            "hub",
            "bridge",
            "leaf",
            "new"
          ],
          "values_field": "values",
          "value_min": 0,
          "value_max": 0.75,
          "palette": [
            [
              0,
              "#d9e6ef"
            ],
            [
              0.45,
              "#c9952f"
            ],
            [
              1,
              "#b95a50"
            ]
          ],
          "show_x_labels": true,
          "show_y_labels": true,
          "show_cell_values": true,
          "cell_value_min": 0.55,
          "x_axis_label": "node group drift score",
          "axis_label_x": 234,
          "axis_label_y": 181
        },
        "dataBinding": {
          "source": "chart.CHART-REP-003.heatmap"
        }
      },
      {
        "componentInstanceId": "CHART-REP-003.distance.0",
        "componentType": "distance_metric_view",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "time",
          "y_field": "value",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 22,
            "bottom": 34,
            "left": 48
          },
          "x_min": 1,
          "x_max": 24,
          "y_min": 0,
          "y_max": 0.75,
          "y_ticks": [
            0,
            0.3,
            0.6
          ],
          "x_ticks": [],
          "x_axis_label": "graph-level distance",
          "axis_label_x": 208,
          "axis_label_y": 177,
          "y_axis_label": false,
          "line_class": "rep-distance-line",
          "show_points": false,
          "horizontal_markers": [
            {
              "y": 0.4,
              "class": "threshold-line"
            }
          ],
          "point_highlights": [
            {
              "x": 1,
              "class": "distance-point",
              "r": 3.4
            },
            {
              "x": 4,
              "class": "distance-point",
              "r": 3.4
            },
            {
              "x": 7,
              "class": "distance-point",
              "r": 3.4
            },
            {
              "x": 10,
              "class": "distance-point",
              "r": 3.4
            },
            {
              "x": 13,
              "class": "distance-point",
              "r": 3.4
            },
            {
              "x": 15,
              "class": "distance-point",
              "r": 4.8
            },
            {
              "x": 16,
              "class": "distance-point",
              "r": 4.8
            },
            {
              "x": 18,
              "class": "distance-point",
              "r": 4.8
            },
            {
              "x": 20,
              "class": "distance-point",
              "r": 4.8
            },
            {
              "x": 22,
              "class": "distance-point",
              "r": 4.8
            },
            {
              "x": 24,
              "class": "distance-point",
              "r": 4.8
            }
          ],
          "annotations": [
            {
              "text": "threshold crossed",
              "x": 13,
              "y": 0.62,
              "class": "warning-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-REP-003.distance"
        }
      },
      {
        "componentInstanceId": "CHART-REP-003.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 1,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-REP-003.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-REP-003.summary": [
        {
          "label": "distance",
          "displayValue": "0.67"
        },
        {
          "label": "node max",
          "displayValue": "0.70"
        },
        {
          "label": "alarm",
          "displayValue": "t=15"
        }
      ],
      "chart.CHART-REP-003.projection": [
        {
          "x": -1.45,
          "y": -0.4,
          "group": "baseline"
        },
        {
          "x": -1.199,
          "y": -0.437,
          "group": "baseline"
        },
        {
          "x": -1.025,
          "y": -0.513,
          "group": "baseline"
        },
        {
          "x": -0.923,
          "y": -0.559,
          "group": "baseline"
        },
        {
          "x": -0.806,
          "y": -0.532,
          "group": "baseline"
        },
        {
          "x": -0.606,
          "y": -0.457,
          "group": "baseline"
        },
        {
          "x": -0.345,
          "y": -0.403,
          "group": "baseline"
        },
        {
          "x": -1.371,
          "y": -0.24,
          "group": "baseline"
        },
        {
          "x": -1.223,
          "y": -0.312,
          "group": "baseline"
        },
        {
          "x": -1.127,
          "y": -0.373,
          "group": "baseline"
        },
        {
          "x": -0.99,
          "y": -0.367,
          "group": "baseline"
        },
        {
          "x": -0.766,
          "y": -0.3,
          "group": "baseline"
        },
        {
          "x": -0.503,
          "y": -0.232,
          "group": "baseline"
        },
        {
          "x": -0.291,
          "y": -0.227,
          "group": "baseline"
        },
        {
          "x": -1.426,
          "y": -0.109,
          "group": "baseline"
        },
        {
          "x": -1.327,
          "y": -0.181,
          "group": "baseline"
        },
        {
          "x": -1.166,
          "y": -0.197,
          "group": "baseline"
        },
        {
          "x": -0.922,
          "y": -0.142,
          "group": "baseline"
        },
        {
          "x": -0.665,
          "y": -0.067,
          "group": "baseline"
        },
        {
          "x": -0.479,
          "y": -0.041,
          "group": "baseline"
        },
        {
          "x": -0.371,
          "y": -0.087,
          "group": "baseline"
        },
        {
          "x": -1.522,
          "y": 0.016,
          "group": "baseline"
        },
        {
          "x": -1.334,
          "y": -0.02,
          "group": "baseline"
        },
        {
          "x": -1.077,
          "y": 0.017,
          "group": "baseline"
        },
        {
          "x": -0.834,
          "y": 0.094,
          "group": "baseline"
        },
        {
          "x": -0.674,
          "y": 0.139,
          "group": "baseline"
        },
        {
          "x": -0.576,
          "y": 0.112,
          "group": "baseline"
        },
        {
          "x": -0.449,
          "y": 0.037,
          "group": "baseline"
        },
        {
          "x": -1.496,
          "y": 0.163,
          "group": "baseline"
        },
        {
          "x": -1.233,
          "y": 0.18,
          "group": "baseline"
        },
        {
          "x": -1.01,
          "y": 0.252,
          "group": "baseline"
        },
        {
          "x": -0.875,
          "y": 0.313,
          "group": "baseline"
        },
        {
          "x": -0.778,
          "y": 0.307,
          "group": "baseline"
        },
        {
          "x": -0.629,
          "y": 0.239,
          "group": "baseline"
        },
        {
          "x": -0.394,
          "y": 0.172,
          "group": "baseline"
        },
        {
          "x": -1.393,
          "y": 0.348,
          "group": "baseline"
        },
        {
          "x": -1.194,
          "y": 0.41,
          "group": "baseline"
        },
        {
          "x": -1.079,
          "y": 0.481,
          "group": "baseline"
        },
        {
          "x": -0.976,
          "y": 0.496,
          "group": "baseline"
        },
        {
          "x": -0.801,
          "y": 0.441,
          "group": "baseline"
        },
        {
          "x": -0.549,
          "y": 0.367,
          "group": "baseline"
        },
        {
          "x": -0.298,
          "y": 0.341,
          "group": "baseline"
        },
        {
          "x": 0.72,
          "y": 0.24,
          "group": "current"
        },
        {
          "x": 1.017,
          "y": 0.174,
          "group": "current"
        },
        {
          "x": 1.201,
          "y": 0.085,
          "group": "bridge"
        },
        {
          "x": 1.325,
          "y": 0.121,
          "group": "bridge"
        },
        {
          "x": 1.529,
          "y": 0.222,
          "group": "current"
        },
        {
          "x": 1.837,
          "y": 0.22,
          "group": "current"
        },
        {
          "x": 2.12,
          "y": 0.118,
          "group": "current"
        },
        {
          "x": 0.746,
          "y": 0.266,
          "group": "current"
        },
        {
          "x": 0.874,
          "y": 0.356,
          "group": "current"
        },
        {
          "x": 1.099,
          "y": 0.42,
          "group": "bridge"
        },
        {
          "x": 1.414,
          "y": 0.351,
          "group": "bridge"
        },
        {
          "x": 1.679,
          "y": 0.264,
          "group": "current"
        },
        {
          "x": 1.829,
          "y": 0.303,
          "group": "current"
        },
        {
          "x": 1.966,
          "y": 0.404,
          "group": "current"
        },
        {
          "x": 0.672,
          "y": 0.579,
          "group": "current"
        },
        {
          "x": 0.988,
          "y": 0.476,
          "group": "current"
        },
        {
          "x": 1.234,
          "y": 0.447,
          "group": "bridge"
        },
        {
          "x": 1.371,
          "y": 0.539,
          "group": "bridge"
        },
        {
          "x": 1.521,
          "y": 0.6,
          "group": "current"
        },
        {
          "x": 1.786,
          "y": 0.528,
          "group": "current"
        },
        {
          "x": 2.101,
          "y": 0.443,
          "group": "current"
        },
        {
          "x": 0.786,
          "y": 0.666,
          "group": "current"
        },
        {
          "x": 0.914,
          "y": 0.765,
          "group": "current"
        },
        {
          "x": 1.08,
          "y": 0.757,
          "group": "bridge"
        },
        {
          "x": 1.363,
          "y": 0.654,
          "group": "bridge"
        },
        {
          "x": 1.671,
          "y": 0.628,
          "group": "current"
        },
        {
          "x": 1.875,
          "y": 0.721,
          "group": "current"
        },
        {
          "x": 1.999,
          "y": 0.78,
          "group": "current"
        },
        {
          "x": 0.643,
          "y": 0.886,
          "group": "current"
        },
        {
          "x": 0.94,
          "y": 0.802,
          "group": "current"
        },
        {
          "x": 1.237,
          "y": 0.848,
          "group": "bridge"
        },
        {
          "x": 1.421,
          "y": 0.947,
          "group": "bridge"
        },
        {
          "x": 1.545,
          "y": 0.935,
          "group": "current"
        },
        {
          "x": 1.749,
          "y": 0.832,
          "group": "current"
        },
        {
          "x": 2.057,
          "y": 0.809,
          "group": "current"
        },
        {
          "x": 0.8,
          "y": 1.084,
          "group": "current"
        },
        {
          "x": 0.965,
          "y": 1.139,
          "group": "current"
        },
        {
          "x": 1.094,
          "y": 1.063,
          "group": "bridge"
        },
        {
          "x": 1.319,
          "y": 0.982,
          "group": "bridge"
        },
        {
          "x": 1.634,
          "y": 1.03,
          "group": "current"
        },
        {
          "x": 1.899,
          "y": 1.128,
          "group": "current"
        },
        {
          "x": 2.049,
          "y": 1.113,
          "group": "current"
        }
      ],
      "chart.CHART-REP-003.heatmap": [
        {
          "group": "core",
          "values": [
            0.18,
            0.22,
            0.26,
            0.31,
            0.35,
            0.38
          ]
        },
        {
          "group": "hub",
          "values": [
            0.2,
            0.24,
            0.33,
            0.48,
            0.62,
            0.7
          ]
        },
        {
          "group": "bridge",
          "values": [
            0.14,
            0.18,
            0.27,
            0.43,
            0.58,
            0.66
          ]
        },
        {
          "group": "leaf",
          "values": [
            0.1,
            0.16,
            0.2,
            0.29,
            0.36,
            0.44
          ]
        },
        {
          "group": "new",
          "values": [
            0.12,
            0.15,
            0.18,
            0.24,
            0.28,
            0.31
          ]
        }
      ],
      "chart.CHART-REP-003.distance": [
        {
          "time": 1,
          "value": 0.08
        },
        {
          "time": 2,
          "value": 0.09
        },
        {
          "time": 3,
          "value": 0.1
        },
        {
          "time": 4,
          "value": 0.09
        },
        {
          "time": 5,
          "value": 0.11
        },
        {
          "time": 6,
          "value": 0.12
        },
        {
          "time": 7,
          "value": 0.13
        },
        {
          "time": 8,
          "value": 0.16
        },
        {
          "time": 9,
          "value": 0.18
        },
        {
          "time": 10,
          "value": 0.21
        },
        {
          "time": 11,
          "value": 0.25
        },
        {
          "time": 12,
          "value": 0.29
        },
        {
          "time": 13,
          "value": 0.33
        },
        {
          "time": 14,
          "value": 0.37
        },
        {
          "time": 15,
          "value": 0.42
        },
        {
          "time": 16,
          "value": 0.46
        },
        {
          "time": 17,
          "value": 0.5
        },
        {
          "time": 18,
          "value": 0.54
        },
        {
          "time": 19,
          "value": 0.57
        },
        {
          "time": 20,
          "value": 0.6
        },
        {
          "time": 21,
          "value": 0.62
        },
        {
          "time": 22,
          "value": 0.64
        },
        {
          "time": 23,
          "value": 0.66
        },
        {
          "time": 24,
          "value": 0.67
        }
      ],
      "chart.CHART-REP-003.notes": [
        {
          "title": "해석",
          "text": "Graph embedding drift는 그래프 전체 embedding 분리, node drift score 집중, graph-level distance 상승을 함께 본다. 이 예시에서는 distance가 t=15 이후 threshold를 넘고 hub/bridge score가 0.70, 0.66까지 높아져 graph representation drift 후보로 해석한다.",
          "legend": [
            {
              "label": "baseline graph",
              "class": "swatch-base"
            },
            {
              "label": "current graph",
              "class": "swatch-current"
            },
            {
              "label": "high node drift",
              "class": "swatch-drift"
            },
            {
              "label": "threshold",
              "class": "swatch-threshold"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-STREAM-001",
    "title": "ADWIN 경보 이후 스트림 평균 상승과 윈도 축소",
    "originalPath": "./drift_report_charts/chart_stream_001.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "chart_stream_001_source",
      "displayName": "CHART-STREAM-001 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 112px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "스트림 평균 상승",
          "description": "t=23 경보 전후로 metric이 0.38 수준에서 0.68 수준으로 올라가는지 읽는다.",
          "headerHeight": 76,
          "stageInset": {
            "top": 84,
            "right": 16,
            "bottom": -8,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "적응형 윈도 폭",
          "description": "경보 직후 170에서 62로 줄고 이후 다시 넓어진다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "경보 전후 평균",
          "description": "0.38에서 0.68로 올라 delta +0.30이 기준 0.20을 넘는다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "notes",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-STREAM-001.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 1,
        "config": {},
        "dataBinding": {
          "source": "chart.CHART-STREAM-001.summary"
        }
      },
      {
        "componentInstanceId": "CHART-STREAM-001.stream.0",
        "componentType": "trend_line",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "time",
          "y_field": "value",
          "secondary_value_field": "rolling_mean",
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 28,
            "bottom": 62,
            "left": 58
          },
          "x_min": 1,
          "x_max": 36,
          "y_min": 0.2,
          "y_max": 0.85,
          "x_ticks": [
            1,
            10,
            20,
            30,
            36
          ],
          "y_ticks": [
            0.2,
            0.4,
            0.6,
            0.8
          ],
          "x_axis_label": "time index",
          "y_axis_label": "metric",
          "line_class": "stream-line",
          "secondary_line_class": "mean-line-solid",
          "show_points": false,
          "show_secondary_points": false,
          "vertical_markers": [
            {
              "x": 23,
              "class": "alarm-line"
            }
          ],
          "point_highlights": [
            {
              "x": 23,
              "class": "alarm-point",
              "r": 7
            }
          ],
          "annotations": [
            {
              "text": "ADWIN alarm",
              "x": 23.5,
              "y": 0.82,
              "class": "warning"
            },
            {
              "text": "새 평균 수준으로 안정",
              "x": 27,
              "y": 0.77,
              "class": "callout"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-STREAM-001.stream"
        }
      },
      {
        "componentInstanceId": "CHART-STREAM-001.window.0",
        "componentType": "trend_line",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "time",
          "y_field": "value",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 22,
            "bottom": 34,
            "left": 48
          },
          "x_min": 1,
          "x_max": 36,
          "y_min": 40,
          "y_max": 180,
          "y_ticks": [
            50,
            100,
            150
          ],
          "x_ticks": [],
          "x_axis_label": "window width",
          "axis_label_x": 208,
          "axis_label_y": 177,
          "y_axis_label": false,
          "line_class": "window-line",
          "primary_point_class": "window-point",
          "point_radius": 3.6,
          "vertical_markers": [
            {
              "x": 23,
              "class": "alarm-line"
            }
          ],
          "point_highlights": [
            {
              "x": 23,
              "class": "alarm-point",
              "r": 5.5
            }
          ],
          "annotations": [
            {
              "text": "alarm 후 window 축소",
              "x": 23.5,
              "y": 70,
              "class": "warning"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-STREAM-001.window"
        }
      },
      {
        "componentInstanceId": "CHART-STREAM-001.mean.0",
        "componentType": "bar_chart",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "bar_style": "vertical_threshold",
          "category_field": "label",
          "value_field": "value",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 32,
            "bottom": 34,
            "left": 58
          },
          "y_max": 0.85,
          "threshold": 0.2,
          "threshold_class": "threshold-line",
          "bar_width": 29,
          "caption": "운영 기준 delta 0.20",
          "annotations": [
            {
              "text": "운영 기준 delta 0.20",
              "x": 318,
              "y": 120,
              "class": "warning"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-STREAM-001.mean"
        }
      },
      {
        "componentInstanceId": "CHART-STREAM-001.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 1,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-STREAM-001.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-STREAM-001.summary": [
        {
          "label": "alarm index",
          "displayValue": "23"
        },
        {
          "label": "mean delta",
          "displayValue": "+0.30"
        },
        {
          "label": "p-value",
          "displayValue": "0.009"
        }
      ],
      "chart.CHART-STREAM-001.stream": [
        {
          "time": 1,
          "value": 0.31,
          "rolling_mean": 0.31
        },
        {
          "time": 2,
          "value": 0.29,
          "rolling_mean": 0.3
        },
        {
          "time": 3,
          "value": 0.33,
          "rolling_mean": 0.31
        },
        {
          "time": 4,
          "value": 0.3,
          "rolling_mean": 0.31
        },
        {
          "time": 5,
          "value": 0.32,
          "rolling_mean": 0.31
        },
        {
          "time": 6,
          "value": 0.34,
          "rolling_mean": 0.32
        },
        {
          "time": 7,
          "value": 0.31,
          "rolling_mean": 0.32
        },
        {
          "time": 8,
          "value": 0.35,
          "rolling_mean": 0.33
        },
        {
          "time": 9,
          "value": 0.33,
          "rolling_mean": 0.33
        },
        {
          "time": 10,
          "value": 0.36,
          "rolling_mean": 0.34
        },
        {
          "time": 11,
          "value": 0.34,
          "rolling_mean": 0.34
        },
        {
          "time": 12,
          "value": 0.37,
          "rolling_mean": 0.35
        },
        {
          "time": 13,
          "value": 0.35,
          "rolling_mean": 0.35
        },
        {
          "time": 14,
          "value": 0.36,
          "rolling_mean": 0.36
        },
        {
          "time": 15,
          "value": 0.38,
          "rolling_mean": 0.36
        },
        {
          "time": 16,
          "value": 0.39,
          "rolling_mean": 0.37
        },
        {
          "time": 17,
          "value": 0.37,
          "rolling_mean": 0.37
        },
        {
          "time": 18,
          "value": 0.4,
          "rolling_mean": 0.38
        },
        {
          "time": 19,
          "value": 0.41,
          "rolling_mean": 0.39
        },
        {
          "time": 20,
          "value": 0.39,
          "rolling_mean": 0.39
        },
        {
          "time": 21,
          "value": 0.43,
          "rolling_mean": 0.41
        },
        {
          "time": 22,
          "value": 0.45,
          "rolling_mean": 0.43
        },
        {
          "time": 23,
          "value": 0.5,
          "rolling_mean": 0.46
        },
        {
          "time": 24,
          "value": 0.56,
          "rolling_mean": 0.5
        },
        {
          "time": 25,
          "value": 0.61,
          "rolling_mean": 0.55
        },
        {
          "time": 26,
          "value": 0.65,
          "rolling_mean": 0.6
        },
        {
          "time": 27,
          "value": 0.68,
          "rolling_mean": 0.64
        },
        {
          "time": 28,
          "value": 0.7,
          "rolling_mean": 0.67
        },
        {
          "time": 29,
          "value": 0.72,
          "rolling_mean": 0.69
        },
        {
          "time": 30,
          "value": 0.71,
          "rolling_mean": 0.7
        },
        {
          "time": 31,
          "value": 0.73,
          "rolling_mean": 0.71
        },
        {
          "time": 32,
          "value": 0.75,
          "rolling_mean": 0.73
        },
        {
          "time": 33,
          "value": 0.76,
          "rolling_mean": 0.74
        },
        {
          "time": 34,
          "value": 0.74,
          "rolling_mean": 0.74
        },
        {
          "time": 35,
          "value": 0.77,
          "rolling_mean": 0.75
        },
        {
          "time": 36,
          "value": 0.78,
          "rolling_mean": 0.76
        }
      ],
      "chart.CHART-STREAM-001.window": [
        {
          "time": 1,
          "value": 120
        },
        {
          "time": 2,
          "value": 122
        },
        {
          "time": 3,
          "value": 125
        },
        {
          "time": 4,
          "value": 127
        },
        {
          "time": 5,
          "value": 130
        },
        {
          "time": 6,
          "value": 132
        },
        {
          "time": 7,
          "value": 135
        },
        {
          "time": 8,
          "value": 138
        },
        {
          "time": 9,
          "value": 140
        },
        {
          "time": 10,
          "value": 142
        },
        {
          "time": 11,
          "value": 145
        },
        {
          "time": 12,
          "value": 148
        },
        {
          "time": 13,
          "value": 150
        },
        {
          "time": 14,
          "value": 152
        },
        {
          "time": 15,
          "value": 154
        },
        {
          "time": 16,
          "value": 156
        },
        {
          "time": 17,
          "value": 158
        },
        {
          "time": 18,
          "value": 160
        },
        {
          "time": 19,
          "value": 162
        },
        {
          "time": 20,
          "value": 164
        },
        {
          "time": 21,
          "value": 166
        },
        {
          "time": 22,
          "value": 168
        },
        {
          "time": 23,
          "value": 170
        },
        {
          "time": 24,
          "value": 62
        },
        {
          "time": 25,
          "value": 70
        },
        {
          "time": 26,
          "value": 78
        },
        {
          "time": 27,
          "value": 86
        },
        {
          "time": 28,
          "value": 94
        },
        {
          "time": 29,
          "value": 104
        },
        {
          "time": 30,
          "value": 112
        },
        {
          "time": 31,
          "value": 120
        },
        {
          "time": 32,
          "value": 128
        },
        {
          "time": 33,
          "value": 136
        },
        {
          "time": 34,
          "value": 144
        },
        {
          "time": 35,
          "value": 152
        },
        {
          "time": 36,
          "value": 160
        }
      ],
      "chart.CHART-STREAM-001.mean": [
        {
          "label": "before",
          "value": 0.38,
          "class": "mean-bar-before"
        },
        {
          "label": "after",
          "value": 0.68,
          "class": "mean-bar-after"
        },
        {
          "label": "delta",
          "value": 0.3,
          "class": "delta-bar"
        }
      ],
      "chart.CHART-STREAM-001.notes": [
        {
          "title": "해석",
          "text": "이 예시에서는 t=23에서 ADWIN 경보가 발생하고 p-value는 0.009로 표시된다. 경보 직후 적응형 윈도 폭이 170에서 62로 축소되며, 경보 전후 평균 차이 +0.30은 운영 기준 delta 0.20을 넘어 스트림 평균 상승 드리프트 후보로 읽는다.",
          "legend": [
            {
              "label": "stream metric",
              "class": "swatch-stream"
            },
            {
              "label": "rolling mean",
              "class": "swatch-mean"
            },
            {
              "label": "drift alarm",
              "class": "swatch-alarm"
            },
            {
              "label": "?? ??",
              "class": "swatch-threshold"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-STREAM-002",
    "title": "최근 윈도 분포 이동과 KSWIN 경보",
    "originalPath": "./drift_report_charts/chart_stream_002.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "chart_stream_002_source",
      "displayName": "CHART-STREAM-002 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 112px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "슬라이딩 윈도 구간",
          "description": "과거 window 10~20과 최근 window 24~34가 값 상승 전후를 나누어 비교된다.",
          "headerHeight": 76,
          "stageInset": {
            "top": 84,
            "right": 16,
            "bottom": -8,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "윈도 경험누적분포 비교",
          "description": "x=0.51 부근에서 ECDF 최대 차이 D=0.55가 나타난다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "KS 통계량 추세",
          "description": "최근 비교 구간의 KS statistic 0.55가 threshold 0.36을 넘는다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "notes",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-STREAM-002.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 1,
        "config": {},
        "dataBinding": {
          "source": "chart.CHART-STREAM-002.summary"
        }
      },
      {
        "componentInstanceId": "CHART-STREAM-002.stream.0",
        "componentType": "trend_line",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "time",
          "y_field": "value",
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 28,
            "bottom": 62,
            "left": 58
          },
          "x_min": 1,
          "x_max": 36,
          "y_min": 0.25,
          "y_max": 0.82,
          "x_ticks": [
            1,
            10,
            20,
            30,
            36
          ],
          "y_ticks": [
            0.3,
            0.5,
            0.7
          ],
          "x_axis_label": "time index",
          "y_axis_label": "metric",
          "line_class": "stream-green-line",
          "show_points": false,
          "background_regions": [
            {
              "x0": 10,
              "x1": 20,
              "fill": "rgba(47,111,159,0.14)"
            },
            {
              "x0": 24,
              "x1": 34,
              "fill": "rgba(185,90,80,0.16)"
            }
          ],
          "vertical_markers": [
            {
              "x": 28,
              "class": "threshold-line"
            }
          ],
          "point_highlights": [
            {
              "x": 28,
              "class": "alarm-point",
              "r": 7
            }
          ],
          "annotations": [
            {
              "text": "과거 window",
              "x": 11.5,
              "y": 0.77,
              "class": "callout"
            },
            {
              "text": "최근 window",
              "x": 25.5,
              "y": 0.77,
              "class": "warning"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-STREAM-002.stream"
        }
      },
      {
        "componentInstanceId": "CHART-STREAM-002.ecdf.0",
        "componentType": "trend_line",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "x",
          "y_field": "reference",
          "secondary_value_field": "current",
          "line_interpolation": "step",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 22,
            "bottom": 34,
            "left": 48
          },
          "x_min": 0.3,
          "x_max": 0.75,
          "y_min": 0,
          "y_max": 1,
          "x_ticks": [],
          "y_ticks": [
            0,
            0.5,
            1.0
          ],
          "x_axis_label": "sample value",
          "axis_label_x": 249,
          "axis_label_y": 177,
          "y_axis_label": false,
          "line_class": "ref-line",
          "secondary_line_class": "cur-line",
          "show_points": false,
          "show_secondary_points": false,
          "vertical_markers": [
            {
              "x": 0.51,
              "class": "threshold-line"
            }
          ],
          "annotations": [
            {
              "text": "D=0.55",
              "x": 0.52,
              "y": 0.58,
              "class": "warning"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-STREAM-002.ecdf"
        }
      },
      {
        "componentInstanceId": "CHART-STREAM-002.ks.0",
        "componentType": "trend_line",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "time",
          "y_field": "value",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 22,
            "bottom": 34,
            "left": 48
          },
          "x_min": 1,
          "x_max": 10,
          "y_min": 0,
          "y_max": 0.65,
          "y_ticks": [
            0,
            0.2,
            0.4,
            0.6
          ],
          "x_ticks": [],
          "x_axis_label": "window comparison",
          "axis_label_x": 208,
          "axis_label_y": 177,
          "y_axis_label": false,
          "line_class": "ks-line",
          "show_points": false,
          "horizontal_markers": [
            {
              "y": 0.36,
              "class": "threshold-line"
            }
          ],
          "point_highlights": [
            {
              "x": 1,
              "class": "ks-point",
              "r": 4
            },
            {
              "x": 2,
              "class": "ks-point",
              "r": 4
            },
            {
              "x": 3,
              "class": "ks-point",
              "r": 4
            },
            {
              "x": 4,
              "class": "ks-point",
              "r": 4
            },
            {
              "x": 5,
              "class": "ks-point",
              "r": 4
            },
            {
              "x": 6,
              "class": "ks-point",
              "r": 4
            },
            {
              "x": 7,
              "class": "ks-point",
              "r": 4
            },
            {
              "x": 8,
              "class": "alarm-point",
              "r": 4.8
            },
            {
              "x": 9,
              "class": "alarm-point",
              "r": 4.8
            },
            {
              "x": 10,
              "class": "alarm-point",
              "r": 4.8
            }
          ],
          "annotations": [
            {
              "text": "threshold 0.36",
              "x": 7.7,
              "y": 0.39,
              "class": "warning"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-STREAM-002.ks"
        }
      },
      {
        "componentInstanceId": "CHART-STREAM-002.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 1,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-STREAM-002.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-STREAM-002.summary": [
        {
          "label": "KS statistic",
          "displayValue": "0.55"
        },
        {
          "label": "p-value",
          "displayValue": "0.011"
        },
        {
          "label": "alarm index",
          "displayValue": "28"
        }
      ],
      "chart.CHART-STREAM-002.stream": [
        {
          "time": 1,
          "value": 0.28
        },
        {
          "time": 2,
          "value": 0.31
        },
        {
          "time": 3,
          "value": 0.3
        },
        {
          "time": 4,
          "value": 0.34
        },
        {
          "time": 5,
          "value": 0.32
        },
        {
          "time": 6,
          "value": 0.35
        },
        {
          "time": 7,
          "value": 0.33
        },
        {
          "time": 8,
          "value": 0.37
        },
        {
          "time": 9,
          "value": 0.35
        },
        {
          "time": 10,
          "value": 0.36
        },
        {
          "time": 11,
          "value": 0.34
        },
        {
          "time": 12,
          "value": 0.38
        },
        {
          "time": 13,
          "value": 0.36
        },
        {
          "time": 14,
          "value": 0.39
        },
        {
          "time": 15,
          "value": 0.37
        },
        {
          "time": 16,
          "value": 0.4
        },
        {
          "time": 17,
          "value": 0.38
        },
        {
          "time": 18,
          "value": 0.41
        },
        {
          "time": 19,
          "value": 0.4
        },
        {
          "time": 20,
          "value": 0.42
        },
        {
          "time": 21,
          "value": 0.43
        },
        {
          "time": 22,
          "value": 0.45
        },
        {
          "time": 23,
          "value": 0.49
        },
        {
          "time": 24,
          "value": 0.52
        },
        {
          "time": 25,
          "value": 0.57
        },
        {
          "time": 26,
          "value": 0.61
        },
        {
          "time": 27,
          "value": 0.64
        },
        {
          "time": 28,
          "value": 0.67
        },
        {
          "time": 29,
          "value": 0.69
        },
        {
          "time": 30,
          "value": 0.71
        },
        {
          "time": 31,
          "value": 0.7
        },
        {
          "time": 32,
          "value": 0.72
        },
        {
          "time": 33,
          "value": 0.74
        },
        {
          "time": 34,
          "value": 0.73
        },
        {
          "time": 35,
          "value": 0.75
        },
        {
          "time": 36,
          "value": 0.77
        }
      ],
      "chart.CHART-STREAM-002.ecdf": [
        {
          "x": 0.3,
          "reference": 0.1,
          "current": 0.0
        },
        {
          "x": 0.35,
          "reference": 0.28,
          "current": 0.02
        },
        {
          "x": 0.4,
          "reference": 0.52,
          "current": 0.05
        },
        {
          "x": 0.45,
          "reference": 0.78,
          "current": 0.12
        },
        {
          "x": 0.5,
          "reference": 0.92,
          "current": 0.24
        },
        {
          "x": 0.55,
          "reference": 0.98,
          "current": 0.38
        },
        {
          "x": 0.6,
          "reference": 1.0,
          "current": 0.55
        },
        {
          "x": 0.65,
          "reference": 1.0,
          "current": 0.72
        },
        {
          "x": 0.7,
          "reference": 1.0,
          "current": 0.88
        },
        {
          "x": 0.75,
          "reference": 1.0,
          "current": 1.0
        }
      ],
      "chart.CHART-STREAM-002.ks": [
        {
          "time": 1,
          "value": 0.12
        },
        {
          "time": 2,
          "value": 0.14
        },
        {
          "time": 3,
          "value": 0.16
        },
        {
          "time": 4,
          "value": 0.18
        },
        {
          "time": 5,
          "value": 0.21
        },
        {
          "time": 6,
          "value": 0.24
        },
        {
          "time": 7,
          "value": 0.31
        },
        {
          "time": 8,
          "value": 0.39
        },
        {
          "time": 9,
          "value": 0.48
        },
        {
          "time": 10,
          "value": 0.55
        }
      ],
      "chart.CHART-STREAM-002.notes": [
        {
          "title": "해석",
          "text": "KSWIN은 stream에서 과거 window와 최근 window의 sample 분포를 KS statistic으로 비교한다. 이 예시에서는 alarm index 28에서 KS statistic 0.55, p-value 0.011이 표시된다. 최근 window 24~34가 과거 window 10~20보다 높은 값 구간에 놓이고, ECDF 최대 차이와 threshold 초과가 함께 보여 stream 분포 이동 후보로 해석한다.",
          "legend": [
            {
              "label": "stream metric",
              "class": "swatch-stream-green"
            },
            {
              "label": "?? window",
              "class": "swatch-reference"
            },
            {
              "label": "?? window",
              "class": "swatch-current-red"
            },
            {
              "label": "threshold",
              "class": "swatch-threshold"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-STREAM-003",
    "title": "페이지-힌클리 기반 스트림 평균 상승 경보",
    "originalPath": "./drift_report_charts/chart_stream_003.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "chart_stream_003_source",
      "displayName": "CHART-STREAM-003 source layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 112px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "스트림 값과 이동 평균",
          "description": "t=20 이후 metric이 0.53에서 0.84까지 오르고, t=29에 alarm이 표시된다.",
          "headerHeight": 76,
          "stageInset": {
            "top": 84,
            "right": 16,
            "bottom": -8,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "PH 통계량",
          "description": "누적 통계량이 threshold 18.0을 넘어 25.5까지 증가한다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "경보 상태 흐름",
          "description": "normal 이후 t=22 warning, t=29 drift로 전환된다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "notes",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-STREAM-003.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "isOverlay": false,
        "zIndex": 1,
        "config": {},
        "dataBinding": {
          "source": "chart.CHART-STREAM-003.summary"
        }
      },
      {
        "componentInstanceId": "CHART-STREAM-003.stream.0",
        "componentType": "trend_line",
        "area": "main",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "time",
          "y_field": "value",
          "secondary_value_field": "running_mean",
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 28,
            "bottom": 62,
            "left": 58
          },
          "x_min": 1,
          "x_max": 36,
          "y_min": 0.35,
          "y_max": 0.88,
          "x_ticks": [
            1,
            10,
            20,
            30,
            36
          ],
          "y_ticks": [
            0.4,
            0.6,
            0.8
          ],
          "x_axis_label": "time index",
          "y_axis_label": "metric",
          "line_class": "stream-line",
          "secondary_line_class": "mean-line-solid",
          "show_points": false,
          "show_secondary_points": false,
          "vertical_markers": [
            {
              "x": 29,
              "class": "alarm-line"
            }
          ],
          "point_highlights": [
            {
              "x": 29,
              "class": "alarm-point",
              "r": 7
            }
          ],
          "annotations": [
            {
              "text": "Page-Hinkley alarm",
              "x": 29.5,
              "y": 0.84,
              "class": "warning-text"
            },
            {
              "text": "평균 shift ++0.31",
              "x": 21,
              "y": 0.82,
              "class": "callout"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-STREAM-003.stream"
        }
      },
      {
        "componentInstanceId": "CHART-STREAM-003.ph.0",
        "componentType": "trend_line",
        "area": "side_top",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "x_field": "time",
          "y_field": "value",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 22,
            "bottom": 34,
            "left": 48
          },
          "x_min": 1,
          "x_max": 36,
          "y_min": 0,
          "y_max": 28,
          "y_ticks": [
            0,
            10,
            20
          ],
          "x_ticks": [],
          "x_axis_label": "time index",
          "axis_label_x": 208,
          "axis_label_y": 177,
          "y_axis_label": false,
          "line_class": "ph-line",
          "show_points": false,
          "horizontal_markers": [
            {
              "y": 18,
              "class": "threshold-line"
            }
          ],
          "point_highlights": [
            {
              "x": 1,
              "class": "ph-point",
              "r": 3.6
            },
            {
              "x": 2,
              "class": "ph-point",
              "r": 3.6
            },
            {
              "x": 3,
              "class": "ph-point",
              "r": 3.6
            },
            {
              "x": 4,
              "class": "ph-point",
              "r": 3.6
            },
            {
              "x": 5,
              "class": "ph-point",
              "r": 3.6
            },
            {
              "x": 6,
              "class": "ph-point",
              "r": 3.6
            },
            {
              "x": 7,
              "class": "ph-point",
              "r": 3.6
            },
            {
              "x": 8,
              "class": "ph-point",
              "r": 3.6
            },
            {
              "x": 9,
              "class": "ph-point",
              "r": 3.6
            },
            {
              "x": 10,
              "class": "ph-point",
              "r": 3.6
            },
            {
              "x": 11,
              "class": "ph-point",
              "r": 3.6
            },
            {
              "x": 12,
              "class": "ph-point",
              "r": 3.6
            },
            {
              "x": 13,
              "class": "ph-point",
              "r": 3.6
            },
            {
              "x": 14,
              "class": "ph-point",
              "r": 3.6
            },
            {
              "x": 15,
              "class": "ph-point",
              "r": 3.6
            },
            {
              "x": 16,
              "class": "ph-point",
              "r": 3.6
            },
            {
              "x": 17,
              "class": "ph-point",
              "r": 3.6
            },
            {
              "x": 18,
              "class": "ph-point",
              "r": 3.6
            },
            {
              "x": 19,
              "class": "ph-point",
              "r": 3.6
            },
            {
              "x": 20,
              "class": "ph-point",
              "r": 3.6
            },
            {
              "x": 21,
              "class": "ph-point",
              "r": 3.6
            },
            {
              "x": 22,
              "class": "ph-point",
              "r": 3.6
            },
            {
              "x": 23,
              "class": "ph-point",
              "r": 3.6
            },
            {
              "x": 24,
              "class": "ph-point",
              "r": 3.6
            },
            {
              "x": 25,
              "class": "ph-point",
              "r": 3.6
            },
            {
              "x": 26,
              "class": "ph-point",
              "r": 3.6
            },
            {
              "x": 27,
              "class": "ph-point",
              "r": 3.6
            },
            {
              "x": 28,
              "class": "ph-point",
              "r": 3.6
            },
            {
              "x": 29,
              "class": "alarm-point",
              "r": 4.8
            },
            {
              "x": 30,
              "class": "alarm-point",
              "r": 4.8
            },
            {
              "x": 31,
              "class": "alarm-point",
              "r": 4.8
            },
            {
              "x": 32,
              "class": "alarm-point",
              "r": 4.8
            },
            {
              "x": 33,
              "class": "alarm-point",
              "r": 4.8
            },
            {
              "x": 34,
              "class": "alarm-point",
              "r": 4.8
            },
            {
              "x": 35,
              "class": "alarm-point",
              "r": 4.8
            },
            {
              "x": 36,
              "class": "alarm-point",
              "r": 4.8
            }
          ],
          "annotations": [
            {
              "text": "threshold 18.0",
              "x": 27,
              "y": 19.3,
              "class": "warning-text"
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-STREAM-003.ph"
        }
      },
      {
        "componentInstanceId": "CHART-STREAM-003.timeline.0",
        "componentType": "state_timeline",
        "area": "side_bottom",
        "isOverlay": false,
        "zIndex": 10,
        "config": {
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 32,
            "right": 24,
            "bottom": 38,
            "left": 48
          },
          "track_y": 74,
          "track_height": 30,
          "window_role_field": "role",
          "window_id_field": "window",
          "role_class_map": {
            "normal": "state-normal",
            "warning": "state-warning",
            "drift": "state-drift"
          },
          "x_ticks": [
            1,
            10,
            20,
            30,
            36
          ],
          "axis_label": "alarm marker timeline",
          "axis_label_x": 218,
          "axis_label_y": 179,
          "markers": [
            {
              "x": 29,
              "class": "alarm-line",
              "circle": true,
              "circle_class": "alarm-point",
              "radius": 7
            }
          ]
        },
        "dataBinding": {
          "source": "chart.CHART-STREAM-003.timeline"
        }
      },
      {
        "componentInstanceId": "CHART-STREAM-003.notes.0",
        "componentType": "domain_specific_visual",
        "area": "notes",
        "isOverlay": false,
        "zIndex": 1,
        "config": {
          "card_style": "notes_legend"
        },
        "dataBinding": {
          "source": "chart.CHART-STREAM-003.notes"
        }
      }
    ],
    "data": {
      "chart.CHART-STREAM-003.summary": [
        {
          "label": "PH statistic",
          "displayValue": "25.5"
        },
        {
          "label": "threshold",
          "displayValue": "18.0"
        },
        {
          "label": "alarm index",
          "displayValue": "29"
        }
      ],
      "chart.CHART-STREAM-003.stream": [
        {
          "time": 1,
          "value": 0.42,
          "running_mean": 0.42
        },
        {
          "time": 2,
          "value": 0.4,
          "running_mean": 0.41
        },
        {
          "time": 3,
          "value": 0.43,
          "running_mean": 0.42
        },
        {
          "time": 4,
          "value": 0.41,
          "running_mean": 0.42
        },
        {
          "time": 5,
          "value": 0.44,
          "running_mean": 0.42
        },
        {
          "time": 6,
          "value": 0.45,
          "running_mean": 0.43
        },
        {
          "time": 7,
          "value": 0.43,
          "running_mean": 0.43
        },
        {
          "time": 8,
          "value": 0.46,
          "running_mean": 0.43
        },
        {
          "time": 9,
          "value": 0.45,
          "running_mean": 0.43
        },
        {
          "time": 10,
          "value": 0.47,
          "running_mean": 0.44
        },
        {
          "time": 11,
          "value": 0.46,
          "running_mean": 0.44
        },
        {
          "time": 12,
          "value": 0.48,
          "running_mean": 0.45
        },
        {
          "time": 13,
          "value": 0.47,
          "running_mean": 0.45
        },
        {
          "time": 14,
          "value": 0.49,
          "running_mean": 0.45
        },
        {
          "time": 15,
          "value": 0.48,
          "running_mean": 0.45
        },
        {
          "time": 16,
          "value": 0.5,
          "running_mean": 0.46
        },
        {
          "time": 17,
          "value": 0.49,
          "running_mean": 0.46
        },
        {
          "time": 18,
          "value": 0.51,
          "running_mean": 0.47
        },
        {
          "time": 19,
          "value": 0.52,
          "running_mean": 0.47
        },
        {
          "time": 20,
          "value": 0.53,
          "running_mean": 0.48
        },
        {
          "time": 21,
          "value": 0.55,
          "running_mean": 0.49
        },
        {
          "time": 22,
          "value": 0.57,
          "running_mean": 0.5
        },
        {
          "time": 23,
          "value": 0.6,
          "running_mean": 0.51
        },
        {
          "time": 24,
          "value": 0.63,
          "running_mean": 0.53
        },
        {
          "time": 25,
          "value": 0.66,
          "running_mean": 0.54
        },
        {
          "time": 26,
          "value": 0.69,
          "running_mean": 0.56
        },
        {
          "time": 27,
          "value": 0.71,
          "running_mean": 0.58
        },
        {
          "time": 28,
          "value": 0.74,
          "running_mean": 0.6
        },
        {
          "time": 29,
          "value": 0.76,
          "running_mean": 0.62
        },
        {
          "time": 30,
          "value": 0.78,
          "running_mean": 0.64
        },
        {
          "time": 31,
          "value": 0.79,
          "running_mean": 0.65
        },
        {
          "time": 32,
          "value": 0.81,
          "running_mean": 0.67
        },
        {
          "time": 33,
          "value": 0.8,
          "running_mean": 0.68
        },
        {
          "time": 34,
          "value": 0.82,
          "running_mean": 0.69
        },
        {
          "time": 35,
          "value": 0.83,
          "running_mean": 0.7
        },
        {
          "time": 36,
          "value": 0.84,
          "running_mean": 0.72
        }
      ],
      "chart.CHART-STREAM-003.ph": [
        {
          "time": 1,
          "value": 0.1
        },
        {
          "time": 2,
          "value": 0.2
        },
        {
          "time": 3,
          "value": 0.3
        },
        {
          "time": 4,
          "value": 0.4
        },
        {
          "time": 5,
          "value": 0.6
        },
        {
          "time": 6,
          "value": 0.8
        },
        {
          "time": 7,
          "value": 1.0
        },
        {
          "time": 8,
          "value": 1.2
        },
        {
          "time": 9,
          "value": 1.5
        },
        {
          "time": 10,
          "value": 1.7
        },
        {
          "time": 11,
          "value": 2.0
        },
        {
          "time": 12,
          "value": 2.3
        },
        {
          "time": 13,
          "value": 2.5
        },
        {
          "time": 14,
          "value": 2.8
        },
        {
          "time": 15,
          "value": 3.1
        },
        {
          "time": 16,
          "value": 3.4
        },
        {
          "time": 17,
          "value": 3.8
        },
        {
          "time": 18,
          "value": 4.2
        },
        {
          "time": 19,
          "value": 4.7
        },
        {
          "time": 20,
          "value": 5.3
        },
        {
          "time": 21,
          "value": 6.1
        },
        {
          "time": 22,
          "value": 7.0
        },
        {
          "time": 23,
          "value": 8.2
        },
        {
          "time": 24,
          "value": 9.6
        },
        {
          "time": 25,
          "value": 11.3
        },
        {
          "time": 26,
          "value": 13.1
        },
        {
          "time": 27,
          "value": 15.2
        },
        {
          "time": 28,
          "value": 17.5
        },
        {
          "time": 29,
          "value": 19.6
        },
        {
          "time": 30,
          "value": 21.2
        },
        {
          "time": 31,
          "value": 22.4
        },
        {
          "time": 32,
          "value": 23.5
        },
        {
          "time": 33,
          "value": 24.0
        },
        {
          "time": 34,
          "value": 24.6
        },
        {
          "time": 35,
          "value": 25.1
        },
        {
          "time": 36,
          "value": 25.5
        }
      ],
      "chart.CHART-STREAM-003.timeline": [
        {
          "start": 1,
          "end": 22,
          "role": "normal",
          "window": "normal"
        },
        {
          "start": 22,
          "end": 29,
          "role": "warning",
          "window": "warning"
        },
        {
          "start": 29,
          "end": 36,
          "role": "drift",
          "window": "drift"
        }
      ],
      "chart.CHART-STREAM-003.notes": [
        {
          "title": "해석",
          "text": "이 예시에서는 stream metric이 초반 0.42~0.53 수준에서 t=20 이후 계속 상승하고, PH statistic이 threshold 18.0을 넘어 최종 25.5까지 증가한다. t=22 warning 이후 t=29 drift 상태로 바뀌므로 평균 상승 방향의 stream drift 후보로 읽는다.",
          "legend": [
            {
              "label": "raw stream",
              "class": "swatch-stream"
            },
            {
              "label": "running mean",
              "class": "swatch-mean"
            },
            {
              "label": "drift alarm",
              "class": "swatch-alarm"
            },
            {
              "label": "threshold",
              "class": "swatch-threshold"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-STREAM-004",
    "title": "CHART-STREAM-004 - SeqDrift 순차 스트림 상승 경보",
    "originalPath": "./drift_report_charts/chart_stream_004.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_stream_text_unc_var",
      "displayName": "source matching layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 120px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "스트림 값 상승",
          "description": "t=27 alarm point rises above reference mean 0.53 and delta reaches +0.34.",
          "headerHeight": 76,
          "stageInset": {
            "top": 84,
            "right": 16,
            "bottom": -8,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "순차 증거와 판정 경계",
          "description": "Evidence crosses the decision bound and reaches 26.5.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "주의에서 드리프트로 전환",
          "description": "State changes from warning at t=22 to drift at t=27.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "notes",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1,
          "stageInset": {
            "top": 0,
            "right": 0,
            "bottom": 0,
            "left": 0
          }
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-STREAM-004.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "dataBinding": {
          "source": "summary"
        },
        "config": {}
      },
      {
        "componentInstanceId": "CHART-STREAM-004.main.0",
        "componentType": "trend_line",
        "area": "main",
        "dataBinding": {
          "source": "stream"
        },
        "config": {
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 28,
            "bottom": 62,
            "left": 58
          },
          "x_min": 1,
          "x_max": 36,
          "y_min": 0.42,
          "y_max": 0.9,
          "x_ticks": [
            1,
            10,
            20,
            30,
            36
          ],
          "y_ticks": [
            0.5,
            0.7,
            0.9
          ],
          "x_axis_label": "time index",
          "y_axis_label": "value",
          "line_class": "stream-line",
          "show_points": false,
          "horizontal_markers": [
            {
              "y": 0.53,
              "class": "mean-line",
              "label": "reference mean 0.53",
              "label_x": 3,
              "label_class": "callout"
            }
          ],
          "vertical_markers": [
            {
              "x": 27,
              "class": "alarm-line"
            }
          ],
          "point_highlights": [
            {
              "x": 27,
              "class": "alarm-point",
              "r": 7
            }
          ],
          "annotations": [
            {
              "text": "alarm, delta +0.34",
              "x": 27.5,
              "y": 0.82,
              "class": "warning-text"
            }
          ]
        }
      },
      {
        "componentInstanceId": "CHART-STREAM-004.side_top.0",
        "componentType": "trend_line",
        "area": "side_top",
        "dataBinding": {
          "source": "evidence"
        },
        "config": {
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 22,
            "bottom": 34,
            "left": 48
          },
          "x_min": 1,
          "x_max": 36,
          "y_min": 0,
          "y_max": 30,
          "x_ticks": [],
          "y_ticks": [
            0,
            10,
            20,
            30
          ],
          "x_axis_label": "time index",
          "y_axis_label": false,
          "value_field": "evidence",
          "secondary_value_field": "bound",
          "line_class": "evidence-line",
          "secondary_line_class": "bound-line",
          "primary_point_class": "evidence-point",
          "point_sample_every": 1,
          "point_radius": 3.4,
          "secondary_point_radius": 0,
          "show_secondary_points": false,
          "point_highlights": [],
          "annotations": [
            {
              "text": "decision bound",
              "x": 27,
              "y": 13.2,
              "class": "warning-text"
            }
          ],
          "point_class_field": "pointClass",
          "point_radius_field": "pointRadius"
        }
      },
      {
        "componentInstanceId": "CHART-STREAM-004.side_bottom.0",
        "componentType": "state_timeline",
        "area": "side_bottom",
        "dataBinding": {
          "source": "timeline"
        },
        "config": {
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 32,
            "right": 24,
            "bottom": 38,
            "left": 48
          },
          "start_field": "start",
          "end_field": "end",
          "window_role_field": "role",
          "window_id_field": "label",
          "track_y": 74,
          "track_height": 30,
          "role_class_map": {
            "monitor": "state-normal",
            "warning": "state-warning",
            "drift": "state-drift"
          },
          "label_map": {},
          "markers": [
            {
              "x": 27,
              "class": "alarm-line"
            }
          ],
          "x_ticks": [
            1,
            10,
            20,
            30,
            36
          ],
          "axis_label": "sequential decision timeline"
        }
      },
      {
        "componentInstanceId": "CHART-STREAM-004.notes.0",
        "componentType": "decision_card",
        "area": "notes",
        "dataBinding": {
          "source": "notes"
        },
        "config": {
          "card_style": "notes_legend"
        }
      }
    ],
    "data": {
      "summary": [
        {
          "label": "evidence",
          "value": "26.5"
        },
        {
          "label": "alarm index",
          "value": "27"
        },
        {
          "label": "detect delay",
          "value": "4 step"
        }
      ],
      "stream": [
        {
          "time": 1,
          "value": 0.5
        },
        {
          "time": 2,
          "value": 0.48
        },
        {
          "time": 3,
          "value": 0.51
        },
        {
          "time": 4,
          "value": 0.49
        },
        {
          "time": 5,
          "value": 0.52
        },
        {
          "time": 6,
          "value": 0.5
        },
        {
          "time": 7,
          "value": 0.51
        },
        {
          "time": 8,
          "value": 0.53
        },
        {
          "time": 9,
          "value": 0.5
        },
        {
          "time": 10,
          "value": 0.52
        },
        {
          "time": 11,
          "value": 0.54
        },
        {
          "time": 12,
          "value": 0.51
        },
        {
          "time": 13,
          "value": 0.53
        },
        {
          "time": 14,
          "value": 0.55
        },
        {
          "time": 15,
          "value": 0.52
        },
        {
          "time": 16,
          "value": 0.54
        },
        {
          "time": 17,
          "value": 0.56
        },
        {
          "time": 18,
          "value": 0.55
        },
        {
          "time": 19,
          "value": 0.57
        },
        {
          "time": 20,
          "value": 0.58
        },
        {
          "time": 21,
          "value": 0.6
        },
        {
          "time": 22,
          "value": 0.62
        },
        {
          "time": 23,
          "value": 0.65
        },
        {
          "time": 24,
          "value": 0.68
        },
        {
          "time": 25,
          "value": 0.7
        },
        {
          "time": 26,
          "value": 0.73
        },
        {
          "time": 27,
          "value": 0.75
        },
        {
          "time": 28,
          "value": 0.77
        },
        {
          "time": 29,
          "value": 0.79
        },
        {
          "time": 30,
          "value": 0.8
        },
        {
          "time": 31,
          "value": 0.82
        },
        {
          "time": 32,
          "value": 0.83
        },
        {
          "time": 33,
          "value": 0.85
        },
        {
          "time": 34,
          "value": 0.84
        },
        {
          "time": 35,
          "value": 0.86
        },
        {
          "time": 36,
          "value": 0.87
        }
      ],
      "evidence": [
        {
          "time": 1,
          "evidence": 0.0,
          "bound": 7,
          "pointClass": "evidence-point",
          "pointRadius": 3.4
        },
        {
          "time": 2,
          "evidence": 0.1,
          "bound": 7.2,
          "pointClass": "evidence-point",
          "pointRadius": 3.4
        },
        {
          "time": 3,
          "evidence": 0.1,
          "bound": 7.4,
          "pointClass": "evidence-point",
          "pointRadius": 3.4
        },
        {
          "time": 4,
          "evidence": 0.2,
          "bound": 7.6,
          "pointClass": "evidence-point",
          "pointRadius": 3.4
        },
        {
          "time": 5,
          "evidence": 0.3,
          "bound": 7.8,
          "pointClass": "evidence-point",
          "pointRadius": 3.4
        },
        {
          "time": 6,
          "evidence": 0.4,
          "bound": 8.0,
          "pointClass": "evidence-point",
          "pointRadius": 3.4
        },
        {
          "time": 7,
          "evidence": 0.6,
          "bound": 8.2,
          "pointClass": "evidence-point",
          "pointRadius": 3.4
        },
        {
          "time": 8,
          "evidence": 0.7,
          "bound": 8.4,
          "pointClass": "evidence-point",
          "pointRadius": 3.4
        },
        {
          "time": 9,
          "evidence": 0.9,
          "bound": 8.6,
          "pointClass": "evidence-point",
          "pointRadius": 3.4
        },
        {
          "time": 10,
          "evidence": 1.1,
          "bound": 8.8,
          "pointClass": "evidence-point",
          "pointRadius": 3.4
        },
        {
          "time": 11,
          "evidence": 1.4,
          "bound": 9.0,
          "pointClass": "evidence-point",
          "pointRadius": 3.4
        },
        {
          "time": 12,
          "evidence": 1.6,
          "bound": 9.2,
          "pointClass": "evidence-point",
          "pointRadius": 3.4
        },
        {
          "time": 13,
          "evidence": 1.9,
          "bound": 9.4,
          "pointClass": "evidence-point",
          "pointRadius": 3.4
        },
        {
          "time": 14,
          "evidence": 2.2,
          "bound": 9.6,
          "pointClass": "evidence-point",
          "pointRadius": 3.4
        },
        {
          "time": 15,
          "evidence": 2.5,
          "bound": 9.8,
          "pointClass": "evidence-point",
          "pointRadius": 3.4
        },
        {
          "time": 16,
          "evidence": 2.8,
          "bound": 10.0,
          "pointClass": "evidence-point",
          "pointRadius": 3.4
        },
        {
          "time": 17,
          "evidence": 3.2,
          "bound": 10.2,
          "pointClass": "evidence-point",
          "pointRadius": 3.4
        },
        {
          "time": 18,
          "evidence": 3.6,
          "bound": 10.4,
          "pointClass": "evidence-point",
          "pointRadius": 3.4
        },
        {
          "time": 19,
          "evidence": 4.1,
          "bound": 10.6,
          "pointClass": "evidence-point",
          "pointRadius": 3.4
        },
        {
          "time": 20,
          "evidence": 4.8,
          "bound": 10.8,
          "pointClass": "evidence-point",
          "pointRadius": 3.4
        },
        {
          "time": 21,
          "evidence": 5.7,
          "bound": 11.0,
          "pointClass": "evidence-point",
          "pointRadius": 3.4
        },
        {
          "time": 22,
          "evidence": 6.8,
          "bound": 11.2,
          "pointClass": "evidence-point",
          "pointRadius": 3.4
        },
        {
          "time": 23,
          "evidence": 8.1,
          "bound": 11.4,
          "pointClass": "evidence-point",
          "pointRadius": 3.4
        },
        {
          "time": 24,
          "evidence": 9.7,
          "bound": 11.6,
          "pointClass": "evidence-point",
          "pointRadius": 3.4
        },
        {
          "time": 25,
          "evidence": 11.4,
          "bound": 11.8,
          "pointClass": "evidence-point",
          "pointRadius": 3.4
        },
        {
          "time": 26,
          "evidence": 13.2,
          "bound": 12.0,
          "pointClass": "alarm-point",
          "pointRadius": 4.8
        },
        {
          "time": 27,
          "evidence": 15.1,
          "bound": 12.2,
          "pointClass": "alarm-point",
          "pointRadius": 4.8
        },
        {
          "time": 28,
          "evidence": 17.0,
          "bound": 12.4,
          "pointClass": "alarm-point",
          "pointRadius": 4.8
        },
        {
          "time": 29,
          "evidence": 18.8,
          "bound": 12.6,
          "pointClass": "alarm-point",
          "pointRadius": 4.8
        },
        {
          "time": 30,
          "evidence": 20.4,
          "bound": 12.8,
          "pointClass": "alarm-point",
          "pointRadius": 4.8
        },
        {
          "time": 31,
          "evidence": 21.8,
          "bound": 13.0,
          "pointClass": "alarm-point",
          "pointRadius": 4.8
        },
        {
          "time": 32,
          "evidence": 23.0,
          "bound": 13.2,
          "pointClass": "alarm-point",
          "pointRadius": 4.8
        },
        {
          "time": 33,
          "evidence": 24.1,
          "bound": 13.4,
          "pointClass": "alarm-point",
          "pointRadius": 4.8
        },
        {
          "time": 34,
          "evidence": 25.0,
          "bound": 13.6,
          "pointClass": "alarm-point",
          "pointRadius": 4.8
        },
        {
          "time": 35,
          "evidence": 25.8,
          "bound": 13.8,
          "pointClass": "alarm-point",
          "pointRadius": 4.8
        },
        {
          "time": 36,
          "evidence": 26.5,
          "bound": 14.0,
          "pointClass": "alarm-point",
          "pointRadius": 4.8
        }
      ],
      "timeline": [
        {
          "start": 1,
          "end": 22,
          "role": "monitor",
          "label": "monitor"
        },
        {
          "start": 22,
          "end": 27,
          "role": "warning",
          "label": "warning"
        },
        {
          "start": 27,
          "end": 36,
          "role": "drift",
          "label": "drift"
        }
      ],
      "notes": [
        {
          "title": "해석",
          "text": "Stream value rises above the reference mean 0.53, sequential evidence exceeds the bound, and the t=27 alarm is interpreted as sequential drift evidence.",
          "legend": [
            {
              "label": "stream value",
              "class": "swatch-stream"
            },
            {
              "label": "reference mean",
              "class": "swatch-mean"
            },
            {
              "label": "drift alarm",
              "class": "swatch-marker"
            },
            {
              "label": "decision bound",
              "class": "swatch-threshold"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-STREAM-005",
    "title": "CHART-STREAM-005 - SPRT 오류 증가 판정",
    "originalPath": "./drift_report_charts/chart_stream_005.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_stream_text_unc_var",
      "displayName": "source matching layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 120px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "로그 우도비 누적",
          "description": "At t=25, LLR 11.0 crosses the H1 boundary 10.8.",
          "headerHeight": 76,
          "stageInset": {
            "top": 84,
            "right": 16,
            "bottom": -8,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "오류율 스트림",
          "description": "Error rate rises from 0.08 to 0.40 and moves above the 0.30 guide.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "순차 판정 상태",
          "description": "Decision state moves from continue to review, then accept H1 from t=25.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "notes",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1,
          "stageInset": {
            "top": 0,
            "right": 0,
            "bottom": 0,
            "left": 0
          }
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-STREAM-005.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "dataBinding": {
          "source": "summary"
        },
        "config": {}
      },
      {
        "componentInstanceId": "CHART-STREAM-005.main.0",
        "componentType": "trend_line",
        "area": "main",
        "dataBinding": {
          "source": "llr"
        },
        "config": {
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 28,
            "bottom": 62,
            "left": 58
          },
          "x_min": 1,
          "x_max": 32,
          "y_min": -4,
          "y_max": 18,
          "x_ticks": [
            1,
            8,
            16,
            24,
            32
          ],
          "y_ticks": [
            -4,
            0,
            5,
            10,
            15
          ],
          "x_axis_label": "time index",
          "y_axis_label": "log likelihood ratio",
          "line_class": "llr-line",
          "primary_point_class": "llr-point",
          "point_sample_every": 1,
          "point_radius": 3.5,
          "horizontal_markers": [
            {
              "y": 10.8,
              "class": "upper-boundary-line",
              "label": "accept H1 boundary",
              "label_x": 3,
              "label_class": "warning-text"
            },
            {
              "y": -2.2,
              "class": "lower-boundary-line",
              "label": "accept H0 boundary",
              "label_x": 3,
              "label_dy": 16,
              "label_class": "callout"
            }
          ],
          "vertical_markers": [
            {
              "x": 25,
              "class": "alarm-line"
            }
          ],
          "point_highlights": [],
          "point_class_field": "pointClass",
          "point_radius_field": "pointRadius"
        }
      },
      {
        "componentInstanceId": "CHART-STREAM-005.side_top.0",
        "componentType": "trend_line",
        "area": "side_top",
        "dataBinding": {
          "source": "error_rate"
        },
        "config": {
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 22,
            "bottom": 34,
            "left": 48
          },
          "x_min": 1,
          "x_max": 32,
          "y_min": 0,
          "y_max": 0.45,
          "x_ticks": [],
          "y_ticks": [
            0,
            0.15,
            0.3,
            0.45
          ],
          "x_axis_label": "error rate",
          "y_axis_label": false,
          "line_class": "error-line",
          "show_points": false,
          "horizontal_markers": [
            {
              "y": 0.3,
              "class": "upper-boundary-line"
            }
          ],
          "vertical_markers": [
            {
              "x": 25,
              "class": "alarm-line"
            }
          ],
          "annotations": [
            {
              "text": "H1 direction increase",
              "x": 21,
              "y": 0.36,
              "class": "warning-text"
            }
          ]
        }
      },
      {
        "componentInstanceId": "CHART-STREAM-005.side_bottom.0",
        "componentType": "state_timeline",
        "area": "side_bottom",
        "dataBinding": {
          "source": "timeline"
        },
        "config": {
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 32,
            "right": 24,
            "bottom": 38,
            "left": 48
          },
          "track_y": 74,
          "track_height": 30,
          "role_class_map": {
            "continue": "state-normal",
            "review": "state-warning",
            "h1": "state-drift"
          },
          "markers": [
            {
              "x": 25,
              "class": "alarm-line"
            }
          ],
          "x_ticks": [
            1,
            8,
            16,
            24,
            32
          ],
          "axis_label": "sequential decision timeline"
        }
      },
      {
        "componentInstanceId": "CHART-STREAM-005.notes.0",
        "componentType": "decision_card",
        "area": "notes",
        "dataBinding": {
          "source": "notes"
        },
        "config": {
          "card_style": "notes_legend"
        }
      }
    ],
    "data": {
      "summary": [
        {
          "label": "final LLR",
          "value": "16.0"
        },
        {
          "label": "alpha / beta",
          "value": "0.05 / 0.10"
        },
        {
          "label": "decision",
          "value": "accept H1"
        }
      ],
      "llr": [
        {
          "time": 1,
          "value": -0.4,
          "pointClass": "llr-point",
          "pointRadius": 3.5
        },
        {
          "time": 2,
          "value": -0.7,
          "pointClass": "llr-point",
          "pointRadius": 3.5
        },
        {
          "time": 3,
          "value": -0.5,
          "pointClass": "llr-point",
          "pointRadius": 3.5
        },
        {
          "time": 4,
          "value": -0.8,
          "pointClass": "llr-point",
          "pointRadius": 3.5
        },
        {
          "time": 5,
          "value": -0.4,
          "pointClass": "llr-point",
          "pointRadius": 3.5
        },
        {
          "time": 6,
          "value": -0.2,
          "pointClass": "llr-point",
          "pointRadius": 3.5
        },
        {
          "time": 7,
          "value": 0.1,
          "pointClass": "llr-point",
          "pointRadius": 3.5
        },
        {
          "time": 8,
          "value": 0.3,
          "pointClass": "llr-point",
          "pointRadius": 3.5
        },
        {
          "time": 9,
          "value": 0.6,
          "pointClass": "llr-point",
          "pointRadius": 3.5
        },
        {
          "time": 10,
          "value": 0.9,
          "pointClass": "llr-point",
          "pointRadius": 3.5
        },
        {
          "time": 11,
          "value": 1.3,
          "pointClass": "llr-point",
          "pointRadius": 3.5
        },
        {
          "time": 12,
          "value": 1.7,
          "pointClass": "llr-point",
          "pointRadius": 3.5
        },
        {
          "time": 13,
          "value": 2.0,
          "pointClass": "llr-point",
          "pointRadius": 3.5
        },
        {
          "time": 14,
          "value": 2.4,
          "pointClass": "llr-point",
          "pointRadius": 3.5
        },
        {
          "time": 15,
          "value": 2.9,
          "pointClass": "llr-point",
          "pointRadius": 3.5
        },
        {
          "time": 16,
          "value": 3.5,
          "pointClass": "llr-point",
          "pointRadius": 3.5
        },
        {
          "time": 17,
          "value": 4.2,
          "pointClass": "llr-point",
          "pointRadius": 3.5
        },
        {
          "time": 18,
          "value": 5.0,
          "pointClass": "llr-point",
          "pointRadius": 3.5
        },
        {
          "time": 19,
          "value": 5.9,
          "pointClass": "llr-point",
          "pointRadius": 3.5
        },
        {
          "time": 20,
          "value": 6.8,
          "pointClass": "llr-point",
          "pointRadius": 3.5
        },
        {
          "time": 21,
          "value": 7.7,
          "pointClass": "llr-point",
          "pointRadius": 3.5
        },
        {
          "time": 22,
          "value": 8.6,
          "pointClass": "llr-point",
          "pointRadius": 3.5
        },
        {
          "time": 23,
          "value": 9.4,
          "pointClass": "llr-point",
          "pointRadius": 3.5
        },
        {
          "time": 24,
          "value": 10.2,
          "pointClass": "llr-point",
          "pointRadius": 3.5
        },
        {
          "time": 25,
          "value": 11.0,
          "pointClass": "decision-point",
          "pointRadius": 4.8
        },
        {
          "time": 26,
          "value": 11.8,
          "pointClass": "decision-point",
          "pointRadius": 4.8
        },
        {
          "time": 27,
          "value": 12.6,
          "pointClass": "decision-point",
          "pointRadius": 4.8
        },
        {
          "time": 28,
          "value": 13.4,
          "pointClass": "decision-point",
          "pointRadius": 4.8
        },
        {
          "time": 29,
          "value": 14.1,
          "pointClass": "decision-point",
          "pointRadius": 4.8
        },
        {
          "time": 30,
          "value": 14.8,
          "pointClass": "decision-point",
          "pointRadius": 4.8
        },
        {
          "time": 31,
          "value": 15.4,
          "pointClass": "decision-point",
          "pointRadius": 4.8
        },
        {
          "time": 32,
          "value": 16.0,
          "pointClass": "decision-point",
          "pointRadius": 4.8
        }
      ],
      "error_rate": [
        {
          "time": 1,
          "value": 0.08
        },
        {
          "time": 2,
          "value": 0.09
        },
        {
          "time": 3,
          "value": 0.07
        },
        {
          "time": 4,
          "value": 0.1
        },
        {
          "time": 5,
          "value": 0.08
        },
        {
          "time": 6,
          "value": 0.09
        },
        {
          "time": 7,
          "value": 0.11
        },
        {
          "time": 8,
          "value": 0.1
        },
        {
          "time": 9,
          "value": 0.12
        },
        {
          "time": 10,
          "value": 0.13
        },
        {
          "time": 11,
          "value": 0.14
        },
        {
          "time": 12,
          "value": 0.15
        },
        {
          "time": 13,
          "value": 0.16
        },
        {
          "time": 14,
          "value": 0.17
        },
        {
          "time": 15,
          "value": 0.18
        },
        {
          "time": 16,
          "value": 0.2
        },
        {
          "time": 17,
          "value": 0.22
        },
        {
          "time": 18,
          "value": 0.24
        },
        {
          "time": 19,
          "value": 0.25
        },
        {
          "time": 20,
          "value": 0.27
        },
        {
          "time": 21,
          "value": 0.29
        },
        {
          "time": 22,
          "value": 0.3
        },
        {
          "time": 23,
          "value": 0.31
        },
        {
          "time": 24,
          "value": 0.32
        },
        {
          "time": 25,
          "value": 0.34
        },
        {
          "time": 26,
          "value": 0.35
        },
        {
          "time": 27,
          "value": 0.36
        },
        {
          "time": 28,
          "value": 0.35
        },
        {
          "time": 29,
          "value": 0.37
        },
        {
          "time": 30,
          "value": 0.38
        },
        {
          "time": 31,
          "value": 0.39
        },
        {
          "time": 32,
          "value": 0.4
        }
      ],
      "timeline": [
        {
          "start": 1,
          "end": 18,
          "role": "continue",
          "label": "continue"
        },
        {
          "start": 18,
          "end": 25,
          "role": "review",
          "label": "review"
        },
        {
          "start": 25,
          "end": 32,
          "role": "h1",
          "label": "accept H1"
        }
      ],
      "notes": [
        {
          "title": "해석",
          "text": "Error rate climbs from the early 0.08-0.15 range to 0.35-0.40. The LLR crosses the H1 boundary at t=25 and ends at 16.0, so SPRT accepts the error-increase drift hypothesis.",
          "legend": [
            {
              "label": "LLR",
              "class": "swatch-current"
            },
            {
              "label": "accept H1",
              "class": "swatch-high"
            },
            {
              "label": "accept H0",
              "class": "swatch-base"
            },
            {
              "label": "decision",
              "class": "swatch-marker"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-TEXT-001",
    "title": "CHART-TEXT-001 - 질의 임베딩 이동과 토픽 구성 변화",
    "originalPath": "./drift_report_charts/chart_text_001.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_stream_text_unc_var",
      "displayName": "source matching layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 120px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "임베딩 투영 산점도",
          "description": "Baseline cluster is on the left while current cluster shifts right and separates.",
          "headerHeight": 76,
          "stageInset": {
            "top": 84,
            "right": 16,
            "bottom": -8,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "의미 거리 추세",
          "description": "Cosine distance crosses threshold 0.36 at t=22 and reaches 0.58.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "토픽 비율과 분류 성능 곡선",
          "description": "Topic 3 rises from 0.20 to 0.48 (+28pt), with domain AUC 0.82.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "notes",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1,
          "stageInset": {
            "top": 0,
            "right": 0,
            "bottom": 0,
            "left": 0
          }
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-TEXT-001.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "dataBinding": {
          "source": "summary"
        },
        "config": {}
      },
      {
        "componentInstanceId": "CHART-TEXT-001.main.0",
        "componentType": "projection_scatter",
        "area": "main",
        "dataBinding": {
          "source": "projection"
        },
        "config": {
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 28,
            "bottom": 62,
            "left": 58
          },
          "x_min": -2.4,
          "x_max": 3.0,
          "y_min": -2.0,
          "y_max": 2.0,
          "x_ticks": [
            -2,
            -1,
            0,
            1,
            2
          ],
          "y_ticks": [
            -1.6,
            -0.8,
            0,
            0.8,
            1.6
          ],
          "x_axis_label": "UMAP-1",
          "y_axis_label": "UMAP-2",
          "group_class_map": {
            "baseline": "ref-point",
            "current": "cur-point"
          },
          "point_radius": 4,
          "diagonal_markers": [
            {
              "x0": -0.85,
              "y0": -0.12,
              "x1": 1.15,
              "y1": 0.4,
              "class": "centroid-line"
            }
          ],
          "point_highlights": [
            {
              "x": 1.15,
              "y": 0.4,
              "class": "alarm-point",
              "r": 7
            }
          ],
          "annotations": [
            {
              "text": "query embedding clusters separate",
              "x": 0.2,
              "y": 1.58,
              "class": "warning-text"
            }
          ]
        }
      },
      {
        "componentInstanceId": "CHART-TEXT-001.side_top.0",
        "componentType": "trend_line",
        "area": "side_top",
        "dataBinding": {
          "source": "distance"
        },
        "config": {
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 22,
            "bottom": 34,
            "left": 48
          },
          "x_min": 1,
          "x_max": 32,
          "y_min": 0,
          "y_max": 0.65,
          "x_ticks": [],
          "y_ticks": [
            0,
            0.2,
            0.4,
            0.6
          ],
          "x_axis_label": "centroid cosine distance",
          "y_axis_label": false,
          "line_class": "distance-line",
          "primary_point_class": "distance-point",
          "point_sample_every": 4,
          "point_radius": 3.4,
          "horizontal_markers": [
            {
              "y": 0.36,
              "class": "threshold-line"
            }
          ],
          "point_highlights": [
            {
              "x": 22,
              "class": "alarm-point",
              "r": 4.8
            },
            {
              "x": 23,
              "class": "alarm-point",
              "r": 4.8
            },
            {
              "x": 24,
              "class": "alarm-point",
              "r": 4.8
            },
            {
              "x": 25,
              "class": "alarm-point",
              "r": 4.8
            },
            {
              "x": 26,
              "class": "alarm-point",
              "r": 4.8
            },
            {
              "x": 27,
              "class": "alarm-point",
              "r": 4.8
            },
            {
              "x": 28,
              "class": "alarm-point",
              "r": 4.8
            },
            {
              "x": 29,
              "class": "alarm-point",
              "r": 4.8
            },
            {
              "x": 30,
              "class": "alarm-point",
              "r": 4.8
            },
            {
              "x": 31,
              "class": "alarm-point",
              "r": 4.8
            },
            {
              "x": 32,
              "class": "alarm-point",
              "r": 4.8
            }
          ],
          "annotations": [
            {
              "text": "threshold exceeded",
              "x": 19,
              "y": 0.56,
              "class": "warning-text"
            }
          ]
        }
      },
      {
        "componentInstanceId": "CHART-TEXT-001.side_bottom.0",
        "componentType": "bar_chart",
        "area": "side_bottom",
        "dataBinding": {
          "source": "topic_mix"
        },
        "config": {
          "bar_style": "horizontal_stacked",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 18,
            "right": 244,
            "bottom": 32,
            "left": 78
          },
          "category_field": "category",
          "series_fields": [
            "topic1",
            "topic2",
            "topic3"
          ],
          "series_classes": [
            "bar-topic-a",
            "bar-topic-b",
            "bar-topic-c"
          ],
          "first_y": 42,
          "row_gap": 40,
          "bar_height": 26,
          "caption": "topic mix",
          "caption_x": 166,
          "caption_y": 132,
          "value_label_field": "topic3_label"
        }
      },
      {
        "componentInstanceId": "CHART-TEXT-001.side_bottom.1",
        "componentType": "cumulative_curve",
        "area": "side_bottom",
        "dataBinding": {
          "source": "roc_small"
        },
        "config": {
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 24,
            "right": 42,
            "bottom": 43,
            "left": 294
          },
          "x_min": 0,
          "x_max": 1,
          "y_min": 0,
          "y_max": 1,
          "x_ticks": [],
          "y_ticks": [],
          "x_axis_label": "domain classifier",
          "axis_label_x": 372,
          "axis_label_y": 166,
          "y_axis_label": false,
          "line_class": "roc-line",
          "show_points": false,
          "diagonal_markers": [
            {
              "x0": 0,
              "y0": 0,
              "x1": 1,
              "y1": 1,
              "class": "random-line"
            }
          ],
          "annotations": [
            {
              "text": "ROC AUC 0.82",
              "x": 0.42,
              "y": 0.92,
              "class": "warning-text"
            }
          ]
        },
        "isOverlay": true
      },
      {
        "componentInstanceId": "CHART-TEXT-001.notes.0",
        "componentType": "decision_card",
        "area": "notes",
        "dataBinding": {
          "source": "notes"
        },
        "config": {
          "card_style": "notes_legend"
        }
      }
    ],
    "data": {
      "summary": [
        {
          "label": "cosine dist",
          "value": "0.58"
        },
        {
          "label": "topic shift",
          "value": "+28pt"
        },
        {
          "label": "domain AUC",
          "value": "0.82"
        }
      ],
      "projection": [
        {
          "x": -1.45,
          "y": -0.48,
          "group": "baseline"
        },
        {
          "x": 0.66,
          "y": 0.14,
          "group": "current"
        },
        {
          "x": -1.1836,
          "y": -0.5346,
          "group": "baseline"
        },
        {
          "x": 0.9899,
          "y": 0.0699,
          "group": "current"
        },
        {
          "x": -1.0584,
          "y": -0.6389,
          "group": "baseline"
        },
        {
          "x": 1.073,
          "y": -0.0511,
          "group": "current"
        },
        {
          "x": -1.0088,
          "y": -0.6787,
          "group": "baseline"
        },
        {
          "x": 1.1705,
          "y": -0.0686,
          "group": "current"
        },
        {
          "x": -0.8583,
          "y": -0.6107,
          "group": "baseline"
        },
        {
          "x": 1.514,
          "y": 0.0396,
          "group": "current"
        },
        {
          "x": -0.5785,
          "y": -0.5091,
          "group": "baseline"
        },
        {
          "x": 1.8287,
          "y": 0.1356,
          "group": "current"
        },
        {
          "x": -0.3301,
          "y": -0.485,
          "group": "baseline"
        },
        {
          "x": 1.8991,
          "y": 0.0969,
          "group": "current"
        },
        {
          "x": -0.2281,
          "y": -0.5647,
          "group": "baseline"
        },
        {
          "x": 2.0125,
          "y": -0.0271,
          "group": "current"
        },
        {
          "x": -1.5328,
          "y": -0.4911,
          "group": "baseline"
        },
        {
          "x": 0.6878,
          "y": 0.1017,
          "group": "current"
        },
        {
          "x": -1.3562,
          "y": -0.4989,
          "group": "baseline"
        },
        {
          "x": 0.9859,
          "y": 0.1886,
          "group": "current"
        },
        {
          "x": -1.068,
          "y": -0.4096,
          "group": "baseline"
        },
        {
          "x": 1.0455,
          "y": 0.3028,
          "group": "current"
        },
        {
          "x": -0.8413,
          "y": -0.3207,
          "group": "baseline"
        },
        {
          "x": 1.1761,
          "y": 0.2986,
          "group": "current"
        },
        {
          "x": -0.7592,
          "y": -0.3294,
          "group": "baseline"
        },
        {
          "x": 1.5412,
          "y": 0.1814,
          "group": "current"
        },
        {
          "x": -0.6929,
          "y": -0.4262,
          "group": "baseline"
        },
        {
          "x": 1.8215,
          "y": 0.1006,
          "group": "current"
        },
        {
          "x": -0.4905,
          "y": -0.5053,
          "group": "baseline"
        },
        {
          "x": 1.8723,
          "y": 0.1593,
          "group": "current"
        },
        {
          "x": -0.1994,
          "y": -0.4802,
          "group": "baseline"
        },
        {
          "x": 2.0213,
          "y": 0.2826,
          "group": "current"
        },
        {
          "x": -1.3571,
          "y": -0.2084,
          "group": "baseline"
        },
        {
          "x": 0.7141,
          "y": 0.4933,
          "group": "current"
        },
        {
          "x": -1.2909,
          "y": -0.1411,
          "group": "baseline"
        },
        {
          "x": 0.9755,
          "y": 0.3922,
          "group": "current"
        },
        {
          "x": -1.2087,
          "y": -0.1819,
          "group": "baseline"
        },
        {
          "x": 1.0198,
          "y": 0.2883,
          "group": "current"
        },
        {
          "x": -0.9819,
          "y": -0.2861,
          "group": "baseline"
        },
        {
          "x": 1.188,
          "y": 0.3141,
          "group": "current"
        },
        {
          "x": -0.6937,
          "y": -0.34,
          "group": "baseline"
        },
        {
          "x": 1.5662,
          "y": 0.4367,
          "group": "current"
        },
        {
          "x": -0.5173,
          "y": -0.2846,
          "group": "baseline"
        },
        {
          "x": 1.8081,
          "y": 0.4998,
          "group": "current"
        },
        {
          "x": -0.462,
          "y": -0.1804,
          "group": "baseline"
        },
        {
          "x": 1.8481,
          "y": 0.4229,
          "group": "current"
        },
        {
          "x": -0.3598,
          "y": -0.1414,
          "group": "baseline"
        },
        {
          "x": 2.0361,
          "y": 0.3041,
          "group": "current"
        },
        {
          "x": -1.4714,
          "y": -0.0401,
          "group": "baseline"
        },
        {
          "x": 0.7374,
          "y": 0.4749,
          "group": "current"
        },
        {
          "x": -1.1916,
          "y": -0.1415,
          "group": "baseline"
        },
        {
          "x": 0.9594,
          "y": 0.587,
          "group": "current"
        },
        {
          "x": -1.0413,
          "y": -0.1647,
          "group": "baseline"
        },
        {
          "x": 0.9974,
          "y": 0.6774,
          "group": "current"
        },
        {
          "x": -0.9916,
          "y": -0.0845,
          "group": "baseline"
        },
        {
          "x": 1.2054,
          "y": 0.6309,
          "group": "current"
        },
        {
          "x": -0.8663,
          "y": 0.0116,
          "group": "baseline"
        },
        {
          "x": 1.5875,
          "y": 0.5067,
          "group": "current"
        },
        {
          "x": -0.5999,
          "y": 0.0185,
          "group": "baseline"
        },
        {
          "x": 1.7895,
          "y": 0.4632,
          "group": "current"
        },
        {
          "x": -0.3336,
          "y": -0.0713,
          "group": "baseline"
        },
        {
          "x": 1.8278,
          "y": 0.5559,
          "group": "current"
        },
        {
          "x": -0.2085,
          "y": -0.1597,
          "group": "baseline"
        },
        {
          "x": 2.0559,
          "y": 0.6666,
          "group": "current"
        },
        {
          "x": -1.5188,
          "y": 0.0199,
          "group": "baseline"
        },
        {
          "x": 0.7565,
          "y": 0.8341,
          "group": "current"
        },
        {
          "x": -1.3683,
          "y": 0.1171,
          "group": "baseline"
        },
        {
          "x": 0.9385,
          "y": 0.7143,
          "group": "current"
        },
        {
          "x": -1.0884,
          "y": 0.1956,
          "group": "baseline"
        },
        {
          "x": 0.9795,
          "y": 0.6401,
          "group": "current"
        },
        {
          "x": -0.8401,
          "y": 0.1696,
          "group": "baseline"
        },
        {
          "x": 1.2274,
          "y": 0.706,
          "group": "current"
        },
        {
          "x": -0.7382,
          "y": 0.0676,
          "group": "baseline"
        },
        {
          "x": 1.6042,
          "y": 0.828,
          "group": "current"
        },
        {
          "x": -0.6828,
          "y": 0.001,
          "group": "baseline"
        },
        {
          "x": 1.7665,
          "y": 0.8505,
          "group": "current"
        },
        {
          "x": -0.5061,
          "y": 0.0426,
          "group": "baseline"
        },
        {
          "x": 1.8125,
          "y": 0.7448,
          "group": "current"
        },
        {
          "x": -0.2179,
          "y": 0.1469,
          "group": "baseline"
        },
        {
          "x": 2.0798,
          "y": 0.6457,
          "group": "current"
        },
        {
          "x": -1.3513,
          "y": 0.37,
          "group": "baseline"
        },
        {
          "x": 0.7704,
          "y": 0.8596,
          "group": "current"
        },
        {
          "x": -1.2693,
          "y": 0.3138,
          "group": "baseline"
        },
        {
          "x": 0.9138,
          "y": 0.9832,
          "group": "current"
        },
        {
          "x": -1.2029,
          "y": 0.2097,
          "group": "baseline"
        },
        {
          "x": 0.967,
          "y": 1.039,
          "group": "current"
        },
        {
          "x": -1.0004,
          "y": 0.1715,
          "group": "baseline"
        },
        {
          "x": 1.2528,
          "y": 0.9557,
          "group": "current"
        },
        {
          "x": -0.7094,
          "y": 0.241,
          "group": "baseline"
        },
        {
          "x": 1.6151,
          "y": 0.8397,
          "group": "current"
        },
        {
          "x": -0.5072,
          "y": 0.3421,
          "group": "baseline"
        },
        {
          "x": 1.7405,
          "y": 0.8388,
          "group": "current"
        },
        {
          "x": -0.441,
          "y": 0.3645,
          "group": "baseline"
        },
        {
          "x": 1.8031,
          "y": 0.9542,
          "group": "current"
        },
        {
          "x": -0.3587,
          "y": 0.2836,
          "group": "baseline"
        },
        {
          "x": 2.1064,
          "y": 1.0388,
          "group": "current"
        }
      ],
      "distance": [
        {
          "time": 1,
          "value": 0.08
        },
        {
          "time": 2,
          "value": 0.09
        },
        {
          "time": 3,
          "value": 0.1
        },
        {
          "time": 4,
          "value": 0.11
        },
        {
          "time": 5,
          "value": 0.1
        },
        {
          "time": 6,
          "value": 0.12
        },
        {
          "time": 7,
          "value": 0.13
        },
        {
          "time": 8,
          "value": 0.14
        },
        {
          "time": 9,
          "value": 0.16
        },
        {
          "time": 10,
          "value": 0.17
        },
        {
          "time": 11,
          "value": 0.18
        },
        {
          "time": 12,
          "value": 0.19
        },
        {
          "time": 13,
          "value": 0.21
        },
        {
          "time": 14,
          "value": 0.22
        },
        {
          "time": 15,
          "value": 0.24
        },
        {
          "time": 16,
          "value": 0.25
        },
        {
          "time": 17,
          "value": 0.27
        },
        {
          "time": 18,
          "value": 0.29
        },
        {
          "time": 19,
          "value": 0.31
        },
        {
          "time": 20,
          "value": 0.33
        },
        {
          "time": 21,
          "value": 0.35
        },
        {
          "time": 22,
          "value": 0.37
        },
        {
          "time": 23,
          "value": 0.4
        },
        {
          "time": 24,
          "value": 0.42
        },
        {
          "time": 25,
          "value": 0.45
        },
        {
          "time": 26,
          "value": 0.47
        },
        {
          "time": 27,
          "value": 0.49
        },
        {
          "time": 28,
          "value": 0.51
        },
        {
          "time": 29,
          "value": 0.53
        },
        {
          "time": 30,
          "value": 0.54
        },
        {
          "time": 31,
          "value": 0.56
        },
        {
          "time": 32,
          "value": 0.58
        }
      ],
      "topic_mix": [
        {
          "category": "baseline",
          "topic1": 0.48,
          "topic2": 0.32,
          "topic3": 0.2,
          "topic3_label": "20%"
        },
        {
          "category": "current",
          "topic1": 0.22,
          "topic2": 0.3,
          "topic3": 0.48,
          "topic3_label": "48%"
        }
      ],
      "roc_small": [
        {
          "time": 0,
          "value": 0
        },
        {
          "time": 0.08,
          "value": 0.35
        },
        {
          "time": 0.18,
          "value": 0.58
        },
        {
          "time": 0.34,
          "value": 0.75
        },
        {
          "time": 0.55,
          "value": 0.88
        },
        {
          "time": 1,
          "value": 1
        }
      ],
      "notes": [
        {
          "title": "해석",
          "text": "Semantic drift is shown through embedding separation, rising centroid cosine distance, and the topic mix shift toward topic 3 after t=22.",
          "legend": [
            {
              "label": "baseline",
              "class": "swatch-base"
            },
            {
              "label": "current",
              "class": "swatch-current-red"
            },
            {
              "label": "semantic distance",
              "class": "swatch-distance"
            },
            {
              "label": "topic shift",
              "class": "swatch-topic"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-TEXT-002",
    "title": "CHART-TEXT-002 - 텍스트 도메인 분류기 드리프트",
    "originalPath": "./drift_report_charts/chart_text_002.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_stream_text_unc_var",
      "displayName": "source matching layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 120px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "도메인 분류기 성능 곡선",
          "description": "ROC AUC 0.89 indicates a classifier can separate baseline and current text.",
          "headerHeight": 76,
          "stageInset": {
            "top": 84,
            "right": 16,
            "bottom": -8,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "분류기 점수 분포",
          "description": "Baseline score peak is 0.19/34 while current peak is 0.68/35.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "설명자 드리프트와 임베딩",
          "description": "refund policy 0.32 and enterprise SSO 0.25 are the top descriptor changes.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "notes",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1,
          "stageInset": {
            "top": 0,
            "right": 0,
            "bottom": 0,
            "left": 0
          }
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-TEXT-002.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "dataBinding": {
          "source": "summary"
        },
        "config": {}
      },
      {
        "componentInstanceId": "CHART-TEXT-002.main.0",
        "componentType": "cumulative_curve",
        "area": "main",
        "dataBinding": {
          "source": "roc"
        },
        "config": {
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 28,
            "right": 42,
            "bottom": 62,
            "left": 68
          },
          "x_min": 0,
          "x_max": 1,
          "y_min": 0,
          "y_max": 1,
          "x_ticks": [
            0,
            0.25,
            0.5,
            0.75,
            1
          ],
          "y_ticks": [
            0,
            0.25,
            0.5,
            0.75,
            1
          ],
          "x_axis_label": "false positive rate",
          "y_axis_label": "true positive rate",
          "line_class": "domain-roc-line",
          "primary_point_class": "cur-point",
          "point_sample_every": 1,
          "point_radius": 4.5,
          "diagonal_markers": [
            {
              "x0": 0,
              "y0": 0,
              "x1": 1,
              "y1": 1,
              "class": "random-line"
            }
          ],
          "annotations": [
            {
              "text": "domain classifier separates text domains (AUC 0.89)",
              "x": 0.38,
              "y": 0.88,
              "class": "callout"
            }
          ]
        }
      },
      {
        "componentInstanceId": "CHART-TEXT-002.side_top.0",
        "componentType": "distribution_view",
        "area": "side_top",
        "dataBinding": {
          "source": "scores"
        },
        "config": {
          "distribution_style": "density_area",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 24,
            "bottom": 34,
            "left": 44
          },
          "x_min": 0,
          "x_max": 1,
          "y_min": 0,
          "y_max": 40,
          "x_ticks": [],
          "y_ticks": [
            0,
            20,
            40
          ],
          "x_axis_label": "domain classifier score",
          "y_axis_label": false,
          "x_field": "score",
          "primary_value_field": "baseline",
          "secondary_value_field": "current",
          "primary_area_class": "base-area",
          "secondary_area_class": "current-red-area",
          "annotations": [
            {
              "text": "score distributions separate",
              "x": 0.39,
              "y": 36,
              "class": "warning-text"
            }
          ]
        }
      },
      {
        "componentInstanceId": "CHART-TEXT-002.side_bottom.0",
        "componentType": "feature_projection_view",
        "area": "side_bottom",
        "dataBinding": {
          "source": "descriptor_projection"
        },
        "config": {
          "view_box": [
            472,
            185
          ],
          "kind_field": "kind",
          "feature_kind": "feature",
          "point_kind": "point",
          "feature_name_field": "feature",
          "feature_value_field": "value",
          "feature_bar_class": "bar-fill",
          "feature_area": {
            "x": 120,
            "y": 18,
            "width": 150,
            "x_max": 0.34,
            "row_gap": 23,
            "bar_height": 14,
            "axis_y": 151
          },
          "projection_area": {
            "x0": 318,
            "x1": 430,
            "y0": 24,
            "y1": 142,
            "x_min": -1,
            "x_max": 1.5,
            "y_min": -0.8,
            "y_max": 1.2
          },
          "projection_frame": false,
          "crosshair": false,
          "group_class_map": {
            "baseline": "base-dot",
            "current": "text2-current-dot"
          },
          "point_radius": 3.5,
          "labels": [
            {
              "text": "descriptor drift",
              "x": 196,
              "y": 154,
              "class": "axis-label",
              "anchor": "middle"
            },
            {
              "text": "embedding split",
              "x": 390,
              "y": 154,
              "class": "axis-label",
              "anchor": "middle"
            }
          ],
          "point_coordinate_mode": "pixel"
        }
      },
      {
        "componentInstanceId": "CHART-TEXT-002.notes.0",
        "componentType": "decision_card",
        "area": "notes",
        "dataBinding": {
          "source": "notes"
        },
        "config": {
          "card_style": "notes_legend"
        }
      }
    ],
    "data": {
      "summary": [
        {
          "label": "ROC AUC",
          "value": "0.89"
        },
        {
          "label": "KS score",
          "value": "0.47"
        },
        {
          "label": "top descriptor",
          "value": "refund"
        }
      ],
      "roc": [
        {
          "time": 0,
          "value": 0
        },
        {
          "time": 0.04,
          "value": 0.32
        },
        {
          "time": 0.1,
          "value": 0.54
        },
        {
          "time": 0.2,
          "value": 0.71
        },
        {
          "time": 0.34,
          "value": 0.84
        },
        {
          "time": 0.52,
          "value": 0.92
        },
        {
          "time": 0.75,
          "value": 0.97
        },
        {
          "time": 1,
          "value": 1
        }
      ],
      "scores": [
        {
          "score": 0.05,
          "baseline": 22,
          "current": 0
        },
        {
          "score": 0.12,
          "baseline": 28,
          "current": 0
        },
        {
          "score": 0.19,
          "baseline": 34,
          "current": 1
        },
        {
          "score": 0.26,
          "baseline": 31,
          "current": 2
        },
        {
          "score": 0.33,
          "baseline": 24,
          "current": 4
        },
        {
          "score": 0.4,
          "baseline": 16,
          "current": 8
        },
        {
          "score": 0.47,
          "baseline": 9,
          "current": 14
        },
        {
          "score": 0.54,
          "baseline": 5,
          "current": 22
        },
        {
          "score": 0.61,
          "baseline": 2,
          "current": 31
        },
        {
          "score": 0.68,
          "baseline": 1,
          "current": 35
        },
        {
          "score": 0.75,
          "baseline": 0,
          "current": 30
        },
        {
          "score": 0.82,
          "baseline": 0,
          "current": 21
        },
        {
          "score": 0.89,
          "baseline": 0,
          "current": 12
        },
        {
          "score": 0.96,
          "baseline": 0,
          "current": 5
        }
      ],
      "descriptor_projection": [
        {
          "kind": "point",
          "x": 318,
          "y": 94.0,
          "group": "baseline"
        },
        {
          "kind": "point",
          "x": 363,
          "y": 56.0,
          "group": "current"
        },
        {
          "kind": "point",
          "x": 329,
          "y": 97.36588393923158,
          "group": "baseline"
        },
        {
          "kind": "point",
          "x": 374,
          "y": 54.16120922347256,
          "group": "current"
        },
        {
          "kind": "point",
          "x": 340,
          "y": 97.63718970730272,
          "group": "baseline"
        },
        {
          "kind": "point",
          "x": 385,
          "y": 50.33541265381143,
          "group": "current"
        },
        {
          "kind": "point",
          "x": 351,
          "y": 94.56448003223947,
          "group": "baseline"
        },
        {
          "kind": "point",
          "x": 396,
          "y": 48.04003001359822,
          "group": "current"
        },
        {
          "kind": "point",
          "x": 362,
          "y": 90.9727900187683,
          "group": "baseline"
        },
        {
          "kind": "point",
          "x": 407,
          "y": 49.38542551654555,
          "group": "current"
        },
        {
          "kind": "point",
          "x": 373,
          "y": 90.16430290134744,
          "group": "baseline"
        },
        {
          "kind": "point",
          "x": 418,
          "y": 53.13464874185291,
          "group": "current"
        },
        {
          "kind": "point",
          "x": 318,
          "y": 102.8823380072043,
          "group": "baseline"
        },
        {
          "kind": "point",
          "x": 363,
          "y": 65.84068114660147,
          "group": "current"
        },
        {
          "kind": "point",
          "x": 329,
          "y": 106.62794639487515,
          "group": "baseline"
        },
        {
          "kind": "point",
          "x": 374,
          "y": 65.01560901737322,
          "group": "current"
        },
        {
          "kind": "point",
          "x": 340,
          "y": 107.95743298649353,
          "group": "baseline"
        },
        {
          "kind": "point",
          "x": 385,
          "y": 61.41799986476555,
          "group": "current"
        },
        {
          "kind": "point",
          "x": 351,
          "y": 105.64847394096702,
          "group": "baseline"
        },
        {
          "kind": "point",
          "x": 396,
          "y": 58.35547895246129,
          "group": "current"
        },
        {
          "kind": "point",
          "x": 362,
          "y": 101.82391555644251,
          "group": "baseline"
        },
        {
          "kind": "point",
          "x": 407,
          "y": 58.64371388369419,
          "group": "current"
        },
        {
          "kind": "point",
          "x": 373,
          "y": 100.00003917379719,
          "group": "baseline"
        },
        {
          "kind": "point",
          "x": 418,
          "y": 62.0177027919522,
          "group": "current"
        },
        {
          "kind": "point",
          "x": 318,
          "y": 111.85370832799826,
          "group": "baseline"
        },
        {
          "kind": "point",
          "x": 363,
          "y": 75.37541583492997,
          "group": "current"
        },
        {
          "kind": "point",
          "x": 329,
          "y": 115.68066814730656,
          "group": "baseline"
        },
        {
          "kind": "point",
          "x": 374,
          "y": 75.62978712580079,
          "group": "current"
        },
        {
          "kind": "point",
          "x": 340,
          "y": 117.96242942277948,
          "group": "baseline"
        },
        {
          "kind": "point",
          "x": 385,
          "y": 72.54694887283134,
          "group": "current"
        },
        {
          "kind": "point",
          "x": 351,
          "y": 116.60115136062846,
          "group": "baseline"
        },
        {
          "kind": "point",
          "x": 396,
          "y": 68.96124834856471,
          "group": "current"
        },
        {
          "kind": "point",
          "x": 362,
          "y": 112.84838673333974,
          "group": "baseline"
        },
        {
          "kind": "point",
          "x": 407,
          "y": 68.16936207870646,
          "group": "current"
        },
        {
          "kind": "point",
          "x": 373,
          "y": 110.15441003248178,
          "group": "baseline"
        },
        {
          "kind": "point",
          "x": 418,
          "y": 70.8993466477936,
          "group": "current"
        },
        {
          "kind": "feature",
          "feature": "refund policy",
          "value": 0.32,
          "display_value": "0.32",
          "class": "bar-fill hot"
        },
        {
          "kind": "feature",
          "feature": "enterprise SSO",
          "value": 0.25,
          "display_value": "0.25",
          "class": "bar-fill"
        },
        {
          "kind": "feature",
          "feature": "invoice issue",
          "value": 0.18,
          "display_value": "0.18",
          "class": "bar-fill"
        },
        {
          "kind": "feature",
          "feature": "API latency",
          "value": 0.14,
          "display_value": "0.14",
          "class": "bar-fill"
        },
        {
          "kind": "feature",
          "feature": "legacy flow",
          "value": 0.11,
          "display_value": "0.11",
          "class": "bar-fill"
        }
      ],
      "notes": [
        {
          "title": "해석",
          "text": "Text domain classifier drift is supported by ROC AUC 0.89, KS 0.47, separated classifier-score distributions, and refund-policy descriptor drift.",
          "legend": [
            {
              "label": "baseline",
              "class": "swatch-base"
            },
            {
              "label": "current",
              "class": "swatch-current-red"
            },
            {
              "label": "ROC",
              "class": "swatch-roc"
            },
            {
              "label": "descriptor drift",
              "class": "swatch-desc"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-UNC-001",
    "title": "CHART-UNC-001 - 신뢰도 하락과 엔트로피 상승",
    "originalPath": "./drift_report_charts/chart_unc_001.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_stream_text_unc_var",
      "displayName": "source matching layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 120px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "신뢰도/엔트로피 분포",
          "description": "Baseline peak is 0.82/41, while current peak shifts lower to 0.47/38.",
          "headerHeight": 76,
          "stageInset": {
            "top": 84,
            "right": 16,
            "bottom": -8,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "불확실성 추세",
          "description": "Entropy crosses threshold 0.55 at t=15 and reaches 0.77.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "보정 곡선과 클래스 막대",
          "description": "ECE is 0.12 and class C uncertainty is highest at 0.46.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "notes",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1,
          "stageInset": {
            "top": 0,
            "right": 0,
            "bottom": 0,
            "left": 0
          }
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-UNC-001.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "dataBinding": {
          "source": "summary"
        },
        "config": {}
      },
      {
        "componentInstanceId": "CHART-UNC-001.main.0",
        "componentType": "distribution_view",
        "area": "main",
        "dataBinding": {
          "source": "confidence"
        },
        "config": {
          "distribution_style": "density_area",
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 24,
            "right": 28,
            "bottom": 62,
            "left": 58
          },
          "x_min": 0.05,
          "x_max": 0.96,
          "y_min": 0,
          "y_max": 44,
          "x_ticks": [
            0.1,
            0.3,
            0.5,
            0.7,
            0.9
          ],
          "y_ticks": [
            0,
            10,
            20,
            30,
            40
          ],
          "x_axis_label": "softmax confidence",
          "y_axis_label": "density",
          "x_field": "confidence",
          "primary_value_field": "baseline",
          "secondary_value_field": "current",
          "primary_area_class": "base-area",
          "secondary_area_class": "current-area",
          "vertical_markers": [
            {
              "x": 0.5,
              "class": "threshold-line",
              "label": "low-confidence region",
              "label_y": 34,
              "label_dx": 10,
              "label_class": "warning-text"
            }
          ],
          "annotations": [
            {
              "text": "current confidence shifts lower",
              "x": 0.32,
              "y": 40,
              "class": "warning-text"
            }
          ]
        }
      },
      {
        "componentInstanceId": "CHART-UNC-001.side_top.0",
        "componentType": "trend_line",
        "area": "side_top",
        "dataBinding": {
          "source": "entropy"
        },
        "config": {
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 22,
            "bottom": 34,
            "left": 48
          },
          "x_min": 1,
          "x_max": 24,
          "y_min": 0.15,
          "y_max": 0.82,
          "x_ticks": [],
          "y_ticks": [
            0.2,
            0.5,
            0.8
          ],
          "x_axis_label": "time index",
          "y_axis_label": false,
          "line_class": "entropy-line",
          "primary_point_class": "entropy-point",
          "point_sample_every": 3,
          "point_radius": 3.3,
          "horizontal_markers": [
            {
              "y": 0.55,
              "class": "threshold-line"
            }
          ],
          "point_highlights": [
            {
              "x": 15,
              "class": "entropy-point",
              "r": 4.7
            },
            {
              "x": 16,
              "class": "entropy-point",
              "r": 4.7
            },
            {
              "x": 17,
              "class": "entropy-point",
              "r": 4.7
            },
            {
              "x": 18,
              "class": "entropy-point",
              "r": 4.7
            },
            {
              "x": 19,
              "class": "entropy-point",
              "r": 4.7
            },
            {
              "x": 20,
              "class": "entropy-point",
              "r": 4.7
            },
            {
              "x": 21,
              "class": "entropy-point",
              "r": 4.7
            },
            {
              "x": 22,
              "class": "entropy-point",
              "r": 4.7
            },
            {
              "x": 23,
              "class": "entropy-point",
              "r": 4.7
            },
            {
              "x": 24,
              "class": "entropy-point",
              "r": 4.7
            }
          ],
          "annotations": [
            {
              "text": "threshold crossed",
              "x": 13,
              "y": 0.75,
              "class": "warning-text"
            }
          ]
        }
      },
      {
        "componentInstanceId": "CHART-UNC-001.side_bottom.0",
        "componentType": "cumulative_curve",
        "area": "side_bottom",
        "dataBinding": {
          "source": "calibration"
        },
        "config": {
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 16,
            "right": 264,
            "bottom": 34,
            "left": 46
          },
          "x_min": 0,
          "x_max": 1,
          "y_min": 0,
          "y_max": 1,
          "x_ticks": [],
          "y_ticks": [],
          "x_axis_label": "calibration",
          "axis_label_x": 124,
          "axis_label_y": 177,
          "y_axis_label": false,
          "line_class": "calibration-line",
          "primary_point_class": "current-point",
          "point_sample_every": 1,
          "point_radius": 4,
          "diagonal_markers": [
            {
              "x0": 0,
              "y0": 0,
              "x1": 1,
              "y1": 1,
              "class": "perfect-line"
            }
          ],
          "pixel_bars": [
            {
              "source": "class_uncertainty",
              "category_field": "label",
              "value_field": "value",
              "x": 290,
              "y": 30,
              "width": 162,
              "x_max": 0.5,
              "row_gap": 27,
              "bar_height": 14,
              "bar_class": "bar-base",
              "over_class": "bar-class",
              "threshold": 0.45,
              "caption": "class uncertainty",
              "caption_x": 360,
              "caption_y": 177
            }
          ]
        }
      },
      {
        "componentInstanceId": "CHART-UNC-001.notes.0",
        "componentType": "decision_card",
        "area": "notes",
        "dataBinding": {
          "source": "notes"
        },
        "config": {
          "card_style": "notes_legend"
        }
      }
    ],
    "data": {
      "summary": [
        {
          "label": "entropy",
          "value": "0.77"
        },
        {
          "label": "ECE",
          "value": "0.12"
        },
        {
          "label": "alarm",
          "value": "t=15"
        }
      ],
      "confidence": [
        {
          "confidence": 0.05,
          "baseline": 0,
          "current": 3
        },
        {
          "confidence": 0.12,
          "baseline": 0,
          "current": 7
        },
        {
          "confidence": 0.19,
          "baseline": 1,
          "current": 12
        },
        {
          "confidence": 0.26,
          "baseline": 2,
          "current": 20
        },
        {
          "confidence": 0.33,
          "baseline": 4,
          "current": 29
        },
        {
          "confidence": 0.4,
          "baseline": 7,
          "current": 36
        },
        {
          "confidence": 0.47,
          "baseline": 10,
          "current": 38
        },
        {
          "confidence": 0.54,
          "baseline": 15,
          "current": 31
        },
        {
          "confidence": 0.61,
          "baseline": 22,
          "current": 24
        },
        {
          "confidence": 0.68,
          "baseline": 30,
          "current": 16
        },
        {
          "confidence": 0.75,
          "baseline": 37,
          "current": 9
        },
        {
          "confidence": 0.82,
          "baseline": 41,
          "current": 5
        },
        {
          "confidence": 0.89,
          "baseline": 35,
          "current": 2
        },
        {
          "confidence": 0.96,
          "baseline": 22,
          "current": 1
        }
      ],
      "entropy": [
        {
          "time": 1,
          "value": 0.22
        },
        {
          "time": 2,
          "value": 0.23
        },
        {
          "time": 3,
          "value": 0.24
        },
        {
          "time": 4,
          "value": 0.24
        },
        {
          "time": 5,
          "value": 0.26
        },
        {
          "time": 6,
          "value": 0.27
        },
        {
          "time": 7,
          "value": 0.28
        },
        {
          "time": 8,
          "value": 0.3
        },
        {
          "time": 9,
          "value": 0.33
        },
        {
          "time": 10,
          "value": 0.36
        },
        {
          "time": 11,
          "value": 0.39
        },
        {
          "time": 12,
          "value": 0.43
        },
        {
          "time": 13,
          "value": 0.47
        },
        {
          "time": 14,
          "value": 0.52
        },
        {
          "time": 15,
          "value": 0.57
        },
        {
          "time": 16,
          "value": 0.61
        },
        {
          "time": 17,
          "value": 0.65
        },
        {
          "time": 18,
          "value": 0.68
        },
        {
          "time": 19,
          "value": 0.7
        },
        {
          "time": 20,
          "value": 0.72
        },
        {
          "time": 21,
          "value": 0.74
        },
        {
          "time": 22,
          "value": 0.75
        },
        {
          "time": 23,
          "value": 0.76
        },
        {
          "time": 24,
          "value": 0.77
        }
      ],
      "calibration": [
        {
          "time": 0.1,
          "value": 0.06
        },
        {
          "time": 0.3,
          "value": 0.21
        },
        {
          "time": 0.5,
          "value": 0.38
        },
        {
          "time": 0.7,
          "value": 0.52
        },
        {
          "time": 0.9,
          "value": 0.66
        }
      ],
      "class_uncertainty": [
        {
          "label": "A",
          "value": 0.19,
          "class": "bar-base"
        },
        {
          "label": "B",
          "value": 0.31,
          "class": "bar-base"
        },
        {
          "label": "C",
          "value": 0.46,
          "class": "bar-class"
        },
        {
          "label": "D",
          "value": 0.28,
          "class": "bar-base"
        }
      ],
      "notes": [
        {
          "title": "해석",
          "text": "Uncertainty drift is shown by a lower confidence distribution, entropy crossing 0.55 at t=15, calibration degradation, and high class-C uncertainty.",
          "legend": [
            {
              "label": "baseline",
              "class": "swatch-base"
            },
            {
              "label": "current",
              "class": "swatch-current"
            },
            {
              "label": "uncertainty",
              "class": "swatch-uncertainty"
            },
            {
              "label": "threshold",
              "class": "swatch-threshold"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  },
  {
    "chartId": "CHART-VAR-001",
    "title": "CHART-VAR-001 - 현재 구간에서 커진 값의 변동성",
    "originalPath": "./drift_report_charts/chart_var_001.html",
    "layout": {
      "layoutType": "semantic_grid",
      "presetCode": "source_stream_text_unc_var",
      "displayName": "source matching layout",
      "columns": 12,
      "rows": 4,
      "gridTemplateRows": "76px 250px 250px 120px",
      "gap": "16px",
      "showAreaLabels": false,
      "areas": [
        {
          "area": "summary",
          "role": "summary",
          "x": 7,
          "y": 0,
          "w": 5,
          "h": 1
        },
        {
          "area": "main",
          "role": "primary_visual",
          "x": 0,
          "y": 1,
          "w": 7,
          "h": 2,
          "title": "분포 폭과 상자 비교",
          "description": "기준 SD 6.5보다 현재 SD 10.6이 커지고, whisker도 31.0~77.5로 넓어진다.",
          "headerHeight": 76,
          "stageInset": {
            "top": 84,
            "right": 16,
            "bottom": -8,
            "left": 16
          }
        },
        {
          "area": "side_top",
          "role": "secondary_visual",
          "x": 7,
          "y": 1,
          "w": 5,
          "h": 1,
          "title": "분산 비교",
          "description": "분산 42.3에서 112.4로 2.66배 증가한다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "side_bottom",
          "role": "secondary_visual",
          "x": 7,
          "y": 2,
          "w": 5,
          "h": 1,
          "title": "절대편차 변화",
          "description": "평균 절대편차가 5.1에서 8.7로 +3.6 커지고 p=0.012다.",
          "headerHeight": 65,
          "stageInset": {
            "top": 76,
            "right": 16,
            "bottom": 8,
            "left": 16
          }
        },
        {
          "area": "notes",
          "role": "notes",
          "x": 0,
          "y": 3,
          "w": 12,
          "h": 1,
          "stageInset": {
            "top": 0,
            "right": 0,
            "bottom": 0,
            "left": 0
          }
        }
      ]
    },
    "components": [
      {
        "componentInstanceId": "CHART-VAR-001.summary.0",
        "componentType": "decision_card",
        "area": "summary",
        "dataBinding": {
          "source": "summary"
        },
        "config": {}
      },
      {
        "componentInstanceId": "CHART-VAR-001.main.0",
        "componentType": "distribution_view",
        "area": "main",
        "dataBinding": {
          "source": "spread"
        },
        "config": {
          "distribution_style": "violin_summary",
          "view_box": [
            630,
            440
          ],
          "margin": {
            "top": 22,
            "right": 28,
            "bottom": 60,
            "left": 58
          },
          "y_min": 28,
          "y_max": 82,
          "y_ticks": [
            30,
            40,
            50,
            60,
            70,
            80
          ],
          "y_axis_label": "feature value",
          "category_field": "label",
          "center_field": "center",
          "median_field": "median",
          "q1_field": "q1",
          "q3_field": "q3",
          "low_field": "low",
          "high_field": "high",
          "density_field": "density",
          "violin_width": 74,
          "x_positions": [
            243,
            448
          ],
          "violin_classes": [
            "ref-fill",
            "cur-fill"
          ],
          "box_class": "summary-box",
          "center_class": "center-line",
          "median_class": "median-line",
          "annotations": [
            {
              "text": "분산비 2.66x: 현재 구간의 폭이 넓어짐",
              "x": 315,
              "y": 34,
              "class": "callout",
              "anchor": "middle"
            }
          ],
          "mean_field": "mean",
          "mean_line_class": "mean-line-solid",
          "mean_label_class": "callout"
        }
      },
      {
        "componentInstanceId": "CHART-VAR-001.side_top.0",
        "componentType": "bar_chart",
        "area": "side_top",
        "dataBinding": {
          "source": "variance"
        },
        "config": {
          "bar_style": "vertical_grouped",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 12,
            "right": 26,
            "bottom": 36,
            "left": 74
          },
          "category_field": "label",
          "series_fields": [
            "variance"
          ],
          "series_classes": [
            "ref-bar"
          ],
          "series_class_fields": [
            "class"
          ],
          "value_label_fields": [
            "display"
          ],
          "show_value_labels": true,
          "bar_width": 74,
          "group_padding": 72,
          "y_max": 130,
          "y_ticks": [
            0,
            50,
            100
          ],
          "x_axis_label": "variance ratio = 2.66x",
          "axis_label_y": 27
        }
      },
      {
        "componentInstanceId": "CHART-VAR-001.side_bottom.0",
        "componentType": "bar_chart",
        "area": "side_bottom",
        "dataBinding": {
          "source": "deviation"
        },
        "config": {
          "bar_style": "horizontal_threshold",
          "view_box": [
            472,
            185
          ],
          "margin": {
            "top": 16,
            "right": 28,
            "bottom": 34,
            "left": 118
          },
          "category_field": "label",
          "value_field": "value",
          "value_label_field": "display",
          "threshold_field": "threshold",
          "x_max": 10,
          "first_y": 26,
          "row_gap": 43,
          "bar_height": 18,
          "bar_class": "ref-bar",
          "over_class": "deviation-bar",
          "caption": "Levene p=0.012"
        }
      },
      {
        "componentInstanceId": "CHART-VAR-001.notes.0",
        "componentType": "decision_card",
        "area": "notes",
        "dataBinding": {
          "source": "notes"
        },
        "config": {
          "card_style": "notes_legend"
        }
      }
    ],
    "data": {
      "summary": [
        {
          "label": "Variance ratio",
          "value": "2.66"
        },
        {
          "label": "p-value",
          "value": "0.012"
        },
        {
          "label": "절대편차 변화",
          "value": "+3.6"
        }
      ],
      "spread": [
        {
          "label": "기준",
          "variance": 42.3,
          "sd": 6.5,
          "center": 52.0,
          "q1": 47.6,
          "median": 52.1,
          "q3": 56.5,
          "low": 39.5,
          "high": 64.0,
          "absDev": 5.1,
          "density": [
            [
              39,
              0.1
            ],
            [
              43,
              0.36
            ],
            [
              47,
              0.72
            ],
            [
              51,
              0.98
            ],
            [
              55,
              0.88
            ],
            [
              59,
              0.52
            ],
            [
              63,
              0.2
            ],
            [
              67,
              0.06
            ]
          ],
          "class": "ref-fill",
          "mean": 52.0,
          "meanLabel": "기준 SD 6.5"
        },
        {
          "label": "현재",
          "variance": 112.4,
          "sd": 10.6,
          "center": 52.6,
          "q1": 44.0,
          "median": 52.3,
          "q3": 61.8,
          "low": 31.0,
          "high": 77.5,
          "absDev": 8.7,
          "density": [
            [
              31,
              0.07
            ],
            [
              37,
              0.24
            ],
            [
              43,
              0.52
            ],
            [
              49,
              0.76
            ],
            [
              55,
              0.82
            ],
            [
              61,
              0.66
            ],
            [
              67,
              0.39
            ],
            [
              73,
              0.18
            ],
            [
              78,
              0.06
            ]
          ],
          "class": "cur-fill",
          "mean": 52.6,
          "meanLabel": "현재 SD 10.6"
        }
      ],
      "variance": [
        {
          "label": "기준 SD 6.5",
          "variance": 42.3,
          "display": "42.3",
          "class": "ref-bar"
        },
        {
          "label": "현재 SD 10.6",
          "variance": 112.4,
          "display": "112.4",
          "class": "cur-bar"
        }
      ],
      "deviation": [
        {
          "label": "기준 |x-center|",
          "value": 5.1,
          "display": "5.1",
          "threshold": 0,
          "class": "ref-bar"
        },
        {
          "label": "현재 |x-center|",
          "value": 8.7,
          "display": "8.7",
          "threshold": 0,
          "class": "deviation-bar"
        },
        {
          "label": "분산비",
          "value": 6.65,
          "display": "2.66x",
          "threshold": 3.75,
          "class": "ratio-bar"
        }
      ],
      "notes": [
        {
          "title": "해석",
          "text": "이 예시에서는 중심값이 52.0에서 52.6으로 거의 유지되지만 분산은 42.3에서 112.4로 2.66배 커진다. Levene p-value 0.012와 절대편차 +3.6이 함께 나타나므로 현재 구간의 값 퍼짐이 커진 분산 drift 후보로 읽는다. 평균 이동이나 일부 이상치만 만든 변화인지는 평균 chart와 tail/outlier 점검으로 분리 확인해야 한다.",
          "legend": [
            {
              "label": "기준 구간",
              "class": "swatch-reference"
            },
            {
              "label": "현재 구간",
              "class": "swatch-current-red"
            },
            {
              "label": "분산/편차",
              "class": "swatch-spread"
            },
            {
              "label": "판단 기준",
              "class": "swatch-threshold"
            }
          ]
        }
      ]
    },
    "reproduction": {
      "status": "designed",
      "issues": [
        "Builder에서 저장된 chart payload를 그대로 사용했다.",
        "layout, component area, data는 generator가 재조합하지 않았다."
      ]
    }
  }
];
