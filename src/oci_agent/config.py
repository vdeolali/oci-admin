"""Settings and configuration for the OCI DevOps agent."""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    # Anthropic — support both common spellings found in .env
    anthropic_api_key: str = ""
    # Fallback for the typo variant present in the existing .env
    antropic_api_key: str = ""

    # OCI
    oci_profile: str = "CVM"
    oci_config_path: str = "~/.oci/config"

    # Claude model
    model: str = "claude-sonnet-4-6"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    @property
    def resolved_api_key(self) -> str:
        """Return whichever API key is set, preferring the correct spelling."""
        return self.anthropic_api_key or self.antropic_api_key

    @property
    def resolved_oci_config_path(self) -> str:
        return str(Path(self.oci_config_path).expanduser())


settings = Settings()
