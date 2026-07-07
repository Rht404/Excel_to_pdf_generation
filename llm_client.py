# # llm_client.py  (requests-based Azure wrapper)

# import os
# import json
# from dotenv import load_dotenv, find_dotenv
# import requests

# # Load .env file
# load_dotenv(find_dotenv())


# def _getenv_strip(k: str):
#     """Fetch environment variable and strip whitespace if string."""
#     v = os.getenv(k)
#     return v.strip() if isinstance(v, str) else v


# class AzureHTTPClient:
#     """
#     Lightweight wrapper that issues the exact HTTP call to the Azure
#     'cognitiveservices' openai/deployments/{deployment}/chat/completions endpoint.
#     Uses api-key authentication header.
#     """

#     def __init__(self, base: str, deployment: str, key: str, api_version: str):
#         # base should be e.g. https://<resource>.cognitiveservices.azure.com
#         self.base = base.rstrip("/")
#         self.deployment = deployment
#         self.key = key
#         self.api_version = api_version

#     def create_chat(self, messages, max_tokens: int = 800, temperature: float = 0.7, **kwargs):
#         """
#         POST to:
#         {base}/openai/deployments/{deployment}/chat/completions?api-version={api_version}
#         Returns parsed JSON (dict).
#         """
#         url = f"{self.base}/openai/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"
#         headers = {
#             "Content-Type": "application/json",
#             "api-key": self.key,
#         }
#         payload = {
#             "messages": messages,
#             "max_tokens": max_tokens,
#             "temperature": temperature,
#         }
#         # allow extra kwargs to be merged
#         payload.update(kwargs)

#         r = requests.post(url, headers=headers, json=payload, timeout=30)
#         r.raise_for_status()
#         return r.json()


# def get_llm_client():
#     """
#     Returns: (client_wrapper, deployment_name, api_version)
#     client_wrapper has method: create_chat(messages, max_tokens=..., temperature=...)
#     """
#     azure_key = _getenv_strip("AZURE_OPENAI_API_KEY")
#     azure_base = _getenv_strip("AZURE_OPENAI_BASE")
#     azure_deployment = _getenv_strip("AZURE_OPENAI_DEPLOYMENT")
#     azure_api_version = _getenv_strip("AZURE_OPENAI_API_VERSION") or "2025-01-01-preview"

#     print("DEBUG env read:")
#     print("  AZURE_OPENAI_API_KEY present:", bool(azure_key))
#     print("  AZURE_OPENAI_BASE:", azure_base)
#     print("  AZURE_OPENAI_DEPLOYMENT:", azure_deployment)
#     print("  AZURE_OPENAI_API_VERSION:", azure_api_version)

#     if not (azure_key and azure_base and azure_deployment):
#         raise RuntimeError("Missing AZURE_OPENAI_{API_KEY,BASE,DEPLOYMENT} in environment")

#     client = AzureHTTPClient(azure_base, azure_deployment, azure_key, azure_api_version)
#     return client, azure_deployment, azure_api_version



# llm_client.py  (Ollama-based client, OpenAI-compatible endpoint)

# import os
# import requests
# from dotenv import load_dotenv, find_dotenv

# # Load .env file
# load_dotenv(find_dotenv())


# def _getenv_strip(k: str, default=None):
#     """Fetch environment variable and strip whitespace if string."""
#     v = os.getenv(k)
#     if isinstance(v, str) and v.strip():
#         return v.strip()
#     return default


# class OllamaHTTPClient:
#     """
#     Lightweight wrapper that calls a locally running Ollama server via its
#     OpenAI-compatible /v1/chat/completions endpoint, so the response shape
#     (choices[0].message.content) matches what the rest of the codebase
#     already expects from the old Azure client.
#     """

#     def __init__(self, base: str, model: str):
#         self.base = base.rstrip("/")
#         self.model = model

#     def create_chat(self, messages, max_tokens: int = 800, temperature: float = 0.7, **kwargs):
#         url = f"{self.base}/v1/chat/completions"
#         payload = {
#             "model": self.model,
#             "messages": messages,
#             "max_tokens": max_tokens,
#             "temperature": temperature,
#         }
#         payload.update(kwargs)

#         # Local quantized models can be slow on CPU — generous timeout
#         r = requests.post(url, json=payload, timeout=180)
#         r.raise_for_status()
#         return r.json()


# def get_llm_client():
#     """
#     Returns: (client_wrapper, model_name, provider)
#     client_wrapper has method: create_chat(messages, max_tokens=..., temperature=...)
#     """
#     ollama_base = _getenv_strip("OLLAMA_BASE", "http://localhost:11434")
#     ollama_model = _getenv_strip("OLLAMA_MODEL", "qwen2.5:3b-instruct-q4_K_M")

#     print("DEBUG env read:")
#     print("  OLLAMA_BASE:", ollama_base)
#     print("  OLLAMA_MODEL:", ollama_model)

#     client = OllamaHTTPClient(ollama_base, ollama_model)
#     return client, ollama_model, "ollama"





# llm_client.py  (Ollama-based client, OpenAI-compatible endpoint, serialized calls)

# import os
# import threading
# import requests
# from dotenv import load_dotenv, find_dotenv

# # Load .env file
# load_dotenv(find_dotenv())

# # Local Ollama serves one generation at a time by default — this lock ensures
# # only one request from this process hits Ollama concurrently, regardless of
# # how many threads/requests call create_chat() at once.
# _ollama_lock = threading.Lock()


# def _getenv_strip(k: str, default=None):
#     """Fetch environment variable and strip whitespace if string."""
#     v = os.getenv(k)
#     if isinstance(v, str) and v.strip():
#         return v.strip()
#     return default


# class OllamaHTTPClient:
#     """
#     Lightweight wrapper that calls a locally running Ollama server via its
#     OpenAI-compatible /v1/chat/completions endpoint, so the response shape
#     (choices[0].message.content) matches what the rest of the codebase
#     already expects.
#     """

#     def __init__(self, base: str, model: str):
#         self.base = base.rstrip("/")
#         self.model = model

#     def create_chat(self, messages, max_tokens: int = 800, temperature: float = 0.7, **kwargs):
#         url = f"{self.base}/v1/chat/completions"
#         payload = {
#             "model": self.model,
#             "messages": messages,
#             "max_tokens": max_tokens,
#             "temperature": temperature,
#         }
#         payload.update(kwargs)

#         # Serialize: wait our turn before sending, so we never stack requests
#         # on top of an already-busy Ollama worker.
#         with _ollama_lock:
#             r = requests.post(url, json=payload, timeout=600)
#             r.raise_for_status()
#             return r.json()


# def get_llm_client():
#     """
#     Returns: (client_wrapper, model_name, provider)
#     client_wrapper has method: create_chat(messages, max_tokens=..., temperature=...)
#     """
#     ollama_base = _getenv_strip("OLLAMA_BASE", "http://localhost:11434")
#     ollama_model = _getenv_strip("OLLAMA_MODEL", "qwen2.5:3b-instruct-q4_K_M")

#     print("DEBUG env read:")
#     print("  OLLAMA_BASE:", ollama_base)
#     print("  OLLAMA_MODEL:", ollama_model)

#     client = OllamaHTTPClient(ollama_base, ollama_model)
#     return client, ollama_model, "ollama"




# llm_client.py — LangChain Ollama version
import os
import threading
from dotenv import load_dotenv, find_dotenv
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv(find_dotenv())

# Same lock as before — local Ollama still serves one request at a time
_ollama_lock = threading.Lock()


def _getenv_strip(k: str, default=None):
    v = os.getenv(k)
    if isinstance(v, str) and v.strip():
        return v.strip()
    return default


class LangChainOllamaClient:
    """
    Drop-in replacement for OllamaHTTPClient.
    Exposes the same create_chat(messages, max_tokens, temperature) interface
    so insight_agent.py needs zero changes.
    """

    def __init__(self, model: str):
        self.model = model
        self.llm = ChatOllama(
            model=model,
            temperature=0.7,
            num_predict=800,   # equivalent to max_tokens
            timeout=600,       # seconds
        )

    def create_chat(
        self,
        messages: list[dict],
        max_tokens: int = 800,
        temperature: float = 0.7,
        **kwargs,
    ) -> dict:
        """
        Accepts the same OpenAI-style messages list your insight_agent already sends:
        [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
        Returns a dict shaped like OpenAI's response so insight_agent.py
        (which does j["choices"][0]["message"]["content"]) keeps working unchanged.
        """
        # rebuild LangChain message objects from the plain dicts
        lc_messages = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            else:
                lc_messages.append(HumanMessage(content=content))

        # serialize so only one call hits Ollama at a time
        with _ollama_lock:
            # rebuild with per-call temperature/max_tokens overrides
            llm = ChatOllama(
                model=self.model,
                temperature=temperature,
                num_predict=max_tokens,
                timeout=600,
            )
            response = llm.invoke(lc_messages)

        # return in the same shape insight_agent.py already expects
        return {
            "choices": [
                {
                    "message": {
                        "content": response.content
                    }
                }
            ]
        }


def get_llm_client():
    """
    Returns: (client_wrapper, model_name, provider)
    Same signature as before — nothing else in the codebase needs to change.
    """
    ollama_model = _getenv_strip("OLLAMA_MODEL", "qwen2.5:3b-instruct-q4_K_M")

    print("DEBUG env read:")
    print("  OLLAMA_MODEL:", ollama_model)

    client = LangChainOllamaClient(ollama_model)
    return client, ollama_model, "ollama-langchain"