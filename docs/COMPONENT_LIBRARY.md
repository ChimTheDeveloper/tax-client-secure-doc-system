# Component Library Specification
**Phase 1: Foundation Components**  
**Date**: April 17, 2026  
**Status**: Specification (Ready for Phase 2 Implementation)

This document defines reusable components for the Tax Intelligence System. Each component includes:
- Purpose and use cases
- HTML markup
- CSS classes and variants
- Accessibility requirements
- States (default, hover, active, disabled, focus)

---

## Table of Contents
1. [Button](#button)
2. [Text Input](#text-input)
3. [Form Select](#form-select)
4. [Card](#card)
5. [Badge / Status Indicator](#badge--status-indicator)
6. [Alert](#alert)
7. [Stat Card](#stat-card)
8. [Table with Actions](#table-with-actions)
9. [Empty State](#empty-state)
10. [Loading State](#loading-state)

---

## Button

### Purpose
Primary interactive element. Used for form submission, navigation, and actions.

### Variants
- **Primary**: Call-to-action (submit, confirm)
- **Secondary**: Alternate action (cancel, back)
- **Tertiary**: Low-emphasis link-style
- **Danger**: Destructive action (delete, reject)

### HTML Markup

```html
<!-- Primary Button -->
<button type="submit" class="button-primary">
  Upload Document
</button>

<!-- Secondary Button -->
<button type="button" class="button-secondary">
  Cancel
</button>

<!-- Danger Button -->
<button type="button" class="button-danger">
  Reject
</button>

<!-- With Loading State (optional icon class) -->
<button type="submit" class="button-primary" aria-busy="true">
  <span class="spinner"></span> Processing...
</button>

<!-- Disabled State -->
<button type="submit" class="button-primary" disabled>
  Submit
</button>
```

### CSS Classes
```
.button-primary      /* Green/teal gradient, white text */
.button-secondary    /* Light teal background, teal text */
.button-danger       /* Light red background, red text */
.button-small        /* Smaller padding variant */
```

### Accessibility
- [ ] Button has visible text label (no icon-only buttons without aria-label)
- [ ] `:focus-visible` outline applied (blue outline, 2px)
- [ ] Hover state changes background color (visual feedback)
- [ ] Disabled state uses `disabled` attribute (not just CSS class)
- [ ] For loading state, add `aria-busy="true"` and `aria-label="Processing"`

### Details
- **Padding**: 13px 18px (primary), 10px 14px (small)
- **Border radius**: 999px (full pill shape)
- **Transition**: 150ms ease-in-out on background + transform
- **Hover feedback**: Subtle `translateY(-1px)` + color shift
- **Font**: Inherit from body (Space Grotesk)
- **Touch target**: 44px minimum height (44x44 for touch devices)

### States

| State | Background | Color | Outline | Cursor |
|-------|------------|-------|---------|--------|
| Default | Teal gradient | White | None | pointer |
| Hover | Darker teal | White | None | pointer |
| Focus | Teal gradient | White | 2px blue outline | pointer |
| Active | Darkest teal | White | None | pointer |
| Disabled | Gray 200 | Gray 500 | None | not-allowed |

---

## Text Input

### Purpose
Collect user-entered text (email, password, search, comments).

### HTML Markup

```html
<!-- Email Input -->
<label>
  <span>Email Address</span>
  <input 
    type="email" 
    name="email" 
    placeholder="name@firm.com"
    required 
    aria-describedby="email-hint"
  >
  <small id="email-hint">We'll never share your email.</small>
</label>

<!-- Password Input with Show/Hide (Phase 2+) -->
<label>
  <span>Password</span>
  <div class="input-group">
    <input 
      type="password" 
      name="password" 
      placeholder="Enter your password"
      required 
    >
    <button type="button" class="button-ghost" aria-label="Show password">👁</button>
  </div>
</label>

<!-- With Error State -->
<label aria-invalid="true">
  <span>Document Upload</span>
  <input 
    type="file" 
    name="file" 
    accept=".pdf,.png,.jpg"
    aria-describedby="file-error"
  >
  <small id="file-error" class="text-error">File must be PDF or image.</small>
</label>

<!-- Disabled State -->
<label>
  <span>Reference ID</span>
  <input 
    type="text" 
    value="AUTO-GENERATED" 
    disabled 
  >
</label>
```

### CSS Classes
```
.form-input          /* Base styling for all inputs */
```

### Accessibility
- [ ] Label associated with input via `<label for="id">` or label nesting
- [ ] `aria-describedby` links error/hint text to input
- [ ] `aria-invalid="true"` on error state
- [ ] `:focus-visible` outline applied (blue, 2px, 2px offset)
- [ ] Placeholder is hint, not label (always show label)
- [ ] Error message is red text (`color: var(--color-error-text)`)
- [ ] Minimum 44px touch target (padding + font size)

### Details
- **Padding**: 14px 16px
- **Border**: 1px solid `rgba(31, 27, 22, 0.14)`
- **Background**: `rgba(255, 255, 255, 0.85)` (frosted glass effect)
- **Border radius**: 16px
- **Font size**: Inherit (1rem)
- **Placeholder color**: Muted gray, 70% opacity

### States

| State | Border | Background | Outline | Notes |
|-------|--------|------------|---------|-------|
| Default | Gray 200 | White 85% | None | Clear, readable |
| Focus | Accent (teal) | White 90% | 2px blue outline | User input |
| Error | Error red | Error light 12% | 2px error red | `aria-invalid="true"` |
| Disabled | Gray 200 | Gray 100 | None | `opacity: 0.6` |

---

## Form Select

### Purpose
Dropdown menu for predefined options (role, document type, status filter).

### HTML Markup

```html
<!-- Role Selection -->
<label>
  <span>Assign Role</span>
  <select name="role" required aria-label="User role">
    <option value="">-- Select a role --</option>
    <option value="uploader">Uploader</option>
    <option value="reviewer">Reviewer</option>
    <option value="admin">Admin</option>
  </select>
</label>

<!-- With Grouping (Phase 2+) -->
<label>
  <span>Filter by Status</span>
  <select name="status">
    <option value="">All Statuses</option>
    <optgroup label="Document">
      <option value="uploaded">Uploaded</option>
      <option value="processing">Processing</option>
    </optgroup>
    <optgroup label="Review">
      <option value="needs_review">Needs Review</option>
      <option value="approved">Approved</option>
    </optgroup>
  </select>
</label>
```

### CSS Classes
```
.form-select         /* Base styling for all selects */
```

### Accessibility
- [ ] Label associated with select
- [ ] First option is placeholder or empty (helps screen readers)
- [ ] `:focus-visible` outline applied
- [ ] Disabled options use `disabled` attribute
- [ ] `aria-label` for screen reader context if needed

### Details
- **Styling**: Same as text input (border, padding, border-radius)
- **Font**: Inherit
- **Appearance**: Use native browser select (no custom styling needed for Phase 1)

---

## Card

### Purpose
Container for grouped content (section, form, information block).

### HTML Markup

```html
<!-- Basic Card -->
<section class="card">
  <h2>Upload Document</h2>
  <p class="muted">Send a PDF through the production pipeline.</p>
  <!-- Content here -->
</section>

<!-- Card with Icon Header (Phase 2+) -->
<article class="card">
  <header class="card-header">
    <span class="card-icon">📄</span>
    <h3>Document Details</h3>
  </header>
  <div class="card-body">
    <!-- Content -->
  </div>
</article>

<!-- Elevated Card (for priority content) -->
<div class="card card-elevated">
  <h3>Urgent Review Needed</h3>
  <p>2 documents awaiting your review.</p>
</div>
```

### CSS Classes
```
.card              /* Base card with glassmorphism */
.card-elevated     /* Increased shadow for emphasis */
.card-header       /* Optional header section */
.card-body         /* Optional content wrapper */
.card-footer       /* Optional footer with actions */
```

### Accessibility
- [ ] Use semantic elements (`<section>`, `<article>`, `<header>`, `<footer>`)
- [ ] Heading hierarchy preserved (h2, h3, etc.)
- [ ] No focus required (passive content container)

### Details
- **Background**: `rgba(255, 252, 246, 0.88)` (semi-transparent)
- **Backdrop filter**: `blur(14px)` (glassmorphism)
- **Border**: 1px solid `rgba(31, 27, 22, 0.12)`
- **Border radius**: 24px
- **Box shadow**: `var(--shadow-2xl)`
- **Padding**: 28px

---

## Badge / Status Indicator

### Purpose
Display short labels for status, role, or confidence level. Non-interactive.

### HTML Markup

```html
<!-- Success Badge (Approved) -->
<span class="badge badge-success" aria-label="Status: Approved">
  Approved
</span>

<!-- Warning Badge (Needs Review) -->
<span class="badge badge-warning" aria-label="Status: Needs Review">
  Needs Review
</span>

<!-- Error Badge (Rejected) -->
<span class="badge badge-error" aria-label="Status: Rejected">
  Rejected
</span>

<!-- Info Badge (Role or Tag) -->
<span class="badge badge-info">Admin</span>

<!-- Confidence Score with Icon (Phase 2+) -->
<span class="confidence-score high" aria-label="High confidence">
  <span class="confidence-icon">✓</span>
  High
</span>

<span class="confidence-score medium" aria-label="Medium confidence">
  <span class="confidence-icon">!</span>
  Medium
</span>

<span class="confidence-score low" aria-label="Low confidence">
  <span class="confidence-icon">⚠</span>
  Low
</span>
```

### CSS Classes
```
.badge              /* Base badge styling */
.badge-success      /* Green/teal badge */
.badge-warning      /* Amber/orange badge */
.badge-error        /* Red badge */
.badge-info         /* Blue badge */
.badge-neutral      /* Gray badge */
.confidence-score   /* Confidence display (high, medium, low) */
```

### Accessibility
- [ ] Use `aria-label` for screen readers to explain meaning
- [ ] Color + text used together (never color alone)
- [ ] High contrast (4.5:1 minimum for normal text, 3:1 for large text)

### Details
- **Padding**: 4px 8px
- **Border radius**: 999px (pill)
- **Font size**: 12px
- **Font weight**: 500 (medium)
- **Text transform**: uppercase
- **Letter spacing**: 0.06em (wide)
- **Whitespace**: `nowrap` (prevent wrapping)

---

## Alert

### Purpose
Display inline messages (error, success, info, warning) to user.

### HTML Markup

```html
<!-- Error Alert -->
<div class="alert alert-error" role="alert">
  <strong>Upload failed:</strong> File size exceeds 10MB limit.
</div>

<!-- Success Alert -->
<div class="alert alert-success" role="alert">
  Document processed successfully. Ready for review.
</div>

<!-- Info Alert -->
<div class="alert alert-info" role="alert">
  <span class="sr-only">Information:</span>
  Your invite expires on April 24, 2026. Set your password now.
</div>

<!-- Warning Alert (Phase 2+) -->
<div class="alert alert-warning" role="alert">
  Low confidence extraction (62%). Manual review recommended.
</div>
```

### CSS Classes
```
.alert              /* Base alert styling */
.alert-error        /* Red background, red text */
.alert-success      /* Green background, green text */
.alert-info         /* Blue background, blue text */
.alert-warning      /* Amber background, amber text */
```

### Accessibility
- [ ] `role="alert"` announced immediately to screen readers
- [ ] High contrast text (4.5:1 minimum)
- [ ] Icon + text (color not sole indicator)
- [ ] Use `.sr-only` for context if icon-only

### Details
- **Padding**: 14px 16px
- **Border radius**: 16px
- **Font size**: 0.95rem
- **Margin bottom**: 18px
- **Background**: Semantic color light variant (e.g., `var(--color-error-light)`)
- **Text color**: Semantic color text variant (e.g., `var(--color-error-text)`)

---

## Stat Card

### Purpose
Display a metric or statistic (document count, pending review, etc.) in dashboard.

### HTML Markup

```html
<article class="stat-card">
  <span class="stat-label">Total Documents</span>
  <strong class="stat-value">42</strong>
</article>

<article class="stat-card">
  <span class="stat-label">Pending Review</span>
  <strong class="stat-value">5</strong>
</article>

<article class="stat-card stat-card-highlight">
  <span class="stat-label">Approved This Week</span>
  <strong class="stat-value">28</strong>
</article>
```

### CSS Classes
```
.stat-card           /* Base stat card */
.stat-card-highlight /* For emphasized metric */
.stat-label          /* Label text (muted gray) */
.stat-value          /* Large number display */
```

### Accessibility
- [ ] Semantic `<article>` element
- [ ] Label is descriptive (screen reader understands metric)
- [ ] Value is bold/large (visual emphasis)

### Details
- **Padding**: 22px
- **Background**: Card styling (same as `.card`)
- **Label font size**: Small (var(--font-size-sm))
- **Label color**: Muted gray
- **Value font size**: 2rem (large, readable)
- **Value font weight**: Bold (700)

---

## Table with Actions

### Purpose
Display row-based data (document list, user list) with inline status and actions.

### HTML Markup

```html
<div class="table-wrap">
  <table>
    <caption class="sr-only">Recent documents and their status</caption>
    <thead>
      <tr>
        <th scope="col">Document Name</th>
        <th scope="col">Status</th>
        <th scope="col">Confidence</th>
        <th scope="col">Uploaded</th>
        <th scope="col">Actions</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>2024 W-2 - ABC Corp.pdf</strong></td>
        <td><span class="badge badge-warning">Needs Review</span></td>
        <td><span class="confidence-score medium">68%</span></td>
        <td>Apr 15, 2026</td>
        <td>
          <button class="button-small" aria-label="Approve 2024 W-2 - ABC Corp.pdf">Approve</button>
          <button class="button-small button-secondary" aria-label="View details for 2024 W-2 - ABC Corp.pdf">View</button>
        </td>
      </tr>
      <tr>
        <td><strong>1099-NEC - Freelance.pdf</strong></td>
        <td><span class="badge badge-success">Approved</span></td>
        <td><span class="confidence-score high">95%</span></td>
        <td>Apr 14, 2026</td>
        <td>
          <button class="button-small button-secondary" aria-label="View details for 1099-NEC - Freelance.pdf">View</button>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

### CSS Classes
```
.table-wrap         /* Scrollable wrapper for mobile */
table                /* Base table */
th                   /* Header cell (uppercase, muted) */
td                   /* Data cell */
```

### Accessibility
- [ ] `<caption>` describes table purpose (or use `aria-label`)
- [ ] `<th scope="col">` for column headers
- [ ] `<th scope="row">` for row headers if applicable
- [ ] Action buttons have descriptive `aria-label` (not just "Edit", but "Edit [row name]")
- [ ] Table is keyboard navigable (Tab through buttons)
- [ ] `.table-wrap` is horizontally scrollable on mobile (preserves data)

### Details
- **Padding**: 14px 12px (cells)
- **Border**: Bottom border 1px solid between rows
- **Header font size**: 0.84rem
- **Font transformation**: Uppercase
- **Letter spacing**: 0.06em (wide)
- **Text alignment**: Left

---

## Empty State

### Purpose
Friendly message when no data is available (no documents, no search results, etc.).

### HTML Markup

```html
<!-- Empty Document List -->
<div class="empty-state">
  <p>No documents yet.</p>
  <p class="muted">Upload your first tax document to get started.</p>
  <button class="button-primary" onclick="location.href='#upload-section'">Upload Document</button>
</div>

<!-- Empty Review Queue -->
<div class="empty-state">
  <p><strong>All caught up!</strong></p>
  <p class="muted">No documents need review right now. Check back later.</p>
</div>

<!-- No Search Results -->
<div class="empty-state">
  <p>No results for "<strong>xyz.pdf</strong>"</p>
  <p class="muted"><a href="/documents">Clear filters</a> to see all documents.</p>
</div>
```

### CSS Classes
```
.empty-state        /* Container for empty state */
.muted              /* Secondary text (gray) */
```

### Accessibility
- [ ] Clear, friendly message (not just blank space)
- [ ] CTA button to next action (upload, clear filters, etc.)
- [ ] Uses semantic elements (`<p>`, `<button>`)

### Details
- **Text alignment**: Center
- **Padding**: 22px
- **Color**: Muted gray for secondary text
- **Font size**: Normal (1rem)

---

## Loading State

### Purpose
Visual feedback while content is loading (upload progress, document fetch, etc.).

### HTML Markup

```html
<!-- Spinner Icon (Inline) -->
<button class="button-primary" aria-busy="true">
  <span class="spinner"></span> Processing...
</button>

<!-- Skeleton Loader (Table Placeholder, Phase 2+) -->
<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th scope="col">Document Name</th>
        <th scope="col">Status</th>
        <th scope="col">Actions</th>
      </tr>
    </thead>
    <tbody>
      <tr class="skeleton">
        <td class="skeleton-line" style="width: 60%;"></td>
        <td class="skeleton-line" style="width: 40%;"></td>
        <td class="skeleton-line" style="width: 30%;"></td>
      </tr>
      <tr class="skeleton">
        <td class="skeleton-line" style="width: 55%;"></td>
        <td class="skeleton-line" style="width: 45%;"></td>
        <td class="skeleton-line" style="width: 32%;"></td>
      </tr>
    </tbody>
  </table>
</div>

<!-- Upload Progress Bar (Phase 2+) -->
<div class="progress-bar">
  <div class="progress-fill" style="width: 45%;" aria-valuenow="45" aria-valuemin="0" aria-valuemax="100">
    Uploading: 45%
  </div>
</div>
```

### CSS Classes
```
.spinner             /* Animated rotation spinner */
.skeleton            /* Placeholder row styling */
.skeleton-line       /* Placeholder text line */
.progress-bar        /* Upload/processing progress indicator */
.progress-fill       /* Filled portion of progress */
```

### Accessibility
- [ ] Use `aria-busy="true"` on loading element
- [ ] Progress bars use `role="progressbar"` with `aria-valuenow`, `aria-valuemin`, `aria-valuemax`
- [ ] Spinner is purely decorative; don't announce it (or use `aria-hidden="true"`)
- [ ] Include text label ("Processing...", "45% uploaded")

### Details
- **Spinner animation**: 360° rotation, 1s infinite, linear timing
- **Spinner color**: Accent teal (`var(--color-success)`)
- **Spinner size**: 1em (inherit font size)
- **Progress bar height**: 8px
- **Progress fill color**: Accent teal

---

## Implementation Checklist (Phase 2)

Use this checklist when building each component in CSS + HTML:

- [ ] HTML markup validated (no semantic errors)
- [ ] CSS classes match spec (no typos, consistent naming)
- [ ] Token variables used (colors, spacing, radius, shadows)
- [ ] Focus states tested (keyboard Tab through all interactive elements)
- [ ] Hover states visible (color or shadow change)
- [ ] Disabled state clear (opacity, cursor: not-allowed)
- [ ] Mobile responsive (tested at 320px, 768px, 1024px)
- [ ] Contrast ratio ≥ 4.5:1 for normal text (WCAG AA)
- [ ] Touch targets ≥ 44x44px (for buttons, inputs)
- [ ] Color not sole indicator (use text + color, icon + color)
- [ ] Screen reader tested (NVDA or Mac VoiceOver)
- [ ] No console errors or warnings
- [ ] Component test page created (reference for QA)

---

## Next Steps (Phase 2)

1. Build all 10 components in CSS (add to `static/styles.css`)
2. Create test template (`templates/component-library.html`) showing all variants
3. Test each component:
   - Browser test (Chrome, Firefox, Safari)
   - Accessibility audit (keyboard + screen reader)
   - Mobile responsive
4. Document any deviations from this spec
5. Get approval before shipping to production
