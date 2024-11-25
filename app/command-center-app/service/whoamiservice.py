import os
from dotenv import load_dotenv
load_dotenv()


class WhoAmIService:
    def __init__(self, headers, config):
        self.access_token = None
        self.headers = headers
        self.config = config

    def get_access_token(self):
        import pdb;pdb.set_trace()
        if token := self.headers.get('Token'):
            return token

        if self.config.get('ENV') != 'localhost':
            return "Token is required in the environment, but it's missing."

        if self.config.get('ENV') == "dev":
            return os.getenv('ACCESS_TOKEN')
        # If not, check for localhost and load from .env
        if self.is_local_host(self.config.get('ENV')):
            return os.getenv('ACCESS_TOKEN')

        return "Access token not found in headers or environment variables."

    @staticmethod
    def is_local_host(host):
        # A simple check to determine if the host is localhost
        # return host in (os.getenv('LOCAL_HOST_KEY'), os.getenv('ENV'))
        return host in ("127.0.0.1", "localhost")
