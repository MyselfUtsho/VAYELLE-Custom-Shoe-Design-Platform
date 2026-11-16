# 👟 VAYELLE — Match it. Vibe it: A Custom Shoe Design and AI-Powered Recommendation Platform

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-lightgrey)
![MongoDB](https://img.shields.io/badge/MongoDB-PyMongo-green)
![Course](https://img.shields.io/badge/BRACU-CSE471-orange)
![Semester](https://img.shields.io/badge/Semester-Fall%202026-informational)

---

## 🌐 Live Website

> **Render Deployment:**  
> 🔗 **Live Website URL:** [https://vayelle-platform.onrender.com](https://vayelle-platform.onrender.com)  
> *The production Flask application is hosted on Render in the Singapore region with Gunicorn and MongoDB Atlas cloud database connectivity.*

---

## 📌 Project Overview

**VAYELLE** is a fashion-tech custom shoe design and AI-powered recommendation platform engineered for the **CSE471 (System Analysis and Design)** course at BRAC University.

The platform empowers users to discover shoes by style and category, explore color palettes, customize footwear through an interactive design canvas, calculate dynamic pricing, receive intelligent style recommendations, preview designs, and manage orders.

* **Course:** CSE471 — System Analysis and Design
* **Group:** 03 | **Lab Section:** 01
* **Semester:** Fall 2026

---

## 👥 Team Members & Module Responsibilities

| Student ID | Name | Module 1 (Lab 5) | Module 2 (Lab 6) | Module 3 (Lab 7) |
| :--- | :--- | :--- | :--- | :--- |
| **23101197** | Athoy Roy | Browse Shoes by Category | Material and Sole Selection | Decorative Elements Library & On-Foot Preview; 3D Shoe Viewer |
| **24101537** | Miftahul Islam Prangon | Color Exploration and Suggestions | Interactive 2D Design Canvas | Live Design Preview & Layer Simulation; Color-Blind-Friendly Palette Mode |
| **22101062** | Diya Zerin | Budget-Based Shoe Search | Estimated Price Calculation | Material Recommendations & Save Designs; Outfit Analysis with Gemini Vision |
| **23101347** | Khairul Islam Bhuiya | Outfit Image Upload | Shoe Size Guide & Sandbox Payment | Smart Shoe Recommendations; Community Design Showcase and Remix |

---

## 🔌 External API Allocation

| Team Member | Assigned External API | Intended Use |
| :--- | :--- | :--- |
| **Athoy Roy** | Cloudinary API | Storing, transforming, and delivering high-fidelity shoe images and design assets |
| **Miftahul Islam Prangon** | Color API | Retrieving color information, palette generation, and accessibility contrasts |
| **Diya Zerin** | Gemini API | Multi-modal outfit photo analysis and style trait extraction |
| **Khairul Islam Bhuiya** | SSLCommerz Sandbox API | Simulating secure payment transactions and verification workflows |

---

## 🛠️ Technology Stack

### A. Currently Implemented (Phase 1 Infrastructure)
* **Backend Framework:** Python 3.10+, Flask 3.x (Modular Application Factory with Blueprints)
* **Production WSGI Server:** Gunicorn 21.x / 27.x
* **Database & Driver:** MongoDB (Local Community Server & Cloud MongoDB Atlas), PyMongo 4.x, dnspython
* **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5
* **Authentication & Security:** Werkzeug password hashing (`scrypt`), cryptographically signed session cookies, role-based access decorators (`@login_required`, `@manager_required`)
* **Environment Management:** `python-dotenv` for configuration separation (`.env`)
* **Version Control:** Git & GitHub

### B. Planned Technologies for Upcoming Modules
* **Interactive 2D Design:** Fabric.js (Canvas object manipulation)
* **3D Visualizer:** Three.js (3D shoe model rendering and orbital controls)
* **Cloud & AI APIs:** Cloudinary API, Color API, Google Gemini Vision API, SSLCommerz Sandbox API

---

## ✅ Completed & Verified Work (Phase 1)

The foundational architecture and Manager management system are 100% complete, tested, and verified:

1. **Flask Application Architecture:** Scalable application factory pattern (`create_app()`) with blueprints:
   * `main`: Homepage, landing layout, and product browsing.
   * `auth`: User registration, secure login, session creation, and logout.
   * `manager`: Protected Manager portal, inventory management, and database operations.
2. **User Registration:**
   * Strict `role="user"` assignment (role tampering attempts are completely blocked).
   * Validations for required fields, email formatting, and minimum 6-character passwords.
   * Duplicate email prevention backed by MongoDB unique indexes.
3. **Password Security:**
   * One-way password hashing using Werkzeug `scrypt` algorithm. Passwords are never stored in plain text.
4. **Session Management & Authentication:**
   * Secure session cookies (`HttpOnly`, `SameSite="Lax"`).
   * Graceful authentication state transitions with dynamic navbar rendering.
5. **Role-Based Access Control:**
   * Strict separation between regular `user` and `manager`.
   * Unauthenticated guests accessing manager routes are redirected to `/login`.
   * Authenticated non-manager users receive HTTP access denial.
6. **Secure Manager CLI Setup:**
   * Interactive setup command (`python manage.py create-manager`) with secure masked password input (`getpass`).
   * No hardcoded manager credentials in source code.
7. **Manager Dashboard:**
   * Real-time metrics: Total Shoes, Categories Count, and In-Stock items.
   * Database connection health banner with live ping diagnostic.
8. **Add Shoe Functionality:**
   * Manager form to create new shoe records with validations (name, category, gender, base price in BDT, availability, description, image).
9. **Shoe Inventory Management:**
   * Comprehensive inventory view with category pills, availability badges, BDT price formatting (`৳`), and deletion controls.
10. **MongoDB Integration:**
    * Unified connection utility supporting both local MongoDB (`mongodb://127.0.0.1:27017/vayelle_db`) and cloud MongoDB Atlas (`mongodb+srv://...`).
11. **Module 1 (Athoy Roy) — Browse Shoes by Category & Cloudinary Integration:**
    * **Category-Based Catalog (`/explore`):** Dynamic shoe browsing with real-time filter chips by Gender (Men, Women, Unisex) and Shoe Type (Sneakers, Casual, Formal).
    * **Cloudinary Image Storage & CDN Delivery:** Centralized cloud image storage using the official Cloudinary Python SDK. Replaces local image dependencies with secure HTTPS URLs.
    * **Dual Manager Image Uploads (`/manager/dashboard`):** Option A (direct file upload up to 10 MB with MIME/magic-byte checks) and Option B (public image URL download with robust IPv4/IPv6 SSRF guards).
    * **Automated Transformations:** Automatic format selection (`f_auto`), quality optimization (`q_auto`), and responsive bounding dimensions (`c_limit,w_800,h_800`).

---

## ⏳ Planned Team Features — Upcoming Lab Modules

*The following features are assigned to teammates for upcoming lab modules:*

* ❌ **Color Exploration & Accessible Palettes:** Color API integration and high-contrast color-blind mode (Miftahul).
* ❌ **Interactive 2D Design Canvas:** Fabric.js drag-and-drop customization editor (Miftahul).
* ❌ **Budget-Based Shoe Search & Dynamic Price Calculation:** Algorithmic price estimation based on materials and sole components (Diya).
* ❌ **Outfit Image Upload & Gemini Vision Analysis:** Multi-modal outfit photo style parsing (Diya).
* ❌ **Material & Sole Selection:** Custom sole and leather/mesh material selection (Athoy - Module 2).
* ❌ **Decorative Elements Library & On-Foot Preview:** Lifestyle image synthesis with Cloudinary (Athoy - Module 3).
* ❌ **3D Shoe Viewer:** Interactive Three.js model viewer (Athoy - Module 3).
* ❌ **Shoe Size Guide & Sandbox Payment:** SSLCommerz payment gateway integration (Khairul).
* ❌ **Smart Shoe Recommendations & Community Remix:** Recommendation engine and design sharing gallery (Khairul).

---

## 👥 Teammate Setup Guide — Shared Database & Cloudinary Architecture

To ensure all team members work seamlessly without synchronizing image files or experiencing missing data, VAYELLE utilizes a **centralized cloud architecture**:

1. **Shared Database:** Every teammate connects their local Flask app to the **same authorized MongoDB Atlas cluster** via `MONGO_URI`.
2. **Centralized Media Hosting:** Shoe images are hosted in the cloud on **Cloudinary**. MongoDB stores only the secure HTTPS URLs, not raw binary files or local disk paths.
3. **Zero Local File Copying:** Teammates do not need to download or copy shoe images to their computers. The browser automatically streams them via Cloudinary's fast global CDN.
4. **Instant Synchronization:** When an authorized manager adds a shoe on the live site or from their local workstation, the product and image are immediately available to every teammate locally and on Render.

---

### Step-by-Step Setup for Teammates

#### 1. Clone the Repository
```bash
git clone https://github.com/MyselfUtsho/VAYELLE-Custom-Shoe-Design-Platform.git
cd VAYELLE-Custom-Shoe-Design-Platform
```

#### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Local Environment (`.env`)
Copy `.env.example` to create your local `.env`:
```bash
cp .env.example .env
```
Open `.env` and fill in the shared project settings:
```ini
# Flask Security
SECRET_KEY=generate_a_secure_random_string_for_your_local_session

# Shared MongoDB Atlas Database (Required for all teammates)
MONGO_URI=mongodb+srv://<db_username>:<db_password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
DB_NAME=vayelle_db

# Cloudinary API Configuration (Athoy Roy — Module 1)
# Note: Required for Managers uploading images; optional for teammates only browsing catalog
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Runtime
FLASK_ENV=development
FLASK_DEBUG=1
PORT=5000
```

> [!IMPORTANT]
> **Security Rules:**
> * **Never commit `.env` to GitHub.** `.env` is ignored by `.gitignore` and must stay on your local machine only.
> * Never paste database passwords or API secrets into code files, README, or pull requests.
> * Every teammate uses the shared database: `DB_NAME=vayelle_db`.

#### 5. Verify Database Connectivity
```bash
python manage.py test-db
```
Confirm that the terminal outputs `Database Connection: SUCCESSFUL`.

#### 6. Run the Application Locally
```bash
python run.py
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser. Navigate to **[http://127.0.0.1:5000/explore](http://127.0.0.1:5000/explore)** to browse the shared catalog.

---

## 🚀 Management & Utility Commands

### Create Initial Manager Account
Run the secure interactive management CLI:
```bash
python manage.py create-manager
```
Follow the prompts to enter Manager Name, Email, and Password.

### Seed Sample Inventory (Offline / Mock Mode)
```bash
python manage.py seed-shoes
```

---

## 🧪 Testing Suite

### Unit & Mock Database Tests:
```bash
python -m unittest discover -s tests -p "test_phase1.py" -v
```

### Real MongoDB Integration Tests:
```bash
python tests/test_real_db_integration.py
```

---

## 🌿 GitHub Team Collaboration & Branch Workflow

To keep the repository clean and avoid breaking the production deployment:

### Branch Structure:
* **`main`**: Production-ready branch deployed to Render. **Protected** — direct commits should not be made here.
* **`develop`**: Integration branch for combining tested features.
* **Member Branches**: Individual working branches for each verified team member:
  * `member/athoy-roy`
  * `member/miftahul-islam-prangon`
  * `member/diya-zerin`
  * `member/khairul-islam-bhuiya`

### How to Work on Your Assigned Feature:
1. **Checkout your member branch:**
   ```bash
   git fetch origin
   git checkout member/<your-name>
   git pull origin main
   ```
2. **Develop and test locally:**
   Verify that your code runs cleanly and tests pass.
3. **Commit your changes:**
   ```bash
   git add <modified-files>
   git commit -m "Add: [Feature Name] - Brief description of work done"
   ```
4. **Push to your branch:**
   ```bash
   git push origin member/<your-name>
   ```
5. **Open a Pull Request (PR):**
   * Create a PR from `member/<your-name>` into `main` (or `develop`).
   * Have team members review the PR.
   * Once approved and merged into `main`, Render automatically triggers a deployment to update the live website!

---

## ☁️ Online Deployment Guide (Render)

The application includes production configuration files (`Procfile`, `render.yaml`, `gunicorn` in `requirements.txt`).

### Steps to Deploy on Render:
1. Log in to **[Render.com](https://render.com)** and click **New +** > **Web Service**.
2. Connect your GitHub repository: `MyselfUtsho/VAYELLE-Custom-Shoe-Design-Platform`.
3. Configure settings:
   * **Name:** `vayelle-platform` (or your preferred name)
   * **Region:** Singapore (or closest to your location)
   * **Branch:** `main`
   * **Runtime:** `Python 3`
   * **Build Command:** `pip install -r requirements.txt`
   * **Start Command:** `gunicorn run:app`
4. Add **Environment Variables**:
   * `SECRET_KEY`: A secure random secret string
   * `MONGO_URI`: Your MongoDB Atlas connection string (`mongodb+srv://...`)
   * `DB_NAME`: `vayelle_db`
   * `PYTHON_VERSION`: `3.13.0`
5. Click **Create Web Service**.
6. Render builds and deploys your website automatically on every push to `main`!

> [!NOTE]
> On Render's Free tier, services spin down after 15 minutes of inactivity. When accessed again, the first request may take 30–50 seconds to wake up the service.

---

## 📁 Repository Structure

```
VAYELLE-Custom-Shoe-Design-Platform/
├── app/                        # Flask Application Package
│   ├── routes/                 # Blueprint Route Handlers
│   │   ├── auth.py             # User Register, Login, Logout
│   │   ├── main.py             # Homepage & Public Routes
│   │   └── manager.py          # Manager Dashboard & Shoe Inventory
│   ├── static/                 # Static Assets
│   │   ├── css/                # style.css, components.css, responsive.css
│   │   ├── js/                 # main.js, store.js, colors.js, data.js
│   │   └── images/             # Shoe photography & UI imagery
│   ├── templates/              # Jinja2 HTML Templates
│   │   ├── base.html           # Master Layout Template
│   │   ├── index.html          # Homepage
│   │   ├── login.html          # Authentication / Login
│   │   ├── register.html       # Customer Registration
│   │   └── manager/            # Manager Dashboard & Inventory Views
│   ├── auth_utils.py           # Password Hashing & Access Decorators
│   └── db.py                   # PyMongo Connection & Database Helpers
├── docs/                       # Project Specification & Module Docs
│   ├── MODULE_1.md             # Lab 5 Plan
│   ├── MODULE_2.md             # Lab 6 Plan
│   ├── MODULE_3.md             # Lab 7 Plan
│   └── TEAM_RESPONSIBILITIES.md# External API & Feature Allocations
├── frontend/                   # Static Frontend Template Backups
├── tests/                      # Automated Unit & Integration Test Suites
│   ├── test_phase1.py          # Unit & Mock DB Tests
│   └── test_real_db_integration.py # Real Database E2E Tests
├── .env.example                # Template for Environment Configuration
├── .gitignore                  # Git Exclusion Rules (Secrets, Virtualenvs, Cache)
├── config.py                   # Flask Config Loader
├── manage.py                   # Administrative CLI Management Script
├── Procfile                    # WSGI Server Definition for Render / Heroku
├── PROJECT_PLAN.md             # Overall Project Plan
├── README.md                   # Comprehensive Project Documentation
├── render.yaml                 # Render Infrastructure-as-Code Blueprint
├── requirements.txt            # Python Dependencies
└── run.py                      # Flask Application Entry Point
```

---

## 📜 Academic Integrity & Course Information

This project is developed as part of **CSE471: System Analysis and Design** at BRAC University, Fall 2026. All source code, design assets, and architectural documents are produced for academic collaboration within Team 03.
