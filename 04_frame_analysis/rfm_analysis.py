"""
4차 과제: RFM(Recency, Frequency, Monetary) 고객 세분화 분석

데이터: Kaggle "Online Retail Dataset" (영국 온라인 소매업체 거래 내역, 2009.12~2010.12)

흐름:
  1) 정제: Customer ID 결측/취소 거래/비정상 값 제거
  2) RFM 계산: 고객별 최근성(R)·구매빈도(F)·구매액(M)
  3) 5분위(quintile) 점수화 후 세그먼트 이름 부여
  4) 세그먼트별 분포 및 인사이트 시각화

실행 전 준비:
  pip install pandas matplotlib openpyxl
"""

import pandas as pd
import matplotlib.pyplot as plt
import re

INPUT_XLSX = 'Online Retail Dataset.xlsx'


def clean_data(df):
    """RFM 계산에 방해되는 행들을 제거합니다."""
    before = len(df)

    df = df.dropna(subset=['Customer ID'])                          # 고객 특정 불가
    df = df[~df['Invoice'].astype(str).str.startswith('C')]         # 취소 거래
    df = df[(df['Quantity'] > 0) & (df['Price'] > 0)]                # 반품/샘플(가격 0) 제외

    print(f"정제 전: {before:,}행 -> 정제 후: {len(df):,}행 "
          f"({(1 - len(df)/before)*100:.1f}% 제거)")

    df['TotalPrice'] = df['Quantity'] * df['Price']
    return df


def compute_rfm(df):
    """고객별 Recency, Frequency, Monetary를 계산합니다."""
    reference_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)

    rfm = df.groupby('Customer ID').agg(
        Recency=('InvoiceDate', lambda x: (reference_date - x.max()).days),
        Frequency=('Invoice', 'nunique'),
        Monetary=('TotalPrice', 'sum')
    ).reset_index()

    return rfm


def score_rfm(rfm):
    """R, F, M을 각각 5분위로 나눠 1~5점을 매깁니다.
    Recency는 값이 작을수록(최근일수록) 좋은 거라 점수를 거꾸로 매깁니다.
    R로 치면 dplyr::ntile()과 같은 개념입니다.
    """
    rfm['R_score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm['F_score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm['M_score'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5]).astype(int)

    rfm['RF_segment_code'] = rfm['R_score'].astype(str) + rfm['F_score'].astype(str)
    return rfm


def assign_segment(rfm):
    """R+F 점수 조합을 업계에서 흔히 쓰는 세그먼트 이름으로 매핑합니다."""
    segment_map = {
        r'[1-2][1-2]': 'Hibernating',
        r'[1-2][3-4]': 'At Risk',
        r'[1-2]5': "Cant Lose",
        r'3[1-2]': 'About to Sleep',
        r'33': 'Need Attention',
        r'[3-4][4-5]': 'Loyal Customers',
        r'41': 'Promising',
        r'51': 'New Customers',
        r'[4-5][2-3]': 'Potential Loyalists',
        r'5[4-5]': 'Champions',
    }

    def match_segment(code):
        for pattern, name in segment_map.items():
            if re.fullmatch(pattern, code):
                return name
        return 'Other'

    rfm['Segment'] = rfm['RF_segment_code'].apply(match_segment)
    return rfm


def main():
    df = pd.read_excel(INPUT_XLSX)
    df = clean_data(df)

    rfm = compute_rfm(df)
    print(f"\nRFM 계산 완료: 고객 {len(rfm):,}명")
    print(rfm[['Customer ID', 'Recency', 'Frequency', 'Monetary']].describe().round(1))

    rfm = score_rfm(rfm)
    rfm = assign_segment(rfm)

    print("\n=== 세그먼트별 고객 수 및 평균 지표 ===")
    summary = rfm.groupby('Segment').agg(
        Customers=('Customer ID', 'count'),
        Avg_Recency=('Recency', 'mean'),
        Avg_Frequency=('Frequency', 'mean'),
        Avg_Monetary=('Monetary', 'mean')
    ).round(1).sort_values('Customers', ascending=False)
    print(summary)

    rfm.to_csv('rfm_result.csv', index=False)
    print("\nCSV 저장 완료: rfm_result.csv")

    # ---------- 시각화 1: 세그먼트별 고객 수 ----------
    plt.figure(figsize=(9, 5))
    order = summary.index
    plt.barh(order, summary['Customers'], color='steelblue')
    plt.xlabel('Number of customers')
    plt.title('Customer count by RFM segment')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig('rfm_segment_counts.png', dpi=120)

    # ---------- 시각화 2: 세그먼트별 총 매출 기여도 ----------
    monetary_by_segment = rfm.groupby('Segment')['Monetary'].sum().sort_values(ascending=False)
    plt.figure(figsize=(9, 5))
    plt.barh(monetary_by_segment.index, monetary_by_segment.values, color='darkorange')
    plt.xlabel('Total monetary value (GBP)')
    plt.title('Total revenue contribution by segment')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig('rfm_segment_revenue.png', dpi=120)

    print("\n시각화 저장 완료: rfm_segment_counts.png, rfm_segment_revenue.png")


if __name__ == '__main__':
    main()
