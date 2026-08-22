# Design QA — 首页研究模块三列布局

- Source visual truth: `/var/folders/xx/r68yfq7n04n256vjslj6z3r00000gn/T/TemporaryItems/NSIRD_screencaptureui_3zFoMz/截屏2026-08-22 22.25.23.png`
- Implementation screenshot: `/tmp/palm-contract-production.haXhmN/output/playwright/research-modules-three-column.png`
- Combined comparison: `/tmp/palm-contract-production.haXhmN/output/playwright/research-modules-comparison.png`
- Source pixels: 2672 × 820
- Browser viewport: 1280 × 820 CSS px for final desktop inspection; 390 × 844 CSS px for responsive inspection
- Browser full-page capture: 1280 × 1968 pixels
- Compared region: `.research-entries`; source and implementation normalized to 564 px width in the combined comparison
- State: 首页默认态，三张研究入口卡片，无悬停

## Full-view comparison evidence

The supplied source shows three populated cards followed by two empty grid tracks. The revised implementation keeps the same header, typography, colors, borders, copy, and card order while distributing the three cards across the full available width. Computed desktop tracks are three equal 374.133 px columns at the 1280 px browser viewport, and document scroll width equals viewport width.

## Focused region comparison evidence

The combined comparison isolates the research-module region. It confirms that the blank right-hand area is removed and the three card boundaries now terminate at the section's right border. No new imagery, icons, or assets were introduced. A separate focused mobile measurement confirms one 364 px column at a 390 px viewport with no horizontal overflow.

## Required fidelity surfaces

- Fonts and typography: unchanged from the source implementation; weights, hierarchy, line height, labels, and wrapping remain consistent.
- Spacing and layout rhythm: three equal desktop tracks now fill the section; existing card padding and section rhythm are preserved. Mobile uses one column.
- Colors and visual tokens: unchanged dark-green panel, green labels, muted body copy, and hairline borders.
- Image quality and asset fidelity: this section contains no raster imagery or custom icons; no asset substitutions were made.
- Copy and content: all three titles, descriptions, numbering, CTAs, and the section note are unchanged.

## Comparison history

1. Initial finding — P1: `.research-entry-grid` declared five columns for only three cards, producing two visually empty tracks on the right.
   - Fix: changed the desktop grid to `repeat(3, minmax(0, 1fr))`.
   - Post-fix evidence: three equal desktop tracks fill the section in `research-modules-comparison.png`.
2. Initial finding — P2: a later `max-width: 1050px` rule overrode the earlier phone layout, leaving three 120.66 px columns at 390 px.
   - Fix: added a final `max-width: 700px` one-column rule.
   - Post-fix evidence: three cards measure 364 px each in a single column; `scrollWidth` equals 390 px.

## Findings

No actionable P0, P1, or P2 differences remain for the requested change. Browser console errors: 0.

## Implementation checklist

- [x] Remove the two unused desktop grid tracks.
- [x] Preserve existing card content and interaction styling.
- [x] Restore a single-column phone layout.
- [x] Verify no horizontal overflow.
- [x] Check browser console errors.

## Follow-up polish

No P3 follow-up is required for this scoped change.

final result: passed
