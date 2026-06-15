import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
GROQ_FAST_MODEL = "llama-3.1-8b-instant"
MAX_HEADLINES = 30
MIN_HEADLINES = 7

TRUSTED_SOURCES = [
    "reuters.com",
    "bloomberg.com",
    "ft.com",
    "bbc.com",
    "cnbc.com",
    "forbes.com",
    "marketwatch.com",
    "wsj.com",
    "apnews.com",
    "fxstreet.com",
    "dailyfx.com",
    "investing.com",
    "forexfactory.com",
    "economist.com",
    "financialpost.com",
    "scmp.com",
    "asia.nikkei.com",
    "afp.com",
    "dowjones.com",
    "fortune.com",
    "businessinsider.com",
    "theguardian.com",
    "economictimes.indiatimes.com",
    "channelnewsasia.com",
    "aljazeera.com",
    "finance.yahoo.com",
    "thehill.com",
    "nbcnews.com",
    "abcnews.go.com",
]