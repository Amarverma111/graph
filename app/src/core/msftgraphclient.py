import os, aiohttp
from urllib.parse import urlencode
from contracts.msftgraphcontract import GetTokenBody
from helper.httpclienthelper import HttpHelper

GRANT_TYPE_CLIENT = ""
HEADER_FORM_URL_ENCODED = ""

class MSFTGraphClient:
    def __init__(self, http_helper):
        self.http_helper = http_helper

    async def get_access_token(self):
        try:
            body = {
                "client_id": os.environ["CONFIG_MSFT_GRAPH_CLIENT_ID"],
                "client_secret": os.environ["CONFIG_MSFT_GRAPH_CLIENT_SECRET"],
                "scope": f"{os.environ['CONFIG_MSFT_GRAPH_SCOPE']}/.default",
                "grant_type": "client_credentials",
                "resource": os.environ["CONFIG_MSFT_GRAPH_SCOPE"]
            }

            body_encoded = urlencode(body)
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            url = os.environ["CONFIG_MSFT_TOKENURL"]

            # Make a POST request using the http_helper
            response, status = await self.http_helper.post(
                url, headers=headers, data=body_encoded
            )

            if status == 200:
                response_json = await response.json()
                if "access_token" in response_json:
                    return response_json["access_token"],status
                else:
                    raise ValueError("Missing 'access_token' in response.")
            else:
                raise ValueError(
                    f"Failed to fetch access token: {response.reason} (status: {status})"
                )

        except Exception as e:
            # Log and return error details
            return {"error": str(e)}, 500

    async def get_userdetails(self, email_id):
        try:
            access_token = await self.get_access_token()
            if isinstance(access_token, tuple):  # Handle error tuple from `get_access_token`
                return access_token

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
            url = f"{os.environ['CONFIG_MSFT_GRAPH_USER_URL']}/{email_id}?$select=id,department"

            # Use the http_helper for the GET request
            response, status = await self.http_helper.get(url, headers=headers)

            if status == 200:
                response_json = await response.json()
                return response_json, status
            elif status == 404:
                return {"error": f"User {email_id} not found"}, status
            else:
                return {"error": response.reason}, status

        except Exception as e:
            # Log and return error details
            return {"error": str(e)}, 500

