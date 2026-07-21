# SMES — Kevo (Kevin) — Sprint 2 (2-Day MVP Push)

## 0. Full scope — what we're building and why (read this first)

**Project:** Student Marketplace E-Commerce System (SMES), Kabarak University. Buyers browse without accounts; only sellers register. Sellers post `Good`s (physical items, new/used) or `Service`s. Seller contact (WhatsApp) is public; deals happen off-platform.

**Where we are:** T1–T9 are done. Models exist and are migrated: `User`, `Profile` (accounts), `CampusLocation`, `Category` (catalog), `Good`, `GoodImage` (goods), `Service`, `ServiceImage` (services). DRF is installed (T9) but **we are pivoting away from a DRF API for this demo** — 2 days left, 3 people, and React+DRF would add auth/CORS/build-tooling overhead with zero product payoff in that time. **Django templates instead — server-rendered, session auth.** DRF stays installed for later; nobody writes serializers/viewsets for the next 2 days.

**Decisions locked for this MVP:**
- No OTP flow — registration auto-verifies.
- `Profile.is_open` (seller-wide availability toggle) is being added via migration (Maximus is doing this) — it was a locked product decision missing from T4.
- `ServiceImage` uses real file uploads (`ImageField` + Pillow) — more authentic for a live demo than requiring pre-hosted image links. Maximus is doing the one-time setup (Pillow install, `MEDIA_ROOT`/`MEDIA_URL`, field rename from `image_url` to `image`) — wait for his go-ahead before wiring your form, so you're not building against a field that's about to change.

**Who's doing what:**
- **Maximus (Lee):** auth (register/login/logout), Profile edit incl. `is_open`, seller dashboard, combined buyer-side browse/search across Goods+Services, `base.html`, final integration.
- **Iyaan (Ian):** real `CampusLocation` seed data, Goods templates/views/forms (list, detail, create/edit/delete).
- **You (Kevo/Kevin):** Services templates/views/forms — mirrors Iyaan's Goods work, minus `condition`.

**Definition of done for the demo:** on a fresh clone + fresh DB, a seller can register → log in → edit profile (incl. toggling `is_open`) → post a Good and a Service → an anonymous buyer can browse, search/filter, open a listing, and see the seller's contact + open/closed status. Runs locally on a laptop. No deployment needed.

---

## 1. Your steps

### Step 1 — `ServiceForm` + `ServiceImageForm`
- In `apps/services/forms.py`:
  - `ServiceForm(ModelForm)`: `fields = ['title', 'description', 'price', 'category']` — **no `condition`**, `Service` doesn't have that field.
  - `ServiceImageForm(ModelForm)`: `fields = ['image']` — real file input now (`ImageField`), not a URL field. Wait for Maximus's Step 2a to land before writing this.
- **Success criteria:** form renders correctly (dropdown for `category`, file picker for image); submitting a negative price shows a form error before hitting the DB `CHECK` constraint.

### Step 2 — Services views
- `service_list(request)` — public, `Service.objects.filter(status='available')`, support GET-param filtering (`q` on title/description, `category`, `price_min`, `price_max` — **no `condition` param**, services don't have one) so this page works standalone.
- `service_detail(request, pk)` — public. Pull `service.seller.profile` for WhatsApp contact + `is_open` status, shown clearly.
- `service_create(request)` — `@login_required`. Set `service.seller = request.user` server-side before saving — never trust a seller field from POST data.
- `service_update(request, pk)` / `service_delete(request, pk)` — `@login_required`, and explicitly check `request.user == service.seller` before allowing edit/delete. Don't skip this — it's the same access-control check Iyaan is doing on Goods, and it matters for both.
- **Success criteria:** a logged-in seller can create a Service, see it on `service_list`, edit it, delete it; a different user attempting to edit/delete via direct URL is blocked.

### Step 3 — Services templates
- `service_list.html` — grid/list: title, price, category, link to detail. Extends `base.html`.
- `service_detail.html` — description, price, category, seller's WhatsApp contact, open/closed badge.
- `service_form.html` — shared by create and update. **Must have `enctype="multipart/form-data"` on the `<form>` tag**, or uploaded files silently won't arrive in `request.FILES`. In the view, pass both `request.POST` and `request.FILES` into the form.
- Inline image add: one extra `image` file field on the same form, same approach as Goods — no multi-image upload widget for this demo.
- `service_detail.html`: render the uploaded image with `<img src="{{ service.serviceimage_set.first.image.url }}">` (adjust related-name to whatever's actually on the model) — guard with an `{% if %}` in case a listing has no image yet.
- **Success criteria:** all three templates render with real data, extend `base.html`, look presentable with Bootstrap classes, and an uploaded image actually displays on the detail page.

### Step 4 — Secondary: verify `Category` seed data
- Original Sprint 1 note (T15) was to confirm `Category` seed rows exactly match Section 1.8/3.6.5 of the project paper. Quick check: open `Category.objects.all()` in the shell against those sections — fix any mismatch directly via admin or a migration data fix.
- **Success criteria:** the six seeded categories match the paper's wording exactly (case, naming) — this matters for the academic deliverable, not just the demo.

### Step 5 — Day 2: wire real data + support integration
- Confirm nothing in your templates is still hardcoded/dummy — everything loops over real querysets.
- Add a handful of demo Services via admin or a seed command so browse isn't empty.
- Be available during Maximus's final integration pass (his Step 7) to fix anything breaking on the Services side.
- **Success criteria:** fresh DB + your seed data → browse page and `service_list` both show real, populated listings, no errors.

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
│   └── management/commands/seed_catalog.py   # Iyaan
├── goods/                   # Iyaan owns this layout
│   └── (models/forms/views/urls/templates)
├── services/
│   ├── models.py           # Service, ServiceImage
│   ├── forms.py            # <- yours
│   ├── views.py            # <- yours
│   ├── urls.py              # <- yours
│   └── templates/services/  # <- yours
│       ├── service_list.html
│       ├── service_detail.html
│       └── service_form.html
└── marketplace/
    ├── views.py             # browse, dashboard (Maximus)
    ├── urls.py
    └── templates/marketplace/
        ├── browse.html
        └── dashboard.html

templates/
└── base.html               # shared navbar, Bootstrap CDN (Maximus)
```
