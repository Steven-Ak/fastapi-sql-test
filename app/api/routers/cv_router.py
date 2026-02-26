from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from app.schemas.cv_schema import CVResponse
from app.services.cv_service import CVService
from app.models.user_model import User
from app.auth.auth_deps import get_current_user
from app.core.service_deps import get_cv_service
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/cv", tags=["CV Parser"])


@router.post("/", response_model=CVResponse)
async def upload_cv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: CVService = Depends(get_cv_service),
):
    """Upload a CV PDF and extract structured information"""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    try:
        contents = await file.read()
        cv, file_url, processing_time_ms = service.upload_and_parse(
            file_bytes=contents,
            filename=file.filename,
            user_id=current_user.id,
        )
        return CVResponse(
            id=cv.id,
            user_id=cv.user_id,
            file_url=file_url,
            created_at=cv.created_at,
            updated_at=cv.updated_at,
            details=cv.details,
            processing_time_ms=round(processing_time_ms, 2),
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me", response_model=CVResponse)
def get_my_cv(
    current_user: User = Depends(get_current_user),
    service: CVService = Depends(get_cv_service),
):
    """Get current user's CV with extracted details"""
    try:
        cv, file_url = service.get_cv(current_user.id)
        return CVResponse(
            id=cv.id,
            user_id=cv.user_id,
            file_url=file_url,
            created_at=cv.created_at,
            updated_at=cv.updated_at,
            details=cv.details,
        )
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/me")
def delete_my_cv(
    current_user: User = Depends(get_current_user),
    service: CVService = Depends(get_cv_service),
):
    """Delete current user's CV"""
    try:
        service.delete_cv(current_user.id)
        return {"detail": "CV deleted successfully"}
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))