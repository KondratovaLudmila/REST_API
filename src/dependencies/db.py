from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base


from pathlib import Path
import configparser


from ..models.user import Base


config_path = Path(__file__).parent.parent.joinpath('conf', 'config.ini')
config = configparser.ConfigParser()
config.read(config_path)

user = config.get('DB', 'user')
password = config.get('DB', 'pass')
database = config.get('DB', 'database')
host = config.get('DB', 'host')
port = config.get('DB', 'port')

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

