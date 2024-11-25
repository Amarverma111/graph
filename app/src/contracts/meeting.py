from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Tuple
from quart import jsonify
from uuid import UUID

class GetMeetingRequest(BaseModel):
    start_date: datetime
    end_date: datetime

class CreateMeetingRequest(BaseModel):
    subject: str
    start_time: datetime
    end_time: datetime
    participants: List[Tuple[str, str]]  # List of participant email IDs or names

class MeetingResponse(BaseModel):
    status: str
    message: str
    data: dict

class GetMeetingResponse(BaseModel):
    status: str
    message: str
    data: list

class DeleteMeetingRequest(BaseModel):
    meeting_id: str
    confirm: str

class DeleteMeetingResponse(BaseModel):
    status: str
    message: str
    data: List[dict]

class UpdateMeetingRequest(BaseModel):
    meeting_id: str
    subject: str
    start_time: datetime
    end_time: datetime
    participants: List[List[str]]

class RescheduleMeetingRequest(BaseModel):
    meeting_id: str
    start_time: datetime
    end_time: datetime

class AddParticipantsRequest(BaseModel):
    meeting_id: str
    subject: str
    participants: List[List[str]]

