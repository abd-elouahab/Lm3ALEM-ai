# 🔧 L'M3alem AI — معلم AI

<div align="center">

![L'M3alem AI](https://img.shields.io/badge/L'M3alem-AI-e94560?style=for-the-badge&logo=robot&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Grok AI](https://img.shields.io/badge/Grok-Vision_AI-1e293b?style=for-the-badge&logo=xai&logoColor=white)

**AI-powered marketplace connecting clients with skilled Moroccan artisans in the Souss-Massa region.**

[Live Demo](#-live-demo) • [Features](#-features) • [Tech Stack](#-tech-stack) • [Getting Started](#-getting-started) • [API Docs](#-api-documentation)

</div>

---

## 📖 About The Project

**L'M3alem AI** is a two-sided marketplace platform built for the **L'M3alem AI Hackathon 2026**. It solves a real problem in Morocco : over **150,000 skilled artisans** (plumbers, electricians, plasterers, painters, tile workers) remain unemployed — not because they lack skills, but because they lack visibility and market access.

### The Problem

```
Artisan                                    Client
(Skilled but invisible)    ←  GAP  →    (Needs help but can't find trust)
     💼                                       🏠
```

### The Solution

L'M3alem AI uses **Grok Vision AI** to analyze repair photos, automatically diagnose the problem, estimate the price, and match the client with the best nearby artisan — all within minutes.

```
📸 Client takes photo
        ↓
🤖 AI chat diagnoses problem (Darija)
        ↓
💰 ML model estimates price & duration
        ↓
📍 Algorithm matches nearest artisan
        ↓
📞 Artisan receives client contact info
        ↓
🛡️ 48h quality guarantee
```

### Key Metric

> **VAE (Volume d'Affaires Équitables)** — Total transaction value where the artisan was paid fairly AND the client received guaranteed quality service.

---

## ✨ Features

### 👤 Client Side
- **AI Photo Chat** — conversational diagnosis in Moroccan Darija (العربية الدارجة)
- **Automatic Problem Detection** — AI identifies problem type from photo (no manual selection)
- **Price Estimation** — ML model predicts price range and duration
- **Real-time Matching** — algorithm finds best nearby artisan instantly
- **48h Quality Guarantee** — complaint window with automatic escrow release
- **Rating System** — rate artisans after service completion

### 🔨 Artisan Side
- **Job Offers** — receive new job notifications with client details
- **Accept / Refuse** — with 10-point penalty for unjustified refusals
- **Client Contact Info** — full name, phone, city, problem photo on acceptance
- **Fair Pricing** — artisan receives 50% of client price displayed
- **Availability Toggle** — set availability in one tap
- **Ranking System** — score-based levels (مبتدئ → متوسط → معلم → معلم كبير)

### 🤖 AI & Algorithm
- **Grok Vision AI** — `grok-2-vision-1212` for image analysis
- **Conversational Diagnosis** — 2-4 question chat before final analysis
- **Random Forest ML** — price and duration prediction (trained on 1000 synthetic Souss-Massa data points)
- **Turn-based Matching** — prioritizes artisans who haven't worked recently (fairness system)
- **Haversine Distance** — GPS-based proximity scoring

### 💰 Business Model
```
Client pays full price
├── 50% → Artisan (direct)
├── 30% → Artisan savings account (released after 48h guarantee)
└── 20% → Platform
```

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **FastAPI** | REST API framework |
| **PostgreSQL** | Primary database |
| **SQLAlchemy** | ORM |
| **Grok Vision AI** | Photo analysis & diagnosis chat |
| **scikit-learn** | Price prediction ML model |
| **Twilio** | SMS notifications |
| **bcrypt** | Password hashing |
| **JWT** | Authentication |

### Frontend
| Technology | Purpose |
|---|---|
| **React 18** | UI framework |
| **Tailwind CSS** | Styling |
| **Axios** | API calls |
| **React Router v6** | Navigation |
| **Zustand** | State management |
| **Framer Motion** | Animations |
| **React Hot Toast** | Notifications |

### Infrastructure
| Technology | Purpose |
|---|---|
| **Vercel** | Frontend hosting |
| **Ngrok** | Backend tunnel (demo) |
| **GitHub** | Version control |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/YourUsername/lm3alem-ai.git
cd lm3alem-ai
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your values (see Environment Variables section)
```

### 3. Database Setup

```bash
# Open psql
psql -U postgres

# Create database
CREATE DATABASE lm3alem_ai;
\c lm3alem_ai

# Run schema
\i backend/schema.sql

# Run seed data (20 artisans + 5 clients)
\i backend/seed.sql
```

### 4. Train ML Model

```bash
cd backend
python ml/generate_data.py    # Generate synthetic dataset
python ml/train_price_model.py # Train price & duration models
```

### 5. Start Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Backend runs at : `http://localhost:8000`
API docs at : `http://localhost:8000/docs`

### 6. Frontend Setup

```bash
cd frontend
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env

# Start dev server
npm run dev
```

Frontend runs at : `http://localhost:5173`

---

## 🔐 Environment Variables

Create `backend/.env` with these values :

```env
# Database
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/lm3alem_ai

# AI
XAI_API_KEY=xai-your-grok-api-key

# Auth
JWT_SECRET=your-super-secret-jwt-key
JWT_EXPIRE_MINUTES=1440

# SMS (optional for demo)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# Matching
MATCHING_WAIT_MINUTES=60
GUARANTEE_HOURS=48
```

Create `frontend/.env` :

```env
VITE_API_URL=http://localhost:8000
```

---

## 🧪 Test Accounts

After running seed.sql, these accounts are ready :

### Clients
| Email | Password | City |
|---|---|---|
| client1@test.com | password123 | Agadir |
| client2@test.com | password123 | Inezgane |
| client3@test.com | password123 | Ait Melloul |
| client4@test.com | password123 | Tiznit |
| client5@test.com | password123 | Taroudant |

### Artisans (sample)
| Email | Password | Specialty | City |
|---|---|---|---|
| ahmed.zlayji@example.com | password123 | Zlayji | Agadir |
| hassan.plombier@example.com | password123 | Plombier | Chtouka |
| khalid.electricien@example.com | password123 | Electricien | Drarga |
| fatima.sebbagh@example.com | password123 | Sebbagh | Ait Melloul |
| mohamed.gebbas@example.com | password123 | Gebbas | Taroudant |

---

## 📡 API Documentation

Full interactive docs available at `http://localhost:8000/docs`

### Core Endpoints

#### Auth
```
POST /auth/register   → Create account (client or artisan)
POST /auth/login      → Login and receive JWT token
```

#### Jobs
```
POST /jobs/analyze    → Upload photo → AI analysis + price estimate
POST /jobs/chat       → Conversational AI diagnosis (Darija)
POST /jobs            → Create job request
GET  /jobs            → List all jobs for current user
GET  /jobs/:id        → Job detail (price shown differs by role)
PATCH /jobs/:id/accept       → Artisan accepts job
PATCH /jobs/:id/refuse       → Artisan refuses (-10 points)
PATCH /jobs/:id/confirm-dates → Start service
PATCH /jobs/:id/complete     → Declare service complete
POST /jobs/:id/claim         → Client files complaint
```

#### Matching
```
POST /match           → Trigger artisan matching algorithm
```

#### Artisans
```
GET   /artisans              → List artisans with filters
GET   /artisans/:id          → Artisan public profile
PATCH /artisans/:id/availability → Toggle availability
```

#### Ratings
```
POST /ratings         → Submit rating after completed job
```

---

## 🤖 AI Features In Detail

### Vision Analysis Flow
```
1. Client uploads photo
2. Grok Vision (grok-2-vision-1212) analyzes image
3. AI starts conversation in Darija
4. After 2-4 questions → final diagnosis JSON
5. ML model predicts price and duration
6. Results displayed to client
```

### Matching Algorithm
```python
score = (distance_score × 0.40) +
        (ranking_normalized × 0.35) +
        (turn_fairness_score × 0.25)

# turn_fairness ensures artisans who haven't
# worked recently get priority over those
# who worked yesterday
```

### Ranking Levels
| Level | Arabic | Score | Min Jobs |
|---|---|---|---|
| Apprenti | مبتدئ | < 60 | any |
| Compagnon | متوسط | ≥ 60 | 5+ |
| Maître Artisan | معلم | ≥ 75 | 20+ |
| Maître Maâlem | معلم كبير | ≥ 90 | 50+ |

---

## 🗄️ Database Schema

```
users ──────────────┬── artisans
                    └── clients
                           │
                         jobs ──── matching_attempts
                           │
                    ┌──────┼──────┐
                 ratings  guarantees  payments
```

Key tables : `users`, `artisans`, `clients`, `jobs`, `matching_attempts`, `ratings`, `guarantees`, `payments`

---

## 🌍 Geographic Scope

**Souss-Massa Region, Morocco**

Cities covered :
`Agadir` • `Inezgane` • `Ait Melloul` • `Tiznit` • `Taroudant` • `Biougra` • `Chtouka` • `Massa` • `Drarga` • `Dcheira`

---

## 🚀 Deployment

### Frontend (Vercel)
```bash
# Push to GitHub
git push origin main

# Vercel auto-deploys on every push
# Set VITE_API_URL in Vercel environment variables
```

### Backend (Ngrok for demo)
```bash
# Terminal 1 — keep running
uvicorn app.main:app --reload --port 8000

# Terminal 2 — keep running
ngrok http 8000

# Copy forwarding URL → update VITE_API_URL in Vercel
```

---

## 🛡️ Technical Limitations & Mitigations

| Limitation | Mitigation |
|---|---|
| AI can't see hidden problems (pipes behind walls) | Human selects, AI measures — clear confidence indicator |
| ML trained on synthetic data | Continuous learning from real transactions |
| Rural connectivity issues | Redundant SMS + push notifications, silence ≠ refusal |
| No skill verification in MVP | Ranking system acts as natural filter |
| Matching scalability | PostGIS + Redis cache planned for scale |

---

## 👥 Team

Built with ❤️ during **L'M3alem AI Hackathon 2026** — Souss-Massa, Morocco.

---

## 📄 License

This project was built for hackathon purposes.

---

<div align="center">

**L'M3alem AI** — التكنولوجيا فخدمة الناس

*La technologie au service de l'humain, la tradition enrichie par l'innovation.*

</div>
