# Drift Chart Title Authoring Guide

## 목적

차트 제목은 내부 구현 요소를 나열하는 이름이 아니라, 사용자가 차트가 보여주는 상황을 바로 이해할 수 있는 보고서용 제목이어야 한다.

## 기본 원칙

1. 제목은 한글 설명형 문장으로 작성한다.
2. 차트 ID는 목록, 메타데이터, 본문 보조 표기에서 유지하되 제목의 중심이 되지 않게 한다.
3. 패널 이름이나 지표명을 단순 나열하지 않는다.
4. 차트가 보여주는 분석 대상, 변화 과정, 판단 포인트를 제목에 담는다.
5. 알고리즘 이름은 해석에 꼭 필요할 때만 제목 앞부분에 둔다.
6. 제목은 15~35자 안팎으로 유지한다.

## 피해야 할 제목

다음처럼 패널명과 지표명을 더한 제목은 피한다.

```text
Online Accuracy + Detector State + Alternate Tree Replacement + Tree Size
KS Statistic + ECDF Overlay + P-value
Error Rate + Warning Timeline + Threshold
```

이런 제목은 차트 구성요소는 말하지만, 사용자가 무엇을 읽어야 하는지 설명하지 못한다.

## 권장 제목 형식

다음 형식을 우선 사용한다.

```text
[대상/모델]의 [변화 또는 감지]와 [대응 또는 판단 과정]
[지표] 변화로 보는 [드리프트/분포 변화/성능 저하] 판단
[방법] 기반 [드리프트 후보] 확인 과정
```

예시는 다음과 같다.

```text
HAT 모델의 드리프트 감지와 대체 트리 교체 과정
예측 오류율 상승과 드리프트 경보 발생 과정
기준 구간과 현재 구간의 분포 차이 확인
특성 중요도 변화로 보는 모델 설명 드리프트
```

## CHART-ADAPT-001 적용

기존 제목:

```text
Online Accuracy + Detector State + Alternate Tree Replacement + Tree Size
```

개선 제목:

```text
HAT 모델의 드리프트 감지와 대체 트리 교체 과정
```

이 제목은 `online accuracy`, `detector state`, `alternate tree`, `replacement`, `tree size`를 각각 나열하지 않고, 차트가 보여주는 전체 상황을 설명한다.
