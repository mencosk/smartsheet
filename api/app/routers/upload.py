import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import settings
from app.services.file_processor import process_file
from app.services.ai_analyzer import analyze_data

router = APIRouter()

# In-memory store for processed DataFrames (keyed by session_id)
_dataframes: dict = {}


def get_dataframe(session_id: str):
    """Retrieve a stored DataFrame by session ID."""
    df = _dataframes.get(session_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Session not found. Please upload your file again.")
    return df


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Validate extension
    ext = Path(file.filename or "").suffix.lower()
    if ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' is not supported. Please upload a .csv or .xlsx file.",
        )

    # Read file content
    content = await file.read()

    # Validate size
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.max_file_size_mb:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds the maximum size of {settings.max_file_size_mb} MB.",
        )

    # Process the file into a DataFrame
    try:
        df = process_file(content, ext)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

    if df.empty:
        raise HTTPException(status_code=400, detail="The uploaded file contains no data.")

    # Store DataFrame with a session ID
    session_id = str(uuid.uuid4())
    _dataframes[session_id] = df

    # Generate AI analysis
    try:
        suggestions = await analyze_data(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

    return {
        "session_id": session_id,
        "rows": len(df),
        "columns": list(df.columns),
        "suggestions": suggestions,
    }
