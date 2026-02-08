from fastapi import HTTPException, status

class NotFoundException(HTTPException):
    def __init__(self, entity: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity} not found"
        )

class DuplicateException(HTTPException):
    def __init__(self, entity: str, field: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{entity} with this {field} already exists"
        )