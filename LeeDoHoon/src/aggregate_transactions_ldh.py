"""
KKBox Transactions 집계 (상태 + 누적 중심)
작성자: 이도훈 (LDH)
작성일: 2025-12-16

kkbox_aggregation_plan.md 기준으로 집계:
- 상태 기반 피처 (마지막 거래 기준)
- 누적 히스토리 피처 (전체 기간)
- 제한적 Recency 집계 (30일, 90일)
- 데이터 누수 방지: T = 2017-03-31 이전만 사용
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional
import warnings

warnings.filterwarnings('ignore')

# ============================================
# 설정
# ============================================
T = pd.Timestamp('2017-03-31')  # 기준 시점

DATA_DIR = Path(__file__).parent.parent / 'data'


# ============================================
# 집계 함수
# ============================================
def load_transactions(data_dir: Path = DATA_DIR) -> pd.DataFrame:
    """transactions_v2.csv 로드 및 전처리"""
    print("📂 transactions_v2.csv 로드 중...")
    
    df = pd.read_csv(data_dir / 'transactions_v2.csv')
    print(f"  ✓ 원본: {df.shape}")
    
    # 날짜 변환
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], format='%Y%m%d')
    df['membership_expire_date'] = pd.to_datetime(df['membership_expire_date'], format='%Y%m%d')
    
    # T 이전 데이터만 사용 (데이터 누수 방지)
    df = df[df['transaction_date'] <= T].copy()
    
    print(f"  ✓ T 이전 필터링 후: {df.shape}")
    print(f"  ✓ 날짜 범위: {df['transaction_date'].min().strftime('%Y-%m-%d')} ~ {df['transaction_date'].max().strftime('%Y-%m-%d')}")
    print(f"  ✓ 고유 사용자: {df['msno'].nunique():,}")
    
    return df


def create_state_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    상태 기반 피처 (마지막 거래 기준)
    - 가장 중요한 피처들
    """
    print("\n📊 상태 기반 피처 생성 중...")
    
    # 사용자별 최신 거래 추출
    df_sorted = df.sort_values(['msno', 'transaction_date'], ascending=[True, False])
    latest = df_sorted.groupby('msno').first().reset_index()
    
    # 상태 피처 생성
    features = pd.DataFrame()
    features['msno'] = latest['msno']
    
    # 마지막 결제 후 경과일
    features['days_since_last_payment'] = (T - latest['transaction_date']).dt.days
    
    # 마지막 거래 정보
    features['is_auto_renew_last'] = latest['is_auto_renew']
    features['last_plan_days'] = latest['payment_plan_days']
    features['last_payment_method'] = latest['payment_method_id']
    features['last_amount_paid'] = latest['actual_amount_paid']
    features['last_list_price'] = latest['plan_list_price']
    
    # 마지막 거래 할인율
    features['last_discount_rate'] = 1 - (features['last_amount_paid'] / (features['last_list_price'] + 1e-9))
    features['last_discount_rate'] = features['last_discount_rate'].clip(0, 1)
    
    # 만료까지 남은 일수 (T 기준)
    features['days_to_expire'] = (latest['membership_expire_date'] - T).dt.days
    
    # 이미 만료됨 플래그
    features['is_expired'] = (features['days_to_expire'] < 0).astype(int)
    
    # 마지막 거래가 취소인지
    features['is_last_cancel'] = latest['is_cancel']
    
    print(f"  ✓ 상태 피처 {len(features.columns)-1}개 생성")
    
    return features


def create_history_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    누적 히스토리 피처 (전체 기간)
    - 2015-01-01 ~ 2017-03-31
    """
    print("\n📊 누적 히스토리 피처 생성 중...")
    
    # 할인율 계산
    df = df.copy()
    df['discount_rate'] = 1 - (df['actual_amount_paid'] / (df['plan_list_price'] + 1e-9))
    df['discount_rate'] = df['discount_rate'].clip(0, 1)
    
    # 집계
    agg_dict = {
        'transaction_date': 'count',           # 총 거래 횟수
        'actual_amount_paid': ['sum', 'mean'], # 총/평균 결제액
        'is_cancel': 'sum',                    # 취소 횟수
        'is_auto_renew': 'mean',               # 자동갱신 비율
        'payment_plan_days': ['mean', 'nunique'],  # 평균/고유 플랜
        'payment_method_id': 'nunique',        # 고유 결제수단
        'discount_rate': 'mean',               # 평균 할인율
    }
    
    history = df.groupby('msno').agg(agg_dict)
    
    # 컬럼명 정리
    history.columns = [
        'total_payment_count',
        'total_amount_paid',
        'avg_amount_per_payment',
        'total_cancel_count',
        'auto_renew_rate_history',
        'avg_plan_days',
        'unique_plan_count',
        'unique_payment_method_count',
        'avg_discount_rate_history',
    ]
    
    history = history.reset_index()
    
    # 추가 파생 피처
    # 취소 비율
    history['cancel_rate'] = history['total_cancel_count'] / (history['total_payment_count'] + 1e-9)
    
    # 취소 이력 유무
    history['has_cancelled'] = (history['total_cancel_count'] > 0).astype(int)
    
    # 구독 개월 수 추정 (총 결제 횟수 기반)
    history['subscription_months_est'] = history['total_payment_count']
    
    print(f"  ✓ 히스토리 피처 {len(history.columns)-1}개 생성")
    
    return history


def create_recency_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    제한적 Recency 집계 (30일, 90일)
    - 7일, 14일은 대부분 0이므로 비권장
    """
    print("\n📊 Recency 피처 생성 중...")
    
    features = pd.DataFrame({'msno': df['msno'].unique()})
    
    # 최근 30일 (2017-03-01 ~ 2017-03-31)
    last_30d = df[df['transaction_date'] >= T - pd.Timedelta(days=30)]
    count_30d = last_30d.groupby('msno').size().reset_index(name='payment_count_last_30d')
    
    # 최근 90일 (2017-01-01 ~ 2017-03-31)
    last_90d = df[df['transaction_date'] >= T - pd.Timedelta(days=90)]
    count_90d = last_90d.groupby('msno').size().reset_index(name='payment_count_last_90d')
    
    # 최근 180일
    last_180d = df[df['transaction_date'] >= T - pd.Timedelta(days=180)]
    count_180d = last_180d.groupby('msno').size().reset_index(name='payment_count_last_180d')
    
    # 병합
    features = features.merge(count_30d, on='msno', how='left')
    features = features.merge(count_90d, on='msno', how='left')
    features = features.merge(count_180d, on='msno', how='left')
    
    # 결측 = 0
    features = features.fillna(0)
    
    # 최근 결제 집중도
    features['recency_30d_90d_ratio'] = features['payment_count_last_30d'] / (features['payment_count_last_90d'] + 1e-9)
    
    print(f"  ✓ Recency 피처 {len(features.columns)-1}개 생성")
    
    return features


def create_cancel_features(df: pd.DataFrame) -> pd.DataFrame:
    """취소 관련 상세 피처"""
    print("\n📊 취소 관련 피처 생성 중...")
    
    # 취소 거래만 필터링
    cancel_df = df[df['is_cancel'] == 1]
    
    if len(cancel_df) == 0:
        print("  ⚠️ 취소 데이터 없음")
        return pd.DataFrame({'msno': df['msno'].unique()})
    
    # 마지막 취소일
    last_cancel = cancel_df.groupby('msno')['transaction_date'].max().reset_index()
    last_cancel.columns = ['msno', 'last_cancel_date']
    last_cancel['days_since_last_cancel'] = (T - last_cancel['last_cancel_date']).dt.days
    
    features = last_cancel[['msno', 'days_since_last_cancel']]
    
    print(f"  ✓ 취소 피처 {len(features.columns)-1}개 생성")
    
    return features


def merge_all_features(state_features: pd.DataFrame,
                       history_features: pd.DataFrame,
                       recency_features: pd.DataFrame,
                       cancel_features: pd.DataFrame) -> pd.DataFrame:
    """모든 피처 병합"""
    print("\n🔗 피처 병합 중...")
    
    # state 기준으로 병합
    result = state_features.copy()
    
    result = result.merge(history_features, on='msno', how='left')
    result = result.merge(recency_features, on='msno', how='left')
    result = result.merge(cancel_features, on='msno', how='left')
    
    # 결측치 처리
    result = result.fillna(0)
    
    # Inf 처리
    result = result.replace([np.inf, -np.inf], 0)
    
    print(f"  ✓ 병합 완료: {result.shape}")
    
    return result


def sanity_check(df: pd.DataFrame) -> None:
    """집계 결과 검증"""
    
    print("\n🔍 Sanity Check...")
    print(f"  Shape: {df.shape}")
    print(f"  고유 msno: {df['msno'].nunique():,}")
    print(f"  중복 msno: {df['msno'].duplicated().sum()}")
    print(f"  결측치: {df.isnull().sum().sum()}")
    
    # 주요 피처 통계
    print("\n  주요 피처 통계:")
    key_features = ['days_since_last_payment', 'is_auto_renew_last', 'days_to_expire', 
                    'total_payment_count', 'has_cancelled']
    
    for feat in key_features:
        if feat in df.columns:
            print(f"    {feat}: mean={df[feat].mean():.2f}, std={df[feat].std():.2f}")


def run_aggregation_pipeline(data_dir: Path = DATA_DIR,
                             save: bool = True) -> pd.DataFrame:
    """전체 집계 파이프라인 실행"""
    
    print("=" * 60)
    print("🚀 Transactions 집계 파이프라인 (상태 + 누적)")
    print("=" * 60)
    print(f"기준 시점 (T): {T.strftime('%Y-%m-%d')}")
    
    # 1. 데이터 로드
    transactions = load_transactions(data_dir)
    
    # 2. 상태 기반 피처
    state_features = create_state_features(transactions)
    
    # 3. 누적 히스토리 피처
    history_features = create_history_features(transactions)
    
    # 4. Recency 피처
    recency_features = create_recency_features(transactions)
    
    # 5. 취소 관련 피처
    cancel_features = create_cancel_features(transactions)
    
    # 6. 병합
    agg_df = merge_all_features(state_features, history_features, 
                                 recency_features, cancel_features)
    
    # 7. Sanity Check
    sanity_check(agg_df)
    
    # 8. 저장 (Parquet + PyArrow)
    if save:
        output_path = data_dir / 'transactions_aggregated_ldh.parquet'
        agg_df.to_parquet(output_path, engine='pyarrow', index=False)
        print(f"\n💾 저장 완료 (Parquet): {output_path}")
    
    print("\n" + "=" * 60)
    print("✅ 집계 완료!")
    print("=" * 60)
    
    # 피처 목록 출력
    print(f"\n📋 생성된 피처 ({len(agg_df.columns)}개):")
    for i, col in enumerate(agg_df.columns):
        print(f"  {i+1:2d}. {col}")
    
    return agg_df


# ============================================
# 실행
# ============================================
if __name__ == "__main__":
    agg_df = run_aggregation_pipeline()

