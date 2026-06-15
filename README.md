# Sentiment Trader

A tool I built to analyze financial and political news for forex currency pairs and generate a sentiment report classifying the overall market mood as bullish, bearish, or neutral. Built around my own forex trading experience to make the classifications actually useful rather than generic.

\---

## What it does

You run the script, enter a currency pair like GBP/JPY or EUR/USD, and it pulls the latest headlines from trusted financial news sources. Each headline gets sent to an LLM that classifies it as bullish, bearish, or neutral for that specific pair, filters out anything irrelevant, and produces a confidence-weighted overall verdict. The output is an HTML report that opens automatically in your browser.

\---

## How it works

The pipeline has four stages:

fetcher.py pulls up to 30 headlines from the GNews API and filters them against a whitelist of trusted sources like Reuters, Bloomberg, FT, WSJ, CNBC, FXStreet, and others.

analyzer.py sends each headline to Groq's LLaMA3-70B model. The model is prompted to reason as a forex analyst — it knows that a BOJ rate hike is bearish for GBP/JPY, that dovish BOE language weakens GBP, that risk-off flows into JPY and CHF. I included few-shot examples from my own trading experience to improve accuracy over zero-shot prompting. Each headline returns a JSON object with sentiment, relevance, confidence score, and reasoning.

reporter.py takes the filtered and scored headlines, computes the overall verdict by weighting confidence scores, generates a 2-3 sentence analyst summary, and builds the HTML report.

main.py ties it all together and handles the CLI.

\---

## Tech stack

* Python
* Groq API (LLaMA3-70B-8192)
* GNews API
* python-dotenv

\---

## Setup

Clone the repo and install dependencies:

```bash
git clone https://github.com/khanmikaeel99-tech/Sentiment-Analysis.git
cd Sentiment-Analysis
python -m venv env
env\\Scripts\\activate
pip install requests groq python-dotenv
```

Create a .env file in the project root:

```
GROQ\_API\_KEY=your\_key\_here
GNEWS\_API\_KEY=your\_key\_here

NEWS\_API\_KEY=your\_key\_here
```

Then run:

```bash
python main.py
```

\---

## Backtesting

Currently validating the tool against live paper trading sessions on TradingView using the OANDA feed. Running the report each morning, logging the signal against actual GBP/JPY price movement at end of day.

|Sessions tracked|Correct signals|Win rate|
|-|-|-|
|In progress|—|—|

Will update this table as data comes in.

\---

## Notes

GNews free tier has roughly a 1-2 day delay on articles. A production version would use a real-time paid feed. The reports folder is gitignored so generated reports stay local.

