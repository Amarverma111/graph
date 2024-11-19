from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Tuple, Optional
from quart import jsonify

class TaskResponse(BaseModel):
    status: str
    message: str
    data: dict

class TaskCreateHeadingRequest(BaseModel):
   displayName: str

class TaskCreateSubRequest(BaseModel):
   title: str
   todo_list_id: str


class TaskCreateResponse(BaseModel):
    status: str
    message: str
    data: dict
