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
    try:
        yesterdayClose = stkClose["Close"].iloc[-1]
    except:
        yesterdayClose = 0
        yesterdayOpen = 0
        yesterdayDate = '2025-01-01'
    else:
        yesterdayOpen = stkOpen["Open"].iloc[-1]
        yesterdayDate = historicalData.index[-1].strftime('%A, %d %B %Y')
        if yesterdayClose and yesterdayOpen:
            # Find the positive difference between Open and Close
            priceDiff = yesterdayClose - yesterdayOpen
            diffPercent = round((priceDiff / yesterdayClose) * 100, 1)
            upDown = "🔺" if diffPercent > 0 else "🔻"
            return upDown, diffPercent, yesterdayDate
        else:
            return 0, 0, '2025-01-01'


def GetStockNews(companyName, yesterdayDate):
    # Use the News API to get articles related to the companyName
    # from 2 days prior
    
    fDate = datetime.strptime(yesterdayDate,'%A, %d %B %Y') - timedelta(days=1)
    fromDate = fDate.strftime('%Y-%m-%d') 
    
    newsParams = {
        "apiKey": NEWS_API_KEY,
        "q": companyName,
        "searchIn": "content",
        "sortBy": "popularity",
        "from": fromDate,
        "language": "en",
    }
    try:
        newsResponse = requests.get(NEWS_ENDPOINT, params=newsParams)
        newsResponse.raise_for_status()
        newsData = newsResponse.json()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {newsResponse.status_code} - {newsResponse.text}")
        topArticle = [{"title": "Unable to retrieve news data.", "content": "Please try again later.", "url": ""}]
        return topArticle
    else:
        # Use Python slice operator to create a list that contains the first article.
        articles = newsData["articles"]
        topArticle = articles[:1]
        return topArticle


def formatArticle(stock, companyName, topArticle, upDown, diffPercent):    #upDown, diffPercent,
    formattedArticle = [(f"| {stock[:-3]}:{companyName} {upDown} {abs(diffPercent)}% - {article['title']} | ") for article in topArticle]
    try:
        selectedArticle = formattedArticle[0]
    except:
        selectedArticle = f"| {stock[:-3]}: {upDown} {abs(diffPercent)}% - No News Found for {companyName} |"
    return selectedArticle


def formatTickerPoint(stock, companyName, upDown, diffPercent):
    formattedTickerPoint = f"| <b>{stock[:-3]}</b> - {upDown} <b>{abs(diffPercent)}%</b> | &nbsp;&nbsp;&nbsp;"
    return formattedTickerPoint

    
def buildArticleList():
    articleList = []
    completeArticleList = []
    tickerList = []
    changeInStock = 5
    for stock in asx100symbols:
        companyName = getCompanyName(stock)
        try:
            upDown, diffPercent, yesterdayDate = getStockData(stock)
        except:
            upDown = 0
            diffPercent = 0
        else:
            tickerPoint = formatTickerPoint(stock, companyName, upDown, diffPercent)
            tickerList.append(tickerPoint)
            if abs(diffPercent) >= changeInStock:
                topArticle = GetStockNews(companyName, yesterdayDate)
                formattedArticle = formatArticle(stock, companyName, topArticle, upDown, diffPercent)
                completeArticleList.append(topArticle)
                articleList.append(formattedArticle)
        
    return articleList, completeArticleList, yesterdayDate, tickerList


@app.route('/')
def index():
    articles, completeArticleList, yesterdayDate, tickerList = buildArticleList()
    return render_template("index.html", articles=articles, completeArticleList=completeArticleList, yesterdayDate=yesterdayDate, tickerList=tickerList)


if __name__ == '__main__':
    app.run(debug=True)


