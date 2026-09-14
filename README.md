# Food Trend Analysis: From Automated Collection to Machine Learning

## Overview
This project tracks food and beverage search trends over time, using Google Trends as a proxy for consumer interest. It was built in three progressive stages — each adding a new layer of analytical depth on top of the same core dataset — moving from raw data collection, to visualization, to statistical/ML-based pattern discovery.

The guiding question throughout: **what can search behavior tell us about emerging consumer trends in the food industry, and how much of what we see is a real signal versus noise?**

## Project Stages

### [`01_data_pipeline/`](./01_data_pipeline) — Automated Data Collection
Built a Python pipeline using the `pytrends` API to collect rising search queries across six food/beverage categories (snack, dessert, drink, beverage, fast food, organic food), with automatic filtering, SQLite storage, and daily scheduling via cron. Designed to distinguish genuine multi-day trends from single-day noise.

### [`02_dashboard/`](./02_dashboard) — Interactive Visualization
Consolidated the collected data into a Looker Studio dashboard with KPI cards, category breakdowns, a time trend chart, and cross-filtering controls, to make the underlying patterns explorable rather than static.

### [`03_ml_analysis/`](./03_ml_analysis) — Statistical & ML-Based Pattern Discovery
Collected a complementary 5-year weekly time series (via `pytrends`' `interest_over_time`) for the same seven categories, then applied correlation analysis, K-means clustering, PCA, and two independent model-interpretation methods (SHAP, LIME) to uncover structure that wasn't visible from the dashboard alone.

## Key Findings

- **Category interest clusters into two independent groups.** Correlation, clustering, PCA, SHAP, and LIME — five methods with entirely different underlying logic — all converged on the same conclusion: `food delivery` moves independently of the other six categories, while `beverage`, `drink`, `snack`, and `organic food` move together.
- **An algorithm-discovered structure outperformed a human hypothesis.** An initial assumption that categories peak together every April (seasonal) didn't hold up under 3–5 years of data — only `organic food` and `snack` showed a genuine recurring spring peak. Instead, K-means independently surfaced a different pattern: a distinct "elevated interest" period concentrated in late 2025–2026, unrelated to any single calendar month.
- **`food delivery` tells its own story.** Rather than a seasonal pattern, it shows a multi-year structural swing — peaking during 2021 (pandemic-era demand), declining through 2024, and recovering into 2025–2026 — a trend visible only because a longer time series was collected specifically for this purpose.

## Tech Stack
Python (`pytrends`, `pandas`, `scikit-learn`, `shap`, `lime`, `matplotlib`, `seaborn`) · SQLite · macOS `cron` · Looker Studio

## Repository Structure
```
food-trend-analysis/
├── 01_data_pipeline/     # Collection, filtering, automation
├── 02_dashboard/         # Looker Studio dashboard source data + screenshots
├── 03_ml_analysis/       # Correlation, clustering, PCA, SHAP, LIME
└── reports/              # Written summary report (Word)
```
Each stage folder has its own README with implementation detail and results specific to that step.

## Limitations
- Google Trends' relative (0–100) scoring means values are only comparable within a single request — combining data collected across separate runs required care to avoid misinterpreting scale shifts as real changes.
- The automation pipeline (Stage 1) occasionally missed a scheduled run when the local machine was asleep, illustrating a real constraint of local `cron`-based scheduling versus cloud-based schedulers.
- The root cause of the "elevated interest period" found in Stage 3 was not identified within the scope of this analysis and would require external data (news, market events) to explain.
