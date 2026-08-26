# Bhoomi.ai Development Conventions

## 1. Repository Structure
The project maintains strict boundaries to prevent architectural coupling:
- `backend/`: FastAPI application code and API runtime.
- `frontend/`: React application (future).
- `ml/`: Reusable machine learning components, model definitions, and pipeline code.
- `notebooks/`: Experimental Colab notebooks for research. Not for production runtime.
- `data/`: Data organization. Raw and large datasets are strictly kept locally (or in external storage) and NOT committed.
- `docs/`: Technical documentation (architecture, API contracts, etc.).
- `tests/`: Integration, cross-component, and end-to-end tests. (Backend-specific unit tests reside in `backend/tests/`).
- `scripts/`: Maintenance, setup, and data prep utilities.

## 2. Backend Layer Responsibilities
- **`app/main.py`**: Application entry point. Configures FastAPI and registers routes. No business logic, ML, or agent reasoning.
- **`app/api/`**: HTTP interface layer. Handles validation and routing. Calls services/agents—does NOT implement domain logic.
- **`app/agents/`**: LangGraph nodes/workflows and decision logic. Coordinates tools and models. Agents must not implement HTTP endpoints or directly execute raw SQL queries.
- **`app/tools/`**: Deterministic capabilities (e.g., NDVI calc, weather fetch) exposed for agents. No conversational reasoning.
- **`app/services/`**: Application services for orchestrating API workflows or shared domain logic. Do not arbitrarily place agent/model logic here.
- **`app/models/`**: Domain models (e.g., Pydantic schemas, future DB entities).
- **`app/config/`**: Minimal application settings using `pydantic-settings`. No hardcoded secrets.
- **`app/utils/`**: Genuinely shared utilities.

## 3. ML vs Notebook Distinction
- **Notebooks** (`notebooks/`) are for dataset exploration, prototyping, and training experiments via Google Colab.
- **ML Module** (`ml/`) houses mature preprocessing steps, model architecture classes, and standardized inference utilities that can be imported or served in production.

## 4. Data Directory Rules
The `data/` directory is strictly organizational (e.g., `data/raw/`, `data/processed/`, `data/external/`). 
**Large, raw, or sensitive datasets must NOT be committed to Git.**

## 5. Testing Boundaries
- `backend/tests/`: Tightly coupled API, unit, and backend service tests.
- `tests/` (root): Broad, cross-component integration tests verifying end-to-end system flows.

## 6. Dependency Management
- **Backend**: Managed via `backend/requirements.txt`.
- **ML**: Managed via `ml/requirements-ml.txt`.
- **Notebooks**: Install required packages inline within Google Colab cells.
- **Rule**: Do not introduce unified dependency managers (Poetry, Conda) or merge backend and ML dependencies. Keep boundaries isolated.

## 7. Import and Coupling Rules
- API routes must not contain ML algorithms.
- API routes should abstract external fetch requests via Services or Tools.
- Agents must not contain HTTP route definitions.
- Frontend communicates exclusively with backend HTTP APIs.
- Avoid circular imports across the architectural layers.

## 8. Naming Conventions
- **Python**: `snake_case` (modules, variables, functions), `PascalCase` (classes), `UPPER_SNAKE_CASE` (constants).
- **React/Frontend**: Standard React conventions (components in `PascalCase`).
- **API Routes**: RESTful resource naming (e.g., `/api/v1/advisory`).

## 9. Environment and Secrets
- `.env.example`: Committed placeholder file indicating required environment variables.
- `.env`: Local-only file (ignored by Git). Never commit real API keys or credentials.

## 10. Git Conventions
We use a lightweight prefix-based branch and commit convention.

**Branch Names:**
- `feat/` (e.g., `feat/satellite-agent`)
- `fix/` (e.g., `fix/ndvi-calculation`)
- `docs/` (e.g., `docs/architecture`)
- `chore/` (e.g., `chore/update-dependencies`)
- `refactor/` (e.g., `refactor/agent-state`)
- `test/` (e.g., `test/advisory-api`)

**Commit Messages:**
Use the corresponding prefix in the message (e.g., `feat: add satellite integration tool`). An overly rigid Conventional Commits spec is not strictly enforced beyond this clear semantic prefixing.
