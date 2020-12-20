from sqlalchemy.orm import relationship
from models.base import Base
from sqlalchemy import String, Integer, Column, Float, LargeBinary


class Player(Base):
    __tablename__ = "players"

    player_id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String)
    photo = Column(LargeBinary)
    dob = Column(Integer)
    club_id = Column(Integer)
    shirt_number = Column(Integer)
    position = Column(Integer)
    nationality = Column(Integer)
    # value = Column(Float(precision=2))

    value = Column(String)

    club = relationship("Club")
