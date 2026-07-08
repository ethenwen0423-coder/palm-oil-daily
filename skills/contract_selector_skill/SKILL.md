---
name: contract-selector-skill
description: Select the current main and secondary contracts before oil-futures tab analysis. Use before master_analytic_skill or technical_basic_analysis_skill whenever updating data/oil_futures.js or preparing contract-level market inputs. This skill is the required first step and delegates liquidity discovery to contract_discovery_skill.
---

# Skill: contract_selector_skill

## Purpose

`contract_selector_skill` is the required first step before oil-futures contract analysis.

It selects:

- rank 1 main contracts
- rank 2 secondary contracts
- the saved current-month contract universe

It does not perform scoring, report writing, or trading analysis.

## Required Order

When updating the oil-futures tab or preparing report contract inputs:

1. Call `contract_selector_skill`.
2. Run `skills/contract_selector_skill/scripts/select_contracts.py`.
3. Read `data/contracts/current_contracts.json`.
4. Send every rank 1 and rank 2 contract into downstream analysis.
5. Then call `master_analytic_skill` and `technical_basic_analysis_skill`.

Do not analyze only rank 1.

## Entrypoint

```bash
python3 skills/contract_selector_skill/scripts/select_contracts.py
```

The selector delegates the actual liquidity discovery to:

```bash
python3 skills/contract_discovery_skill/scripts/select_contracts.py
```

