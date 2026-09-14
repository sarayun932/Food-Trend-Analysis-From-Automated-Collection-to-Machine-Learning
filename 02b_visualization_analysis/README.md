# Stage 2b: Visualization Analysis

## Purpose
Re-examine the same keyword-level data from Stage 1 (automated daily collection) through Looker Studio, going beyond simple category counts to ask: do categories with similar collection *counts* also show similar *interest intensity*? And separately, is "how often a category appears" the same thing as "how stable it is day to day"?

## Data
Same dataset as `01_data_pipeline` / `02_dashboard`: keyword-level rising search data (`query`, `category`, `trend_score`), 364 records across 16 collection days (2026-08-19 to 2026-09-13, with a few gaps).

## Analysis

### Insight 1 — Interest is polarized across categories, centered on recurring outliers

**Background**: The Stage 2 dashboard showed simple record counts per category, but couldn't answer whether similar counts meant similar interest *intensity*. A bubble chart (avg `trend_score` on X, max on Y, bubble size = record count) was built to separate "consistently high" categories from "occasionally spiking" ones.

![Dashboard: bubble chart, category share, and daily record count table](dashboard_full.png)

| Category | Avg | Max | Count |
|---|---|---|---|
| snack | 7,268 | 17,350 | 77 |
| beverage | 7,169 | 25,950 | 67 |
| dessert | 3,741 | 9,100 | 78 |
| fast food | 1,038 | 5,250 | 32 |
| organic food | 921 | 4,950 | 54 |
| drink | 898 | 1,700 | 56 |

- **Polarization into two groups**: `beverage` and `snack` separated clearly in the upper-right of the scatter plot; the other four clustered lower-left. Splitting into a `category_group` field (high-interest = beverage+snack, low-interest = the rest): the high-interest group is 39.6% of records (144 of 364) but accounts for **71.0% of total trend-score volume**.
- **Coefficient of variation (CV) reveals different volatility**: `fast food` (126.4%) and `beverage` (123.0%) have the highest CV, meaning their averages are heavily skewed by single extreme outliers. `drink` (47.8%) and `dessert` (62.2%) have the lowest CV — consistently low-to-moderate interest with fewer extreme spikes. (`snack` 63.4%, `organic food` 78.7% fall in between.)
- **Outlier detail**: Using the IQR outlier threshold (10,875), 30 of 364 records (8.2%) qualified as outliers — **all 30 came from only `beverage` (14) and `snack` (16)**. Three keywords account for nearly all of them, and each recurred across most of the 16 collection days rather than spiking once and disappearing:
  - `silk beverage listeria settlement` — outlier on **all 14 days** it appeared (out of 16 total collection days)
  - `aldi game day snack container` — outlier on 11 of the 12 days it appeared
  - `prince louis favorite snack` — outlier on 5 of the 6 days it appeared

  This pattern — the same handful of keywords repeatedly crossing the outlier threshold over weeks, not a single spike — suggests sustained real-world attention (e.g. an ongoing food-safety story) rather than noise.

**Implication**: Categories shouldn't be treated as equivalent. High-volatility categories (`fast food`, `beverage`) are more likely to produce sudden spikes, and `beverage`/`snack` together drive the outlier count entirely — both warrant real-time monitoring priority. Low-volatility categories (`drink`, `dessert`) can be treated as a more stable background signal.

### Insight 2 — "Frequent" categories and "stable" categories are not the same thing

**Background**: Insight 1 looked at interest *intensity*. This insight looks at *frequency* (share of records) and *day-to-day stability*, using a pie chart and a category × date pivot table.

**Category share (by record count)**

| Category | Share |
|---|---|
| dessert | 21.4% |
| snack | 21.2% |
| beverage | 18.4% |
| drink | 15.4% |
| organic food | 14.8% |
| fast food | 8.8% |

- **Share vs. intensity mismatch**: By count, `dessert` and `snack` rank highest (21.4%, 21.2%). But by intensity (Insight 1), the ranking is `snack` > `beverage` > `dessert` — `beverage` outranks `dessert` on intensity despite appearing less often (18.4% share). `dessert` appears often but rarely spikes hard; `beverage` appears somewhat less often but spikes much harder when it does. **Frequency and intensity are separate axes — reading only one can mislead.**
- **Daily stability**: Across the full 16-day collection window, `drink` and `fast food` show the widest daily swings (range of 3: e.g. `fast food` runs from 1 to 4 records/day), while `beverage`, `dessert`, `snack`, and `organic food` are comparatively steadier (range of 2 each). `fast food` in particular combines low frequency, low intensity, *and* the least stability of any category.

**Implication**: Combining frequency, intensity, and stability gives a clearer category profile. `snack` and `beverage` score high on intensity and reasonably on stability, making them the priority categories for monitoring — `beverage` in particular combines high intensity with the widest outlier footprint. `dessert` is high-frequency but comparatively low-intensity — a steady background category. `fast food` is low-frequency, low-intensity, *and* the least stable — a category that only matters in short-lived spikes.

## Key Findings
- Category-level metrics that look similar on the surface (record counts) can hide very different underlying patterns in intensity, volatility, and stability.
- `beverage` and `snack` are structurally different from the other four categories — not just "higher on average" but disproportionately driving total interest volume and recurring outliers.
- A single metric (count, average, or share) is not enough to characterize a category; at least three axes (frequency, intensity, stability) are needed.

## Files
```
├── dashboard_full.png             # Looker Studio dashboard: bubble chart, pie chart, daily table
├── food_trends_merged.csv         # Source data (same as 01_data_pipeline / 02_dashboard)
└── README.md
```
