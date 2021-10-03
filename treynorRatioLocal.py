import math
import json
import pandas as pd
import numpy as np
import pandas_datareader as web
import datetime as dt

# Hard-Coded Variables (Change as Needed)

step = "daily"
start = "2020-10-2"
end = "2021-10-2"

# Helper Methods

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
def get_data(tckr_list, start, end):
    df = web.DataReader(tckr_list, 'yahoo', start, end)["Adj Close"]
    return df


def correlation(tckr_list, start, end, step):
    start = dt.datetime.strptime(start, '%Y-%m-%d')
    end = dt.datetime.strptime(end, '%Y-%m-%d')
    price_df = get_data(tckr_list, start, end)
    returns_df = get_returns(price_df, step).pct_change()
    correlation_df = returns_df.corr(method='pearson')
    return tckr_list,correlation_df


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


# turns return dataframe into a returns dataframe in percentages
def get_returns_percentage(returns_df):
    returns_df = np.array(returns_df)
    returns = []
    for i in range(len(returns_df)-1):
        initial_returns = returns_df[i]
        final_returns = returns_df[i+1]
        difference = final_returns - initial_returns # element wise subtraction
        percentage_returns = difference / initial_returns # element wise division
        returns.append(percentage_returns)
    return returns # NOTE: dataframe is now type np.array()


# finds beta; NOTE: Benchmark must be in last index of tckr_list
def get_beta(returns_df, corrs_df):
    std_df = np.std(returns_df, axis=0)
    benchmark_std = std_df[-1] # gets last element from tckr_list standard deviation (industry specific index)
    std_quotient = []
    for i in range(len(std_df)-1):
        quotient = std_df[i] / benchmark_std
        std_quotient.append(quotient)
    corrs_df = np.transpose(np.array(corrs_df))
    corrs_df = corrs_df[-1] # Gets correlation between stocks compared to benchmark
    corrs_df = corrs_df[0:len(corrs_df)-1] # Removes benchmark correlation with itself
    beta = corrs_df * std_quotient
    return beta


def get_returns_total(returns_df):
    returns_df = np.array(returns_df)
    difference = returns_df[len(returns_df)-1] - returns_df[0]
    total_returns = difference / returns_df[0]
    return total_returns


def get_treynor(beta, total_returns):
    risk_free_rate = total_returns[-1]
    treynor = []
    for i in range(len(beta)):
        treynor_part = (total_returns[i] - risk_free_rate) / beta[i]
        treynor.append(treynor_part)
    print(treynor)



# Scripting
tckr_list = ["PLUG", "DCP", "MSFT", "NRZ", "SPY"] # Benchmark has to be in the back
df = get_data(tckr_list, start, end)
returns_df = get_returns(df, step)
total_returns = get_returns_total(returns_df)
returns_df = get_returns_percentage(returns_df)

na,corrs_df = correlation(tckr_list, start, end, step)

beta = get_beta(returns_df, corrs_df)
get_treynor(beta, total_returns)
