# Flags — Student Marketplace E-Commerce System

Open risks, ambiguities, and places where I made a default choice on your behalf. Review before implementation starts. Each item states the issue, the evidence, and the decision I need from you (or the default I applied).

---

## FLAG 1 — Goods/Services split makes cross-type search structurally harder

**Your decision (confirmed):** Two separate tables, `Good` and `Service`, rather than one `Listing` table with a type column.

**Why this needs a second look:** Module 4 (Product Search and Browsing) requires a single keyword search across category and seller name, spanning both goods and services. In Django, combining querysets from two different models requires either:
- `QuerySet.union()` — but this requires identical field sets/order between both querysets, disallows `ORDER BY` before the union, and breaks Django's normal `.filter()` chaining after the union (confirmed by Django's own ORM Cookbook and an open django-filter maintainer discussion on exactly this pattern).
- `itertools.chain()` — simpler, but loses database-level pagination and sorting; you paginate in Python instead of SQL, which doesn't scale well as listings grow.
- A Postgres `VIEW` that unions both tables — works well, but is *extra* schema surface: a view you must maintain in migrations alongside the two base tables.

**Net effect:** every "search all listings" or "browse by category across everything" query becomes measurably more complex than it would be with one shared table plus a `type` discriminator. Two-table designs are a legitimate choice when goods and services genuinely diverge in shape — and yours do diverge (services have no `condition` field) — but the cost shows up specifically in Module 4, which is a core deliverable.

**What I did:** Kept your two-table decision as instructed, and separately added a lightweight recommendation below (not required, your call) — see FLAG 2.

**Decision needed:** Confirm you're comfortable with search being implemented via `chain()` (simplest, Python-side pagination) rather than a database view, for the first version. This affects Sprint 4 effort.

---

## FLAG 2 — Optional mitigation: thin shared index

If FLAG 1's cost becomes a real problem once you're building Module 4, a low-disruption fix is a `Listing` table that stores only `id`, `listing_type` (`good`/`service`), `created_at` — with `Good` and `Service` each holding a one-to-one FK back to it. Search queries hit `Listing` first, then join out. This is **not built into the schema below** — flagging it as a future escape hatch, not adding speculative complexity now (YAGNI).

---

## FLAG 3 — Image support for `Service` listings is undefined

The research paper only says "upload product images" (Module 3), which was written before goods/services were split. You confirmed `ProductImage` (now `GoodImage`) for goods, max 15 images.

**Default I applied:** Added a matching `ServiceImage` table (max 15), for symmetry — e.g., a crochet tutoring service showing sample work. If services should have **no** images, this table should be dropped.

**Decision needed:** Confirm or reject `ServiceImage`.

---

## FLAG 4 — `status` enum (`active`/`sold`/`removed`) doesn't fit services semantically

"Sold" makes sense for a physical good; a service is booked, completed, or discontinued, not "sold." You approved this enum in the context of the original single-table design.

**Default I applied:** Reused the same three values on `Service.status` for consistency and to avoid scope creep, since you called it "pretty inclusive." Read `sold` as "no longer available" for services.

**Decision needed:** Confirm, or ask for a separate enum on `Service` (e.g. `active`/`unavailable`/`removed`).

---

## FLAG 5 — OTP (One-Time Password) stored in plaintext is a known weak point

You approved storing the OTP directly on the `User` table with TTL (Time To Live) handling — this matches the majority pattern I found in current Django implementation guides. However, several of the same sources explicitly note that **storing the OTP as plaintext is a common but weak practice**; a database leak exposes live, usable codes during their validity window.

**Default I applied:** Schema below stores `otp_code_hash` (hashed) instead of plaintext, plus `otp_expires_at`. This is a one-line change at the application layer (hash before save, compare hash on verify) — doesn't change your table structure or your "store in User table" decision, just hardens it.

**Decision needed:** Confirm hashing is fine, or explicitly say you want plaintext for simplicity (not recommended).

---

## FLAG 6 — 15-image cap is not DB-enforceable

Postgres has no native "max 15 child rows per parent" constraint. This must be enforced in the application/serializer layer (check count before insert) or via a trigger. A trigger is more robust (can't be bypassed by a bug in application code) but adds migration complexity for a student project.

**Default I applied:** Application-layer enforcement, documented as a rule, not a DB constraint. Flagging so it isn't forgotten during Module 3 implementation.

---

## FLAG 7 — Search field ambiguity, interpreted

You said "keyword search based on category and seller name" in response to a question asking whether search should be title/description-only, or also include seller/category. I've interpreted this as **additive** — search matches against `title`, `description`, `category.name`, AND `seller.full_name` — not a replacement of title/description. A pure category+seller-name search without title/description would be a strange product decision (you couldn't find "blue jacket" by typing "blue jacket").

**Decision needed:** Confirm this reading is correct.

---

## FLAG 8 — `CampusLocation` fixed list has no real values yet

You confirmed a fixed dropdown of campus locations, with free-text detail pushed to the user's bio. I have no authoritative list of actual Kabarak University campus zones/hostels, and I'm not going to invent specific real-world location names for your institution. The schema includes the table structure with **placeholder seed data** — you or a teammate need to supply the real list before this is usable.

---

## FLAG 9 — Email domain enforcement is app-layer, not DB-layer

Postgres can't natively validate "email must end in @kabarak.ac.ke" as a column constraint without a `CHECK` constraint using a regex — which Postgres *does* support (`CHECK (email ~ '@kabarak\.ac\.ke$')`). I've included this as a `CHECK` constraint in the schema rather than leaving it purely to Django form validation, since a DB-level guarantee is stronger than an application-level one and costs nothing extra.

**Decision needed:** Confirm you're fine with a DB-level `CHECK` constraint here (recommended), or prefer application-only validation for flexibility (e.g. if you ever whitelist a second domain).

---

## FLAG 10 — Subcategories: added a dormant column, not a feature

Per your instruction to flag subcategories for later, I added a nullable `parent_category_id` self-referencing column on `Category` now. It costs nothing today (stays null for every row) and avoids a schema migration + data backfill later. This is a low-risk future-proofing addition — not scope creep — but flagging it since you didn't explicitly ask for it.

---

## Session: Maximus's Sprint 2 build (Claude-assisted) — for Ian/Kevo

### Blocking — needs Kevo's decision
- **`Service` has no `seller` field.** Confirmed by reading the model directly (now in `apps/services/models.py`, moved from `apps/catalog`). Kevo's task doc assumes `service.seller` / `service.seller.profile` exist; they don't yet. This blocks the dashboard's services section (shows a "blocked" notice instead of listings — see `apps/marketplace/views.py::_service_has_seller()`, which checks at runtime and degrades gracefully rather than crashing) and any buyer-facing "contact the seller" display for a service.
- Once added (`seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='services')`), run `makemigrations services && migrate` — the dashboard will pick it up automatically, no other changes needed.

### Done this session — services app move
- Moved `Service`/`ServiceImage` out of `apps/catalog` into a new `apps/services` app (model-only move, no cross-app migration surgery needed since tables were empty).
- Fixed every import referencing `apps.catalog.models.Service`/`ServiceImage`: `apps/api/serializers.py`, `apps/api/views.py`, `apps/marketplace/views.py`.
- Registered `Service`/`ServiceImage` in Django admin (`apps/services/admin.py`) — these were never registered anywhere before, not a regression.
- Migrations: `catalog/0004_...` drops the two models, `services/0001_initial.py` recreates them; dependency order verified correct, `migrate` runs clean on a fresh DB.
- Ran `remove_stale_contenttypes` — cleaned the orphaned `catalog.service`/`catalog.serviceimage` content types + 4 auto permissions each. **If you have a persistent local dev DB, back it up before running this** — it cascade-deletes anything tied to those stale content types.
- **Team coordination:** everyone must `git pull` then `python manage.py migrate` before continuing.
- `Service.is_available` (bool) vs `Good.status` (choice field) are genuinely different shapes — `marketplace/views.py` branches on this; no unified filter expression across both models is possible as-is.

### Known issue I could NOT reproduce
- The "admin Add User form missing email field" open issue — rendered the actual add-user admin page via Django's test client against current `apps/accounts/admin.py`; the email field appears correctly. `add_fieldsets` already includes it and Django 5.2.16 handles it fine. Didn't touch `admin.py`. If still visibly broken in a browser, it's likely something else (cache, different symptom) — worth re-describing before anyone spends time on it.

### Still open / deliberately out of scope
- Goods/Services CRUD templates/views/forms (list, detail, create/edit/delete) — Iyaan/Kevo's territory, untouched.
- `browse.html` cards have **no "View details" link yet** — intentionally omitted rather than pointing at `goods:detail`/`services:detail` URL names that don't exist. Wire it in once those detail views land (marked with a comment in the template).
- Real `CampusLocation` seed data (still placeholder names).

### What landed (Maximus's steps)
- `Profile.is_open` field + migration.
- `GoodImage.image_url` → real `ImageField` + migration; fixed resulting breakage in `apps/goods/serializers.py` and `seed_data.py`.
- Generic placeholder image at `apps/marketplace/static/marketplace/img/placeholder.png` (browse-page `<img>` fallback + used by `seed_data.py`). Point a services seed command at the same file for visual parity.
- No-OTP register/login/logout/profile-edit (template-based), fully separate from existing DRF OTP endpoints under `/api/accounts/` (untouched).
- `apps/marketplace`: public `browse` (search/category/price/condition filters) + `dashboard` (seller's own goods; services blocked pending seller field).
- `templates/base.html`, Bootstrap 5 CDN, auth-aware navbar.
- Settings: `MEDIA_URL`/`MEDIA_ROOT`, project `TEMPLATES DIRS`, `LOGIN_URL`/`LOGIN_REDIRECT_URL`, `apps.services` + `apps.marketplace` added to `INSTALLED_APPS`.

Full flow tested end-to-end via Django's test client on a fresh migrated DB: register (valid + invalid email) → login session → profile edit incl. `is_open` toggle → dashboard → logout. All passed.

---

## Session: closing out everyone's flagged/incomplete tasks + no-CDN frontend rebuild

### Fixed — was genuinely broken or missing
1. **`Service.seller` added** (blocked since Sprint 1, flagged three times). Migration `services/0002_service_seller.py`. One-off default of `seller_id=1` applies ONLY to pre-existing rows on migrate -- if you already have real Service rows locally with a different intended owner, reassign via admin after migrating.
2. **`ServiceImage` upload wired up end-to-end** -- there was no form, no view handling, no way to attach a photo to a service at all. Added `ServiceImageForm` (`apps/services/forms.py`), wired seller assignment + ownership checks (`PermissionDenied` if `request.user != service.seller`, mirroring Iyaan's `UserPassesTestMixin` pattern) + image handling into `service_create`/`service_update` (`apps/services/views.py`). Verified: create a service with an image via the real form, confirm it displays on the detail page.
3. **Real bug in `apps/goods/models.py::GoodImage.clean()`**: called `self.good.images.count()`, but `GoodCreateView`/`GoodUpdateView` validate `image_form.is_valid()` before the `Good` exists, so this crashed with `RelatedObjectDoesNotExist` on literally every image upload attempt -- 100% reproducible, not an edge case. Fixed with a `self.good_id and ...` guard; the 15-image cap is still enforced (re-checked at actual `save()` once `good` is set). Confirmed by reproducing the crash first, then confirming the fix resolves it.
4. **Real bug in Iyaan's new goods templates**: `good.goodimage_set.first` was used everywhere, but `GoodImage.good` has `related_name='images'` -- that accessor doesn't exist, and Django templates fail silently on bad lookups, so uploaded images were just never appearing, with no error to notice. Fixed to `good.images.first` in all four goods templates.
5. **The `/api/goods/` duplicate-include bug is back for the second time** -- same root cause as last session (stale `include("apps.goods.urls")` in `apps/api/urls.py` from before goods became template views), reintroduced via a merge. Removed again. If this shows up a third time, the fix needs to happen on whichever branch keeps reintroducing it, not just on merge.
6. **Category seed data now matches the paper exactly** (Kevo's Step 4, never done -- only an ad-hoc `Category.objects.get_or_create(name='Appliances')` existed in `seed_data.py`, and "Appliances" isn't even one of the six the paper specifies). Added `apps/catalog/management/commands/seed_categories.py` seeding exactly `Books, Electronics, Clothing, Crafts, Furniture, Services` (confirmed verbatim by extracting text from both research paper `.docx` files, not guessed). Fixed `seed_data.py`'s stray `'Appliances'` to `'Electronics'`.
7. **Seller contact (WhatsApp) + open/closed badge were missing from both detail pages** -- explicit, named success criteria in both Iyaan's and Kevo's task docs ("Pull `good.seller.profile` for WhatsApp contact + `is_open` status; show clearly if the seller is currently closed"), and part of the demo's stated Definition of Done. Neither `good_detail.html` nor `service_detail.html` had this. Added to both, removed the dead `href="#"` "Message seller" placeholder link now that real contact is shown.
8. **`service_list` had zero filtering** -- Kevo's task doc requires the same `q`/`category`/`price_min`/`price_max` filtering `good_list` has (minus `condition`). Added it to `apps/services/views.py::service_list` and a matching filter bar to `service_list.html`.

### Verified this session (not just written -- actually run)
- Confirmed `CampusLocation` seed data is real (Iyaan's Step 0 was actually already done, contrary to what I might have assumed -- checked `seed_catalog.py` directly).
- Full flow via Django's test client on a fresh migrated + seeded DB: register -> set profile phone + `is_open` -> create a Good with a real uploaded image -> create a Service with a real uploaded image -> both display images + WhatsApp link + open badge on their detail pages -> browse shows both -> htmx live filter narrows correctly -> dashboard shows both tabs populated with real owned listings -> a second user is correctly blocked (403) from editing either the Good or the Service via direct URL.
- `Category.objects.count()` == 6, exact names match the paper. `CampusLocation` has no leftover `"Placeholder N"` rows.
- Zero CDN references anywhere in `templates/` (grepped). `static/js/htmx.min.js`, `static/js/alpine.min.js`, `static/css/main.css`, `static/img/placeholder.png` all confirmed served locally by an actual running dev server, not assumed.

### Still not done (out of scope for a frontend/integration pass, needs a person)
- Phone numbers aren't validated/normalized to international format anywhere -- the `wa.me/{{ phone_number }}` link will produce a dead link if a seller enters a local-format number (e.g. `0712...` instead of `254712...`). Needs either a form-level normalizer or a documented input format requirement.
- FLAG 7's fuller search interpretation (title + description + category name + seller full name) isn't implemented anywhere -- all list/browse views currently only match `title`/`description`. Flagging the gap rather than silently expanding scope further.
- `goods/urls.py` and `services/urls.py` still have no `app_name` namespace -- left alone again, same reasoning as before.

### Two more found during the final completeness pass
- **Stale duplicate placeholder image**: `apps/marketplace/static/marketplace/img/placeholder.png` was still committed from before the templates/static consolidation, while `seed_data.py` was pointing at that old path. Removed the stale duplicate, repointed `seed_data.py` at the consolidated `static/img/placeholder.png`.
- **No services seed data existed at all** (Kevo's Step 5 -- "browse page isn't empty for the demo"). Added `apps/services/management/commands/seed_services.py`, mirroring the goods seed pattern exactly (same placeholder image, `get_or_create` seller). Run order for a fresh demo DB: `seed_catalog` -> `seed_categories` -> `seed_data` -> `seed_services`.

### Final verification pass (all three task docs' success criteria, tested against real behavior)
Ran a single comprehensive test-client script covering: bad-email rejection, valid registration + auto-verify + auto-login, profile edit incl. `is_open`, real (non-placeholder) CampusLocation data, Category matching the paper exactly, Good creation with server-side seller assignment + real image upload, Service creation with the same, both detail pages showing WhatsApp contact + open/closed badge, both list views' filters, anonymous browse showing both types, htmx live-filter narrowing correctly, dashboard showing the logged-in seller's own goods and services, a second user blocked (403) from editing either listing type, and logout. Every check passed.
