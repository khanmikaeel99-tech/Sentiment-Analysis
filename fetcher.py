import requests
from datetime import datetime, timedelta, timezone
from config import NEWS_API_KEY, FINNHUB_API_KEY, MAX_HEADLINES, TRUSTED_SOURCES


def _fetch_finnhub(title_terms):
    lower_terms = [t.lower() for t in title_terms]
    try:
        response = requests.get(
            "https://finnhub.io/api/v1/news",
            params={"category": "forex", "token": FINNHUB_API_KEY},
            timeout=10,
        )
        if response.status_code != 200:
            print(f"Finnhub error: {response.status_code}")
            return []
        articles = response.json()
    except Exception as e:
        print(f"Finnhub fetch error: {e}")
        return []

    results = []
    for article in articles:
        headline = article.get("headline", "")
        if not headline:
            continue
        if not any(term in headline.lower() for term in lower_terms):
            continue
        ts = article.get("datetime", 0)
        published = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        results.append({
            "headline": headline,
            "source": article.get("source", "Finnhub"),
            "url": article.get("url", ""),
            "published": published,
        })
    return results


def fetch_headlines(currency_pair):
    currency_map = {
        "GBP": "British Pound",
        "JPY": "Japanese Yen",
        "EUR": "Euro",
        "USD": "US Dollar",
        "AUD": "Australian Dollar",
        "CAD": "Canadian Dollar",
        "CHF": "Swiss Franc",
        "NZD": "New Zealand Dollar",
        "XAU": "Gold",
        "XAG": "Silver",
        "MXN": "Mexican Peso",
        "TRY": "Turkish Lira",
        "ZAR": "South African Rand",
        "NOK": "Norwegian Krone",
        "SEK": "Swedish Krona",
        "DKK": "Danish Krone",
        "SGD": "Singapore Dollar",
        "HKD": "Hong Kong Dollar",
        "CNH": "Chinese Yuan",
        "CNY": "Chinese Yuan",
        "PLN": "Polish Zloty",
        "HUF": "Hungarian Forint",
        "CZK": "Czech Koruna",
        "INR": "Indian Rupee",
        "BRL": "Brazilian Real",
    }

    central_bank_map = {
        "GBP": ["Bank of England", "BOE", "Sterling"],
        "JPY": ["Bank of Japan", "BOJ", "Yen"],
        "EUR": ["ECB", "European Central Bank"],
        "USD": ["Federal Reserve", "Fed", "FOMC"],
        "AUD": ["RBA", "Reserve Bank of Australia"],
        "CAD": ["Bank of Canada", "BOC"],
        "CHF": ["SNB", "Swiss National Bank"],
        "NZD": ["RBNZ", "Reserve Bank of New Zealand"],
        "XAU": ["precious metals"],
        "XAG": ["precious metals"],
        "MXN": ["Banxico", "Peso"],
        "TRY": ["TCMB", "Lira"],
        "ZAR": ["SARB", "Rand"],
        "NOK": ["Norges Bank", "Krone"],
        "SEK": ["Riksbank", "Krona"],
        "SGD": ["MAS", "Monetary Authority of Singapore"],
        "HKD": ["HKMA"],
        "CNH": ["PBOC", "Yuan", "Renminbi"],
        "CNY": ["PBOC", "Yuan", "Renminbi"],
        "INR": ["RBI", "Reserve Bank of India", "Rupee"],
        "BRL": ["BCB", "Real"],
    }

    currencies = currency_pair.replace("/", " ").split()
    title_terms = []
    seen = set()
    for c in currencies:
        name = currency_map.get(c)
        if not name:
            continue
        for term in [name] + central_bank_map.get(c, []):
            if term not in seen:
                seen.add(term)
                title_terms.append(term)

    if not title_terms:
        print(f"⚠️  No known currencies in pair {currency_pair}, cannot build search query.")
        return []

    title_query = " OR ".join(f'"{t}"' if " " in t else t for t in title_terms)
    from_date = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")

    url = "https://newsapi.org/v2/everything"
    params = {
        "qInTitle": title_query,
        "language": "en",
        "pageSize": 100,
        "apiKey": NEWS_API_KEY,
        "sortBy": "publishedAt",
        "from": from_date,
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"NewsAPI error: {response.status_code} - {response.text}")
        return []

    data = response.json()
    if data.get("status") != "ok":
        print(f"NewsAPI error: {data.get('message', 'Unknown error')}")
        return []

    articles = data.get("articles", [])

    filtered = []
    for article in articles:
        source_url = article.get("url", "")
        title = article.get("title", "")
        if not title or title == "[Removed]":
            continue
        if any(domain in source_url for domain in TRUSTED_SOURCES):
            filtered.append({
                "headline": title,
                "source": article.get("source", {}).get("name", "Unknown"),
                "url": source_url,
                "published": article.get("publishedAt", "")
            })

    finnhub_articles = _fetch_finnhub(title_terms)
    seen_urls = {a["url"] for a in filtered}
    for a in finnhub_articles:
        if a["url"] and a["url"] not in seen_urls:
            seen_urls.add(a["url"])
            filtered.append(a)

    return filtered[:MAX_HEADLINES]