import aiohttp
from typing import Dict, Any

class HttpHelper:
    def __init__(self, headers: Dict[str, str]):
        self.headers = headers

    async def _request(self, method: str, url: str, params: Dict[str, Any] = None, data: Dict[str, Any] = None) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(method, url, headers=self.headers, params=params, json=data) as response:
                    response.raise_for_status()  # Raise error for bad responses (e.g., 4xx, 5xx)
                    return await response.json()
            except aiohttp.ClientResponseError as e:
                return {"status": "error", "message": f"HTTP Error: {str(e)}", "data": []}
            except aiohttp.ClientError as e:
                return {"status": "error", "message": f"Request Error: {str(e)}", "data": []}
            except Exception as e:
                return {"status": "error", "message": f"Unexpected Error: {str(e)}", "data": []}

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
