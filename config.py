import os
from dotenv import load_dotenv

load_dotenv()

# LINE公式アカウントの設定（Render.comで環境変数として設定します）
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# Groq APIキー（Render.comで環境変数として設定します）
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# アプリ設定
DEBUG = True
KNOWLEDGE_FOLDER = "knowledge_base"
CUSTOM_RULES_FILE = "custom_rules.json"
