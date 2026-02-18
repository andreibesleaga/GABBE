# Visual Design System Guide

## Why a Design System?
A design system is the "single source of truth" for UI components and visuals. It prevents:
- **Inconsistency**: 50 shades of gray.
- **Redundancy**: Re-implementing the "Button" 10 times.
- **Accessibility failures**: Ensuring checking happens once, centrally.

## Core Elements (The Tokens)

### 1. Color Palette
Defined in `templates/coding/DESIGN_TOKENS_TEMPLATE.json`.
- **Primary**: Brand identity.
- **Surface**: Backgrounds (Light/Dark).
- **Semantic**: Success (Green), Warning (Orange), Error (Red).

### 2. Typography
- **Headings**: `Inter Tight`, `Poppins` (Display).
- **Body**: `Inter`, `Roboto` (Readability).
- **Code**: `Fira Code`, `JetBrains Mono`.

### 3. Spacing (The Grid)
Always use multiples of **4px** (0.25rem).
- `4px` (xs)
- `8px` (sm)
- `16px` (md)
- `24px` (lg)
- `32px` (xl)

## Component Lifecycle

1.  **Design** (`ui-design` persona): Defines the look in `tokens.json` or Figma.
2.  **Implementation** (`eng-frontend` persona): Builds the React/Vue component.
3.  **Documentation**: Adds to Storybook or `/docs/components`.

## Accessibility (a11y)
- **Contrast**: Text must be 4.5:1 against background.
- **Focus**: Never remove `outline` without providing a custom style.
- **Motion**: Respect `prefers-reduced-motion`.

## Tools
- **Tailwind CSS**: The preferred engine for utility-first styling.
- **Class Variance Authority (CVA)**: For managing component variants.
- **Radix UI / Headless UI**: For accessible primitives.
