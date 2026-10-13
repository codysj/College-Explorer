import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from core.config import get_settings

settings = get_settings()

# On Lambda each container serves one request at a time and may sit frozen for minutes;
# a pool there only holds idle connections open, which keeps a scale-to-zero Postgres
# (Neon) awake. Open a connection per request instead. Lambda sets AWS_LAMBDA_FUNCTION_NAME.
_pool_args = {"poolclass": NullPool} if os.getenv("AWS_LAMBDA_FUNCTION_NAME") else {"pool_pre_ping": True}

engine = create_engine(settings.database_url, **_pool_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
