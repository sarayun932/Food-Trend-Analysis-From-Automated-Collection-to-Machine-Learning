# Stage 3: ML-Based Structural Analysis

## Purpose
Move beyond category-level visual exploration (Stage 2) to test whether the relationships between food categories hold up under independent statistical and machine-learning methods — correlation, clustering, dimensionality reduction, and model interpretability (SHAP, LIME).

## Why a Different Dataset
The keyword-level data used in Stages 1–2 (`query`, `category`, `trend_score`) is categorical/discovery-based and not structurally suited to algorithms that require continuous numeric variables (correlation, clustering, PCA). Instead, this stage uses a separate dataset collected in Stage 2: **weekly interest scores for 7 categories over ~5 years (262 weeks)**, where each category is an independent numeric variable with enough observations for these methods.

## Data
`weekly_category_trends.csv` — long-format weekly interest data reshaped into wide format (262 rows × 7 category columns: `beverage`, `drink`, `snack`, `organic food`, `dessert`, `fast food`, `food delivery`).

## Analysis

### 1. Correlation Analysis
Computed pairwise correlation coefficients across the 7 categories.
- `beverage`, `drink`, `snack`, `organic food` are strongly correlated (r = 0.71–0.85)
- `dessert` and `fast food` show moderate correlation (r = 0.57)
- `food delivery` is essentially uncorrelated with all other categories (r = -0.21 to 0.18)

### 2. K-Means Clustering
Optimal cluster count (k=2) selected by silhouette score.
- **Cluster 0** (227 weeks, "normal periods"): all categories at typical baseline levels
- **Cluster 1** (35 weeks, "unusually high-interest periods"): nearly all categories elevated simultaneously, *except* `food delivery`
- Re-tested an initial "April seasonality" hypothesis across 3–5 years; only `organic food` and `snack` showed a consistent April peak. `beverage` (May), `drink` (June), `fast food` (July), and `dessert` (November) each peaked in different months — the hypothesis was rejected. Cluster 1's structural cause remains unexplained within this analysis and would need external data (news, market events) to investigate further.

### 3. PCA (Dimensionality Reduction)
PC1 (57.4%) + PC2 (16.7%) explain 74.1% of total variance.
- **PC1**: a general "food interest" axis with even contributions from `beverage`, `drink`, `snack`, `organic food`, `dessert`
- **PC2**: dominated almost entirely by `food delivery` (loading 0.83)
- Plotting K-means clusters on the PC1–PC2 plane visually confirmed Cluster 1 separating clearly along PC1

**Interim conclusion**: Correlation, clustering, and PCA — three independent methods — all converge on the same finding: (1) four categories move together on one shared axis, and (2) `food delivery` moves entirely independently.

### 4. Random Forest + SHAP
Trained a classifier to predict whether a given week belongs to Cluster 0 or Cluster 1, using the 7 category values as features.
- Accuracy: 97% (test set had only 9 Cluster-1 samples, so treat as directional, not conclusive)
- SHAP importance ranking: `drink` > `beverage` > `snack` > `organic food` > `fast food` > `dessert` > `food delivery`
- `food delivery` again shows the lowest importance (0.007), with SHAP values clustered near zero
- High `drink` and `beverage` values push predictions strongly toward "unusual period"

### 5. LIME (Cross-Validation of SHAP)
Applied LIME — a different interpretability method (local linear approximation vs. SHAP's game-theoretic attribution) — to the same model, to check whether an independently-computed importance ranking agrees with SHAP.

| Rank | SHAP | LIME |
|---|---|---|
| 1 | drink | beverage |
| 2 | beverage | drink |
| 3 | snack | organic food |
| 4 | organic food | fast food |
| 5 | fast food | snack |
| 6 | dessert | dessert |
| 7 | food delivery | food delivery |

- Top 2 categories (`drink`, `beverage`) rank highest in both methods
- `food delivery` ranks last (7th) in **both** methods, with a visibly negligible bar length in both plots
- `dessert` ranks 6th in both methods
- Individual sample explanation (LIME): for one "normal period" week, `beverage`, `drink`, and `organic food` contributed most to the classification, while `food delivery`'s contribution was near zero

## Key Findings
- **Five independent methods — correlation, clustering, PCA, SHAP, and LIME — all converge on the same structural conclusion: `food delivery` moves independently of the other 6 food categories.** This consistency across methods with different underlying assumptions suggests a genuine structural pattern in the data, not a coincidence of any single technique.
- `beverage` and `drink` are the strongest and most consistent drivers of "unusual high-interest periods" across every method tested.
- An initial seasonality hypothesis (shared April peak) was tested and rejected — each category peaks in a different month, and Cluster 1's cause remains an open question for further investigation.

## Files
```
├── weekly_category_trends.csv       # 262 weeks × 7 categories, wide format
├── wide_format_preview.png
├── correlation_heatmap.png
├── cluster_timeline.png
├── pca_scatter.png
├── shap_summary.png
├── shap_vs_lime_comparison.png
├── lime_example_explanation.png
├── analysis.ipynb                   # (파일명 확인 필요)
└── README.md
```
