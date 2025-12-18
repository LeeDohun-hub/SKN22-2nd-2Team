
# 📌 KKBox BM-Oriented Churn Prediction Project – Issue Plan

## 🧭 Project Goal
행동 로그 기반으로 **BM 이탈 신호를 정의하고**,  
이를 통해 **고객 churn을 예측 및 설명 가능한 Risk Score**로 확장한다.

---

## 🟣 EPIC 1. Problem Definition & BM Framing

### 🎯 Objective
- 고객 이탈이 아닌 **BM 관점 이탈 신호**를 예측 대상으로 정의

### ✅ Tasks
- [ ] 음악 스트리밍 서비스(KKBox)의 BM 구조 정의
- [ ] Customer Churn vs BM Drop 개념 구분
- [ ] 예측 문제를 비즈니스 질문으로 명확히 정의
- [ ] 예측 시점(T), 관측 윈도우, 예측 윈도우 설계

### 📄 Deliverables
- Problem statement 문서
- 예측 프레임 다이어그램
- README 초안

---

## 🟣 EPIC 2. Data Understanding & Schema Analysis (EDA – Stage 0)

### 🎯 Objective
- KKBox 데이터셋 구조를 비즈니스/BM 관점으로 해석

### ✅ Tasks
- [ ] train_v2 / user_logs_v2 / transactions_v2 / members_v3 구조 파악
- [ ] 테이블 간 관계(ER 구조) 정리
- [ ] 각 컬럼의 비즈니스 의미 정의
- [ ] 데이터 기간, 결측치, 이상치 1차 점검

### 📄 Deliverables
- Schema 설명 문서
- 컬럼 사전(Data Dictionary)

---

## 🟣 EPIC 3. Churn Label Alignment & Prediction Frame

### 🎯 Objective
- 시계열 누수 없는 예측 프레임 확정

### ✅ Tasks
- [ ] churn(is_churn) 라벨 정의 및 생성 로직 이해
- [ ] 관측 윈도우 / 예측 윈도우 수치 확정
- [ ] Feature 생성 시점과 라벨 시점 정렬
- [ ] 데이터 누수 가능성 점검

### 📄 Deliverables
- Label 정의 문서
- Prediction timeline 다이어그램

---

## 🟣 EPIC 4. BM Drop Signal Design (Core)

### 🎯 Objective
- 고객 이탈 이전에 나타나는 **BM 붕괴 신호 정의**

### ✅ Tasks
- [ ] user_logs 기반 사용량/몰입도/완주율 신호 정의
- [ ] transactions 기반 수익/구독 붕괴 신호 정의
- [ ] BM Drop 파생 타겟 정의(옵션)
- [ ] BM 신호와 churn 간 관계 가설 수립

### 📄 Deliverables
- BM Drop 정의 문서
- Feature 설계 초안

---

## 🟣 EPIC 5. Feature Engineering Pipeline

### 🎯 Objective
- Raw 로그 → User-level Feature Table 생성

### ✅ Tasks
- [ ] user_logs_v2 집계 Feature 생성
- [ ] transactions_v2 집계 Feature 생성
- [ ] members_v3 보조 Feature 병합
- [ ] 최종 Feature Table 구성

### 📄 Deliverables
- Feature Table (CSV / Parquet)
- Feature Dictionary

---

## 🟣 EPIC 6. Baseline Churn Prediction Model

### 🎯 Objective
- 기본 churn 예측 성능 확보

### ✅ Tasks
- [ ] Logistic Regression baseline 학습
- [ ] 평가 지표 정의 (ROC-AUC, Recall, PR-AUC)
- [ ] 성능 결과 정리

### 📄 Deliverables
- Baseline 성능 리포트
- Confusion Matrix

---

## 🟣 EPIC 7. BM Risk Score Construction

### 🎯 Objective
- 운영 가능한 **BM Risk Score** 정의

### ✅ Tasks
- [ ] 모델 출력 확률 기반 Risk Score 정의
- [ ] Risk Score 분포 분석
- [ ] Churn과 Risk Score 관계 검증

### 📄 Deliverables
- User-level Risk Score
- Risk Distribution 분석

---

## 🟣 EPIC 8. Model Explainability & Insight

### 🎯 Objective
- 행동 패턴의 기여도 해석

### ✅ Tasks
- [ ] Feature 중요도 분석(Logistic / SHAP)
- [ ] 핵심 행동 패턴 도출
- [ ] BM 관점 인사이트 정리

### 📄 Deliverables
- Feature Importance 리포트
- Insight 요약

---

## 🟣 EPIC 9. Business Action Mapping

### 🎯 Objective
- 예측 결과를 비즈니스 액션으로 연결

### ✅ Tasks
- [ ] Risk 구간 정의 (High / Mid / Low)
- [ ] 구간별 대응 전략 설계
- [ ] 간단한 시뮬레이션 수행

### 📄 Deliverables
- Action Mapping 테이블
- 시뮬레이션 결과

---

## 🟣 EPIC 10. Documentation & Finalization

### 🎯 Objective
- 포트폴리오 수준 프로젝트 정리

### ✅ Tasks
- [ ] README 최종 정리
- [ ] 전체 아키텍처 다이어그램 작성
- [ ] 결과 요약 및 한계/확장 방향 정리

### 📄 Deliverables
- Final README
- Project Summary

---

## 🧠 Project Positioning (One-liner)
> 본 프로젝트는 고객 churn을 직접 예측하는 것이 아니라,  
> **BM 붕괴 신호를 조기에 감지하기 위한 예측 시스템을 설계**하는 것을 목표로 한다.
