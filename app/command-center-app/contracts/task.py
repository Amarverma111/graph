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
   todo_list_id: str
   title: str

class TaskGeTSubRequest(BaseModel):
   todo_list_id: str
   taskId: str

class TaskCreateResponse(BaseModel):
    status: str
    message: str
    data: dict

class TaskSubRequest(BaseModel):
    todo_list_id: str