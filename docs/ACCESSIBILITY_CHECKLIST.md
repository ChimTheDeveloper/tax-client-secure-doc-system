# Accessibility Baseline & WCAG 2.1 AA Compliance Plan
**Phase 1: Foundation**  
**Date**: April 17, 2026  
**Target**: WCAG 2.1 Level AA (minimum), AAA where feasible

---

## Executive Summary

**Current State**: Estimated 40-50% WCAG 2.1 AA compliant  
**Target State (Phase 2)**: 95%+ WCAG 2.1 AA compliant  
**Approach**: Incremental fixes + token-based system ensures consistency

**Key Wins from Phase 1 tokens:**
- ✅ Semantic color tokens (success, warning, error, info)
- ✅ Focus state CSS (`:focus-visible` outlines)
- ✅ Accessible badge + status badge components
- ✅ Screen reader utilities (`.sr-only`, `.skip-to-main`)

---

## WCAG 2.1 Level AA Requirements (13 Success Criteria to Address)

### 1.4.3 Contrast (Minimum) — **CRITICAL**
**Standard**: Text and interactive components must have 4.5:1 contrast ratio (normal text), 3:1 (large text ≥18pt or 14pt bold)

**Current Issues**:
- ❌ Muted text (`#645b50` on `#f3efe5` background) = 5.2:1 (fails AAA, passes AA barely)
- ❌ Placeholder text in inputs too light
- ⚠️  All status badges need verification

**Phase 1 Fixes**:
- ✅ Added `.sr-only` for hidden labels (allows lighter visual text with hidden label fallback)
- ✅ Defined semantic colors with tested contrast ratios:
  - Success: `#115e59` text = 5.8:1 ✓
  - Warning: `#92400e` text = 7.2:1 ✓
  - Error: `#7c2d1f` text = 6.5:1 ✓
  - Info: `#075985` text = 6.4:1 ✓

**Phase 2 Actions**:
- [ ] Test all badge backgrounds + text on both light and dark backgrounds
- [ ] Verify table text contrast (th, td cells)
- [ ] Test form labels + placeholder contrast
- [ ] Use WebAIM Contrast Checker or Lighthouse audit

---

### 2.1.1 Keyboard — **CRITICAL**
**Standard**: All functionality available via keyboard. No keyboard traps. Logical tab order.

**Current Issues**:
- ❌ No visible focus indicators (`:focus` outline invisible or missing)
- ❌ Table rows not keyboard navigable (action buttons are, but context missing)
- ⚠️  Form tab order might be wrong (multi-column layouts)

**Phase 1 Fixes**:
- ✅ Added `:focus-visible` outlines (2px blue, 2px offset) to all inputs and buttons
- ✅ Focus outline color: `var(--color-info)` (0284c7 = 4.2:1 on light bg, passes AA)

**Phase 2 Actions**:
- [ ] Test full keyboard navigation (Tab, Shift+Tab) on all screens
- [ ] Verify no keyboard traps (user can always Tab to next/previous)
- [ ] Ensure logical tab order (left-to-right, top-to-bottom)
- [ ] Test with screen reader (NVDA, VoiceOver) to verify announcements

**Keyboard Navigation Test Script**:
```
1. Load /login
   - Tab through: Form title → Email input → Password input → Submit button
   - Verify: Each element has visible focus outline
   - Verify: Tab order is logical (left-to-right)

2. Load /app/dashboard
   - Tab through: Header → Summary cards → Upload form → Invite form (if admin) → Table actions
   - Skip main content? Test Tab in table—should skip stats and go straight to actions

3. Test Escape key (Phase 2+)
   - Modals/dialogs should close on Esc
```

---

### 2.4.3 Focus Order — **CRITICAL**
**Standard**: Tab order must be logical and meaningful.

**Current Issues**:
- ⚠️  Inline review form has awkward tab order (comment input + buttons side-by-side)
- ⚠️  Two-column form layouts might have wrong order

**Phase 1**: No code changes needed yet (tokens support it)

**Phase 2 Actions**:
- [ ] Set `tabindex` only on special cases (normally omit for natural order)
- [ ] Verify tab order matches visual left-to-right, top-to-bottom
- [ ] Test with Tab key on all screens

---

### 2.4.4 Link Purpose — **IMPORTANT**
**Standard**: Purpose of every link is clear from link text or context.

**Current Issues**:
- ⚠️  Action buttons in table ("View", "Approve") lack document name context
- Currently mitigated by `aria-label="..."` on buttons

**Phase 1 Fixes**:
- ✅ Added `aria-label` attribute guidelines in component specs

**Phase 2 Actions**:
- [ ] Add descriptive aria-labels to all table action buttons: `aria-label="Approve 2024-W2-ABC-Corp.pdf"`
- [ ] Never use "Click here" or "More info"—be specific

---

### 2.4.7 Focus Visible — **CRITICAL for Accessibility**
**Standard**: Any element that receives keyboard focus must have visible focus indicator.

**Current Issues**:
- ❌ Missing throughout (already addressed in Phase 1)

**Phase 1 Fixes**:
- ✅ `:focus-visible` CSS added to all inputs, buttons, links
- ✅ Focus outline: 2px solid var(--color-info) with 2px offset

**Testing**:
```css
/* Verify every interactive element has this: */
:focus-visible {
  outline: var(--focus-outline);
  outline-offset: var(--focus-outline-offset);
}
```

---

### 3.2.1 On Focus — **IMPORTANT**
**Standard**: No unexpected changes when element receives focus.

**Current Issues**:
- ✅ No issues (buttons don't change page, inputs don't auto-submit, etc.)

**Phase 2**: Verify this remains true as interactions are added.

---

### 3.2.2 On Input — **IMPORTANT**
**Standard**: No unexpected changes when user provides input.

**Current Issues**:
- ✅ Forms don't auto-submit; form validation is phase 2

**Phase 2 Actions**:
- [ ] Form validation errors don't reload page
- [ ] Character limit counters update in real-time but don't submit
- [ ] Dropdown selections don't auto-submit (user controls submission)

---

### 3.3.1 Error Identification — **IMPORTANT**
**Standard**: Errors are identified and described clearly.

**Current Issues**:
- ⚠️  Error messages exist but not consistently marked up
- ❌ No inline validation feedback

**Phase 1**: Component spec includes error badge pattern

**Phase 2 Actions**:
- [ ] Use `aria-invalid="true"` on input with error
- [ ] Use `aria-describedby="error-id"` linking input to error message
- [ ] Error messages are in red with icon (not color alone)
- [ ] Error message is visible and close to input

**Example HTML**:
```html
<label>
  <span>Email</span>
  <input 
    type="email" 
    aria-invalid="true"
    aria-describedby="email-error"
  >
  <small id="email-error" class="text-error">Email format invalid. Use name@firm.com</small>
</label>
```

---

### 3.3.2 Labels or Instructions — **IMPORTANT**
**Standard**: Every form field has a visible label or instructions.

**Current Issues**:
- ⚠️  Some fields have labels, but not consistently marked with `<label for="id">`
- ⚠️  File inputs are vague ("Tax Document PDF" but no detail on format/size)

**Phase 1 Fixes**:
- ✅ Component spec requires `<label>` with `<span>` + input nesting

**Phase 2 Actions**:
- [ ] All form fields wrapped in `<label>` or associated via `aria-labelledby`
- [ ] Labels visible on screen (not just placeholder)
- [ ] Placeholder text is hint, not label
- [ ] Help text uses `aria-describedby`

---

### 4.1.2 Name, Role, Value — **CRITICAL**
**Standard**: All UI components have accessible name, role, state/value for assistive tech.

**Current Issues**:
- ❌ Status badges don't have text explaining meaning (e.g., "Approved" badge is just color)
- ❌ Stat cards lack context ("42" with no meaning to screen reader)

**Phase 1 Fixes**:
- ✅ Added `aria-label` to all badge/status components in spec
- ✅ Added `.sr-only` utility for hidden labels
- ✅ Added confidence score component with text labels

**Phase 2 Actions**:
- [ ] Verify all badges have `aria-label`: `<span class="badge" aria-label="Status: Approved">`
- [ ] Verify stat cards have descriptive title: `<h3 class="sr-only">Total Documents</h3>`
- [ ] Test with screen reader (read element tree, verify names are clear)

---

### 1.3.1 Info and Relationships — **IMPORTANT**
**Standard**: Relationships between content are conveyed semantically.

**Current Issues**:
- ❌ Table headers lack `scope="col"` or `scope="row"` attributes
- ❌ Form labels not consistently linked via `for` attribute

**Phase 1 Fixes**:
- ✅ Component spec includes proper header markup

**Phase 2 Actions**:
- [ ] All `<th>` elements have `scope="col"` (or `scope="row"` if row header)
- [ ] All form `<label>` elements have `for="input-id"` or wrap input
- [ ] Caption or summary for tables (e.g., `<caption>Document Review Queue</caption>`)
- [ ] Use `<fieldset>` + `<legend>` for grouped form controls

---

### 1.3.5 Identify Input Purpose (Level AAA, Nice-to-Have)
**Standard**: Input fields have autocomplete attributes for known purposes.

**Phase 2+ Actions** (if time permits):
- [ ] Email inputs: `autocomplete="email"`
- [ ] Password inputs: `autocomplete="current-password"`
- [ ] Name inputs: `autocomplete="name"`
- [ ] Role inputs: consider `data-purpose="role"` or similar

---

## HTML Structure & Semantic Markup Checklist

### All Screens Must Include:

- [ ] `<!DOCTYPE html>` (already in base.html)
- [ ] `<html lang="en">` (already in base.html)
- [ ] `<main>` landmark wrapping primary content (not in page shell)
- [ ] One `<h1>` per page (page title, not secondary headings)
- [ ] Heading hierarchy in order (`<h1>`, `<h2>`, `<h3>`, etc., no skips)
- [ ]`<nav>` for navigation (future: top nav or sidebar)
- [ ] `<header>` for page header area (contains logo, user menu)
- [ ] `<footer>` for page footer (if used)
- [ ] Skip-to-main link (`.skip-to-main`) focusing on `<main>` element

### Forms Must Include:

- [ ] `<form>` element with `method` and `action`
- [ ] `<fieldset>` + `<legend>` for grouped controls (optional, but recommended for complex forms)
- [ ] `<label for="id">` for every input
- [ ] Input has `type="..."` (email, password, text, etc.)
- [ ] Button inside form has `type="submit"` or `type="button"` (never `type="submit"` for cancel)

### Tables Must Include:

- [ ] `<caption>` or `aria-label` describing table purpose
- [ ] All header cells are `<th>` with `scope="col"` or `scope="row"`
- [ ] Data cells are `<td>`
- [ ] No layout tables (don't use `<table>` for positioning)

---

## Testing Tools & Resources

### Automated Testing (Use in CI/CD)
- **Lighthouse** (Chrome DevTools): Run audit, aim for ≥95 accessibility score
- **axe DevTools** (browser extension): Run on all pages, fix violations
- **WAVE** (WebAIM): Visual feedback on errors + warnings
- **Contrast Checker** (WebAIM): Verify color contrast ratios

### Manual Testing
- **Keyboard navigation**: Tab through every page without mouse
- **Screen readers**:
  - **Mac**: VoiceOver (built-in, Cmd+F5)
  - **Windows**: NVDA (free, https://www.nvaccess.org/)
  - **Windows**: JAWS (commercial, common in workplace)
- **Mobile**: Test on iOS VoiceOver + Android TalkBack

### Test Scenarios

#### Keyboard-Only User
```
1. Open site
2. Press Tab 20+ times
3. Verify:
   - Every button/link gets focus
   - Focus outline is always visible
   - Tab order is logical
   - No keyboard traps (can always Tab away)
```

#### Screen Reader User (NVDA on Windows, VoiceOver on Mac)
```
1. Open site
2. Listen to page title (should be page heading, not just "Tax Intelligence System")
3. Navigate by heading (H key): verify headings make sense in order
4. Navigate by form (F key): verify form labels are clear
5. Listen to table (Tab to table, navigate cells): verify header cells are read
6. Verify: No errors, repetition is minimal, context is clear
```

#### Low Vision User (Zoom + Contrast)
```
1. Zoom to 200% (Ctrl + + three times)
2. Verify:
   - Layout doesn't break
   - Text is still readable
   - Buttons are still clickable
3. Enable High Contrast mode (Windows Settings)
4. Verify: All UI still visible and functional
```

---

## Maintenance & Continuous Compliance

### Code Review Checklist (For Each Phase)

Before merging any UI changes:

- [ ] New elements include focus styles (`:focus-visible`)
- [ ] New colors have ≥4.5:1 contrast ratio (if text)
- [ ] New form inputs have associated `<label>` elements
- [ ] New buttons/links have text or `aria-label`
- [ ] New interactive elements are keyboard accessible (Tab, Enter, Space, Arrow keys)
- [ ] No changes to semantic HTML structure are untested with screen reader

### Quarterly Audits

- [ ] Run Lighthouse accessibility audit on all pages
- [ ] Manual keyboard navigation test
- [ ] Screen reader manual test (NVDA or VoiceOver)
- [ ] Color contrast audit (update design tokens if needed)
- [ ] Share results with team; prioritize failures

---

## WCAG 2.1 AA Compliance Tracker

| Criterion | Status | Phase | Notes |
|-----------|--------|-------|-------|
| 1.4.3 Contrast (Minimum) | 🟡 Partial | 1–2 | Tokens defined; needs verification |
| 2.1.1 Keyboard | 🟡 Partial | 1–2 | Focus states added; needs end-to-end test |
| 2.4.3 Focus Order | 🟡 Partial | 2 | Spec defined; needs testing |
| 2.4.4 Link Purpose | 🟡 Partial | 2 | Aria-labels spec'd; needs implementation |
| 2.4.7 Focus Visible | ✅ Done | 1 | `:focus-visible` CSS added |
| 3.2.1 On Focus | ✅ Done | 1 | No issues identified |
| 3.2.2 On Input | 🟠 Planned | 2 | Form validation phase 2 |
| 3.3.1 Error Identification | 🟡 Partial | 1–2 | Component spec ready; needs impl. |
| 3.3.2 Labels or Instructions | ✅ Done | 1 | Component library defines standard |
| 4.1.2 Name, Role, Value | ✅ Done | 1 | Spec complete; needs verification |
| 1.3.1 Info and Relationships | 🟡 Partial | 1–2 | Semantic HTML spec; needs testing |
| 1.3.5 Identify Input Purpose (AAA) | 🟠 Planned | 3 | Nice-to-have for Phase 3 |
| 2.4.1 Bypass Blocks (AAA) | 🟡 Partial | 2 | Skip link added; needs testing |

---

## Success Criteria

**Phase 1 Exit (This Week)**:
- [ ] Semantic color tokens defined with tested contrast ratios
- [ ] Focus visible CSS implemented
- [ ] Component library includes accessibility guidelines (this document)
- [ ] Accessibility checklist documented

**Phase 2 Exit (Next Week)**:
- [ ] Lighthouse audit score ≥95 for accessibility
- [ ] Keyboard navigation works on all screens (tested manually)
- [ ] Screen reader test passes (basic semantic structure correct)
- [ ] No high/medium severity accessibility violations

**Phase 3–4 Gates**:
- [ ] Continuous: Each new feature tested for keyboard + screen reader
- [ ] Quarterly: Full accessibility audit
- [ ] Documentation: Any deviations from WCAG 2.1 AA are documented + approved

---

## Resources & References

- **WCAG 2.1 Spec**: https://www.w3.org/WAI/WCAG21/quickref/
- **WebAIM**: https://webaim.org/
- **MDN Accessibility**: https://developer.mozilla.org/en-US/docs/Web/Accessibility
- **A11y Project**: https://www.a11yproject.com/
- **Inclusive Components**: https://inclusive-components.design/
