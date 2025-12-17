# 04. 피처 사전 (Feature Dictionary)

> **작성자**: 이도훈 (LDH)  
> **작성일**: 2025-12-16  
> **버전**: v1.0

---

## 1. 피처 개요

| 카테고리 | 피처 수 | 소스 테이블 |
|----------|---------|-------------|
| User Log Features | 16개 | `user_logs_v2.csv` |
| Transaction Features | 13개 | `transactions_v2.csv` |
| Member Features | 8개 | `members_v3.csv` |
| **Total** | **37개** | - |

---

## 2. User Log Features (행동 피처)

> **소스**: `user_logs_v2.csv`  
> **집계 기간**: 2017-03-01 ~ 2017-03-31 (30일)

### 2.1 집계 피처 (Raw Aggregation)

| Feature | Type | Description | 계산 방법 |
|---------|------|-------------|-----------|
| `total_songs` | numeric | 30일간 총 재생 곡 수 | `sum(num_25 + num_50 + num_75 + num_985 + num_100)` |
| `total_secs` | numeric | 30일간 총 청취 시간 (초) | `sum(total_secs)` |
| `num_25_sum` | numeric | 25% 미만 청취 곡 수 (스킵) | `sum(num_25)` |
| `num_50_sum` | numeric | 25-50% 청취 곡 수 | `sum(num_50)` |
| `num_75_sum` | numeric | 50-75% 청취 곡 수 | `sum(num_75)` |
| `num_985_sum` | numeric | 75-98.5% 청취 곡 수 | `sum(num_985)` |
| `num_100_sum` | numeric | 완주 곡 수 (98.5%+) | `sum(num_100)` |
| `num_unq_sum` | numeric | 고유 곡 수 | `sum(num_unq)` |
| `active_days` | numeric | 활동 일수 (30일 중) | `count(distinct date)` |

### 2.2 파생 피처 (Derived)

| Feature | Type | Description | 계산 방법 | 의미 |
|---------|------|-------------|-----------|------|
| `skip_ratio` | numeric | 스킵율 | `num_25_sum / total_songs` | 높을수록 불만족 신호 |
| `complete_ratio` | numeric | 완주율 | `num_100_sum / total_songs` | 높을수록 몰입도 높음 |
| `partial_ratio` | numeric | 부분 청취율 | `(num_50_sum + num_75_sum) / total_songs` | 중간 이탈 패턴 |
| `avg_songs_per_day` | numeric | 일평균 재생 곡 수 | `total_songs / active_days` | 일일 사용량 |
| `avg_secs_per_day` | numeric | 일평균 청취 시간 (초) | `total_secs / active_days` | 일일 청취량 |
| `listening_variety` | numeric | 청취 다양성 | `num_unq_sum / total_songs` | 1에 가까울수록 다양하게 청취 |
| `avg_song_length` | numeric | 평균 곡 길이 (초) | `total_secs / total_songs` | 선호 곡 길이 |

### 2.3 BM 관점 해석

| Feature | 이탈 위험 신호 |
|---------|----------------|
| `skip_ratio` ↑ | 콘텐츠 불만족 → 이탈 위험 |
| `complete_ratio` ↓ | 몰입도 저하 → 이탈 위험 |
| `active_days` ↓ | 서비스 이용 감소 → 이탈 위험 |
| `listening_variety` ↓ | 콘텐츠 탐색 감소 → 이탈 위험 |

---

## 3. Transaction Features (결제 피처)

> **소스**: `transactions_v2.csv`  
> **집계 기간**: ~ 2017-03-31 (약 2년 전체 이력)

### 3.1 금액 관련 피처

| Feature | Type | Description | 계산 방법 |
|---------|------|-------------|-----------|
| `total_payment` | numeric | 총 결제 금액 (2년 누적) | `sum(actual_amount_paid)` |
| `avg_payment` | numeric | 평균 결제 금액 | `mean(actual_amount_paid)` |
| `avg_list_price` | numeric | 평균 정가 | `mean(plan_list_price)` |
| `avg_discount_rate` | numeric | 평균 할인율 (0~1) | `mean(1 - actual/list_price)` |

### 3.2 거래 횟수 피처

| Feature | Type | Description | 계산 방법 |
|---------|------|-------------|-----------|
| `transaction_count` | numeric | 거래 횟수 (2년 누적) | `count(*)` |
| `cancel_count` | numeric | 취소 횟수 | `sum(is_cancel)` |

### 3.3 최근 거래 피처

| Feature | Type | Description | 계산 방법 |
|---------|------|-------------|-----------|
| `is_auto_renew_last` | binary | 최근 거래 자동갱신 여부 | 최신 거래의 `is_auto_renew` |
| `plan_days_last` | numeric | 최근 구독 기간 (일) | 최신 거래의 `payment_plan_days` |
| `payment_method_last` | categorical | 최근 결제 수단 | 최신 거래의 `payment_method_id` |
| `days_to_expire` | numeric | 만료까지 남은 일수 | `membership_expire_date - T` |

### 3.4 플래그 피처

| Feature | Type | Description | 계산 방법 |
|---------|------|-------------|-----------|
| `has_cancelled` | binary | 취소 이력 여부 | `cancel_count > 0` |
| `auto_renew_rate` | numeric | 자동 갱신 비율 | `mean(is_auto_renew)` |

### 3.5 BM 관점 해석

| Feature | 이탈 위험 신호 |
|---------|----------------|
| `is_auto_renew_last` = 0 | **매우 높은 이탈 위험** |
| `days_to_expire` ↓ (음수) | 이미 만료됨 → 이탈 |
| `has_cancelled` = 1 | 취소 이력 → 이탈 위험 |
| `cancel_count` ↑ | 반복 취소 → 높은 이탈 위험 |

---

## 4. Member Features (정적 피처)

> **소스**: `members_v3.csv`  
> **특징**: 시간에 독립적인 사용자 기본 정보

### 4.1 원본 피처

| Feature | Type | Description | 처리 |
|---------|------|-------------|------|
| `city` | categorical | 도시 코드 | 결측 → 0 |
| `age` | numeric | 나이 | 이상치 → 중앙값 |
| `registered_via` | categorical | 가입 경로 | 결측 → 0 |
| `tenure_days` | numeric | 가입 후 경과 일수 | `T - registration_init_time` |

### 4.2 인코딩된 피처

| Feature | Type | Description | 원본 |
|---------|------|-------------|------|
| `gender_female` | binary | 성별: 여성 | `gender` One-hot |
| `gender_male` | binary | 성별: 남성 | `gender` One-hot |
| `gender_unknown` | binary | 성별: 미입력 | `gender` One-hot |

### 4.3 BM 관점 해석

| Feature | 인사이트 |
|---------|----------|
| `tenure_days` ↓ | 신규 가입자 → 이탈 위험 (초기 이탈) |
| `tenure_days` ↑ | 장기 사용자 → 상대적 안정 |
| `age` | 연령대별 이탈 패턴 분석 가능 |

---

## 5. 타겟 변수

| Feature | Type | Description | 값 |
|---------|------|-------------|-----|
| `is_churn` | binary | 이탈 여부 | 0: 유지, 1: 이탈 |

---

## 6. ID 변수

| Feature | Type | Description |
|---------|------|-------------|
| `msno` | string | 사용자 고유 ID (해시) |

---

## 7. 피처 중요도 예상 (가설)

### 7.1 High Importance (예상)

| 순위 | Feature | 사유 |
|------|---------|------|
| 1 | `is_auto_renew_last` | 자동갱신 해제 = 이탈 의사 표현 |
| 2 | `days_to_expire` | 만료 임박/만료됨 = 직접적 이탈 신호 |
| 3 | `has_cancelled` | 취소 이력 = 과거 이탈 시도 |
| 4 | `active_days` | 활동 감소 = 관심 저하 |
| 5 | `skip_ratio` | 높은 스킵율 = 콘텐츠 불만 |

### 7.2 Medium Importance (예상)

| Feature | 사유 |
|---------|------|
| `complete_ratio` | 몰입도 지표 |
| `tenure_days` | 사용자 성숙도 |
| `transaction_count` | 결제 습관 |
| `avg_songs_per_day` | 사용량 지표 |

### 7.3 Low Importance (예상)

| Feature | 사유 |
|---------|------|
| `city` | 지역 영향 불확실 |
| `gender_*` | 성별 영향 불확실 |
| `avg_song_length` | 간접적 지표 |

---

## 8. 피처 값 범위

| Feature | Min | Max | 비고 |
|---------|-----|-----|------|
| `skip_ratio` | 0 | 1 | 비율 |
| `complete_ratio` | 0 | 1 | 비율 |
| `days_to_expire` | 음수 가능 | 양수 | 음수 = 이미 만료 |
| `age` | 1 | 99 | 이상치 처리 후 |
| `active_days` | 0 | 31 | 30일 윈도우 |

---

## 9. 결측치 발생 패턴

| Feature | 결측 사유 | 처리 |
|---------|-----------|------|
| User Log 피처 전체 | 30일간 활동 없음 | → 0 |
| Transaction 피처 전체 | 거래 이력 없음 | → 0 |
| `gender` | 미입력 | → "unknown" |

---

> **📌 이 피처 사전은 모델 학습 및 해석 시 참조용으로 사용됩니다.**

