from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001"
    isric_base_url: str = "https://rest.isric.org/soilgrids/v2.0"
    elevation_api_url: str = "https://api.open-elevation.com/api/v1/lookup"
    isric_max_requests_per_minute: int = 4
    soil_cache_ttl: int = 3600
    elevation_cache_ttl: int = 86400

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
