# Healthcare Backend System API

A secure, enterprise-grade healthcare backend system built with **Django**, **Django REST Framework (DRF)**, **PostgreSQL**, and **JWT Authentication** (`djangorestframework-simplejwt`).

This backend allows users to register, log in, and securely manage patient health records, doctor registries, and patient-doctor care assignments with strict multi-tenant isolation.

---

## 🌟 Key Features

- **JWT Authentication**: Secure stateless token authentication with access and refresh tokens via `djangorestframework-simplejwt`.
- **User Management**: Custom email-based user model with password hashing and validation.
- **Patient Management**: Full CRUD operations for patient records, strictly scoped so practitioners only access patients they created.
- **Doctor Registry**: Comprehensive physician management with specialization tracking, experience, and hospital affiliation.
- **Patient-Doctor Mapping**: Assign doctors to patients with duplicate-assignment prevention and cascading integrity.
- **PostgreSQL Database**: Configured with `psycopg` connection pooling and relational constraints.
- **Unified Error Handling**: Consistent JSON error envelope across all endpoints.
- **Interactive API Documentation**: Live Swagger UI (`/api/docs/`) and ReDoc (`/api/redoc/`) via `drf-spectacular`.
- **Dockerized**: 1-command startup via `docker compose up --build`.
- **100% Test Coverage**: Comprehensive test suite covering authentication, authorization, permissions, and edge cases.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.11+ / 3.14 |
| **Framework** | Django 6+ / Django REST Framework (DRF) 3.18+ |
| **Database** | PostgreSQL 15+ (with native ORM integration) |
| **Database Driver** | `psycopg` 3.3+ / `psycopg2-binary` |
| **Authentication** | JSON Web Tokens (`djangorestframework-simplejwt`) |
| **API Docs** | OpenAPI 3.0 via `drf-spectacular` |
| **Environment Config** | `python-dotenv` (12-Factor App methodology) |
| **Containerization** | Docker & Docker Compose |
| **Testing** | Django TestCase & `pytest-django` |

---

## 🚀 Quick Start Guide

### Option 1: Run with Docker Compose (Recommended)

1. Clone or navigate to the project directory:
   ```bash
   cd /path/to/project
   ```

2. Start PostgreSQL and the Django backend:
   ```bash
   docker compose up --build
   ```

3. The system will automatically:
   - Launch PostgreSQL on port `5432`
   - Run database migrations
   - Seed sample demo data
   - Start the server on `http://127.0.0.1:8000`

---

### Option 2: Run Locally with Python Virtual Environment

#### 1. Prerequisites
- Python 3.10+
- PostgreSQL 14+ running locally (or via Docker)

#### 2. Create and Activate Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Ensure your database credentials match:
```ini
SECRET_KEY=your-secure-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

DB_ENGINE=django.db.backends.postgresql
DB_NAME=healthcare_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

#### 5. Apply Migrations & Seed Sample Data
```bash
python manage.py migrate
python manage.py seed_data
```

#### 6. Start the Development Server
```bash
python manage.py runserver 0.0.0.0:8000
```

Access the API at: `http://127.0.0.1:8000/`  
Access Swagger UI at: `http://127.0.0.1:8000/api/docs/`

---

## 🔑 Demo Credentials (from `seed_data`)

| Role | Email | Password |
|---|---|---|
| **Admin** | `admin@healthcare.com` | `AdminPass123!` |
| **Staff / Doctor** | `staff@healthcare.com` | `StaffPass123!` |

---

## 📖 API Documentation & Endpoints

### 1. Authentication APIs

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/auth/register/` | Register a new user (`name`, `email`, `password`) | No |
| `POST` | `/api/auth/login/` | Log in with `email` and `password`, returns JWT tokens | No |
| `GET` | `/api/auth/me/` | Retrieve current authenticated user profile | Yes (Bearer) |
| `POST` | `/api/auth/token/refresh/` | Refresh expired access token | No |

---

### 2. Patient Management APIs

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/patients/` | Add a new patient (assigned to authenticated user) | Yes (Bearer) |
| `GET` | `/api/patients/` | Retrieve all patients created by the authenticated user | Yes (Bearer) |
| `GET` | `/api/patients/<id>/` | Get details of a specific patient | Yes (Bearer) |
| `PUT` | `/api/patients/<id>/` | Update patient details | Yes (Bearer) |
| `DELETE` | `/api/patients/<id>/` | Delete a patient record | Yes (Bearer) |

---

### 3. Doctor Management APIs

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/doctors/` | Add a new doctor record | Yes (Bearer) |
| `GET` | `/api/doctors/` | Retrieve all registered doctors | Yes (Bearer) |
| `GET` | `/api/doctors/<id>/` | Get details of a specific doctor | Yes (Bearer) |
| `PUT` | `/api/doctors/<id>/` | Update doctor details | Yes (Bearer) |
| `DELETE` | `/api/doctors/<id>/` | Delete a doctor record | Yes (Bearer) |

---

### 4. Patient-Doctor Mapping APIs

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/mappings/` | Assign a doctor to a patient | Yes (Bearer) |
| `GET` | `/api/mappings/` | Retrieve all patient-doctor mappings | Yes (Bearer) |
| `GET` | `/api/mappings/<patient_id>/` | Get all doctors assigned to a specific patient | Yes (Bearer) |
| `DELETE` | `/api/mappings/<id>/` | Remove a doctor from a patient (delete by mapping ID) | Yes (Bearer) |

---

### 5. System Health Check

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/health/` | Real-time PostgreSQL database & API status | No |

---

## 💻 Sample cURL Requests

### Register User
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Meredith Grey",
    "email": "meredith.grey@hospital.org",
    "password": "HospitalSecurePass123!"
  }'
```

### Login & Obtain JWT Token
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "meredith.grey@hospital.org",
    "password": "HospitalSecurePass123!"
  }'
```
*Response:*
```json
{
  "success": true,
  "message": "Login successful.",
  "data": {
    "user": {
      "id": 1,
      "name": "Dr. Meredith Grey",
      "email": "meredith.grey@hospital.org",
      "created_at": "2026-10-12T08:00:00Z"
    },
    "tokens": {
      "refresh": "eyJhbGciOi...",
      "access": "eyJhbGciOi..."
    }
  }
}
```

### Add a Patient
```bash
curl -X POST http://127.0.0.1:8000/api/patients/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{
    "name": "Bruce Banner",
    "age": 42,
    "gender": "Male",
    "contact_number": "+1-555-0987",
    "email": "bruce.banner@avengers.org",
    "address": "Culver University Lab",
    "medical_history": "Gamma radiation exposure, elevated pulse triggers."
  }'
```

### List User's Patients
```bash
curl -X GET http://127.0.0.1:8000/api/patients/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### Add a Doctor
```bash
curl -X POST http://127.0.0.1:8000/api/doctors/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{
    "name": "Leonard McCoy",
    "specialization": "Chief Medical Officer",
    "contact_number": "+1-555-4567",
    "email": "mccoy@starfleet.org",
    "years_of_experience": 18,
    "hospital_name": "Starfleet Medical"
  }'
```

### Assign Doctor to Patient
```bash
curl -X POST http://127.0.0.1:8000/api/mappings/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{
    "patient": 1,
    "doctor": 1,
    "notes": "Assigned for bi-weekly diagnostic review."
  }'
```

### Get All Doctors Assigned to a Specific Patient
```bash
curl -X GET http://127.0.0.1:8000/api/mappings/1/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### Remove a Doctor from a Patient
```bash
curl -X DELETE http://127.0.0.1:8000/api/mappings/1/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

---

## 🧪 Running Automated Tests

### 1. Run Django Test Suite (against PostgreSQL)
```bash
python manage.py test
```

### 2. Run with Pytest
```bash
pytest
```

### 3. Run Automated End-to-End API Verification
```bash
python verify_apis.py
```
*Output:*
```
=================================================================
🏥 HEALTHCARE BACKEND E2E API VERIFICATION TEST RUNNER
=================================================================
1. [AUTH] Registering a new doctor user... -> 201 Created
2. [AUTH] Logging in to obtain JWT tokens... -> 200 OK
3. [AUTH] Checking GET /api/auth/me/... -> 200 OK
...
✨ ALL 18 ENDPOINT CHECKS EXECUTED & PASSED WITH 100% SUCCESS! ✨
```

---

## 📬 Postman Collection

A complete Postman Collection is included at:
[`postman_collection.json`](file:///Users/pradhumay/vs/whatbyes/postman_collection.json)

**How to use in Postman:**
1. Open Postman.
2. Click **Import** and select `postman_collection.json`.
3. Set `base_url` to `http://127.0.0.1:8000`.
4. Run `1. Authentication -> Login User`. The test script automatically stores `access_token` and `refresh_token` in collection variables for all subsequent requests!

---

## 📁 Project Structure

```
├── Dockerfile                      # Production Docker container definition
├── docker-compose.yml              # Multi-container orchestration (Django + PostgreSQL)
├── requirements.txt                # Pinned Python package dependencies
├── pytest.ini                      # Pytest runner configuration
├── verify_apis.py                  # Automated 18-step E2E integration test runner
├── postman_collection.json         # Postman collection with token extraction scripts
├── .env.example                    # Template environment variables
├── .env                            # Active environment configuration
├── notes.md                        # Engineering decisions and architectural notes
├── architecture.md                 # System architecture and technical design
├── README.md                       # Comprehensive project documentation
├── manage.py                       # Django CLI management script
├── healthcare_project/             # Main Django project settings & URL configuration
│   ├── settings.py
│   ├── urls.py
│   ├── exceptions.py               # Centralized standardized JSON exception handler
│   └── wsgi.py
├── authentication/                 # App: Identity, JWT & Custom User Model
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
├── patients/                       # App: Patient Health Records & Scoped Access
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
├── doctors/                        # App: Doctor Registry
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
└── mappings/                       # App: Patient-Doctor Care Assignments
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    └── tests.py
```
