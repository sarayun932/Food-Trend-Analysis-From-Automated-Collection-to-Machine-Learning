# Stage 2b: Visualization Analysis

## Purpose
Re-examine the same keyword-level data from Stage 1 (5-day automated collection) through Power BI, going beyond simple category counts to ask: do categories with similar collection *counts* also show similar *interest intensity*? And separately, is "how often a category appears" the same thing as "how stable it is day to day"?

## Data
Same dataset as `01_data_pipeline` / `02_dashboard`: keyword-level rising search data (`query`, `category`, `trend_score`), 111 records across 5 collection days (2026-08-20 to 2026-08-26, with gaps).

## Analysis

### Insight 1 — Interest is polarized across categories, centered on recurring outliers

**Background**: The Stage 2 dashboard showed simple record counts per category, but couldn't answer whether similar counts meant similar interest *intensity*. A bubble chart (avg `trend_score` on X, max on Y, bubble size = record count) was built to separate "consistently high" categories from "occasionally spiking" ones.

![Dashboard: bubble chart, category share, and daily record count table](dashboard_full.png)

| Category | Avg | Max | Count |
|---|---|---|---|
| beverage | *(확인 필요)* | *(확인 필요)* | 67 |
| snack | *(확인 필요)* | *(확인 필요)* | 77 |
| dessert | *(확인 필요)* | *(확인 필요)* | 78 |
| fast food | *(확인 필요)* | *(확인 필요)* | 32 |
| organic food | *(확인 필요)* | *(확인 필요)* | 54 |
| drink | *(확인 필요)* | *(확인 필요)* | 56 |

> ⚠️ Counts above reflect the full 364-record dataset. Average/max `trend_score` values are from an earlier 111-record snapshot and need to be re-pulled from the updated dashboard to stay accurate.

- **Polarization into two groups**: `beverage` and `snack` separated clearly in the upper-right of the scatter plot; the other four clustered lower-left. *(급상승 지표 비중 — 40.5%/72.8% 수치도 364건 기준으로 재계산 필요)*
- **Coefficient of variation (CV) reveals different volatility**: *(재계산 필요 — 아래는 111건 기준 참고용 수치)* `beverage` (117.8%) and `fast food` (101.8%) previously had unusually high CV; `drink` (37.7%) and `organic food` (43.5%) had low CV.
- **Outlier detail**: *(재계산 필요)* Using the IQR outlier threshold, 7 of 111 records previously qualified as outliers — all from `beverage` and `snack`. Needs to be re-run against the 364-record dataset. One recurring outlier keyword worth re-checking: `silk beverage listeria settlement`.

**Implication**: Categories shouldn't be treated as equivalent. High-volatility categories (`beverage`, `snack`) are more likely to produce sudden spikes and warrant real-time monitoring priority; low-volatility categories (`drink`, `organic food`) can be treated as a more stable background signal.

### Insight 2 — "Frequent" categories and "stable" categories are not the same thing

**Background**: Insight 1 looked at interest *intensity*. This insight looks at *frequency* (share of records) and *day-to-day stability*, using a pie chart and a category × date pivot table.

**Category share (by record count)**

| Category | Share |
|---|---|
| beverage | 20.7% |
| dessert | 20.7% |
| snack | 19.8% |
| drink | 13.5% |
| fast food | 12.6% |
| organic food | 12.6% |

- **Share vs. intensity mismatch**: By count, `beverage` and `dessert` tie for 1st (20.7% each). But by intensity (Insight 1), the ranking was `beverage` > `snack` > `dessert`. `dessert` appears often but rarely spikes hard; `snack` appears less often but spikes harder when it does. **Frequency and intensity are separate axes — reading only one can mislead.**
- **Daily stability**: *(재계산 필요 — 아래는 8/20~8/26 5일 기준 참고용, 새 대시보드는 날짜 범위가 다름)* `beverage` previously had the smallest daily range (steady 4–5/day), while `drink` had the largest (2→2→5→2→4).

**Implication**: Combining frequency, intensity, and stability gives a clearer category profile. `beverage` scores high on all three — the priority category for monitoring. `dessert` is high-frequency but low-intensity — a steady background category. `drink` is low-frequency and unstable — reactive to one-off spikes only.

## Key Findings
- Category-level metrics that look similar on the surface (record counts) can hide very different underlying patterns in intensity, volatility, and stability.
- `beverage` and `snack` are structurally different from the other four categories — not just "higher on average" but disproportionately driving total interest volume and recurring outliers.
- A single metric (count, average, or share) is not enough to characterize a category; at least three axes (frequency, intensity, stability) are needed.

## Files
```
├── dashboard_full.png             # Power BI dashboard: bubble chart, pie chart, daily table
└── README.md
```
