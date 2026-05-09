from pydantic import BaseModel, ConfigDict


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"error": {"code": "http_404", "message": "Not found"}}})

    error: ErrorDetail
