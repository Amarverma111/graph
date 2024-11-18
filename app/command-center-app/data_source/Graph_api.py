import requests


class MSFTGraph:
    def __init__(self, client_id: str, client_secret: str, tenant_id: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.access_token = None

    def get_access_token(self, config):
        """Fetch the access token from Azure."""
        if self.access_token:
            return self.access_token  # Return the cached token if it's already fetched
        url = f"{config['GRAPH_API__AUTH']}/{self.tenant_id}/oauth2/v2.0/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        SCOPE=None
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": SCOPE,
            "grant_type": "client_credentials"
        }
        try:
            data = self._extracted_from_get_access_token_18(url, headers, data)
            return data
        except requests.exceptions.RequestException as e:
            # Handle request exceptions (e.g., network issues, invalid request)
            raise Exception(f"Failed to get access token: {str(e)}") from e

        except ValueError as e:
            # Handle cases where the token is missing from the response
            raise Exception(f"Error parsing token: {str(e)}") from e

    # TODO Rename this here and in `get_access_token`
    def _extracted_from_get_access_token_18(self, url, headers, data):
        self.access_token="EwCIA8l6BAAUbDba3x2OMJElkF7gJ4z/VbCPEz0AATS5R8/R21/Ojae54Lo1ZUWEg8O2zMjQ/pPsW8nh/06DTwIUcF8S7BfFqUQqXm3mVbRPLirDw75eL9n7PT5xEs+j7HsY5z1IT2QFm5UyC4MiKMe56dOZgOlS3Eb8va7eM0u/+veuS+YJW8ymmMPCbbe3Nqi78KINNW3oy7SB0c8W7XrJSrdCOst27nOPKjLbNxcwTYxOdj0X6KJZj694o1AkRybttYzyl8HPHRYugdPJ2VCapdU8p+pNKbl29Swy+LLPZotjo449p+Esuq0r1VQqgbZTaPOXWXNtOdRaepBs0O2DWYrNdWyOWdTZGbxsC9c2sS85ycm833f6uEm/gRoQZgAAEJATfGzQbzkIMw1l64/jbKVQAseW2IPXgeE1PHp6sZ5PXjSqqfFwoxlI1UTLgf4NlL0L+1a6DlqNYZgDnb9GsZNXAAMQXsiPx0C1I6IIGO5wsCnRivYHMgXA4PPTKHQs9O+/z01AZSSI4Jx+LU9YhEkMf5CE2hIvHOcgU0tdtMsr4bbUsUMNq/sz/pjXWchrv6Fo1mRZa7vbxbb/CoRNSXiykl6S+5ZJvb0FK49U7JfniMtEoOTeoi5dR363YgWXelivXgal0oVV/a2Ii8TFd5OMc/bRTCwhBc9cIwlvHOQJGT+3T+KGqx564YFK7EmOL/KzAXTlJxNuAusvzyXnN0LCl2qmLX+JKi9Li/C4deMaSvzrgHVWYswXkBY8H8ID2VeTxjkPLsERKCQdv2qIZFEapOGd28CwRaLZ2//kVZ9U7yhgwRSWGDGYx/B4JPsYj5vnQKEEX1xzvrlju6RfiHpsU3v/xwr1U4c058FsCkaq4eEBS2bjcvE/70WSq5a+T9SkhIGjwHccBullL0QipzcMLoQyncktv1SfuDLi3Mhi4JE8zf2D6kUWQZlDIVrOxp+A+WpkktTyVAjP100zIo9ATwaoUQdZWwlM65hOTC9ujBGZxhQ+7VHBE+i3Q0xythdugFoYPyLD3K2oWuEiterof0B434tQ3OBMoUHlpzWoaJqbn92t68O/o793HQXnBMViywSdITDi5O1MQXaa8YWfSUGBGWegEjYanxqXD/LiayQ2mJeyuJBM0/me5N8bHXPN1e3nI8Z8n46vBcbrizQ4lBO0BDuVcEhiJ/7r8m5hEhyJAg=="
        # response = requests.post(url, headers=headers, data=data)
        # response.raise_for_status()  # Raise an exception if there is an HTTP error
        # response_data = response.json()
        # self.access_token = response_data.get("access_token")  # Store the token
        #
        # if not self.access_token:
        #     raise ValueError("Access token not found in the response")

        return self.access_token


