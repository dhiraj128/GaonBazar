---
name: Gramin Commerce
colors:
  surface: '#f9f9ff'
  surface-dim: '#cfdaf2'
  surface-bright: '#f9f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f0f3ff'
  surface-container: '#e7eeff'
  surface-container-high: '#dee8ff'
  surface-container-highest: '#d8e3fb'
  on-surface: '#111c2d'
  on-surface-variant: '#3e4a3d'
  inverse-surface: '#263143'
  inverse-on-surface: '#ecf1ff'
  outline: '#6e7b6c'
  outline-variant: '#bdcaba'
  surface-tint: '#006e2d'
  primary: '#006b2c'
  on-primary: '#ffffff'
  primary-container: '#00873a'
  on-primary-container: '#f7fff2'
  inverse-primary: '#62df7d'
  secondary: '#a73a00'
  on-secondary: '#ffffff'
  secondary-container: '#fd651e'
  on-secondary-container: '#571a00'
  tertiary: '#825100'
  on-tertiary: '#ffffff'
  tertiary-container: '#a36700'
  on-tertiary-container: '#fffbff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#7ffc97'
  primary-fixed-dim: '#62df7d'
  on-primary-fixed: '#002109'
  on-primary-fixed-variant: '#005320'
  secondary-fixed: '#ffdbce'
  secondary-fixed-dim: '#ffb599'
  on-secondary-fixed: '#370e00'
  on-secondary-fixed-variant: '#7f2b00'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#f9f9ff'
  on-background: '#111c2d'
  surface-variant: '#d8e3fb'
typography:
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 30px
    fontWeight: '800'
    lineHeight: 38px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 26px
    fontWeight: '800'
    lineHeight: 34px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 22px
    fontWeight: '700'
    lineHeight: 28px
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '700'
    lineHeight: 24px
  title-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '700'
    lineHeight: 22px
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '500'
    lineHeight: 24px
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
  label-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '700'
    lineHeight: 18px
    letterSpacing: 0.01em
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 14px
    letterSpacing: 0.04em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1rem
  margin: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.25rem
  space-xl: 1.75rem
---

## Brand & Style

This design system is engineered for rural and semi-urban last-mile commerce, connecting village communities, local kirana partners, and delivery runners. The system balances high-utility digital infrastructure with the grounded familiarity of village marketplaces (*haats* and *bazaars*).

### Personality & Values
- **Uncompromising Trust & Reliability:** Transactions, order confirmations, and delivery states must feel absolute, transparent, and immediate to remove digital hesitancy.
- **Physical & Functional Familiarity:** Visual cues mirror physical commodities, token systems, and clear state markers rather than abstract technical interfaces.
- **Inclusivity & Vernacular Literacy:** First-class visual hierarchy catering to multilingual contexts (Hindi and English scripts), varying degrees of digital literacy, and variable sunlight visibility.

### Aesthetic Movement
The aesthetic adheres to **Tactile Utility & Functional Clarity**:
- Deep contrast ratios exceeding WCAG AAA wherever transactional information or pricing is shown.
- Tactile, large-format touch surfaces designed for single-thumb field navigation and low-cost smartphones.
- Physical card metaphors paired with reassuring ambient elevation to ground screen layers without cluttered decoration.

## Colors

The palette leverages agrarian growth tones, urgent logistics signifiers, and deep slate anchors for extreme sunlight readability.

### Color Tokens & Roles
- **Primary (`#16A34A`):** Trust, agricultural prosperity, verified statuses, successful transactions, and primary navigation active states.
- **Secondary / Action (`#EA580C`):** High-urgency action points, cart checkout triggers, delivery tracking anchors, and key system prompts.
- **Accent Amber (`#F59E0B`):** In-transit states, pending balances, warnings, festive tags, and rating badges.
- **Surface & Canvas:**
  - `bg-app`: `#F8FAFC` (Canvas foundation)
  - `bg-subtle`: `#F1F5F9` (Secondary wells, chip backgrounds, disabled containers)
  - `surface-card`: `#FFFFFF` (Elevated component surfaces)
- **Text & Hierarchy:**
  - `text-primary`: `#1E293B` (High-contrast headings, prices, item counts)
  - `text-secondary`: `#64748B` (Bilingual captions, descriptions, meta-tags)
- **Borders & Dividers:**
  - `border-subtle`: `#E2E8F0` (Card outlines, static input boundaries)
  - `border-focus`: `#16A34A` or `#EA580C` (Active 2px focus rings)

### Sunlight & Accessibility Rules
- Text on colored chips must never fall below a 4.5:1 contrast ratio. When using `#F59E0B` for badges, always pair with `#1E293B` text rather than white.
- Avoid low-opacity text overrides under daylight conditions; use strictly `#1E293B` and `#64748B`.

## Typography

The typography scale utilizes **Plus Jakarta Sans** for its generous x-height, open apertures, wide counters, and rounded friendly demeanor. This font provides clear glyph rendering across both high-density and low-resolution budget displays.

### Bilingual Typography Guidelines
- **Dual-Script Pairing:** When English is displayed alongside Devanagari script (Hindi, Marathi, etc.), scale line-heights by an additional `+2px` to accommodate ascending *matras* and prevent vertical clipping.
- **Price Presentation:** Currency symbols (₹) and price numerals must render with `fontWeight: 700` or `800` using `headline-md` or `title-lg` for instant clarity at checkout points.
- **Minimum Size Floor:** No actionable label, form hint, or primary product detail may drop below `12px` (`label-md`). Sub-12px styles are reserved exclusively for badge categories and metadata tags.

## Layout & Spacing

The layout is built on an **8pt flexible grid system** optimized primarily for mobile form factors, scaling out to tablet surfaces for shopkeeper inventory portals.

### Grid & Breakpoints
- **Compact Mobile (up to 420px):** 4-column fluid layout with `margin: 1rem` (16px) and `gutter: 0.75rem` (12px).
- **Tablet / Counter POS (421px - 840px):** 8-column layout with `margin: 1.5rem` (24px) and `gutter: 1rem` (16px).
- **Desktop Logistics Portal (841px+):** 12-column structured grid centered at a maximum width of `1200px`.

### Touch-First Rhythm
- **Minimum Tap Target:** All interactive nodes (buttons, steppers, voice search triggers, back buttons) must conform to a hard boundary minimum of **48px × 48px**.
- **Edge Cushioning:** Critical action triggers (such as fixed bottom checkouts) must retain a safe area clearance of `space-md` plus device inset bottom values.

## Elevation & Depth

Visual hierarchy uses **Soft Ambient Elevation** combined with **Crisp Defensive Outlines** to remain legible on dim screens and high-glare environments.

### Shadow Scale
- **Flat Surface (`elevation-0`):** Pure `#FFFFFF` resting on `#F8FAFC`, enclosed with a 1px border of `#E2E8F0`. Used for nested lists, inline data summaries, and static specs.
- **Card / Rest State (`elevation-1`):** `box-shadow: 0 2px 8px rgba(30, 41, 59, 0.06);` paired with a 1px `#E2E8F0` border. Applied to catalog items, order cards, and delivery timeline containers.
- **Floating Controls & Action Trays (`elevation-2`):** `box-shadow: 0 6px 16px rgba(30, 41, 59, 0.10);` with no border. Applied to sticky cart bars, voice search buttons, and live delivery pills.
- **Modal Sheets & Overlays (`elevation-3`):** `box-shadow: 0 12px 32px rgba(30, 41, 59, 0.16);` paired with a 50% opacity neutral backdrop (`rgba(30, 41, 59, 0.5)`).

### Sunlight Optimization
Never use blur-only shadow separation for critical boundary identification. Every elevated surface on mobile must maintain a structural hairline border (`#E2E8F0`) to ensure distinction when backlights are at maximum brightness.

## Shapes

The shape vocabulary uses approachable, friendly rounded contours that feel warm and modern while preserving layout density.

### Shape Token Implementation
- **Cards & Banners (`rounded-xl` / 18px-20px):** Large external card corners that create a distinct visual pocket for multi-item groupings, delivery statuses, and category hero blocks.
- **Inputs & Action Buttons (`rounded-lg` / 12px-14px):** Balanced curve providing a tactile, pill-adjacent surface that clearly indicates interactive affordance.
- **Chips, Badges & Micro-controls (`rounded-full` / 9999px):** Fully rounded pill geometry for category filters, status indicators, and floating counter badges.

## Components

### Buttons
- **Primary / Action Button:** Solid `#EA580C` background with `#FFFFFF` text. Height of 52px (minimum 48px). Bold text (`label-lg`), `rounded-lg` (12px), active compression state (`transform: scale(0.98)`).
- **Secondary / Utility Button:** Solid `#16A34A` background with `#FFFFFF` text for core agricultural or order-placement actions.
- **Outline / Secondary Flow:** Transparent background, 2px border in `#16A34A` or `#E2E8F0`, text in `#1E293B`.
- **Icon Assist:** Buttons accommodate a 24px leading icon (e.g., Speaker icon for audio readouts or WhatsApp icon for community order support).

### Cards
- **Product & Category Cards:** Background `#FFFFFF`, border 1px `#E2E8F0`, border-radius 18px (`rounded-xl`), padding `space-md` (16px), elevation `elevation-1`.
- **Order Tracking Card:** Distinct left accent border (4px solid `#16A34A` or `#EA580C`) showing the current physical dispatch point (e.g., "Left Taluka Hub", "Reached Village Point").

### Inputs & Form Fields
- **Container:** Height 52px, background `#FFFFFF`, border 1.5px `#E2E8F0`, border-radius 12px (`rounded-lg`), horizontal padding 16px.
- **Active Focus:** Border transitions to 2px solid `#16A34A` or `#EA580C` with a soft outer ring `rgba(22, 163, 74, 0.12)`.
- **Bilingual Supporting Labels:** Floating label in `#64748B` supporting dual English/Hindi hints (e.g., "Mobile Number / मोबाइल नंबर").
- **Integrated Voice Input:** Trailing mic icon inside input fields to initiate vernacular speech-to-text queries.

### Chips & Filters
- **Default State:** Height 38px, background `#F1F5F9`, border 1px solid `#E2E8F0`, text `#1E293B` (`label-md`), fully rounded.
- **Selected State:** Background `#16A34A`, border 1px solid `#16A34A`, text `#FFFFFF`, bold font weight.

### Quantity Stepper (Rural Cart Utility)
- Compact, high-visibility counter with 48px tap areas for `-` and `+` triggers.
- Background `#F8FAFC`, bordered with 1px `#E2E8F0`, counter value in `#1E293B` (`title-lg`).

### Lists
- Dividers use 1px `#F1F5F9`. Minimum row height of 56px with primary bilingual title stacked vertically over secondary status meta-text.

### Checkboxes & Radio Buttons
- 24px × 24px touch box centered within a 48px minimum touch cell.
- Checkbox uses 2px border `#1E293B`, filling with `#16A34A` upon selection with a crisp white tick. Radio buttons use a 2px ring with a solid center dot on active selection.