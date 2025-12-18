# 01. ML 모델 학습 결과 (ML Training Results)

> **작성자**: 이도훈 (LDH)  
> **작성일**: 2025-12-16  
> **버전**: v1.0

---

## 1. 학습 개요

### 1.1 모델 목록
| 모델 | 유형 | 목적 |
|------|------|------|
| Logistic Regression | Linear | Baseline 모델 |
| LightGBM | Tree-based | 성능 향상 모델 |

### 1.2 데이터 분할
| 셋 | 비율 | 용도 |
|----|------|------|
| Train | 70% | 모델 학습 |
| Valid | 10% | 하이퍼파라미터 튜닝 / Early Stopping |
| Test | 20% | 최종 성능 평가 |

### 1.3 클래스 불균형 처리
- **Logistic Regression**: `class_weight='balanced'`
- **LightGBM**: `scale_pos_weight` 적용

---

## 2. 평가 지표 비교

### 2.1 Validation Set 성능

| 지표 | Logistic Regression | LightGBM | 우수 모델 |
|------|---------------------|----------|-----------|
| **ROC-AUC** | 0.9475 | 0.9884 | LightGBM ✅ |
| **PR-AUC** | 0.7559 | 0.9279 | LightGBM ✅ |
| **Recall** | 0.8819 | 0.9407 | LightGBM ✅ |
| **Precision** | 0.5148 | 0.6257 | LightGBM ✅ |
| **F1-Score** | 0.6501 | 0.7515 | LightGBM ✅ |

### 2.2 Test Set 성능 (최종)

| 지표 | Logistic Regression | LightGBM | 우수 모델 |
|------|---------------------|----------|-----------|
| **ROC-AUC** | 0.9474 | 0.9887 | LightGBM ✅ |
| **PR-AUC** | 0.7498 | 0.9277 | LightGBM ✅ |
| **Recall** | 0.8843 | 0.9413 | LightGBM ✅ |
| **Precision** | 0.5134 | 0.6199 | LightGBM ✅ |
| **F1-Score** | 0.6496 | 0.7475 | LightGBM ✅ |

---

## 3. Confusion Matrix (Test Set)

### 3.1 Logistic Regression

```
              Predicted
              0        1
Actual  0    162,086    14,640
        1    2,021    15,445
```

### 3.2 LightGBM

```
              Predicted
              0        1
Actual  0    166,644    10,082
        1    1,026    16,440
```

---

## 4. Feature Importance (LightGBM)

| 순위 | Feature | Importance |
|------|---------|------------|
| 1 | `days_to_expire` | 2684694.84 |
| 2 | `auto_renew_rate` | 2000318.20 |
| 3 | `total_payment` | 1707088.26 |
| 4 | `cancel_count` | 869436.24 |
| 5 | `avg_discount_rate` | 637001.29 |
| 6 | `transaction_count` | 621996.81 |
| 7 | `payment_method_last` | 574306.78 |
| 8 | `avg_list_price` | 184590.20 |
| 9 | `tenure_days` | 177507.58 |
| 10 | `avg_payment` | 105958.70 |

---

## 5. 모델별 하이퍼파라미터

### 5.1 Logistic Regression

| 파라미터 | 값 |
|----------|-----|
| C (규제 강도) | 1.0 |
| class_weight | balanced |
| max_iter | 1000 |
| solver | lbfgs |

### 5.2 LightGBM

| 파라미터 | 값 |
|----------|-----|
| num_leaves | 31 |
| max_depth | 6 |
| learning_rate | 0.05 |
| feature_fraction | 0.8 |
| bagging_fraction | 0.8 |
| min_child_samples | 100 |
| reg_alpha | 0.1 |
| reg_lambda | 0.1 |
| best_iteration | 385 |

---

## 6. 결론

### 6.1 최종 모델 선정
- **추천 모델**: LightGBM
- **선정 사유**: ROC-AUC 기준 우수한 성능

### 6.2 성능 요약
- **ROC-AUC**: 0.9887
- **PR-AUC**: 0.9277
- **Recall**: 0.9413

### 6.3 주요 이탈 예측 피처
1. **`days_to_expire`**: 가장 중요한 이탈 신호
2. **`auto_renew_rate`**: 두 번째 중요 피처
3. **`total_payment`**: 세 번째 중요 피처

---

## 7. 저장된 파일

| 파일 | 경로 | 설명 |
|------|------|------|
| Logistic Regression | `models/logistic_regression.pkl` | Baseline 모델 |
| LightGBM | `models/lightgbm.txt` | Tree 모델 |
| Scaler | `models/scaler.pkl` | 표준화 스케일러 |
| Feature 목록 | `models/feature_cols.json` | 학습 피처 목록 |
| 결과 JSON | `models/training_results.json` | 전체 결과 |

---

> **📌 다음 단계**: 딥러닝 모델 학습 또는 Risk Score 생성
