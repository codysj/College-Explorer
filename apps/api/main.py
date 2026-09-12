from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware

from api.routes.health import router as health_router
from api.routes.analytics import router as analytics_router
from api.routes.cost_calculator import router as cost_calculator_router
from api.routes.decision import router as decision_router
from api.routes.rankings import router as rankings_router
from api.routes.semantic_search import router as semantic_search_router
from api.routes.sensitivity import router as sensitivity_router
from api.routes.schools import router as schools_router
from core.config import get_settings
from core.errors import (
    http_exception_handler,
    pydantic_validation_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Backend API foundation for the College Exploration Platform.",
    )
    if settings.cors_origin_list:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origin_list,
            allow_credentials=False,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["*"],
        )
    app.include_router(health_router)
    app.include_router(schools_router)
    app.include_router(rankings_router)
    app.include_router(semantic_search_router)
    app.include_router(decision_router)
    app.include_router(cost_calculator_router)
    app.include_router(sensitivity_router)
    app.include_router(analytics_router)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(PydanticValidationError, pydantic_validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
    return app


app = create_app()
