from sqlalchemy.orm import Session

from database import models
from database import schemas


def get_meetings(db: Session):
    return db.query(models.Meeting).all()


def get_meeting(db: Session, meeting_id: int):
    return db.query(models.Meeting).get(meeting_id)


def schedule_meeting(db: Session, meeting: schemas.Meeting):
    db_meeting = models.Meeting(start_time=meeting.start_time, end_time=meeting.end_time,
                                required_seats=meeting.required_seats)
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    return db_meeting


# just for developing
def delete_meeting(db: Session, meeting: schemas.Meeting):
    db.delete(meeting)
    db.commit()
