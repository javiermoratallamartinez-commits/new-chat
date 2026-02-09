from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql+psycopg2://postgres:1234@localhost:5432/jotaai"

engine = create_engine(
    DATABASE_URL,
    echo=True  # muestra SQL en consola (muy útil ahora)
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def init_db():
    """
    Crea las tablas en la base de datos si no existen
    """
    from app import models  # 👈 IMPORTANTE (registra los modelos)
    Base.metadata.create_all(bind=engine)
