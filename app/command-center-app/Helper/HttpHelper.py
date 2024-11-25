import aiohttp
from typing import Dict, Any
from enum import Enum

import aiohttp
from typing import Dict, Any, Tuple

class HttpHelper:
    def __init__(self, headers: Dict[str, str]):
        self.headers = headers

    async def _request(
        self, method: str, url: str, params: Dict[str, Any] = None, data: Dict[str, Any] = None
    ) -> Tuple[Dict[str, Any], int]:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    method, url, headers=self.headers, params=params, json=data
                ) as response:
                    # Return the response JSON along with the status code
                    return {
                        "status": "success",
                        "message":response['message'],
                        "data": await response.json(),
                    }, response.status
            except aiohttp.ClientResponseError as e:
                return {
                    "status": "error",
                    "message": f"HTTP Error: {e.message}",
                    "data": [],
                }, e.status
            except aiohttp.ClientError as e:
                return {
                    "status": "error",
                    "message": f"Request Error: {str(e)}",
                    "data": [],
                }, 500  # Assuming a 500 error for client-side issues
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Unexpected Error: {str(e)}",
                    "data": [],
                }, 500  # Assuming a 500 error for unknown issues

    async def get(self, url: str) -> Tuple[Dict[str, Any], int]:
        return await self._request("GET", url)

    async def post(self, url: str, data: Dict[str, Any] = None) -> Tuple[Dict[str, Any], int]:
        return await self._request("POST", url, data=data)

    async def put(self, url: str, data: Dict[str, Any] = None) -> Tuple[Dict[str, Any], int]:
        return await self._request("PUT", url, data=data)

    async def patch(self, url: str, data: Dict[str, Any] = None) -> Tuple[Dict[str, Any], int]:
        return await self._request("PATCH", url, data=data)

    async def delete(self, url: str) -> Tuple[Dict[str, Any], int]:
        return await self._request("DELETE", url)


class HttpStatusCode(Enum):
    # Successful responses
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204

    # Client error responses
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    NOT_ACCEPTABLE = 406
    REQUEST_TIMEOUT = 408
    LENGTH_REQUIRED = 411

    # Server error responses
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504


#
# import aiohttp
# from enum import Enum
#
#
# class HttpClientHelper:
#     @staticmethod
#     async def post(url, json=None, data=None, headers=None):
#         async with aiohttp.ClientSession() as session:
#             try:
#                 async with session.post(url, data=data, json=json, headers=headers) as response:
#                     if response.status == HttpStatusCode.OK.value:
#                         response_json = await response.json()
#                         return response_json, response.status
#                     else:
#                         return response.reason, response.status
#             except aiohttp.ContentTypeError as e:
#                 return response, response.status
#             except Exception as e:
#                 return f"Unexpected error: {str(e)}", HttpStatusCode.INTERNAL_SERVER_ERROR.value
#
#     @staticmethod
#     async def get(url, headers):
#         async with aiohttp.ClientSession() as session:
#             try:
#                 async with session.get(url, headers=headers) as response:
#                     if response.status == HttpStatusCode.OK.value:
#                         return response, response.status
#                     else:
#                         return response.reason, response.status
#             except Exception as e:
#                 return f"Unexpected error: {str(e)}", HttpStatusCode.INTERNAL_SERVER_ERROR.value
#
#
