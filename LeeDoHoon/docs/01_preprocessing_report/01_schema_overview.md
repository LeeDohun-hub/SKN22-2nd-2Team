# 01. 스키마 개요 (Schema Overview)

> **작성자**: 이도훈 (LDH)  
> **작성일**: 2025-12-16  
> **버전**: v1.0

---

## 1. 데이터셋 개요

### 1.1 KKBox Churn Prediction Dataset
- **출처**: Kaggle Competition
- **목적**: 음악 스트리밍 서비스 고객 이탈 예측
- **구성**: 4개 테이블 (train, members, transactions, user_logs)

### 1.2 테이블 요약

| 테이블 | 행 수 | 컬럼 수 | 설명 |
|--------|-------|---------|------|
| `train_v2.csv` | 970,960 | 2 | 타겟 라벨 (is_churn) |
| `members_v3.csv` | 6,769,473 | 6 | 사용자 기본 정보 |
| `transactions_v2.csv` | 1,431,009 | 9 | 결제/구독 내역 |
| `user_logs_v2.csv` | 18,396,362 | 9 | 일별 청취 로그 |

---

## 2. 테이블 스키마

### 2.1 train_v2.csv

> 타겟 변수를 포함한 학습 데이터

| 컬럼 | 타입 | 설명 | 예시 |
|------|------|------|------|
| `msno` | string | 사용자 ID (해시) | `ugx0Cj...` |
| `is_churn` | int | 이탈 여부 (0/1) | 1 |

```
Shape: (970,960 rows × 2 columns)
결측치: 없음
```

### 2.2 members_v3.csv

> 사용자 기본 정보 (가입 시점 정보)

| 컬럼 | 타입 | 설명 | 예시 |
|------|------|------|------|
| `msno` | string | 사용자 ID | `Rb9UwL...` |
| `city` | int | 도시 코드 | 1 |
| `bd` | int | 나이 (birth date) | 25 |
| `gender` | string | 성별 (male/female) | male |
| `registered_via` | int | 가입 경로 | 7 |
| `registration_init_time` | int | 가입일 (YYYYMMDD) | 20110911 |

```
Shape: (6,769,473 rows × 6 columns)
결측치: gender 4,429,505개 (65.4%)
```

### 2.3 transactions_v2.csv

> 결제 및 구독 거래 내역

| 컬럼 | 타입 | 설명 | 예시 |
|------|------|------|------|
| `msno` | string | 사용자 ID | `++6eU4...` |
| `payment_method_id` | int | 결제 수단 | 41 |
| `payment_plan_days` | int | 구독 기간 (일) | 30 |
| `plan_list_price` | int | 정가 | 149 |
| `actual_amount_paid` | int | 실결제 금액 | 149 |
| `is_auto_renew` | int | 자동 갱신 (0/1) | 1 |
| `transaction_date` | int | 거래일 (YYYYMMDD) | 20170131 |
| `membership_expire_date` | int | 만료일 (YYYYMMDD) | 20170504 |
| `is_cancel` | int | 취소 여부 (0/1) | 0 |

```
Shape: (1,431,009 rows × 9 columns)
결측치: 없음
```

### 2.4 user_logs_v2.csv

> 일별 음악 청취 로그

| 컬럼 | 타입 | 설명 | 예시 |
|------|------|------|------|
| `msno` | string | 사용자 ID | `u9E91Q...` |
| `date` | int | 날짜 (YYYYMMDD) | 20170331 |
| `num_25` | int | 25% 미만 청취 곡 수 | 5 |
| `num_50` | int | 25-50% 청취 곡 수 | 3 |
| `num_75` | int | 50-75% 청취 곡 수 | 2 |
| `num_985` | int | 75-98.5% 청취 곡 수 | 4 |
| `num_100` | int | 완주 곡 수 (98.5%+) | 10 |
| `num_unq` | int | 고유 곡 수 | 18 |
| `total_secs` | float | 총 청취 시간 (초) | 6309.273 |

```
Shape: (18,396,362 rows × 9 columns)
결측치: 없음
```

---

## 3. 날짜 범위 (Date Range)

| 테이블 | 컬럼 | Min | Max | 기간 |
|--------|------|-----|-----|------|
| `members_v3` | registration_init_time | 2004-03-26 | 2017-04-29 | 약 13년 |
| `transactions_v2` | transaction_date | 2015-01-01 | 2017-03-31 | **약 2년 3개월** |
| `transactions_v2` | membership_expire_date | 2016-04-19 | 2036-10-15 | - |
| `user_logs_v2` | date | 2017-03-01 | 2017-03-31 | **30일** |

### 3.1 시간 프레임 시각화

```
                    transactions_v2
    ├──────────────────────────────────────────┤
    2015-01-01                           2017-03-31
    
                                    user_logs_v2
                                    ├──────────┤
                                 2017-03-01  2017-03-31
                                               ↓
                                           T (예측 시점)
                                           2017-04-01
```

---

## 4. 테이블 관계 (Entity Relationship)

### 4.1 ER 다이어그램

```
┌─────────────────┐     ┌─────────────────┐
│   train_v2      │     │   members_v3    │
├─────────────────┤     ├─────────────────┤
│ msno (PK)       │────▶│ msno (PK)       │
│ is_churn        │     │ city            │
└─────────────────┘     │ bd              │
        │               │ gender          │
        │               │ registered_via  │
        │               │ registration_   │
        │               │   init_time     │
        │               └─────────────────┘
        │
        │               ┌─────────────────┐
        │               │ transactions_v2 │
        │               ├─────────────────┤
        └──────────────▶│ msno (FK)       │
                        │ payment_method  │
                        │ payment_plan_   │
                        │   days          │
                        │ plan_list_price │
                        │ actual_amount_  │
                        │   paid          │
                        │ is_auto_renew   │
                        │ transaction_    │
                        │   date          │
                        │ membership_     │
                        │   expire_date   │
                        │ is_cancel       │
                        └─────────────────┘
                        
        │               ┌─────────────────┐
        │               │  user_logs_v2   │
        │               ├─────────────────┤
        └──────────────▶│ msno (FK)       │
                        │ date            │
                        │ num_25 ~ num_100│
                        │ num_unq         │
                        │ total_secs      │
                        └─────────────────┘
```

### 4.2 관계 유형

| 관계 | 유형 | 설명 |
|------|------|------|
| train ↔ members | 1:1 | 사용자별 1개 정보 |
| train ↔ transactions | 1:N | 사용자별 N개 거래 |
| train ↔ user_logs | 1:N | 사용자별 N개 일별 로그 |

---

## 5. 테이블 간 사용자 커버리지

### 5.1 사용자 수 비교

| 테이블 | 고유 사용자 수 |
|--------|----------------|
| `train_v2` | 970,960 |
| `members_v3` | 6,769,473 |
| `transactions_v2` | 1,197,050 |
| `user_logs_v2` | 1,103,894 |

### 5.2 train 기준 커버리지

| 교집합 | 사용자 수 | 커버리지 |
|--------|-----------|----------|
| train ∩ members | 860,967 | **88.7%** |
| train ∩ transactions | 933,578 | **96.1%** |
| train ∩ user_logs | 754,551 | **77.7%** |

### 5.3 train에서 빠진 사용자

| 차집합 | 사용자 수 | 의미 |
|--------|-----------|------|
| train - members | 109,993 | 회원 정보 없음 |
| train - transactions | 37,382 | 거래 내역 없음 |
| train - user_logs | 216,409 | 3월 로그 없음 |

> **⚠️ 주의**: train의 22.3% 사용자는 3월 로그가 없음 → 활동 없는 사용자

---

## 6. 타겟 변수 분포 (is_churn)

### 6.1 분포

| is_churn | 사용자 수 | 비율 |
|----------|-----------|------|
| 0 (유지) | 883,630 | 91.01% |
| 1 (이탈) | 87,330 | **8.99%** |

### 6.2 클래스 불균형

```
┌──────────────────────────────────────────────────┐
│ ████████████████████████████████████████░░░░░░░░ │ 유지 (91%)
│ ░░░░░                                            │ 이탈 (9%)
└──────────────────────────────────────────────────┘
```

- **불균형 비율**: 약 10:1
- **처리 방법**: class_weight, scale_pos_weight 적용 필요

---

## 7. 데이터 품질 이슈

### 7.1 결측치

| 테이블 | 컬럼 | 결측 수 | 결측률 |
|--------|------|---------|--------|
| members_v3 | gender | 4,429,505 | 65.4% |

### 7.2 이상치

| 테이블 | 컬럼 | 이상치 | 설명 |
|--------|------|--------|------|
| members_v3 | bd | 다수 | 음수, 0, 100+ 값 존재 |
| transactions_v2 | membership_expire_date | 일부 | 2036년까지 (정상) |

### 7.3 bd (나이) 통계

```
count    6,769,473
mean           9.8    ← 대부분 0으로 기록됨
std           17.9
min       -7,168     ← 이상치
25%            0     ← 50% 이상이 0
50%            0
75%           21
max        2,016     ← 이상치
```

---

## 8. 전처리 시 고려사항

### 8.1 결측치 처리
- `gender`: NaN → "unknown" 범주로 처리

### 8.2 이상치 처리
- `bd`: 0 < bd < 100 범위 외 → 중앙값 대체

### 8.3 날짜 필터링
- `user_logs`: 2017-03-01 ~ 2017-03-31 (이미 필터링됨)
- `transactions`: < 2017-04-01 필터링 필요

### 8.4 조인 전략
- 기준: `train_v2` (모든 사용자 유지)
- 방식: LEFT JOIN
- 결측: 0 또는 "unknown"으로 처리

---

> **📌 이 문서는 전처리 파이프라인의 입력 데이터 구조를 정의합니다.**

