# Stage 4: Frame-Based Analysis — Keyword RFM

## Purpose
Apply a validated analytical framework (RFM) to the keyword-level dataset to move beyond ad-hoc visual exploration (Stage 2b) toward a structured, repeatable segmentation — and to explicitly define problems and monitoring priorities rather than just describing patterns.

## Framework: RFM, Adapted for Keywords
Standard RFM segments customers by Recency, Frequency, and Monetary value. This dataset has no customer concept, so keywords are treated as the segmented entity instead:

- **R (Recency)**: days since the keyword last appeared, relative to the most recent collection date
- **F (Frequency)**: number of distinct collection days (of 16) the keyword appeared on
- **M (Magnitude)**: average `trend_score` on the days it appeared (standing in for "Monetary")

## Method
1. Computed R/F/M per keyword (68 total) from `food_trends_merged.csv`
2. Scored each metric into terciles (3/2/1) using rank-based splitting
3. **Tie-breaking rule (critical for reproducibility)**: ties are broken by `rank(method='first')`, i.e. original row order in the source CSV — without this, re-running the same segmentation on the same data produced different segment counts between runs (see Stage 5 for how this was caught and fixed)
4. Classified keywords into 5 segments based on R/F/M combinations:

| Segment | Rule |
|---|---|
| 핵심 트렌드 (Core Trend) | R=3, F=3, M≥2 |
| 급상승 신규 (Emerging) | R=3, F≤2, M=3 |
| 휴면 (Dormant, previously recurring) | R≤1, F≥2 |
| 단발성 소멸 (One-off, faded) | R≤1, F≤1 |
| 일반 유지 (Steady/Other) | everything else |

## Results

**Segment distribution (68 keywords)**

| Segment | Count | Share |
|---|---|---|
| 핵심 트렌드 | 12 | 17.6% |
| 급상승 신규 | 2 | 2.9% |
| 휴면(과거 반복) | 12 | 17.6% |
| 단발성 소멸 | 11 | 16.2% |
| 일반 유지 | 31 | 45.6% |

**Core Trend share by category**

| Category | Total keywords | Core Trend | Share |
|---|---|---|---|
| organic food | 5 | 2 | 40.0% |
| dessert | 13 | 4 | 30.8% |
| snack | 15 | 3 | 20.0% |
| beverage | 15 | 2 | 13.3% |
| drink | 13 | 1 | 7.7% |
| fast food | 7 | 0 | 0.0% |

## Key Findings
- **Raw volume and Core Trend conversion rate point in different directions.** `beverage` and `snack` lead on total record count (Stage 2b/3 findings), but `organic food` and `dessert` convert a much higher *share* of their keywords into sustained Core Trends (40.0% and 30.8% vs. 13.3% and 20.0%). Volume alone overstates beverage/snack's structural importance.
- **`fast food` produces zero Core Trend keywords.** Of the 6 categories, it's the only one with no persistent, recent, high-magnitude keyword — suggesting either genuinely low trend-forming power in this category, or that current seed keywords aren't capturing its real trend signal.
- **F–M mismatch keywords (low frequency, very high magnitude)** — e.g. `universal theme parks snack restrictions` (F=1, M=7,650) — are one-off large-magnitude spikes that a frequency-only view would miss entirely. These are exactly the kind of keyword a "share of records" metric (Stage 2b) undercounts.

## Problem Definition & Direction
Categories should not be monitored uniformly. `beverage`/`snack` carry high total volume but a meaningful share of that volume is driven by occasional large spikes (F–M mismatches) rather than sustained trends — they warrant spike-detection monitoring. `organic food`/`dessert` show a disproportionately high rate of turning into durable Core Trends despite lower volume — they warrant continuous trend tracking. `fast food`'s zero Core Trend rate is a signal to revisit either the category's real dynamics or the keyword collection seeds themselves.

## Files
```
├── rfm_analysis.py            # R/F/M computation, tercile scoring, segmentation
├── rfm_result.csv             # Full 68-keyword RFM table with scores and segments
├── rfm_segment_counts.png     # Segment distribution chart
├── rfm_segment_revenue.png    # Category x segment breakdown chart
└── README.md
```
