"""
3차 과제 1~2단계: 데이터 재구성 + 상관분석

1) '주 x 카테고리' 형태(long format)였던 데이터를
   '주 하나당 7개 카테고리 값을 나란히 놓은 표'(wide format)로 재구성합니다.
2) 7개 카테고리 간 상관계수를 계산하고 히트맵으로 시각화합니다.

R로 치면 tidyr::pivot_wider() + cor() + heatmap()과 같은 흐름입니다.

실행 전 준비:
  pip install pandas seaborn matplotlib
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

INPUT_CSV = 'food_categories_5yr_trend_US.csv'
WIDE_CSV = 'food_categories_wide.csv'


def main():
    df = pd.read_csv(INPUT_CSV)
    df['week'] = pd.to_datetime(df['week'])

    # ---------- 1) wide format으로 재구성 ----------
    # long format: week, category, interest_score (한 행 = 한 주의 한 카테고리)
    # wide format: week가 행, 7개 카테고리가 각각 열이 됨 (한 행 = 한 주의 7개 값)
    wide = df.pivot(index='week', columns='category', values='interest_score')
    wide = wide.sort_index()

    print(f"재구성 완료: {wide.shape[0]}개 주 x {wide.shape[1]}개 카테고리")
    print(wide.head())

    wide.to_csv(WIDE_CSV)
    print(f"\nwide 형태 CSV 저장 완료: {WIDE_CSV}")

    # ---------- 2) 상관분석 ----------
    corr = wide.corr()

    print("\n=== 카테고리 간 상관계수 ===")
    print(corr.round(2))

    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', vmin=-1, vmax=1,
                square=True, cbar_kws={'label': 'Correlation'})
    plt.title('Correlation between Food Categories (weekly interest, 5yr)')
    plt.tight_layout()
    plt.savefig('correlation_heatmap.png', dpi=120)
    print("\n히트맵 저장 완료: correlation_heatmap.png")

    # 상관관계가 특히 강한 쌍만 따로 뽑아서 보기 쉽게 정리
    print("\n=== 상관계수 절댓값 0.5 이상인 카테고리 쌍 ===")
    pairs = corr.where(~corr.isna()).stack()
    pairs = pairs[pairs.index.get_level_values(0) < pairs.index.get_level_values(1)]
    strong = pairs[pairs.abs() >= 0.5].sort_values(ascending=False)
    print(strong.round(2))


if __name__ == '__main__':
    main()
