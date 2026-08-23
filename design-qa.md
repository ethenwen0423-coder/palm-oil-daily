**Design QA — Signal Grid site refresh**

- Source visual truth: `/Users/ethen/.codex/generated_images/01a029b7-39c7-7aa2-a6b9-09183a664138/exec-b46b7733-9300-49fd-832a-fde884a7e20b.png`
- Implementation: `http://127.0.0.1:8790/assistant.html`
- Desktop screenshot: `/tmp/palm-signal-grid-desktop.jpg`
- Mobile screenshot: `/tmp/palm-signal-grid-mobile.jpg`
- Expanded-timeline screenshot: `/tmp/palm-signal-grid-timeline-expanded-viewport.jpg`
- Combined comparison: `/tmp/palm-signal-grid-comparison.jpg`
- Source pixels: 1487 x 1058.
- Desktop implementation pixels/CSS viewport: 1440 x 1024 at device scale 1.
- Mobile implementation pixels/CSS viewport: 390 x 844 at device scale 1.
- Comparison normalization: source and desktop capture were independently scaled to 720 x 512 and placed side by side in a 1440 x 512 comparison image.
- State: assistant loaded from local static datasets; market correctly presented as a last-known snapshot and the research/status chain remained active.

**Full-view comparison evidence**

The implementation carries over the selected design's core composition: fixed left command rail, compact system bar, AI judgment plus priority split, one merged market module, evidence timeline, and right-side operational rail. The same pine-black, mint, ivory, amber, red, and cyan semantic palette is used. Above-the-fold density now keeps the timeline visible at 1440 x 1024.

The AI area is intentionally taller than the generated concept because the existing product requires explicit fundamental, technical, and execution-boundary explanations. Secondary evidence and the secondary oil-contract desk are collapsed by default so this added research depth does not crowd the primary scan path.

**Focused-region comparison evidence**

- Timeline expansion: the first row expands into three bounded columns (why it matters, evidence, next check); document width remains 1440 px and the expanded detail remains inside the 781 px timeline content area.
- Market module: the five primary contracts remain visible in one row; secondary contracts and external references expand inside the same module.
- Mobile: the AI judgment and priority panel stack to one column at 390 px; document and body widths both remain 390 px with no horizontal overflow.

**Required fidelity surfaces**

- Fonts and typography: compact sans-serif UI, tabular numerals, strong Chinese hierarchy, and restrained English micro-labels match the terminal direction. Real research titles wrap naturally rather than being truncated to the concept's mock copy.
- Spacing and layout rhythm: 68 px command bar, 176 px desktop rail, compact 6–10 px section radii, and divider-led grouping reproduce the selected direction without card nesting.
- Colors and visual tokens: deep pine surfaces, mint actions/status, amber confidence and warnings, and red/green market semantics are consistent across the assistant, homepage, reports, and OTC pages.
- Image quality and asset fidelity: the target is UI-led and contains no required photography or custom illustration. Existing product assets were preserved; no placeholder art or approximate custom icon assets were introduced.
- Copy and content: production-bound Chinese research content, data timestamps, health states, contract values, and risk boundaries are preserved. Concept-only mock values were not copied into the implementation.

**Findings**

No actionable P0, P1, or P2 issues remain.

**Comparison history**

- Initial P2: AI evidence and the full secondary oil desk pushed the timeline below the first viewport. Fix: kept the richer judgment summary visible, moved deeper evidence and secondary contracts into native expandable sections, and rechecked the same 1440 x 1024 state. Post-fix evidence: `/tmp/palm-signal-grid-desktop.jpg` and `/tmp/palm-signal-grid-comparison.jpg`.
- Initial P1: the desktop decision grid overrode the mobile single-column breakpoint, causing the AI title and priority list to overlap at 390 px. Fix: restored explicit one-column decision/workspace tracks below 980 px and removed the inter-column border. Post-fix evidence: `/tmp/palm-signal-grid-mobile.jpg`; document width equals viewport width.
- Earlier functional issue rechecked: expanding timeline detail previously risked abnormal layout. Post-fix evidence: `/tmp/palm-signal-grid-timeline-expanded-viewport.jpg`; expanded row stays within the timeline and page width does not grow.

**Primary interactions tested**

- Timeline row expand/collapse.
- Intelligence category filter (`研究`: 1 matching item, active state updated).
- Secondary oil desk expand/collapse (5 cards rendered).
- Persistent return-to-home link navigates to `index.html`.
- Desktop and mobile horizontal-overflow checks.
- Browser console: no errors or warnings in the tested local assistant state.
- Contract-analysis request wiring remains covered by `scripts.tests.test_contract_analysis_frontend` (3/3 passing); the standalone static server does not provide the production analysis backend.

**Follow-up polish**

- P3: add a compact icon set to the desktop command rail only if a production-safe local icon dependency is later approved; text labels are currently clearer than introducing a remote runtime dependency.

final result: passed
