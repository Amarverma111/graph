from pydantic import BaseModel, Field
from datetime import datetime

# class TaskResponse(BaseModel):
#     status: str
#     message: str
#     data: []

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

class GetTaskRequest(BaseModel):
    start_date: datetime
    end_date: datetime