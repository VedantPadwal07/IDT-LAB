# Fenestra Pro: Advanced Window & Door Fabrication Management

**Fenestra Pro** is an enterprise-grade, highly sophisticated web application built with Django, designed specifically for the complex needs of the fenestration (window and door) industry. Manufacturing bespoke window and door units requires navigating parametric geometry, dynamic hardware configurations, precise cutting formulas (like saw kerf deductions and glass clearance gaps), and fluctuating material costs. Traditionally, these workflows rely on cumbersome legacy desktop software or manual spreadsheet calculations. 

Fenestra Pro modernizes this entire pipeline, delivering a seamless, cloud-based, end-to-end software solution. It bridges the critical communication gap between B2B clients (builders, contractors, and architects) and the fabrication shop floor. By unifying the design, quoting, and manufacturing processes into a single source of truth, Fenestra Pro drastically reduces human error, accelerates turnaround times, and provides deep operational visibility.

The platform achieves this through a robust **dual-portal architecture**, cleanly separating workflows into specialized, highly optimized interfaces for **Customers** (who submit bespoke designs and request quotes) and **Makers / Manufacturers** (who manage real-time inventory, process orders, define pricing configurations, and oversee production analytics).

---

## 🚀 Comprehensive Key Features

### 1. Dual-Portal Architecture & Security
*   **Airtight Role Isolation:** The system utilizes a split-screen landing page routing users directly to either the Customer or Maker portal. Powered by custom Django authentication backends and strict view-layer decorators (`@customer_required` and `@maker_required`), the system guarantees absolute separation of concerns. Customers cannot access proprietary pricing algorithms, and the Maker dashboard remains unpolluted by draft designs.
*   **Stateful Session Management:** Secure tracking of user sessions allows the platform to automatically resume where the user left off, maintaining context across complex multi-step wizards or deep analytical drill-downs.

### 2. State-of-the-Art UI/UX & Theming
*   **Premium Design System:** The application leaves behind generic bootstrapped looks in favor of a curated, bespoke design language featuring "Cool Neutral" backgrounds. It leverages modern CSS techniques such as subtle glassmorphism, smooth micro-animations on hover states, and dynamic typography (e.g., the *Inter* font family) to deliver a truly state-of-the-art SaaS feel.
*   **Context-Aware Dynamic Styling:** The UI is completely theme-aware depending on the active user role:
    *   **Customer Portal:** Imbued with elegant gold accents (`--accent-gold` and `--accent-gold-dim`) to provide a premium, white-glove client-facing experience.
    *   **Maker Portal:** Utilizes sharp, professional blue tones (`--accent-blue`) tailored for high-density data visualization and manufacturing dashboards.
*   **Smart Template Rendering:** Advanced Django templating ensures that UI elements, including complex inline SVG logos, buttons, and status badges, automatically adapt their colors, strokes, and layouts to match the exact context of the current portal without requiring duplicate code.

### Customer Portal
The Customer Portal focuses on an intuitive ordering and tracking experience:
*   **Interactive Dashboard:** A high-level overview of total designs, categorized by their current status (Draft, Quoted, Approved, In Production, Completed). Includes quick summaries of recent designs and total quoted values.
*   **Multi-Step Design Wizard:** An guided process for creating window/door designs:
    1.  **Basic Information:** Design Type (Casement, Sliding, Bi-fold, Tilt & Turn, etc.), Name, and Description.
    2.  **Dimensions & Glass:** Precise millimetric dimensions (Width/Height), Panel configuration, Glass Type (Clear, Tinted, Frosted, Tempered, Double Glazed, Laminated), and Glass Thickness.
    3.  **Material & Finish:** Frame Material (uPVC, Aluminium, Wood Composite), Finish (Colors, Wood Grains, Custom RAL), and Mesh configurations.
*   **Order & Quotation Management:** Customers can bundle draft designs into Quote Requests, view detailed cost breakdowns once the maker replies, and track unit production statuses.

### Maker (Manufacturer) Portal
The Maker Portal acts as the ERP backend for the fabrication shop:
*   **Production Analytics Dashboard:** Real-time insights into total revenue, pending quote approvals, orders in production, and total registered customers.
*   **Material & Hardware Management:**
    *   `ProfileDatabase`: Tracks frame, sash, mullion, transom, and bead profiles including weight per meter, cost, standard bar lengths, and cutting waste factors.
    *   `GlassType`: Database of glass categories and their respective pricing per square meter.
    *   `HardwareItem`: Detailed inventory of handles, locks, hinges, and rollers with specific formulas (e.g., "2 per sash", "perimeter meter").
*   **Dynamic Pricing Engine:** 
    *   Powered by a `PricingConfig` singleton model that allows the manufacturer to update global markup percentages (Profile, Glass, Hardware), labor costs, overhead percentages, and tax rates globally.
*   **Algorithmic Calculation Engine:** 
    *   Uses `CuttingRule` models to define exact mathematical formulas (including saw kerf and clearance gaps) to determine profile cut lengths and hardware quantities based on the selected Window/Door design.

---

## 🛠️ Technology Stack

*   **Backend Framework:** Python 3.10+, Django 5.x
*   **Frontend UI:** HTML5, Vanilla CSS (Custom Design System), JavaScript
*   **API & Interactivity:** Django REST Framework (DRF), Django-HTMX
*   **Database:** SQLite (Development) / PostgreSQL (Production ready)
*   **Report Generation:** ReportLab (PDF Quotations), OpenPyXL (Excel exports)
*   **Image Processing:** Pillow

---

## 📂 Project Structure

```text
IDT-PROJECT/
├── fenestra_pro/               # Main Django Project Directory
│   ├── apps/
│   │   ├── accounts/           # Custom User models, Auth forms, and Role Decorators
│   │   ├── calculations/       # Cutting rules and parametric geometry algorithms
│   │   ├── dashboard/          # Customer & Maker split dashboard views
│   │   ├── designs/            # WindowDoorDesign models & Multi-step Wizard forms
│   │   ├── materials/          # Database definitions for Profiles, Glass, Hardware
│   │   ├── pricing/            # Global PricingConfig logic (Singleton Pattern)
│   │   ├── quotations/         # Quote generation and status tracking workflows
│   │   └── reports/            # PDF/Excel report generation utilities
│   ├── static/                 # CSS/JS, Fonts, and Theme Variables (landing.css)
│   ├── templates/              # HTML Templates (Base, Auth, Dashboards, Emails)
│   └── fenestra_pro/           # Django settings, WSGI/ASGI, and main URL routing
├── requirements.txt            # Project dependencies
└── venv/                       # Python Virtual Environment
```

---

## 🗄️ Database Architecture

The system utilizes highly relational models:
*   **Users:** `CustomUser` extends Django's AbstractUser, adding fields for `role` (Customer/Maker), `company_name`, and address details.
*   **Designs:** `WindowDoorDesign` stores the physical specifications. `DesignRevision` tracks historical changes to these designs.
*   **Quotations:** `Quotation` links multiple `QuotationItem` objects (which link to Designs) and tracks financial totals, validity dates, and status progression.

---

## ⚙️ Installation & Local Setup

1. **Clone the repository and navigate into the project:**
   ```bash
   cd IDT-PROJECT
   ```

2. **Activate the virtual environment:**
   *   **Windows:** `venv\Scripts\activate`
   *   **Mac/Linux:** `source venv/bin/activate`

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Navigate to the Django Root:**
   ```bash
   cd fenestra_pro
   ```

5. **Apply database migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a Superuser (Optional but recommended for Maker Portal access):**
   ```bash
   python manage.py createsuperuser
   ```
   *Note: After creating a superuser, log into the Django Admin at `/admin/` and ensure your user has the `role` set to "Maker" to view the Maker Dashboard.*

7. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
   Open your browser and navigate to `http://127.0.0.1:8000/`.

---

## 🔒 Environment Variables
For production deployment, create a `.env` file in the `fenestra_pro/` directory:
```env
DJANGO_SECRET_KEY=your-secure-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=fenestrapro.example.com,localhost,127.0.0.1
```
