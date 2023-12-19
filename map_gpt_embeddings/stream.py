import os

from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.streams import RESTStream
import requests
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential

class OpenAIStream(RESTStream):
    """OpenAI stream class."""
    name = "openai"
    rest_method = "POST"

    @property
    def path(self):
        if self.config.get("deployment_name", None):
            return f"/openai/deployments/{self.config.get('deployment_name')}/embeddings?api-version=2023-05-15"
        else:
            return "/v1/embeddings"

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
            scope = "https://cognitiveservices.azure.com/.default"
            if self.config.get("msi_client_id", None):
                creds = ManagedIdentityCredential(client_id=self.config.get("msi_client_id"))
                token = creds.get_token(scope).token
            else:
                creds = DefaultAzureCredential()
                token = creds.get_token(scope).token


        return BearerTokenAuthenticator(
            stream=self,
            token=token,
        )


    @property
    def url_base(self) -> str:
        
        base_url = self.config.get("api_endpoint", "https://api.openai.com")
        self.logger.info(f"Using API endpoint: {base_url}")
        return base_url


    def prepare_request_payload(
        self,
        context,
        next_page_token,
    ):
        return {
            "input": context["text"].replace("\n", " ")
        }
