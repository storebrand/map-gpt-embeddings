import os

from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.streams import RESTStream
import requests

class OpenAIStream(RESTStream):
    name = "openai"
    path = "/v1/embeddings"
    rest_method = "POST"

    @property
    def http_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
        }

    @property
    def authenticator(self):

        if self.config.get("openai_api_key", False):
            token = self.get_msi_token()
        else:
            token = self.config.get("openai_api_key", os.environ.get("OPENAI_API_KEY"))
            
        return BearerTokenAuthenticator(
            stream=self,
            token=token,
        )


    @property
    def url_base(self) -> str:
        base_url = self.config.get("api_endpoint", "https://api.openai.com")
        return base_url

    @classmethod
    def get_msi_token():
        auth_url = "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https%3A%2F%2Fcognitiveservices.microsoft.com%2F/.default"
        headers = {"Metadata": "true"}
        mi_token = requests.get(auth_url, headers=headers)

        mi_token.raise_for_status()

        token = mi_token.json()["access_token"]

        return token


    def prepare_request_payload(
        self,
        context,
        next_page_token,
    ):
        return {
            "input": context["text"].replace("\n", " "),
            "model": context["model"],
        }
