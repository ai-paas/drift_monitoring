# HAT 알고리즘 변종 목록

## 1. 목적

이 문서는 `HAT`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 HAT 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. HAT의 위치

```text
methodFamily HAT
       ├─ algorithmVariant HAT_ADWIN_NODE_MONITORING
       └─ algorithmVariant HAT_ALTERNATE_TREE_REPLACEMENT
```

`HAT`는 Hoeffding Adaptive Tree 계열에 속한다. 온라인 트리 학습과 drift detector를 결합해 감지와 적응을 함께 수행한다.

---

## 3. 공통 개념

```text
methodFamily HAT
  purpose ->
    온라인 트리 학습과 drift detector를 결합해 감지와 적응을 함께 수행한다.

  commonOutputs ->
    TEST_STATISTIC_OR_DISTANCE
    P_VALUE_OR_SCORE_OPTIONAL
    ALARM_STATE_OPTIONAL

  commonCautions ->
    detector 결과만으로 원인, 성능 저하, concept drift를 확정하지 않는다.
    reference 기간, current 기간, sample size, threshold 근거를 함께 보고한다.
    label이 없으면 supervised concept drift 또는 performance drift 확정 표현을 피한다.
```

---

## 변종: HAT_ADWIN_NODE_MONITORING

`HAT_ADWIN_NODE_MONITORING`은 Hoeffding Adaptive Tree 내부 노드나 분기에서 ADWIN 같은 drift detector가 성능 변화를 감시하는 변종이다. 온라인 분류기가 새 label stream을 받으면서 학습하고, 특정 노드의 오류율이나 정확도 흐름이 달라질 때 warning 또는 drift 상태를 기록한다. 출력은 node별 drift state, online accuracy, detector statistic 또는 alarm event로 해석한다.

사용 상황:
- label이 지속적으로 들어오는 online adaptive classifier 운영 환경에서
- 전체 모델 정확도보다 트리 내부의 특정 분기 또는 노드가 불안정한지 확인하고 싶을 때
- drift 감지와 모델 적응 과정을 함께 보고해야 할 때

해석 방법:
- node drift state가 warning에서 drift로 전환되면 해당 노드의 예측 성능 흐름이 기준보다 악화됐다는 후보 신호로 본다.
- online accuracy가 하락하고 detector alarm이 같은 시점에 발생하면 supervised error-rate 변화 근거가 강해진다.
- node별 alarm 수와 위치를 보면 변화가 전체 tree에 퍼졌는지 특정 decision path에 집중됐는지 설명할 수 있다.
- 보고서에서는 alarm 시점, 영향을 받은 노드, 전후 accuracy 변화를 함께 적는다.

주의점:
- label 지연이 크거나 label 품질이 불안정하면 detector state가 실제 concept drift가 아니라 label stream 문제를 반영할 수 있다.
- 내부 detector의 delta, window, warning 설정을 모르면 alarm 민감도를 해석하기 어렵다.
- 노드 단위 alarm만으로 업무 원인이나 전체 모델 성능 저하를 확정하지 않는다.

보고서 문장 예시:

```text
온라인 트리 모델을 HAT_ADWIN_NODE_MONITORING으로 추적한 결과,
일부 노드에서 detector state가 warning 또는 drift로 전환되고 online accuracy 하락이 함께 관측됐다.
이는 특정 decision path에서 supervised drift 후보가 발생했을 가능성을 나타낸다.
다만 label 지연과 detector 설정의 영향을 받으므로, alarm 시점의 데이터 구성과 전체 성능 지표를 함께 확인해야 한다.
```

---

## 변종: HAT_ALTERNATE_TREE_REPLACEMENT

`HAT_ALTERNATE_TREE_REPLACEMENT`는 HAT가 drift 후보를 감지한 뒤 alternate tree를 생성하고, 새 tree가 기존 branch보다 낫다고 판단될 때 교체하는 적응 이벤트를 감시하는 변종이다. 단순 alarm보다 한 단계 더 나아가 모델이 변화에 어떻게 대응했는지 운영 로그로 설명할 수 있다. 출력은 alternate tree 생성 여부, replacement event, 교체 전후 성능 지표로 해석한다.

사용 상황:
- 온라인 모델이 drift를 감지한 뒤 자동 적응 또는 branch 교체를 수행하는 경우
- champion/challenger 또는 기존 branch/alternate branch 비교를 운영 리포트에 포함해야 할 때
- drift alarm 이후 모델 성능이 회복됐는지 추적하고 싶을 때

해석 방법:
- alternate tree created는 기존 branch에 변화 후보가 있어 대체 후보를 학습하기 시작했다는 신호다.
- tree replaced는 alternate branch가 기존 branch보다 낫다고 판단되어 구조가 교체됐다는 적응 이벤트다.
- pre/post metric이 개선되면 교체가 성능 회복에 기여했을 가능성이 있지만, 별도 검증 지표로 확인해야 한다.
- 보고서에서는 alarm, alternate 생성, replacement, 교체 후 성능 회복을 시간 순서로 설명한다.

주의점:
- replacement event가 곧 원인 해결이나 장기 성능 개선을 의미하지는 않는다.
- 교체 직후 표본 수가 적으면 post metric이 일시적으로 좋아 보일 수 있다.
- label 지연, drift detector 설정, alternate tree 평가 기준을 함께 남겨야 재현 가능한 해석이 된다.

보고서 문장 예시:

```text
HAT_ALTERNATE_TREE_REPLACEMENT 로그를 확인한 결과,
drift alarm 이후 alternate tree가 생성되고 일부 branch가 새 tree로 교체됐다.
교체 후 online metric이 회복되는 흐름이 관측되어 모델 적응 후보 이벤트로 해석할 수 있다.
다만 교체 효과는 장기 성능과 label 지연 영향을 함께 봐야 하므로, post-replacement window를 추가로 검증해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule HAT_DEFAULT_USE
  if ->
    input_signal_matches_method_assumption
    and reference_or_baseline_is_defined

  recommend ->
    대표 변종 중 운영 목적에 맞는 variant

  because ->
    같은 method family 안에서도 입력 신호, window 구성, threshold 목적에 따라 해석이 달라진다.

  caveat ->
    detector 결과만으로 성능 저하, concept drift, 원인을 확정하지 않는다.
```

---

## LLM 추천을 위한 최종 구조

```text
상황 조건
  -> selection rule
  -> algorithm variant 추천
  -> output metric 설명
  -> caveat 설명
  -> report guidance 생성
```

한 문장으로 정리하면:

> HAT 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
