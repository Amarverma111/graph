import requests
from requests.exceptions import HTTPError, RequestException
import time

class TaskServices:
    def __init__(self, access_token):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    async def get_task(self, config):
        """Fetch all meetings for the user."""
        url = f"{config['GRAPH_API_ENDPOINT']}/me/todo/lists"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

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
