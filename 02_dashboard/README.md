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
- KPI scorecards — total records (364), unique keywords (68)
- Category distribution bar chart (collection count by category)
- Keyword ranking table (sorted by trend_score, all 68 keywords)
- Category group bar chart — categories split into "high-interest" (`beverage`, `snack`) vs. "low-interest" (the remaining four), using a calculated field (`category_group`)
- Bubble scatter — unique keyword count vs. total record count per category, colored by category
- Daily collection trend, as both a line chart and stacked bar charts (absolute count and percentage share), all sorted chronologically by a calculated date field (`CollectedDate`, parsed from the raw `YYYYMMDD` text column)
- Category filter control with cross-filtering enabled across all charts

<img width="847" height="725" alt="image" src="https://github.com/user-attachments/assets/a24ab7e3-9a7f-46c3-82de-bd25934f7a71" />
<img width="857" height="224" alt="image" src="https://github.com/user-attachments/assets/77809796-a1b5-4d2b-910d-be2d5771d593" />
<img width="852" height="694" alt="image" src="https://github.com/user-attachments/assets/5f46b102-d811-44be-9f29-688fd5689e9a" />


## Key Observations
- **69.1% of keywords (47 of 68) appeared on 2 or more separate collection days** — evidence that most of what's captured is a recurring signal rather than one-off noise.
- Two keywords — `wellhealthorganic organic food benefits` and `portillo's dr pepper dessert` — appeared on **every single collection day (16/16)**, making them the most consistently persistent trends in the dataset.
- `silk beverage listeria settlement` appeared on 14 of 16 days and recorded the highest single-day score in the dataset (25,950), suggesting a food-safety story with unusually sustained attention.
- The category-group split shows `beverage` and `snack` consistently outweighing the other four categories in both keyword count and collection volume, day after day — visible in the stacked daily trend charts, not just in a single-day snapshot.

## Files
```
├── food_trends_merged.csv     # Combined daily data, 16 days
├── dashboard_screenshot.png   # Looker Studio dashboard export
└── README.md
```
