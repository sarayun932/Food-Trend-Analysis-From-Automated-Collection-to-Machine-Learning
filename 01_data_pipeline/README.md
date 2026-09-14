# Stage 1: Automated Data Collection

## Purpose
Build a pipeline that discovers rising food/beverage search trends via the Google Trends API, filters out noise, stores results persistently, and runs on a daily schedule without manual intervention — the foundation dataset for Stages 2 and 3.

## Pipeline

```
[Google Trends] → [Collect] → [Filter] → [Store (SQLite + CSV)] → [Automate (cron)]
```

**1. Collect**
Uses `pytrends`' `related_queries()` to fetch rising search queries for six seed categories: `snack`, `dessert`, `drink`, `beverage`, `fast food`, `organic food`. Each request is independent, so a 429 (rate limit) error on one category doesn't block the others — a retry-with-backoff loop (up to 3 attempts, waiting 60s → 120s → 180s) handles temporary rate limiting without failing the whole run.

**2. Filter**
Removes irrelevant results (pet/animal-related terms that surface as false positives from the "food" category), drops rows below a minimum rising-interest threshold, and keeps only the top N results per category so no single category dominates the output.

**3. Store**
Each day's results are saved to a dated CSV (`food_trends_rising_YYYYMMDD.csv`) and appended to a SQLite database (`food_trends.db`) with a collection timestamp — giving both a daily snapshot and a queryable historical record.

**4. Automate**
Registered as a daily macOS `cron` job (`0 22 * * *`) to run unattended every night.

## Files
```
├── food_trend_pipeline.py         # Main collection script (collect → filter → store)
├── merge_all_trends.py            # Combines all dated CSVs into one long-format table
├── food_trends_rising_20260913.csv # Example single-day output
└── README.md
```

## Data Schema (per row)
| Column | Description |
|---|---|
| `query` | The rising search query discovered |
| `value` | Google Trends' relative rising-interest score |
| `seed` | Which of the 6 seed categories surfaced this query |
| `collected_at` | Timestamp of collection (SQLite table only) |

## Known Limitations
- **Local scheduling is not fully reliable.** Because the job runs via `cron` on a personal laptop rather than a cloud scheduler, collection was skipped on days the machine was asleep or powered off — visible as gaps in the collection date range (e.g., 2026-08-23, 08-25, 08-27, 08-29–30 are missing from the 16-day window this project ultimately covers). A cloud-based scheduler (e.g., GCP Cloud Scheduler) would remove this failure mode.
- **Google Trends' rising-interest score is relative, not absolute.** A single request's scores are only comparable to each other, not to scores from a different request — which is why merging multiple days' CSVs requires care (handled in `merge_all_trends.py` by keeping each day's rows distinct with a `collected_date` tag, rather than treating scores as directly additive across days).
- Automation was manually stopped (`crontab -r`) once sufficient data had been collected for this project; it is not intended to run indefinitely.
