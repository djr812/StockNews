import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
import os
import json
import yfinance as yf

# import pandas as pd


load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")
application = app

# News API details
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = os.getenv("NEWS_API_KEY")


# Load stock symbols from stocks.json
with open("stocks.json") as f:
    asx100 = json.load(f)

# Extract symbols into an array
asx100symbols = [item["symbol"] for item in asx100]


def getCompanyName(symbol):
    """
    Name:       getCompanyName
    Desc:       Look up the company name of an ASX100
                symbol
    Params:     symbol - string
    Returns:    None
    """
    for item in asx100:
        if item["symbol"] == symbol:
            return item["company_name"]
    return None


# Get the stock data from API
def getStockData(stock):
    """
    Name:       getStockData
    Desc:       Get Stock Data from yFinance API
    Params:     stock - string
    Returns:    upDown - string (emoji)
                diffPercent - float
                yesterdayDate - string
    """
    # YFinance Connection
    # Define the ticker symbol
    tickerSymbol = stock

    # Create a Ticker object
    ticker = yf.Ticker(tickerSymbol)

    # Fetch historical market data
    historicalData = ticker.history(period="1d")  # data for the last day
    stkClose = historicalData[["Close"]]
    stkOpen = historicalData[["Open"]]
    try:
        yesterdayClose = stkClose["Close"].iloc[-1]
    except:
        yesterdayClose = 0
        yesterdayOpen = 0
        yesterdayDate = "2025-01-01"
    else:
        yesterdayOpen = stkOpen["Open"].iloc[-1]
        yesterdayDate = historicalData.index[-1].strftime("%A, %d %B %Y")
        if yesterdayClose and yesterdayOpen:
            # Find the positive difference between Open and Close
            priceDiff = yesterdayClose - yesterdayOpen
            diffPercent = round((priceDiff / yesterdayClose) * 100, 1)
            upDown = "🔺" if diffPercent > 0 else "🔻"
            return upDown, diffPercent, yesterdayDate
        else:
            return 0, 0, "2025-01-01"


def getStockNews(stock, companyName, yesterdayDate):
    """
    Name:       getStockNews
    Desc:       Get current news articles about company
                passed in companyName from NewsAPI
    Params:     companyName - string
                yesterdayDate - string
    Returns:    topArticle - list
    """
    # Use the News API to get articles related to the companyName
    # from 2 days prior

    fDate = datetime.strptime(yesterdayDate, "%A, %d %B %Y") - timedelta(days=1)
    fromDate = fDate.strftime("%Y-%m-%d")

    stock = stock[:-3] + " AND ASX"

    newsParams = {
        "apiKey": NEWS_API_KEY,
        "q": stock,
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
        topArticle = [
            {
                "title": "Unable to retrieve news data.",
                "content": "Please try again later.",
                "url": "",
            }
        ]
        return topArticle
    else:
        # Use Python slice operator to create a list that contains the first article.
        articles = newsData["articles"]
        topArticle = articles[:1]
        return topArticle


def getASXNews(yesterdayDate):
    """
    Name:       getASXNews
    Desc:       Get 2 current news articles about ASX200
                passed in yesterdayDate from NewsAPI
    Params:     yesterdayDate - string
    Returns:    asxArticles - list
    """
    fDate = datetime.strptime(yesterdayDate, "%A, %d %B %Y") - timedelta(days=3)
    fromDate = fDate.strftime("%Y-%m-%d")

    newsParams = {
        "apiKey": NEWS_API_KEY,
        "q": "ASX 200",
        "searchIn": "title",
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
        asxArticles = [
            {
                "title": "Unable to retrieve news data.",
                "content": "Please try again later.",
                "url": "",
            },
            {
                "title": "Unable to retrieve news data.",
                "content": "Please try again later.",
                "url": "",
            },
        ]
        return asxArticles
    else:
        # Use Python slice operator to create a list that contains the first article.
        articles = newsData["articles"]
        asxArticles = articles[:2]
        return asxArticles


def formatArticle(stock, companyName, topArticle, upDown, diffPercent):
    """
    Name:       formatArticle
    Desc:       Format the Article Information found on
                NewsAPI with the current stock price
                details ready for News Ticker
    Params:     stock - string
                companyName - string
                topArticle - list
                upDown - string (emoji)
                diffPercent - float
    Returns:    selectedArticle - string
    """
    formattedArticle = [
        (f"| {stock[:-3]}: {upDown} {abs(diffPercent)}% - {article['title']} | ")
        for article in topArticle
    ]
    try:
        selectedArticle = formattedArticle[0]
    except:
        selectedArticle = f"| {stock[:-3]}: {upDown} {abs(diffPercent)}% - No News Found for {companyName} |"
    return selectedArticle


def formatTickerPoint(stock, upDown, diffPercent):
    """
    Name:       formatTickerPoint
    Desc:       Format the information string for the
                stock ticker for each stock passed
                to it.
    Params:     stock - string
                upDown - string (emoji)
                diffPercent - float
    Returns:    formattedTickerPoint - string
    """
    formattedTickerPoint = f"| <b>{stock[:-3]}</b> - {upDown} <b>{abs(diffPercent)}%</b> | &nbsp;&nbsp;&nbsp;"
    return formattedTickerPoint


def buildArticleList():
    """
    Name:       buildArticleList
    Desc:       Build 3 different lists from the arguments
                passed to it - articleList (a brief title for
                the ticker), completeArticleList (a full article
                for the news section) and tickerList (a stock
                symbol and price movement)
    Params:     None
    Returns:    articleList - list
                completeArticleList - list
                yesterdayDate - string
                tickerList - list
    """
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
            tickerPoint = formatTickerPoint(stock, upDown, diffPercent)
            tickerList.append(tickerPoint)
            if abs(diffPercent) >= changeInStock:
                topArticle = getStockNews(stock, companyName, yesterdayDate)
                formattedArticle = formatArticle(
                    stock, companyName, topArticle, upDown, diffPercent
                )
                if topArticle != []:
                    completeArticleList.append(topArticle)
                articleList.append(formattedArticle)
    asxArticles = getASXNews(yesterdayDate)

    return articleList, completeArticleList, yesterdayDate, tickerList, asxArticles


@app.route("/")
def index():
    """
    Name:       index
    Desc:       Trigger building of index.html and pass
                relevant data
    Params:     None
    Returns     render_template
    """
    articles, completeArticleList, yesterdayDate, tickerList, asxArticles = (
        buildArticleList()
    )

    asxNewsDate = datetime.strptime(yesterdayDate, '%A, %d %B %Y') - timedelta(days=3)

    return render_template(
        "index.html",
        articles=articles,
        completeArticleList=completeArticleList,
        yesterdayDate=yesterdayDate,
        tickerList=tickerList,
        asxArticles=asxArticles,
        asxNewsDate=asxNewsDate,
    )


if __name__ == "__main__":
    app.run(debug=True)
