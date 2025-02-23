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
def getCompanyName(symbol):
    for item in asx100:
        if item['symbol'] == symbol:
            return item['company_name']
    return None

# Get the stock data from API
def getStockData(stock):
    # YFinance Connection
    # Define the ticker symbol
    tickerSymbol = stock

    # Create a Ticker object
    ticker = yf.Ticker(tickerSymbol)

    # Fetch historical market data
    historicalData = ticker.history(period="1d")  # data for the last day
    stkClose = historicalData[['Close']]
    stkOpen = historicalData[['Open']]
    yesterdayClose = stkClose["Close"].iloc[-1]
    yesterdayOpen = stkOpen["Open"].iloc[-1]
    
    if yesterdayClose and yesterdayOpen:
        # Find the positive difference between 1 and 2
        priceDiff = yesterdayClose - yesterdayOpen
        diffPercent = round((priceDiff / yesterdayClose) * 100)
        upDown = "🔺" if diffPercent > 0 else "🔻"
        return upDown, diffPercent
    else:
        return None, None


def GetStockNews(companyName):
    # Use the News API to get articles related to the companyName.
    newsParams = {
        "apiKey": NEWS_API_KEY,
        "q": companyName,
        "searchIn": "title",
        "sortBy": "popularity",
    }
    try:
        newsResponse = requests.get(NEWS_ENDPOINT, params=newsParams)
        newsResponse.raise_for_status()
        newsData = newsResponse.json()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {newsResponse.status_code} - {newsResponse.text}")
        topArticle = [{"stock": "error", "title": "Unable to retrieve news data."}]
        return topArticle
    else:
        # Use Python slice operator to create a list that contains the first article.
        articles = newsData["articles"]
        topArticle = articles[:1]
        return topArticle


def formatArticle(stock, topArticle, upDown, diffPercent):    #upDown, diffPercent,
    # formattedArticle = [(f"{stock}: {upDown}  {abs(diffPercent)}%\nHeadline: {article['title']}. \n"
    # f"Brief: {article['content']}") for article in topArticle]
    formattedArticle = [(f"| {stock}: {upDown} {abs(diffPercent)}% - {article['title']} | ") for article in topArticle]
    selectedArticle = formattedArticle[0]
    return selectedArticle

    
def buildArticleList():
    articleList = []
    changeInStock = 3
    for stock in asx100symbols:
        companyName = getCompanyName(stock)
        upDown, diffPercent = getStockData(stock)
        if abs(diffPercent) >= changeInStock:
            topArticle = GetStockNews(companyName)
            formattedArticle = formatArticle(stock, topArticle, upDown, diffPercent)
            articleList.append(formattedArticle)
    return articleList


@app.route('/')
def index():
    articles = buildArticleList()
    return render_template("index.html", articles=articles)


if __name__ == '__main__':
    app.run(debug=True)


