from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:////home/lukasz/Python/projects/football/create_db/db/database.db")


def create_session():
    global engine
    Session = sessionmaker(bind=engine)
    return Session()
