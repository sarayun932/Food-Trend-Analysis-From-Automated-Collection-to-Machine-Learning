# Stage 2: Interactive Dashboard

## Purpose
Consolidate the daily CSV outputs from Stage 1 into a single dataset, then build an interactive Looker Studio dashboard to make the underlying patterns explorable — KPI summaries, category breakdowns, a time trend, and cross-filtering — rather than static numbers in a spreadsheet.

## Data
`food_trends_merged.csv` combines every daily collection run into one long-format table:

| Column | Description |
|---|---|
| `id` | Row identifier |
| `collected_date` | Date the row was collected (YYYYMMDD) |
| `keyword` | The rising search query |
| `category` | Seed category used to discover it (snack, dessert, drink, beverage, fast food, organic food) |
| `trend_score` | Google Trends' relative rising-interest score |

**Coverage**: 16 collection days (2026-08-19 to 2026-09-13, with a few days missed due to the local scheduler being offline), 364 rows, 68 unique keywords.

## Dashboard
Built in Looker Studio, connected via CSV upload, with:
- KPI scorecards (total records, unique keywords)
- Category distribution bar chart
- Time trend line chart
- Keyword ranking table
- Category filter control with cross-filtering enabled across all charts

[대시보드 캡처 이미지 (dashboard_screenshot.png)]

## Key Observations
- **69.1% of keywords (47 of 68) appeared on 2 or more separate collection days** — evidence that most of what's captured is a recurring signal rather than one-off noise.
- Two keywords — `wellhealthorganic organic food benefits` and `portillo's dr pepper dessert` — appeared on **every single collection day (16/16)**, making them the most consistently persistent trends in the dataset.
- `silk beverage listeria settlement` appeared on 14 of 16 days and recorded the highest single-day score in the dataset (25,950), suggesting a food-safety story with unusually sustained attention.

## Files
```
├── food_trends_merged.csv     # Combined daily data, 16 days
├── dashboard_screenshot.png   # Looker Studio dashboard export
└── README.md
```
