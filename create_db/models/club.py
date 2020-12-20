from models.base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, LargeBinary


class Club(Base):
    __tablename__ = "clubs"

    club_id = Column(Integer, ForeignKey("players.club_id"), primary_key=True)
    club_name = Column(String)
    club_logo = Column(LargeBinary)
