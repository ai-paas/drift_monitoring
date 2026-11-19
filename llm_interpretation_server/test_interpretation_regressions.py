import json
import unittest
from unittest.mock import patch

from llm_interpretation_server import interpretation_server as server


class InterpretationRegressionTests(unittest.TestCase):
    def test_double_escaped_newlines_preserve_korean_and_existing_newlines(self):
        for separator in (r"\n", r"\r\n", "\n"):
            detail = separator.join(["한국어 해석 첫 번째 문장입니다.", "두 번째 문장도 유지합니다."])
            raw = json.dumps({
                "summary": "한국어 종합 해석 요약입니다.",
                "detail": detail,
                "componentNotes": [{
                    "componentInstanceId": "tree", "summary": "트리 해석 요약입니다.",
                    "detail": detail,
                }],
            }, ensure_ascii=False)
            result = server.chart_output_from_codex(raw)
            self.assertIn("\n두 번째", result["detail"])
            self.assertNotIn(r"\n", result["detail"])
            self.assertEqual(result["detail"], result["componentNotes"][0]["detail"])

    def test_peak_and_reset_rows_survive_sampling_with_custom_field(self):
        rows = [{"step": i, "nodes": 0} for i in range(32)]
        rows[21]["nodes"] = 64
        rows[22]["nodes"] = 0
        instance = {"componentType": "tree", "config": {"secondary_value_field": "nodes"}}
        with patch.object(server, "component_knowledge", return_value=server.ComponentKnowledge("tree")), \
             patch.object(server, "data_for", return_value=rows), \
             patch.object(server, "area_metadata", return_value={}), \
             patch.object(server, "component_guide_text", return_value=""), \
             patch.object(server, "llm_component_context", return_value={}), \
             patch.object(server, "visual_encoding_note", return_value=""):
            context = server.component_chart_context({}, instance, {})
        self.assertEqual(context["timeEvidence"], [rows[21], rows[22]])
        self.assertNotIn(rows[21], context["dataSample"]["head"])


if __name__ == "__main__":
    unittest.main()
