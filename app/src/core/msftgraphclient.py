import os, aiohttp
from urllib.parse import urlencode
from contracts.msftgraphcontract import GetTokenBody


GRANT_TYPE_CLIENT = ""
HEADER_FORM_URL_ENCODED = ""
class MSFTGraphClient:
    async def get_access_token(self):
        try:
            body = GetTokenBody(
                client_id=os.environ["CONFIG_MSFT_GRAPH_CLIENT_ID"],
                client_secret=os.environ["CONFIG_MSFT_GRAPH_CLIENT_SECRET"],
                scope=f"{os.environ['CONFIG_MSFT_GRAPH_SCOPE']}/.default",
                grant_type=GRANT_TYPE_CLIENT,
                resource=os.environ["CONFIG_MSFT_GRAPH_SCOPE"]
            )

            body_json = body.dict()
            body_encoded = urlencode(body_json)

            headers = HEADER_FORM_URL_ENCODED

            async with aiohttp.ClientSession() as session:
                async with session.post(url=os.environ["CONFIG_MSFT_TOKENURL"], data=body_encoded,
                                        headers=headers) as response:
                    if response.status == 200:
                        response_json = await response.json()
                        return response_json
                    else:
                        return response.reason, response.status
        except Exception as e:
            return {"error": str(e)}, 500

    async def get_userdetails(self, email_id):
        access_response = await self.get_access_token()

        header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_response['access_token']}"
        }
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{os.environ['CONFIG_MSFT_GRAPH_USER_URL']}{email_id}?$select=id,department"
                async with session.get(url=url, headers=header) as response:
                    if response.status == 200:
                        response_json = await response.json()
                        return response_json, 200
                    elif response.status == 404:
                        return f"{email_id} not found", 404
                    else:
                        return response.reason, 500

        except Exception as e:
            return str(e), 500
