'''
!pip install numpy
!pip install pandas
!pip install pandas_datareader
'''

import datetime as dt
import json

import numpy as np
import pandas as pd
import pandas_datareader as web
from flask import Flask, request

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/api/v2/correlation', methods=['POST'])
def correlationMatrix():
    print(request.json)
    tckrs, _unused1, _unused2, corrs, = correlation(request.json["tckrs"], request.json["start"], request.json["end"],
                                                    request.json["step"])
    for row in range(len(tckrs)):
        for col in range(len(tckrs)):
            if col < row:
                corrs.iloc[row, col] = ""
    return corrs.to_json()


@app.route('/api/v2/historical', methods=['POST'])
def historicalCorrelation():
    print(request.json)
    start = dt.datetime.strptime(request.json["start"], '%Y-%m-%d')
    end = dt.datetime.strptime(request.json["end"], '%Y-%m-%d')
    tickers = request.json["tckrs"]
    price_df = web.DataReader(tickers, 'yahoo', start, end)["Adj Close"]
    trail = request.json["trail"]
    step = request.json["step"]

    history = pd.DataFrame()

    returns = pd.DataFrame()
    rem = 1

    if step.lower() == 'daily':
        returns = price_df.iloc[((len(price_df.index) - 1) % 1)::1, :].pct_change()
        rem = 7
    elif step.lower() == 'monthly':
        returns = price_df.iloc[((len(price_df.index) - 1) % 21)::21, :].pct_change()
    elif step.lower() == 'annual':
        returns = price_df.iloc[((len(price_df.index) - 1) % 252)::252, :].pct_change()

    while len(returns.index) >= trail:
        trail_df = returns.tail(trail)
        corr = trail_df.corr(method='pearson')
        series = corr.iloc[len(tickers) - 1]
        series = series.rename(returns.tail(1).index[0].strftime('%Y-%m-%d'))
        history = history.append(series)
        returns.drop(returns.tail(rem).index, inplace=True)

    return history.iloc[::-1].to_json()


@app.route('/api/v2/treynor', methods=['POST'])
def get_treynor():
    print(request.json)
    tckrs, price_df, returns_df, corrs_df, = correlation(request.json["tckrs"], request.json["start"],
                                                         request.json["end"],
                                                         request.json["step"])
    total_returns = get_returns_total(price_df)
    beta = get_beta(returns_df, corrs_df)
    risk_free_rate = total_returns[-1]
    beta_tckrs = []
    treynor = []
    for i in range(len(beta)):
        treynor_part = (total_returns[i] - risk_free_rate) / beta[i]
        beta_tckrs.append(str(tckrs[i]) + "-" + str(tckrs[-1]) + " : " + str(beta[i]))
        treynor.append(str(tckrs[i]) + "-" + str(tckrs[-1]) + " : " + str(treynor_part))
    return json.dumps({"beta": beta_tckrs, "treynor": treynor})


# Helper methods
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
    df = web.DataReader(tckr_list, 'yahoo', st, en)["Adj Close"]
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
    corrs_df = corrs_df[-1]  # Gets correlation between stocks compared to benchmark
    corrs_df = corrs_df[:-1]  # Removes benchmark correlation with itself
    beta = corrs_df * std_quotient
    return beta


def correlation(tckr_list, start, end, step):
    """
    Calculates correlation of tickers provided.
    :param tckr_list: list of tickers
    :param start: starting date in format YYYY-MM-DD
    :param end: end date in format YYYY-MM-DD
    :param step: granularity of data returned. "Daily", "Monthly", "Annual"
    :return: list of tickers, correlation_df, and return for each day as a percentage.
    """
    start = dt.datetime.strptime(start, '%Y-%m-%d')
    end = dt.datetime.strptime(end, '%Y-%m-%d')
    price_df = get_data(tckr_list, start, end)
    returns_df = get_returns(price_df, step).pct_change()
    print("Returns_df = \n", returns_df)
    correlation_df = returns_df.corr(method='pearson')
    return tckr_list, price_df, returns_df, correlation_df


if __name__ == '__main__':
    app.run()
