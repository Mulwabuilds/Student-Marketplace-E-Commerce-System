# Sprint 1 — Database Design & Implementation (Week 1)

**Team:** Lee · Ian · Kevin
**Repo:** fresh, fork-based workflow — each dev works on their own fork, opens Pull Requests (PRs) against `main`
**Sync cadence:** async check-in every 2 days (end of Day 1, Day 3, Day 5) + full team PR review on Day 7
**Definition of Done (per ticket, unless stated otherwise):** migration created and applies cleanly + model registered in Django admin + admin page loads and a record can be created through it
**Deferred to Sprint 2 (explicit scope cut):** automated tests (`pytest` / Django `TestCase`), the `Listing` search-index table (FLAG 2), `Category.parent_category_id` subcategories (FLAG 10)

App layout (per current Django domain-grouping convention):
```
apps/
├── accounts/   # User, Profile
├── catalog/    # Category, CampusLocation
├── goods/      # Good, GoodImage
└── services/   # Service, ServiceImage
```

---

## Day 1 (Mon) — Foundation

> **T1 must get an expedited sanity-check merge same day** (not the full Day-7 review) — everything on Day 2 branches off it. See flag above if you'd rather not special-case this.

### T1 — Project scaffold + `accounts` app + `User` model
- **Labels:** `foundation`, `accounts`, `priority:blocking`
- **Assignee:** Lee 
- **Depends on:** nothing (first ticket)
- **Description:** Initialize the Django project (`django-admin startproject`), configure `.env`-based settings (`django-environ` or `python-decouple`), create the `apps/accounts` app, implement a custom `User` model (subclassing `AbstractUser`) with: `email` (unique, `CHECK` constraint enforcing `@kabarak.ac.ke` domain at the DB level), `otp_code_hash`, `otp_expires_at`, `is_email_verified`. Wire `AUTH_USER_MODEL` in settings before the first migration (cannot be changed later without a painful reset).
- **Acceptance criteria:** `python manage.py migrate` runs clean on a fresh PostgreSQL database; `User` is registered in Django admin; a superuser can be created and logged into `/admin`; attempting to create a user with a non-`@kabarak.ac.ke` email fails at the database level, not just in a form.
- **Merge note:** expedited review — confirm it runs, then merge, so T4/T5/T6 aren't blocked.

### T2 — Environment setup + `catalog` app + `CampusLocation`
- **Labels:** `foundation`, `catalog`, `onboarding`
- **Assignee:** Ian 
- **Depends on:** nothing
- **Description:** Get local PostgreSQL running, Django connected via `.env`, confirm `manage.py runserver` works. Create `apps/catalog`, implement `CampusLocation` (`id`, `name` unique). Seed 3–5 placeholder rows (real Kabarak locations still needed from the team — FLAG 8 unresolved).
- **Acceptance criteria:** migration applies; `CampusLocation` visible and editable in admin.

### T3 — `Category` model
- **Labels:** `foundation`, `catalog`, `onboarding`
- **Assignee:** Kevin 
- **Depends on:** nothing (can share `apps/catalog` with T2 — coordinate to avoid both editing the same migration file simultaneously)
- **Description:** Implement `Category` (`id`, `name` unique) in `apps/catalog`. No `parent_category_id` — deferred (FLAG 10). Seed the six known categories: Books, Electronics, Clothing, Crafts, Furniture, Services.
- **Acceptance criteria:** migration applies; `Category` visible and editable in admin; six seed rows present.

---

## Day 2 (Tue) — Core listing entities

### T4 — `Profile` model
- **Labels:** `accounts`
- **Assignee:** Lee 
- **Depends on:** T1 (merged), T2 (merged)
- **Description:** `Profile` in `apps/accounts` — one-to-one with `User`, FK to `CampusLocation`, `phone_number`, `bio` (free text), `profile_photo_url`.
- **Acceptance criteria:** migration applies; admin shows Profile inline on the User admin page or as its own registered model; a Profile can be created linking an existing User and CampusLocation.

### T5 — `Good` model
- **Labels:** `goods`
- **Assignee:** Ian 
- **Depends on:** T1 (merged), T3 (merged)
- **Description:** `Good` in new `apps/goods` — FK `seller`→`User`, FK `category`→`Category`, `title`, `description`, `price` (`DECIMAL(10,2)`, `CHECK price >= 0`), `condition` (`CHECK IN ('new','used')`), `status` (`CHECK IN ('available','unavailable')`, default `'available'`).
- **Acceptance criteria:** migration applies; admin registered; a Good can be created via admin referencing a real User and Category; inserting `price = -5` fails at the DB level.

### T6 — `Service` model
- **Labels:** `services`
- **Assignee:** Kevin 
- **Depends on:** T1 (merged), T3 (merged)
- **Description:** `Service` in new `apps/services` — same shape as `Good` minus `condition`.
- **Acceptance criteria:** migration applies; admin registered; a Service can be created via admin.

---

## Day 3 (Wed) — Images + shared API setup — **sync checkpoint**

### T7 — `GoodImage` model
- **Labels:** `goods`
- **Assignee:** Ian 
- **Depends on:** T5
- **Description:** `GoodImage` — FK `good`→`Good` (`ON DELETE CASCADE`), `image_url`, `uploaded_at`. Enforce max 15 images per Good in `clean()`/admin validation (not DB-enforceable — FLAG 6).
- **Acceptance criteria:** migration applies; admin registered as inline on Good or standalone; attempting a 16th image for the same Good is rejected with a clear error.

### T8 — `ServiceImage` model
- **Labels:** `services`
- **Assignee:** Kevin 
- **Depends on:** T6
- **Description:** Same as T7, scoped to `Service`.
- **Acceptance criteria:** same pattern as T7.

### T9 — Django REST Framework (DRF) project setup
- **Labels:** `foundation`, `api`, `priority:blocking`
- **Assignee:** Lee 
- **Depends on:** T1
- **Description:** Install `djangorestframework`, add to `INSTALLED_APPS`, configure default pagination, default permission classes, and a base `urls.py` API router. This unblocks Day 4's serializer/view tickets for everyone — no one should start writing DRF serializers before this merges.
- **Acceptance criteria:** `/api/` root loads (even empty); DRF browsable API renders.

**Sync checkpoint (end of Day 3):** confirm T1–T9 all merged before Day 4 starts. If T9 is late, Day 4 slips — flag immediately, don't wait for Day 5.

---

## Day 4 (Thu) — Serializers & views, round 1

### T10 — `accounts` API: registration, OTP, login, Profile
- **Labels:** `accounts`, `api`
- **Assignee:** Lee 
- **Depends on:** T4, T9
- **Description:** Registration endpoint (validates `@kabarak.ac.ke` email, generates + hashes OTP, sends it), OTP verification endpoint, login endpoint, Profile retrieve/update endpoint (`ModelViewSet` or `GenericAPIView` + mixins per DRF convention).
- **Acceptance criteria:** registering with a non-university email is rejected before hitting the DB; a valid registration produces a hashed OTP with an expiry; verifying the correct OTP sets `is_email_verified = True`; Profile endpoint returns/updates the logged-in user's own profile only.

### T11 — `goods` API: CRUD + image upload
- **Labels:** `goods`, `api`
- **Assignee:** Ian 
- **Depends on:** T7, T9
- **Description:** `GoodSerializer` + `ModelViewSet` for full CRUD, nested `GoodImageSerializer` for upload (respecting the 15-image cap at the serializer/view level too — belt and suspenders with T7's model-level check).
- **Acceptance criteria:** a seller can create/edit/delete their own Good via the API; a Good's images can be listed and added; a 16th image attempt returns a clear validation error, not a 500.

### T12 — `services` API: CRUD + image upload
- **Labels:** `services`, `api`
- **Assignee:** Kevin 
- **Depends on:** T8, T9
- **Description:** Mirrors T11 for `Service`/`ServiceImage`.
- **Acceptance criteria:** mirrors T11.

---

## Day 5 (Fri) — Catalog API, seed data, search — **sync checkpoint**

### T13 — `catalog` API: read-only Category + CampusLocation endpoints
- **Labels:** `catalog`, `api`
- **Assignee:** whoever finishes T11/T12 first (likely Kevin, since Service is the simpler slice)
- **Depends on:** T2, T3, T9
- **Description:** Read-only `ModelViewSet`s (`ReadOnlyModelViewSet`) exposing categories and campus locations for use in registration/listing forms.
- **Acceptance criteria:** both endpoints return seeded data.

### T14 — Cross-listing keyword search (`itertools.chain()`)
- **Labels:** `api`, `search`, `risk:overflow`
- **Assignee:** Lee 
- **Depends on:** T10, T11, T12
- **Description:** Search endpoint matching keyword against `Good`/`Service` `title`, `description`, `Category.name`, and seller `full_name`, combining both querysets via `itertools.chain()` per the confirmed FLAG 1 decision. Python-side pagination for v1 (the DB-view mitigation from FLAG 2 is explicitly out of scope this sprint).
- **Acceptance criteria:** a keyword search returns matching Goods and Services together, ranked/ordered consistently.
- **Risk flag:** this is the most architecturally awkward ticket in the sprint (see FLAG 1). If Day 4's tickets slip at all, **this is the one to let overflow into Sprint 2** — not the model/admin tickets, which are foundational for everything else.

### T15 — Seed data pass
- **Labels:** `catalog`, `data`
- **Assignee:** Ian 
- **Depends on:** T2, T3
- **Description:** Replace placeholder `CampusLocation` rows with the real list once supplied (still outstanding — FLAG 8). Confirm `Category` seed data matches Section 1.8/3.6.5 of the research paper exactly.
- **Acceptance criteria:** seed data reviewed by at least one other Ianefore Day 7.

---

## Day 6 (Sat) — Buffer, smoke test, overflow absorption

### T16 — End-to-end smoke check
- **Labels:** `qa`
- **Assignee:** all three, together or split by app
- **Depends on:** everything above
- **Description:** Fresh clone, fresh `migrate`, `createsuperuser`, and manually verify every model (`User`, `Profile`, `CampusLocation`, `Category`, `Good`, `GoodImage`, `Service`, `ServiceImage`) can be created and viewed through Django admin end to end. This is the manual substitute for the automated tests deferred to Sprint 2 — treat it as non-optional, not a nice-to-have.
- **Acceptance criteria:** a written checklist (one line per model) confirming pass/fail, attached to the PR review in T17.

- Buffer time for T14 if it hasn't landed — if it overflows, note it explicitly in the Day 7 review rather than merging something half-working.

---

## Day 7 (Sun) — Full team PR review

### T17 — Sprint review & merge
- **Labels:** `review`
- **Assignee:** all three
- **Depends on:** everything
- **Description:** All outstanding PRs reviewed together against the Definition of Done above. Anything not meeting it (including, retroactively, T1's expedited merge) gets fixed before final merge to `main`. Confirm which tickets (if any) roll into Sprint 2 — T14 is the most likely candidate.
- **Acceptance criteria:** `main` branch has migrations for all 8 models, all admin-registered, smoke-tested per T16.

---

## Summary table

| Day | Lee  | Ian  | Kevin  |
|---|---|---|---|
| 1 | T1 User + scaffold (expedited merge) | T2 CampusLocation + env setup | T3 Category + env setup |
| 2 | T4 Profile | T5 Good | T6 Service |
| 3 | T9 DRF setup | T7 GoodImage | T8 ServiceImage |
| 4 | T10 accounts API | T11 goods API | T12 services API |
| 5 | T14 search (risk: overflow) | T15 seed data | T13 catalog API |
| 6 | T16 smoke test (all) | T16 smoke test (all) | T16 smoke test (all) |
| 7 | T17 review & merge (all) | T17 review & merge (all) | T17 review & merge (all) |

**Likely overflow into Sprint 2:** T14 (search), and any of T10–T13 that slip if T9 lands late on Day 3.
