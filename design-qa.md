# 24h 盯盘助手导航高亮与品牌修复 QA

## Evidence

- Source visual truth: `/var/folders/xx/r68yfq7n04n256vjslj6z3r00000gn/T/codex-clipboard-57c0fc4b-348a-4d08-92ee-df40ee6a1703.png`
- Browser-rendered implementation: `/tmp/palm-nav-highlight.dhPInY/nav-highlight-final.png`
- Focused same-size comparison: `/tmp/palm-nav-highlight.dhPInY/nav-highlight-final-comparison.png`
- Browser viewport: 1280 × 720 CSS px, device scale factor 1
- Source pixels: 374 × 578
- Implementation full-view pixels: 1280 × 720
- Implementation comparison crop: 374 × 578 from viewport origin (0, 0)
- Density normalization: both focused regions compared at 374 × 578 physical pixels; no scaling applied
- State: page top, `盯盘总览` current, pointer hovering `油脂主力`

## Full-view comparison evidence

- The assistant layout, dark green palette, left navigation placement, content density, borders, and typography hierarchy remain consistent with the existing Signal Grid design.
- Only the intended navigation/brand region changed; market cards, research content, filters, and action controls did not move.
- The left rail now begins below the 68 px header and extends to the viewport bottom instead of overlapping the header.

## Focused region comparison evidence

- The source screenshot shows `盯盘总览` and hovered `油脂主力` with the same active treatment. The final capture keeps the green rail and stronger panel fill only on `盯盘总览`; `油脂主力` receives a lower-contrast hover fill without an active rail.
- `Vinson Research` and `24h 盯盘助手` are fully visible in the final focused comparison. Computed brand bounds are inside the header, and casing is no longer forced to uppercase.

## Findings

- No actionable P0/P1/P2 findings remain.
- Fonts and typography: passed. Brand uses a standard system Latin stack at 700/15 px, normal casing, 0.01 em spacing, and does not wrap or clip.
- Spacing and layout rhythm: passed. Sidebar geometry is top 68 px, height 652 px at the 1280 × 720 viewport; active and hover states retain existing padding and radii.
- Colors and visual tokens: passed. Current state uses the existing `--green` token; hover uses a deliberately weaker 3.5% green fill.
- Image quality and asset fidelity: not applicable; this UI region contains no raster images, logos, or custom icons.
- Copy and content: passed. Navigation labels and brand copy are unchanged except presentation casing.

## Comparison history

1. Initial P1: hover and current navigation shared the same selector and visual treatment, producing two highlighted items. Fixed by separating hover/focus/current CSS and enforcing exactly one `aria-current="location"` link.
2. Initial P1: the fixed sidebar was positioned relative to the backdrop-filtered sticky header, causing it to overlap and visually clip the brand. Fixed by disabling the unnecessary header backdrop filter on this page; post-fix geometry confirms the sidebar begins at 68 px.
3. Initial P2: clicking the final `全品种` section could resolve back to `供需数据` because the document could not scroll its heading to the header threshold. Fixed with an explicit bottom-of-document branch; click regression now returns one matching current link for all four sections.
4. Post-fix visual comparison: no remaining P0/P1/P2 differences in the affected region.

## Primary interactions tested

- Clicked `盯盘总览`, `油脂主力`, `供需数据`, and `全品种`; each produced exactly one matching current item.
- Hovered `油脂主力` while `盯盘总览` remained current; only `盯盘总览` retained `aria-current` and the strong active rail.
- Checked browser console warnings/errors: none.

## Implementation checklist

- [x] Separate hover and current navigation styles.
- [x] Add scroll/click tracking with a single current item.
- [x] Handle the bottom-most section correctly.
- [x] Restore readable brand casing, font, spacing, and complete visibility.
- [x] Bump CSS/JS asset versions to avoid stale browser cache.
- [x] Pass automated tests and browser interaction regression.

## Follow-up polish

- None required for this scoped repair.

final result: passed
