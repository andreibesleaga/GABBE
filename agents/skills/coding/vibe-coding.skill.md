---
name: vibe-coding
description: "Turn a mood request (90s cyberpunk, Apple-style minimalism) into design tokens, CSS, motion and copy changes. Use when the user describes how a UI should feel rather than what it should do."
triggers: [vibe, aesthetic, style, feel, atmosphere, theme, mood, redesign, make it pop]
tags: [coding]
context_cost: medium
---
# Vibe Coding Skill

## Goal
Translate abstract user intents ("Vibes") into concrete implementation details (Design Tokens, CSS, Animation, Tone of Voice).

## Flow

### Steps
## 1. Vibe Analysis
**Input**: User Request (e.g., "Make the dashboard feel like a spaceship HUD")
**Action**: Decompose "The Vibe" into technical primitives.
*   **Color Palette**: High contrast? Neons? Pastels? Dark mode?
*   **Typography**: Monospace? Serif? Sans-Serif? Size/Weight?
*   **Motion**: Snappy? Float? ease-in-out? Glitch effects?
*   **Border/Shape**: Rounded? Sharp? Glassmorphism? Brutalist?

### 2. The "Vibe Translator" Persona
Adopt the `design-sys-arch` persona temporarily.
*   **Step 1**: Consult `design-tokens.json` or CSS variables.
*   **Step 2**: Propose a "Vibe Drift" (e.g., changing `--primary-color` from `#007bff` to `#00ffcc`).
*   **Step 3**: Generate a quick prototype of the change.

### 3. Implementation Patterns

#### A. Cyberpunk / Sci-Fi / HUD
*   **CSS**: `border: 1px solid var(--neon); box-shadow: 0 0 10px var(--neon);`
*   **Font**: Monospace (e.g., Fira Code, JetBrains Mono).
*   **Motion**: Glitch effects, scanning lines.

#### B. Clean / Minimal / "Apple"
*   **CSS**: `backdrop-filter: blur(20px); border-radius: 20px; box-shadow: 0 4px 24px rgba(0,0,0,0.05);`
*   **Font**: Systematic Sans-Serif (Inter, SF Pro).
*   **Motion**: Spring physics, subtle scales.

#### C. Brutalist / Retro
*   **CSS**: `border: 3px solid black; box-shadow: 4px 4px 0 black;`
*   **Font**: Bold headers, distinct serifs.
*   **Motion**: No easing, hard cuts.

### 4. Verification
*   ASK USER: "Does this match the vibe you were looking for?"
*   If NO -> Adjust **Intensity** (e.g., "More neon", "Less blur").

## Constraints
- Change design tokens and CSS first; add wrapper elements or heavy filters only when the effect needs them.
- Keep error and warning styling readable under every theme.

## Output Format
The CSS, token or component changes, and a short list of tokens changed (before and after).

## Limits and safety
- Validate any user-supplied theme value (for example `^#[0-9a-fA-F]{6}$`) before it goes into CSS or a `style` attribute.
- Do not copy the look of another organisation's login page or a trusted brand's sign-in; ask the human.
- Run an accessibility check (`axe-core` if the project has it); keep contrast and focus outlines, and no content flashing more than three times a second.
- Error, warning and consent text stays visible; a theme override must not hide it.
- At most 3 revision rounds on a vague request, then ask for concrete requirements.
