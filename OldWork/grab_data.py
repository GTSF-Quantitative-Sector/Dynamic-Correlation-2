import pandas_datareader.data as web
import datetime as dt

def get_data(tckr, st, en):
    start = dt.datetime(st[0], st[1], st[2])
    end = dt.datetime(en[0], en[1], en[2])
    temp = web.DataReader(tckr, 'yahoo', start, end)

    # temp.drop(['Volume', 'Open', 'High', 'Low', 'Close'], axis=1, inplace=True)
    temp.drop(['Volume'], axis=1, inplace=True)
    cols = temp.columns.values
    # newcols = []
    # for col in cols:
    #     tempstr = tckr + ' ' + col
    #     newcols.append(tempstr)
    #
    # temp.columns = newcols
    # temp.columns = [tckr + ' close']
    #
    # emas = [50,200]
    # emas = []
    # for ema in emas:
    #     newstr = tckr + str(ema) + 'ema'
    #     newstr2 = tckr + ' ' + 'Adj Close'
    #     temp[newstr] = pd.Series.ewm(temp[newstr2], span = ema).mean()

    return temp


### Calling the function
symb = 'TSLA'
start = (2020, 1, 1)
end = (2020, 2, 12)
df = get_data(symb, start, end)
print(df)