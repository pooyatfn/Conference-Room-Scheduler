from sqlalchemy import Column, Integer, DateTime

from database.database import Base


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    required_seats = Column(Integer)
