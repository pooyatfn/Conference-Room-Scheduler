import datetime

from fastapi.testclient import TestClient

from database import crud, models
from database.database import SessionLocal, engine
from main import app, has_overlap

models.Base.metadata.create_all(bind=engine)


def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_schedule_meeting_with_enough_seats():
    client = TestClient(app)

    # Define meeting data with a valid number of seats
    meeting_data = {
        "title": "Test Meeting",
        "start_time": "2022-01-01T09:00:00",
        "end_time": "2022-01-01T10:00:00",
        "required_seats": 5
    }

    # Schedule the meeting
    response = client.post("/schedule_meeting", json=meeting_data)
    assert response.status_code == 200
    assert response.json() == meeting_data


def test_schedule_meeting_with_insufficient_seats():
    client = TestClient(app)

    # Define meeting data with more seats required than the conference room has
    meeting_data = {
        "title": "Test Meeting",
        "start_time": "2022-01-01T09:00:00",
        "end_time": "2022-01-01T10:00:00",
        "required_seats": 150
    }

    # Schedule the meeting
    response = client.post("/schedule_meeting", json=meeting_data)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "The conference room does not have enough seats!"
    }


def test_schedule_meeting_with_overlap():
    client = TestClient(app)

    # Define an existing meeting that overlaps with the new meeting
    existing_meeting = {
        "title": "Existing Meeting",
        "start_time": "2022-01-01T09:30:00",
        "end_time": "2022-01-01T10:30:00",
        "required_seats": 3
    }
    crud.schedule_meeting(SessionLocal(), existing_meeting)

    # Define a new meeting with overlapping time range
    new_meeting = {
        "title": "Test Meeting",
        "start_time": "2022-01-01T10:00:00",
        "end_time": "2022-01-01T11:00:00",
        "required_seats": 3
    }

    # Schedule the new meeting
    response = client.post("/schedule_meeting", json=new_meeting)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Meeting overlaps with an existing meeting"
    }


def test_schedule_meeting_with_invalid_details():
    client = TestClient(app)

    # Define meeting data with missing required fields
    meeting_data = {
        "title": "Test Meeting",
        "start_time": "2022-01-01T09:00:00"
    }

    # Schedule the meeting
    response = client.post("/schedule_meeting", json=meeting_data)
    assert response.status_code == 422


def test_get_meetings_from_empty_database():
    client = TestClient(app)

    # Retrieve all meetings
    response = client.get("/meetings/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_meetings_from_non_empty_database():
    client = TestClient(app)

    # Define a meeting in the database
    meeting_data = {
        "title": "Test Meeting",
        "start_time": "2022-01-01T09:00:00",
        "end_time": "2022-01-01T10:00:00",
        "required_seats": 5
    }
    crud.schedule_meeting(SessionLocal(), meeting_data)

    # Retrieve all meetings
    response = client.get("/meetings/")
    assert response.status_code == 200
    assert response.json() == [meeting_data]


def test_has_overlap_with_non_overlapping_ranges():
    # Define two non-overlapping time ranges
    start_time_1 = datetime.datetime(2022, 1, 1, 9, 0, 0)
    end_time_1 = datetime.datetime(2022, 1, 1, 10, 0, 0)
    start_time_2 = datetime.datetime(2022, 1, 1, 11, 0, 0)
    end_time_2 = datetime.datetime(2022, 1, 1, 12, 0, 0)

    assert not has_overlap(start_time_1, end_time_1, start_time_2, end_time_2)


def test_has_overlap_with_overlapping_ranges():
    # Define two overlapping time ranges
    start_time_1 = datetime.datetime(2022, 1, 1, 9, 0, 0)
    end_time_1 = datetime.datetime(2022, 1, 1, 10, 0, 0)
    start_time_2 = datetime.datetime(2022, 1, 1, 9, 30, 0)
    end_time_2 = datetime.datetime(2022, 1, 1, 11, 0, 0)

    assert has_overlap(start_time_1, end_time_1, start_time_2, end_time_2)


def test_has_overlap_with_one_range_inside_another():
    # Define two time ranges with one range completely inside the other
    start_time_1 = datetime.datetime(2022, 1, 1, 9, 0, 0)
    end_time_1 = datetime.datetime(2022, 1, 1, 12, 0, 0)
    start_time_2 = datetime.datetime(2022, 1, 1, 10, 0, 0)
    end_time_2 = datetime.datetime(2022, 1, 1, 11, 0, 0)

    assert has_overlap(start_time_1, end_time_1, start_time_2, end_time_2)
