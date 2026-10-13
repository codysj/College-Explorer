from pydantic import ConfigDict

from schemas.base import ApiModel

class ErrorDetail(ApiModel):
    code: str
    message: str


class ErrorResponse(ApiModel):
    model_config = ConfigDict(json_schema_extra={"example": {"error": {"code": "http_404", "message": "Not found"}}})

    error: ErrorDetail
