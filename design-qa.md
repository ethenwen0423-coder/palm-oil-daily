# Design QA — 首页四个研究入口一致性

**Evidence**

- Source visual truth: `/var/folders/xx/r68yfq7n04n256vjslj6z3r00000gn/T/TemporaryItems/NSIRD_screencaptureui_Bf0OR9/截屏2026-08-23 14.38.55.png`
- Browser-rendered implementation: `/tmp/palm-nav-highlight.dhPInY/home-entry-unified-full.jpg`
- Focused side-by-side comparison: `/tmp/palm-nav-highlight.dhPInY/home-entry-unified-comparison.jpg`
- Browser viewport: 1280 × 720 CSS px, device scale factor 1.
- Source pixels: 738 × 516. Implementation full-view pixels: 1280 × 720. Focus crop: 343 × 500, proportionally fitted without distortion onto a 738 × 516 comparison canvas.
- State: desktop, default; four entry links visible after report data loaded.

**Findings**

- No actionable P0, P1, or P2 findings remain.
- Fonts and typography: all four entries now share the same type family, size, weight, line height, and alignment.
- Spacing and layout rhythm: all four entries use one height, padding, radius, border, and icon slot; vertical gaps are consistent.
- Colors and visual tokens: all four entries use the same subtle filled background, foreground, and border tokens. Hover and focus use one shared emphasis state.
- Image quality and asset fidelity: each entry uses the same 24 px Iconoir `arrow-right` source asset rendered at 20 px; no mixed arrow glyphs remain.
- Copy and content: the four labels and destinations are unchanged.
- Accessibility: decorative arrow images use empty alt text; link names remain the visible Chinese labels.

**Comparison History**

1. Earlier P2: the first two links used a transparent option style and diagonal arrow, while the last two used a filled secondary style and horizontal arrow.
2. Fix: removed the two variant classes, applied one shared `.hero-button` treatment, and replaced all four glyphs with the same Iconoir arrow-right asset.
3. Post-fix evidence: focused comparison shows equal default fills, borders, padding, and arrows across all four links. Static checks found four links and four identical icon assets.

**Interaction Verification**

- Open 24h assistant → `/assistant.html`.
- Read today’s morning report → `/report.html?id=2026-08-03`.
- View this week’s report → `/report.html?id=2026-08-02-weekend`.
- OTC structuring suggestion → `/otc-structure.html`.
- Browser console errors: 0.

**Implementation Checklist**

- [x] One shared default background and border.
- [x] One shared hover, focus, and active state.
- [x] One arrow direction and icon asset.
- [x] Four destinations tested in the browser.
- [x] Focused visual comparison completed.

**Follow-up Polish**

- None required for this scope.

---

# Design QA — AI敢死队决策模式下拉框

**Evidence**

- Issue capture: `/var/folders/xx/r68yfq7n04n256vjslj6z3r00000gn/T/TemporaryItems/NSIRD_screencaptureui_ZO8s0h/截屏2026-08-30 23.00.41.png`
- Browser-rendered implementation: `/Users/ethen/Sites/palm-oil-daily/design-qa-ai-daredevil-select.png`
- Focused implementation: `/Users/ethen/Sites/palm-oil-daily/design-qa-ai-daredevil-select-focus.png`
- Side-by-side comparison: `/Users/ethen/Sites/palm-oil-daily/design-qa-ai-daredevil-select-comparison.png`
- Viewport: 1280 × 720 CSS px, device scale factor 1; state: `纯AI决策` selected.

**Findings**

- No actionable P0, P1, or P2 differences remain for the reported component.
- Typography and spacing preserve the existing component rules: 15 px/700 value text, 360 px desktop width, and 46 px control height.
- The white native surface is replaced by the site panel color, existing green gradient and border, with a dark explicit fallback for browser differences.
- The native disclosure indicator, copy, keyboard focus styling, and strategy switching behavior are preserved.

**Comparison History**

1. Initial P1: the issue capture showed a white select that broke the dark site theme. P2: the stylesheet URL had no release version, allowing stale CSS to persist.
2. Fix: added an explicit dark background and text fill while preserving the existing gradient and native arrow; versioned the stylesheet URL.
3. Post-fix: computed styles show `rgb(11, 27, 22)`, a green border, white text, square corners, and working switching between both strategies.

final result: passed

---

# Design QA — AI敢死队交易卡片溢出与内部字段

**Evidence**

- Source visual truth: `/var/folders/xx/r68yfq7n04n256vjslj6z3r00000gn/T/TemporaryItems/NSIRD_screencaptureui_xInE1b/截屏2026-09-02 21.15.02.png`
- Browser-rendered implementation: `/tmp/ai-daredevil-cards-fixed-974x486.png`
- Side-by-side comparison: `/tmp/ai-daredevil-cards-comparison.png`
- Viewport: 974 × 486 CSS px, device scale factor 1 for implementation. The 1948 × 972 Retina source was normalized to 974 × 486 without distortion.
- State: desktop, `纯AI决策` selected, 6 条今日动作、40 条下一步指令、0 条未执行信号，使用同一批线上数据。

**Findings**

- No actionable P0, P1, or P2 findings remain.
- Fonts and typography: headings, timestamps, strategy copy, realized P&L, and confidence keep the existing type scale and weights; long text wraps at Chinese and identifier boundaries without clipping.
- Spacing and layout rhythm: all three panels stay inside the 3-column grid. Each activity record now uses a contained top summary row followed by vertically flowing detail copy.
- Colors and visual tokens: existing dark panel, muted copy, green strategy text, and red/green Chinese-market P&L semantics are unchanged.
- Image quality and asset fidelity: this component contains no raster or icon assets; no source asset was replaced or approximated.
- Copy and content: internal keys such as `INPUT.local_strategy_backtests`, `current_bias`, `EXIT_LONG`, and `trend_vs_ma60` are converted to readable Chinese labels while preserving strategy name, return, rules, action, date, confidence, and realized P&L.
- Accessibility and responsiveness: the information order remains semantic in the DOM, both strategy modes switch successfully, and the browser console reports no warnings or errors.

**Comparison History**

1. Earlier P1: long strategy text forced the trailing amount or confidence column outside its panel, leaving isolated numbers across the gap between cards.
2. Earlier P2: raw backend identifiers and missing decision dates appeared as garbled or implementation-facing copy.
3. Fix: replaced the three-track activity row with a contained summary header plus vertical detail flow; added width and overflow guards; translated known strategy/action fields; used the backtest close date when a decision has no independent timestamp.
4. Post-fix evidence: the normalized side-by-side comparison shows all three cards contained in the viewport, no isolated numbers between panels, and readable strategy labels. Both mode switches pass and browser console errors are 0.

**Implementation Checklist**

- [x] Keep realized P&L and confidence inside each record header.
- [x] Prevent long strategy/rule text from expanding grid tracks.
- [x] Replace backend identifiers with reader-facing Chinese labels.
- [x] Preserve all strategy, action, return, time, and P&L facts.
- [x] Verify both decision modes and console state in the browser.

**Follow-up Polish**

- None required for this scope.

final result: passed
