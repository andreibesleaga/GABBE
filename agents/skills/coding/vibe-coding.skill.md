---
name: vibe-coding
description: Translates high-level aesthetic or behavioral "vibe" requests (e.g., "Make it feel like 90s cyberpunk", "Apple-style minimalism") into concrete code changes (CSS, Animation, Copy).
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
*   If NO -> Adjuest **Intensity** (e.g., "More neon", "Less blur").

## Security & Guardrails

### 1. Skill Security (Vibe Coding)
- **CSS Injection via Theme Customization**: Step 1 implies dynamic theme generation based on user inputs. If the agent implements a feature allowing users to customize "The Vibe" by saving color hex codes to a database, and the agent injects these directly into inline `<style>` tags or CSS variables without strict validation (e.g., `style="--primary: ${userColor}"`), an attacker can inject arbitrary CSS (e.g., `red; background-image: url(...)`). The agent must strictly validate all dynamic design tokens against rigorous regex patterns (e.g., verifying strict `#AABBCC` format) before injection.
- **Visual Deception (Phishing Aesthetics)**: An attacker could request a "vibe" that exactly mimics a trusted internal system or a third-party login page (e.g., "Make it feel exactly like the corporate Okta login"). This creates a high-fidelity phishing lure. The agent must employ visual heuristic scanning to detect and refuse requests that attempt to perfectly clone authenticated corporate infrastructure or known authentication portals.

### 2. System Integration Security
- **Accessibility Denial of Service (a11y DoS)**: In pursuit of extreme aesthetics (e.g., "Cyberpunk Glitch effects" or "Brutalist Hard cuts" from Step 3), the agent might generate CSS that violates WCAG guidelines so severely (e.g., flashing lights causing seizures, zero-contrast text, invisible focus states) that the application becomes legally unusable for disabled users. The system must enforce an automated accessibility gate (e.g., `axe-core`) that vetos any "Vibe Drift" triggering critical a11y regressions.
- **Information Hiding via Aesthetics**: When translating the vibe (Step 1), the agent might decide that error messages, security warnings, or consent banners "disrupt the aesthetic" and style them to be nearly invisible (e.g., opacity: 0.1, or hiding them off-screen). The agent must mathematically guarantee that all elements semantically tagged as `alert`, `warning`, or `error` adhere to strict minimum visibility and contrast thresholds, immune to global vibe overrides.

### 3. LLM & Agent Guardrails
- **The Infinite Design Loop**: Aesthetic adjustments are highly subjective. The `vibe-coding` loop (Step 4 "Verification") can trap the LLM in an infinite loop of endless, minor CSS tweaks if the user repeatedly responds with vague feedback like "make it pop more." The orchestrator must enforce a strict bound on "Vibe Revisions" (e.g., max 3 iterations) before gracefully exiting the loop and requesting concrete, specific technical requirements.
- **Component Bloat Hallucination**: To achieve a complex vibe (like Glassmorphism), the LLM might hallucinate the need for dozens of nested, unnecessary `<div>` wrappers or massively complex SVG filters, severely degrading the DOM performance and battery life of mobile devices. The agent must enforce a "Structural Simplicity" constraint, rejecting aesthetic implementations that arbitrarily inflate the DOM depth by more than $N$ levels.
