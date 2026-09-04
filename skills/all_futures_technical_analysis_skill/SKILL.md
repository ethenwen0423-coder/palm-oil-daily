---
name: all_futures_technical_analysis_skill
description: Analyze the exact futures contract selected by a website user with completed daily bars, technical indicators, support/resistance, and an explicit no-standalone-direction rule.
---

# All-futures technical analysis skill

Use this skill only after the user selects a concrete published `PYYMM` futures
contract. Pass that exact symbol's daily OHLC history and latest verified price
to `scripts/analyze.py`.

The skill calculates MA20/MA60, MACD, RSI14, KDJ, Bollinger bands, ATR14 and
20-day support/resistance. It describes technical state but must not independently
decide the final bullish or bearish view. If fewer than 60 valid bars are
available, return `insufficient` and no directional judgement.

