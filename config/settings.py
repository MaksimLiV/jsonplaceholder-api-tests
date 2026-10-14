import os
from dataclasses import dataclass

DEFAULT_BASE_URL = "https://jsonplaceholder.typicode.com"


@dataclass(frozen=True)
class Settings:
    base_url: str
    timeout: float
    retries: int

    @classmethod
    def load(cls, cli_base_url: str | None = None) -> "Settings":
        # Priority: CLI option > environment variable > default
        base_url = cli_base_url or os.getenv("API_BASE_URL") or DEFAULT_BASE_URL
        return cls(
            base_url=base_url.rstrip("/"),
            timeout=float(os.getenv("API_TIMEOUT", "10")),
            retries=int(os.getenv("API_RETRIES", "3")),
        )
