import collect_data as cd
import least_correlated_alg as lca

if __name__ == '__main__':
    tckrs, correlations = cd.collect_data()
    print(correlations)
    sub = int(input('What size subset would you like: '))
    stocks, finCor = lca.lcs(tckrs, correlations, sub)
    print(stocks)
    print(finCor)