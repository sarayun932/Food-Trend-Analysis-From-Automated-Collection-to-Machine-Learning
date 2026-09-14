"""
3차 과제 5단계: 랜덤포레스트 + SHAP

목표: "이 주가 평상시(cluster 0)인지, 이례적 고관심 시기(cluster 1)인지"를
     7개 카테고리 값만 보고 맞추는 분류 모델(랜덤포레스트)을 만들고,
     SHAP으로 "어느 카테고리가 이 판단에 가장 큰 영향을 줬는지" 뜯어봅니다.

지금까지 상관분석 -> 군집분석 -> PCA로 "카테고리들이 두 개의 축(①일반 식품군
②food delivery)으로 나뉜다"는 걸 확인했는데, 이번엔 그 중 어떤 카테고리가
"이례적 시기 판별"에 실제로 가장 크게 기여하는지 숫자로 뜯어보는 마지막 단계입니다.

실행 전 준비:
  pip install pandas scikit-learn shap matplotlib
"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import shap
import matplotlib.pyplot as plt

INPUT_CSV = 'food_categories_with_cluster.csv'


def main():
    df = pd.read_csv(INPUT_CSV, index_col='week', parse_dates=True)

    feature_cols = ['beverage', 'dessert', 'drink', 'fast food',
                     'food delivery', 'organic food', 'snack']

    X = df[feature_cols]
    y = df['cluster']

    # 시계열이지만 이번엔 "패턴 분류"가 목적이라, 일반적인 train/test 분리를 씁니다.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("=== 분류 성능 ===")
    print(classification_report(y_test, y_pred, target_names=['평상시(0)', '이례적 시기(1)']))

    # ---------- SHAP 적용 ----------
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)

    # 이진 분류라 shap_values가 클래스별로 나뉘어 있을 수 있음 -> "이례적 시기(1)"에 대한 값만 사용
    if isinstance(shap_values, list):
        sv = shap_values[1]
    else:
        sv = shap_values[:, :, 1] if shap_values.ndim == 3 else shap_values

    print("\n=== 카테고리별 평균 SHAP 영향도 (절댓값 기준, 클수록 중요) ===")
    importance = pd.Series(
        abs(sv).mean(axis=0), index=feature_cols
    ).sort_values(ascending=False)
    print(importance.round(3))

    # ---------- 시각화 ----------
    plt.figure()
    shap.summary_plot(sv, X_test, show=False)
    plt.tight_layout()
    plt.savefig('shap_summary.png', dpi=120, bbox_inches='tight')
    print("\nSHAP 요약 시각화 저장 완료: shap_summary.png")


if __name__ == '__main__':
    main()
