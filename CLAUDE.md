# Design Guidelines

These rules govern all UI/UX work in this project. Treat them as defaults, not
dogma — if you break one, say so and say why.

## Core principle
Before building any screen, state in one line the *job* the user is trying to get
done here (Jobs To Be Done), and design backward from that outcome. If the job is
unclear, ask before designing.

## Spacing & layout
- Use a strict 4px spacing scale: 4, 8, 12, 16, 24, 32, 48, 64. No arbitrary values.
- Establish consistent vertical rhythm; related elements close, unrelated ones apart
  (proximity does the grouping work — avoid relying on borders/boxes).
- Default to generous whitespace. When unsure, add space rather than remove it.
- Mobile-first. Define behavior at 360px before desktop.

## Typography
- Type scale with clear hierarchy; no more than 2 font families.
- Body text: 16px minimum. Line length 60–75 characters (set a max-width on text).
- Line-height ~1.5 for body, tighter (1.1–1.25) for large headings.
- Headings establish hierarchy through size/weight, not color alone.

## Color & contrast
- All text must meet WCAG AA contrast (4.5:1 body, 3:1 large text). Verify, don't guess.
- One primary accent color used sparingly for the single most important action per view.
- Never use color as the *only* way to convey meaning (accessibility + clarity).
- Neutral grays for most of the UI; saturation earns attention, so spend it carefully.

## Interaction & usability (apply Laws of UX)
- Hick's Law: limit choices per screen; one clear primary action, secondary actions de-emphasized.
- Fitts's Law: tap targets ≥ 44x44px; primary actions large and easy to reach.
- Jakob's Law: use conventional patterns; don't reinvent common controls.
- Provide immediate feedback for every action (loading, success, error states).
- Every interactive element has visible hover, focus, active, and disabled states.
- Forms: inline validation, clear error messages that say how to fix the problem.

## Component systems (Atomic Design)
- Build from reusable primitives up; never hardcode a style that should be a token.
- Use design tokens / CSS variables for color, spacing, type, radius, shadow — no magic numbers.
- A new component must reuse existing tokens and primitives before introducing new ones.
- Keep components composable and single-responsibility.

## Accessibility (non-negotiable)
- Semantic HTML first; ARIA only when semantics can't express it.
- Full keyboard navigability; visible focus indicators (never remove focus outlines without replacement).
- All images have alt text; all inputs have associated labels.
- Respect prefers-reduced-motion.

## Motion
- Motion is functional, not decorative: it shows relationships and state changes.
- Keep durations short (150–300ms) with ease-out for entrances. No gratuitous animation.

## Before marking UI work done — self-check
1. Is spacing on the 4px scale and consistent?
2. Does contrast pass AA? Is hierarchy clear without relying on color?
3. Are all interactive states (hover/focus/active/disabled) present?
4. Does it work at 360px width and via keyboard only?
5. Did I reuse tokens/components instead of one-off values?