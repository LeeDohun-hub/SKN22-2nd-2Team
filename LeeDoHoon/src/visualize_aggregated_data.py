"""
KKBox 집계 데이터 시각화
작성자: 이도훈 (LDH)
작성일: 2025-12-16

집계된 Parquet 파일을 시각화합니다.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# 한글 폰트 설정 (Windows)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 설정
DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'outputs'


def load_aggregated_data():
    """집계된 데이터 로드"""
    print("📂 집계 데이터 로드 중...")
    
    data = {}
    
    # User Logs
    user_logs_path = DATA_DIR / 'user_logs_aggregated_ldh.parquet'
    if user_logs_path.exists():
        data['user_logs'] = pd.read_parquet(user_logs_path)
        print(f"  ✓ user_logs: {data['user_logs'].shape}")
    else:
        print(f"  ⚠️ user_logs 파일 없음")
    
    # Transactions
    txn_path = DATA_DIR / 'transactions_aggregated_ldh.parquet'
    if txn_path.exists():
        data['transactions'] = pd.read_parquet(txn_path)
        print(f"  ✓ transactions: {data['transactions'].shape}")
    else:
        print(f"  ⚠️ transactions 파일 없음")
    
    return data


def print_data_summary(data: dict):
    """데이터 요약 출력"""
    print("\n" + "=" * 60)
    print("📊 집계 데이터 요약")
    print("=" * 60)
    
    for name, df in data.items():
        print(f"\n【 {name} 】")
        print(f"  Shape: {df.shape}")
        print(f"  Columns ({len(df.columns)}개):")
        for i, col in enumerate(df.columns[:10]):
            print(f"    {i+1}. {col}")
        if len(df.columns) > 10:
            print(f"    ... 외 {len(df.columns)-10}개")
        
        print(f"\n  통계:")
        numeric_cols = df.select_dtypes(include=[np.number]).columns[:5]
        for col in numeric_cols:
            print(f"    {col}: mean={df[col].mean():.2f}, std={df[col].std():.2f}")


def visualize_user_logs(df: pd.DataFrame, output_dir: Path):
    """User Logs 시각화"""
    print("\n🎨 User Logs 시각화 중...")
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('User Logs 집계 데이터 시각화', fontsize=16, fontweight='bold')
    
    # 1. 활동 일수 분포 (W30)
    if 'num_days_active_w30' in df.columns:
        ax = axes[0, 0]
        df['num_days_active_w30'].hist(bins=31, ax=ax, color='steelblue', edgecolor='white')
        ax.set_title('활동 일수 분포 (30일)')
        ax.set_xlabel('활동 일수')
        ax.set_ylabel('사용자 수')
    
    # 2. 총 청취 시간 분포
    if 'total_secs_w30' in df.columns:
        ax = axes[0, 1]
        # 상위 99% 제한 (이상치 제외)
        data = df['total_secs_w30'].clip(upper=df['total_secs_w30'].quantile(0.99))
        data.hist(bins=50, ax=ax, color='coral', edgecolor='white')
        ax.set_title('총 청취 시간 분포 (30일)')
        ax.set_xlabel('청취 시간 (초)')
        ax.set_ylabel('사용자 수')
    
    # 3. 스킵율 분포
    if 'skip_ratio_w30' in df.columns:
        ax = axes[0, 2]
        df['skip_ratio_w30'].hist(bins=50, ax=ax, color='tomato', edgecolor='white')
        ax.set_title('스킵율 분포 (30일)')
        ax.set_xlabel('스킵율')
        ax.set_ylabel('사용자 수')
    
    # 4. 완주율 분포
    if 'completion_ratio_w30' in df.columns:
        ax = axes[1, 0]
        df['completion_ratio_w30'].hist(bins=50, ax=ax, color='seagreen', edgecolor='white')
        ax.set_title('완주율 분포 (30일)')
        ax.set_xlabel('완주율')
        ax.set_ylabel('사용자 수')
    
    # 5. 사용량 변화 추세 (W7/W30)
    if 'secs_trend_w7_w30' in df.columns:
        ax = axes[1, 1]
        data = df['secs_trend_w7_w30'].clip(0, 2)  # 0~2 범위로 제한
        data.hist(bins=50, ax=ax, color='purple', edgecolor='white')
        ax.axvline(x=1.0, color='red', linestyle='--', label='변화 없음')
        ax.set_title('사용량 변화 추세 (최근7일/전체30일)')
        ax.set_xlabel('비율 (1=변화없음, <1=감소)')
        ax.set_ylabel('사용자 수')
        ax.legend()
    
    # 6. 윈도우별 평균 비교
    ax = axes[1, 2]
    windows = ['w7', 'w14', 'w21', 'w30']
    means = []
    for w in windows:
        col = f'num_songs_{w}'
        if col in df.columns:
            means.append(df[col].mean())
        else:
            means.append(0)
    
    colors = ['#ff6b6b', '#feca57', '#48dbfb', '#1dd1a1']
    ax.bar(windows, means, color=colors, edgecolor='white')
    ax.set_title('윈도우별 평균 곡 수')
    ax.set_xlabel('윈도우')
    ax.set_ylabel('평균 곡 수')
    
    plt.tight_layout()
    
    output_path = output_dir / 'user_logs_visualization.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"  ✓ 저장: {output_path}")
    plt.close()


def visualize_transactions(df: pd.DataFrame, output_dir: Path):
    """Transactions 시각화"""
    print("\n🎨 Transactions 시각화 중...")
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Transactions 집계 데이터 시각화', fontsize=16, fontweight='bold')
    
    # 1. 마지막 결제 후 경과일
    if 'days_since_last_payment' in df.columns:
        ax = axes[0, 0]
        data = df['days_since_last_payment'].clip(upper=365)
        data.hist(bins=50, ax=ax, color='steelblue', edgecolor='white')
        ax.set_title('마지막 결제 후 경과일')
        ax.set_xlabel('경과일')
        ax.set_ylabel('사용자 수')
    
    # 2. 만료까지 남은 일수
    if 'days_to_expire' in df.columns:
        ax = axes[0, 1]
        data = df['days_to_expire'].clip(-100, 365)
        data.hist(bins=50, ax=ax, color='coral', edgecolor='white')
        ax.axvline(x=0, color='red', linestyle='--', label='만료일')
        ax.set_title('만료까지 남은 일수')
        ax.set_xlabel('일수 (음수=이미 만료)')
        ax.set_ylabel('사용자 수')
        ax.legend()
    
    # 3. 자동갱신 여부
    if 'is_auto_renew_last' in df.columns:
        ax = axes[0, 2]
        counts = df['is_auto_renew_last'].value_counts()
        colors = ['#ff6b6b', '#1dd1a1']
        ax.pie(counts, labels=['OFF', 'ON'], autopct='%1.1f%%', colors=colors)
        ax.set_title('자동갱신 설정')
    
    # 4. 총 결제 횟수
    if 'total_payment_count' in df.columns:
        ax = axes[1, 0]
        data = df['total_payment_count'].clip(upper=50)
        data.hist(bins=50, ax=ax, color='seagreen', edgecolor='white')
        ax.set_title('총 결제 횟수')
        ax.set_xlabel('결제 횟수')
        ax.set_ylabel('사용자 수')
    
    # 5. 취소 이력 여부
    if 'has_cancelled' in df.columns:
        ax = axes[1, 1]
        counts = df['has_cancelled'].value_counts()
        colors = ['#1dd1a1', '#ff6b6b']
        ax.pie(counts, labels=['취소 없음', '취소 있음'], autopct='%1.1f%%', colors=colors)
        ax.set_title('취소 이력')
    
    # 6. 평균 결제액
    if 'avg_amount_per_payment' in df.columns:
        ax = axes[1, 2]
        data = df['avg_amount_per_payment'].clip(upper=500)
        data.hist(bins=50, ax=ax, color='purple', edgecolor='white')
        ax.set_title('평균 결제액')
        ax.set_xlabel('금액')
        ax.set_ylabel('사용자 수')
    
    plt.tight_layout()
    
    output_path = output_dir / 'transactions_visualization.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"  ✓ 저장: {output_path}")
    plt.close()


def create_correlation_heatmap(df: pd.DataFrame, name: str, output_dir: Path):
    """상관관계 히트맵"""
    print(f"\n🎨 {name} 상관관계 히트맵 생성 중...")
    
    # 수치형 컬럼만 선택 (상위 15개)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 15:
        # 분산이 큰 상위 15개 선택
        variances = df[numeric_cols].var().sort_values(ascending=False)
        numeric_cols = variances.head(15).index.tolist()
    
    corr = df[numeric_cols].corr()
    
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdYlBu_r', 
                center=0, ax=ax, annot_kws={'size': 8})
    ax.set_title(f'{name} 주요 피처 상관관계', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    output_path = output_dir / f'{name}_correlation.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"  ✓ 저장: {output_path}")
    plt.close()


def run_visualization():
    """시각화 파이프라인 실행"""
    print("=" * 60)
    print("🚀 집계 데이터 시각화")
    print("=" * 60)
    
    # 출력 폴더 생성
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 데이터 로드
    data = load_aggregated_data()
    
    if not data:
        print("❌ 로드할 데이터가 없습니다. 집계를 먼저 실행하세요.")
        return
    
    # 데이터 요약 출력
    print_data_summary(data)
    
    # 시각화
    if 'user_logs' in data:
        visualize_user_logs(data['user_logs'], OUTPUT_DIR)
        create_correlation_heatmap(data['user_logs'], 'user_logs', OUTPUT_DIR)
    
    if 'transactions' in data:
        visualize_transactions(data['transactions'], OUTPUT_DIR)
        create_correlation_heatmap(data['transactions'], 'transactions', OUTPUT_DIR)
    
    print("\n" + "=" * 60)
    print("✅ 시각화 완료!")
    print("=" * 60)
    print(f"\n📁 출력 폴더: {OUTPUT_DIR}")
    print("  - user_logs_visualization.png")
    print("  - user_logs_correlation.png")
    print("  - transactions_visualization.png")
    print("  - transactions_correlation.png")


if __name__ == "__main__":
    run_visualization()

