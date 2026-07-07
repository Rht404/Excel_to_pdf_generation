# from fastapi import FastAPI, Request, UploadFile, File
# from fastapi.responses import FileResponse, RedirectResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from pathlib import Path
# from datetime import datetime, timedelta
# import shutil
# import json
# import uuid
# import os
# from zoneinfo import ZoneInfo


# from .pipeline import run_pipeline

# # Timezone
# IST = ZoneInfo("Asia/Kolkata")

# # Directories
# APP_DIR = Path(__file__).resolve().parent
# ROOT_DIR = APP_DIR.parent
# OUTPUTS_DIR = ROOT_DIR / "outputs"
# OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# # History file
# HIST_PATH = OUTPUTS_DIR / "history.json"

# # FastAPI app setup
# app = FastAPI()
# app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")
# templates = Jinja2Templates(directory=str(APP_DIR / "templates"))

# # ----------------------
# # History helpers
# # ----------------------
# def _load_history() -> list[dict]:
#     if not HIST_PATH.exists():
#         return []
#     try:
#         return json.loads(HIST_PATH.read_text(encoding="utf-8"))
#     except Exception:
#         return []

# def _save_history(rows: list[dict]) -> None:
#     HIST_PATH.write_text(json.dumps(rows, indent=2), encoding="utf-8")

# def _human_size(p: Path) -> str:
#     try:
#         b = p.stat().st_size
#         for unit in ["B", "KB", "MB", "GB"]:
#             if b < 1024.0:
#                 return f"{b:.1f} {unit}"
#             b /= 1024.0
#     except Exception:
#         pass
#     return "?"

# # ----------------------
# # SAS utility
# # ----------------------
# def generate_sas_url(blob_name: str) -> str:
#     conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
#     container_name = os.getenv("AZURE_CONTAINER_NAME")

#     blob_service_client = BlobServiceClient.from_connection_string(conn_str)
#     blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

#     # SAS valid for 10 days
#     sas_token = generate_blob_sas(
#         account_name=blob_client.account_name,
#         container_name=container_name,
#         blob_name=blob_name,
#         account_key=blob_service_client.credential.account_key,
#         permission=BlobSasPermissions(read=True),
#         expiry=datetime.utcnow() + timedelta(days=10),
#     )

#     return f"{blob_client.url}?{sas_token}"

# # ----------------------
# # Routes
# # ----------------------
# @app.get("/")
# def home(request: Request):
#     history = _load_history()
#     history = sorted(history, key=lambda r: r.get("created_at_ts", 0), reverse=True)
#     return templates.TemplateResponse("index.html", {"request": request, "history": history})

# @app.post("/process")
# async def process(request: Request, file: UploadFile = File(...)):
#     job_id = uuid.uuid4().hex[:8]
#     temp_xlsx = OUTPUTS_DIR / f"{job_id}_{file.filename}"
#     with temp_xlsx.open("wb") as buf:
#         shutil.copyfileobj(file.file, buf)

#     # Run pipeline -> pdf path
#     pdf_path = run_pipeline(str(temp_xlsx))  # returns string
#     local_pdf = Path(pdf_path)

#     # Upload to Azure Blob
#     try:
#         blob_name = f"report_{job_id}.pdf"
#         conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
#         container_name = os.getenv("AZURE_CONTAINER_NAME")
#         blob_service_client = BlobServiceClient.from_connection_string(conn_str)
#         blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
#         with open(local_pdf, "rb") as data:
#             blob_client.upload_blob(data, overwrite=True)

#         size_str = _human_size(local_pdf) if local_pdf.exists() else "?"
#         try:
#             local_pdf.unlink(missing_ok=True)
#         except Exception:
#             pass

#         final_download_url = f"/blob/{blob_name}"
#         final_path = OUTPUTS_DIR / f"report_{job_id}.pdf"

#     except Exception as e:
#         print("Blob upload failed:", e)
#         final_path = OUTPUTS_DIR / f"report_{job_id}.pdf"
#         try:
#             local_pdf.rename(final_path)
#         except Exception:
#             shutil.copy2(str(local_pdf), str(final_path))
#         final_download_url = f"/download/{final_path.name}"
#         size_str = _human_size(final_path)

#     # Save history row
#     now_ist = datetime.now(IST)
#     history = _load_history()
#     row = {
#         "id": job_id,
#         "filename": Path(final_download_url).name,
#         "original_name": file.filename,
#         "path": str(final_path),
#         "size": size_str,
#         "created_at": now_ist.strftime("%Y-%m-%d %I:%M:%S %p IST"),
#         "created_at_ts": now_ist.timestamp(),
#         "download_url": final_download_url,
#     }
#     history.append(row)
#     _save_history(history)

#     return templates.TemplateResponse(
#         "index.html",
#         {
#             "request": request,
#             "success": True,
#             "download_url": row["download_url"],
#             "history": sorted(history, key=lambda r: r["created_at_ts"], reverse=True),
#         },
#     )

# @app.get("/blob/{blob_name}")
# def get_blob(blob_name: str):
#     sas_url = generate_sas_url(blob_name)
#     return RedirectResponse(url=sas_url)

# @app.get("/download/{filename}")
# def download(filename: str):
#     pdf = OUTPUTS_DIR / filename
#     return FileResponse(pdf, media_type="application/pdf", filename=filename)

# @app.get("/delete/{report_id}")
# def delete(report_id: str):
#     history = _load_history()
#     keep: list[dict] = []
#     for row in history:
#         if row.get("id") == report_id:
#             try:
#                 Path(row.get("path", "")).unlink(missing_ok=True)
#             except Exception:
#                 pass
#         else:
#             keep.append(row)
#     _save_history(keep)
#     return RedirectResponse(url="/", status_code=303)

# @app.get("/health")
# def health():
#     return {"status": "ok"}


# main.py
import matplotlib
matplotlib.use("Agg")  # force non-GUI backend before ANY other import loads matplotlib

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from datetime import datetime
import shutil
import json
import uuid
from zoneinfo import ZoneInfo

from .pipeline import run_pipeline

# ... rest of main.py unchanged

# Timezone
IST = ZoneInfo("Asia/Kolkata")

# Directories
APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent
OUTPUTS_DIR = ROOT_DIR / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# History file
HIST_PATH = OUTPUTS_DIR / "history.json"

# FastAPI app setup
app = FastAPI()
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(APP_DIR / "templates"))


# ----------------------
# History helpers
# ----------------------
def _load_history() -> list[dict]:
    if not HIST_PATH.exists():
        return []
    try:
        return json.loads(HIST_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_history(rows: list[dict]) -> None:
    HIST_PATH.write_text(json.dumps(rows, indent=2), encoding="utf-8")


def _human_size(p: Path) -> str:
    try:
        b = p.stat().st_size
        for unit in ["B", "KB", "MB", "GB"]:
            if b < 1024.0:
                return f"{b:.1f} {unit}"
            b /= 1024.0
    except Exception:
        pass
    return "?"


# ----------------------
# Routes
# ----------------------
@app.get("/")
def home(request: Request):
    history = _load_history()
    history = sorted(history, key=lambda r: r.get("created_at_ts", 0), reverse=True)
    return templates.TemplateResponse(request, "index.html", {"history": history})


@app.post("/process")
async def process(request: Request, file: UploadFile = File(...)):
    job_id = uuid.uuid4().hex[:8]
    temp_xlsx = OUTPUTS_DIR / f"{job_id}_{file.filename}"
    with temp_xlsx.open("wb") as buf:
        shutil.copyfileobj(file.file, buf)

    # Run pipeline -> pdf path
    pdf_path = run_pipeline(str(temp_xlsx))  # returns string
    local_pdf = Path(pdf_path)

    # Move/rename the generated report into a stable, job-tagged filename
    final_path = OUTPUTS_DIR / f"report_{job_id}.pdf"
    try:
        local_pdf.rename(final_path)
    except Exception:
        shutil.copy2(str(local_pdf), str(final_path))

    size_str = _human_size(final_path)
    final_download_url = f"/download/{final_path.name}"

    # Clean up the uploaded source Excel file (optional — comment out if you want to keep it)
    try:
        temp_xlsx.unlink(missing_ok=True)
    except Exception:
        pass

    # Save history row
    now_ist = datetime.now(IST)
    history = _load_history()
    row = {
        "id": job_id,
        "filename": final_path.name,
        "original_name": file.filename,
        "path": str(final_path),
        "size": size_str,
        "created_at": now_ist.strftime("%Y-%m-%d %I:%M:%S %p IST"),
        "created_at_ts": now_ist.timestamp(),
        "download_url": final_download_url,
    }
    history.append(row)
    _save_history(history)

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "success": True,
            "download_url": row["download_url"],
            "history": sorted(history, key=lambda r: r["created_at_ts"], reverse=True),
        },
    )


@app.get("/download/{filename}")
def download(filename: str):
    pdf = OUTPUTS_DIR / filename
    return FileResponse(pdf, media_type="application/pdf", filename=filename)


@app.get("/delete/{report_id}")
def delete(report_id: str):
    history = _load_history()
    keep: list[dict] = []
    for row in history:
        if row.get("id") == report_id:
            try:
                Path(row.get("path", "")).unlink(missing_ok=True)
            except Exception:
                pass
        else:
            keep.append(row)
    _save_history(keep)
    return RedirectResponse(url="/", status_code=303)


@app.get("/health")
def health():
    return {"status": "ok"}