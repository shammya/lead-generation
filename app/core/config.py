from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    google_places_api_key: str
    openai_api_key: str
    gpt_model: str = 'gpt-3.5-turbo-0125'
    version: str = "1.0.0"
    base_dir: str = "app/"
    webdriver_path: str = "/Users/shammo/Downloads/Services/chromedriver_mac_arm64/chromedriver"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
