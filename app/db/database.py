from dotenv import load_dotenv

load_dotenv(override=True)

from os import getenv
from sqlmodel import create_engine, Session

print("DATABASE_URL ENV =", getenv("DATABASE_URL"))

DATABASE_URL = getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:peumayen@localhost:5432/tpi_test"
)

print("DATABASE_URL FINAL =", DATABASE_URL)

engine = create_engine(
    DATABASE_URL,
    echo=getenv("ENV", "dev") == "dev"
)

def get_session():
    with Session(engine) as session:
        yield session
