from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from cpmpy import *
from database.database import SessionLocal, engine
from database import crud, schemas, models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Conference_Room:
    total_seats: int

    def __init__(self, total_seats=100):
        self.total_seats = total_seats


conference_room = Conference_Room()


@app.post('/schedule_meeting', response_model=schemas.Meeting)
def schedule_meeting(meeting: schemas.Meeting, db: Session = Depends(get_db)):
    model = Model()
    model += meeting.required_seats > conference_room.total_seats

    if model.solve():
        raise HTTPException(status_code=400, detail="The conference room does not have enough seats!")

    start_time = meeting.start_time.replace(tzinfo=None)
    end_time = meeting.end_time.replace(tzinfo=None)

    # Retrieve existing meetings from the database
    existing_meetings = crud.get_meetings(db)

    # Check for overlap with existing meetings
    for existing_meeting in existing_meetings:
        existing_start_time = existing_meeting.start_time
        existing_end_time = existing_meeting.end_time

        if has_overlap(start_time, end_time, existing_start_time, existing_end_time):
            raise HTTPException(status_code=400, detail="Meeting overlaps with an existing meeting")

    # Save the meeting in the database
    crud.schedule_meeting(db, meeting)

    return meeting


@app.get("/meetings/", response_model=list[schemas.Meeting])
def get_meetings(db: Session = Depends(get_db)):
    meetings = crud.get_meetings(db)
    return meetings


# just for developing
@app.delete("/meetings/{meeting_id}")
def delete_meeting(meeting_id: int, db: Session = Depends(get_db)):
    crud.delete_meeting(db, crud.get_meeting(db, meeting_id))
    return {"ok"}


def has_overlap(start_time_1, end_time_1, start_time_2, end_time_2):
    if start_time_1 > end_time_2 or end_time_1 < start_time_2:
        return False
    else:
        return True
