# Stage 3: ML-Based Structural Analysis

## Purpose
Move beyond category-level visual exploration (Stage 2) to test whether the relationships between food categories hold up under independent statistical and machine-learning methods — correlation, clustering, dimensionality reduction, and model interpretability (SHAP, LIME).

## Why a Different Dataset
The keyword-level data used in Stages 1–2 (`query`, `category`, `trend_score`) is categorical/discovery-based and not structurally suited to algorithms that require continuous numeric variables (correlation, clustering, PCA). Instead, this stage collects a new dataset via `pytrends`' `interest_over_time()`: **weekly interest scores for 7 food categories in the US, over the last 5 years (262 weeks)**. Because a single 5-year request is normalized against one shared 0–100 baseline, category values and seasonality are comparable on the same scale — unlike `related_queries()` used in Stages 1–2, which is only for keyword discovery. Each category here is an independent numeric variable with enough observations for correlation/clustering/PCA/SHAP.

## Data Pipeline
| File | Produced by | Description |
|---|---|---|
| `food_categories_5yr_trend_US.csv` | `google_five_years.py` | Raw weekly interest scores, long format (`week`, `category`, `interest_score`), 7 categories × 5 years, US only |
| `food_categories_wide.csv` | `step1_2_correlation.py` | Reshaped to wide format — 262 weeks × 7 category columns |
| `food_categories_with_cluster.csv` | `step3_clustering.py` | Wide format + K-means `cluster` label per week |

**Categories**: `snack`, `dessert`, `drink`, `beverage`, `fast food`, `organic food`, `food delivery`

## Analysis

### 1–2. Data Reshaping + Correlation (`step1_2_correlation.py`)
Reshaped long-format data into wide format, then computed pairwise correlation across the 7 categories.
- `beverage`, `drink`, `snack`, `organic food` are strongly correlated (r = 0.71–0.85)
- `dessert` and `fast food` show moderate correlation (r = 0.57)
- `food delivery` is essentially uncorrelated with all other categories (r = -0.21 to 0.18)

*(`correlation_heatmap.png`)*

### 3. K-Means Clustering (`step3_clustering.py`)
Standardized all 7 categories (`StandardScaler`) before clustering, since raw scales differ widely (e.g. `food delivery` ~60–90 vs. `organic food` ~7–20). Optimal cluster count (k=2) selected by silhouette score.
- **Cluster 0** (227 weeks, "normal periods"): all categories at typical baseline levels
- **Cluster 1** (35 weeks, "unusually high-interest periods"): nearly all categories elevated simultaneously, *except* `food delivery`
- Re-tested an initial "April seasonality" hypothesis across the 5-year window; only `organic food` and `snack` showed a consistent April peak. `beverage` (May), `drink` (June), `fast food` (July), and `dessert` (November) each peaked in different months — the hypothesis was rejected. Cluster 1's structural cause remains unexplained within this analysis and would need external data (news, market events) to investigate further.

*(`cluster_timeline.png`)*

### 4. PCA (`step4_pca.py`)
PC1 (57.4%) + PC2 (16.7%) explain 74.1% of total variance.
- **PC1**: a general "food interest" axis with even contributions from `beverage`, `drink`, `snack`, `organic food`, `dessert`
- **PC2**: dominated almost entirely by `food delivery` (loading 0.83)
- Plotting K-means clusters on the PC1–PC2 plane visually confirmed Cluster 1 separating clearly along PC1

*(`pca_scatter.png`)*

**Interim conclusion**: Correlation, clustering, and PCA — three independent methods — all converge on the same finding: (1) four categories move together on one shared axis, and (2) `food delivery` moves entirely independently.

### 5. Random Forest + SHAP (`step5_rf_shap.py`)
Trained a Random Forest classifier to predict whether a given week belongs to Cluster 0 or Cluster 1, using the 7 category values as features.
- Accuracy: 97% (test set had only 9 Cluster-1 samples, so treat as directional, not conclusive)
- SHAP importance ranking: `drink` > `beverage` > `snack` > `organic food` > `fast food` > `dessert` > `food delivery`
- `food delivery` again shows the lowest importance (0.007), with SHAP values clustered near zero
- High `drink` and `beverage` values push predictions strongly toward "unusual period"

*(`shap_summary.png`)*

### 6. LIME Cross-Validation (`step5b_lime.py`)
Applied LIME — a different interpretability method (local linear approximation around each prediction, vs. SHAP's game-theoretic attribution) — to the same Random Forest model, to check whether an independently-computed importance ranking agrees with SHAP.

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
- Individual sample explanation: for one "normal period" week, `beverage`, `drink`, and `organic food` contributed most to the classification, while `food delivery`'s contribution was near zero

*(`shap_vs_lime_comparison.png`, `lime_example_explanation.png`)*

## Key Findings
- **Five independent methods — correlation, clustering, PCA, SHAP, and LIME — all converge on the same structural conclusion: `food delivery` moves independently of the other 6 food categories.** This consistency across methods with different underlying assumptions suggests a genuine structural pattern in the data, not a coincidence of any single technique.
- `beverage` and `drink` are the strongest and most consistent drivers of "unusual high-interest periods" across every method tested.
- An initial seasonality hypothesis (shared April peak) was tested and rejected — each category peaks in a different month, and Cluster 1's cause remains an open question for further investigation.

## Files
```
├── google_five_years.py               # Step 0: collect 5yr weekly interest via pytrends (US, 7 categories)
├── step1_2_correlation.py             # Steps 1-2: long -> wide reshape + correlation analysis
├── step3_clustering.py                # Step 3: K-means clustering
├── step4_pca.py                       # Step 4: PCA
├── step5_rf_shap.py                   # Step 5: Random Forest + SHAP
├── step5b_lime.py                     # Step 5b: LIME cross-validation
├── food_categories_5yr_trend_US.csv   # Raw long-format data
├── food_categories_wide.csv           # Wide-format data (262 weeks x 7 categories)
├── food_categories_with_cluster.csv   # Wide-format + cluster labels
├── correlation_heatmap.png
├── cluster_timeline.png
├── pca_scatter.png
├── shap_summary.png
├── shap_vs_lime_comparison.png
├── lime_example_explanation.png
└── README.md
```
