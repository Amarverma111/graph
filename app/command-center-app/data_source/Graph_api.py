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
        url = f"{config['GRAPH_API__AUTH']}/{config['TENANT_ID']}/oauth2/v2.0/token"
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
        self.access_token="EwCIA8l6BAAUbDba3x2OMJElkF7gJ4z/VbCPEz0AAVQtw3F/nUvXbd5KTf/kG3CmpiXochhIukRiwfuKvAyeGntfpLqDI9nFpvehhTaHX/+LTWjG6kg9I7nau+mU6M0FY34iyinbSG0pJTXXyP9TdqA8FEH6HliP/dcxP34A5WJeXQVQtY12bd62YWSby3ntVlB71OKU5c5ARZo24H7JmQi+icZgmWTUiHGaBEqnHgKeB/57gjG2FumifJ3TVx1SNONm+2GfdxatN1vPhUWJXjXB6YWhK7k0kJ85NgIsDWbnH3FGp1Ur46oxTMqMnrDB/ErIqByL1n9OMS1FyW+H0o7fnwOd/nU9DwIEBcrR5RqcexEnMfhEgq0osEbfc5AQZgAAEIqXtEWXuPGYLjtQGC037g1QAkaee9P6x1vggH9PyTJCDhsFVu0QRl7XyvEJPckg7ak1mtSZnVo4mfmA/mL36tloMZmavLMtshdkjDsMAwwFTaLcM0ab4KpaX9SVoL74sTs3XIX9ck4P0qVB3sbIptWYBP3LbJ4LcJEznjKUtWOmB1oLRQS3NpIgWqp7tVBKN89hoNBc9YqLbLqPAJK58n4vX1wK5mQOW+0Qze5kQxYlX6pYRaq1ROMWmJd2Eg/GM9N5htXNVjQUVriBx9kTbYNNRrXJLRtFqGKxuZr0ytqo4QKEmv4aM/FEy0Z+9nmZohWLbA5B5tXJbfDMfQacUu62xk8PIPWJknxhcgJE6eHc2tie1OyprduXSc96njTl50MrrMkRzLfXGC1ciCNMX96y77L79g14+fXW3aFDp6IQmQTQbov136lp5w2PwgNuZbRFkzdxlpB9RSEUF+N5i4w6/vbB7ZaUQ/Oz6ym9Ebnb0qXAUSGzD65/YrLzQGHPZYWbnN+PZG64KPSKzAB2q3PsF2WdWj770vOWHgT53gumUXYSQCNYcEvo8JwJJ/HvbCrRiZ9R+XBiRW+n30zc77x6ZUVAkS3xxK5+gG44uzgIF1Oii//TLXUyrCJuBHNbu7+ldzuCzKWbhr/5dofU3PAG+fFkC8kiw/FopTM3XHmuYSVlCk2HwExujk53ThM/f2/+8ONl7ZwN4yDms8qa8BwSEVq72bCE2uR4GLKNksScihixUs6W2nrfJgqauH3DE+NL1a9xnjCnnFVeXCB1w87HiD7vBcg+jTu9xYcigQbIT7qJAg=="

        # response = requests.post(url, headers=headers, data=data)
        # response.raise_for_status()  # Raise an exception if there is an HTTP error
        # response_data = response.json()
        # self.access_token = response_data.get("access_token")  # Store the token
        #
        # if not self.access_token:
        #     raise ValueError("Access token not found in the response")

        return self.access_token


