---
name: all_futures_fundamental_analysis_skill
description: Build a selected futures contract's fundamental view from current verifiable evidence and a labeled published snapshot without inventing missing facts.
---

# All-futures fundamental analysis skill

Use this skill after a user selects a concrete futures contract. Give it the
selected contract's published fundamental snapshot plus evidence fetched for
that exact variety, such as registered warrants or an index spot/basis reading.

Current numeric evidence must appear before research-framework text. Preserve
the source date. When no new evidence is available, label the snapshot and
return `missing`; never turn a generic supply-demand checklist into a current
fundamental conclusion.

