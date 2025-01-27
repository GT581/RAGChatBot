from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query, Form
from sqlalchemy.orm import Session
from ..services.ingest_service import IngestService
from ..db.database import get_db
from ..core.settings import settings

router = APIRouter(prefix="/ingest")

@router.post("/upload")
async def upload_file(
    file: UploadFile,
    session_id: str,
    db: Session = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")
    
    # Check file size
    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE/1024/1024}MB"
        )
    await file.seek(0)  # Reset file position after reading
    
    ingest_service = IngestService(db)
    try:
        result = await ingest_service.process_file(file, session_id)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error processing file. Please try again.") 