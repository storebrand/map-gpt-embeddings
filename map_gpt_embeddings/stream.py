import os

from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.streams import RESTStream
import requests
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential

class OpenAIStream(RESTStream):
    name = "openai"
    path = "/v1/embeddings"
    rest_method = "POST"

    @property
    def path(self):
        return self.config.get("path", "/v1/embeddings")

    @property
    def http_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
        }

    @property
    def authenticator(self):

        if self.config.get("openai_api_key", False):
            token = self.config.get("openai_api_key", os.environ.get("OPENAI_API_KEY"))
        else:
            scope = "https://cognitiveservices.azure.com/.default""
            if self.config.get("msi_client_id", None):
                creds = ManagedIdentityCredential(client_id=self.config.get("msi_client_id"))
                token = creds.get_token(scope)
            else:
                creds = DefaultAzureCredential()
                token = creds.get_token(scope)


        return BearerTokenAuthenticator(
            stream=self,
            token=token,
        )


    @property
    def url_base(self) -> str:
        base_url = self.config.get("api_endpoint", "https://api.openai.com")
        return base_url


    def prepare_request_payload(
        self,
        context,
        next_page_token,
    ):
        return {
            "input": context["text"].replace("\n", " "),
            "model": context["model"],
        }
