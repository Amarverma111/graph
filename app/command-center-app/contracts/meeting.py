from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Tuple
from quart import jsonify

class GetMeetingRequest(BaseModel):
    start_date: str
    end_date: str

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

def success_response(message, data=None):
    return jsonify({
        "status": "success",
        "message": message,
        "data": data or {}
    }), 200

def error_response(message, status_code):
    return jsonify({
        "status": "error",
        "message": message
    }), status_code

