# Drift Control Plane Testing

이 폴더는 drift monitoring 서버군의 통합 테스트 하네스와 테스트 산출물을 둔다.

## 문서

- [test_requirements.md](./test_requirements.md): 테스트 요구사항, 테스트 계층, artifact 저장 정책
- [test_harness_implementation_design.md](./test_harness_implementation_design.md): 하네스 모듈 구조와 실행 흐름

## 실행

Headless Mode A CASE-010 실행:

```powershell
python -m testing.harness.main --scenario testing/harness/scenarios/case010_mode_a.json
```

결과는 다음 위치에 저장된다.

```text
testing/runs/{run_id}/
```

