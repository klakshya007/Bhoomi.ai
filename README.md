# Bhoomi.ai

## Short Description
Bhoomi.ai is a software-only, multi-agent AI agricultural intelligence platform for EPICS.

## Core Philosophy
Observe → Analyze → Predict → Simulate → Explain → Advise

Bhoomi.ai aims to empower agricultural decision-making by combining multi-modal data streams with explainable AI and what-if simulation scenarios. It acts as an orchestrator of intelligence rather than merely a data wrapper, providing original feature engineering, specific ML models, and insightful recommendations.

## High-Level Capabilities
- **Observe**: Ingest data from Sentinel-2, Google Earth Engine, Weather APIs, and SoilGrids.
- **Analyze**: Process multi-modal data to extract agricultural features.
- **Predict**: Utilize self-built ML models to predict crop-stress and risks.
- **Simulate**: Run what-if agricultural simulation scenarios.
- **Explain**: Provide explainability for AI decisions using SHAP.
- **Advise**: Generate actionable recommendations based on analysis.

## High-Level Architecture
Bhoomi.ai is an intentionally hybrid architecture:
- External services provide data (Satellite, Weather, Soil).
- Bhoomi.ai internally provides agent orchestration, feature engineering, ML models, recommendation logic, simulation, and explainability.

## Technology Stack
- **Backend**: Python, FastAPI
- **Frontend**: React
- **AI/ML**: LangGraph (multi-agent orchestration), LangChain, Custom ML Models, SHAP
- **Database**: PostgreSQL/PostGIS
- **Data Integration**: Sentinel-2, Google Earth Engine, Weather APIs, SoilGrids

## Repository Structure
```
bhoomi-ai/
├── backend/    # Python/FastAPI application root
├── frontend/   # React application root
├── ml/         # ML components, model artifacts, and configuration
├── data/       # Project-level data organization (Raw/large datasets are NOT committed)
├── notebooks/  # Experimental Google Colab notebooks
├── docs/       # Architecture, API, database, agent, and project documentation
├── tests/      # Automated tests
└── scripts/    # Project utility and development scripts
```

## Development Environment
- **Local Development**: Performed using local IDEs (e.g., VS Code / Antigravity environment) for application code (backend, frontend, agents).
- **ML Experimentation**: Google Colab is utilized for resource-intensive ML experimentation and model training.

## Dependency Management
- **Frontend**: The React application will use `npm` as the package manager.
- **Python / Backend / ML**: Standard `requirements.txt` files are used (`backend/requirements.txt` and `ml/requirements-ml.txt`). Complex environment managers like Poetry or Conda are intentionally omitted to keep the setup straightforward.
- **Experimental ML**: Google Colab notebooks will install required dependencies independently within their own environments.

## Current Development Phase
**Phase 0 — Architecture & Development Environment**
We are currently establishing the repository foundation and defining the initial architecture. Application logic, models, and external integrations will be implemented in subsequent phases.

## Future Roadmap
1. **Phase 1**: Data Integration (Satellite, Weather, Soil).
2. **Phase 2**: Multi-agent Orchestration and Core Backend API.
3. **Phase 3**: Custom ML Models & Explainability (SHAP).
4. **Phase 4**: Frontend Dashboard & What-if Simulation.
5. **Phase 5**: Optional Multilingual/Voice Interaction & Refinements.
