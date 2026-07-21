# SMES — Maximus (Lee) — Sprint 2 (2-Day MVP Push)

## 0. Full scope — what we're building and why (read this first)

**Project:** Student Marketplace E-Commerce System (SMES), Kabarak University. Buyers browse without accounts; only sellers register. Sellers post `Good`s (physical items, new/used) or `Service`s. Seller contact (WhatsApp) is public; deals happen off-platform.

**Where we are:** T1–T9 are done. Models exist and are migrated: `User`, `Profile` (accounts), `CampusLocation`, `Category` (catalog), `Good`, `GoodImage` (goods), `Service`, `ServiceImage` (services). DRF is installed (T9) but **we are pivoting away from a DRF API for this demo** — 2 days left, 3 people, and building React+DRF auth/CORS/build-tooling on top of the same model work was pure plumbing with no product payoff. **Django templates instead — server-rendered, session auth, zero extra moving parts.** DRF stays installed for later (post-demo/Chapter 4) but nobody should be writing serializers/viewsets for the next 2 days.

**Decisions locked for this MVP:**
- No OTP flow. Registration auto-verifies (`is_email_verified = True` on save). OTP fields stay in the `User` model for later, just unused.
- `Profile.is_open` (seller-wide availability toggle) is being **added now** via migration — it was a locked product decision missing from the T4 schema.
- `GoodImage`/`ServiceImage` are being switched from a URL text field to real file uploads (`ImageField` + Pillow) — more authentic for a live demo than requiring pre-hosted image links. Small one-time setup cost (~20–30 min), owned by you (Step 2a below).

**Who's doing what:**
- **You (Maximus/Lee):** auth (register/login/logout), Profile edit incl. `is_open`, seller dashboard, combined buyer-side browse/search across Goods+Services, `base.html`, final integration.
- **Iyaan (Ian):** real `CampusLocation` seed data, Goods templates/views/forms (list, detail, create/edit/delete).
- **Kevo (Kevin):** Services templates/views/forms (mirrors Iyaan, minus `condition`).

**Definition of done for the demo:** on a fresh clone + fresh DB, a seller can register → log in → edit profile (incl. toggling `is_open`) → post a Good and a Service → an anonymous buyer can browse, search/filter, open a listing, and see the seller's contact + open/closed status. Runs locally on a laptop. No deployment needed.

---

## 1. Your steps

### Step 1 — Add `is_open` to `Profile`
- In `apps/accounts/models.py`, add to `Profile`: `is_open = models.BooleanField(default=True)`.
- Run `python manage.py makemigrations accounts && python manage.py migrate`.
- **Success criteria:** migration file created, applies with no errors; field visible and editable on the `Profile` admin page; you can flip it on an existing test profile via `/admin/`.

### Step 2a — Enable real image uploads (do this early — Iyaan and Kevo both depend on it)
- `pip install Pillow`.
- In `apps/goods/models.py` and `apps/services/models.py`, change `GoodImage.image_url` / `ServiceImage.image_url` from a URL/text field to `image = models.ImageField(upload_to='goods/%Y/%m/')` (services: `upload_to='services/%Y/%m/'`). These tables are still empty/placeholder data, so this is a safe field rename — run `makemigrations goods services && migrate`.
- In `settings.py`: add `MEDIA_URL = '/media/'` and `MEDIA_ROOT = BASE_DIR / 'media'`.
- In the project's root `urls.py` (dev only):
  ```python
  from django.conf import settings
  from django.conf.urls.static import static
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
  ```
- **Success criteria:** `python manage.py migrate` runs clean; a superuser can upload an actual image file to a `GoodImage`/`ServiceImage` via `/admin/` and it's viewable at its `/media/...` URL in the browser.
- **Tell Iyaan and Kevo the moment this is merged/pulled** — their forms and templates need the field rename (`image` not `image_url`) and `enctype="multipart/form-data"`.

### Step 2 — Registration form + view (no OTP)
- Create `apps/accounts/forms.py` with `RegistrationForm(UserCreationForm)`:
  - `Meta.model = User`, `fields = ['username', 'email', 'password1', 'password2']`
  - Override `clean_email` to explicitly reject non-`@kabarak.ac.ke` addresses at the form level too (the DB `CHECK` constraint already blocks it, but a raw `IntegrityError` is an ugly user-facing error — catch it in the form for a clean message).
- In `apps/accounts/views.py`, write a function-based `register(request)` view: on valid POST, `form.save(commit=False)`, set `user.is_email_verified = True`, `user.save()`, then `django.contrib.auth.login(request, user)`, redirect to `marketplace:browse`.
- **Success criteria:** submitting a non-`@kabarak.ac.ke` email shows a form error, no exception; a valid registration creates the user with `is_email_verified=True`, logs them in immediately, and redirects to the homepage.

### Step 3 — Login/logout
- Do **not** write custom views. In `apps/accounts/urls.py`:
  ```python
  from django.contrib.auth.views import LoginView, LogoutView
  path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
  path('logout/', LogoutView.as_view(next_page='marketplace:browse'), name='logout'),
  ```
- **Success criteria:** login with valid credentials redirects correctly and `request.user.is_authenticated` is `True` afterward; logout clears the session and redirects to browse.

### Step 4 — Profile edit view
- `ProfileForm(ModelForm)` in `forms.py`: `fields = ['campus_location', 'phone_number', 'bio', 'profile_photo_url', 'is_open']`.
- `profile_edit(request)` view, `@login_required`: `Profile.objects.get_or_create(user=request.user)`, bind form, save on POST.
- **Success criteria:** a logged-in user can load the edit page pre-filled with their existing data, change any field including `is_open`, save, and see it persist on reload.

### Step 5 — `base.html` + navbar
- Project-level `templates/base.html` (add `BASE_DIR / 'templates'` to `TEMPLATES[0]['DIRS']` in `settings.py`).
- Bootstrap 5 via CDN `<link>`/`<script>` tags — no build step.
- Navbar: anonymous users see **Login / Register**; authenticated users see **Dashboard / Edit Profile / Logout** and their username.
- **Success criteria:** every other template extends this and inherits a working, consistent navbar that correctly reflects auth state.

### Step 6 — `marketplace` app: browse/search + dashboard
- `python manage.py startapp marketplace`, add to `INSTALLED_APPS`.
- `browse(request)` view (public, no login required):
  - `goods = Good.objects.filter(status='available')`, `services = Service.objects.filter(status='available')`
  - Apply GET-param filters before combining: `q` (icontains on `title`/`description`), `category` (id), `price_min`/`price_max`, `condition` (goods only, ignored for services).
  - Combine with `itertools.chain(goods, services)` for the template — don't try to force them into one queryset, they're different models.
- `dashboard(request)` view, `@login_required`: `Good.objects.filter(seller=request.user)` + `Service.objects.filter(seller=request.user)` (all statuses, not just available), with edit/delete links.
- `apps/marketplace/urls.py`: `path('', browse, name='browse')`, `path('dashboard/', dashboard, name='dashboard')`.
- **Success criteria:** browse page with no query params shows all available goods+services; adding `?q=phone&category=2` narrows correctly; dashboard shows only the logged-in seller's own listings, including unavailable ones.

### Step 7 — Final integration (Day 2, afternoon — do this with Iyaan and Kevo present)
- Fresh clone on one machine, fresh DB, `migrate`, `createsuperuser`.
- Walk the full flow end to end: register → login → edit profile (toggle `is_open`) → create a Good → create a Service → log out → browse anonymously → search/filter → open a listing → confirm seller contact + open/closed status shows correctly.
- **Success criteria:** the whole flow completes with zero unhandled exceptions on a clean database. Any break found here gets fixed before you call it done — don't ship a "mostly works."

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
│   └── management/commands/seed_catalog.py
├── goods/
│   ├── models.py           # Good, GoodImage
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── templates/goods/
│       ├── good_list.html
│       ├── good_detail.html
│       └── good_form.html
├── services/                # mirrors goods/, no `condition`
│   └── (same layout as goods/)
└── marketplace/
    ├── views.py             # browse, dashboard
    ├── urls.py
    └── templates/marketplace/
        ├── browse.html
        └── dashboard.html

templates/
└── base.html               # shared navbar, Bootstrap CDN
```
