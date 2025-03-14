# src/utils.py
import os
from dotenv import load_dotenv

def load_config():
    """
    Loads configuration from a .env file.
    """
    load_dotenv()
    config = {
        "APP_TITLE": os.getenv("APP_TITLE", "Financial Simulator")
    }
    return config
