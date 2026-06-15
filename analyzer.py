import json
import re
import time
from groq import Groq
from config import GROQ_API_KEY, GROQ_FAST_MODEL

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are a senior forex analyst with deep experience trading major,
minor, and exotic currency pairs. You understand:
- Central bank policy and interest rate differentials (Fed, ECB, BOE, BOJ, SNB, RBA)
- Risk-on vs risk-off market sentiment and safe haven flows
- Geopolitical risk premiums and their impact on currency strength
- Inflation data interpretation (CPI, PPI) and its effect on rate expectations
- Employment data (NFP, unemployment) and GDP impact on currencies
- Trade balance, current account, and capital flow dynamics
- Technical sentiment: overbought/oversold conditions in broader context

When classifying headlines, think like a professional trader, not a journalist.
A rate hike is bullish for that currency. A dovish surprise is bearish.
Political instability weakens a currency. Safe haven demand strengthens JPY, CHF, USD.
Always consider the DIRECT impact on the specific currency pair mentioned.
For cross pairs (e.g. GBP/JPY), news about EITHER currency's central bank or economy is relevant."""

FEW_SHOT_EXAMPLES = """
Examples of correct classification:

Headline: "Fed signals two more rate hikes in 2026"
Currency: EUR/USD
Sentiment: BEARISH
Reasoning: Higher US rates strengthen USD, pushing EUR/USD down
Score: 0.85

Headline: "ECB cuts rates unexpectedly by 25bps"
Currency: EUR/USD
Sentiment: BEARISH
Reasoning: Dovish ECB surprise weakens EUR directly
Score: 0.90

Headline: "US CPI comes in hotter than expected at 4.2%"
Currency: EUR/USD
Sentiment: BEARISH
Reasoning: Hot inflation increases Fed rate expectations, strengthening USD
Score: 0.80

Headline: "Eurozone GDP beats expectations, growing 2.1%"
Currency: EUR/USD
Sentiment: BULLISH
Reasoning: Strong EU growth supports EUR strength
Score: 0.75

Headline: "Geopolitical tensions rise in Eastern Europe"
Currency: EUR/USD
Sentiment: BEARISH
Reasoning: European geopolitical risk weakens EUR, flows to USD safe haven
Score: 0.70

Headline: "Bank of England holds rates, signals cuts incoming"
Currency: GBP/USD
Sentiment: BEARISH
Reasoning: Dovish BOE forward guidance weakens GBP
Score: 0.80

Headline: "Gold surges as recession fears mount"
Currency: XAU/USD
Sentiment: BULLISH
Reasoning: Risk-off sentiment drives safe haven demand for gold
Score: 0.85
"""

FALLBACK = {"sentiment": "NEUTRAL", "relevant": False, "score": 0.0, "reasoning": "Could not parse response"}

def _analyze_batch_chunk(chunk, currency_pair):
    numbered = "\n".join(f'{i+1}. {h}' for i, h in enumerate(chunk))

    prompt = f"""{FEW_SHOT_EXAMPLES}

Classify each headline below for the currency pair {currency_pair}.
News about EITHER currency in the pair is relevant (e.g. BOE/UK news for GBP, BOJ/Japan news for JPY).

Headlines:
{numbered}

Return a JSON object with key "results" containing an array of exactly {len(chunk)} objects, one per headline:
{{"results": [{{"sentiment": "BULLISH"|"BEARISH"|"NEUTRAL", "relevant": true|false, "score": 0.0-1.0, "reasoning": "one sentence"}}, ...]}}"""

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=GROQ_FAST_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content.strip()
            data = json.loads(raw)
            results = data.get("results") or data.get("analyses") or next(
                (v for v in data.values() if isinstance(v, list)), []
            )
            if not isinstance(results, list):
                return [dict(FALLBACK) for _ in chunk]
            padded = list(results[:len(chunk)])
            while len(padded) < len(chunk):
                padded.append(dict(FALLBACK))
            return padded
        except Exception as e:
            msg = str(e)
            wait_match = re.search(r'try again in (\d+(?:\.\d+)?)s', msg)
            if wait_match:
                wait = float(wait_match.group(1)) + 1
                print(f"\n⏳ Rate limit hit, waiting {wait:.0f}s before retry...")
                time.sleep(wait)
            elif attempt < 2:
                time.sleep(5)
            else:
                print(f"\n❌ Groq API error: {e}")
    return [dict(FALLBACK) for _ in chunk]

def analyze_headlines_batch(headlines, currency_pair, chunk_size=10):
    results = []
    for i in range(0, len(headlines), chunk_size):
        chunk = headlines[i:i + chunk_size]
        results.extend(_analyze_batch_chunk(chunk, currency_pair))
    return results

def generate_summary(headlines_data, currency_pair, overall_verdict):
    headlines_text = "\n".join([
        f"- {h['headline']} ({h['sentiment']}, score: {h['score']})"
        for h in headlines_data
    ])

    prompt = f"""You are a senior forex analyst. Based on these headlines for {currency_pair}:

{headlines_text}

Overall verdict: {overall_verdict}

Write a 2-3 sentence professional summary explaining WHY the sentiment is {overall_verdict}
for {currency_pair} right now. Be specific about the key drivers. Think like a trader."""

    try:
        response = client.chat.completions.create(
            model=GROQ_FAST_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Summary unavailable: {e}"
