---
name: htfc-tianji-router
description: Route read-only HTFC Tianji market-news, smart-Kline, research-report, and trend-compass collection for the palm-oil site.
---

# HTFC Tianji router

Use `scripts/update_htfc_tianji_data.py` to refresh `data/htfc_tianji.json`.

- Route news to `/bus/info` and `/bus/info/filter`.
- Route market interpretation to the smart-Kline label tree and K-line endpoints.
- Route research to report category/list endpoints.
- Route trend evidence to the exchange-futures mapping and trend endpoints.
- Resolve Chinese product names to a unique API code before detail calls. Return candidates when mapping is not unique; never guess.
- Preserve upstream fields and module errors. A restricted module degrades independently.
- Read-only by default. Do not call preference, notification, subscription, ranking-save, or other write endpoints.
- Require `HTFC_BASE_URL` and `HTFC_API_KEY`; never print or persist the key.
