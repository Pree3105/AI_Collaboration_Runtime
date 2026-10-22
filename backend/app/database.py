from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

SessionLocal = async_sessionmaker(autocommit=False,autoflush=False,expire_on_commit=False,)
_engine: AsyncEngine | None = None


class Base(DeclarativeBase):
    pass


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        from app.config import settings
        _engine = create_async_engine(settings.database_url)
    return _engine

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal(bind=get_engine()) as db:
        yield db



def get_redis_client() -> "redis.Redis":
    import redis

    from app.config import settings

    return redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=0,
        decode_responses=True,
    )


NEO4J_CONSTRAINTS = (
    "CREATE CONSTRAINT task_id_unique IF NOT EXISTS "
    "FOR (t:Task) REQUIRE t.id IS UNIQUE",
    "CREATE CONSTRAINT execution_step_id_unique IF NOT EXISTS "
    "FOR (s:ExecutionStep) REQUIRE s.id IS UNIQUE",
    "CREATE CONSTRAINT decision_id_unique IF NOT EXISTS "
    "FOR (d:Decision) REQUIRE d.id IS UNIQUE",
)


def init_neo4j() -> None:
    from neo4j import GraphDatabase

    from app.config import settings

    driver = GraphDatabase.driver(
        settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password)
    )
    try:
        with driver.session() as session:
            for constraint in NEO4J_CONSTRAINTS:
                session.run(constraint)
    finally:
        driver.close()
