# Runtime Methods

이 폴더는 drift method 알고리즘 구현을 보관하는 곳이 아니다.

drift method의 실제 구현과 단위 테스트는 다음 위치에서 관리한다.

```text
drift_algorithm_impl/
```

이 폴더의 책임은 Drift Server 실행 환경에 맞는 wrapper를 제공하는 것이다.

```text
source_method_assignment
bucket
previous method_state
  -> drift_algorithm_impl 호출
  -> method_run result_json 형태로 변환
  -> nextState/event/metrics/diagnostics 반환
```

따라서 여기에 새 파일을 추가할 때는 알고리즘을 새로 구현하지 말고,
`drift_algorithm_impl.drift_algorithm.methods.*`를 호출하는 adapter/wrapper만 작성한다.
