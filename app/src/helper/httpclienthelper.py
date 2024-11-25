from enum import Enum
import aiohttp
from typing import Dict, Any, Tuple
import logging


class HttpHelper:
    def __init__(self, headers: Dict[str, str], timeout: int = 10, max_retries: int = 3):
        """
        Initializes the HTTP helper.

        :param headers: Default headers to be included in all requests.
        :param timeout: Timeout for requests in seconds.
        :param max_retries: Number of retries for transient errors.
        """
        self.headers = headers
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)

    async def _request(
        self, method: str, url: str, params: Dict[str, Any] = None, data: Dict[str, Any] = None
    ) -> Tuple[Dict[str, Any], int]:
        """
        Handles the core HTTP request.

        :param method: HTTP method (GET, POST, etc.).
        :param url: The endpoint URL.
        :param params: Query parameters for the request.
        :param data: JSON payload for the request.
        :return: A tuple of the response data and HTTP status code.
        """
        retries = 0

        while retries <= self.max_retries:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                try:
                    async with session.request(
                        method, url, headers=self.headers, params=params, json=data
                    ) as response:
                        json_data = await response.json()
                        self.logger.info(f"{method} {url} - Status: {response.status}")
                        if response.status == HttpStatusCode.OK.value:
                            return {
                                "status": "success",
                                "message": json_data.get("message", ""),
                                "data": json_data,
                            }, response.status
                        elif response.status == HttpStatusCode.CREATED.value:
                            return {
                                "status": "success",
                                "message": json_data.get("message", ""),
                                "data": json_data,
                            }, response.status
                        elif response.status == HttpStatusCode.UNAUTHORIZED.value:
                            return {
                                "status": "error",
                                "message": json_data.get("error").get("message")
                                ,
                                "data": [],
                            }, response.status
                        else:
                            self.logger.warning(f"Request failed with status {response.status}: {json_data}")
                            return {
                                "status": "error",
                                "message": json_data.get("error")
,
                                "data": [],
                            }, response.status

                except aiohttp.ClientResponseError as e:
                    self.logger.error(f"HTTP Error: {e.message}")
                    return {
                        "status": "error",
                        "message": f"HTTP Error: {e.message}",
                        "data": [],
                    }, e.status

                except aiohttp.ClientError as e:
                    self.logger.error(f"Request Error: {str(e)}")
                    retries += 1
                    if retries > self.max_retries:
                        return {
                            "status": "error",
                            "message": f"Request Error after retries: {str(e)}",
                            "data": [],
                        }, 500

                except Exception as e:
                    self.logger.error(f"Unexpected Error: {str(e)}")
                    return {
                        "status": "error",
                        "message": f"Unexpected Error: {str(e)}",
                        "data": [],
                    }, 500

    async def get(self, url: str, params: Dict[str, Any] = None) -> Tuple[Dict[str, Any], int]:
        """
        Sends a GET request.

        :param url: The endpoint URL.
        :param params: Query parameters for the request.
        :return: A tuple of the response data and HTTP status code.
        """
        return await self._request("GET", url, params=params)

    async def post(self, url: str, data: Dict[str, Any] = None) -> Tuple[Dict[str, Any], int]:
        return await self._request("POST", url, data=data)

    async def put(self, url: str, data: Dict[str, Any] = None) -> Tuple[Dict[str, Any], int]:
        return await self._request("PUT", url, data=data)

    async def patch(self, url: str, data: Dict[str, Any] = None) -> Tuple[Dict[str, Any], int]:
        return await self._request("PATCH", url, data=data)

    async def delete(self, url: str, params: Dict[str, Any] = None) -> Tuple[Dict[str, Any], int]:
        """
        Sends a DELETE request.

        :param url: The endpoint URL.
        :param params: Query parameters for the request.
        :return: A tuple of the response data and HTTP status code.
        """
        return await self._request("DELETE", url, params=params)


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
