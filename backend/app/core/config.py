
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    FRONTEND_ORIGIN: str = ""
    ADMIN_API_TOKEN: str = ""

    POLICY_PATH: str = "public/airline_policy.md"
    VECTORSTORE_PATH: str = "data/vectorstore"
    METADATA_PATH: str = "data/metadata"

    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 650
    CHUNK_OVERLAP: int = 100
    SIMILARITY_THRESHOLD: float = 0.35
    TOP_K_CHUNKS: int = 5
    INDEX_SCHEMA_VERSION: str = "v1.0"

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_absolute_path(self, relative_path: str) -> Path:
        p = Path(relative_path)
        if p.is_absolute():
            return p
        return BACKEND_ROOT / p

    @property
    def policy_file_path(self) -> Path:
        return self.get_absolute_path(self.POLICY_PATH)

    @property
    def vectorstore_dir(self) -> Path:
        return self.get_absolute_path(self.VECTORSTORE_PATH)

    @property
    def metadata_dir(self) -> Path:
        return self.get_absolute_path(self.METADATA_PATH)


settings = Settings()
