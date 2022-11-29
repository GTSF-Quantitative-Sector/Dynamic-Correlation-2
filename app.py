'''
!pip install numpy
!pip install pandas
!pip install pandas_datareader
!pip install sklearn.linear_model
!pip install polygon
'''

import datetime as dt
import json
import numpy as np
import pandas as pd
from flask import Flask, request
from sklearn.linear_model import LinearRegression
from polygon import RESTClient


client = RESTClient("xkkpZQNLtXmSTyJlZT1RpJtpPMG07N4z")

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/api/v2/corr-matrix', methods=['POST'])
def correlationMatrix():
    print(request.json)
    ticker_list, start, end, price_df, returns_df = get_stock_data(request.json["tckrs"], request.json["start"],
                                                                   request.json["end"],
                                                                   request.json["step"])
    corr_df = returns_df.corr(method='pearson')
    for row in range(len(ticker_list)):
        for col in range(len(ticker_list)):
            if col < row:
                corr_df.iloc[row, col] = ""
    return corr_df.to_json()


@app.route('/api/v2/corr-hist', methods=['POST'])
def correlationHistorical():
    print(request.json)
    ticker_list, start, end, price_df, returns_df = get_stock_data(request.json["tckrs"], request.json["start"],
                                                                   request.json["end"],
                                                                   request.json["step"])
    trail = request.json["trail"]
    history = pd.DataFrame()
    rem = 1
    while len(returns_df.index) >= trail:
        trail_df = returns_df.tail(trail)
        corr = trail_df.corr(method='pearson')
        series = corr.iloc[len(ticker_list) - 1]
        series = series.rename(returns_df.tail(1).index[0].strftime('%Y-%m-%d'))
        history = history.append(series)
        returns_df.drop(returns_df.tail(rem).index, inplace=True)

    return history.iloc[::-1].to_json()


@app.route('/api/v2/treynor', methods=['POST'])
def treynor():
    print(request.json)
    ticker_list, start, end, price_df, returns_df = get_stock_data(request.json["tckrs"], request.json["start"],
                                                                   request.json["end"],
                                                                   request.json["step"])
    returns = ((1 + returns_df).cumprod().iloc[-1])
    beta_list = []
    treynor_list = []
    for ticker in ticker_list:
        beta = get_beta_linreg(returns_df[ticker], returns_df[ticker_list[-1]])
        treynor = (returns[ticker] - returns[ticker_list[-1]]) / beta
        beta_list.append(str(ticker) + "-" + str(ticker_list[-1]) + " : " + str(beta))
        treynor_list.append(str(ticker) + "-" + str(ticker_list[-1]) + " : " + str(treynor))
    return json.dumps({"beta": beta_list, "treynor": treynor_list})


# Helper methods
def get_stock_data(tckr_list, start, end, step):
    """
    Calculates get_stock_data of tickers provided.
    :param tckr_list: list of tickers
    :param start: starting date in format YYYY-MM-DD
    :param end: end date in format YYYY-MM-DD
    :param step: granularity of data returned. "Daily", "Monthly", "Annual"
    :return: list of tickers, correlation_df, and return for each day as a percentage.
    """
    start = dt.datetime.strptime(start, '%Y-%m-%d')
    end = dt.datetime.strptime(end, '%Y-%m-%d')
    price_df = get_data(tckr_list, start, end)
    returns_df = get_returns(price_df, step).pct_change().fillna(0)
    return tckr_list, start, end, price_df, returns_df


def get_tckrs():
    """
    Handles manual user input for tickers.
    :return: list of tickers.
    """
    # user gives number of tckrs they will provide
    n = int(input("Enter number of tickers: "))
    tckr_list = []
    # iterates for each tckr
    for i in range(n):
        ele = input("TCKR " + str(i + 1) + ": ")
        tckr_list.append(ele.upper())  # adding the element
    return tckr_list


def get_data(tckr_list, st, en):
    """
    Fetches data from yahoo finance using pandas datareader, returns dataframe
    :param tckr_list: list of tickers
    :param st: starting date in format YYYY-MM-DD
    :param en: ending date in format YYYY-MM-DD
    :return: pandas dataframe of price data
    """

    #Let me think about this here, so I would need to iterate through all the tickers (which are the columns) then I would
    #pull from those dates and format the time from datetime as the row index and get the data from there
    df = pd.DataFrame()

    timestamps = [dt.date.fromtimestamp(time_agg.timestamp/1000.0) for time_agg in client.get_aggs("AAPL", 1, "day", st, en)]
    df.index = timestamps
    
    for tckr in tckr_list:
        data = []
        group_aggs = client.get_aggs(tckr, 1, "day", st, en)
        for agg in group_aggs:
            data.append(agg.close)
        df[tckr] = data
    return df


def get_returns(price_df, step):
    """
    Turns price dataframe into a returns dataframe dependent on desired time step size
    :param price_df:
    :param step:
    :return:
    """
    returns = pd.DataFrame()
    if (step.lower() == 'daily'):
        returns = price_df.iloc[((len(price_df.index) - 1) % 1)::1, :]
    elif (step.lower() == 'monthly'):
        returns = price_df.iloc[((len(price_df.index) - 1) % 21)::21, :]
    elif (step.lower() == 'annual'):
        returns = price_df.iloc[((len(price_df.index) - 1) % 252)::252, :]
    return returns


def get_beta_linreg(asset_df, bench_df):
    """
    :param asset_df:
    :param bench_df:
    :return: scalar beta coefficient
    """
    x = np.array(asset_df.values.reshape((-1, 1)))
    y = np.array(bench_df)
    model = LinearRegression().fit(x, y)
    beta_df = model.coef_
    return beta_df


def get_returns_total(price_df):
    """
    Helper method to get the total returns of a given period.
    :param price_df: dataframe of prices.
    :return: returns as a percentage of each ticker.
    """
    difference = price_df.iloc[-1] - price_df.iloc[0]
    total_returns = difference / price_df.iloc[0]
    return total_returns


def get_beta(returns_df, corrs_df):
    """
    Calculates beta of given tickers using the correlation method.
    NOTE: Benchmark must be in last index of returns_df
    :param returns_df: dataframe of all tickers' returns over period.
    :param corrs_df: dataframe of all tickers' correlation over period.
    :return: list of beta for each ticker
    """
    # returns_df = get_returns_percentage(returns_df)
    std_df = np.std(returns_df, axis=0)
    benchmark_std = std_df[-1]  # gets last element from tckr_list standard deviation (industry specific index)
    std_quotient = []
    for i in range(len(std_df) - 1):
        quotient = std_df[i] / benchmark_std
        std_quotient.append(quotient)
    corrs_df = np.transpose(np.array(corrs_df))
    corrs_df = corrs_df[-1]  # Gets get_stock_data between stocks compared to benchmark
    corrs_df = corrs_df[:-1]  # Removes benchmark get_stock_data with itself
    beta = corrs_df * std_quotient
    return beta

# Run app
if __name__ == '__main__':
    app.run()
