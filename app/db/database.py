from sqlmodel import create_engine, Session
from os import getenv

DATABASE_URL = getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:enzo2006@localhost:5432/parcial_db"
)

engine = create_engine(
    DATABASE_URL,
    echo=getenv("ENV", "dev") == "dev"
)

def get_session():
    with Session(engine) as session:
        yield session