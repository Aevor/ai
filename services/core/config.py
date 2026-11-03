import os

class Settings:
    APP_NAME: str = "Aevor AI"
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    MAX_DIFF_SIZE_CHARS: int = 100000
    HOST: str = "0.0.0.0"
    PORT: int = 11434

    def __init__(self):
        self.APP_NAME = os.getenv("APP_NAME", "Aevor AI")
        self.ENV = os.getenv("ENV", "development")
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "t", "yes")
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
        self.GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.MAX_DIFF_SIZE_CHARS = int(os.getenv("MAX_DIFF_SIZE_CHARS", "100000"))
        self.HOST = os.getenv("AI_SERVICE_HOST", os.getenv("HOST", "0.0.0.0"))
        self.PORT = int(os.getenv("AI_SERVICE_PORT", os.getenv("PORT", "11434")))


settings = Settings()
