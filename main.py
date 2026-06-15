from fetcher import fetch_headlines
from analyzer import analyze_headlines_batch, generate_summary
from reporter import generate_report
from config import MIN_HEADLINES

def get_overall_verdict(headlines_data):
    weighted = {"BULLISH": 0.0, "BEARISH": 0.0, "NEUTRAL": 0.0}
    for h in headlines_data:
        sentiment = h.get("sentiment", "NEUTRAL").upper().strip()
        if sentiment not in weighted:
            sentiment = "NEUTRAL"
        weighted[sentiment] += float(h.get("score", 0.0))
    return max(weighted, key=weighted.get)

def main():
    print("\n🌐 Sentiment Trader — Forex News Analyzer")
    print("=" * 45)
    currency_pair = input("Enter currency pair (e.g. EUR/USD, GBP/USD, XAU/USD): ").strip().lstrip('﻿').upper()

    parts = [p.strip() for p in currency_pair.split("/") if p.strip()]
    if len(parts) != 2 or not all(len(p) >= 2 for p in parts):
        print("❌ Invalid format. Please enter a pair like EUR/USD or GBP/JPY.")
        return

    currency_pair = f"{parts[0]}/{parts[1]}"

    print(f"\n📡 Fetching headlines for {currency_pair}...")
    headlines = fetch_headlines(currency_pair)

    if not headlines:
        print("❌ No headlines found. Check your NewsAPI key or try a different pair.")
        return

    print(f"📰 {len(headlines)} headlines fetched from trusted sources.")
    print("🤖 Analyzing sentiment in batch...")

    results = analyze_headlines_batch([a["headline"] for a in headlines], currency_pair)

    analyzed = []
    for article, result in zip(headlines, results):
        if result.get("relevant"):
            analyzed.append({
                "headline": article["headline"],
                "source": article["source"],
                "url": article["url"],
                "sentiment": result.get("sentiment", "NEUTRAL").upper().strip(),
                "score": float(result.get("score", 0.0)),
                "reasoning": result.get("reasoning", "")
            })

    print(f"\n✅ {len(analyzed)} relevant headlines after filtering.")

    low_data_warning = len(analyzed) < MIN_HEADLINES

    if len(analyzed) == 0:
        print("❌ No relevant headlines survived filtering. Try a different pair or time.")
        return

    overall_verdict = get_overall_verdict(analyzed)
    print(f"📊 Overall verdict: {overall_verdict}")
    print("✍️  Generating analyst summary...")

    summary = generate_summary(analyzed, currency_pair, overall_verdict)

    print("📄 Building report...")
    generate_report(currency_pair, analyzed, overall_verdict, summary, low_data_warning)

if __name__ == "__main__":
    main()