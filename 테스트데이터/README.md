# Drift Test Data Plan

이 폴더는 chart-method 연결별 테스트 데이터를 설계하고 생성하기 위한 작업 공간이다.

## 파일

- `chart_method_links.csv`: PostgreSQL `drift_monitoring` DB의 `variant_chart` 기준 188개 chart-method_variant 연결 목록
- `representative_dataset_cases.csv`: 여러 chart-method 연결이 복사/재사용할 대표 테스트 데이터 케이스 목록
- `drift_generation_scenarios.md`: 대표 케이스별 데이터 흐름과 drift 생성 시나리오
- `chart_method_dataset_mapping.csv`: 188개 연결에 대표 케이스와 복사 정책을 배정하기 위한 작업용 매핑 파일

## 설계 원칙

1. 188개 연결마다 새 데이터를 만들지 않는다.
2. 입력 데이터 형태와 drift 신호가 같은 연결은 대표 케이스 데이터를 복사한다.
3. 대표 케이스는 reference/current/windowed stream을 모두 만들 수 있어야 한다.
4. 각 케이스는 abrupt, gradual, seasonal, cyclic drift 중 적용 가능한 패턴을 명시한다.
5. chart는 drift를 탐지하지 않고, method 결과와 입력 분포 변화를 시각화한다.

