"""
3차 과제 4단계: PCA (주성분분석, 차원축소)

목표: 7개 카테고리를 정보 손실을 최소화하면서 2개의 "핵심 축"으로 압축합니다.
     이 압축된 2축 공간에, 3단계(K-means)에서 찾은 군집(평상시/이례적 시기)을
     색으로 표시해서, 사람이 눈으로 봐도 두 군집이 실제로 잘 갈라지는지 검증합니다.

R로 치면 prcomp() 함수와 같은 개념입니다.

실행 전 준비:
  pip install pandas scikit-learn matplotlib
"""

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

INPUT_CSV = 'food_categories_with_cluster.csv'   # 3단계에서 저장한, cluster 컬럼이 포함된 파일


def main():
    df = pd.read_csv(INPUT_CSV, index_col='week', parse_dates=True)

    feature_cols = ['beverage', 'dessert', 'drink', 'fast food',
                     'food delivery', 'organic food', 'snack']

    X = df[feature_cols]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # ---------- PCA 적용 ----------
    pca = PCA()
    pca.fit(X_scaled)

    print("=== 각 주성분이 설명하는 분산 비율 ===")
    for i, ratio in enumerate(pca.explained_variance_ratio_, start=1):
        print(f"  PC{i}: {ratio*100:.1f}%")
    cum = pca.explained_variance_ratio_[:2].sum() * 100
    print(f"\nPC1 + PC2 두 개만으로 전체 정보의 {cum:.1f}%를 설명함")

    print("\n=== PC1, PC2에 각 카테고리가 얼마나 기여하는지 (loading) ===")
    loadings = pd.DataFrame(
        pca.components_[:2].T,
        columns=['PC1', 'PC2'],
        index=feature_cols
    )
    print(loadings.round(2))

    # ---------- 2차원으로 압축한 좌표 계산 ----------
    pcs = pca.transform(X_scaled)[:, :2]
    df['PC1'] = pcs[:, 0]
    df['PC2'] = pcs[:, 1]

    # ---------- 시각화: PC1-PC2 평면에 군집별로 색칠 ----------
    plt.figure(figsize=(7, 6))
    scatter = plt.scatter(df['PC1'], df['PC2'], c=df['cluster'], cmap='tab10', alpha=0.7)
    plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)')
    plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)')
    plt.title('PCA: 7 categories compressed into 2 axes (colored by cluster)')
    plt.colorbar(scatter, label='Cluster (from K-means)')
    plt.tight_layout()
    plt.savefig('pca_scatter.png', dpi=120)
    print("\nPCA 시각화 저장 완료: pca_scatter.png")


if __name__ == '__main__':
    main()
