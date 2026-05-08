from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = Field(default="local", alias="MEANINGGRID_ENV")
    public_url: str = Field(default="http://localhost:3000", alias="MEANINGGRID_PUBLIC_URL")
    api_public_url: str = Field(default="http://localhost:8000", alias="API_PUBLIC_URL")
    mcp_public_url: str = Field(default="http://localhost:8010", alias="MCP_PUBLIC_URL")

    auth_mode: str = Field(default="local", alias="AUTH_MODE")
    database_url: str = Field(
        default="postgresql+psycopg://meaninggrid:meaninggrid@postgres:5432/meaninggrid",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")
    qdrant_url: str = Field(default="http://qdrant:6333", alias="QDRANT_URL")

    s3_endpoint: str = Field(default="http://minio:9000", alias="S3_ENDPOINT")
    s3_access_key: str = Field(default="meaninggrid", alias="S3_ACCESS_KEY")
    s3_secret_key: str = Field(default="meaninggrid-local", alias="S3_SECRET_KEY")
    s3_bucket_raw: str = Field(default="meaninggrid-raw", alias="S3_BUCKET_RAW")
    s3_bucket_artifacts: str = Field(default="meaninggrid-artifacts", alias="S3_BUCKET_ARTIFACTS")
    s3_bucket_exports: str = Field(default="meaninggrid-exports", alias="S3_BUCKET_EXPORTS")

    vector_backend: str = Field(default="qdrant", alias="VECTOR_BACKEND")
    object_store_backend: str = Field(default="s3", alias="OBJECT_STORE_BACKEND")
    queue_backend: str = Field(default="redis", alias="QUEUE_BACKEND")
    embedding_provider: str = Field(default="local", alias="EMBEDDING_PROVIDER")
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        alias="EMBEDDING_MODEL",
    )
    embedding_dimension: int = Field(default=384, alias="EMBEDDING_DIMENSION")
    llm_provider: str = Field(default="none", alias="LLM_PROVIDER")
    default_modules: str = Field(default="site_audit", alias="DEFAULT_MODULES")
    enable_telemetry: bool = Field(default=False, alias="ENABLE_TELEMETRY")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
