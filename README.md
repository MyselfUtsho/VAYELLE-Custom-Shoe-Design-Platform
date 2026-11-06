# 👟 VAYELLE — Match it. Vibe it: A Custom Shoe Design and AI-Powered Recommendation Platform

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Flask-Framework-lightgrey)
![MongoDB](https://img.shields.io/badge/MongoDB-Database-green)
![Course](https://img.shields.io/badge/BRACU-CSE471-orange)
![Semester](https://img.shields.io/badge/Semester-Fall%202026-informational)

---

## 📌 Project Overview

**VAYELLE** is a web-based shoe customization and recommendation platform designed for the **CSE471 (System Analysis and Design)** course at BRAC University. The platform allows users to browse shoes, explore colors, upload outfit images, customize shoes through an interactive 2D design canvas, calculate dynamic pricing, receive AI-assisted recommendations, preview designs in 3D/on-foot, save custom configurations, and share or remix community designs[cite: 13, 16].

---

## 👥 Team Members & Responsibilities

| Student ID | Name | Module 1 (Lab 5) | Module 2 (Lab 6) | Module 3 (Lab 7) |
| :--- | :--- | :--- | :--- | :--- |
| **23101197** | Athoy Roy | Browse Shoes by Category | Material and Sole Selection | Decorative Elements Library & On-Foot Preview; 3D Shoe Viewer[cite: 13, 14] |
| **24101537** | Miftahul Islam Prangon | Color Exploration and Suggestions | Interactive 2D Design Canvas | Live Design Preview & Layer Simulation; Color-Blind-Friendly Palette Mode[cite: 13, 14] |
| **22101062** | Diya Zerin | Budget-Based Shoe Search | Estimated Price Calculation | Material Recommendations & Save Designs; Outfit Analysis with Gemini Vision[cite: 13, 14] |
| **23101347** | Khairul Islam Bhuiya | Outfit Image Upload | Shoe Size Guide & Sandbox Payment | Smart Shoe Recommendations; Community Design Showcase and Remix[cite: 13, 14] |

---

## 🛠️ Technology Stack

| Component | Technology / Library |
| :--- | :--- |
| **Languages** | Python, JavaScript, HTML, CSS[cite: 13, 16] |
| **Backend Framework** | Flask[cite: 13, 16] |
| **Frontend Styling** | Bootstrap and CSS[cite: 13, 16] |
| **Database & Driver** | MongoDB, PyMongo[cite: 13, 16] |
| **Design Libraries** | Fabric.js (2D Canvas), Three.js (3D Viewer)[cite: 13, 16] |
| **External APIs** | Cloudinary API, Color API, Gemini API, SSLCommerz Sandbox API[cite: 13, 16] |
| **Version Control** | GitHub[cite: 13, 16] |

---

## 🔌 External API Allocation

| Team Member | Assigned API | Intended Use |
| :--- | :--- | :--- |
| **Athoy Roy** | Cloudinary API[cite: 16] | Uploading, storing, transforming, and delivering shoe images and design assets[cite: 16] |
| **Miftahul Islam Prangon** | Color API[cite: 16] | Retrieving color information and supporting color-combination suggestions and accessible palettes[cite: 16] |
| **Diya Zerin** | Gemini API[cite: 16] | Outfit image analysis and optional material suggestions[cite: 16] |
| **Khairul Islam Bhuiya** | SSLCommerz Sandbox API[cite: 16] | Testing checkout payments, handling success/failure responses, and verifying transactions[cite: 16] |

---

## 📁 Project Documentation Structure

Detailed documentation for each module and component can be found inside the `docs/` folder:

- 📄 **[Full Project Development Plan](./PROJECT_PLAN.md)**[cite: 16]
- 🧩 **[Module 1: Shoe Discovery & Selection](./docs/MODULE_1.md)** (Lab 5)[cite: 13, 16]
- ⚙️ **[Module 2: Shoe Configuration & Analysis](./docs/MODULE_2.md)** (Lab 6)[cite: 13, 14, 16]
- 🎨 **[Module 3: Design Finalization, Community & Checkout](./docs/MODULE_3.md)** (Lab 7)[cite: 14, 16]

---

## ⚙️ Quick Start & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/MyselfUtsho/VAYELLE-Custom-Shoe-Design-Platform.git](https://github.com/MyselfUtsho/VAYELLE-Custom-Shoe-Design-Platform.git)
   cd VAYELLE-Custom-Shoe-Design-Platform