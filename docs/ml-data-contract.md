# ML Data Contract (Phase 1 Boundary)

This document defines the strict architectural boundary between **Bhoomi.ai Core** (Phase 0) and the **Machine Learning Pipeline** running in Google Colab (Phase 1).

## The Boundary Principle

**PostgreSQL is the single source of truth for persisted observations.**
The ML environment (Google Colab) will **never** connect directly to the production PostgreSQL database.

Instead, Bhoomi.ai provides a deterministic export artifact (via `scripts/export_observations_dataset.py`) which serves as the handoff boundary. 

### Responsibilities

**Bhoomi.ai Core (Phase 0) is responsible for:**
- Fetching raw data from external providers (Weather, GEE, SoilGrids).
- Normalizing that data into `NormalizedObservationDTO` format.
- Persisting it to PostgreSQL safely and idempotently.
- Exporting the data cleanly into Parquet/CSV formats.

**Google Colab (Phase 1) is responsible for:**
- Consuming the exported artifact.
- Exploratory Data Analysis (EDA).
- Data cleaning and null imputation.
- Feature Engineering (e.g., aggregating NDVI and Weather into usable tensors/dataframes).
- Target label creation.
- Train/Validation/Test splitting.
- ML Training, Tuning, and Evaluation.

---

## The Export Artifact Schema

The primary export artifact is `data/observations_dataset.parquet` (with a CSV fallback). It contains raw, normalized observations without any feature engineering applied.

| Column | Type | Description | Example |
|---|---|---|---|
| `field_id` | `UUID` (String) | The unique identifier of the agricultural field. | `123e4567-e89b-12d3-a456-426614174000` |
| `crop_cycle_id` | `UUID` (String) | (Optional) The specific crop cycle this observation belongs to. | `null` |
| `source` | `String` | The provider system that acquired this data. | `OpenMeteo`, `GEE_Sentinel2`, `ISRIC_SoilGrids` |
| `type` | `String` | The normalized observation type. | `Rainfall_mm`, `NDVI_Mean`, `soil_phh2o` |
| `depth_interval` | `String` | (Optional) Depth interval for soil observations. | `0-5cm`, `5-15cm` |
| `value` | `Float` or `JSON` | The recorded value. Usually a scalar float. | `6.5`, `12.4` |
| `unit` | `String` | The physical unit of the value. | `mm`, `°C`, `pH` |
| `observed_at` | `DateTime` (UTC) | The exact timestamp the physical event occurred. | `2023-10-01 12:00:00+00:00` |
| `provenance_id`| `String` | Traceable ID from the external provider (image ID, request hash). | `S2A_MSIL2A_20231001T082011_N0509_R121_T36QWF_20231001T114402` |

## Usage in Colab

To load the artifact into Pandas within Google Colab:

```python
import pandas as pd

# Load the Parquet artifact (preserves data types like DateTime)
df = pd.read_parquet("observations_dataset.parquet")

# Alternatively, if using CSV:
# df = pd.read_csv("observations_dataset.csv", parse_dates=["observed_at"])

print(df.head())
```

Once loaded, Colab data scientists are free to pivot, resample, and engineer features as required by the chosen ML models.
