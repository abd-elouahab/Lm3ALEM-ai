# L'M3alem AI — Frontend/Backend Integration Map

## Update (post-wiring)

- **Auth**: Wired — Login (POST /auth/login + GET /auth/me), Register (POST /auth/register then login), token + user in store and localStorage.
- **ClientDashboard**: Wired — GET /jobs, stats from real data, StatusBadge with backend statuses.
- **NewJobPage**: Wired — Step 1 specialty; Step 2 create job → POST /jobs/analyze with file → show aiResult; Step 3 confirm with aiResult/city → POST /match; success → navigate to /client/jobs/:id.
- **ClientJobDetail**: Wired — GET /jobs/:id, poll every 15s when pending/matching, GET /artisans/:id for artisan card, POST /jobs/:id/claim (params), POST /ratings.
- **ArtisanDashboard**: Wired — GET /artisans/me, GET /jobs, PATCH /artisans/:id/availability, PATCH /jobs/:id/accept, PATCH /jobs/:id/refuse; stats from real data.
- **ArtisanJobDetail**: Wired — GET /jobs/:id, PATCH /jobs/:id/confirm-dates, PATCH /jobs/:id/complete (modal for after_photo_url).
- **ArtisanProfile**: Wired — GET /artisans/me, GET /ratings/:artisan_id for reviews.
- **Backend**: GET /auth/me added. GET /jobs returns list for client or artisan. POST /match body `{ job_id }`. GET /artisans/me added for current artisan profile.

---

## Internal analysis (Step 1)

### Frontend pages and API needs

| Page | API calls needed | Current status |
|------|------------------|----------------|
| **Index** | None (static + links to auth) | No wiring needed |
| **AuthPage** | POST /auth/register, POST /auth/login (form) | **Needs wiring** — currently mock login/register |
| **ClientDashboard** | GET /jobs (list jobs for client) | **Needs wiring** — uses mockJobs |
| **NewJobPage** | POST /jobs (create), POST /jobs/analyze (with job_id + file), POST /match | **Needs wiring** — mock photo analyze, mock submit. Backend analyze requires job_id so flow: create job first then analyze then match |
| **ClientJobDetail** | GET /jobs/:id, POST /jobs/:id/claim, POST /ratings | **Needs wiring** — mock job, claim and rating not wired |
| **ArtisanDashboard** | GET /jobs (artisan’s jobs + pending offers), PATCH /artisans/:id/availability, PATCH /jobs/:id/accept, PATCH /jobs/:id/refuse, PATCH /jobs/:id/complete | **Needs wiring** — mock data, toasts only |
| **ArtisanJobDetail** | GET /jobs/:id, PATCH /jobs/:id/confirm-dates, PATCH /jobs/:id/complete | **Needs wiring** — mock job |
| **ArtisanProfile** | GET /artisans/:id (for public profile by id), or current user’s artisan profile | **Needs wiring** — hardcoded “Hassan” profile |

### Backend endpoints summary

- **POST /auth/register** — Body: UserCreate. Returns UserResponse (no token). Frontend must call login after register to get token.
- **POST /auth/login** — Form: username (email), password. Returns { access_token }. No user in response; frontend stores user from register or builds from JWT.
- **GET /jobs** — **Missing**. Required for client dashboard and artisan dashboard. Add: returns list of jobs for current user (client: by client_id; artisan: jobs where artisan_id = me or matching_attempt for me).
- **POST /jobs** — Body: JobCreate (problem_type, symptom?, photo_url?). Returns JobResponse.
- **POST /jobs/analyze** — Form: job_id, problem_type, file (optional). Returns JobAnalyzeResponse (description, severity, surface_area_m2, complexity, nb_elements_affected, confidence, price_min, price_max, duration_hours).
- **GET /jobs/:id** — Returns JobResponse.
- **PATCH /jobs/:id/accept** — Returns JobAcceptResponse (artisan_name, artisan_phone, etc.).
- **PATCH /jobs/:id/refuse** — No body.
- **PATCH /jobs/:id/confirm-dates** — Body: { confirmed_start, confirmed_end } (ISO datetime).
- **PATCH /jobs/:id/complete** — Body: JobComplete (after_photo_url?).
- **POST /jobs/:id/claim** — Body: complaint_text?, complaint_photo_url?.
- **POST /match** — Body: job_id (integer). Triggers matching.
- **GET /artisans** — Query: specialty?, city?, is_available?. Returns list. No auth required in backend (but frontend may send token).
- **GET /artisans/:id** — Returns ArtisanResponse.
- **PATCH /artisans/:id/availability** — Body: { is_available: boolean }.
- **POST /ratings** — Body: job_id, score (1–5), comment?.

### Status mapping (backend → frontend)

Backend: `pending` \| `matching` \| `accepted` \| `in_progress` \| `completed` \| `disputed` \| `cancelled`.  
Frontend mockData used: `assigned` (→ backend `accepted`), `dispute` (→ backend `disputed`), `guarantee` (not a job status; show when completed and guarantee open).  
StatusBadge: add `accepted` and `cancelled`, `disputed`; map `accepted` to “Artisan assigné” (same as assigned).

### Auth flow

- Register returns user only. Frontend: after register call login(email, password) to get token, then store token + user (from register response) and redirect.
- Login returns { access_token }. Frontend: decode JWT for role or call a /me endpoint. Backend does not have /me; JWT payload has sub, email, role. Frontend can decode JWT to get role and build minimal user, or store user from register and reuse after login.
