from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from app.core.config import settings
from app.core.logging import logger


def get_engine() -> Engine:
    database_url = settings.DATABASE_URL

    connect_args = {}
    engine_kwargs = {
        "echo": False,
        "future": True,
    }

    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        engine_kwargs["connect_args"] = connect_args
    else:
        # Production PostgreSQL settings: connection pooling & pre-ping
        engine_kwargs.update({
            "pool_size": 10,
            "max_overflow": 20,
            "pool_pre_ping": True,
            "pool_recycle": 1800,
        })

    logger.info(f"Initializing database engine with target: {database_url.split('@')[-1] if '@' in database_url else database_url}")
    return create_engine(database_url, **engine_kwargs)


engine = get_engine()
