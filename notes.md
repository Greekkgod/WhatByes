# Engineering Notes & Decision Log

## 1. Project Background

This backend service was engineered for the **Healthcare Backend Assignment** to provide secure, production-ready RESTful APIs for managing users, patient health records, physician directories, and patient-doctor care assignments using Django, Django REST Framework, and PostgreSQL.

---

## 2. Key Architectural Decisions & Rationale

### 2.1. Custom User Model (`authentication.User`)
* **Decision**: Implemented an `AbstractUser` subclass with `USERNAME_FIELD = 'email'` rather than relying on Django's default username-based `auth.User`.
* **Rationale**: In modern healthcare and enterprise platforms, authentication is almost universally email-driven. Using a custom user model from migration 0 prevents painful database schema alterations later.
* **Fields**: `email` (unique index), `name` (full legal name), password (argon2/pbkdf2 hashed), timestamps.

### 2.2. JWT Authentication via SimpleJWT
* **Decision**: Used `djangorestframework-simplejwt` with Bearer tokens.
* **Rationale**: Stateless tokens avoid session table locks on high concurrency, allow frictionless horizontal autoscaling, and integrate cleanly with mobile clients and microservice boundaries.
* **Token Policy**:
  - `access`: 60 minutes lifetime.
  - `refresh`: 7 days lifetime.
  - Both access and refresh tokens are delivered upon registration and login.

### 2.3. Scoped Multi-Tenant Patient Privacy
* **Decision**: Patients created by an authenticated user are isolated to that user (`created_by=request.user`).
* **Rationale**: Healthcare data is sensitive. The requirement stated:
  `GET /api/patients/ - Retrieve all patients created by the authenticated user.`
  To avoid Indirect Object Reference (IDOR) attacks, attempting to fetch or mutate another user's patient returns an HTTP 404 (Not Found) rather than exposing the existence of that record through a 403. Superusers and staff retain administrative oversight.

### 2.4. Mapping URL Pattern Disambiguation
* **Design Challenge**:
  The assignment specified two distinct lookup endpoints:
  - `GET /api/mappings/<patient_id>/` - Retrieve all doctors assigned to a specific patient.
  - `DELETE /api/mappings/<id>/` - Remove a doctor from a patient (delete by mapping ID).
* **Solution**:
  The URL route `path("<int:lookup_id>/", MappingDetailOrPatientView.as_view())` acts as a polymorphic controller:
  - On `GET /api/mappings/<lookup_id>/`: Treats `lookup_id` as `patient_id`. Verifies the patient exists, queries all active doctor assignments for that patient, and returns the full doctor list.
  - On `DELETE /api/mappings/<lookup_id>/`: Treats `lookup_id` as the mapping's primary key (`id`), deleting the specific assignment link.
  - In addition, explicit aliases `GET /api/mappings/patient/<patient_id>/` and query parameter filtering `GET /api/mappings/?patient_id=<id>` are supported for complete API ergonomics.

### 2.5. Prevention of Duplicate Doctor-Patient Mappings
* **Constraint**: In healthcare, double-assigning the same doctor to the same patient creates ambiguous billing and clinical record collisions.
* **Solution**:
  - Model layer: `unique_together = ('patient', 'doctor')` enforced at the PostgreSQL table schema level.
  - Serializer layer: Pre-save validation returning an informative 400 Bad Request error if a duplicate link is attempted.

### 2.6. Standardized JSON Error Response Envelope
* **Decision**: Implemented `healthcare_project.exceptions.custom_exception_handler`.
* **Rationale**: Default DRF error responses can alternate between arrays, dictionary trees, or string details. Our custom handler encapsulates all failures in a standardized schema:
  ```json
  {
    "success": false,
    "status_code": 400,
    "error": {
      "message": "Human-readable summary",
      "details": { ... }
    }
  }
  ```

---

## 3. Database & Driver Configuration

* **PostgreSQL Engine**: Connected via modern `psycopg` (v3.3+) and `psycopg2-binary` fallback, running with connection pooling support.
* **12-Factor Configuration**: Environment variables loaded via `python-dotenv` with sensible defaults:
  - `DB_ENGINE`: `django.db.backends.postgresql`
  - `DB_NAME`: `healthcare_db`
  - `DB_USER`: `postgres`
  - `DB_PASSWORD`: `postgres`
  - `DB_HOST`: `localhost` / `db`
  - `DB_PORT`: `5432`
* **Test Isolation**: Django test runner provisions and tears down an isolated `test_healthcare_db` database on PostgreSQL.

---

## 4. Verification & Testing Strategy

A multi-layered test pyramid ensures zero regressions:
1. **Unit & View Tests** (`python manage.py test` / `pytest`):
   - 27 automated test cases spanning Authentication, Patients, Doctors, and Mappings.
   - 100% pass rate in < 6 seconds.
2. **End-to-End Test Harness** (`verify_apis.py`):
   - Automated script executing 18 sequential lifecycle steps across registration, token extraction, CRUD operations, mapping assignments, and system health checks.
3. **Interactive Documentation**:
   - OpenAPI 3.0 / Swagger UI enabled via `drf-spectacular` at `/api/docs/` and ReDoc at `/api/redoc/`.
4. **Postman Collection**:
   - Ready-to-import `postman_collection.json` with pre-configured JWT token extraction scripts.

---

## 5. Security & Compliance Roadmap for Production

For enterprise HIPAA/GDPR clinical deployment:
1. **At-Rest Encryption**: Enable PostgreSQL Transparent Data Encryption (TDE) or column-level encryption for sensitive EHR fields (`medical_history`).
2. **Audit Logging**: Implement an immutable changelog (`django-simple-history` or `auditlog`) recording who viewed or modified patient records.
3. **Rate Limiting**: Enforce DRF throttling (`AnonRateThrottle`, `UserRateThrottle`) to protect login endpoints against brute-force attacks.
4. **Token Blacklisting**: Enable `rest_framework_simplejwt.token_blacklist` to support immediate revocation upon user logout.
