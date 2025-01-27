from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.core.settings import settings
from .document_service import DocumentService
import magic
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class IngestService:
    def __init__(self, db: Session):
        self.db = db
        self.document_service = DocumentService(db)
        self.supported_types = settings.SUPPORTED_FILE_TYPES
        
    async def process_dataframe(self, df: pd.DataFrame, session_id: str):
        content = df.to_string()
        return await self.document_service.process_document(
            session_id=session_id,
            file_content=content,
            filename="dataframe.txt",
            file_type="txt"
        )

    async def process_file(self, file: UploadFile, session_id: str):
        try:
            # Check if file is empty
            await file.seek(0)
            first_byte = await file.read(1)
            if not first_byte:
                logger.error("Empty file uploaded")
                raise HTTPException(status_code=400, detail="Empty file uploaded")
            await file.seek(0)
            
            content_type = await self._get_content_type(file)
            logger.info(f"File upload attempt - Name: {file.filename}, Type: {content_type}")
            
            if content_type not in self.supported_types:
                logger.warning(f"Unsupported file type: {content_type}. Supported types: {self.supported_types}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type. Supported types: {', '.join(self.supported_types.values())}"
                )

            content = await file.read()
            if len(content) == 0:
                logger.error("File content is empty")
                raise HTTPException(status_code=400, detail="File content is empty")
            
            file_content = self.document_service.read_file_content(content, content_type)
            
            if not file_content:
                logger.error(f"Could not extract content from file: {file.filename}")
                raise HTTPException(status_code=400, detail="Could not extract content from file")
            
            logger.info(f"Processing document - Name: {file.filename}, Size: {len(file_content)} chars")
            document = await self.document_service.process_document(
                session_id=session_id,
                file_content=file_content,
                filename=file.filename,
                file_type=self.supported_types[content_type]
            )
            
            logger.info(f"Successfully processed document: {str(document.id)}")
            return {"status": "success", "document_id": str(document.id)}
            
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    async def _get_content_type(self, file: UploadFile) -> str:
        header = await file.read(2048)
        await file.seek(0)
        mime = magic.Magic(mime=True)
        return mime.from_buffer(header) 