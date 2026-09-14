"""
3차 과제 5단계 보강: LIME으로 SHAP 결과 교차검증

목표: SHAP과는 다른 방식으로 작동하는 LIME을 같은 랜덤포레스트 모델에 적용해서,
     "이 주가 이례적 시기인지" 판별에 어느 카테고리가 중요한지를 다시 뽑아보고,
     SHAP이 찾은 순위(drink > beverage > snack > ...)와 얼마나 일치하는지 비교합니다.

SHAP과 LIME의 차이:
  - SHAP: 게임이론 기반으로, 모든 변수 조합을 수학적으로 고려해서 "공정한 기여도"를 계산
  - LIME: 예측하고 싶은 데이터 주변에 가상의 비슷한 데이터를 many개 만들어서,
          그 주변에서는 복잡한 모델을 간단한 선형모델로 근사해 설명
  즉 방법은 다르지만, 같은 결론에 도달하면 그 결론의 신뢰도가 더 높아집니다.

실행 전 준비:
  pip install pandas scikit-learn lime
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from lime.lime_tabular import LimeTabularExplainer

INPUT_CSV = 'food_categories_with_cluster.csv'
N_SAMPLES_TO_EXPLAIN = 15   # LIME은 예측 하나하나를 설명하는 방식이라, 여러 개를 뽑아서 평균냅니다


def main():
    df = pd.read_csv(INPUT_CSV, index_col='week', parse_dates=True)

    feature_cols = ['beverage', 'dessert', 'drink', 'fast food',
                     'food delivery', 'organic food', 'snack']

    X = df[feature_cols]
    y = df['cluster']

    # SHAP 단계와 동일한 조건으로 재현 (같은 random_state)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    # ---------- LIME 설명기 준비 ----------
    explainer = LimeTabularExplainer(
        X_train.values,
        feature_names=feature_cols,
        class_names=['평상시', '이례적 시기'],
        mode='classification'
    )

    # ---------- 테스트셋 중 여러 샘플을 골라 LIME으로 설명하고, 기여도를 누적 ----------
    n = min(N_SAMPLES_TO_EXPLAIN, len(X_test))
    importance_totals = {col: 0.0 for col in feature_cols}

    print(f"=== LIME으로 {n}개 샘플 개별 설명 중 ===")
    for i in range(n):
        row = X_test.iloc[i].values
        exp = explainer.explain_instance(
            row, model.predict_proba, num_features=len(feature_cols)
        )
        # exp.as_list()는 [('beverage <= 40.00', 0.12), ...] 형태로 나오므로
        # 조건문 앞부분에서 실제 카테고리 이름만 뽑아서 매칭합니다.
        for condition, weight in exp.as_list():
            for col in feature_cols:
                if col in condition:
                    importance_totals[col] += abs(weight)
                    break

    lime_importance = pd.Series(importance_totals).sort_values(ascending=False) / n

    print("\n=== LIME 기준 카테고리별 평균 영향도 ===")
    print(lime_importance.round(3))

    # ---------- SHAP 순위와 비교 ----------
    # (지난 단계 step5_rf_shap.py에서 나온 순위를 여기 직접 옮겨서 비교합니다)
    shap_ranking = ['drink', 'beverage', 'snack', 'organic food',
                     'fast food', 'dessert', 'food delivery']
    lime_ranking = lime_importance.index.tolist()

    comparison = pd.DataFrame({
        'SHAP 순위': shap_ranking,
        'LIME 순위': lime_ranking,
    })
    print("\n=== SHAP vs LIME 중요도 순위 비교 ===")
    print(comparison)

    # 상위 3개가 얼마나 겹치는지로 간단히 일치도 확인
    overlap = set(shap_ranking[:3]) & set(lime_ranking[:3])
    print(f"\n상위 3개 중 겹치는 카테고리: {overlap} ({len(overlap)}/3 일치)")

    # 예시 하나 자세히 출력 (보고서에 캡처해서 넣기 좋음)
    print("\n=== 샘플 1개 상세 설명 예시 ===")
    example = explainer.explain_instance(
        X_test.iloc[0].values, model.predict_proba, num_features=len(feature_cols)
    )
    for condition, weight in example.as_list():
        direction = "이례적 시기 쪽으로" if weight > 0 else "평상시 쪽으로"
        print(f"  {condition}: {weight:+.3f} ({direction} 영향)")

    # ---------- 시각화 1: LIME 자체 설명 그래프 (샘플 1개) ----------
    fig = example.as_pyplot_figure()
    fig.set_size_inches(8, 5)
    plt.title('LIME explanation for one sample\n(positive = pushes toward "unusual period")')
    plt.tight_layout()
    plt.savefig('lime_example_explanation.png', dpi=120, bbox_inches='tight')
    print("\nLIME 개별 설명 시각화 저장 완료: lime_example_explanation.png")

    # ---------- 시각화 2: SHAP vs LIME 중요도 비교 막대그래프 ----------
    shap_importance = pd.Series(
        {'drink': 0.067, 'beverage': 0.058, 'snack': 0.039, 'organic food': 0.027,
         'fast food': 0.025, 'dessert': 0.017, 'food delivery': 0.007}
    )
    compare_df = pd.DataFrame({
        'SHAP': shap_importance,
        'LIME': lime_importance
    }).loc[feature_cols]

    compare_df.plot(kind='barh', figsize=(7, 5))
    plt.xlabel('Average importance (absolute value)')
    plt.title('SHAP vs LIME: feature importance comparison')
    plt.tight_layout()
    plt.savefig('shap_vs_lime_comparison.png', dpi=120, bbox_inches='tight')
    print("SHAP vs LIME 비교 시각화 저장 완료: shap_vs_lime_comparison.png")


if __name__ == '__main__':
    main()