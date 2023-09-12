from datetime import datetime

from pydantic import BaseModel


class Meeting(BaseModel):
    start_time: datetime
    end_time: datetime
    required_seats: int

    class Config:
        orm_mode = True
