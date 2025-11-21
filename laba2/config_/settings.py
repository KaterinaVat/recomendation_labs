from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")
GPT_MODEL_NAME = os.getenv("GPT_MODEL_NAME")
GPT_URL = os.getenv('GPT_URL')
LLAMA_MODEL_NAME = os.getenv("LLAMA_MODEL_NAME")
LLAMA_URL = os.getenv("LLAMA_URL")