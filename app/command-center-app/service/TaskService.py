import requests
from requests.exceptions import HTTPError, RequestException
import time

from contracts.task import TaskResponse


class TaskServices:
    def __init__(self, access_token,config):
        self.access_token = access_token
        self.config = config
        self.headers = {
            self.config['AUTHORIZATION_HEADER']: f"{self.config['BEARER_PREFIX']} {self.access_token}",
            self.config['CONTENT_TYPE_HEADER']: self.config['CONTENT_TYPE']
        }
        self.http_helper = HttpHelper(self.headers)

    async def get_task(self, GetTaskRequest) -> TaskResponse:
        start_date = GetTaskRequest.start_date
        end_date = GetTaskRequest.end_date
        if not all([start_date, end_date]):
            # Handle missing parameters case
            response_data = TaskResponse(
                status="error",
                message="Missing required parameters",
                data={}
            )
            return response_data  # Return error response with missing parameters
        """Fetch all meetings for the user."""
        url = f"{config['GRAPH_API_ENDPOINT']}/me/todo/lists"
        response = await self.http_helper.get(url)
        if response.get("status") == "error":
            return TaskResponse(
                status="error",
                message=response["message"],
                data={}
            )
        # TaskResponse
        return  TaskResponse(
                status="error",
                message=response["message"],
                data=response.json()
            )

    async def get_sub_task(self, config,taskId,todo_list_id):
        """Fetch all meetings for the user."""
        url = f"{config['GRAPH_API_ENDPOINT']}/me/todo/lists/{todo_list_id}/tasks/{taskId}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()


    async def creat_task(self, config, displayName):
        """Fetch all meetings for the user."""
        url = f"{config['GRAPH_API_ENDPOINT']}/me/todo/lists"
        body ={
            "displayName": displayName
        }

        response = requests.post(url, headers=self.headers, json=body)
        response.raise_for_status()
        return response.json()

    async def create_sub_task(self, config, title, todo_list_id):
        """Fetch all meetings for the user."""
        url = f"{config['GRAPH_API_ENDPOINT']}/me/todo/lists/{todo_list_id}/task"
        body ={
            "title": title
        }

        response = requests.post(url, headers=self.headers, json=body)
        response.raise_for_status()
        return response.json()

    async def update_sub_task(self, config, title, todo_list_id):
        """Fetch all meetings for the user."""
        url = f"{config['GRAPH_API_ENDPOINT']}/me/todo/lists/{todo_list_id}/task"
        body = {
            "title": title
        }

        response = requests.post(url, headers=self.headers, json=body)
        response.raise_for_status()
        return response.json()

    async def delete_task(self, config, taskId, todo_list_id):
        """Fetch all meetings for the user."""
        url = f"{config['GRAPH_API_ENDPOINT']}/me/todo/lists/{todo_list_id}/tasks/{taskId}"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
