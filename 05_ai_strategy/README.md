# Stage 5: AI Strategy — MCP-Connected Automated Reporting

## Purpose
Connect Claude directly to the project's local data via MCP (Model Context Protocol), and use a Claude Project with fixed instructions so that re-running the same request against updated data always produces a report in the same structure — turning Stage 4's one-off RFM analysis into a repeatable reporting workflow.

## MCP Setup
- Installed Node.js and Claude Desktop
- Registered a `filesystem` MCP server in `claude_desktop_config.json`, scoped to the project folder (`/Users/.../Comento`)
- Verified the connection by asking Claude to list the folder's contents without any file upload — it correctly enumerated all Python scripts, CSV/DB files, and visualization outputs in the folder

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project/folder"]
    }
  }
}
```

## Claude Project: Fixed Report Template
Created a Claude Project with instructions that lock down:
- The analysis frame (keyword RFM, as defined in Stage 4) and its exact scoring/segmentation rules
- The report's fixed section order (data overview → segment summary → category×segment cross-analysis → notable changes → conclusions/monitoring suggestions)
- Output language and formatting conventions

## Reproducibility Issue Found and Fixed
Running the same request twice against the same dataset initially produced **different segment counts** (e.g. Core Trend: 12 vs. 13 keywords) between runs. The cause: the instructions specified tercile scoring but not how ties should be broken, so tie-handling was left to whatever order pandas happened to process rows in.

**Fix**: added an explicit tie-breaking rule to the Project instructions — `rank(method='first')`, based on original row order in the source CSV — so tercile boundaries are computed identically every time. Re-running after this fix reproduced the exact same segment counts and category breakdown as the first (manually verified) run, confirming the report is now deterministic given the same input data.

## Result
The Project can now be re-run with a single request ("이번 달 food_trends_merged.csv로 리포트 작성해줘") whenever the source CSV is updated, and will always return a report in the same 5-section structure with results directly traceable to the source data — no manual re-analysis or file upload required.

## Limitations & Next Steps
- Currently reasons only from the project's own collected data (Google Trends). Connecting external sources (news, market data) via additional MCP servers would let future reports explain *why* a keyword spiked, not just that it did.
- The "notable changes vs. previous report" section requires a prior report to compare against — not populated on a first run, but will activate from the second run onward.

## Files
```
├── claude_desktop_config.json.example   # MCP server config (path redacted)
├── project_instructions.md              # Fixed Claude Project instructions (frame, template, tie-breaking rule)
├── food_trend_rfm_report.md             # Example generated report
└── README.md
```
