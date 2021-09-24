'''
!pip install numpy
!pip install pandas
!pip install pandas_datareader
'''

import math
import json
import pandas as pd
import numpy as np
import pandas_datareader as web
import datetime as dt
from flask import Flask, request, jsonify

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/api/v1/correlation', methods=['POST'])
def correlationMatrix():
    print(request.json)
    tckrs,corrs = correlation(request.json["tckrs"], request.json["start"], request.json["end"], request.json["step"])
    for row in range(len(tckrs)):
        for col in range(len(tckrs)):
            if col < row:
                corrs.iloc[row, col] = ""
    return corrs.to_json()


# Helper methods

# handles uers input for tckrs
def get_tckrs():
    # user gives number of tckrs they will provide
    n = int(input("Enter number of tickers: "))
    tckr_list = []
    # iterates for each tckr
    for i in range(n):
        ele = input("TCKR " + str(i+1) + ": ")
        tckr_list.append(ele.upper())  # adding the element

    return tckr_list

# fetches data from yahoo finance using pandas datareader, returns dataframe
def get_data(tckr_list, st, en):
    df = web.DataReader(tckr_list, 'yahoo', st, en)["Adj Close"]
    return df

# turns price dataframe into a returns dataframe dependent on desired time step size
def get_returns(price_df, step):
    returns = pd.DataFrame()
    if (step.lower() == 'daily'):
        returns = price_df.iloc[((len(price_df.index)-1)%1)::1, :]
    elif (step.lower() == 'monthly'):
        returns = price_df.iloc[((len(price_df.index)-1)%21)::21, :]
    elif (step.lower() == 'annual'):
        returns = price_df.iloc[((len(price_df.index)-1)%252)::252, :]
    return returns
    
def correlation(tckr_list, start, end, step):
    start = dt.datetime.strptime(start, '%Y-%m-%d')
    end = dt.datetime.strptime(end, '%Y-%m-%d')
    price_df = get_data(tckr_list, start, end)
    returns_df = get_returns(price_df, step).pct_change()
    correlation_df = returns_df.corr(method='pearson')
    return tckr_list,correlation_df

@app.route('/api/v1/historical', methods=['POST'])
def historicalCorrelation():
    start = dt.datetime.strptime(request.json["start"], '%Y-%m-%d')
    end = dt.datetime.strptime(request.json["end"], '%Y-%m-%d')
    tickers = request.json["tckrs"]
    price_df = web.DataReader(tickers, 'yahoo', start, end)["Adj Close"]
    trail = request.json["trail"]
    step = request.json["step"]

    history = pd.DataFrame()

    returns = pd.DataFrame()
    rem = 1

    if (step.lower() == 'daily'):
        returns = price_df.iloc[((len(price_df.index)-1)%1)::1, :].pct_change()
        rem = 7
    elif (step.lower() == 'monthly'):
        returns = price_df.iloc[((len(price_df.index)-1)%21)::21, :].pct_change()
    elif (step.lower() == 'annual'):
        returns = price_df.iloc[((len(price_df.index)-1)%252)::252, :].pct_change()
        
    while len(returns.index) >= trail:
        trail_df = returns.tail(trail)
        corr = trail_df.corr(method='pearson')
        series = corr.iloc[len(tickers)-1]
        series = series.rename(returns.tail(1).index[0].strftime('%Y-%m-%d'))
        history = history.append(series)
        returns.drop(returns.tail(rem).index, inplace=True)
    
    return history.iloc[::-1].to_json()


if __name__ == '__main__':
    app.run()