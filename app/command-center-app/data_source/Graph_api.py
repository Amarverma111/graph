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
        self.access_token ="EwCIA8l6BAAUbDba3x2OMJElkF7gJ4z/VbCPEz0AAZFYwxSSW6xgc3nJn0wcZvXhnqRDOWQEM9Lx34MdT1A6/iXT3FkgbH8sx3iAZaybYb/aF9svaW2EeBEONtkhvopFB4i2U1sDstepzoXXkZUOxszfKMy7VJ0rcW9CYin4aZpE26hI7DTgV8w9QjTJJWVpT2YxwowaWdWLq5Y+Phejgj3c3jjNFCP4UgZVdyY2XXcrh2AmsGjHp8yn7+IEYxpSMGByKSupRBIUcLOSbDvSx+lao8H+hgs/xk1l8oCFdzr4+4QxienHF/SvHvW8BfgyJJJSaW+J6cLnBJWdHMJmztmjDRUzlZcL+XRbQ/4xexbbc78HkFabZa5BRWcSokQQZgAAEH1IK14HkWJUxtlz4eVNiaVQAu67hAyYOIwSijPawYHP5UnpCFb74JkdOVna47RE/u+FS6BoQrY1fRWsuxbcVToZnN6LisrmY8PC6BZp3art02A7EX3clO4vqg/T1A3mPvuhAxYUZSeFGL+lE0/MVfkrCoPjPsZz7eAC1kLs5T/wlSsuD8kbI6FCCRLjs4eVao6Gd8ACi3B1kjxveF5H3AmL7kk/yUF+9aXDJJ3e2+5YvzE5GV4u68i3sKwWEWgIi+cMMLXAcDcTYwvHvAsJqig5UKIpxzIgCEDBELDtMXrSfbiN/WBxQSCwEa66I8xj//O7x319NLuF3acNBhyfK7xb64jxOWmedF1WHj9flvDwfTZwJ9C5ZtIEXOpsxjqdqm0W+lxlcwOFDWAs6tBzy3yYPAJku/5ZwS0CojKX0S3A5hgE4xYQGf06N0ciKx6dl8sVCvMzliurn5x8OdDtN796lyGnwueSaJ3XJQReGJ3ibYwvO3VgPNQajs6kLWzj2ibsKJ0PqA/k5Q4BtUi6cHNsB4ezJF0AhukIbhzqW/3vl+37GBuIAFgFMMUVizlSPpjTAPXZDKIHyB0QCtDH+mGDon4jxv58+m4Z+Ac3Q45puNA1hYN6LqJ9eZACNog404VlPR7Aq7iTRPIvZ5Si30Pk4pgkOaeWC0VNYjgi/ccHLEz37HQOvHV0JOFbFiiSx15xFyS6wPBrXgTql0E/2nNMIVNy566ZbQGQZWJ/RPgbTr+QmiHUp034z9UUEwytk1DZ2PBPd3w2c6ozblrYnt5kKavwns0tfzmaRkJHtZ8jdp+JAg=="
        # response = requests.post(url, headers=headers, data=data)
        # response.raise_for_status()  # Raise an exception if there is an HTTP error
        # response_data = response.json()
        # self.access_token = response_data.get("access_token")  # Store the token
        #
        # if not self.access_token:
        #     raise ValueError("Access token not found in the response")

        return self.access_token


