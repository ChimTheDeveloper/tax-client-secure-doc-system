# Phase 1: Design Audit Report
**Date**: April 17, 2026  
**Scope**: Current UI state analysis for Tax Intelligence System  
**Target**: WCAG 2.1 AA compliance + modern, professional appearance

---

## Executive Summary

The current UI is **functionally solid** but visually and accessibly underdeveloped. The app has:
- ✅ Clear information hierarchy and sensible layouts
- ✅ Decent color palette (teal + warm, earthy background)
- ✅ Responsive grid system
- ❌ **Missing accessibility features** (focus states, semantic HTML gaps, keyboard navigation incomplete)
- ❌ **Inconsistent spacing and sizing** (ad-hoc values, not token-based)
- ❌ **No dark mode** or accessible contrast in some areas
- ❌ **Limited feedback states** (loading, error, success interactions)
- ❌ **Poor mobile UX** (no hamburger nav, form inputs need refinement)

**Impact**: Users cannot navigate keyboard-only, screen readers struggle, and the interface feels more "prototype" than "production."

---

## Current Screen Inventory

### 1. **Login** (`login.html`)
**Purpose**: Entry point for authenticated users (email + password)

**Current State**:
- Two-column layout (hero on left, form on right)
- Form fields: Email, Password
- Button: "Enter Workspace"
- Feedback: Error message display

**Friction Points**:
- ❌ No visible focus outline on inputs (keyboard users can't see where they are)
- ❌ Input placeholder text is too light (nearly illegible)
- ❌ Button lacks hover/active feedback
- ❌ No success/confirmation after login (abrupt redirect)
- ❌ Password input should have a show/hide toggle
- ❌ Form doesn't prevent accidental submission (no validation feedback)
- ⚠️  Heading hierarchy incorrect (h1 for marketing copy, not semantic page title)

**Responsive Issues**:
- ⚠️  Two-column layout breaks at 900px → single column, but hero text is still marketing-focused (should adapt)

---

### 2. **Dashboard** (`dashboard.html`)
**Purpose**: Main workspace for authenticated users (uploader, reviewer, admin)

**Current State**:
- Header with greeting, role display, logout button
- Summary grid (4 stat cards: total docs, pending, approved, auto-processed)
- Two-column form grid (upload document, invite user) for admins
- Document table (filename, status, review actions)
- All users see all content (no role-based filtering)

**Friction Points**:
- ❌ **No role-based views** (admin sees user invite form; uploader doesn't need it but can't hide it)
- ❌ **Stat cards are meaningless without context** (what does "Pending Review" mean to an uploader vs. reviewer?)
- ❌ **Table is cramped** (long filenames truncate, review actions are inline and hard to scan)
- ❌ **No empty state** (what if there are no documents? Just blank table?)
- ❌ **Status column is unclear** (what does each status badge represent? Colors not defined)
- ❌ **No pagination/sorting** (10+ documents = unreadable table)
- ❌ **Inline review form is awkward** (enter comment + approve/reject in tight space)
- ❌ **No loading indicator** while documents fetch
- ⚠️  Mobile: summary grid collapses to 1 column, table becomes unmanageable
- ⚠️  No keyboard navigation in action buttons (table rows not navigable)

---

### 3. **Accept Invite** (`accept_invite.html`)
**Purpose**: Onboarding new users to set a password

**Current State**:
- Two-column layout (hero + invite summary on left, form on right)
- Shows invite details (name, email, role, expiration)
- Form fields: Password, Confirm Password
- Button: "Create Account"
- Feedback: Error message display

**Friction Points**:
- ❌ **No password strength indicator** (require 10 chars but no feedback as user types)
- ❌ **No real-time validation** (confirm password mismatch only on submit)
- ❌ **Focus outlines missing** (keyboard users lost)
- ❌ **Invite summary not visually distinct** (card styling blends with form card)
- ❌ **Expiration time not highlighted** (user might miss deadline)
- ⚠️  Similar mobile layout issues as login (text scale, form usability)

---

## Global Accessibility Issues (All Screens)

### Color & Contrast
- ⚠️  `.muted` text color (`#645b50`) on light backgrounds: Contrast ratio ~5.2:1 (WCAG AA passes, but AAA doesn't)
- ❌ **No focus indicators**: Links and buttons have no `:focus-visible` state
- ❌ **Error states rely on color alone**: Red alert box but no icon or text cue
- ⚠️  Stat card numbers are large but muted label text might be hard to read for low-vision users

### Keyboard Navigation
- ❌ No visible focus outline on form inputs
- ❌ Button focus outline exists but is very subtle
- ❌ Table rows don't support keyboard navigation (Tab skips over)
- ❌ No keyboard shortcuts defined (e.g., `Alt+U` for upload, `Alt+L` for logout)
- ⚠️  Tab order might be wrong in multi-column layouts (side-by-side forms)

### Semantic HTML
- ❌ Missing main/nav/header/footer elements (page structure implicit, not explicit)
- ❌ Form labels don't use `<label for="id">` pattern (some rely on nesting; inconsistent)
- ❌ Table headers (`<th>`) are styled but lack `scope="col"` attributes
- ❌ Status badges and role indicators have no ARIA labels (screen reader doesn't know what they mean)
- ❌ No `<main>` element (accessibility landmark missing)

### Mobile & Touch
- ⚠️  Input fields are too small for touch on mobile (44px minimum recommended, current is ~40px)
- ❌ No hamburger menu for mobile navigation
- ❌ Two-column layouts break abruptly (no tablet optimization)
- ❌ Inline review form becomes unusable on phone

---

## Design System Gaps

### Tokens Not Yet Defined
- ❌ **Color semantics**: No distinction between `--color-success`, `--color-warning`, `--color-error`, `--color-info`
- ❌ **Spacing scale**: Values are ad-hoc (8px, 12px, 14px, 16px, 18px, 22px, 24px, 28px, 32px)
- ❌ **Typography scale**: No defined sizes or line heights (using `clamp()` but no consistent scale)
- ❌ **Border radius scale**: Currently only `999px` (pill) and `24px` and `16px` (card); no middle values
- ❌ **Shadows**: Only one shadow defined; no elevation system
- ❌ **Transitions/animations**: Ad-hoc 120ms easing; no consistent timing or curves
- ❌ **Component states**: Hover, active, disabled, focused not systematically defined

### Spacing Inconsistencies
- Page padding: 32px (desktop), 18px (mobile)
- Card padding: 28px (hero, card), 22px (stat card)
- Form gaps: 16px (default), 8px (label gap), 4px (inline review form)
- Margin resets: Inconsistent (some elements margin-0, others margin: 8px 0)

### Typography Issues
- Font-family: Space Grotesk (good, distinctive)
- Fallback: No other weights used; only `wght@400;500;700` imported
- Font sizes: Mix of `rem`, `clamp()`, and hardcoded values; not layered
- Line-height: Not explicitly set on body; individual elements override
- Letter-spacing: Used for eyebrow (0.12em), th (0.06em); no standard

---

## Missing States & Interactions

### Feedback States
- ❌ **Loading**: No spinner/skeleton for document fetch or upload progress
- ❌ **Empty state**: No message if dashboard has 0 documents
- ❌ **Disabled state**: Buttons don't show disabled styling
- ❌ **Success feedback**: Upload success is just a redirect, no confirmation toast
- ⚠️  Error alerts are functional but could use icons

### Micro-interactions
- ⚠️  Button hover: Subtle transform (translateY -1px) is good but no color shift
- ❌ Form inputs: No focus styling beyond default browser outline
- ❌ Table rows: No hover highlight to show interactivity
- ❌ No transitions: Layout changes are instant (no fade/slide)

---

## Mobile Responsiveness Rating

| Breakpoint | Status | Issues |
|------------|--------|--------|
| 320px (phone) | ⚠️ Partial | Column stacking works; forms are cramped; no nav solution |
| 768px (tablet) | ⚠️ Partial | Summary grid 2x2, table readable but hero text oversized |
| 1024px (desktop) | ✅ Good | Current target; layout clear, content well-organized |
| 1440px (large) | ⚠️ Fine | Content centered; could use wider max-width or side margins |

---

## Performance & Code Quality

| Aspect | Status | Notes |
|--------|--------|-------|
| CSS Size | ✅ Good | ~350 lines; manageable |
| Font Loading | ⚠️ Improvable | 2 Google Fonts; consider `font-display: swap` |
| Layout Shifts | ⚠️ Low risk | Grid-based, predictable; no abrupt reflows |
| Unused CSS | ⚠️ Possible | `.invite-summary p` styling is narrow; could be more general |
| Selector Complexity | ✅ Good | Mostly single-class selectors; no deep nesting |

---

## Prioritized Friction Points (Top 10)

Ranked by **impact** (user confusion) × **effort to fix** (low effort = high ROI):

| Priority | Issue | Impact | Effort | Phase |
|----------|-------|--------|--------|-------|
| 🔴 P0 | Focus indicators missing on all inputs/buttons | High (keyboard navigation broken) | Low | 1 |
| 🔴 P0 | Semantic HTML structure incomplete (no main, nav, landmarks) | High (a11y failure) | Low | 1 |
| 🔴 P0 | Color tokens not semantic (no success/warning/error distinction) | High (confusing status) | Low | 1 |
| 🟠 P1 | Role-based dashboard views (admins see irrelevant forms) | Medium | Medium | 2 |
| 🟠 P1 | Table status column unclear (no consistent badge styling) | Medium | Low | 1 |
| 🟠 P1 | Mobile hamburger nav missing | Medium (phone users stuck) | Medium | 2 |
| 🟠 P1 | Loading states invisible (upload feels broken) | Medium | Low | 1 |
| 🟡 P2 | Empty state message missing | Low | Low | 1 |
| 🟡 P2 | Password strength indicator | Low | Low | 2 |
| 🟡 P2 | Dark mode (nice-to-have) | Low | Medium | 4 |

---

## Recommendations for Phase 1 (This Week)

### Do First (High ROI, Quick Wins)
1. ✅ **Define semantic color tokens** (success, warning, error, info) in CSS
2. ✅ **Add focus indicators** (`:focus-visible`) to all interactive elements
3. ✅ **Establish spacing scale** (xs, sm, md, lg, xl, 2xl)
4. ✅ **Document component specs** (buttons, inputs, cards, badges, status indicators)
5. ✅ **Create accessibility baseline** (keyboard nav, semantic HTML checklist)

### Do Second (Phase 2)
1. ✅ Refactor templates with semantic HTML (`<main>`, `<nav>`, `<header>`)
2. ✅ Implement all token-based styles (no hard-coded colors/spacing)
3. ✅ Build component library (reusable buttons, forms, cards)
4. ✅ Add loading/empty states to dashboard

### Do Later (Phase 3+)
1. ✅ Role-based dashboard views
2. ✅ Table pagination and sorting
3. ✅ Mobile navigation (hamburger)
4. ✅ Dark mode

---

## Exit Criteria for Phase 1

- [ ] Audit document complete (this file) ✅
- [ ] Design token system fully defined in CSS (colors, spacing, typography, shadows)
- [ ] Component specifications documented with HTML/CSS examples
- [ ] Accessibility checklist created + baseline sample component passes WCAG AA
- [ ] No breaking changes; existing layouts still functional
- [ ] CSS includes new tokens but old styles remain as fallback (backward compatible)

---

## Next Steps

1. Update `static/styles.css` with semantic color tokens, spacing scale, and component spec placeholders
2. Create `docs/COMPONENT_LIBRARY.md` with button, input, card, badge, and status indicator specs
3. Create `docs/ACCESSIBILITY_CHECKLIST.md` with WCAG 2.1 AA requirements and test plan
4. Review all templates for semantic HTML gaps (main, nav, landmarks)
5. Get approval on token system before proceeding to Phase 2 implementation
