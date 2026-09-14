"""
3차 과제 3단계: K-means 군집분석

목표: 262개 주를, 7개 카테고리 관심도 패턴이 비슷한 것끼리
     사람이 기준을 정하지 않고 알고리즘이 스스로 몇 개의 그룹으로 나누게 합니다.

주의: 카테고리마다 값의 크기(스케일)가 다릅니다
     (예: food delivery는 보통 60~90, organic food는 보통 7~20).
     스케일이 큰 카테고리가 거리 계산을 지배해버리는 걸 막기 위해,
     먼저 표준화(StandardScaler)를 거칩니다.
     R로 치면 scale() 함수와 같은 역할입니다.

실행 전 준비:
  pip install pandas scikit-learn matplotlib
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt

WIDE_CSV = 'food_categories_wide.csv'


def main():
    wide = pd.read_csv(WIDE_CSV, index_col='week', parse_dates=True)

    # ---------- 표준화 ----------
    scaler = StandardScaler()
    X = scaler.fit_transform(wide)

    # ---------- 적절한 군집 개수(k) 찾기: 실루엣 점수 ----------
    # 실루엣 점수: 군집이 얼마나 "잘 나뉘었는지" 보는 지표 (1에 가까울수록 좋음)
    print("=== k(군집 개수)별 실루엣 점수 ===")
    scores = {}
    for k in range(2, 7):
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X)
        score = silhouette_score(X, labels)
        scores[k] = score
        print(f"  k={k}: {score:.3f}")

    best_k = max(scores, key=scores.get)
    print(f"\n실루엣 점수가 가장 높은 k = {best_k} (이 값을 최종 군집 개수로 사용합니다)")

    # ---------- 최종 군집분석 ----------
    km = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    wide['cluster'] = km.fit_predict(X)

    print(f"\n=== 군집별 주(week) 개수 ===")
    print(wide['cluster'].value_counts().sort_index())

    print(f"\n=== 군집별 카테고리 평균 (원래 척도로 환산) ===")
    print(wide.groupby('cluster').mean().round(1))

    print(f"\n=== 군집별로 어느 달(month)이 많이 포함되는지 ===")
    wide['month'] = wide.index.month
    print(pd.crosstab(wide['cluster'], wide['month']))

    wide.to_csv('food_categories_with_cluster.csv')
    print("\nCSV 저장 완료: food_categories_with_cluster.csv")

    # ---------- 시각화: 시간 흐름에 따라 군집이 어떻게 분포하는지 ----------
    plt.figure(figsize=(12, 3))
    colors = plt.cm.tab10(wide['cluster'] / wide['cluster'].max())
    plt.scatter(wide.index, [1] * len(wide), c=wide['cluster'], cmap='tab10', s=20)
    plt.yticks([])
    plt.title('Cluster assignment over time (each dot = one week)')
    plt.xlabel('Week')
    plt.tight_layout()
    plt.savefig('cluster_timeline.png', dpi=120)
    print("타임라인 시각화 저장 완료: cluster_timeline.png")


if __name__ == '__main__':
    main()
