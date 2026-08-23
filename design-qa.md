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

final result: passed
