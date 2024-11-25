
class GetTokenBody:
    def __init__(self, client_id: str, client_secret: str, scope: str, grant_type: str, resource):
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.grant_type = grant_type
        self.resource = resource

    def to_dict(self):
        return {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": self.scope,
            "grant_type": self.grant_type,
            "resource": self.resource
        }


class GetTokenResponse:
    def __init__(self, access_token):
        self.access_token = access_token