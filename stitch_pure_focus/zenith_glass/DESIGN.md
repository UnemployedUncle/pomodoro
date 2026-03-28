# Design System: The Ethereal Editor

## 1. Overview & Creative North Star
The Creative North Star for this design system is **"The Ethereal Editor."** 

This system moves away from the "app-as-a-utility" look and toward "app-as-an-environment." By prioritizing high-end editorial layouts, we treat the screen as a canvas where time is the subject and photography is the soul. We break the rigid, boxy templates of traditional productivity tools through **intentional asymmetry** and **tonal depth**. Elements do not sit *on* the background; they live *within* it, using glassmorphism and sophisticated layering to create a sense of focused calm. The interface should feel like a quiet, high-end gallery space—minimalist, yet deeply intentional.

---

## 2. Colors & The Surface Philosophy
The palette is rooted in muted neutrals (`surface`, `primary`, `secondary`) to ensure the focus remains on the user's task and the ambient photography.

### The "No-Line" Rule
**Explicit Instruction:** Designers are prohibited from using 1px solid borders to define sections. Layout boundaries must be established through background color shifts or subtle tonal transitions. For example, a `surface-container-low` section should sit directly against a `surface` background to create a soft, modern distinction.

### Surface Hierarchy & Nesting
Treat the UI as a series of physical layers—like stacked sheets of frosted glass.
*   **Base:** High-quality photography.
*   **Layer 1:** `surface-container-lowest` (for the most transparent, expansive areas).
*   **Layer 2:** `surface-container-low` (for secondary information).
*   **Layer 3:** `surface-container-high` (for active interactive elements or modals).

### The "Glass & Gradient" Rule
To achieve a signature feel, apply `backdrop-blur` (12px–20px) to all container elements. Use semi-transparent versions of `surface-variant` or `surface-container`. 
*   **Signature Textures:** For the main "Focus" CTA or progress indicators, use a subtle linear gradient transitioning from `primary` to `primary-container`. This adds a "soulful" shimmer that flat colors lack.

---

## 3. Typography: The Editorial Contrast
We use a dual-typeface system to balance functional clarity with emotional resonance.

*   **The Voice (Serif):** `notoSerif` is our editorial voice. It is used for quotes and primary time displays (`display-lg`, `headline-lg`). It should feel prestigious and slow, encouraging reflection.
*   **The Engine (Sans-Serif):** `manrope` is our functional engine. Used for UI labels, settings, and button text (`label-md`, `body-sm`). It is modern, clean, and recedes into the background to keep the "engine" of the app quiet.

**Intentional Scale:** Do not fear large type. A `display-lg` timer set in `notoSerif` against a minimalist background creates an authoritative, premium aesthetic that needs no further decoration.

---

## 4. Elevation & Depth
In this system, elevation is conveyed through **Tonal Layering** rather than structural lines.

*   **The Layering Principle:** Stacking `surface-container` tiers creates natural lift. Place a `surface-container-highest` card on a `surface-container-low` background to create a soft, natural focal point.
*   **Ambient Shadows:** When an element must "float" (e.g., a settings modal), use extra-diffused shadows. 
    *   **Blur:** 40px–60px.
    *   **Opacity:** 4%–8%.
    *   **Color:** Use a tinted version of `on-surface` rather than pure black to maintain a natural, ambient light feel.
*   **The "Ghost Border" Fallback:** If a container needs more definition against a busy photo, use a **Ghost Border**: the `outline-variant` token at **15% opacity**. Never use 100% opaque borders.

---

## 5. Components

### The Focus Timer (Signature Component)
The central element. Use `display-lg` in `notoSerif`. The progress ring should use `tertiary` with a soft outer glow (ambient shadow) to signify "active energy" without being distracting.

### Buttons
*   **Primary:** A glassmorphic pill shape (`rounded-full`) using `primary` text on a `surface-container-high` background with 60% opacity. 
*   **Secondary:** Ghost-style. No background, `label-md` in `on-surface-variant`.
*   **Tertiary (The "Accent"):** Used only for the "Start" state. Use the `tertiary` color for text to draw the eye subtly.

### Cards & Containers
*   **Rule:** Forbid divider lines. 
*   **Execution:** Use `spacing-8` or `spacing-10` to separate content. Group related items by nesting them within a `surface-container-low` shape with `rounded-xl` (0.75rem) corners.

### Interactive Inputs
*   **Checkboxes/Radio:** Use `primary-dim` for the "off" state and `tertiary` for the "on" state. The transition should be a slow fade (300ms) to maintain the "Ethereal" feel.
*   **Input Fields:** Minimalist under-lines only using the "Ghost Border" rule. Focus states should transition the line to `primary`.

### Navigation
Use a floating bottom bar with a high `backdrop-blur`. The active state is indicated by a subtle shift from `on-surface-variant` to `on-surface` and a small `primary` dot—no heavy backgrounds or boxes.

---

## 6. Do's and Don'ts

### Do:
*   **Embrace Negative Space:** Use `spacing-16` and `spacing-20` to let the quotes and photography breathe.
*   **Use Asymmetry:** Place the quote in the top-left and the timer in the bottom-right to create a sophisticated, editorial "Golden Ratio" layout.
*   **Prioritize Legibility:** Ensure that glassmorphic containers have enough `backdrop-blur` so that text remains readable over complex backgrounds.

### Don't:
*   **Don't use 1px dividers:** They shatter the "Ethereal" illusion. Use white space.
*   **Don't use pure black (#000) for shadows:** It looks "dirty." Always tint your shadows with the background tone.
*   **Don't overcrowd the screen:** If a feature isn't essential for focus, hide it behind a `surface-container` layer.
*   **Don't use standard "Alert" colors:** Even for errors, use the `error_dim` token to ensure the UI doesn't "shout" at the user. Stay elegant, even in failure states.