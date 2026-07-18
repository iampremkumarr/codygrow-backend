from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.dataset_utils import analyze_dataset
import os
import shutil
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
DATASET_DIR = "generated/datasets"

@router.post("/dataset/upload")
async def upload_dataset(file: UploadFile = File(...)):
    os.makedirs(DATASET_DIR, exist_ok=True)

    # ✅ Validate file type (allow common CSV MIME types and extensions)
    allowed_mime_types = [
        "text/csv",
        "application/csv",
        "text/comma-separated-values",
        "text/x-csv",
        "application/vnd.ms-excel"
    ]
    
    # Also validate by file extension as fallback
    if (file.content_type not in allowed_mime_types and
        not file.filename.lower().endswith('.csv')):
        logger.warning(f"Invalid file type: {file.content_type}, filename: {file.filename}")
        raise HTTPException(status_code=400, detail=f"Invalid file type: {file.content_type}. Please upload a CSV file.")

    import re
    # Extract only the filename to prevent directory traversal
    safe_filename = os.path.basename(file.filename)
    # Sanitize the filename to contain only alphanumeric characters, dots, dashes, and underscores
    safe_filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', safe_filename)
    file_path = os.path.join(DATASET_DIR, safe_filename)

    # ✅ Save file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        logger.info(f"Analyzing dataset: {safe_filename}")
        analysis = analyze_dataset(file_path)
        logger.info(f"Dataset analysis successful: {safe_filename}")
        return {
            "file_path": file_path,
            "filename": safe_filename,
            **analysis
        }
    except Exception as e:
        logger.error(f"Failed to analyze file {file.filename}: {str(e)}")
        # Clean up the uploaded file if analysis fails
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up failed upload: {file_path}")
        raise HTTPException(status_code=400, detail=f"Failed to analyze file: {str(e)}")
