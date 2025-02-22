import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
import os
import json
import yfinance as yf
import pandas as pd


load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')
application = app

# News API details
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = os.getenv("NEWS_API_KEY")


# Time variables
# yesterday_date = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
# day_before_yesterday_date = (datetime.now() - timedelta(2)).strftime('%Y-%m-%d')
# five_days_ago_date = (datetime.now() - timedelta(5)).strftime('%Y-%m-%d')

# Load stock symbols from stocks.json
with open(os.path.join(os.path.dirname(__file__), 'stocks.json')) as f:
    asx100 = json.load(f)

# Extract symbols into an array
asx100symbols = [item['symbol'] for item in asx100]

# Function to look up the name of an ASX100 symbol
def get_company_name(symbol):
    for item in asx100:
        if item['symbol'] == symbol:
            return item['company_name']
    return None

# Get the stock data from API
def getStockData(stock):
    # YFinance Connection
    # Define the ticker symbol
    ticker_symbol = stock

    # Create a Ticker object
    ticker = yf.Ticker(ticker_symbol)

    # Fetch historical market data
    historical_data = ticker.history(period="1d")  # data for the last day
    stk_close = historical_data[['Close']]
    stk_open = historical_data[['Open']]
    yesterday_close = stk_close["Close"].iloc[-1]
    yesterday_open = stk_open["Open"].iloc[-1]
    
    if yesterday_close and yesterday_open:
        # Find the positive difference between 1 and 2
        price_diff = yesterday_close - yesterday_open
        diff_percent = round((price_diff / yesterday_close) * 100)
        up_down = "⬆️" if diff_percent > 0 else "⬇️"
        return up_down, diff_percent
    else:
        return None, None


def GetStockNews(company_name):
    # Use the News API to get articles related to the COMPANY_NAME.
    news_params = {
        "apiKey": NEWS_API_KEY,
        "q": company_name,
        "searchIn": "title",
        "sortBy": "popularity",
    }
    news_response = requests.get(NEWS_ENDPOINT, params=news_params)
    news_response.raise_for_status()
    news_data = news_response.json()

    # Use Python slice operator to create a list that contains the first article.
    articles = news_data["articles"]
    top_article = articles[:1]

    return top_article


def formatArticle(stock, top_article, up_down, diff_percent):    #up_down, diff_percent,
    # formatted_article = [(f"{stock}: {up_down}  {abs(diff_percent)}%\nHeadline: {article['title']}. \n"
    # f"Brief: {article['content']}") for article in top_article]
    formatted_article = [(f"{stock}: {up_down} {abs(diff_percent)}% - {article['title']}. ") for article in top_article]
    return formatted_article

    
def buildArticleList():
    article_list = []
    for stock in asx100symbols:
        company_name = get_company_name(stock)
        up_down, diff_percent = getStockData(stock)
        top_article = GetStockNews(company_name)
        formatted_article = formatArticle(stock, top_article, up_down, diff_percent)
        article_list.append(formatted_article)
    return article_list


@app.route('/')
def index():
    articles = buildArticleList()
    return render_template("index.html", articles=articles)


if __name__ == '__main__':
    app.run(debug=True)


