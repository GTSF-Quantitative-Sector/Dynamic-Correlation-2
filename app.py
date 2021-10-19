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
    tckrs,corrs,_unused = correlation(request.json["tckrs"], request.json["start"], request.json["end"], request.json["step"])
    for row in range(len(tckrs)):
        for col in range(len(tckrs)):
            if col < row:
                corrs.iloc[row, col] = ""
    return corrs.to_json()



@app.route('/api/v1/treynor', methods=['POST'])
def get_treynor():

    tckrs,corrs_df,_unused = correlation(request.json["tckrs"], request.json["start"], request.json["end"], request.json["step"])

    df = get_data(tckrs, request.json["start"], request.json["end"])
    returns_df = np.array(get_returns(df, request.json["step"]))

    total_returns = get_returns_total(returns_df)

    beta = get_beta(returns_df, corrs_df)
    print(beta)

    risk_free_rate = total_returns[-1]
    print(risk_free_rate)
    treynor = []
    for i in range(len(beta)):
        treynor_part = (total_returns[i] - risk_free_rate) / beta[i]
        treynor.append(treynor_part)

    print(treynor)
    return json.dumps(treynor)



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
    return tckr_list,correlation_df,returns_df

def get_returns_percentage(returns_df):
    #returns_df = np.array(returns_df)
    returns = []
    for i in range(len(returns_df)-1):
        initial_returns = returns_df[i]
        final_returns = returns_df[i+1]
        difference = final_returns - initial_returns # element wise subtraction
        if sum(initial_returns == 0) > 0: # if any initial returns are zero, go to next element (don't divide by zero)
            continue
        percentage_returns = difference / initial_returns # element wise division
        returns.append(percentage_returns)
    return returns # NOTE: dataframe is now type np.array()

# finds beta; NOTE: Benchmark must be in last index of tckr_list
def get_beta(returns_df, corrs_df):
    # print(returns_df)
    returns_df = get_returns_percentage(returns_df)
    std_df = np.std(returns_df, axis=0)
    benchmark_std = std_df[-1] # gets last element from tckr_list standard deviation (industry specific index)

    std_quotient = []
    for i in range(len(std_df)-1):
        quotient = std_df[i] / benchmark_std
        std_quotient.append(quotient)
    print(corrs_df)
    corrs_df = np.transpose(np.array(corrs_df))
    corrs_df = corrs_df[-1] # Gets correlation between stocks compared to benchmark
    corrs_df = corrs_df[0:len(corrs_df)-1] # Removes benchmark correlation with itself
    print(corrs_df)
    beta = corrs_df * std_quotient
    return beta

def get_returns_total(returns_df):
    # returns_df = np.array(returns_df)
    difference = returns_df[-1] - returns_df[0]
    total_returns = difference / returns_df[0]
    return total_returns

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
