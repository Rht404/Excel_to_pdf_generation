# CAPSTONE PROJECT — Automated Data Insights Report
> An end-to-end AI-powered pipeline that accepts an Excel or CSV file and
> produces a fully formatted PDF report with analytical insights, business
> insights, an executive summary, and data visualizations.

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Tech Stack](#2-tech-stack)
3. [Project Structure](#3-project-structure)
4. [Architecture & Data Flow](#4-architecture--data-flow)
5. [Agent Reference](#5-agent-reference)
   - [DataAgent](#51-dataagent)
   - [InsightAgent](#52-insightagent)
   - [VizAgent](#53-vizagent)
   - [ReportAgent](#54-reportagent)
6. [Pipeline (LangGraph)](#6-pipeline-langgraph)
7. [LLM Client](#7-llm-client)
8. [Web App (FastAPI)](#8-web-app-fastapi)
9. [Supported File Formats](#9-supported-file-formats)
10. [Environment Variables](#10-environment-variables)
11. [Installation & Setup](#11-installation--setup)
12. [Running the App](#12-running-the-app)
13. [Output Files](#13-output-files)
14. [Known Limitations & Edge Cases](#14-known-limitations--edge-cases)
15. [Evolution History](#15-evolution-history)
16. [Future Improvements](#16-future-improvements)

---

## 1. Project Overview

This project takes any Excel (`.xlsx`, `.xls`, `.xlsm`, `.xlsb`, `.ods`) or
CSV (`.csv`) file as input and automatically produces a **multi-page PDF
report** containing:

- **Cover page** with file metadata and generation timestamp
- **Executive Summary** — 5 high-level bullets across all sheets
- **Dataset Overview** — per-sheet shape, column types, missing data, outliers
- **Analytical Insights** — 15 data-grounded bullet points per sheet
- **Business Insights** — 6 actionable strategic insights per sheet
- **Visualizations** — 8–10 charts per sheet (bar, pie, histogram, box plot,
  heatmap, scatter, line)

Empty sheets are automatically detected and skipped throughout the report.

---

## 2. Tech Stack

| Layer | Technology |
|---|---|
| Web framework | FastAPI |
| Templating | Jinja2 |
| Pipeline orchestration | LangGraph |
| LLM backend | Ollama (local) — `qwen2.5:7b-instruct-q4_K_M` |
| Data processing | pandas |
| Visualizations | matplotlib, seaborn |
| PDF generation | ReportLab |
| Environment management | python-dotenv |
| Concurrency safety | `threading.Lock` |
| Virtual environment | venv (`myvenv`) |
| OS / IDE | Windows, VS Code |

---

## 3. Project Structure

```
CAPSTONE_PROJECT/
│
├── agents/                        # Core processing agents
│   ├── data_agent.py              # Reads files, extracts statistics
│   ├── insight_agent.py           # LLM-powered insights + chart planning
│   ├── viz_agent.py               # Renders charts using matplotlib/seaborn
│   └── report_agent.py            # Assembles final PDF with ReportLab
│
├── app/                           # FastAPI web application
│   ├── static/
│   │   └── style.css              # Frontend stylesheet
│   ├── templates/
│   │   └── index.html             # Jinja2 HTML template
│   ├── main.py                    # FastAPI routes and upload handling
│   └── pipeline.py                # LangGraph graph definition
│
├── outputs/                       # Generated reports and charts (auto-created)
│   ├── charts/                    # PNG chart images (temp, per-run)
│   ├── history.json               # Report history log
│   └── report_<name>_<ts>.pdf     # Generated PDF reports
│
├── myvenv/                        # Python virtual environment
├── .env                           # Environment variables (not committed)
├── llm_client.py                  # Ollama HTTP wrapper with threading lock
└── requirements.txt               # Python dependencies
```

---

## 4. Architecture & Data Flow

```
Browser (index.html)
       │
       │  POST /process  (multipart file upload)
       ▼
   main.py  (FastAPI)
       │  validates extension (.xlsx / .csv)
       │  saves temp file to outputs/
       ▼
  pipeline.py  (LangGraph — serial graph)
       │
       ▼
  ┌─────────────────────────────────────────────────┐
  │                  LangGraph Nodes                │
  │                                                 │
  │  load_node                                      │
  │    └─► DataAgent.process()                      │
  │         reads file, extracts per-sheet stats    │
  │                    │                            │
  │  insights_node     │                            │
  │    └─► InsightAgent.generate_insights()         │
  │                    │                            │
  │  chart_plan_node   │                            │
  │    └─► InsightAgent.generate_chart_plan()       │
  │                    │                            │
  │  viz_node          │                            │
  │    └─► VizAgent.create_charts()                 │
  │                    │                            │
  │  exec_summary_node │                            │
  │    └─► InsightAgent.generate_exec_summary()     │
  │                    │                            │
  │  business_insights_node                         │
  │    └─► InsightAgent.generate_business_insights()│
  │                    │                            │
  │  report_node       │                            │
  │    └─► ReportAgent.generate_pdf()               │
  └─────────────────────────────────────────────────┘
       │
       ▼
  PDF saved to outputs/
       │
       ▼
  main.py returns download link
       │
       ▼
  Browser (download / history table)
```

### LangGraph Execution Order (Serial)
```
START
  → load
  → insights
  → chart_plan
  → viz  ──────────────────────┐
  → exec_summary               │
  → business_insights ─────────┤
                               ▼
                            report → END
```
> Serial execution is intentional — local Ollama handles one generation at
> a time. The `threading.Lock` in `llm_client.py` provides a second layer
> of protection if multiple web requests arrive simultaneously.

---

## 5. Agent Reference

### 5.1 DataAgent

**File:** `agents/data_agent.py`  
**Input:** File path (string)  
**Output:** Structured dict with raw DataFrames + per-sheet statistics

#### Supported formats
| Extension | Reader |
|---|---|
| `.xlsx`, `.xls`, `.xlsm`, `.xlsb`, `.ods` | `pd.ExcelFile` (multi-sheet) |
| `.csv` | `pd.read_csv` (single sheet, named after file stem) |

#### What it extracts per sheet

| Field | Description |
|---|---|
| `shape` | (rows, cols) tuple |
| `columns` | All column names |
| `numeric_cols` | Columns with numeric dtype, excluding ID columns and low-cardinality (<= 5 unique) |
| `categorical_cols` | String/object columns + low-cardinality numeric |
| `datetime_cols` | Datetime-typed columns |
| `encoded_categorical_cols` | String columns that look like ranges ("20-30", "1 to 2", "4+") |
| `missing_by_col` | Missing % per column |
| `top_categories` | Top 5 values for every categorical column |
| `numeric_describe` | count, mean, std, min, max per numeric column |
| `skewness` | Skewness per numeric column |
| `kurtosis` | Kurtosis per numeric column |
| `outliers` | IQR-based outlier count + bounds per numeric column |
| `corr` | Correlation pairs filtered to \|r\| >= 0.3 only |
| `datetime_ranges` | min, max, range_days, null_count per datetime column |
| `sample_rows` | First 20 rows, all columns, as string records |
| `column_definitions` | dtype + unique count per column |
| `data_quality_notes` | overall_missing_pct, duplicate_rows |

#### Output dict shape
```python
{
    "sheets": {
        "Sheet1": { ...per-sheet stats... },
        "Sheet2": { ... },
    },
    "sheet_names": ["Sheet1", "Sheet2"],
    "dataframes": {
        "Sheet1": <pd.DataFrame>,
        "Sheet2": <pd.DataFrame>,
    },
    "metadata": {
        "file_name": "data.xlsx",
        "sheet_count": 2,
        "file_type": ".xlsx",
    }
}
```

---

### 5.2 InsightAgent

**File:** `agents/insight_agent.py`  
**Input:** Summary dict from DataAgent  
**Output:** Text insights + JSON chart plan

#### Methods

| Method | Output | Max tokens | Temp |
|---|---|---|---|
| `generate_insights()` | 15 analytical bullets per sheet | 900 | 0.3 |
| `generate_business_insights()` | 6 strategic insights per sheet | 700 | 0.3 |
| `generate_exec_summary()` | 5 cross-sheet bullets | 400 | 0.2 |
| `generate_chart_plan()` | JSON chart spec per sheet | 1000 | 0.2 |

#### Token management (`_build_context`)
To avoid overloading the local LLM, context is filtered before sending:

| Data | What gets sent |
|---|---|
| Sample rows | Max 15 rows, max 12 columns |
| Correlations | Already filtered >= 0.3 in DataAgent |
| Outliers | Count only, zero-outlier cols excluded |
| Skewness | Only \|skew\| > 1 (notable only) |
| Kurtosis | Not sent (redundant with skewness for insights) |
| Top categories | First 8 categorical cols |
| Numeric describe | mean/std/min/max/count only (no percentiles) |
| Datetime ranges | Full (small payload) |

#### Chart plan rules
The LLM follows these smart rules when building the chart plan:
- `outlier_cols` → `box` chart
- `skewed_cols` → `hist` with more bins
- `has_correlation` → `heatmap`
- `corr_pairs` → `scatter` per pair
- Low-cardinality categorical → `pie`
- High-cardinality categorical → `bar`
- `datetime_cols` → `line` chart
- `encoded_categorical_cols` → `bar` only (never hist/box/scatter)

#### Retry logic
All LLM calls use `_safe_completion()` with:
- 6 retries maximum
- Exponential backoff: `min(2^attempt, 30)` seconds

---

### 5.3 VizAgent

**File:** `agents/viz_agent.py`  
**Input:** Summary dict, raw DataFrames, chart plan JSON  
**Output:** `{sheet: [{"path": str, "description": str}]}`

#### Supported chart types

| Type | Requires | Notes |
|---|---|---|
| `bar` | `col` | Top-N categories, wrapped labels |
| `pie` | `col` | Use only for <= 6 unique values |
| `hist` | `col` | Must be truly numeric — skipped if all NaN after conversion |
| `box` | `col` | Must be truly numeric — skipped if all NaN |
| `heatmap` | — | Computes full correlation matrix from numeric cols |
| `scatter` | `col_x`, `col_y` | Both must be truly numeric, includes trend line |
| `line` | `col_x` (datetime), `col_y` | Auto date formatting on x-axis |
| `stacked_bar` | `cols: [col1, col2]` | Cross-tab of two categoricals |

#### Key safety guard
`_to_numeric_series(df, col)` — converts a column to numeric and returns
`None` if the result is entirely NaN. All hist/box/scatter chart types check
this before rendering, preventing blank charts for string-encoded columns.

#### Chart outputs
- Saved as PNG to `outputs/charts/<sheet>_<index>_<type>.png`
- DPI: 200
- Size: 7×5 or 10×5 (wide) depending on chart type
- Heatmap: dynamic sizing based on number of columns

---

### 5.4 ReportAgent

**File:** `agents/report_agent.py`  
**Input:** Summary dict, insights, charts, exec summary, business insights  
**Output:** PDF file path string

#### PDF section order
```
1. Cover Page
2. Executive Summary
3. Dataset Overview
4. Analytical Insights
5. Business Insights
6. Visualizations
```

#### Custom paragraph styles

| Style | Used for |
|---|---|
| `CoverTitle` | Report title on cover |
| `CoverSub` | File name, type, date on cover |
| `SectionHead` | H1 section headings |
| `SubHead` | H2 sheet sub-headings |
| `InsightBullet` | Bullets with bold heading before colon |
| `BulletItem` | Plain bullet points |
| `BodyText2` | General paragraph text |
| `Muted` | Chart captions, secondary info |
| `EmptySheet` | Empty sheet notice |
| `ChapterLabel` | Chapter markers |

#### Empty sheet handling
`_is_empty_sheet(info)` returns `True` if rows == 0 or cols == 0.
Empty sheets are skipped in Overview, Insights, Business Insights,
and Visualizations — they show only a single warning line in Overview.

#### Text sanitization
`_safe_text()` strips:
- HTML special chars (`&`, `<`, `>`)
- Markdown bold (`**`)
- Markdown headers (`##`)

---

## 6. Pipeline (LangGraph)

**File:** `app/pipeline.py`

### State schema (`PipelineState`)
```python
class PipelineState(TypedDict, total=False):
    file_path        : str
    summary          : Dict[str, Any]
    insights         : Dict[str, str]
    chart_plan       : Dict[str, Any]
    charts           : Dict[str, List[Dict[str, str]]]
    exec_summary     : str
    business_insights: Dict[str, str]
    pdf_path         : str
    error            : Optional[str]
```

### Nodes
| Node | Calls | Depends on |
|---|---|---|
| `load_node` | `DataAgent.process()` | `file_path` |
| `insights_node` | `InsightAgent.generate_insights()` | `summary` |
| `chart_plan_node` | `InsightAgent.generate_chart_plan()` | `summary` |
| `viz_node` | `VizAgent.create_charts()` | `chart_plan` |
| `exec_summary_node` | `InsightAgent.generate_exec_summary()` | `summary` |
| `business_insights_node` | `InsightAgent.generate_business_insights()` | `summary` |
| `report_node` | `ReportAgent.generate_pdf()` | all above |

### Previous versions (commented out in file)
- **CrewAI version** — used `Agent`/`Task`/`Crew` with Azure OpenAI
- **LangGraph parallel version** — fanned out insights/chart_plan/exec/business concurrently (caused Ollama timeouts)
- **Current: LangGraph serial version** — all LLM calls run one after another

---

## 7. LLM Client

**File:** `llm_client.py`  
**Location:** Project root (imported as `from llm_client import get_llm_client`)

### Active implementation
`OllamaHTTPClient` — calls Ollama's OpenAI-compatible endpoint:
```
POST http://localhost:11434/v1/chat/completions
```

Response shape matches OpenAI:
```python
response["choices"][0]["message"]["content"]
```

### Threading lock
```python
_ollama_lock = threading.Lock()
```
Ensures only one `create_chat()` call hits Ollama at a time across all
threads. Works in combination with the serial LangGraph graph.

### Previous versions (commented out)
- **Azure version** — `AzureHTTPClient` using `api-key` header auth
- **Ollama v1** — same as current but without the threading lock and
  with a 180s timeout (current: 600s)

### Configuration via `.env`
```
OLLAMA_BASE=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b-instruct-q4_K_M
```

---

## 8. Web App (FastAPI)

**File:** `app/main.py`

### Routes

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Home page with upload form and report history |
| `POST` | `/process` | Accepts file upload, runs pipeline, returns result |
| `GET` | `/download/{filename}` | Serves a generated PDF |
| `GET` | `/delete/{report_id}` | Deletes a report from history and disk |
| `GET` | `/health` | Health check — returns `{"status": "ok"}` |

### File validation
```python
SUPPORTED_EXTENSIONS = {".xlsx", ".xls", ".xlsm", ".xlsb", ".ods", ".csv"}
```
Unsupported formats return an error message rendered in the template —
no pipeline is invoked.

### History
Reports are logged to `outputs/history.json` with these fields:
```json
{
  "id": "a1b2c3d4",
  "filename": "report_a1b2c3d4.pdf",
  "original_name": "sales_data.xlsx",
  "path": "/absolute/path/to/report.pdf",
  "size": "1.2 MB",
  "created_at": "2026-07-07 12:03:00 PM IST",
  "created_at_ts": 1751234580.0,
  "download_url": "/download/report_a1b2c3d4.pdf"
}
```
History is sorted newest-first on every page load.

### Frontend (`index.html` + `style.css`)
- Single-page Jinja2 template
- Upload form with file type restriction
- Success banner with download link after generation
- Error banner for unsupported file types
- History table with download and delete actions

---

## 9. Supported File Formats

| Format | Extensions | Multi-sheet |
|---|---|---|
| Excel | `.xlsx`, `.xls`, `.xlsm`, `.xlsb`, `.ods` | ✅ Yes |
| CSV | `.csv` | ❌ Single sheet (named after file) |

---

## 10. Environment Variables

Create a `.env` file in the project root:

```env
# Ollama (active)
OLLAMA_BASE=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b-instruct-q4_K_M

# Azure OpenAI (commented out — kept for reference)
# AZURE_OPENAI_API_KEY=your_key_here
# AZURE_OPENAI_BASE=https://your-resource.cognitiveservices.azure.com
# AZURE_OPENAI_DEPLOYMENT=your_deployment_name
# AZURE_OPENAI_API_VERSION=2025-01-01-preview
```

> **VS Code note:** Enable `python.terminal.useEnvFile` in VS Code settings
> so `.env` variables are injected into the integrated terminal.

---

## 11. Installation & Setup

### Prerequisites
- Python 3.11+
- [Ollama](https://ollama.com) installed and running locally
- The `qwen2.5:7b-instruct-q4_K_M` model pulled in Ollama

### Pull the Ollama model
```bash
ollama pull qwen2.5:7b-instruct-q4_K_M
```

### Create and activate virtual environment
```bash
# Windows
python -m venv myvenv
myvenv\Scripts\activate

# macOS / Linux
python -m venv myvenv
source myvenv/bin/activate
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Key dependencies (`requirements.txt`)
```
fastapi
uvicorn
python-multipart
jinja2
pandas
openpyxl
xlrd
reportlab
matplotlib
seaborn
langgraph
python-dotenv
requests
numpy
```

---

## 12. Running the App

### Start Ollama (if not already running)
```bash
ollama serve
```

### Start the FastAPI app
```bash
# From the project root
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Open in browser
```
http://localhost:8000
```

### Upload a file
1. Click **Choose Excel file**
2. Select a `.xlsx` or `.csv` file
3. Click **Generate Report**
4. Wait for processing (time depends on file size and LLM speed)
5. Click **Download PDF** when complete

---

## 13. Output Files

All outputs are saved to the `outputs/` directory:

| File | Description |
|---|---|
| `report_<name>_<timestamp>.pdf` | Final generated PDF report |
| `charts/<sheet>_<i>_<type>.png` | Chart images (generated per run) |
| `history.json` | JSON log of all generated reports |
| `<jobid>_<original_filename>` | Temp copy of uploaded file (deleted after processing) |

---

## 14. Known Limitations & Edge Cases

| Issue | Behaviour | Workaround |
|---|---|---|
| Empty sheets in Excel | Detected and skipped with a notice | None needed |
| String-encoded numeric cols (`"20-30"`, `"1 to 2"`) | Kept as categorical, hist/box/scatter skipped | Detected via `encoded_categorical_cols` |
| 100% missing column (e.g. `Unnamed: 0`) | Shown in overview table but excluded from insights context | Drop column before uploading |
| Large files (>10k rows) | LLM context may be truncated | Sample rows capped at 15 rows × 12 cols |
| Very wide datasets (>50 cols) | Categorical/correlation caps apply | Top 8 cats, corr filtered |
| Ollama not running | Pipeline fails with connection error | Run `ollama serve` first |
| Multiple concurrent uploads | Serialized by `threading.Lock` — second request waits | Expected behaviour |
| CSV with no header row | pandas assigns `0, 1, 2...` column names | Add header row before uploading |

---

## 15. Evolution History

### LLM Backend
```
Azure OpenAI (AzureHTTPClient)
  → Ollama without lock (OllamaHTTPClient v1, timeout 180s)
  → Ollama with threading.Lock (current, timeout 600s)
```

### Pipeline Orchestration
```
CrewAI (Agent/Task/Crew)
  → LangGraph parallel fan-out (insights/chart_plan/exec/business concurrent)
  → LangGraph serial (current — prevents Ollama timeout)
```

### DataAgent Improvements
```
v1: 8-col sample rows, corr capped at 12 cols, top 6 cats only
  → v2: all cols in sample, corr filtered by |r|>=0.3,
         all cats covered, outliers, skewness, kurtosis,
         datetime ranges, duplicates, encoded_categorical_cols
```

---

## 16. Future Improvements

| Area | Idea |
|---|---|
| File formats | Add JSON, Parquet, XML support (already scaffolded) |
| LLM backend | Add OpenAI / Anthropic API option via env flag |
| Charts | Add stacked area, violin plot, word cloud for text cols |
| Report | Add table of contents page with page numbers |
| Report | Add per-column detailed stats appendix |
| UI | Add progress bar / streaming status during generation |
| UI | Add preview of charts before PDF download |
| Performance | Cache DataAgent output for repeated uploads of same file |
| Quality | Add confidence scores to LLM-generated insights |
| Deployment | Docker container with Ollama bundled |
| History | Add search/filter to history table |
| History | Add re-download for reports older than current session |