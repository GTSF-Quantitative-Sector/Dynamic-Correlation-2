import pandas as pd
import pandas_datareader as web
import datetime as dt

def get_user_input():
    # number of elements as input
    n = int(input("Enter number of elements : "))
    print(n)
    tckr_list = []
    # iterates from 0 to n - 1
    for i in range(n):
        ele = input()
        print(ele)
        print(i)
        tckr_list.append(ele)  # adding the element

    return tckr_list


def get_first_stock_data(tckr, st, en):
    start = dt.datetime(st[0], st[1], st[2])
    end = dt.datetime(en[0], en[1], en[2])
    stock_data = web.DataReader(tckr, 'yahoo', start, end)
    stock_data.drop(['Open', 'High', 'Low', 'Close', 'Volume'], axis=1, inplace=True)
    return stock_data

def get_data(tckr_list, st, en):
    df = pd.DataFrame()
    for tckr in tckr_list:
        print(tckr + ': FETCHING DATA')
        start = dt.datetime(st[0], st[1], st[2])
        end = dt.datetime(en[0], en[1], en[2])
        stock_data = web.DataReader(tckr, 'yahoo', start, end)
        print(tckr + ': DONE')
        df[str(tckr)] = stock_data['Adj Close']
    return df

### Calling the function



def stock_returns(tckr_list, return_data, price_df):
    df2 = pd.DataFrame(return_data)
    for tckr in tckr_list:
        df2[tckr] = price_df[tckr].pct_change()
    return df2



def collect_data():
    tckr_list = get_user_input()
    # tckr_list = ['TSLA', 'MSFT', 'AAPL']
    start = (2020, 1, 1)
    end = (2020, 3, 25)
    print('CREATED')
    # price_data = get_first_stock_data(tckr, start, end)
    price_df = get_data(tckr_list, start, end)
    price_df.to_csv("stock_data.csv")
    print('PRICE DATA DONE')
    # Start of calculating returns
    return_data = price_df[tckr_list[0]].pct_change()
    returns_df = stock_returns(tckr_list, return_data, price_df)
    returns_df.to_csv("stock_returns.csv")
    print('RETURNS DONE')
    # Calculating get_stock_data
    correlation_df = returns_df.corr()
    correlation_df.to_csv("stock_correlation.csv")
    print('CORRELATION DONE')
    return tckr_list, correlation_df.to_numpy()

