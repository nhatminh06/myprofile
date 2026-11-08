# UI follow-up report — 2026-11-08

## Screenshot issues fixed

- **Excessive space below page introductions:** project, writing, research, and About intros now use a compact shared rhythm; subtitles no longer add a second large bottom margin.
- **Unreadable writing filters:** the legacy global button rule forced dark text with `!important`. Filter labels now explicitly use accessible light colors in default, hover, focused, and active states.
- **Content starting below the fold:** projects, writing cards, and the research card begin closer to their page heading without removing useful hierarchy.
- **About page style mismatch:** the centered promotional composition, circular glowing portrait, rounded gradient callout, and oversized gaps were replaced with the same flat editorial system used by projects and case studies.
- **Redundant Now page:** `now.html`, every navigation link to it, and its sitemap entry were removed.

## About page changes

- Left-aligned heading and summary consistent with other pages.
- Restrained two-column desktop layout: portrait rail plus a readable 72-character text column.
- Square, minimally treated portrait with no glow or hover zoom.
- Flat bordered kicker and callout using the terminal green/amber tokens.
- Consistent section dividers and experience timeline alignment.
- Single-column mobile reflow with a smaller portrait.

## Preserved

- Verified 14-project registry and GitHub metadata.
- Existing project claims, evidence, limitations, writing, and resume.
- Terminal palette, typography split, navigation cues, focus styles, and reduced-motion behavior.
- Static architecture and deployment configuration.

## Verification boundary

The supplied desktop screenshots were used to identify the CSS conflicts. No automated browser executable is available in this environment, so final viewport screenshots and hands-on checks at 375, 768, 1024, and 1440 pixels remain manual.
