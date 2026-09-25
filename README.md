# CampusConnect – Smart Lost and Found Management System
**Institutional Campus Portal for VSIT (Vidyalankar School of Information Technology)**

---

## 📌 Project Abstract
**CampusConnect** is a web-based, full-stack campus utility developed for **VSIT (Vidyalankar School of Information Technology)** to streamline, automate, and safeguard the recovery of misplaced personal belongings across university premises. Combining deterministic rule-based matching algorithms with an administrative verification workflow, the platform connects students, faculty, and administrative officers into an accountable, transparent, and privacy-preserving lost-and-found network.

---

## 🛑 Problem Statement
On large higher-education campuses, hundreds of valuable assets (laptops, mobile phones, RFID ID cards, wallets, calculators, and keys) are misplaced each semester. Conventional methods of managing lost and found—such as informal social media groups, fragmented WhatsApp chats, and paper inquiry logs at security booths—suffer from several critical flaws:
1. **Lack of Centralization**: Lost notices and found reports are scattered, preventing students from knowing where to look.
2. **Privacy Vulnerabilities**: Directly broadcasting personal telephone numbers leads to student harassment, spam, and identity theft.
3. **Fraudulent Claims**: Without a formal verification procedure, dishonest individuals can claim high-value items without ownership proof.
4. **Zero Automation**: Students must manually browse through hundreds of notices without automated matching notifications.

---

## 🎯 Project Objectives
- Provide a unified digital catalog for lost and found reports accessible to all campus students, staff, and guests.
- Implement an explainable, rule-based **Smart Matching Engine** in Python that pairs Lost and Found reports with scores $\ge 50\%$.
- Establish an **Administrative Ownership Verification Desk** where claimants must describe confidential identifying details before physical item collection.
- Safeguard student privacy by preventing public disclosure of sensitive contact details.
- Provide administrators with real-time operational analytics (Lost vs Found ratios, inventory by category, status distributions) through interactive visual charts.

---

## 🚀 Key Features

### A. Student & Staff Features
- **Secure Authentication**: Registration and login with Werkzeug password hashing and role-based access control.
- **Report Lost Item**: Capture item name, category, brand, color, location, date, approximate time, identifying marks, optional estimated value in Indian Rupees (₹), and photo upload.
- **Report Found Item**: Quick logging of found campus belongings with safe contact instructions.
- **Multi-Attribute Search & Filter**: Case-insensitive keyword search, category filters, report type filter, campus spot filtering, date range selector, and sorting (Newest, Oldest, Name A-Z, Location A-Z).
- **Automated Smart Matches**: Real-time evaluation of newly reported items against candidate reports of the opposite type with percentage confidence and plain-English reasons.
- **Claim Submission**: Submit ownership claims with private identifying details (wallpapers, serial numbers, engraved initials, contents) visible only to campus administrators.
- **In-App Notification Center**: Instant alerts for discovered matches, claim approvals, claim rejections, and return confirmations.
- **Self-Service Report Management**: Edit and delete open reports submitted by the authenticated user.

### B. Campus Administrator Features
- **Unified Login**: Seamless single-portal access with role detection.
- **Analytical Dashboard**: Visual metrics and Chart.js visualizations (Lost vs Found doughnut chart, category bar chart, status distribution pie chart).
- **Claim Verification**: Dedicated console to cross-examine private details, approve genuine claims with pickup notes, or reject unverifiable requests.
- **Return Handover**: Formally mark items as "Returned" upon physical collection, automatically updating claim records and notifying owners.
- **User Directory**: View registered campus users with one-click account suspension and role toggle.

### C. Guest Capabilities
- Browse and search the public catalog without an account.
- View detailed item specifications (while contact information remains protected).
- Clear prompts to register or sign in to submit reports or claims.

---

## 🛠️ Technology Stack

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Backend Framework** | Python 3.12 / Flask 3.1 | Lightweight, beginner-friendly WSGI web framework |
| **Database** | SQLite 3 | Embedded, zero-configuration relational database |
| **ORM** | SQLAlchemy 2.x / Flask-SQLAlchemy 3.1 | Declarative Object Relational Mapping |
| **Security** | Werkzeug | Industry-standard password hashing (`generate_password_hash`) |
| **Frontend UI** | HTML5, CSS3, Vanilla JavaScript | Custom college theme (Deep Navy `#0a2540`, Vibrant Orange `#ff6b35`, Crisp White) |
| **CSS Framework** | Bootstrap 5.3 (CDN) | Modern responsive layout, cards, and modal dialogs |
| **Icons** | Bootstrap Icons 1.11 (CDN) | Semantic vector iconography |
| **Data Visualization** | Chart.js 4.4 (CDN) | Client-side reactive graphs for administrative metrics |
| **Testing** | Python `unittest` | Comprehensive unit and integration test suite |

---

## 📁 Project Directory Structure

```text
campusconnect/
│
├── app.py                      # Application entry point & factory
├── config.py                   # Configuration (Secret key, SQLite DB path, Uploads)
├── requirements.txt            # Python dependencies
├── seed.py                     # Realistic demo data populator
├── verify_workflows.py         # End-to-end workflow verification runner
├── lost_found.db               # SQLite database file (generated automatically)
├── README.md                   # Complete academic documentation
├── PROJECT_REPORT.md           # Formal college project report
│
├── models/
│   ├── __init__.py             # Database instance export & model imports
│   ├── user.py                 # User model (student, staff, admin roles)
│   ├── item.py                 # Item model (Lost/Found records, categories, status)
│   ├── match.py                # Match model (score, reason, paired item IDs)
│   ├── claim.py                # Claim model (reasons, private details, admin status)
│   └── notification.py         # Notification model (in-app alerts)
│
├── routes/
│   ├── __init__.py             # Auth & admin decorator helpers
│   ├── auth_routes.py          # Register, Login, Logout, Session management
│   ├── main_routes.py          # Home, About, User Dashboard, Notifications
│   ├── item_routes.py          # Search & Filter, Report Lost/Found, Details, Edit, Delete
│   ├── claim_routes.py         # Claim submission and My Claims tracking
│   └── admin_routes.py         # Admin Dashboard, Claims Review, User Directory
│
├── services/
│   ├── matching_service.py     # Deterministic explainable rule-based matching algorithm
│   ├── notification_service.py # In-app notification creation and dispatch
│   └── validation_service.py   # File upload validation (PNG/JPG/JPEG, max 5MB) & input sanitization
│
├── static/
│   ├── css/
│   │   └── style.css           # Institutional theme (Navy #0a2540, Orange #ff6b35)
│   ├── js/
│   │   └── script.js           # Client interactions, image preview, deletion checks, Chart.js
│   └── uploads/                # Local storage for item photos
│
├── templates/
│   ├── base.html               # Master layout with college branding, navbar, and footer
│   ├── home.html               # Landing page (Hero, metrics, recent cards, 3-step guide)
│   ├── about.html              # Campus guidelines, FAQ, algorithm breakdown
│   ├── login.html              # Unified login portal with quick demo hints
│   ├── register.html           # Student/staff registration
│   ├── dashboard.html          # User dashboard (reports, claims, match alerts)
│   ├── admin_dashboard.html    # Admin console with Chart.js analytics and quick tables
│   ├── report_item.html        # Dynamic form for reporting Lost or Found items
│   ├── edit_item.html          # Edit report form for open items
│   ├── search.html             # Multi-attribute search & filter catalog
│   ├── item_details.html       # Full item view with privacy-safe contact modal
│   ├── my_reports.html         # User submitted reports management
│   ├── claims.html             # Claims submission and status timeline
│   ├── matches.html            # Smart matches paired comparison viewer
│   ├── notifications.html      # Notifications inbox with read controls
│   ├── admin/
│   │   ├── claims.html         # Admin claim review, approval, and rejection
│   │   └── users.html          # Admin user directory and role controls
│   └── errors/
│       ├── 404.html            # Custom college-themed 404 error page
│       └── 500.html            # Custom college-themed 500 error page
│
└── tests/
    ├── __init__.py
    ├── test_auth.py            # Registration, login, session, password hashing tests
    ├── test_items.py           # Item creation, validation, search, filter, edit, delete tests
    ├── test_matching.py        # Algorithm scoring, thresholds, notification trigger tests
    └── test_claims.py          # Claim submission, admin approval, and return flow tests
```

---

## 🧮 Smart Matching Algorithm Specification

The smart matching engine runs transparently within `services/matching_service.py` without requiring paid APIs or black-box external services. Whenever an item is reported or updated, it is evaluated against active opposite-type records using an additive point system:

$$\text{Total Score} = S_{\text{category}} + S_{\text{name}} + S_{\text{brand}} + S_{\text{color}} + S_{\text{location}} + S_{\text{keywords}}$$

| Attribute | Points | Criteria & Logic |
| :--- | :---: | :--- |
| **Category** | **+30** | Exact category match (e.g. `Laptop` == `Laptop`) |
| **Similar Name** | **+25** | Token overlap OR Levenshtein/difflib Sequence ratio $\ge 0.60$ |
| **Same Brand** | **+15** | Non-empty case-insensitive substring or exact brand equality |
| **Same Color** | **+10** | Color keyword match (e.g. `Silver`, `Blue`, `Black`) |
| **Same/Nearby Location** | **+10** | Significant location token match (e.g. `Library`, `Canteen`) |
| **Description Keywords** | **+10** | Filtered non-stopword keyword intersection $\ge 1$ |
| **Maximum Score** | **100** | Capped at 100 points |

### Match Discovery Threshold: $\ge 50$ points
- Any Lost-Found pairing reaching **50 points or higher** creates a permanent `Match` record.
- Both item statuses automatically transition from `Open` to `Possible Match`.
- Both reporting users receive in-app notifications with a clear explanation:
  *Example*: `"Same category, similar item name, same brand, and same color."*

---

## 🔑 Demo Login Credentials

The project includes pre-configured demo accounts for college evaluation and presentations:

| Role | Name | Department | Email Address | Password |
| :--- | :--- | :--- | :--- | :--- |
| **Administrator** | Dr. Sunita Kulkarni | Campus Operations | `admin@vsit.edu.in` | `Admin@123` |
| **Student 1** | Aarav Sharma | B.Sc. IT | `aarav.sharma@vsit.edu.in` | `Student@123` |
| **Student 2** | Priya Patel | B.Sc. CS | `priya.patel@vsit.edu.in` | `Student@123` |
| **Student 3** | Rohan Deshmukh | BMS | `rohan.deshmukh@vsit.edu.in` | `Student@123` |

---

## 💻 Installation & Setup Guide

### 1. Prerequisites
- **Python 3.10+** (Python 3.12 recommended)
- **pip** package installer

### 2. Navigate to Project Directory
```powershell
cd C:\Users\User\.gemini\antigravity\scratch\campusconnect
```

### 3. (Optional) Create and Activate a Virtual Environment
```powershell
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 5. Initialize & Seed Demo Database
```powershell
python seed.py
```
*This creates `lost_found.db` and populates realistic users, items, matches, claims, and notifications.*

### 6. Run the Application
```powershell
python app.py
```
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Testing Instructions

Run the full automated test suite containing 23 tests covering authentication, reporting, matching formulas, claims, and access permissions:

```powershell
python -m unittest discover tests
```

To run end-to-end workflow verification across all 4 key user journeys:
```powershell
python verify_workflows.py
```

---

## 📸 Screenshots Section (Placeholders)

| Screen | Description |
| :--- | :--- |
| **Home Page** | Hero section with campus metrics, recent cards, and 3-step guide |
| **Search Catalog** | Responsive multi-attribute filter sidebar with pagination |
| **Item Details** | Full specs, photo view, privacy-safe contact modal, and claim triggers |
| **Admin Dashboard** | Chart.js visual analytics, pending claims review, and return controls |
| **Smart Matches** | Paired Lost & Found cards with match score breakdown |

---

## 🔮 Future Enhancements
- **QR Code Asset Tagging**: Generate campus QR stickers for student laptops, student IDs, and water bottles.
- **Campus SMS / Push Gateway**: Optional opt-in WhatsApp or SMS alerts for verified claims.
- **Campus Map Integration**: Interactive Leaflet.js campus map displaying incident pins by building block.
- **Optical Character Recognition (OCR)**: Automatic text extraction from photos of misplaced student ID cards.

---

## ⚠️ Limitations
- File uploads are stored locally in `static/uploads/` rather than a distributed cloud CDN.
- In-app notification delivery is synchronous upon database write; email dispatch is omitted to prevent external SMTP dependencies.
- Single-institution scope tailored specifically for the **VSIT (Vidyalankar School of Information Technology)** campus environment.

---

## 👥 Team Member Contributions
- **Full-Stack Architecture & Backend**: Database modeling, RESTful routes, matching engine, authentication, and test suite.
- **Frontend UI/UX Design**: Responsive Jinja2 templates, Bootstrap 5 styling, CSS theme, and interactive Chart.js analytics.
- **Quality Assurance & Verification**: Unit testing, security validation, and workflow test automation.
- **Technical Documentation**: Comprehensive README and university Project Report compilation.
