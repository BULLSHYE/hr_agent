import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

connection_string = os.getenv("DATABASE_CONNECTION_STRING")

engine = create_engine(
    connection_string,
    pool_size=10,
    max_overflow=20,
    pool_timeout=90,
)
# Create a configured "Session" class
Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

def create_tables():
    Base.metadata.create_all(engine)

def drop_tables():
    Base.metadata.drop_all(engine)

# Dependency injector for database sessions reuse in FastAPI
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()