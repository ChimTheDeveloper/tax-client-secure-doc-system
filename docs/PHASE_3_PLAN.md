# Phase 3: Role-Based Refinement & Feature Screens
**Date**: April 18, 2026  
**Status**: Ready to Start (After Phase 2 approval)  
**Duration**: 2 weeks (12 days active work, 4 days QA)

---

## Executive Summary

Phase 3 introduces **role-based personalization** and **advanced form interactions**. Users will see customized dashboards per role (uploader, reviewer, admin), forms will have real-time validation, and we'll add mobile-first navigation.

**Key Goals**:
- Personalized workflows per role
- Form validation (real-time + submit)
- Password strength indicator
- Mobile navigation (hamburger)
- Advanced table features (sorting, pagination)
- Review queue optimization

---

## Phase 3 Scope (High Priority)

### 1. Dashboard Role-Based Views (NEW)

#### Uploader Dashboard
**Purpose**: User who uploads documents

**Content**:
- My Uploads (list: filename, status, confidence, date)
- Quick Stat: "3 processed, 1 awaiting review, 0 errors"
- Upload Document (drag-drop + file picker)
- Recent Activity (timeline of uploads)

**Template**: `dashboard-uploader.html` (conditional in main dashboard.html)

#### Reviewer Dashboard
**Purpose**: User who validates extractions

**Content**:
- Review Queue (sorted by confidence ASC: low confidence first)
- Quick Stat: "5 ready for review, 12 completed this week"
- Approve/Reject inline (with confidence reason)
- Document Detail modal (inline expansion)

**Template**: `dashboard-reviewer.html` (conditional)

#### Admin Dashboard
**Purpose**: Team management + systems overview

**Content**:
- Team Overview (users, roles, active sessions)
- Systems Health (documents processed, errors, avg confidence)
- Configuration (confidence threshold, retention policy)
- Audit Log search

**Template**: `dashboard-admin.html` (conditional)

**Implementation**:
```python
# In src/api/main.py, before rendering:
if subject.role == "admin":
    template = "dashboard-admin.html"
elif subject.role == "reviewer":
    template = "dashboard-reviewer.html"
else:
    template = "dashboard-uploader.html"
```

---

### 2. Form Validation System

#### Real-Time Validation (On Change)
- Email: must be valid format, show inline error if invalid
- Password: min 10 chars, show strength indicator
- File upload: check size before submit, show file count
- Name: alphanumeric + spaces only

#### Submit Validation (On Form Submit)
- All required fields filled
- Password confirmation matches
- File size within limit
- Custom errors in alert bar

#### Validation UI Components

**Input Error State**:
```html
<label aria-invalid="true">
  <span>Email</span>
  <input type="email" aria-invalid="true" aria-describedby="email-error">
  <small id="email-error" class="form-error">Invalid email format</small>
</label>
```

**Password Strength Meter**:
```html
<div class="password-strength">
  <progress value="30" max="100"></progress>
  <small>Weak password - Add uppercase letters</small>
</div>
```

---

### 3. Document Review Queue (NEW SCREEN)

**Purpose**: Dedicated interface for reviewers

**URL**: `/app/review-queue`

**Features**:
- List of documents with status "needs_review"
- Sorted by confidence (lowest first for priority)
- Inline quick-view of extracted fields
- Approve/Reject with notes
- Filters: confidence range, document type, date

**Table Structure**:
| Document | Type | Confidence | Extracted Fields | Uploaded | Actions |
|----------|------|------------|------------------|----------|---------|
| W-2.pdf | W-2 | 62% (⚠️) | SSN, EIN, Wages | 2h ago | [Expand] [Approve] [Reject] |

**Expand Row**:
Shows extracted key-value pairs with confidence per field:
- SSN: 75% high confidence
- EIN: 85% high confidence  
- Wages: 42% low confidence
- Federal Tax: 55% medium confidence

---

### 4. Mobile Navigation (Hamburger Menu)

**Trigger**: At 768px breakpoint and below

**Menu Contents** (conditional on role):
- Dashboard
- (If reviewer) Review Queue
- (If uploader) My Documents
- (If admin) Team Management
- Settings
- Logout

**Implementation**:
```html
<button class="hamburger" aria-label="Toggle navigation menu" aria-expanded="false">
  <span></span><span></span><span></span>
</button>

<nav class="mobile-nav" aria-hidden="true">
  <a href="/app">Dashboard</a>
  <a href="/app/review-queue">Review Queue</a>
  <a href="/app/settings">Settings</a>
  <form action="/auth/logout" method="post">
    <button type="submit">Log Out</button>
  </form>
</nav>
```

---

### 5. Advanced Table Features

#### Sorting
- Click column header to sort ascending/descending
- Visual indicator (↑ or ↓) on active column
- Multiple columns sortable (shift+click)

#### Pagination
- Show 10, 25, 50 documents per page
- Navigation: Previous, page numbers, Next
- Total count: "Showing 1-10 of 42 documents"

#### Filtering
- Filter by status (approved, needs review, rejected)
- Filter by confidence (high, medium, low)
- Filter by date range (Calendar picker, Phase 2.5)

---

## Phase 3 Deliverables Checklist

### By Day 3 (Role-Based Dashboards)
- [ ] Create `dashboard-uploader.html`
- [ ] Create `dashboard-reviewer.html`
- [ ] Create `dashboard-admin.html`
- [ ] Update Python route to serve correct template per role
- [ ] CSS for role-specific layouts
- [ ] Test all 3 roles see correct content

### By Day 6 (Form Validation)
- [ ] Add real-time validation CSS (`.input-error`, `.input-valid`)
- [ ] Create validation JavaScript snippet (minimal, progressive enhancement)
- [ ] Implement password strength meter UI
- [ ] Test on login, invite, upload, invite-user forms

### By Day 9 (Review Queue + Mobile Nav)
- [ ] Create `/app/review-queue` route + template
- [ ] Review queue table (semantic HTML, sorting ready)
- [ ] Hamburger menu + mobile nav CSS
- [ ] JavaScript for menu toggle
- [ ] Test menu at 768px and below

### By Day 12 (Quality Assurance)
- [ ] Accessibility audit (Lighthouse ≥95)
- [ ] Keyboard navigation on all new screens
- [ ] Screen reader test (NVDA/VoiceOver)
- [ ] Mobile device test (iPhone, Android)
- [ ] Cross-browser test (Chrome, Firefox, Safari)
- [ ] Performance audit (Lighthouse ≥90)

---

## Phase 3 Technical Details

### Template Structure
```
templates/
├── base.html                   (no change)
├── dashboard.html              (main decision logic, role check)
├── dashboard-uploader.html     (role-specific content)
├── dashboard-reviewer.html     (role-specific content)
├── dashboard-admin.html        (role-specific content)
├── review-queue.html           (new: reviewer-only)
├── component-library.html      (reference, no change)
├── login.html                  (no change, maybe form validation)
└── accept_invite.html          (add password strength meter)
```

### CSS Additions (~300 lines)
- `.password-strength` (progress bar + text)
- `.input-error`, `.input-valid` (validation states)
- `.hamburger` (button + animation)
- `.mobile-nav` (offscreen menu, slide-in)
- `.table-sortable` (header hover, sort indicators)
- `.pagination` (buttons, active state)
- `.filter-bar` (filter badges, remove button)

### JavaScript Minimal (~200 lines, progressive enhancement)
- Hamburger toggle (show/hide menu)
- Form validation (real-time email, password checks)
- Password strength calculator
- Table sorting (click header)
- Mobile detection (show/hide nav at breakpoint)
- **No frameworks**: Vanilla JS only, VanillaJS or no JS fallback

---

## Mockup: Uploader Dashboard

```
┌─────────────────────────────────────────────┐
│ [≡] Tax Intelligence Workspace               │ (hamburger menu on mobile)
│                                             │
│ Welcome, Alice                              │
│ Role: [Uploader]                            │
│                                    [Log Out] │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ Quick Stats:                                │
│ ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│ │3          │  │1         │  │0          │   │
│ │Processed  │  │Awaiting  │  │Errors    │   │
│ │           │  │Review    │  │          │   │
│ └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ Upload New Document                         │
│ ┌──────────────────────────────────────┐   │
│ │ Drag PDF here or click to select      │   │
│ │ Max 10MB                              │   │
│ └──────────────────────────────────────┘   │
│                        [Upload and Process] │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ Your Recent Uploads                         │
│ ┌──────────────────┬────┬────┬──────┐      │
│ │File              │Type│Conf│Status│      │
│ ├──────────────────┼────┼────┼──────┤      │
│ │2024-W-2.pdf      │W-2 │ 95%│ ✓    │      │
│ │1099-NEC.pdf      │NEC │ 82%│ ✓    │      │
│ │State-Return.pdf  │ST  │ 48%│ ⚠    │      │
│ └──────────────────┴────┴────┴──────┘      │
└─────────────────────────────────────────────┘
```

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| Role-based logic breaks for some users | Medium | High | Test all 3 roles day 3 |
| Form validation JS has bugs | Medium | Medium | Vanilla JS, no external deps |
| Mobile menu not keyboard accessible | Low | High | Test hamburger + keyboard nav |
| Table sorting breaks on large datasets | Low | High | Limit to client-side for now (Phase 4 backend sort) |
| Performance regression from new JS | Low | Medium | Minimal JS, lazy-load if needed |

---

## Success Metrics (Phase 3 Exit)

| Metric | Target | How We Measure |
|--------|--------|-----------------|
| Role-based dashboards work | 3/3 roles | Test all roles see correct content |
| Form validation prevents errors | 90% reduction | Manual test: submit invalid data |
| Password strength useful | Users understand | Manual: Check if meter is informative |
| Mobile nav keyboard accessible | ✓ | Test hamburger + Tab through menu |
| Table sorting works | 5/5 columns | Test sorting on each column |
| Lighthouse accessibility | ≥95 | Run audit on all 3 dashboards |
| No console errors | 0 | Check DevTools on all pages |

---

## Phase 3 Timeline

```
Day 1–2   │ Role-based dashboards (HTML + CSS)
Day 3     │ Test role logic, Python routing
Day 4–5   │ Form validation (CSS + minimal JS)
Day 6     │ Password strength meter UI
Day 7–8   │ Review queue screen + mobile nav
Day 9     │ Table sorting + pagination (UI)
Day 10–11 │ Cross-browser + accessibility testing
Day 12    │ Final QA + bug fixes
───────────────────────────────────────────
Day 13–14 │ Gate 3 review + phase 4 planning
```

---

## Questions for Phase 3

1. **Role-based filtering**: Should non-admin users see admin sections greyed out, or hidden entirely?
   - **Recommendation**: Hidden entirely (simpler UX)

2. **Password strength**: Use visual meter (progress bar), numeric score, or text description?
   - **Recommendation**: Progress bar + text ("Weak", "Good", "Strong")

3. **Review queue**: One screen per role, or shared with role-specific filters?
   - **Recommendation**: Shared screen, role selector if user has multiple roles (Phase 4)

4. **Mobile hamburger**: Side drawer or full-screen overlay?
   - **Recommendation**: Side drawer (less disruptive, standard pattern)

5. **Pagination**: Show 10/25/50 per page, or infinite scroll?
   - **Recommendation**: Pagination (better for accessibility, faster)

---

## Dependencies

- ✅ Phase 1: Design tokens + component specs (DONE)
- ✅ Phase 2: Core components + templates (DONE)
- 🟠 Phase 3: Role-based logic + advanced forms (READY TO START)
- ⏳ Phase 4: Polish + dark mode (after Phase 3)

---

## Sign-Off Checklist (Ready to Proceed)

- [x] Phase 2 complete + approved
- [x] No blocking issues from Phase 2
- [x] Phase 3 scope clearly defined
- [x] Mockups prepared (see above)
- [x] Risk mitigation identified
- [x] Success metrics defined
- [ ] **Phase 3 kickoff approval** (awaiting green light)

---

**Ready to start Phase 3?** 🚀
