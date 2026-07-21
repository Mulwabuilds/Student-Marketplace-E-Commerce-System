# SMES — Iyaan (Ian) — Sprint 2 (2-Day MVP Push)

## 0. Full scope — what we're building and why (read this first)

**Project:** Student Marketplace E-Commerce System (SMES), Kabarak University. Buyers browse without accounts; only sellers register. Sellers post `Good`s (physical items, new/used) or `Service`s. Seller contact (WhatsApp) is public; deals happen off-platform.

**Where we are:** T1–T9 are done. Models exist and are migrated: `User`, `Profile` (accounts), `CampusLocation`, `Category` (catalog), `Good`, `GoodImage` (goods), `Service`, `ServiceImage` (services). DRF is installed (T9) but **we are pivoting away from a DRF API for this demo** — 2 days left, 3 people, and React+DRF would add auth/CORS/build-tooling overhead with zero product payoff in that time. **Django templates instead — server-rendered, session auth.** DRF stays installed for later; nobody writes serializers/viewsets for the next 2 days.

**Decisions locked for this MVP:**
- No OTP flow — registration auto-verifies.
- `Profile.is_open` (seller-wide availability toggle) is being added via migration (Maximus is doing this) — it was a locked product decision missing from T4.
- `GoodImage`/`ServiceImage` use real file uploads (`ImageField` + Pillow) — more authentic for a live demo than requiring pre-hosted image links. Maximus is doing the one-time setup (Pillow install, `MEDIA_ROOT`/`MEDIA_URL`, field rename from `image_url` to `image`) — wait for his go-ahead before wiring your form, so you're not building against a field that's about to change.

**Who's doing what:**
- **Maximus (Lee):** auth (register/login/logout), Profile edit incl. `is_open`, seller dashboard, combined buyer-side browse/search across Goods+Services, `base.html`, final integration.
- **You (Iyaan/Ian):** real `CampusLocation` seed data, Goods templates/views/forms (list, detail, create/edit/delete).
- **Kevo (Kevin):** Services templates/views/forms (mirrors your Goods work, minus `condition`).

**Definition of done for the demo:** on a fresh clone + fresh DB, a seller can register → log in → edit profile (incl. toggling `is_open`) → post a Good and a Service → an anonymous buyer can browse, search/filter, open a listing, and see the seller's contact + open/closed status. Runs locally on a laptop. No deployment needed.

---

## 1. Your steps

### Step 0 — Real `CampusLocation` data (do this FIRST, today — it's blocking)
- This has been an open flag since Sprint 1 (FLAG 8) — placeholder rows are still in the DB.
- Write/update `apps/catalog/management/commands/seed_catalog.py` to replace the placeholder `CampusLocation` rows with the real list (hostels, blocks, gate, library, etc. — whatever the actual campus location set is).
- Run it: `python manage.py seed_catalog` (or split into `seed_locations` if cleaner).
- **Success criteria:** `CampusLocation.objects.all()` in the Django shell shows real names, no `"Placeholder 1"`-style rows left; Maximus's `ProfileForm` dropdown (Step 4 in his file) shows real locations, not placeholders — check with him once his form is up.

### Step 1 — `GoodForm` + `GoodImageForm`
- In `apps/goods/forms.py`:
  - `GoodForm(ModelForm)`: `fields = ['title', 'description', 'price', 'category', 'condition']`.
  - `GoodImageForm(ModelForm)`: `fields = ['image']` — real file input now (`ImageField`), not a URL field. Wait for Maximus's Step 2a to land before writing this.
- **Success criteria:** form renders with correct field types (dropdown for `category`, choice field for `condition`, file picker for image); submitting invalid data (e.g. negative price) shows a form error before it ever reaches the DB `CHECK` constraint.

### Step 2 — Goods views
- `good_list(request)` — public, `Good.objects.filter(status='available')`, support the same GET-param filtering Maximus's browse view uses (`q`, `category`, `price_min`, `price_max`, `condition`) so this page works standalone too, not just via his combined browse.
- `good_detail(request, pk)` — public. Pull `good.seller.profile` for WhatsApp contact + `is_open` status; show clearly if the seller is currently closed.
- `good_create(request)` — `@login_required`. On save, set `good.seller = request.user` before saving — **never** trust a seller field from the form/POST data.
- `good_update(request, pk)` / `good_delete(request, pk)` — `@login_required`, and explicitly check `request.user == good.seller` before allowing edit/delete (return 403 or redirect if not). Don't skip this check — anyone could otherwise edit anyone else's listing by guessing a URL.
- **Success criteria:** a logged-in seller can create a Good, see it appear on `good_list`, edit it, delete it; a *different* logged-in user attempting to edit/delete someone else's Good via direct URL is blocked, not silently allowed.

### Step 3 — Goods templates
- `good_list.html` — grid/list: title, price, category, condition, a link to detail. Extends `base.html`.
- `good_detail.html` — full description, price, condition, category, seller's WhatsApp contact, open/closed badge.
- `good_form.html` — shared by create and update. **Must have `enctype="multipart/form-data"` on the `<form>` tag**, or uploaded files silently won't arrive in `request.FILES`. In the view, pass both `request.POST` and `request.FILES` into the form.
- Inline image add: for v1, one extra `image` file field on the same form — don't build a full multi-image upload widget, it's not worth the time for this demo.
- `good_detail.html`: render the uploaded image with `<img src="{{ good.goodimage_set.first.image.url }}">` (adjust related-name to whatever's actually on the model) — guard with an `{% if %}` in case a listing has no image yet.
- **Success criteria:** all three templates render with real data (no hardcoded/dummy content left over from earlier scaffolding), extend `base.html`, look presentable with Bootstrap classes, and an uploaded image actually displays on the detail page.

### Step 4 — Day 2: wire real data + support Maximus's browse page
- Double check nothing in your templates still has placeholder/static content — everything should be looping over real querysets by now.
- Add a handful of demo Goods via the admin or a quick seed command so the browse page isn't empty for the demo.
- Be available during Maximus's Step 7 integration pass to fix anything that breaks on the Goods side.
- **Success criteria:** fresh DB + your seed data → browse page and `good_list` both show real, populated listings with no errors.

---

## 2. Project structure (shared — everyone follows this)

```
apps/
├── accounts/
│   ├── models.py          # User, Profile (+ is_open)
│   ├── forms.py           # RegistrationForm, ProfileForm
│   ├── views.py           # register, profile_edit
│   ├── urls.py
│   └── templates/accounts/
│       ├── register.html
│       ├── login.html
│       └── profile_edit.html
├── catalog/
│   ├── models.py           # Category, CampusLocation
│   └── management/commands/seed_catalog.py   # <- yours
├── goods/
│   ├── models.py           # Good, GoodImage
│   ├── forms.py            # <- yours
│   ├── views.py            # <- yours
│   ├── urls.py             # <- yours
│   └── templates/goods/    # <- yours
│       ├── good_list.html
│       ├── good_detail.html
│       └── good_form.html
├── services/                # Kevo mirrors this layout, no `condition`
└── marketplace/
    ├── views.py             # browse, dashboard (Maximus)
    ├── urls.py
    └── templates/marketplace/
        ├── browse.html
        └── dashboard.html

templates/
└── base.html               # shared navbar, Bootstrap CDN (Maximus)
```
