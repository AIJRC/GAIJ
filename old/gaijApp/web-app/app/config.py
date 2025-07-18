from pydantic import BaseSettings

class Settings(BaseSettings):
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    llm_api_url: str

    class Config:
        env_file = ".env"

settings = Settings()