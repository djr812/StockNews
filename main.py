import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')
application = app

# Stock API details
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
STOCK_API_KEY = os.getenv("STOCK_API_KEY")

# News API details
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Time variables
yesterday_date = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
day_before_yesterday_date = (datetime.now() - timedelta(2)).strftime('%Y-%m-%d')
five_days_ago_date = (datetime.now() - timedelta(5)).strftime('%Y-%m-%d')

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
    stock_params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": stock,
        "apikey": STOCK_API_KEY,
        "outputsize": "compact",
    }
    # Get the stock data from API
    stk_response = requests.get(STOCK_ENDPOINT, params=stock_params)
    stk_response.raise_for_status()
    stk_data = stk_response.json()

    print(stk_data)

    # Get yesterday's closing stock price.
    try:
        yesterday_close = float(stk_data["Time Series (Daily)"][yesterday_date]["4. close"])
    except KeyError:
        print(f"No data available for {yesterday_date}")
        yesterday_close = None

    # Get the day before yesterday's closing stock price
    try:
        dby_close = float(stk_data["Time Series (Daily)"][day_before_yesterday_date]["4. close"])
    except KeyError:
        print(f"No data available for {day_before_yesterday_date}")
        dby_close = None

    if yesterday_close and dby_close:
        # Find the positive difference between 1 and 2
        price_diff = yesterday_close - dby_close
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


def formatArticle(stock, top_article):    #up_down, diff_percent,
    # formatted_article = [(f"{stock}: {up_down}  {abs(diff_percent)}%\nHeadline: {article['title']}. \n"
    # f"Brief: {article['content']}") for article in top_article]
    formatted_article = [(f"{stock}: {article['title']}. ") for article in top_article]
    return formatted_article

    
def buildArticleList():
    article_list = []
    for stock in asx100symbols:
        print(stock)
        company_name = get_company_name(stock)
        print(company_name)
        #up_down, diff_percent = getStockData(stock)
        top_article = GetStockNews(company_name)
        formatted_article = formatArticle(stock, top_article)
        print(formatted_article)
        article_list.append(formatted_article)
    return article_list

# articles = buildArticleList()
# for article in articles:
#     print(article)


@app.route('/')
def index():
    articles = buildArticleList()
    return render_template("index.html", articles=articles)


if __name__ == '__main__':
    app.run(debug=True)


