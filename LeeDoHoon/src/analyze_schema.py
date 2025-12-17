"""
데이터 스키마 분석 스크립트
"""
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'data'

def analyze_all():
    print("=" * 60)
    print("TRAIN_V2")
    print("=" * 60)
    df = pd.read_csv(DATA_DIR / 'train_v2.csv')
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"Dtypes:\n{df.dtypes}")
    print(f"\nFirst 3 rows:\n{df.head(3)}")
    print(f"\nNull counts:\n{df.isnull().sum()}")
    print(f"\nis_churn distribution:")
    print(df['is_churn'].value_counts())
    print(f"is_churn ratio: {df['is_churn'].mean()*100:.2f}%")
    
    print("\n" + "=" * 60)
    print("MEMBERS_V3")
    print("=" * 60)
    df = pd.read_csv(DATA_DIR / 'members_v3.csv')
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"Dtypes:\n{df.dtypes}")
    print(f"\nFirst 3 rows:\n{df.head(3)}")
    print(f"\nNull counts:\n{df.isnull().sum()}")
    print(f"\nregistration_init_time range:")
    df['registration_init_time'] = pd.to_datetime(df['registration_init_time'], format='%Y%m%d', errors='coerce')
    print(f"  Min: {df['registration_init_time'].min()}")
    print(f"  Max: {df['registration_init_time'].max()}")
    print(f"\ngender distribution:")
    print(df['gender'].value_counts(dropna=False))
    print(f"\nbd (age) stats:")
    print(df['bd'].describe())
    
    print("\n" + "=" * 60)
    print("TRANSACTIONS_V2")
    print("=" * 60)
    df = pd.read_csv(DATA_DIR / 'transactions_v2.csv')
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"Dtypes:\n{df.dtypes}")
    print(f"\nFirst 3 rows:\n{df.head(3)}")
    print(f"\nNull counts:\n{df.isnull().sum()}")
    print(f"\ntransaction_date range:")
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], format='%Y%m%d', errors='coerce')
    print(f"  Min: {df['transaction_date'].min()}")
    print(f"  Max: {df['transaction_date'].max()}")
    print(f"\nmembership_expire_date range:")
    df['membership_expire_date'] = pd.to_datetime(df['membership_expire_date'], format='%Y%m%d', errors='coerce')
    print(f"  Min: {df['membership_expire_date'].min()}")
    print(f"  Max: {df['membership_expire_date'].max()}")
    print(f"\nis_auto_renew distribution:")
    print(df['is_auto_renew'].value_counts())
    print(f"\nis_cancel distribution:")
    print(df['is_cancel'].value_counts())
    print(f"\npayment_method_id distribution:")
    print(df['payment_method_id'].value_counts().head(10))
    
    print("\n" + "=" * 60)
    print("USER_LOGS_V2")
    print("=" * 60)
    df = pd.read_csv(DATA_DIR / 'user_logs_v2.csv')
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"Dtypes:\n{df.dtypes}")
    print(f"\nFirst 3 rows:\n{df.head(3)}")
    print(f"\nNull counts:\n{df.isnull().sum()}")
    print(f"\ndate range:")
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d', errors='coerce')
    print(f"  Min: {df['date'].min()}")
    print(f"  Max: {df['date'].max()}")
    print(f"\nUnique users: {df['msno'].nunique()}")
    
    # 테이블 간 관계
    print("\n" + "=" * 60)
    print("TABLE RELATIONSHIPS")
    print("=" * 60)
    train = pd.read_csv(DATA_DIR / 'train_v2.csv')
    members = pd.read_csv(DATA_DIR / 'members_v3.csv')
    transactions = pd.read_csv(DATA_DIR / 'transactions_v2.csv')
    user_logs = pd.read_csv(DATA_DIR / 'user_logs_v2.csv')
    
    train_users = set(train['msno'])
    members_users = set(members['msno'])
    txn_users = set(transactions['msno'])
    logs_users = set(user_logs['msno'])
    
    print(f"train_v2 unique users: {len(train_users):,}")
    print(f"members_v3 unique users: {len(members_users):,}")
    print(f"transactions_v2 unique users: {len(txn_users):,}")
    print(f"user_logs_v2 unique users: {len(logs_users):,}")
    
    print(f"\ntrain ∩ members: {len(train_users & members_users):,}")
    print(f"train ∩ transactions: {len(train_users & txn_users):,}")
    print(f"train ∩ user_logs: {len(train_users & logs_users):,}")
    
    print(f"\ntrain - members (no member info): {len(train_users - members_users):,}")
    print(f"train - transactions (no txn): {len(train_users - txn_users):,}")
    print(f"train - user_logs (no logs): {len(train_users - logs_users):,}")

if __name__ == "__main__":
    analyze_all()

