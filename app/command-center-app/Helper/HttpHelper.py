import aiohttp
from typing import Dict, Any


class HttpHelper:
    def __init__(self, headers: Dict[str, str]):
        self.headers = headers

    async def _request(self, method: str, url: str, params: Dict[str, Any] = None, data: Dict[str, Any] = None) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(method, url, headers=self.headers, params=params, json=data) as response:
                    if 200 <= response.status < 300:
                        # Success response
                        return {
                            "status": "success",
                            "message": "Request successful",
                            "data": await response.json(),
                            "status_code": response.status,
                        }
                    elif 400 <= response.status < 500:
                        # Client error
                        return {
                            "status": "error",
                            "message": f"Client error: {response.status}",
                            "data": await response.text(),
                            "status_code": response.status,
                        }
                    elif response.status >= 500:
                        # Server error
                        return {
                            "status": "error",
                            "message": f"Server error: {response.status}",
                            "data": await response.text(),
                            "status_code": response.status,
                        }
                    else:
                        # Other responses
                        return {
                            "status": "unknown",
                            "message": f"Unhandled status code: {response.status}",
                            "data": await response.text(),
                            "status_code": response.status,
                        }
            except aiohttp.ClientResponseError as e:
                return {
                    "status": "error",
                    "message": f"HTTP Error: {str(e)}",
                    "data": [],
                }
            except aiohttp.ClientError as e:
                return {
                    "status": "error",
                    "message": f"Request Error: {str(e)}",
                    "data": [],
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Unexpected Error: {str(e)}",
                    "data": [],
                }

    async def get(self, url: str) -> Dict[str, Any]:
        return await self._request("GET", url)

    async def post(self, url: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        return await self._request("POST", url, data=data)

    async def put(self, url: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        return await self._request("PUT", url, data=data)

    async def patch(self, url: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        return await self._request("PATCH", url, data=data)

    async def delete(self, url: str) -> Dict[str, Any]:
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
