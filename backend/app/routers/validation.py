from fastapi import APIRouter, UploadFile, File, HTTPException
from ..services.ats_validator import ATSValidatorService
import shutil

router = APIRouter(
    prefix="/validation",
    tags=["validation"]
)

validator_service = ATSValidatorService()

@router.post("/validate-file")
async def validate_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        result = validator_service.validate_file(content, file.filename)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno validando archivo: {str(e)}")
