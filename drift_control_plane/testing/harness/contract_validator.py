from __future__ import annotations

from typing import Any

from .models import ValidationResult


class ContractValidator:
    def validate_envelope(self, name: str, response_json: Any) -> ValidationResult:
        if not isinstance(response_json, dict):
            return ValidationResult(name, "failed", "response is not a JSON object")

        missing = [key for key in ("ok", "data", "error") if key not in response_json]
        if missing:
            return ValidationResult(name, "failed", "response envelope is missing fields", {"missing": missing})

        if response_json.get("ok") is not True:
            return ValidationResult(name, "failed", "response ok is not true", {"error": response_json.get("error")})

        return ValidationResult(name, "passed", "response envelope is valid")

    def validate_required_paths(self, name: str, response_json: Any, paths: list[str]) -> list[ValidationResult]:
        results: list[ValidationResult] = []
        for path in paths:
            found = self._path_exists(response_json, path)
            status = "passed" if found else "failed"
            message = "required path exists" if found else "required path is missing"
            results.append(ValidationResult(f"{name}:{path}", status, message, {"path": path}))
        return results

    def _path_exists(self, value: Any, path: str) -> bool:
        current = value
        for part in path.split("."):
            if isinstance(current, dict) and part in current:
                current = current[part]
                continue
            return False
        return True

