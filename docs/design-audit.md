# Portfolio design audit — 2026-11-08

## High impact

- Body copy inherited the terminal monospace face, which weakened readability across case studies, the About page, and long-form writing.
- Projects and writing still inherited older glass, gradient, large-shadow, rounded-card, and lift-on-hover rules. Those rules conflicted with the newer restrained terminal skin.
- Evidence-heavy cards were placed in three columns at desktop widths, creating narrow text measures and tall walls of copy.
- `.project-card--moved` hid five entries that remain part of the verified 14-project registry.
- Focus indication was inconsistent, filtered writing lacked exposed pressed state, motion did not have a global reduced-motion fallback, and long technical tokens could force overflow.

## Medium impact

- The homepage repeated ForgeCI, QuorumKV, and CommerceCore in adjacent “Current Work” and “Featured projects” sections without adding a distinct decision path.
- Mobile navigation wrapped into a dense multi-row block with small targets rather than remaining a predictable, scrollable top-level list.
- Status and technology metadata used too many pill treatments for content that is primarily editorial context.

## Subjective preferences not treated as defects

- The dark green terminal palette is distinctive and has strong measured text contrast, so it remains.
- Terminal prompts in the nameplate and hero provide identity; they were retained rather than repeated on every card.
- The static multi-page architecture is fast and appropriate. No framework, animation library, web font, or component dependency was added.

## UI/UX Pro Max guidance used

- Editorial grid: wider two-column cards, strong text hierarchy, and controlled reading measures.
- Developer mono pairing principle: system sans-serif for prose and system monospace for navigation, headings, labels, and code.
- Accessibility guidance: visible `:focus-visible`, skip link on scripted pages, 44px primary targets, filter state semantics, reduced motion, and long-token wrapping.
- Responsive guidance: one-column cards below 700px and horizontally scrollable mobile navigation without page-level overflow.

HUD effects, motion-driven presentation, oversized minimalism, imported Google fonts, and decorative stock imagery were deliberately rejected as poor fits.
