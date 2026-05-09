from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ok",
                "service": "College Exploration API",
                "environment": "development",
                "version": "0.3.0",
                "timestamp": "2026-05-09T12:00:00Z",
            }
        }
    )

    status: Literal["ok"]
    service: str
    environment: str
    version: str
    timestamp: datetime


class ReadyResponse(BaseModel):
    status: Literal["ready"]
    database: Literal["ok"]
    timestamp: datetime
