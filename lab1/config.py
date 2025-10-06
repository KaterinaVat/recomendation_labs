import os

from dotenv import load_dotenv

load_dotenv()
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
if RAPIDAPI_KEY is None:
    raise ValueError("RAPIDAPI_KEY is not set in the environment variables")

API_HOST_API1 = os.getenv("API_HOST_API1")
if API_HOST_API1 is None:
    raise ValueError("API_HOST_API1 is not set in the environment variables")

API_HOST_API2 = os.getenv("API_HOST_API2")
if API_HOST_API2 is None:
    raise ValueError("API_HOST_API2 is not set in the environment variables")
